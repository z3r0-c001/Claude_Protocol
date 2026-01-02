#!/usr/bin/env python3
"""
agent-announce.py - PreToolUse hook for Task tool
Outputs colored banners when agents are invoked with distinct visual styling
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# ANSI escape codes - comprehensive set
class Colors:
    # Reset
    RESET = "\033[0m"

    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

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


# Agent color schemes: (foreground, background, icon, category_label)
AGENT_THEMES = {
    # Quality agents - warm colors (red/orange/yellow spectrum)
    "security-scanner": (Colors.WHITE, Colors.BG_RED, "🔒", "SECURITY"),
    "laziness-destroyer": (Colors.BLACK, Colors.BG_BRIGHT_RED, "⚡", "QUALITY"),
    "hallucination-checker": (Colors.WHITE, Colors.BG_MAGENTA, "🔍", "VERIFY"),
    "honesty-evaluator": (Colors.BLACK, Colors.BG_BRIGHT_MAGENTA, "✓", "HONESTY"),
    "fact-checker": (Colors.WHITE, Colors.BG_BRIGHT_MAGENTA, "📚", "FACTS"),
    "reviewer": (Colors.BLACK, Colors.BG_YELLOW, "📝", "REVIEW"),
    "tester": (Colors.BLACK, Colors.BG_GREEN, "🧪", "TEST"),
    "test-coverage-enforcer": (Colors.BLACK, Colors.BG_BRIGHT_YELLOW, "📊", "COVERAGE"),

    # Core agents - blue spectrum
    "architect": (Colors.WHITE, Colors.BG_BLUE, "🏗️", "ARCHITECT"),
    "research-analyzer": (Colors.WHITE, Colors.BG_BRIGHT_BLUE, "🔬", "RESEARCH"),
    "performance-analyzer": (Colors.BLACK, Colors.BG_CYAN, "⚡", "PERF"),

    # Domain agents - green/cyan spectrum
    "codebase-analyzer": (Colors.BLACK, Colors.BG_GREEN, "📂", "ANALYZE"),
    "frontend-designer": (Colors.BLACK, Colors.BG_BRIGHT_CYAN, "🎨", "FRONTEND"),
    "ui-researcher": (Colors.WHITE, Colors.BG_CYAN, "🖼️", "UI"),
    "dependency-auditor": (Colors.BLACK, Colors.BG_BRIGHT_YELLOW, "📦", "DEPS"),
    "protocol-generator": (Colors.BLACK, Colors.BG_BRIGHT_GREEN, "⚙️", "PROTOCOL"),
    "protocol-analyzer": (Colors.BLACK, Colors.BG_GREEN, "⚙️", "PROTOCOL"),
    "protocol-updater": (Colors.BLACK, Colors.BG_BRIGHT_GREEN, "⬆️", "UPDATE"),
    "document-processor": (Colors.WHITE, Colors.BG_BLUE, "📄", "DOCS"),

    # Workflow agents - neutral/white spectrum
    "brainstormer": (Colors.BLACK, Colors.BG_WHITE, "💡", "IDEAS"),
    "orchestrator": (Colors.BLACK, Colors.BG_BRIGHT_WHITE, "🎯", "ORCHESTRATE"),

    # Built-in Claude agents
    "general-purpose": (Colors.WHITE, Colors.BG_BRIGHT_BLACK, "🤖", "AGENT"),
    "Explore": (Colors.BLACK, Colors.BG_CYAN, "🔎", "EXPLORE"),
    "Plan": (Colors.BLACK, Colors.BG_YELLOW, "📋", "PLAN"),
    "claude-code-guide": (Colors.WHITE, Colors.BG_BRIGHT_BLUE, "📖", "GUIDE"),
}

# Default theme for unknown agents
DEFAULT_THEME = (Colors.WHITE, Colors.BG_BRIGHT_BLACK, "🤖", "AGENT")


def get_agent_theme(agent_name: str) -> tuple:
    """Get theme for agent, checking agent file first, then defaults."""
    # Check built-in themes first
    if agent_name in AGENT_THEMES:
        return AGENT_THEMES[agent_name]

    # Try to find custom color in agent file
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    agent_paths = [
        Path(project_dir) / ".claude" / "agents" / "core" / f"{agent_name}.md",
        Path(project_dir) / ".claude" / "agents" / "quality" / f"{agent_name}.md",
        Path(project_dir) / ".claude" / "agents" / "domain" / f"{agent_name}.md",
        Path(project_dir) / ".claude" / "agents" / "workflow" / f"{agent_name}.md",
        Path(project_dir) / ".claude" / "agents" / f"{agent_name}.md",
    ]

    for agent_path in agent_paths:
        if agent_path.exists():
            try:
                content = agent_path.read_text()
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end != -1:
                        frontmatter = content[3:end]
                        for line in frontmatter.split("\n"):
                            if line.strip().startswith("color:"):
                                color_name = line.split(":", 1)[1].strip().strip('"\'').lower()
                                # Map color name to theme
                                color_map = {
                                    "red": (Colors.WHITE, Colors.BG_RED),
                                    "green": (Colors.BLACK, Colors.BG_GREEN),
                                    "blue": (Colors.WHITE, Colors.BG_BLUE),
                                    "yellow": (Colors.BLACK, Colors.BG_YELLOW),
                                    "magenta": (Colors.WHITE, Colors.BG_MAGENTA),
                                    "cyan": (Colors.BLACK, Colors.BG_CYAN),
                                    "white": (Colors.BLACK, Colors.BG_WHITE),
                                }
                                if color_name in color_map:
                                    fg, bg = color_map[color_name]
                                    return (fg, bg, "🤖", agent_name.upper()[:8])
            except Exception:
                pass

    return DEFAULT_THEME


def set_terminal_title(title: str):
    """Set terminal title using OSC escape sequence."""
    # OSC 0 sets both title and icon name
    sys.stderr.write(f"\033]0;{title}\007")
    sys.stderr.flush()


def create_banner(agent_name: str, description: str = "") -> str:
    """Create a visually distinct colored banner for the agent."""
    fg, bg, icon, category = get_agent_theme(agent_name)

    # Format agent name
    display_name = agent_name.replace("-", " ").upper()

    # Build the banner with background color
    banner_parts = []

    # Top border
    border_char = "━"
    width = max(len(display_name) + 16, 50)

    # Category tag
    tag = f" {category} "

    # Main banner line with full background
    banner_line = f"{icon}  {display_name}"
    padding = width - len(banner_line) - 2

    banner = f"""
{fg}{bg}{Colors.BOLD}┏{border_char * width}┓{Colors.RESET}
{fg}{bg}{Colors.BOLD}┃{tag:^{width}}┃{Colors.RESET}
{fg}{bg}{Colors.BOLD}┃  {banner_line}{' ' * padding}┃{Colors.RESET}
{fg}{bg}{Colors.BOLD}┗{border_char * width}┛{Colors.RESET}
"""

    return banner


def create_compact_banner(agent_name: str) -> str:
    """Create a compact single-line colored indicator."""
    fg, bg, icon, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").title()

    return f"{fg}{bg}{Colors.BOLD} {icon} {category}: {display_name} {Colors.RESET}"


def main():
    # Log hook invocation for debugging
    log_file = "/tmp/agent-announce-debug.log"
    try:
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] Hook invoked\n")
    except Exception:
        pass

    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            print('{"continue": true}')
            return

        data = json.loads(input_data)

        # Check if this is a Task tool invocation
        tool_name = data.get("tool_name", "")
        if tool_name != "Task":
            print('{"continue": true}')
            return

        # Get the subagent type and description
        tool_input = data.get("tool_input", {})
        subagent_type = tool_input.get("subagent_type", "")
        description = tool_input.get("description", "")

        if not subagent_type:
            print('{"continue": true}')
            return

        # Set terminal title
        set_terminal_title(f"🤖 {subagent_type}")

        # Print the banner to stderr (visible in terminal)
        banner = create_banner(subagent_type, description)
        print(banner, file=sys.stderr)

        # Log the agent invocation
        try:
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now().isoformat()}] Agent: {subagent_type} - {description}\n")
        except Exception:
            pass

        # Return JSON with optional message for Claude Code to display
        # The "message" field gets shown in Claude Code's output
        result = {
            "continue": True,
            "message": create_compact_banner(subagent_type)
        }
        print(json.dumps(result))

    except json.JSONDecodeError:
        print('{"continue": true}')
    except Exception as e:
        # Log error but don't block
        try:
            with open(log_file, "a") as f:
                f.write(f"[{datetime.now().isoformat()}] ERROR: {e}\n")
        except Exception:
            pass
        print('{"continue": true}')


if __name__ == "__main__":
    main()
