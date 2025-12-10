#!/usr/bin/env python3
"""
Claude Code Session Watcher

Monitors Claude transcript in real-time, validates responses,
and provides a live activity display via tmux pane.

Communication with hooks via Unix socket for blocking decisions.
"""
import os
import sys
import json
import time
import signal
import socket
import select
import threading
from pathlib import Path
from datetime import datetime

# Try inotify, fall back to polling
try:
    from inotify_simple import INotify, flags as inotify_flags
    HAS_INOTIFY = True
except ImportError:
    HAS_INOTIFY = False


class SessionWatcher:
    def __init__(self, project_dir: str, session_id: str = None):
        self.project_dir = Path(project_dir)
        self.session_id = session_id
        self.running = False

        # Paths
        self.flags_dir = self.project_dir / ".claude" / "flags"
        self.logs_dir = self.project_dir / ".claude" / "logs"
        self.flags_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.logs_dir / "watcher.log"
        self.pid_file = self.flags_dir / "watcher.pid"
        self.socket_path = self.flags_dir / "watcher.socket"

        # Find transcript path
        self.transcript_path = self._find_transcript()
        self.last_position = 0
        self.pending_issues = []  # Issues found in current response

        # Colors for terminal output
        self.colors = {
            "INFO": "\033[36m",      # Cyan
            "WARN": "\033[33m",      # Yellow
            "ERROR": "\033[31m",     # Red
            "BLOCK": "\033[31;1m",   # Bold Red
            "OK": "\033[32m",        # Green
            "EVENT": "\033[35m",     # Magenta
            "RESET": "\033[0m"
        }

    def _find_transcript(self) -> Path:
        """Locate the active transcript file"""
        claude_projects = Path.home() / ".claude" / "projects"

        # Convert project_dir to Claude's naming convention
        # /home/great_ape/codeOne/Claude_Protocol -> -home-great-ape-codeOne-Claude-Protocol
        # Claude converts both / and _ to -
        project_name = str(self.project_dir).replace("/", "-").replace("_", "-")
        project_path = claude_projects / project_name

        if self.session_id:
            transcript = project_path / f"{self.session_id}.jsonl"
            if transcript.exists():
                return transcript

        # Fallback: find most recently modified .jsonl
        if project_path.exists():
            jsonl_files = list(project_path.glob("*.jsonl"))
            # Filter out agent files
            jsonl_files = [f for f in jsonl_files if not f.name.startswith("agent-")]
            if jsonl_files:
                latest = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                return latest

        return None

    def log(self, level: str, message: str, data: dict = None):
        """Write to log file with timestamp and color formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        color = self.colors.get(level, "")
        reset = self.colors["RESET"]

        line = f"[{timestamp}] {color}[{level:5}]{reset} {message}"
        if data:
            line += f" | {json.dumps(data)}"

        # Write to log file only (spawn script redirects stdout to log)
        with open(self.log_file, "a") as f:
            f.write(line + "\n")
            f.flush()

    def _check_laziness(self, response: str) -> list:
        """Check for lazy response patterns"""
        issues = []
        response_lower = response.lower()

        # Skip if work was done
        work_indicators = ["completed", "fixed", "updated", "created",
                          "implemented", "edited", "wrote", "modified",
                          "has been updated", "has been created"]
        if any(ind in response_lower for ind in work_indicators):
            return []

        # Skip if asking user a question
        question_indicators = ["what would you like", "which option",
                              "do you want", "would you prefer", "let me know"]
        if any(ind in response_lower for ind in question_indicators):
            return []

        # Suggestion patterns
        suggestions = ["you could", "you might want to", "consider adding",
                      "i recommend you", "i suggest you"]
        for pattern in suggestions:
            if pattern in response_lower:
                issues.append({"type": "SUGGESTION", "pattern": pattern})

        # Delegation patterns
        delegations = ["you'll need to", "you need to", "you have to",
                      "make sure to", "don't forget to", "you should then",
                      "now you", "go ahead and"]
        for pattern in delegations:
            if pattern in response_lower:
                issues.append({"type": "DELEGATION", "pattern": pattern})

        # Scope reduction patterns
        scope_reductions = ["for brevity", "to keep this short",
                          "i'll focus on", "i won't cover",
                          "beyond the scope", "i'll leave"]
        for pattern in scope_reductions:
            if pattern in response_lower:
                issues.append({"type": "SCOPE_REDUCTION", "pattern": pattern})

        return issues

    def _check_honesty(self, response: str) -> list:
        """Check for overconfident language and missing uncertainty"""
        issues = []
        response_lower = response.lower()

        # Overconfident language
        overconfident = ["definitely", "certainly", "absolutely",
                        "guaranteed", "always works", "never fails"]
        for word in overconfident:
            if word in response_lower:
                issues.append({"type": "OVERCONFIDENT", "pattern": word})

        # Missing uncertainty on definitive claims
        definitive_claims = ["the answer is", "the solution is",
                            "the result is", "the output is"]
        uncertainty_markers = ["i believe", "i think", "probably",
                              "might", "should", "appears", "seems",
                              "likely", "possibly"]

        has_definitive = any(claim in response_lower for claim in definitive_claims)
        has_uncertainty = any(marker in response_lower for marker in uncertainty_markers)

        if has_definitive and not has_uncertainty:
            issues.append({"type": "MISSING_UNCERTAINTY", "pattern": "definitive claim without uncertainty marker"})

        return issues

    def validate_response(self, response: str) -> list:
        """Run all validators on response"""
        all_issues = []
        all_issues.extend(self._check_laziness(response))
        all_issues.extend(self._check_honesty(response))
        return all_issues

    def process_new_lines(self):
        """Read and process new lines from transcript"""
        if not self.transcript_path or not self.transcript_path.exists():
            return

        try:
            with open(self.transcript_path, "r") as f:
                f.seek(self.last_position)
                new_content = f.read()
                self.last_position = f.tell()
        except Exception as e:
            self.log("ERROR", f"Failed to read transcript: {e}")
            return

        if not new_content:
            return

        for line in new_content.strip().split("\n"):
            if not line:
                continue
            try:
                entry = json.loads(line)
                self._process_entry(entry)
            except json.JSONDecodeError:
                continue

    def _process_entry(self, entry: dict):
        """Process a single transcript entry"""
        entry_type = entry.get("type")

        if entry_type == "assistant":
            # Extract text content
            content = entry.get("message", {}).get("content", [])
            text_parts = []
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    text_parts.append(c.get("text", ""))

            full_text = "\n".join(text_parts)

            if full_text:
                char_count = len(full_text)
                self.log("EVENT", f"Assistant response ({char_count} chars)")

                # Validate
                issues = self.validate_response(full_text)

                if issues:
                    self.pending_issues = issues
                    for issue in issues:
                        self.log("WARN", f"{issue['type']}: '{issue['pattern']}'")
                    self.log("BLOCK", f"Found {len(issues)} issue(s) - Stop hook will block")
                else:
                    self.pending_issues = []
                    self.log("OK", "Response validated - no issues")

        elif entry_type == "user":
            content = entry.get("message", {}).get("content", "")
            if isinstance(content, str) and content:
                preview = content[:60].replace("\n", " ")
                self.log("EVENT", f"User: {preview}...")

        elif entry_type == "tool_use":
            tool = entry.get("message", {}).get("content", [{}])[0]
            if isinstance(tool, dict):
                tool_name = tool.get("name", "unknown")
                self.log("INFO", f"Tool: {tool_name}")

    def start_socket_server(self):
        """Start Unix socket for hook communication"""
        if self.socket_path.exists():
            self.socket_path.unlink()

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.socket_path))
        server.listen(5)
        server.setblocking(False)

        self.log("INFO", f"IPC socket ready: {self.socket_path.name}")

        while self.running:
            try:
                readable, _, _ = select.select([server], [], [], 0.5)
                if server in readable:
                    conn, _ = server.accept()
                    try:
                        data = conn.recv(4096).decode()
                        response = self._handle_ipc(data)
                        conn.send(response.encode())
                    finally:
                        conn.close()
            except Exception as e:
                if self.running:
                    self.log("ERROR", f"Socket error: {e}")

        server.close()
        if self.socket_path.exists():
            self.socket_path.unlink()

    def _handle_ipc(self, data: str) -> str:
        """Handle IPC request from hooks"""
        try:
            request = json.loads(data)
            cmd = request.get("cmd")

            if cmd == "get_pending":
                if self.pending_issues:
                    return json.dumps({
                        "has_issues": True,
                        "issues": self.pending_issues,
                        "count": len(self.pending_issues)
                    })
                return json.dumps({"has_issues": False})

            elif cmd == "status":
                return json.dumps({
                    "running": True,
                    "session": self.session_id,
                    "transcript": str(self.transcript_path)
                })

            elif cmd == "clear_pending":
                self.pending_issues = []
                return json.dumps({"ok": True})

            else:
                return json.dumps({"error": f"unknown command: {cmd}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def run(self):
        """Main watcher loop"""
        # Write PID file
        self.pid_file.write_text(str(os.getpid()))
        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        # Clear log file
        self.log_file.write_text("")

        self.log("INFO", "=" * 50)
        self.log("INFO", "Session Watcher Started")
        self.log("INFO", f"Project: {self.project_dir.name}")
        if self.transcript_path:
            self.log("INFO", f"Transcript: {self.transcript_path.name}")
        else:
            self.log("WARN", "No transcript found yet - waiting...")
        self.log("INFO", "=" * 50)

        # Start socket server in thread
        socket_thread = threading.Thread(target=self.start_socket_server)
        socket_thread.daemon = True
        socket_thread.start()

        # If no transcript yet, try to find it periodically
        if not self.transcript_path:
            for _ in range(30):  # Try for 30 seconds
                time.sleep(1)
                self.transcript_path = self._find_transcript()
                if self.transcript_path:
                    self.log("INFO", f"Found transcript: {self.transcript_path.name}")
                    break
                if not self.running:
                    break

        # Main monitoring loop
        if HAS_INOTIFY and self.transcript_path:
            self._run_inotify()
        else:
            self._run_polling()

        self._cleanup()

    def _run_inotify(self):
        """Watch transcript with inotify"""
        inotify = INotify()
        watch_flags = inotify_flags.MODIFY
        wd = inotify.add_watch(str(self.transcript_path), watch_flags)

        self.log("INFO", "Using inotify for file monitoring")

        while self.running:
            events = inotify.read(timeout=500)
            for event in events:
                if event.mask & inotify_flags.MODIFY:
                    self.process_new_lines()

        inotify.rm_watch(wd)

    def _run_polling(self):
        """Fallback polling mode"""
        self.log("WARN", "Using polling mode (inotify not available)")
        while self.running:
            self.process_new_lines()
            time.sleep(0.3)

    def _shutdown(self, signum, frame):
        """Handle shutdown signal"""
        self.log("INFO", "Shutting down...")
        self.running = False

    def _cleanup(self):
        """Cleanup on exit"""
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.log("INFO", "Watcher stopped")
        self.log("INFO", "=" * 50)


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    session_id = os.environ.get("CLAUDE_SESSION_ID")

    # Also accept session_id as argument
    if len(sys.argv) > 1:
        session_id = sys.argv[1]

    watcher = SessionWatcher(project_dir, session_id)
    watcher.run()


if __name__ == "__main__":
    main()
