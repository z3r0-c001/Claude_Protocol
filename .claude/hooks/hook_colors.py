#!/usr/bin/env python3
"""
hook_colors.py - Colored output utility for Python hooks
Import this module to get colored hook status indicators

This is the v1.1.10 version that works in Claude Code.
"""

import sys
import os

# ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"

# Hook color schemes: background + foreground
HOOK_COLORS = {
    # PreToolUse hooks - warm colors
    "pre-write-check": "\033[1;97;41m",           # White on Red
    "pretool-laziness-check": "\033[1;30;43m",    # Black on Yellow
    "pretool-hallucination-check": "\033[1;97;45m",  # White on Magenta
    "dangerous-command-check": "\033[1;97;101m",  # White on Bright Red
    "agent-announce": "\033[1;30;104m",           # Black on Bright Blue
    "agent-plan-enforcer": "\033[1;97;44m",       # White on Blue
    "model-audit": "\033[1;30;46m",               # Black on Cyan

    # PostToolUse hooks - cool colors
    "post-write-validate": "\033[1;97;44m",       # White on Blue
    "file-edit-tracker": "\033[1;30;46m",         # Black on Cyan
    "context-detector": "\033[1;30;42m",          # Black on Green
    "research-quality-check": "\033[1;97;104m",   # White on Bright Blue
    "doc-size-detector": "\033[1;30;106m",        # Black on Bright Cyan

    # UserPromptSubmit hooks - green spectrum
    "context-loader": "\033[1;30;102m",           # Black on Bright Green
    "skill-activation-prompt": "\033[1;97;42m",   # White on Green

    # Stop hooks - neutral/warning
    "laziness-check": "\033[1;30;103m",           # Black on Bright Yellow
    "honesty-check": "\033[1;97;105m",            # White on Bright Magenta
    "stop-verify": "\033[1;30;47m",               # Black on White

    # SubagentStop hooks
    "research-validator": "\033[1;97;102m",       # White on Bright Green
    "agent-handoff-validator": "\033[1;30;107m",  # Black on Bright White
    "agent-response-handler": "\033[1;97;44m",    # White on Blue
}

# Default for unknown hooks
DEFAULT_COLOR = "\033[1;97;100m"  # White on Bright Black

# Status icons
STATUS_ICONS = {
    "START": "▶",
    "CHECKING": "▶",
    "RUNNING": "▶",
    "OK": "✓",
    "PASS": "✓",
    "CONTINUE": "✓",
    "BLOCK": "✗",
    "FAIL": "✗",
    "ERROR": "✗",
    "WARN": "⚠",
    "SKIP": "⚠",
}

# For compatibility
COLORS_ENABLED = True


def get_hook_name(script_path: str = None) -> str:
    """Extract hook name from script path or __file__."""
    if script_path is None:
        # Try to get from caller's __file__
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            script_path = frame.f_back.f_globals.get("__file__", "unknown")

    name = os.path.basename(script_path)
    name = name.replace(".py", "").replace(".sh", "")
    return name


def get_hook_color(hook_name: str) -> str:
    """Get ANSI color code for a hook."""
    return HOOK_COLORS.get(hook_name, DEFAULT_COLOR)


def hook_status(hook_name: str, status: str, detail: str = "") -> None:
    """
    Output colored hook status to stderr.

    Args:
        hook_name: Name of the hook (e.g., "pre-write-check")
        status: Status string (e.g., "START", "OK", "BLOCK")
        detail: Optional detail message
    """
    color = get_hook_color(hook_name)
    icon = STATUS_ICONS.get(status.upper(), "⚡")

    # Format display name
    display_name = hook_name.replace("-", " ").title()

    if detail:
        msg = f"{color} {icon} {display_name}: {status} {RESET} {detail}"
    else:
        msg = f"{color} {icon} {display_name}: {status} {RESET}"

    print(msg, file=sys.stderr)


def hook_compact(hook_name: str, status: str) -> None:
    """Output a compact one-line colored status."""
    color = get_hook_color(hook_name)
    print(f"{color} {status} {RESET}", file=sys.stderr)


def hook_banner(hook_name: str, message: str = "") -> None:
    """Output a more prominent banner-style status."""
    color = get_hook_color(hook_name)
    display_name = hook_name.replace("-", " ").upper()
    width = max(len(display_name) + 10, 40)

    border = "━" * width
    padding = " " * (width - len(display_name) - 4)

    banner = f"""
{color}┏{border}┓{RESET}
{color}┃  {display_name}{padding}┃{RESET}
{color}┗{border}┛{RESET}
"""
    print(banner, file=sys.stderr)
    if message:
        print(f"  {message}", file=sys.stderr)


# Auto-detect hook name when module is imported
_current_hook = None


def set_current_hook(name: str) -> None:
    """Set the current hook name for simplified API."""
    global _current_hook
    _current_hook = name


def status(status_str: str, detail: str = "") -> None:
    """Simplified status output using auto-detected hook name."""
    global _current_hook
    if _current_hook is None:
        _current_hook = get_hook_name()
    hook_status(_current_hook, status_str, detail)


def compact(status_str: str) -> None:
    """Simplified compact output using auto-detected hook name."""
    global _current_hook
    if _current_hook is None:
        _current_hook = get_hook_name()
    hook_compact(_current_hook, status_str)


# Compatibility with colors.py imports
def get_hook_theme(hook_name: str) -> tuple:
    """Get color tuple for compatibility."""
    color = get_hook_color(hook_name)
    return (color, "")


def get_status_symbol(status: str) -> str:
    """Get symbol for a status."""
    return STATUS_ICONS.get(status.upper(), "⚡")


def format_hook_status(hook_name: str, status: str, detail: str = "") -> str:
    """Format a colored hook status line (returns string)."""
    color = get_hook_color(hook_name)
    icon = STATUS_ICONS.get(status.upper(), "⚡")
    display_name = hook_name.replace("-", " ").title()

    if detail:
        return f"{color} {icon} {display_name}: {status} {RESET} {detail}"
    return f"{color} {icon} {display_name}: {status} {RESET}"
