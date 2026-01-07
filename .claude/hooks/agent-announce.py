#!/usr/bin/env python3
"""
agent-announce.py - PreToolUse hook for Task tool
Displays colored banners when agents are invoked, showing execution mode.
"""

import json
import sys
import os
import re

_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from colors import (
    ANSI,
    COLORS_ENABLED,
    get_agent_theme,
)


def set_terminal_title(title: str) -> None:
    """Set terminal title using OSC escape sequence."""
    if COLORS_ENABLED:
        sys.stderr.write(f"\033]0;{title}\007")
        sys.stderr.flush()


def extract_execution_mode(prompt: str) -> str:
    """Extract execution_mode from prompt if specified."""
    prompt_lower = prompt.lower()
    if "execution_mode: plan" in prompt_lower or "execution_mode:plan" in prompt_lower:
        return "PLAN"
    elif "execution_mode: execute" in prompt_lower or "execution_mode:execute" in prompt_lower:
        return "EXECUTE"
    return ""


def format_agent_banner(agent_name: str, execution_mode: str = "") -> str:
    """Format a colored agent banner with execution mode."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").upper()
    
    width = 58
    border = "=" * width
    
    # Mode indicator
    if execution_mode:
        mode_str = f" [{execution_mode}] "
        mode_line = f"|{mode_str:^{width}}|"
    else:
        mode_line = ""
    
    # Build banner
    banner = f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{category:^{width}}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{display_name:^{width}}|{ANSI.RESET}"""
    
    if mode_line:
        banner += f"""
{fg}{bg}{ANSI.BOLD}{mode_line}{ANSI.RESET}"""
    
    banner += f"""
{fg}{bg}{ANSI.BOLD}+{border}+{ANSI.RESET}
"""
    return banner


def format_agent_compact(agent_name: str, execution_mode: str = "") -> str:
    """Format a compact single-line agent indicator."""
    fg, bg, category = get_agent_theme(agent_name)
    display_name = agent_name.replace("-", " ").title()
    
    if execution_mode:
        return f"{fg}{bg}{ANSI.BOLD} [{category}] {display_name} ({execution_mode}) {ANSI.RESET}"
    return f"{fg}{bg}{ANSI.BOLD} [{category}] {display_name} {ANSI.RESET}"


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
        prompt = tool_input.get("prompt", "")

        if not subagent_type:
            print('{"continue": true}')
            return

        # Extract execution mode from prompt
        execution_mode = extract_execution_mode(prompt)

        # Set terminal title
        title = f"Agent: {subagent_type}"
        if execution_mode:
            title += f" ({execution_mode})"
        set_terminal_title(title)

        # Print banner to stderr
        banner = format_agent_banner(subagent_type, execution_mode)
        print(banner, file=sys.stderr)

        # Return with compact message
        result = {
            "continue": True,
            "message": format_agent_compact(subagent_type, execution_mode)
        }
        print(json.dumps(result))

    except json.JSONDecodeError:
        print('{"continue": true}')
    except Exception:
        print('{"continue": true}')


if __name__ == "__main__":
    main()
