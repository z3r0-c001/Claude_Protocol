#!/usr/bin/env python3
"""
hook_colors.py - Backward compatibility wrapper

All color functionality now lives in colors.py.
This file re-exports for existing imports.

DO NOT add new functionality here - add to colors.py instead.
"""

from colors import (
    # Constants
    RESET,
    BOLD,
    HOOK_COLORS,
    DEFAULT_COLOR,
    STATUS_ICONS,
    COLORS_ENABLED,
    # Functions
    get_hook_name,
    get_hook_color,
    hook_status,
    hook_compact,
    hook_banner,
    set_current_hook,
    status,
    get_hook_theme,
    get_status_symbol,
    format_hook_status,
)

# Alias for hook_colors-specific function name
compact = hook_compact
