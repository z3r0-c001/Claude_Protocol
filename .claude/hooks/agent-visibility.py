#!/usr/bin/env python3
"""
agent-visibility.py - Terminal output for agent auto-invocation system

Provides visual feedback for the 3-layer agent matching system:
- Confidence score display with layer breakdown
- Agent invocation banners with mode indicators
- Progress indicators for multi-agent workflows
- Auto-invoke vs. prompt notifications

Uses unified color system from colors.py
"""

import sys
import os
from typing import Optional

# Import unified color system
try:
    from colors import (
        RESET, BOLD, COLORS_ENABLED,
        get_agent_color, AGENT_COLORS, DEFAULT_AGENT_COLOR,
        red, green, yellow, blue, cyan, magenta, bold
    )
except ImportError:
    # Fallback if colors.py not in path
    RESET = "\033[0m"
    BOLD = "\033[1m"
    COLORS_ENABLED = True
    DEFAULT_AGENT_COLOR = "\033[1;97;100m"
    AGENT_COLORS = {}
    def get_agent_color(name): return DEFAULT_AGENT_COLOR
    def red(t): return f"\033[91m{t}{RESET}"
    def green(t): return f"\033[92m{t}{RESET}"
    def yellow(t): return f"\033[93m{t}{RESET}"
    def blue(t): return f"\033[94m{t}{RESET}"
    def cyan(t): return f"\033[96m{t}{RESET}"
    def magenta(t): return f"\033[95m{t}{RESET}"
    def bold(t): return f"\033[1m{t}{RESET}"


# =============================================================================
# CONSTANTS
# =============================================================================

# Banner width for consistency
BANNER_WIDTH = 60

# Confidence thresholds (should match invoke-config.json)
THRESHOLD_AUTO = 85
THRESHOLD_PROMPT = 60

# Status colors for confidence levels
CONFIDENCE_COLORS = {
    "high": "\033[1;30;42m",      # Black on Green (auto-invoke)
    "medium": "\033[1;30;43m",    # Black on Yellow (prompt)
    "low": "\033[1;97;100m",      # White on Gray (suggest)
}

# Layer names for display
LAYER_NAMES = {
    "keyword": "Keywords",
    "category": "Category",
    "llm_intent": "LLM Intent",
    "memory": "Memory Adj",
}


# =============================================================================
# CONFIDENCE DISPLAY
# =============================================================================

def format_confidence_bar(score: float, width: int = 20) -> str:
    """Create a visual confidence bar."""
    filled = int(score / 100 * width)
    empty = width - filled

    if score >= THRESHOLD_AUTO:
        color = green
    elif score >= THRESHOLD_PROMPT:
        color = yellow
    else:
        color = red

    bar = color("█" * filled) + "░" * empty
    return f"[{bar}]"


def format_confidence_score(score: float, show_bar: bool = True) -> str:
    """Format a confidence score with color and optional bar."""
    if score >= THRESHOLD_AUTO:
        color_code = CONFIDENCE_COLORS["high"]
        label = "AUTO"
    elif score >= THRESHOLD_PROMPT:
        color_code = CONFIDENCE_COLORS["medium"]
        label = "PROMPT"
    else:
        color_code = CONFIDENCE_COLORS["low"]
        label = "SUGGEST"

    score_str = f"{color_code} {score:.1f}% {label} {RESET}"

    if show_bar:
        bar = format_confidence_bar(score)
        return f"{bar} {score_str}"
    return score_str


def format_layer_breakdown(
    keyword_score: float,
    category_score: float,
    llm_score: float,
    memory_adj: float = 0.0,
    weights: Optional[dict] = None
) -> str:
    """
    Format a detailed breakdown of confidence layers.

    Args:
        keyword_score: Layer 1 raw score (0-100)
        category_score: Layer 2 raw score (0-100)
        llm_score: Layer 3 raw score (0-100)
        memory_adj: Memory-based adjustment (-25 to +20)
        weights: Layer weights dict (keyword, category, llm_intent)

    Returns:
        Formatted multi-line breakdown string
    """
    weights = weights or {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40}

    # Calculate weighted contributions
    kw_contrib = keyword_score * weights.get("keyword", 0.25)
    cat_contrib = category_score * weights.get("category", 0.35)
    llm_contrib = llm_score * weights.get("llm_intent", 0.40)

    # Total before and after memory
    base_total = kw_contrib + cat_contrib + llm_contrib
    final_total = max(0, min(100, base_total + memory_adj))

    lines = [
        cyan("  Confidence Breakdown:"),
        f"    {LAYER_NAMES['keyword']:12} {keyword_score:5.1f}% x {weights.get('keyword', 0.25):.2f} = {kw_contrib:5.1f}%",
        f"    {LAYER_NAMES['category']:12} {category_score:5.1f}% x {weights.get('category', 0.35):.2f} = {cat_contrib:5.1f}%",
        f"    {LAYER_NAMES['llm_intent']:12} {llm_score:5.1f}% x {weights.get('llm_intent', 0.40):.2f} = {llm_contrib:5.1f}%",
        f"    {'─' * 35}",
        f"    {'Base Total':12} {base_total:26.1f}%",
    ]

    if memory_adj != 0:
        adj_color = green if memory_adj > 0 else red
        adj_sign = "+" if memory_adj > 0 else ""
        lines.append(f"    {LAYER_NAMES['memory']:12} {adj_color(f'{adj_sign}{memory_adj:.1f}%'):>26}")
        lines.append(f"    {'─' * 35}")

    lines.append(f"    {bold('Final Score'):12} {format_confidence_score(final_total, show_bar=False):>26}")

    return "\n".join(lines)


