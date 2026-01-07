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
import os
from typing import Optional

# Import hook colors utility
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from hook_colors import hook_status, set_current_hook
    set_current_hook("pretool-laziness-check")
except ImportError:
    def hook_status(*args, **kwargs): pass

# =============================================================================
# FILE PATH EXCEPTIONS
# =============================================================================

# Files that legitimately contain "lazy" patterns as OUTPUT (templates, generators)
GENERATOR_PATTERNS = [
    # Generator files
    r'_gen\.py$',           # python_gen.py, test_gen.py
    r'gen_\w+\.py$',        # gen_tests.py
    r'_generator\.py$',     # code_generator.py
    r'generator\.py$',      # generator.py
    r'Generator\.[tj]sx?$', # CodeGenerator.ts, TestGenerator.js
    r'generate_\w+\.py$',   # generate_tests.py
    r'codegen',             # Any codegen file
    
    # Directories
    r'/generators?/',       # generators/ directory
    r'/templates?/',        # templates/ directory
    r'/fixtures?/',         # test fixtures
    r'/stubs?/',           # stub files
    r'/scaffolds?/',       # scaffold files
    r'/skeleton/',         # skeleton code
    r'/boilerplate/',      # boilerplate code
    
    # File patterns
    r'\.template\.',        # file.template.py
    r'_template\.',         # file_template.ts
    r'\.stub\.',           # file.stub.ts
    r'\.skeleton\.',       # file.skeleton.py
    r'\.boilerplate\.',    # file.boilerplate.ts
    
    # Frameworks
    r'cookiecutter',       # cookiecutter templates
    r'jinja2?',            # jinja templates
    r'mustache',           # mustache templates
    r'handlebars',         # handlebars templates
]

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


def is_generator_file(file_path: str) -> bool:
    """Check if this file is a template/generator that legitimately outputs lazy patterns."""
    for pattern in GENERATOR_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def extract_content(tool_input: dict, tool_name: str) -> Optional[str]:
    """Extract the content being written from the tool input."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name in ("Edit", "MultiEdit"):
        # Edit tools have new_string or similar
        return tool_input.get("new_string", tool_input.get("new_str", ""))
    return None


def is_string_literal_context(line: str, match_start: int) -> bool:
    """Check if the match position is inside a string literal."""
    # Look for string delimiters before the match
    before = line[:match_start]
    
    # Count quotes (simple heuristic - not perfect but catches most cases)
    single_quotes = before.count("'") - before.count("\\'")
    double_quotes = before.count('"') - before.count('\\"')
    triple_single = before.count("'''")
    triple_double = before.count('"""')
    
    # If odd number of quotes, we're inside a string
    in_single = (single_quotes - triple_single * 3) % 2 == 1
    in_double = (double_quotes - triple_double * 3) % 2 == 1
    
    return in_single or in_double


def is_string_assignment_line(line: str) -> bool:
    """Check if this line is assigning a string constant (template output)."""
    stripped = line.strip()
    
    # Pattern: VARIABLE = "string" or VARIABLE = 'string' or VARIABLE = '''string'''
    # Uppercase constants are almost always template definitions
    if re.match(r'^[A-Z_][A-Z0-9_]*\s*=\s*[frFRbBuU]?["\']', stripped):
        return True
    
    # Pattern: "key": "value" in dicts (template definitions)
    if re.match(r'^["\'][^"\']+["\']\s*:\s*["\']', stripped):
        return True
    
    # Pattern: variable = f"..." or variable = r"..." (any prefix string)
    if re.match(r'^\w+\s*=\s*[frFRbBuU]{0,2}["\']', stripped):
        # But not if it's a function call result
        if '(' not in stripped.split('=')[0]:
            return True
    
    # Lines in arrays/lists: "string",
    if re.match(r'^[frFRbBuU]{0,2}["\'].*["\'],?\s*$', stripped):
        return True
    
    # Docstrings (triple quoted)
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return True
    
    # Return statements with strings: return "..."
    if re.match(r'^return\s+[frFRbBuU]{0,2}["\']', stripped):
        return True
    
    # Yield statements with strings
    if re.match(r'^yield\s+[frFRbBuU]{0,2}["\']', stripped):
        return True
    
    # Template string methods: .format(, % formatting, f-strings
    if '.format(' in stripped or '% ' in stripped:
        return True
        
    return False


