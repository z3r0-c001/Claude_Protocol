#!/usr/bin/env python3
"""
agent-plan-enforcer.py - PreToolUse hook for Task tool
Enforces plan mode for agents that support it.

When an agent with supports_plan_mode: true is invoked WITHOUT
execution_mode specified, this hook:
1. Warns that plan mode should be used
2. Suggests the corrected prompt
3. Asks user whether to proceed anyway or use plan mode

This is "guided enforcement" - not blocking, but ensuring the user
is aware and makes a conscious choice.
"""

import json
import sys
import os
import re
from pathlib import Path

# Add hooks directory to path
_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from colors import (
    ANSI,
    hook_status,
    format_agent_banner,
)

# Cache for agent metadata
_agent_cache = {}


def get_project_dir() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def load_agent_metadata(agent_name: str) -> dict:
    """Load agent frontmatter to check for supports_plan_mode."""
    if agent_name in _agent_cache:
        return _agent_cache[agent_name]
    
    project_dir = get_project_dir()
    search_paths = [
        f".claude/agents/core/{agent_name}.md",
        f".claude/agents/quality/{agent_name}.md",
        f".claude/agents/domain/{agent_name}.md",
        f".claude/agents/workflow/{agent_name}.md",
        f".claude/agents/{agent_name}.md",
    ]
    
    for rel_path in search_paths:
        agent_path = Path(project_dir) / rel_path
        if agent_path.exists():
            try:
                content = agent_path.read_text()
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end != -1:
                        frontmatter = content[3:end]
                        metadata = {}
                        for line in frontmatter.split("\n"):
                            if ":" in line:
                                key, value = line.split(":", 1)
                                key = key.strip()
                                value = value.strip().strip('"\'')
                                if value.lower() == "true":
                                    value = True
                                elif value.lower() == "false":
                                    value = False
                                metadata[key] = value
                        _agent_cache[agent_name] = metadata
                        return metadata
            except Exception:
                pass
    
    _agent_cache[agent_name] = {}
    return {}


def check_execution_mode_in_prompt(prompt: str) -> str:
    """Check if execution_mode is specified in the prompt."""
    prompt_lower = prompt.lower()
    
    if "execution_mode: plan" in prompt_lower or "execution_mode:plan" in prompt_lower:
        return "plan"
    elif "execution_mode: execute" in prompt_lower or "execution_mode:execute" in prompt_lower:
        return "execute"
    
    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print('{"continue": true}')
        return

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Task":
        print('{"continue": true}')
        return

    tool_input = input_data.get("tool_input", {})
    agent_name = tool_input.get("subagent_type", "")
    prompt = tool_input.get("prompt", "")

    if not agent_name:
        print('{"continue": true}')
        return

    # Load agent metadata
    metadata = load_agent_metadata(agent_name)
    supports_plan_mode = metadata.get("supports_plan_mode", False)

    # Check current execution mode in prompt
    current_mode = check_execution_mode_in_prompt(prompt)

    # If agent supports plan mode but no mode specified
    if supports_plan_mode and current_mode is None:
        hook_status("agent-plan-enforcer", "WARN", f"{agent_name} supports plan mode")
        
        # Build guidance message
        guidance = f"""
{ANSI.BOLD}{ANSI.BG_YELLOW}{ANSI.BLACK} PLAN MODE RECOMMENDED {ANSI.RESET}

Agent '{agent_name}' supports plan mode but none was specified.

{ANSI.BOLD}Recommended:{ANSI.RESET} Add 'execution_mode: plan' to get scope assessment first.

{ANSI.BOLD}Example prompt:{ANSI.RESET}
  execution_mode: plan
  
  {prompt[:100]}{'...' if len(prompt) > 100 else ''}

{ANSI.BOLD}Plan mode benefits:{ANSI.RESET}
  - See scope before execution (files, complexity)
  - Approve or adjust before work begins
  - Better control over agent behavior

{ANSI.BOLD}Options:{ANSI.RESET}
  [P] Use plan mode (recommended)
  [E] Execute directly without plan
  [C] Cancel
"""
        
        # Return with user prompt
        result = {
            "decision": "ask",
            "message": guidance,
            "options": {
                "P": "Rerun with execution_mode: plan",
                "E": "Execute without plan mode",
                "C": "Cancel"
            }
        }
        print(json.dumps(result))
        return

    # Show execution mode in status
    if current_mode:
        hook_status("agent-plan-enforcer", "OK", f"{agent_name} ({current_mode.upper()} mode)")
    else:
        hook_status("agent-plan-enforcer", "OK", f"{agent_name} (no plan mode)")

    print('{"continue": true}')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('{"continue": true}')
