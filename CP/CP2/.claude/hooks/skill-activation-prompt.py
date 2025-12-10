#!/usr/bin/env python3
"""
Skill Auto-Activation Hook (UserPromptSubmit)

Analyzes user prompts and suggests relevant skills based on:
- Keyword matching
- Intent pattern matching
- Detects verification triggers and sets flag for Stop hook
- Auto-spawns Session Watcher on first prompt

Configuration: .claude/skills/skill-rules.json
"""
import json
import sys
import re
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Verification trigger keywords
VERIFY_TRIGGERS = [
    "best practice",
    "should i",
    "how should",
    "correct way",
    "recommended",
    "standard",
    "pattern",
    "convention",
    "proper way",
    "official",
    "according to",
    "the right way",
    "implementation",
    "architecture"
]

def get_project_dir():
    """Get project directory from environment or current directory"""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

def hook_log(level: str, message: str):
    """Write to shared watcher log"""
    project_dir = get_project_dir()
    log_file = Path(project_dir) / ".claude" / "logs" / "watcher.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    colors = {
        "INFO": "\033[36m",
        "WARN": "\033[33m",
        "ERROR": "\033[31m",
        "BLOCK": "\033[31;1m",
        "OK": "\033[32m",
        "EVENT": "\033[35m"
    }
    color = colors.get(level, "")
    reset = "\033[0m"
    
    line = f"[{timestamp}] {color}[{level}]{reset} [skill-activation] {message}\n"
    with open(log_file, "a") as f:
        f.write(line)

def load_skill_rules():
    """Load skill activation rules from skill-rules.json"""
    project_dir = get_project_dir()
    rules_path = Path(project_dir) / ".claude" / "skills" / "skill-rules.json"
    
    if rules_path.exists():
        try:
            return json.loads(rules_path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def check_prompt_triggers(prompt: str, rules: dict) -> list:
    """Check prompt against keyword and intent triggers"""
    matched = []
    prompt_lower = prompt.lower()
    
    for skill_name, config in rules.items():
        triggers = config.get("promptTriggers", {})
        
        # Check keywords
        keywords = triggers.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched.append({
                    "skill": skill_name,
                    "trigger": f"keyword: {kw}",
                    "priority": config.get("priority", "medium")
                })
                break
        
        # Check intent patterns (if not already matched by keyword)
        if skill_name not in [m["skill"] for m in matched]:
            patterns = triggers.get("intentPatterns", [])
            for pattern in patterns:
                try:
                    if re.search(pattern, prompt_lower, re.IGNORECASE):
                        matched.append({
                            "skill": skill_name,
                            "trigger": f"pattern: {pattern[:30]}...",
                            "priority": config.get("priority", "medium")
                        })
                        break
                except re.error:
                    continue
    
    return matched

def should_verify(prompt: str) -> bool:
    """Check if prompt contains verification triggers"""
    prompt_lower = prompt.lower()
    return any(trigger in prompt_lower for trigger in VERIFY_TRIGGERS)

def set_verify_flag(prompt: str):
    """Set flag file for Stop hook to pick up"""
    project_dir = get_project_dir()
    flags_dir = Path(project_dir) / ".claude" / "flags"
    flags_dir.mkdir(parents=True, exist_ok=True)

    flag_file = flags_dir / "verify-pending.json"
    flag_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:500]  # Truncate long prompts
    }
    flag_file.write_text(json.dumps(flag_data))


def ensure_watcher_running():
    """Spawn session watcher if not already running"""
    project_dir = Path(get_project_dir())
    pid_file = project_dir / ".claude" / "flags" / "watcher.pid"
    spawn_script = project_dir / ".claude" / "watcher" / "spawn-watcher.sh"

    # Check if spawn script exists
    if not spawn_script.exists():
        return False

    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process is alive
            os.kill(pid, 0)
            return True  # Already running
        except (OSError, ValueError):
            # Process dead or invalid PID, clean up
            pid_file.unlink(missing_ok=True)

    # Spawn watcher in background
    try:
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
        subprocess.Popen(
            ["bash", str(spawn_script)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True
        )
        hook_log("INFO", "Watcher spawned")
        return True
    except Exception as e:
        hook_log("ERROR", f"Failed to spawn watcher: {e}")
        return False

def make_output(additional_context=None):
    """Create properly formatted UserPromptSubmit output"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit"
        }
    }
    if additional_context:
        output["hookSpecificOutput"]["additionalContext"] = additional_context
    return output

def main():
    # Auto-spawn watcher on first prompt (runs in background)
    ensure_watcher_running()

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_log("WARN", "Invalid JSON input")
        print(json.dumps(make_output()))
        sys.exit(0)

    prompt = input_data.get("prompt", "")

    if not prompt:
        print(json.dumps(make_output()))
        sys.exit(0)

    # Log prompt preview
    prompt_preview = prompt[:50].replace('\n', ' ')
    hook_log("EVENT", f"User prompt: {prompt_preview}...")

    # Check for skill triggers
    rules = load_skill_rules()
    matched_skills = check_prompt_triggers(prompt, rules)
    
    # Check for verification triggers
    needs_verification = should_verify(prompt)
    
    # Build output
    messages = []
    
    if matched_skills:
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        matched_skills.sort(key=lambda x: priority_order.get(x["priority"], 1))
        
        skills_list = ", ".join([m["skill"] for m in matched_skills])
        messages.append(f"SKILL ACTIVATION: Load skill(s): {skills_list}")
        hook_log("INFO", f"Skills activated: {skills_list}")
    
    if needs_verification:
        set_verify_flag(prompt)
        messages.append("VERIFICATION QUEUED: Answer will be checked against docs")
        hook_log("INFO", "Verification queued")
    
    # Output proper UserPromptSubmit format
    if messages:
        print(json.dumps(make_output(" | ".join(messages))))
    else:
        hook_log("OK", "Processed")
        print(json.dumps(make_output()))
    sys.exit(0)

if __name__ == "__main__":
    main()
