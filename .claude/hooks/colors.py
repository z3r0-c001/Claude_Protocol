#!/usr/bin/env python3
"""
colors.py - Unified color system for Claude Protocol hooks and agents

Single source of truth for all terminal colorization.
Supports NO_COLOR environment variable (https://no-color.org/)
"""

import os
import sys

# Check if colors should be disabled
def _colors_enabled() -> bool:
    """Check if terminal colors should be used."""
    # NO_COLOR standard: https://no-color.org/
    if os.environ.get("NO_COLOR"):
        return False
    # Check if output is a TTY
    if not sys.stderr.isatty():
        return False
    # Check TERM
    term = os.environ.get("TERM", "")
    if term == "dumb":
        return False
    return True

COLORS_ENABLED = _colors_enabled()

def _c(code: str) -> str:
    """Return ANSI code if colors enabled, empty string otherwise."""
    return code if COLORS_ENABLED else ""

# =============================================================================
# ANSI CODES
# =============================================================================

class ANSI:
    """ANSI escape codes for terminal styling."""
    # Reset
    RESET = _c("\033[0m")
    
    # Text styles
    BOLD = _c("\033[1m")
    DIM = _c("\033[2m")
    ITALIC = _c("\033[3m")
    UNDERLINE = _c("\033[4m")
    
    # Foreground colors
    BLACK = _c("\033[30m")
    RED = _c("\033[31m")
    GREEN = _c("\033[32m")
    YELLOW = _c("\033[33m")
    BLUE = _c("\033[34m")
    MAGENTA = _c("\033[35m")
    CYAN = _c("\033[36m")
    WHITE = _c("\033[37m")
    
    # Bright foreground
    BRIGHT_BLACK = _c("\033[90m")
    BRIGHT_RED = _c("\033[91m")
    BRIGHT_GREEN = _c("\033[92m")
    BRIGHT_YELLOW = _c("\033[93m")
    BRIGHT_BLUE = _c("\033[94m")
    BRIGHT_MAGENTA = _c("\033[95m")
    BRIGHT_CYAN = _c("\033[96m")
    BRIGHT_WHITE = _c("\033[97m")
    
    # Background colors
    BG_BLACK = _c("\033[40m")
    BG_RED = _c("\033[41m")
    BG_GREEN = _c("\033[42m")
    BG_YELLOW = _c("\033[43m")
    BG_BLUE = _c("\033[44m")
    BG_MAGENTA = _c("\033[45m")
    BG_CYAN = _c("\033[46m")
    BG_WHITE = _c("\033[47m")
    
    # Bright backgrounds
    BG_BRIGHT_BLACK = _c("\033[100m")
    BG_BRIGHT_RED = _c("\033[101m")
    BG_BRIGHT_GREEN = _c("\033[102m")
    BG_BRIGHT_YELLOW = _c("\033[103m")
    BG_BRIGHT_BLUE = _c("\033[104m")
    BG_BRIGHT_MAGENTA = _c("\033[105m")
    BG_BRIGHT_CYAN = _c("\033[106m")
    BG_BRIGHT_WHITE = _c("\033[107m")


# =============================================================================
# HOOK THEMES
# =============================================================================

# Theme tuple: (foreground, background)
HOOK_THEMES = {
    # PreToolUse hooks
    "pre-write-check":            (ANSI.BRIGHT_WHITE, ANSI.BG_RED),
    "pretool-laziness-check":     (ANSI.BLACK, ANSI.BG_YELLOW),
    "pretool-hallucination-check":(ANSI.BRIGHT_WHITE, ANSI.BG_MAGENTA),
    "dangerous-command-check":    (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_RED),
    "agent-announce":             (ANSI.BLACK, ANSI.BG_BRIGHT_BLUE),
    
    # PostToolUse hooks
    "post-write-validate":        (ANSI.BRIGHT_WHITE, ANSI.BG_BLUE),
    "file-edit-tracker":          (ANSI.BLACK, ANSI.BG_CYAN),
    "context-detector":           (ANSI.BLACK, ANSI.BG_GREEN),
    "research-quality-check":     (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLUE),
    "doc-size-detector":          (ANSI.BLACK, ANSI.BG_BRIGHT_CYAN),
    
    # UserPromptSubmit hooks
    "context-loader":             (ANSI.BLACK, ANSI.BG_BRIGHT_GREEN),
    "skill-activation-prompt":    (ANSI.BRIGHT_WHITE, ANSI.BG_GREEN),
    
    # Stop hooks
    "laziness-check":             (ANSI.BLACK, ANSI.BG_BRIGHT_YELLOW),
    "honesty-check":              (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_MAGENTA),
    "stop-verify":                (ANSI.BLACK, ANSI.BG_WHITE),
    
    # SubagentStop hooks
    "research-validator":         (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_GREEN),
    "agent-handoff-validator":    (ANSI.BLACK, ANSI.BG_BRIGHT_WHITE),
}

