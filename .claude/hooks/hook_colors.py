#!/usr/bin/env python3
"""
hook_colors.py - Backward compatibility wrapper

This module re-exports from colors.py for backward compatibility.
New code should import from colors.py directly.
"""

import os
import sys

# Add hooks directory to path for colors import
_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from colors import (
    ANSI,
    COLORS_ENABLED,
    get_hook_theme,
    get_status_symbol,
    format_hook_status,
    hook_status,
    set_current_hook,
    status,
)

# Legacy aliases
RESET = ANSI.RESET
BOLD = ANSI.BOLD

def get_hook_color(hook_name: str) -> str:
    """Legacy function - returns combined fg+bg code."""
    fg, bg = get_hook_theme(hook_name)
    return f"{fg}{bg}{ANSI.BOLD}"

def hook_compact(hook_name: str, status_str: str) -> None:
    """Output a compact one-line colored status."""
    fg, bg = get_hook_theme(hook_name)
    print(f"{fg}{bg}{ANSI.BOLD} {status_str} {ANSI.RESET}", file=sys.stderr)

def hook_banner(hook_name: str, message: str = "") -> None:
    """Output a banner-style status."""
    fg, bg = get_hook_theme(hook_name)
    display_name = hook_name.replace("-", " ").upper()
    width = max(len(display_name) + 10, 40)
    border = "-" * width
    padding = " " * (width - len(display_name) - 4)
    
    banner = f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|  {display_name}{padding}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
"""
    print(banner, file=sys.stderr)
    if message:
        print(f"  {message}", file=sys.stderr)

# Re-export STATUS_ICONS for compatibility
STATUS_ICONS = {
    "START": ">",
    "CHECKING": ">",
    "RUNNING": ">",
    "OK": "+",
    "PASS": "+",
    "CONTINUE": "+",
    "BLOCK": "X",
    "FAIL": "X",
    "ERROR": "X",
    "WARN": "!",
    "SKIP": "-",
}