# =============================================================================
# AGENT BANNERS
# =============================================================================

def format_auto_invoke_banner(
    agent_name: str,
    confidence: float,
    mode: str = "EXECUTE",
    show_breakdown: bool = False,
    breakdown: Optional[dict] = None
) -> str:
    """
    Format an auto-invocation banner when confidence >= THRESHOLD_AUTO.

    Args:
        agent_name: Name of the agent being invoked
        confidence: Overall confidence score
        mode: Execution mode (EXECUTE, PLAN)
        show_breakdown: Whether to show confidence breakdown
        breakdown: Dict with keyword_score, category_score, llm_score, memory_adj

    Returns:
        Formatted banner string
    """
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").upper()

    border = "═" * BANNER_WIDTH
    inner_border = "─" * BANNER_WIDTH

    # Header
    banner_lines = [
        "",
        f"{color}╔{border}╗{RESET}",
        f"{color}║{' AUTO-INVOKING ':═^{BANNER_WIDTH}}║{RESET}",
        f"{color}║{display_name:^{BANNER_WIDTH}}║{RESET}",
        f"{color}║{f'[{mode}]':^{BANNER_WIDTH}}║{RESET}",
        f"{color}╠{inner_border}╣{RESET}",
    ]

    # Confidence line
    conf_str = f"Confidence: {confidence:.1f}%"
    banner_lines.append(f"{color}║{conf_str:^{BANNER_WIDTH}}║{RESET}")

    # Footer
    banner_lines.append(f"{color}╚{border}╝{RESET}")

    result = "\n".join(banner_lines)

    # Optional breakdown
    if show_breakdown and breakdown:
        result += "\n" + format_layer_breakdown(
            breakdown.get("keyword_score", 0),
            breakdown.get("category_score", 0),
            breakdown.get("llm_score", 0),
            breakdown.get("memory_adj", 0),
            breakdown.get("weights")
        )

    return result


def format_prompt_banner(
    agent_name: str,
    confidence: float,
    reason: str = "",
    show_breakdown: bool = False,
    breakdown: Optional[dict] = None
) -> str:
    """
    Format a prompt banner when confidence is in PROMPT range.

    Args:
        agent_name: Name of the suggested agent
        confidence: Overall confidence score
        reason: Why this agent was suggested
        show_breakdown: Whether to show confidence breakdown
        breakdown: Dict with layer scores

    Returns:
        Formatted banner string with prompt options
    """
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").upper()

    border = "═" * BANNER_WIDTH
    inner_border = "─" * BANNER_WIDTH

    banner_lines = [
        "",
        f"{yellow('╔' + border + '╗')}",
        f"{yellow('║')}{' SUGGESTED AGENT ':═^{BANNER_WIDTH}}{yellow('║')}",
        f"{yellow('║')}{display_name:^{BANNER_WIDTH}}{yellow('║')}",
        f"{yellow('╠' + inner_border + '╣')}",
    ]

    # Confidence
    conf_str = f"Confidence: {confidence:.1f}%"
    banner_lines.append(f"{yellow('║')}{conf_str:^{BANNER_WIDTH}}{yellow('║')}")

    # Reason if provided
    if reason:
        # Word wrap reason to fit banner width
        max_reason = BANNER_WIDTH - 4
        if len(reason) > max_reason:
            reason = reason[:max_reason-3] + "..."
        banner_lines.append(f"{yellow('║')}{reason:^{BANNER_WIDTH}}{yellow('║')}")

    banner_lines.append(f"{yellow('╠' + inner_border + '╣')}")

    # Prompt options
    options = "[Y]es / [N]o / [P]lan mode"
    banner_lines.append(f"{yellow('║')}{options:^{BANNER_WIDTH}}{yellow('║')}")
    banner_lines.append(f"{yellow('╚' + border + '╝')}")

    result = "\n".join(banner_lines)

    if show_breakdown and breakdown:
        result += "\n" + format_layer_breakdown(
            breakdown.get("keyword_score", 0),
            breakdown.get("category_score", 0),
            breakdown.get("llm_score", 0),
            breakdown.get("memory_adj", 0),
            breakdown.get("weights")
        )

    return result