# Default theme for unknown hooks
DEFAULT_HOOK_THEME = (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLACK)


# =============================================================================
# AGENT THEMES
# =============================================================================

# Theme tuple: (foreground, background, category_label)
AGENT_THEMES = {
    # Quality agents - red/yellow spectrum
    "security-scanner":       (ANSI.BRIGHT_WHITE, ANSI.BG_RED, "SECURITY"),
    "laziness-destroyer":     (ANSI.BLACK, ANSI.BG_BRIGHT_RED, "QUALITY"),
    "hallucination-checker":  (ANSI.BRIGHT_WHITE, ANSI.BG_MAGENTA, "VERIFY"),
    "honesty-evaluator":      (ANSI.BLACK, ANSI.BG_BRIGHT_MAGENTA, "HONESTY"),
    "fact-checker":           (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_MAGENTA, "FACTS"),
    "reviewer":               (ANSI.BLACK, ANSI.BG_YELLOW, "REVIEW"),
    "tester":                 (ANSI.BLACK, ANSI.BG_GREEN, "TEST"),
    "test-coverage-enforcer": (ANSI.BLACK, ANSI.BG_BRIGHT_YELLOW, "COVERAGE"),
    
    # Core agents - blue spectrum
    "architect":              (ANSI.BRIGHT_WHITE, ANSI.BG_BLUE, "ARCHITECT"),
    "research-analyzer":      (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLUE, "RESEARCH"),
    "performance-analyzer":   (ANSI.BLACK, ANSI.BG_CYAN, "PERF"),
    
    # Domain agents - green/cyan spectrum
    "codebase-analyzer":      (ANSI.BLACK, ANSI.BG_GREEN, "ANALYZE"),
    "frontend-designer":      (ANSI.BLACK, ANSI.BG_BRIGHT_CYAN, "FRONTEND"),
    "ui-researcher":          (ANSI.BRIGHT_WHITE, ANSI.BG_CYAN, "UI"),
    "dependency-auditor":     (ANSI.BLACK, ANSI.BG_BRIGHT_YELLOW, "DEPS"),
    "protocol-generator":     (ANSI.BLACK, ANSI.BG_BRIGHT_GREEN, "PROTOCOL"),
    "protocol-analyzer":      (ANSI.BLACK, ANSI.BG_GREEN, "PROTOCOL"),
    "protocol-updater":       (ANSI.BLACK, ANSI.BG_BRIGHT_GREEN, "UPDATE"),
    "document-processor":     (ANSI.BRIGHT_WHITE, ANSI.BG_BLUE, "DOCS"),
    
    # Workflow agents - neutral spectrum
    "brainstormer":           (ANSI.BLACK, ANSI.BG_WHITE, "IDEAS"),
    "orchestrator":           (ANSI.BLACK, ANSI.BG_BRIGHT_WHITE, "ORCHESTRATE"),
    
    # Built-in Claude agents
    "general-purpose":        (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLACK, "AGENT"),
    "Explore":                (ANSI.BLACK, ANSI.BG_CYAN, "EXPLORE"),
    "Plan":                   (ANSI.BLACK, ANSI.BG_YELLOW, "PLAN"),
    "claude-code-guide":      (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLUE, "GUIDE"),
}

# Default theme for unknown agents
DEFAULT_AGENT_THEME = (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLACK, "AGENT")

# Color pool for unknown agents (deterministic assignment by name hash)
AGENT_COLOR_POOL = [
    (ANSI.BRIGHT_WHITE, ANSI.BG_RED),
    (ANSI.BRIGHT_WHITE, ANSI.BG_BLUE),
    (ANSI.BLACK, ANSI.BG_GREEN),
    (ANSI.BLACK, ANSI.BG_YELLOW),
    (ANSI.BRIGHT_WHITE, ANSI.BG_MAGENTA),
    (ANSI.BLACK, ANSI.BG_CYAN),
    (ANSI.BLACK, ANSI.BG_BRIGHT_RED),
    (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLUE),
    (ANSI.BLACK, ANSI.BG_BRIGHT_GREEN),
    (ANSI.BLACK, ANSI.BG_BRIGHT_YELLOW),
    (ANSI.BLACK, ANSI.BG_BRIGHT_MAGENTA),
    (ANSI.BLACK, ANSI.BG_BRIGHT_CYAN),
    (ANSI.BLACK, ANSI.BG_WHITE),
    (ANSI.BRIGHT_WHITE, ANSI.BG_BRIGHT_BLACK),
]


# =============================================================================
# STATUS INDICATORS
# =============================================================================

