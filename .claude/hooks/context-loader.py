#!/usr/bin/env python3
"""
UserPromptSubmit Context Loader for Claude Code
================================================
Injects context at the start of each prompt:
- Pending violations from previous responses
- Project reminders
- Session state

stdout is added to Claude's context (exit 0)
"""

import json
import sys
from pathlib import Path

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    
    # Find project directory
    cwd = input_data.get("cwd", "")
    claude_dir = Path(cwd) / ".claude"
    
    context_parts = []
    
    # Load pending violations (from previous blocked responses)
    violations_file = claude_dir / "memory" / "pending-violations.json"
    if violations_file.exists():
        try:
            violations = json.loads(violations_file.read_text())
            if violations.get("violations"):
                context_parts.append(
                    "⚠️ PENDING VIOLATIONS FROM PREVIOUS RESPONSE:\n" +
                    "\n".join(f"  • {v}" for v in violations["violations"]) +
                    "\n\nFix these before proceeding with new work."
                )
                # Clear after loading
                violations_file.unlink()
        except (json.JSONDecodeError, IOError):
            pass
    
    # Load project reminders
    reminders_file = claude_dir / "memory" / "reminders.json"
    if reminders_file.exists():
        try:
            reminders = json.loads(reminders_file.read_text())
            if reminders.get("active"):
                context_parts.append(
                    "📌 PROJECT REMINDERS:\n" +
                    "\n".join(f"  • {r}" for r in reminders["active"])
                )
        except (json.JSONDecodeError, IOError):
            pass
    
    # Output context (will be added to Claude's context)
    if context_parts:
        print("\n---\n".join(context_parts))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
