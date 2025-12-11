#!/usr/bin/env python3
"""
Context Loader Hook (UserPromptSubmit)

Loads pending violations and reminders into context.
"""
import json
import sys
import os
from pathlib import Path

def get_project_dir():
    return Path(os.getcwd())

def load_json_file(filepath):
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except (json.JSONDecodeError, IOError):
        pass
    return None

def safe_delete(filepath):
    try:
        if filepath.exists():
            filepath.unlink()
    except (IOError, OSError):
        pass

def main():
    # Read and discard stdin
    try:
        sys.stdin.read()
    except Exception:
        pass

    project_dir = get_project_dir()
    claude_dir = project_dir / ".claude"
    context_parts = []

    # Load pending violations
    violations_file = claude_dir / "memory" / "pending-violations.json"
    violations = load_json_file(violations_file)
    if violations and violations.get("violations"):
        context_parts.append(
            "PENDING VIOLATIONS:\n" +
            "\n".join(f"  - {v}" for v in violations["violations"])
        )
        safe_delete(violations_file)

    # Load reminders
    reminders_file = claude_dir / "memory" / "reminders.json"
    reminders = load_json_file(reminders_file)
    if reminders and reminders.get("active"):
        context_parts.append(
            "REMINDERS:\n" +
            "\n".join(f"  - {r}" for r in reminders["active"])
        )

    # Output context if any
    if context_parts:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n---\n".join(context_parts)
            }
        }
        print(json.dumps(output))

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
