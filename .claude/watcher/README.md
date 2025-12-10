# Session Watcher

Real-time transcript monitor that validates Claude's responses before Stop hooks run.

## Problem Solved

Stop hooks cannot validate the **current** response because it's not written to the transcript yet when the hook fires. The watcher monitors the transcript file in real-time using `inotify` (or polling), capturing responses as they're written.

## Architecture

```
[Claude Code] --writes--> [transcript.jsonl]
                              |
                        [inotify watch]
                              v
                    [Session Watcher Daemon]
                              |
                    +---------+---------+
                    |                   |
                [Unix Socket]      [watcher.log]
                    |                   |
              [Stop Hooks]        [tmux/terminal]
```

## Files

| File | Purpose |
|------|---------|
| `session-watcher.py` | Core daemon - monitors transcript, validates responses, IPC server |
| `spawn-watcher.sh` | Launches watcher in tmux pane or terminal window |
| `ipc.sh` | Hook helper to query watcher via Unix socket |

## Auto-Spawn

The watcher auto-spawns on first prompt via `skill-activation-prompt.py` (UserPromptSubmit hook).

## IPC Commands

Query the watcher from any hook:

```bash
# Check if watcher is running
.claude/watcher/ipc.sh status
# Returns: {"running": true, "session": "...", "transcript": "..."}

# Get pending validation issues
.claude/watcher/ipc.sh get_pending
# Returns: {"has_issues": true, "issues": [...], "count": N}
# Or: {"has_issues": false}

# Clear pending issues
.claude/watcher/ipc.sh clear_pending
# Returns: {"ok": true}
```

## Adding New Validation Rules

Edit `session-watcher.py` and add a new check method:

```python
def _check_my_rule(self, response: str) -> list:
    """Check for my custom pattern"""
    issues = []
    if "bad pattern" in response.lower():
        issues.append({"type": "MY_RULE", "pattern": "bad pattern"})
    return issues
```

Then add it to `validate_response()`:

```python
def validate_response(self, response: str) -> list:
    all_issues = []
    all_issues.extend(self._check_laziness(response))
    all_issues.extend(self._check_honesty(response))
    all_issues.extend(self._check_my_rule(response))  # Add here
    return all_issues
```

## Integrating Stop Hooks with Watcher

For any Stop hook that needs to validate response text:

```bash
#!/bin/bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
IPC_SCRIPT="${PROJECT_DIR}/.claude/watcher/ipc.sh"

INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"decision": "approve"}'
    exit 0
fi

# Query watcher for issues
if [ -x "$IPC_SCRIPT" ]; then
    WATCHER_RESPONSE=$("$IPC_SCRIPT" get_pending 2>/dev/null)

    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == true' >/dev/null 2>&1; then
        # Filter for your specific issue types
        MY_ISSUES=$(echo "$WATCHER_RESPONSE" | jq -r '.issues[] | select(.type == "MY_RULE") | .pattern' | tr '\n' '; ')

        if [ -n "$MY_ISSUES" ]; then
            echo "[MY HOOK BLOCK] ${MY_ISSUES}" >&2
            echo '{"decision": "block", "reason": "My check failed: '"${MY_ISSUES}"'"}'
            exit 2
        fi
    fi

    # Watcher running, no issues for us
    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == false' >/dev/null 2>&1; then
        echo '{"decision": "approve"}'
        exit 0
    fi
fi

# Watcher not available - implement fallback or approve
echo '{"decision": "approve"}'
exit 0
```

## Current Validation Rules

| Rule | Type | Triggers |
|------|------|----------|
| Laziness | SUGGESTION | "you could", "i recommend you", etc. |
| Laziness | DELEGATION | "you need to", "make sure to", etc. |
| Laziness | SCOPE_REDUCTION | "for brevity", "beyond the scope", etc. |
| Honesty | OVERCONFIDENT | "definitely", "absolutely", etc. |
| Honesty | MISSING_UNCERTAINTY | Definitive claims without uncertainty markers |

## Unified Hook Logging

All hooks write to the same `watcher.log` file for centralized visibility. Each hook identifies itself with `[hook-name]` in the log.

### Log Format

```
[HH:MM:SS.mmm] [LEVEL] [hook-name] message
```

Example:
```
[12:34:56.789] [INFO ] [safety-check] Checking: ls -la...
[12:34:56.790] [OK   ] [safety-check] Command approved
[12:34:57.123] [INFO ] [completeness-check] Checking: main.py
[12:34:57.124] [BLOCK] [completeness-check] Placeholders found: task-marker
[12:34:58.456] [EVENT] [skill-activation] User prompt: How do I...
[12:34:58.789] [INFO ] [watcher] Assistant response (450 chars)
[12:34:58.790] [OK   ] [watcher] Response validated - no issues
```

### Hooks That Log

| Hook | Events Logged |
|------|---------------|
| `safety-check.sh` | Command checks, blocks |
| `completeness-check.sh` | File checks, placeholder blocks |
| `file-edit-tracker.sh` | File Write/Edit operations |
| `honesty-check.sh` | Honesty validation results |
| `laziness-check.sh` | Laziness validation results |
| `skill-activation-prompt.py` | User prompts, skill activations |
| `stop-verify.sh` | Session cleanup |
| `session-watcher.py` | Real-time response validation |

### Adding Logging to Custom Hooks

**Bash hooks**: Source the shared logger:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/hook-logger.sh"

hook_log "INFO" "Starting check"
hook_log "OK" "Check passed"
hook_log "BLOCK" "Issue found: reason"
```

**Python hooks**: Add logging function:

```python
from datetime import datetime
from pathlib import Path

def hook_log(level: str, message: str):
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    log_file = Path(project_dir) / ".claude" / "logs" / "watcher.log"
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [{level}] [my-hook] {message}\n")
```

### Log Lifecycle

- Log is **cleared on session start** by `spawn-watcher.sh`
- Log is **cleared on session end** by `stop-verify.sh`
- Log is **ephemeral** - not persisted across sessions

## Viewing Real-Time Logs

```bash
tail -f .claude/logs/watcher.log
```

Or attach to the tmux session:

```bash
tmux attach -t claude-watcher
```

## Cleanup

The watcher is automatically cleaned up by `stop-verify.sh` when the session ends.

Manual cleanup:

```bash
tmux kill-session -t claude-watcher
rm -f .claude/flags/watcher.pid .claude/flags/watcher.socket
```
