#!/usr/bin/env python3
"""
colors.py - Unified color system for Claude Protocol hooks and agents

Single source of truth for all terminal colorization.
Based on the working v1.1.10 implementation - NO TTY detection.
"""

import sys
import os

# =============================================================================
# ANSI ESCAPE CODES - Combined format that works in Claude Code
# =============================================================================

RESET = "\033[0m"
BOLD = "\033[1m"

# Hook color schemes: combined bold + foreground + background
# Format: \033[1;FG;BGm where FG=30-37/90-97, BG=40-47/100-107
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

# Agent color schemes
AGENT_COLORS = {
    # Quality agents - red/yellow spectrum
    "security-scanner": "\033[1;97;41m",          # White on Red
    "laziness-destroyer": "\033[1;30;101m",       # Black on Bright Red
    "hallucination-checker": "\033[1;97;45m",     # White on Magenta
    "honesty-evaluator": "\033[1;30;105m",        # Black on Bright Magenta
    "fact-checker": "\033[1;97;105m",             # White on Bright Magenta
    "reviewer": "\033[1;30;43m",                  # Black on Yellow
    "tester": "\033[1;30;42m",                    # Black on Green
    "test-coverage-enforcer": "\033[1;30;103m",   # Black on Bright Yellow

    # Core agents - blue spectrum
    "architect": "\033[1;97;44m",                 # White on Blue
    "research-analyzer": "\033[1;97;104m",        # White on Bright Blue
    "performance-analyzer": "\033[1;30;46m",      # Black on Cyan
    "debugger": "\033[1;97;41m",                  # White on Red

    # Domain agents - green/cyan spectrum
    "codebase-analyzer": "\033[1;30;42m",         # Black on Green
    "frontend-designer": "\033[1;30;106m",        # Black on Bright Cyan
    "ui-researcher": "\033[1;97;46m",             # White on Cyan
    "dependency-auditor": "\033[1;30;103m",       # Black on Bright Yellow
    "protocol-generator": "\033[1;30;102m",       # Black on Bright Green
    "protocol-analyzer": "\033[1;30;42m",         # Black on Green
    "protocol-updater": "\033[1;30;102m",         # Black on Bright Green
    "document-processor": "\033[1;97;44m",        # White on Blue
    "documenter": "\033[1;97;44m",                # White on Blue

    # Workflow agents - neutral spectrum
    "brainstormer": "\033[1;30;47m",              # Black on White
    "orchestrator": "\033[1;30;107m",             # Black on Bright White
    "git-strategist": "\033[1;30;43m",            # Black on Yellow
    "tech-debt-tracker": "\033[1;30;103m",        # Black on Bright Yellow
}

DEFAULT_AGENT_COLOR = "\033[1;97;100m"  # White on Bright Black

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


# =============================================================================
# BACKWARD COMPATIBILITY - ANSI class
# =============================================================================

class ANSI:
    """ANSI escape codes for terminal styling."""
    RESET = RESET
    BOLD = BOLD
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Bright backgrounds
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"


# Always enabled - no TTY detection (this is what v1.1.10 did)
COLORS_ENABLED = True


# =============================================================================
# HOOK FUNCTIONS
# =============================================================================

def get_hook_color(hook_name: str) -> str:
    """Get ANSI color code for a hook."""
    return HOOK_COLORS.get(hook_name, DEFAULT_COLOR)


def get_agent_color(agent_name: str) -> str:
    """Get ANSI color code for an agent."""
    return AGENT_COLORS.get(agent_name, DEFAULT_AGENT_COLOR)


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


# =============================================================================
# AGENT FUNCTIONS
# =============================================================================

def agent_banner(agent_name: str, mode: str = "") -> None:
    """Output a colored agent banner."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    width = 50

    border = "═" * width
    
    banner = f"""
{color}╔{border}╗{RESET}
{color}║{display_name:^{width}}║{RESET}"""
    
    if mode:
        banner += f"""
{color}║{f'[{mode}]':^{width}}║{RESET}"""
    
    banner += f"""
{color}╚{border}╝{RESET}
"""
    print(banner, file=sys.stderr)


def agent_compact(agent_name: str, mode: str = "") -> None:
    """Output a compact single-line agent indicator."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").title()
    
    if mode:
        print(f"{color} [{mode}] {display_name} {RESET}", file=sys.stderr)
    else:
        print(f"{color} {display_name} {RESET}", file=sys.stderr)


# =============================================================================
# SIMPLIFIED API
# =============================================================================

_current_hook = None


def set_current_hook(name: str) -> None:
    """Set the current hook name for simplified API."""
    global _current_hook
    _current_hook = name