STATUS_SYMBOLS = {
    "START":    ">",
    "CHECKING": ">",
    "RUNNING":  ">",
    "OK":       "+",
    "PASS":     "+",
    "CONTINUE": "+",
    "BLOCK":    "X",
    "FAIL":     "X",
    "ERROR":    "X",
    "WARN":     "!",
    "SKIP":     "-",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_hook_theme(hook_name: str) -> tuple:
    """Get (foreground, background) for a hook."""
    return HOOK_THEMES.get(hook_name, DEFAULT_HOOK_THEME)


def get_agent_theme(agent_name: str) -> tuple:
    """Get (foreground, background, category) for an agent."""
    if agent_name in AGENT_THEMES:
        return AGENT_THEMES[agent_name]
    
    # Deterministic color for unknown agents
    import hashlib
    name_hash = int(hashlib.md5(agent_name.encode()).hexdigest(), 16)
    color_index = name_hash % len(AGENT_COLOR_POOL)
    fg, bg = AGENT_COLOR_POOL[color_index]
    category = agent_name.upper().replace("-", "")[:8]
    return (fg, bg, category)


def get_status_symbol(status: str) -> str:
    """Get ASCII symbol for a status."""
    return STATUS_SYMBOLS.get(status.upper(), "*")


def format_hook_status(hook_name: str, status: str, detail: str = "") -> str:
    """Format a colored hook status line."""
    fg, bg = get_hook_theme(hook_name)
    symbol = get_status_symbol(status)
    display_name = hook_name.replace("-", " ").title()
    
    if detail:
        return f"{fg}{bg}{ANSI.BOLD} {symbol} {display_name}: {status} {ANSI.RESET} {detail}"
    return f"{fg}{bg}{ANSI.BOLD} {symbol} {display_name}: {status} {ANSI.RESET}"


def format_agent_banner(agent_name: str) -> str:
    """Format a colored agent banner."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    
    width = max(len(display_name) + 16, 50)
    border = "-" * width
    tag = f" {category} "
    banner_line = f"   {display_name}"
    padding = width - len(banner_line) - 1
    
    return f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{tag:^{width}}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{banner_line}{' ' * padding}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
"""


def format_agent_compact(agent_name: str) -> str:
    """Format a compact single-line agent indicator."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").title()
    return f"{fg}{bg}{ANSI.BOLD} [{category}] {display_name} {ANSI.RESET}"


# =============================================================================
# HOOK STATUS API
# =============================================================================

_current_hook = None

def set_current_hook(name: str) -> None:
    """Set the current hook name for simplified API."""
    global _current_hook
    _current_hook = name


def hook_status(hook_name: str, status: str, detail: str = "") -> None:
    """Output colored hook status to stderr."""
    msg = format_hook_status(hook_name, status, detail)
    print(msg, file=sys.stderr)


def status(status_str: str, detail: str = "") -> None:
    """Simplified status output using previously set hook name."""
    global _current_hook
    if _current_hook:
        hook_status(_current_hook, status_str, detail)


# =============================================================================
# BASH EXPORT
# =============================================================================

def export_bash_colors() -> str:
    """Generate bash variable declarations for colors."""
    if not COLORS_ENABLED:
        return "# Colors disabled\n"
    
    lines = [
        "# Auto-generated color definitions",
        "RESET=$'\\033[0m'",
        "BOLD=$'\\033[1m'",
    ]
    
    for name, (fg, bg) in HOOK_THEMES.items():
        var_name = name.upper().replace("-", "_")
        # Extract raw codes for bash
        fg_code = fg.replace("\033", "\\033") if fg else ""
        bg_code = bg.replace("\033", "\\033") if bg else ""
        lines.append(f"HOOK_{var_name}=$'{fg_code}{bg_code}\\033[1m'")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo output
    print("Hook Status Examples:", file=sys.stderr)
    for hook in ["pre-write-check", "laziness-check", "context-loader"]:
        hook_status(hook, "OK", "example.py")
    
    print("\nAgent Banner Examples:", file=sys.stderr)
    for agent in ["security-scanner", "architect", "orchestrator"]:
        print(format_agent_banner(agent), file=sys.stderr)


def format_agent_banner_with_mode(agent_name: str, execution_mode: str = "") -> str:
    """Format a colored agent banner with optional execution mode."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    
    width = 58
    border = "=" * width
    
    banner = f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{category:^{width}}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{display_name:^{width}}|{ANSI.RESET}"""
    
    if execution_mode:
        mode_str = f"[{execution_mode}]"
        banner += f"""
{fg}{bg}{ANSI.BOLD}|{mode_str:^{width}}|{ANSI.RESET}"""
    
    banner += f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
"""
    return banner


def format_agent_compact_with_mode(agent_name: str, execution_mode: str = "") -> str:
    """Format a compact single-line agent indicator with optional execution mode."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").title()
    
    if execution_mode:
        return f"{fg}{bg}{ANSI.BOLD} [{category}] {display_name} ({execution_mode}) {ANSI.RESET}"
    return f"{fg}{bg}{ANSI.BOLD} [{category}] {display_name} {ANSI.RESET}"
