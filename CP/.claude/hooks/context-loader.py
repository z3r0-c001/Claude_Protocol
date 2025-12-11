#!/usr/bin/env python3
"""
UserPromptSubmit Context Loader for Claude Code
================================================
Injects context at the start of each prompt:
- Pending violations from previous responses
- Laziness violations (from Stop hook)
- Project reminders

stdout is added to Claude's context (exit 0)
"""

import json
import sys
import os
from pathlib import Path


def get_project_dir():
    """Get project directory from cwd"""
    return Path(os.getcwd())


def load_json_file(filepath):
    """Safely load JSON file, return None on error"""
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except (json.JSONDecodeError, IOError, OSError):
        return None
    return None


def load_text_file(filepath):
    """Safely load text file, return None on error"""
    try:
        if filepath.exists():
            return filepath.read_text().strip()
    except (IOError, OSError):
        return None
    return None


def safe_delete(filepath):
    """Safely delete file, ignore errors"""
    try:
        if filepath.exists():
            filepath.unlink()
    except (IOError, OSError):
        return  # Silently ignore deletion errors


def main():
    project_dir = get_project_dir()
    claude_dir = project_dir / ".claude"

    context_parts = []

    # Load pending violations (JSON format)
    violations_file = claude_dir / "memory" / "pending-violations.json"
    violations = load_json_file(violations_file)
    if violations and violations.get("violations"):
        context_parts.append(
            "PENDING VIOLATIONS FROM PREVIOUS RESPONSE:\n" +
            "\n".join(f"  - {v}" for v in violations["violations"]) +
            "\n\nFix these before proceeding with new work."
        )
        safe_delete(violations_file)

    # Load laziness violations (markdown format - legacy)
    laziness_file = claude_dir / "flags" / "laziness-violation.md"
    laziness_content = load_text_file(laziness_file)
    if laziness_content:
        context_parts.append(
            "LAZINESS VIOLATION DETECTED:\n" + laziness_content +
            "\n\nYou must address this issue."
        )
        safe_delete(laziness_file)

    # Load project reminders
    reminders_file = claude_dir / "memory" / "reminders.json"
    reminders = load_json_file(reminders_file)
    if reminders and reminders.get("active"):
        context_parts.append(
            "PROJECT REMINDERS:\n" +
            "\n".join(f"  - {r}" for r in reminders["active"])
        )

    # Output as JSON with decision
    output = {"ok": True}
    if context_parts:
        output["context"] = "\n---\n".join(context_parts)

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