def status(status_str: str, detail: str = "") -> None:
    """Simplified status output using previously set hook name."""
    global _current_hook
    if _current_hook:
        hook_status(_current_hook, status_str, detail)


def get_hook_name(script_path: str = None) -> str:
    """Extract hook name from script path."""
    if script_path is None:
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            script_path = frame.f_back.f_globals.get("__file__", "unknown")
    
    name = os.path.basename(script_path)
    name = name.replace(".py", "").replace(".sh", "")
    return name


# =============================================================================
# SIMPLE COLOR FUNCTIONS
# =============================================================================

def red(text: str) -> str:
    return f"\033[91m{text}{RESET}"

def green(text: str) -> str:
    return f"\033[92m{text}{RESET}"

def yellow(text: str) -> str:
    return f"\033[93m{text}{RESET}"

def blue(text: str) -> str:
    return f"\033[94m{text}{RESET}"

def cyan(text: str) -> str:
    return f"\033[96m{text}{RESET}"

def magenta(text: str) -> str:
    return f"\033[95m{text}{RESET}"

def bold(text: str) -> str:
    return f"\033[1m{text}{RESET}"


# =============================================================================
# THEME COMPATIBILITY (for hook_colors.py imports)
# =============================================================================

def get_hook_theme(hook_name: str) -> tuple:
    """Get (foreground, background) - returns combined code for compatibility."""
    color = get_hook_color(hook_name)
    return (color, "")


def get_agent_theme(agent_name: str) -> tuple:
    """Get (foreground, background, category) for an agent."""
    color = get_agent_color(agent_name)
    category = agent_name.upper().replace("-", "")[:8]
    return (color, "", category)


def get_status_symbol(status: str) -> str:
    """Get symbol for a status."""
    return STATUS_ICONS.get(status.upper(), "⚡")


def format_hook_status(hook_name: str, status: str, detail: str = "") -> str:
    """Format a colored hook status line (returns string, doesn't print)."""
    color = get_hook_color(hook_name)
    icon = STATUS_ICONS.get(status.upper(), "⚡")
    display_name = hook_name.replace("-", " ").title()

    if detail:
        return f"{color} {icon} {display_name}: {status} {RESET} {detail}"
    return f"{color} {icon} {display_name}: {status} {RESET}"


def format_agent_banner(agent_name: str) -> str:
    """Format a colored agent banner (returns string)."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    width = 50
    border = "═" * width
    
    return f"""
{color}╔{border}╗{RESET}
{color}║{display_name:^{width}}║{RESET}
{color}╚{border}╝{RESET}
"""


def format_agent_banner_with_mode(agent_name: str, execution_mode: str = "") -> str:
    """Format a colored agent banner with optional execution mode."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    width = 50
    border = "═" * width
    
    banner = f"""
{color}╔{border}╗{RESET}
{color}║{display_name:^{width}}║{RESET}"""
    
    if execution_mode:
        banner += f"""
{color}║{f'[{execution_mode}]':^{width}}║{RESET}"""
    
    banner += f"""
{color}╚{border}╝{RESET}
"""
    return banner


def format_agent_compact(agent_name: str) -> str:
    """Format a compact single-line agent indicator."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").title()
    return f"{color} {display_name} {RESET}"


def format_agent_compact_with_mode(agent_name: str, execution_mode: str = "") -> str:
    """Format a compact single-line agent indicator with optional execution mode."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").title()
    
    if execution_mode:
        return f"{color} [{execution_mode}] {display_name} {RESET}"
    return f"{color} {display_name} {RESET}"


# =============================================================================
# MAIN - Demo/Test
# =============================================================================

if __name__ == "__main__":
    print("=== HOOK STATUS EXAMPLES ===", file=sys.stderr)
    hook_status("pre-write-check", "OK", "example.py")
    hook_status("laziness-check", "OK", "No lazy code")
    hook_status("context-loader", "OK", "Loaded context")
    hook_status("dangerous-command-check", "BLOCK", "rm -rf detected")
    
    print("\n=== AGENT BANNER EXAMPLES ===", file=sys.stderr)
    agent_banner("security-scanner")
    agent_banner("orchestrator", "PLANNING")
    
    print("\n=== SIMPLE COLORS ===", file=sys.stderr)
    print(f"  {red('RED')} {green('GREEN')} {yellow('YELLOW')} {blue('BLUE')} {cyan('CYAN')}", file=sys.stderr)
    
    print("\n=== RAW TEST ===", file=sys.stderr)
    print(f"\033[1;97;41m WHITE ON RED \033[0m", file=sys.stderr)
    print(f"\033[1;30;42m BLACK ON GREEN \033[0m", file=sys.stderr)
    print(f"\033[1;30;103m BLACK ON BRIGHT YELLOW \033[0m", file=sys.stderr)
