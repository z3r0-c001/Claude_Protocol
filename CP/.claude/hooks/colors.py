#!/usr/bin/env python3
"""
colors.py - Hook output system for Claude Code

IMPORTANT: ANSI colors do NOT work in Claude Code hook output.
Hook stdout/stderr is captured as plain text - escape codes are not rendered.

ANSI colors ONLY work in:
- Status line scripts (via statusLine in settings.json)
- Direct terminal output (not through hooks)

This module provides:
1. Plain text formatting for hook output (Unicode box-drawing)
2. JSON output helpers for proper Claude Code integration
3. Status line ANSI helpers (for statusline scripts only)

References:
- https://github.com/anthropics/claude-code/issues/4084 (hook visibility)
- https://github.com/anthropics/claude-code/issues/12653 (stderr not displaying)
- https://github.com/anthropics/claude-code/issues/6466 (statusline colors)
"""

import json
import sys
import os
from typing import Optional, Dict, Any


# =============================================================================
# CONSTANTS
# =============================================================================

# Unicode box-drawing characters for visual structure (work everywhere)
BOX = {
    "h": "─",      # horizontal
    "v": "│",      # vertical
    "tl": "┌",     # top-left
    "tr": "┐",     # top-right
    "bl": "└",     # bottom-left
    "br": "┘",     # bottom-right
    "dh": "═",     # double horizontal
    "dv": "║",     # double vertical
    "dtl": "╔",    # double top-left
    "dtr": "╗",    # double top-right
    "dbl": "╚",    # double bottom-left
    "dbr": "╝",    # double bottom-right
}

# Status icons (Unicode, work everywhere)
ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "running": "▶",
    "pending": "○",
    "blocked": "⊘",
    "agent": "🤖",
}

# Hook event types
HOOK_EVENTS = [
    "PreToolUse",
    "PostToolUse",
    "UserPromptSubmit",
    "SessionStart",
    "Stop",
    "SubagentStop",
    "PreCompact",
    "Notification",
]


# =============================================================================
# PLAIN TEXT FORMATTING (for hook output)
# =============================================================================

def format_banner(title: str, width: int = 50) -> str:
    """
    Create a plain text banner with Unicode box-drawing.

    Works in all hook output contexts.
    """
    title = title.upper()
    padding = width - len(title) - 2
    left_pad = padding // 2
    right_pad = padding - left_pad

    top = f"{BOX['dtl']}{BOX['dh'] * width}{BOX['dtr']}"
    middle = f"{BOX['dv']}{' ' * left_pad}{title}{' ' * right_pad}{BOX['dv']}"
    bottom = f"{BOX['dbl']}{BOX['dh'] * width}{BOX['dbr']}"

    return f"{top}\n{middle}\n{bottom}"


def format_status(hook_name: str, status: str, detail: str = "") -> str:
    """
    Format a hook status line (plain text).

    Args:
        hook_name: Name of the hook
        status: Status string (OK, BLOCK, ERROR, etc.)
        detail: Optional detail message

    Returns:
        Formatted status line
    """
    icon = ICONS.get(status.lower(), ICONS["info"])
    display_name = hook_name.replace("-", " ").title()

    if detail:
        return f"{icon} {display_name}: {status} - {detail}"
    return f"{icon} {display_name}: {status}"


def format_agent_banner(agent_name: str, mode: str = "") -> str:
    """
    Create a plain text agent banner.

    Args:
        agent_name: Name of the agent
        mode: Optional mode (PLAN, EXECUTE, etc.)

    Returns:
        Formatted banner string
    """
    display_name = agent_name.replace("-", " ").upper()
    width = 50

    lines = [
        f"{BOX['dtl']}{BOX['dh'] * width}{BOX['dtr']}",
        f"{BOX['dv']}{display_name:^{width}}{BOX['dv']}",
    ]

    if mode:
        lines.append(f"{BOX['dv']}{f'[{mode}]':^{width}}{BOX['dv']}")

    lines.append(f"{BOX['dbl']}{BOX['dh'] * width}{BOX['dbr']}")

    return "\n".join(lines)