def format_suggest_banner(
    agent_name: str,
    confidence: float,
    reason: str = ""
) -> str:
    """
    Format a non-blocking suggestion for low confidence matches.

    Args:
        agent_name: Name of the suggested agent
        confidence: Overall confidence score
        reason: Why this might be relevant

    Returns:
        Compact suggestion string
    """
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").title()

    conf_bar = format_confidence_bar(confidence, width=10)

    line = f"{cyan('Tip:')} Consider {color} {display_name} {RESET} {conf_bar} {confidence:.0f}%"
    if reason:
        line += f" - {reason}"

    return line


def format_disambiguation_banner(
    options: list,
    prompt_snippet: str = ""
) -> str:
    """
    Format a disambiguation banner when multiple agents score closely.

    Args:
        options: List of dicts with {agent, score, description}
        prompt_snippet: Optional short snippet of the user's prompt

    Returns:
        Formatted banner with numbered options for user to choose
    """
    border = "═" * BANNER_WIDTH
    inner_border = "─" * BANNER_WIDTH

    banner_lines = [
        "",
        f"{yellow('╔' + border + '╗')}",
        f"{yellow('║')}{' MULTIPLE AGENTS MATCH ':═^{BANNER_WIDTH}}{yellow('║')}",
    ]

    if prompt_snippet:
        snippet = prompt_snippet[:40] + "..." if len(prompt_snippet) > 40 else prompt_snippet
        banner_lines.append(f"{yellow('║')}{f'\"{snippet}\"':^{BANNER_WIDTH}}{yellow('║')}")

    banner_lines.append(f"{yellow('╠' + inner_border + '╣')}")
    banner_lines.append(f"{yellow('║')}{' Which agent should handle this?':^{BANNER_WIDTH}}{yellow('║')}")
    banner_lines.append(f"{yellow('╠' + inner_border + '╣')}")

    # Format each option
    for i, opt in enumerate(options, 1):
        agent_name = opt.get("agent", "unknown")
        score = opt.get("score", 0)
        desc = opt.get("description", "")

        color = get_agent_color(agent_name)
        display_name = agent_name.replace("-", " ").title()

        # Option line with number and agent
        opt_line = f"  [{i}] {display_name} ({score:.0f}%)"
        padding = BANNER_WIDTH - len(opt_line)
        banner_lines.append(f"{yellow('║')}{opt_line}{' ' * padding}{yellow('║')}")

        # Description line (indented)
        if desc:
            desc_short = desc[:BANNER_WIDTH - 8] + "..." if len(desc) > BANNER_WIDTH - 8 else desc
            desc_line = f"      {desc_short}"
            padding = BANNER_WIDTH - len(desc_line)
            banner_lines.append(f"{yellow('║')}{desc_line}{' ' * padding}{yellow('║')}")

    banner_lines.append(f"{yellow('╠' + inner_border + '╣')}")

    # Instructions
    instr = "Enter number, or [S]kip"
    banner_lines.append(f"{yellow('║')}{instr:^{BANNER_WIDTH}}{yellow('║')}")
    banner_lines.append(f"{yellow('╚' + border + '╝')}")

    return "\n".join(banner_lines)


# =============================================================================
# MULTI-AGENT PROGRESS
# =============================================================================

def format_workflow_header(workflow_name: str, agent_count: int) -> str:
    """Format a header for multi-agent workflow."""
    border = "━" * BANNER_WIDTH
    return f"""
{magenta('┏' + border + '┓')}
{magenta('┃')}{f' {workflow_name.upper()} ':━^{BANNER_WIDTH}}{magenta('┃')}
{magenta('┃')}{f'{agent_count} agents queued':^{BANNER_WIDTH}}{magenta('┃')}
{magenta('┗' + border + '┛')}
"""


def format_agent_progress(
    agent_name: str,
    position: int,
    total: int,
    status: str = "pending"
) -> str:
    """
    Format a progress line for an agent in a workflow.

    Args:
        agent_name: Name of the agent
        position: Position in workflow (1-indexed)
        total: Total agents in workflow
        status: pending, running, complete, skipped

    Returns:
        Formatted progress line
    """
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").title()

    status_indicators = {
        "pending": "○",
        "running": "▶",
        "complete": "✓",
        "skipped": "⊘",
        "failed": "✗",
    }

    status_colors = {
        "pending": cyan,
        "running": yellow,
        "complete": green,
        "skipped": lambda x: x,  # no color
        "failed": red,
    }

    indicator = status_indicators.get(status, "?")
    color_fn = status_colors.get(status, lambda x: x)

    return f"  {color_fn(indicator)} [{position}/{total}] {color} {display_name} {RESET}"


