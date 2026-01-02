#!/usr/bin/env python3
"""
agent-announce.py - PreToolUse hook for Task tool
Minimal semantic colorization for agents, tasks, and skills
"""

import json
import sys
import os

# ANSI escape codes - minimal set
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors only
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright variants
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"


# Agent categories and their colors
QUALITY_AGENTS = {
    "security-scanner", "laziness-destroyer", "hallucination-checker",
    "honesty-evaluator", "fact-checker", "reviewer", "tester",
    "test-coverage-enforcer"
}

CORE_AGENTS = {
    "architect", "research-analyzer", "performance-analyzer"
}

DOMAIN_AGENTS = {
    "codebase-analyzer", "frontend-designer", "ui-researcher",
    "dependency-auditor", "protocol-generator", "protocol-analyzer",
    "protocol-updater", "document-processor"
}

WORKFLOW_AGENTS = {
    "brainstormer", "orchestrator"
}

EXPLORE_AGENTS = {
    "Explore", "general-purpose", "claude-code-guide", "Plan"
}


def get_agent_color(agent_name: str) -> str:
    """Get color based on agent category."""
    if agent_name in QUALITY_AGENTS:
        return Colors.BRIGHT_RED
    elif agent_name in CORE_AGENTS:
        return Colors.BRIGHT_BLUE
    elif agent_name in DOMAIN_AGENTS:
        return Colors.BRIGHT_GREEN
    elif agent_name in WORKFLOW_AGENTS:
        return Colors.BRIGHT_YELLOW
    elif agent_name in EXPLORE_AGENTS:
        return Colors.BRIGHT_CYAN
    else:
        return Colors.WHITE


def format_agent(agent_name: str, description: str = "") -> str:
    """Format agent announcement - simple colored text."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").lower()

    if description:
        return f"{color}{Colors.BOLD}● {display_name}{Colors.RESET} {Colors.DIM}({description}){Colors.RESET}"
    return f"{color}{Colors.BOLD}● {display_name}{Colors.RESET}"


def format_subagent(agent_name: str) -> str:
    """Format sub-agent - dimmed and indented."""
    color = get_agent_color(agent_name)
    display_name = agent_name.replace("-", " ").lower()
    return f"  {Colors.DIM}{color}◦ {display_name}{Colors.RESET}"


def format_task(description: str) -> str:
    """Format task announcement."""
    return f"{Colors.CYAN}▶ {description}{Colors.RESET}"


def format_skill(skill_name: str) -> str:
    """Format skill invocation."""
    return f"{Colors.GREEN}/{skill_name}{Colors.RESET}"


def set_terminal_title(title: str):
    """Set terminal title."""
    sys.stderr.write(f"\033]0;{title}\007")
    sys.stderr.flush()


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print('{"continue": true}')
            return

        data = json.loads(input_data)
        tool_name = data.get("tool_name", "")

        if tool_name != "Task":
            print('{"continue": true}')
            return

        tool_input = data.get("tool_input", {})
        subagent_type = tool_input.get("subagent_type", "")
        description = tool_input.get("description", "")

        if not subagent_type:
            print('{"continue": true}')
            return

        # Set terminal title
        set_terminal_title(f"● {subagent_type}")

        # Print minimal announcement to stderr
        announcement = format_agent(subagent_type, description)
        print(announcement, file=sys.stderr)

        # Return success
        print(json.dumps({"continue": True}))

    except Exception:
        print('{"continue": true}')


if __name__ == "__main__":
    main()
