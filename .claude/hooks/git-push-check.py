#!/usr/bin/env python3
"""
Git Push Check - PreToolUse hook for Bash commands.

Runs git-push-guard.py when a git push command is detected.
"""

import os
import sys
import json
import subprocess

# Color support
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hook_colors import hook_status
except ImportError:
    def hook_status(*args, **kwargs): pass

def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        # No input or invalid JSON, allow
        return 0

    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')

    # Check if this is a git push command
    if 'git push' not in command and 'git push' not in command.replace('  ', ' '):
        # Not a git push, skip silently
        return 0

    hook_status("git-push-check", "CHECKING", "Validating push")

    # Run the git-push-guard
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    guard_script = os.path.join(project_dir, '.claude', 'hooks', 'git-push-guard.py')

    if not os.path.exists(guard_script):
        hook_status("git-push-check", "WARN", "Guard script not found")
        return 0

    result = subprocess.run(
        ['python3', guard_script],
        capture_output=False
    )

    if result.returncode != 0:
        hook_status("git-push-check", "BLOCK", "Guard check failed")
        print(json.dumps({
            "decision": "block",
            "reason": "Git push guard check failed. Fix commit messages before pushing."
        }))
        return 0

    hook_status("git-push-check", "OK", "Push allowed")
    return 0


if __name__ == '__main__':
    sys.exit(main())
