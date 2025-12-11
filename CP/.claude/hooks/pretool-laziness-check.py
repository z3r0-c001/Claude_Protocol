#!/usr/bin/env python3
"""
PreToolUse Laziness Check for Claude Code
==========================================
This hook runs BEFORE Write/Edit/MultiEdit tools execute.
If laziness patterns are detected in the content, it exits with code 2
and writes the violations to stderr, which blocks the tool and feeds
the error back to Claude.

Install:
  1. Copy to .claude/hooks/pretool-laziness-check.py
  2. chmod +x .claude/hooks/pretool-laziness-check.py
  3. Add to .claude/settings.json (see bottom of file)
"""

import json
import sys
import re
from typing import Optional

# =============================================================================
# DETECTION PATTERNS
# =============================================================================

PATTERNS = {
    "placeholder_comments": {
        "severity": "critical",
        "patterns": [
            r"//\s*\.\.\.",           # // ...
            r"#\s*\.\.\.",            # # ...
            r"/\*\s*\.\.\.\s*\*/",    # /* ... */
            r"<!--\s*\.\.\.\s*-->",   # <!-- ... -->
        ],
        "message": "Placeholder comment found"
    },
    "todo_fixme": {
        "severity": "critical",
        "patterns": [
            r"//\s*TODO\b",
            r"#\s*TODO\b",
            r"//\s*FIXME\b",
            r"#\s*FIXME\b",
            r"/\*\s*TODO\b",
            r"/\*\s*FIXME\b",
        ],
        "message": "TODO/FIXME marker found - complete the implementation"
    },
    "stub_implementations": {
        "severity": "critical",
        "patterns": [
            r"raise\s+NotImplementedError",            # Python
            r"throw\s+new\s+NotImplementedError",      # JS/TS
            r"throw\s+new\s+Error\(['\"]not implemented",  # JS/TS
            r"unimplemented!\(\)",                     # Rust
            r"todo!\(\)",                              # Rust
            r"panic!\(['\"]not implemented",           # Rust
        ],
        "message": "Stub implementation found - provide real code"
    },
    "delegation_phrases": {
        "severity": "critical",
        "patterns": [
            r"you\s+could\b",
            r"you\s+might\s+want\s+to\b",
            r"you('ll|\s+will)\s+need\s+to\b",
            r"consider\s+adding\b",
            r"left\s+as\s+an?\s+exercise",
            r"implement\s+this\s+yourself",
            r"add\s+your\s+(own\s+)?logic\s+here",
            r"replace\s+with\s+your",
        ],
        "message": "Delegation to user found - do the work, don't describe it"
    },
    "incomplete_markers": {
        "severity": "major",
        "patterns": [
            r"//\s*add\s+more\s+here",
            r"#\s*add\s+more\s+here",
            r"//\s*etc\.?\s*$",
            r"#\s*etc\.?\s*$",
            r"//\s*and\s+so\s+on",
            r"#\s*and\s+so\s+on",
            r"\.\.\.\s*//",                # code... // 
            r"//\s*\[.*implement.*\]",     # // [implement X]
            r"#\s*\[.*implement.*\]",      # # [implement X]
        ],
        "message": "Incomplete marker found"
    },
}


def extract_content(tool_input: dict, tool_name: str) -> Optional[str]:
    """Extract the content being written from the tool input."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name in ("Edit", "MultiEdit"):
        # Edit tools have new_string or similar
        return tool_input.get("new_string", tool_input.get("new_str", ""))
    return None


def is_string_literal_line(line: str) -> bool:
    """Check if line is defining a string literal (pattern definition, etc.)."""
    stripped = line.strip()
    # Lines that are string definitions in arrays/dicts
    if re.match(r'^["\'].*["\'],?\s*$', stripped):
        return True
    # Lines with r"..." raw strings (regex patterns)
    if re.match(r'^r["\'].*["\'],?\s*$', stripped):
        return True
    # Lines defining patterns in arrays like:  "pattern",
    if re.match(r'^["\'].*["\'],?\s*(#.*)?$', stripped):
        return True
    return False


def check_content(content: str) -> list[dict]:
    """Check content for laziness patterns. Returns list of violations."""
    violations = []
    lines = content.split("\n")

    for category, config in PATTERNS.items():
        for pattern in config["patterns"]:
            for line_num, line in enumerate(lines, 1):
                # Skip noqa lines
                if "noqa" in line.lower() or "nolint" in line.lower():
                    continue
                # Skip string literal definitions (avoids false positives on pattern arrays)
                if is_string_literal_line(line):
                    continue
                if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                    violations.append({
                        "category": category,
                        "severity": config["severity"],
                        "message": config["message"],
                        "line": line_num,
                        "content": line.strip()[:80],
                        "pattern": pattern,
                    })

    return violations


def format_violations(violations: list[dict]) -> str:
    """Format violations for stderr output."""
    lines = ["LAZINESS CHECK FAILED - Fix these issues before writing:\n"]
    
    critical = [v for v in violations if v["severity"] == "critical"]
    major = [v for v in violations if v["severity"] == "major"]
    
    if critical:
        lines.append("CRITICAL (must fix):")
        for v in critical:
            lines.append(f"  Line {v['line']}: {v['message']}")
            lines.append(f"    → {v['content']}")
    
    if major:
        lines.append("\nMAJOR (should fix):")
        for v in major:
            lines.append(f"  Line {v['line']}: {v['message']}")
            lines.append(f"    → {v['content']}")
    
    lines.append("\nProvide complete, working code with no placeholders.")
    return "\n".join(lines)


def output_json(decision: str, reason: str = "", block_message: str = ""):
    """Output properly formatted JSON for Claude Code hooks."""
    result = {"decision": decision}
    if reason:
        result["reason"] = reason
    if block_message:
        result["message"] = block_message
    print(json.dumps(result))


def main():
    # Read JSON input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        output_json("continue")
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write/Edit/MultiEdit
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        output_json("continue")
        sys.exit(0)

    # Skip documentation files - they may describe patterns without being lazy
    file_path = tool_input.get("file_path", "")
    skip_extensions = [".md", ".rst", ".txt", ".mdx"]
    if any(file_path.endswith(ext) for ext in skip_extensions):
        output_json("continue")
        sys.exit(0)

    # Extract content
    content = extract_content(tool_input, tool_name)
    if not content:
        output_json("continue")
        sys.exit(0)

    # Check for violations
    violations = check_content(content)

    # Filter to critical only for blocking
    critical_violations = [v for v in violations if v["severity"] == "critical"]

    if critical_violations:
        # Block with formatted message
        output_json("block", block_message=format_violations(violations))
        sys.exit(0)

    # All good
    output_json("continue")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Absolute fallback - always output valid JSON
        print('{"decision": "continue"}')
        sys.exit(0)


# =============================================================================
# SETTINGS.JSON CONFIGURATION
# =============================================================================
# Add this to your .claude/settings.json:
#
# {
#   "hooks": {
#     "PreToolUse": [
#       {
#         "matcher": "Write|Edit|MultiEdit",
#         "hooks": [
#           {
#             "type": "command",
#             "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/pretool-laziness-check.py\""
#           }
#         ]
#       }
#     ]
#   }
# }
