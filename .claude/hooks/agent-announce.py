#!/usr/bin/env python3
"""
agent-announce.py - PreToolUse hook for Task tool
Outputs colored banners when agents are invoked
"""

import json
import sys
import os
from pathlib import Path

# ANSI color codes
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

# Fallback colors if agent doesn't specify one
DEFAULT_COLORS = {
    # Core agents
    "architect": "blue",
    "research-analyzer": "bright_blue",
    "performance-analyzer": "cyan",
    # Quality agents
    "security-scanner": "red",
    "laziness-destroyer": "bright_red",
    "hallucination-checker": "magenta",
    "honesty-evaluator": "bright_magenta",
    "reviewer": "yellow",
    "tester": "green",
    "test-coverage-enforcer": "bright_yellow",
    "fact-checker": "bright_magenta",
    # Domain agents
    "codebase-analyzer": "green",
    "frontend-designer": "bright_cyan",
    "ui-researcher": "cyan",
    "dependency-auditor": "bright_yellow",
    "protocol-generator": "bright_green",
    "protocol-analyzer": "green",
    "protocol-updater": "bright_green",
    "document-processor": "blue",
    # Workflow agents
    "brainstormer": "white",
    "orchestrator": "bright_white",
    # Built-in agents
    "general-purpose": "white",
    "Explore": "cyan",
    "Plan": "yellow",
}

# Icons for agent categories
ICONS = {
    "security": "🔒",
    "laziness": "⚡",
    "hallucination": "🔍",
    "honesty": "✓",
    "reviewer": "📝",
    "tester": "🧪",
    "test-coverage": "📊",
    "fact": "📚",
    "architect": "🏗️",
    "research": "🔬",
    "performance": "⚡",
    "codebase": "📂",
    "frontend": "🎨",
    "ui": "🖼️",
    "dependency": "📦",
    "protocol": "⚙️",
    "document": "📄",
    "brainstormer": "💡",
    "orchestrator": "🎯",
    "general": "🤖",
    "explore": "🔎",
    "plan": "📋",
}


def get_icon(agent_name: str) -> str:
    """Get icon for agent based on name patterns."""
    name_lower = agent_name.lower()
    for key, icon in ICONS.items():
        if key in name_lower:
            return icon
    return "🤖"


def get_agent_color(agent_name: str) -> str:
    """Get color for agent, checking agent file first, then defaults."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")

    # Try to find and read agent file
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
                # Parse YAML frontmatter for color
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end != -1:
                        frontmatter = content[3:end]
                        for line in frontmatter.split("\n"):
                            if line.strip().startswith("color:"):
                                color = line.split(":", 1)[1].strip().strip('"\'')
                                if color in COLORS:
                                    return color
            except Exception:
                pass

    # Fall back to default colors
    return DEFAULT_COLORS.get(agent_name, "white")


def print_banner(agent_name: str, color_name: str):
    """Print colored banner for agent."""
    color = COLORS.get(color_name, COLORS["white"])
    reset = COLORS["reset"]
    bold = COLORS["bold"]
    icon = get_icon(agent_name)

    # Create banner
    name_display = agent_name.upper().replace("-", " ")
    width = max(len(name_display) + 6, 40)

    # Print to stderr so it doesn't interfere with JSON output
    banner = f"""
{color}{bold}╭{'─' * width}╮
│  {icon}  {name_display}{' ' * (width - len(name_display) - 5)}│
╰{'─' * width}╯{reset}
"""
    print(banner, file=sys.stderr)


def main():
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

        # Get the subagent type
        tool_input = data.get("tool_input", {})
        subagent_type = tool_input.get("subagent_type", "")

        if not subagent_type:
            print('{"continue": true}')
            return

        # Get color and print banner
        color = get_agent_color(subagent_type)
        print_banner(subagent_type, color)

        # Always continue
        print('{"continue": true}')

    except json.JSONDecodeError:
        print('{"continue": true}')
    except Exception as e:
        print(f'[AGENT-ANNOUNCE] Error: {e}', file=sys.stderr)
        print('{"continue": true}')


if __name__ == "__main__":
    main()
