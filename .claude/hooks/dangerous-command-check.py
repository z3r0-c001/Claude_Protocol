#!/usr/bin/env python3
"""
PreToolUse Dangerous Command Check for Claude Code
===================================================
Blocks dangerous bash commands before execution.
"""

import json
import sys
import re

DANGEROUS_PATTERNS = [
    # Filesystem destruction
    (r"rm\s+-rf\s+/(?:\s|$)", "Recursive deletion of root filesystem"),
    (r"rm\s+-rf\s+~", "Recursive deletion of home directory"),
    (r"rm\s+-rf\s+\*", "Recursive deletion with wildcard"),
    (r"rm\s+-rf\s+\.\*", "Recursive deletion of hidden files"),
    
    # Permission changes
    (r"chmod\s+777", "World-writable permissions"),
    (r"chmod\s+-R\s+777", "Recursive world-writable permissions"),
    
    # Piped execution (common malware vector)
    (r"curl\s+.*\|\s*(sh|bash)", "Piped curl to shell"),
    (r"wget\s+.*\|\s*(sh|bash)", "Piped wget to shell"),
    (r"curl\s+.*>\s*/tmp/.*&&\s*(sh|bash)", "Download and execute pattern"),
    
    # Disk operations
    (r"mkfs\.", "Filesystem formatting"),
    (r"dd\s+if=/dev/zero", "Disk zeroing"),
    (r"dd\s+if=/dev/random", "Disk randomization"),
    
    # Fork bomb
    (r":\(\)\{\s*:\|:&\s*\};:", "Fork bomb"),
    (r"\./$0\s*&\s*\./$0", "Process multiplication"),
    
    # Sudo with dangerous commands
    (r"sudo\s+rm\s+-rf", "Sudo recursive deletion"),
    (r"sudo\s+chmod\s+777", "Sudo world-writable"),
    
    # History/log destruction
    (r">\s*/var/log/", "Log file truncation"),
    (r"rm\s+.*\.bash_history", "History deletion"),
    (r"history\s+-c", "History clearing"),
    
    # Sensitive file access
    (r"cat\s+/etc/shadow", "Shadow file access"),
    (r"cat\s+/etc/passwd", "Passwd file access (may be okay, flagging)"),
]


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Failed to parse hook input: {e}", file=sys.stderr)
        sys.exit(1)
    
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    if tool_name != "Bash":
        sys.exit(0)
    
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)
    
    violations = []
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            violations.append(description)
    
    if violations:
        msg = "DANGEROUS COMMAND BLOCKED:\n\n"
        msg += f"  Command: {command[:100]}{'...' if len(command) > 100 else ''}\n\n"
        msg += "  Violations:\n"
        for v in violations:
            msg += f"    • {v}\n"
        msg += "\nUse a safer alternative or get explicit user approval."
        print(msg, file=sys.stderr)
        sys.exit(2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
