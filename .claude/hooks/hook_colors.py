#!/usr/bin/env python3
"""
hook_colors.py - Backward compatibility wrapper

All output functionality now lives in colors.py.
This file re-exports for existing imports.

IMPORTANT: ANSI colors do NOT work in Claude Code hooks.
The color functions now return plain text.
"""

from colors import (
    # Constants
    RESET,
    BOLD,
    ICONS,
    BOX,
    HOOK_EVENTS,
    # Plain text formatting (what actually works)
    format_banner,
    format_status,
    format_agent_banner,
    format_confidence,
    # JSON output (the correct way to communicate)
    json_output,
    output_context,
    output_block,
    # Status line only (ANSI works here)
    StatusLine,
    # Legacy functions (now return plain text)
    hook_status,
    agent_banner,
    get_hook_color,
    get_agent_color,
    red,
    green,
    yellow,
    blue,
    cyan,
    magenta,
    bold,
)

# Alias for compact status
def compact(hook_name: str, status: str) -> None:
    """Output a compact status line."""
    hook_status(hook_name, status)

# Legacy constant (empty - colors don't work)
HOOK_COLORS = {}
DEFAULT_COLOR = ""
STATUS_ICONS = ICONS
COLORS_ENABLED = False  # Colors don't work in hooks