def format_workflow_summary(
    completed: int,
    total: int,
    skipped: int = 0,
    failed: int = 0
) -> str:
    """Format a summary line for workflow completion."""
    parts = [f"{green(str(completed))} complete"]

    if skipped > 0:
        parts.append(f"{yellow(str(skipped))} skipped")

    if failed > 0:
        parts.append(f"{red(str(failed))} failed")

    return f"  Workflow: {' / '.join(parts)} of {total} agents"


# =============================================================================
# MEMORY LEARNING FEEDBACK
# =============================================================================

def format_learning_stored(
    agent_name: str,
    action: str,
    reason: str
) -> str:
    """
    Format a notification that a learning was stored.

    Args:
        agent_name: Agent involved
        action: accepted, rejected, modified
        reason: Why stored (for future reference)

    Returns:
        Formatted learning notification
    """
    action_colors = {
        "accepted": green,
        "rejected": red,
        "modified": yellow,
    }

    color_fn = action_colors.get(action, lambda x: x)
    display_name = agent_name.replace("-", " ").title()

    return f"{cyan('Memory:')} {color_fn(action.upper())} {display_name} - will adjust future suggestions"


def format_learning_applied(
    agent_name: str,
    adjustment: float,
    source_pattern: str
) -> str:
    """
    Format a notification that a past learning was applied.

    Args:
        agent_name: Agent affected
        adjustment: Confidence adjustment applied
        source_pattern: Pattern that triggered the adjustment

    Returns:
        Formatted notification
    """
    if adjustment > 0:
        adj_str = green(f"+{adjustment:.0f}%")
    else:
        adj_str = red(f"{adjustment:.0f}%")

    return f"{cyan('Memory:')} Applied {adj_str} to {agent_name} based on past: \"{source_pattern[:30]}...\""


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

def print_banner(banner: str, file=sys.stderr) -> None:
    """Print a banner to the specified file (default stderr)."""
    if COLORS_ENABLED:
        print(banner, file=file)
    else:
        # Strip ANSI codes if colors disabled
        import re
        clean = re.sub(r'\033\[[0-9;]*m', '', banner)
        print(clean, file=file)


def suppress_output() -> bool:
    """Check if output should be suppressed (e.g., in CI/non-interactive)."""
    # Check for common CI environment variables
    ci_vars = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL', 'TRAVIS']
    for var in ci_vars:
        if os.environ.get(var):
            return True

    # Check for explicit suppression
    if os.environ.get('CLAUDE_QUIET') or os.environ.get('CLAUDE_NO_BANNERS'):
        return True

    return False


# =============================================================================
# MAIN - Demo/Test
# =============================================================================

if __name__ == "__main__":
    print("=== AUTO-INVOKE BANNER ===", file=sys.stderr)
    banner = format_auto_invoke_banner(
        "security-scanner",
        confidence=92.5,
        mode="EXECUTE",
        show_breakdown=True,
        breakdown={
            "keyword_score": 85,
            "category_score": 95,
            "llm_score": 90,
            "memory_adj": 5,
            "weights": {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40}
        }
    )
    print_banner(banner)

    print("\n=== PROMPT BANNER ===", file=sys.stderr)
    banner = format_prompt_banner(
        "architect",
        confidence=72.3,
        reason="Detected architecture-related keywords",
        show_breakdown=True,
        breakdown={
            "keyword_score": 70,
            "category_score": 80,
            "llm_score": 65,
            "memory_adj": 0,
            "weights": {"keyword": 0.25, "category": 0.35, "llm_intent": 0.40}
        }
    )
    print_banner(banner)

    print("\n=== SUGGEST BANNER ===", file=sys.stderr)
    print_banner(format_suggest_banner(
        "performance-analyzer",
        confidence=45.0,
        reason="User mentioned 'slow'"
    ))

    print("\n=== WORKFLOW PROGRESS ===", file=sys.stderr)
    print_banner(format_workflow_header("Security Audit", 3))
    print_banner(format_agent_progress("security-scanner", 1, 3, "complete"))
    print_banner(format_agent_progress("dependency-auditor", 2, 3, "running"))
    print_banner(format_agent_progress("reviewer", 3, 3, "pending"))
    print_banner(format_workflow_summary(1, 3, 0, 0))

    print("\n=== MEMORY FEEDBACK ===", file=sys.stderr)
    print_banner(format_learning_stored("architect", "rejected", "User prefers direct implementation"))
    print_banner(format_learning_applied("brainstormer", -15, "just implement this"))