def format_confidence(score: float, agent_name: str) -> str:
    """
    Format a confidence score with visual bar (plain text).

    Args:
        score: Confidence percentage (0-100)
        agent_name: Name of the matched agent

    Returns:
        Formatted confidence display
    """
    bar_width = 20
    filled = int(score / 100 * bar_width)
    empty = bar_width - filled

    bar = "█" * filled + "░" * empty

    if score >= 85:
        action = "AUTO-INVOKE"
    elif score >= 60:
        action = "PROMPT"
    else:
        action = "SUGGEST"

    return f"[{bar}] {score:.1f}% {action} -> {agent_name}"


# =============================================================================
# JSON OUTPUT (for Claude Code integration)
# =============================================================================

def json_output(
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    additional_context: Optional[str] = None,
    hook_event: Optional[str] = None,
    continue_: bool = True,
    stop_reason: Optional[str] = None,
    permission_decision: Optional[str] = None,
    permission_reason: Optional[str] = None,
    updated_input: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create properly formatted JSON output for Claude Code hooks.

    This is the CORRECT way to communicate from hooks to Claude Code.

    Args:
        decision: "block" or None (for PostToolUse, Stop, SubagentStop)
        reason: Explanation (shown to Claude for block, user for allow)
        additional_context: Added to Claude's context as system-reminder
        hook_event: Hook event name for hookSpecificOutput
        continue_: Whether Claude should continue (default True)
        stop_reason: Message shown to user when continue_=False
        permission_decision: "allow", "deny", or "ask" (PreToolUse only)
        permission_reason: Explanation for permission decision
        updated_input: Modified tool input (PreToolUse only)

    Returns:
        JSON string to print to stdout

    Example:
        # For UserPromptSubmit - add context
        print(json_output(
            additional_context="Agent 'tester' suggested for this task",
            hook_event="UserPromptSubmit"
        ))
        sys.exit(0)

        # For PreToolUse - block dangerous command
        print(json_output(
            permission_decision="deny",
            permission_reason="Blocked: rm -rf detected",
            hook_event="PreToolUse"
        ))
        sys.exit(0)
    """
    output = {}

    # Common fields
    if not continue_:
        output["continue"] = False
        if stop_reason:
            output["stopReason"] = stop_reason

    if decision:
        output["decision"] = decision

    if reason:
        output["reason"] = reason

    # Hook-specific output
    if hook_event or additional_context or permission_decision:
        hook_specific = {}

        if hook_event:
            hook_specific["hookEventName"] = hook_event

        if additional_context:
            hook_specific["additionalContext"] = additional_context

        if permission_decision:
            hook_specific["permissionDecision"] = permission_decision
            if permission_reason:
                hook_specific["permissionDecisionReason"] = permission_reason

        if updated_input:
            hook_specific["updatedInput"] = updated_input

        if hook_specific:
            output["hookSpecificOutput"] = hook_specific

    return json.dumps(output)


def output_context(context: str, hook_event: str = "UserPromptSubmit") -> None:
    """
    Output additional context to Claude (appears as system-reminder).

    This is the recommended way to inject context from hooks.

    Args:
        context: Text to add to Claude's context
        hook_event: The hook event name
    """
    print(json_output(additional_context=context, hook_event=hook_event))


def output_block(reason: str, hook_event: str = "PreToolUse") -> None:
    """
    Block an operation with a reason shown to Claude.

    Args:
        reason: Why the operation was blocked
        hook_event: The hook event name
    """
    if hook_event == "PreToolUse":
        print(json_output(
            permission_decision="deny",
            permission_reason=reason,
            hook_event=hook_event
        ))
    else:
        print(json_output(decision="block", reason=reason))


# =============================================================================
# STATUS LINE ONLY - ANSI Colors
# =============================================================================
# These functions are ONLY for status line scripts.
# They will NOT work in hook stdout/stderr.

class StatusLine:
    """
    ANSI color helpers for status line scripts ONLY.

    Usage in ~/.claude/statusline.sh or statusLine command:
        from colors import StatusLine
        sl = StatusLine()
        print(sl.colored("text", "green", "black"))

    IMPORTANT: These colors ONLY render in status line context.
    Using them in hooks will output raw escape codes.
    """

    # Combined ANSI codes (the only format that works in Claude Code statusline)
    # Format: \033[STYLE;FG;BGm
    # Style: 0=normal, 1=bold
    # FG: 30-37 (dark), 90-97 (bright)
    # BG: 40-47 (dark), 100-107 (bright)

    FG = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "bright_black": 90,
        "bright_red": 91,
        "bright_green": 92,
        "bright_yellow": 93,
        "bright_blue": 94,
        "bright_magenta": 95,
        "bright_cyan": 96,
        "bright_white": 97,
    }

    BG = {
        "black": 40,
        "red": 41,
        "green": 42,
        "yellow": 43,
        "blue": 44,
        "magenta": 45,
        "cyan": 46,
        "white": 47,
        "bright_black": 100,
        "bright_red": 101,
        "bright_green": 102,
        "bright_yellow": 103,
        "bright_blue": 104,
        "bright_magenta": 105,
        "bright_cyan": 106,
        "bright_white": 107,
    }

    RESET = "\033[0m"

    @classmethod
    def colored(cls, text: str, fg: str = "white", bg: str = None, bold: bool = False) -> str:
        """
        Apply color to text using COMBINED escape sequence.

        ONLY works in status line context, not in hooks.

        Args:
            text: Text to color
            fg: Foreground color name
            bg: Background color name (optional)
            bold: Whether to make text bold

        Returns:
            ANSI-colored string
        """
        fg_code = cls.FG.get(fg, cls.FG["white"])
        style = "1" if bold else "0"

        if bg:
            bg_code = cls.BG.get(bg, cls.BG["black"])
            return f"\033[{style};{fg_code};{bg_code}m{text}{cls.RESET}"
        else:
            return f"\033[{style};{fg_code}m{text}{cls.RESET}"

    @classmethod
    def segment(cls, text: str, fg: str, bg: str) -> str:
        """
        Create a powerline-style segment.

        ONLY works in status line context.
        """
        return cls.colored(f" {text} ", fg, bg, bold=True)


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

# These are kept for existing code but they DO NOT render colors in hooks
# They output raw escape codes which appear as garbage text

RESET = "\033[0m"
BOLD = "\033[1m"

def red(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def green(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def yellow(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def blue(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def cyan(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def magenta(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text

def bold(text: str) -> str:
    """DEPRECATED: Colors don't work in hooks. Returns plain text."""
    return text


# Legacy compatibility - these functions now output plain text
def hook_status(hook_name: str, status: str, detail: str = "") -> None:
    """Output hook status to stderr (plain text, no colors)."""
    msg = format_status(hook_name, status, detail)
    print(msg, file=sys.stderr)


def agent_banner(agent_name: str, mode: str = "") -> None:
    """Output agent banner to stderr (plain text, no colors)."""
    banner = format_agent_banner(agent_name, mode)
    print(banner, file=sys.stderr)


def get_hook_color(hook_name: str) -> str:
    """DEPRECATED: Returns empty string. Colors don't work in hooks."""
    return ""


def get_agent_color(agent_name: str) -> str:
    """DEPRECATED: Returns empty string. Colors don't work in hooks."""
    return ""


# =============================================================================
# MAIN - Demo/Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  CLAUDE CODE HOOK OUTPUT SYSTEM")
    print("  (ANSI colors do NOT work in hooks)")
    print("=" * 60)

    print("\n--- Plain Text Banner ---")
    print(format_banner("Security Scanner"))

    print("\n--- Agent Banner ---")
    print(format_agent_banner("orchestrator", "PLANNING"))

    print("\n--- Status Lines ---")
    print(format_status("pre-write-check", "success", "file.py validated"))
    print(format_status("laziness-check", "blocked", "placeholder detected"))
    print(format_status("context-loader", "info", "loaded 3 files"))

    print("\n--- Confidence Display ---")
    print(format_confidence(92.5, "security-scanner"))
    print(format_confidence(67.3, "tester"))
    print(format_confidence(45.0, "brainstormer"))

    print("\n--- JSON Output Examples ---")
    print("\nUserPromptSubmit context injection:")
    print(json_output(
        additional_context="AGENT INVOKE: Use 'tester' agent",
        hook_event="UserPromptSubmit"
    ))

    print("\nPreToolUse block:")
    print(json_output(
        permission_decision="deny",
        permission_reason="Blocked: dangerous command",
        hook_event="PreToolUse"
    ))

    print("\n--- Status Line Colors (ONLY work in statusline) ---")
    sl = StatusLine()
    print(f"In status line: {sl.colored('GREEN', 'green', 'black', True)}")
    print(f"In status line: {sl.segment('SEGMENT', 'white', 'blue')}")
    print("(Above will show raw codes if not in statusline context)")