def is_inside_multiline_string(lines: list[str], line_num: int) -> bool:
    """Check if current line is inside a multiline string."""
    triple_double = 0
    triple_single = 0
    
    for i in range(line_num):
        line = lines[i]
        # Count triple quotes (simple approach - not perfect)
        triple_double += line.count('"""') 
        triple_single += line.count("'''")
    
    # If odd number of triple quotes, we're inside a multiline string
    return (triple_double % 2 == 1) or (triple_single % 2 == 1)


def has_template_marker(content: str) -> bool:
    """Check if content has markers indicating it's a template/generator."""
    markers = [
        # Explicit markers
        'TEMPLATE',
        '_TEMPLATE',
        'MARKER',
        '_MARKER',
        'PLACEHOLDER',
        '_PLACEHOLDER',
        'OUTPUT_',
        'GENERATED_',
        'SCAFFOLD',
        'BOILERPLATE',
        'STUB_',
        '_STUB',
        
        # Comment markers
        '# Template',
        '// Template',
        '/* Template',
        '# Generator',
        '// Generator',
        '# This file generates',
        '// This file generates',
        
        # Description phrases
        'will appear in OUTPUT',
        'will be output',
        'generated file',
        'generated code',
        'template output',
        'template string',
        'output template',
        'code generation',
        'generates code',
        'produces output',
        'emits code',
    ]
    # Check first 50 lines or 2000 chars
    first_lines = '\n'.join(content.split('\n')[:50])[:2000]
    content_upper = first_lines.upper()
    return any(m.upper() in content_upper for m in markers)


def check_content(content: str, file_path: str = "") -> list[dict]:
    """Check content for laziness patterns. Returns list of violations."""
    violations = []
    lines = content.split("\n")
    
    # If file has template markers, be more lenient
    is_template_content = has_template_marker(content)

    for category, config in PATTERNS.items():
        for pattern in config["patterns"]:
            for line_num, line in enumerate(lines, 1):
                # Skip noqa lines
                if "noqa" in line.lower() or "nolint" in line.lower():
                    continue
                    
                # Skip lines with laziness-ok marker
                if "laziness-ok" in line.lower() or "template-ok" in line.lower():
                    continue
                
                # Skip string assignment lines (template output definitions)
                if is_string_assignment_line(line):
                    continue
                
                # Skip if inside multiline string
                if is_inside_multiline_string(lines, line_num - 1):
                    continue
                
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Skip if match is inside a string literal
                    if is_string_literal_context(line, match.start()):
                        continue
                    
                    # For template files, only flag delegation patterns (actual laziness)
                    if is_template_content and category not in ["delegation_phrases"]:
                        continue
                    
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
    lines.append("\nNOTE: If this is a template/generator file, add '# laziness-ok' to the line")
    lines.append("or ensure template strings are in UPPERCASE_CONSTANTS.")
    return "\n".join(lines)


def output_json(decision: str, reason: str = "", block_message: str = ""):
    """Output properly formatted JSON for Claude Code hooks."""
    if decision == "continue":
        print('{"continue": true}')
        return
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

    file_path = tool_input.get("file_path", "")
    
    # Skip documentation files - they may describe patterns without being lazy
    skip_extensions = [".md", ".rst", ".txt", ".mdx"]
    if any(file_path.endswith(ext) for ext in skip_extensions):
        output_json("continue")
        sys.exit(0)
    
    # Skip generator/template files entirely - they legitimately output "lazy" patterns
    if is_generator_file(file_path):
        hook_status("pretool-laziness-check", "SKIP", "generator/template file")
        output_json("continue")
        sys.exit(0)

    hook_status("pretool-laziness-check", "CHECKING", os.path.basename(file_path))

    # Extract content
    content = extract_content(tool_input, tool_name)
    if not content:
        output_json("continue")
        sys.exit(0)

    # Check for violations
    violations = check_content(content, file_path)

    # Filter to critical only for blocking
    critical_violations = [v for v in violations if v["severity"] == "critical"]

    if critical_violations:
        hook_status("pretool-laziness-check", "BLOCK", f"{len(critical_violations)} issues")
        # Block with formatted message
        output_json("block", block_message=format_violations(violations))
        sys.exit(0)

    # All good
    hook_status("pretool-laziness-check", "OK", "No lazy code")
    output_json("continue")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Absolute fallback - always output valid JSON
        print('{"continue": true}')
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
