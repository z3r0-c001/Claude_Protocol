#!/usr/bin/env python3
"""
agent-response-handler.py - SubagentStop hook
Handles agent responses according to AGENT_PROTOCOL.md

When an agent returns with status: needs_approval, this hook:
1. Extracts the plan from present_to_user
2. Displays it clearly to the user
3. Prompts for approval before continuing

When status is complete with next_agents, it:
1. Shows suggested next agents
2. Asks user if they want to proceed with suggestions
"""

import json
import sys
import os
import re
from typing import Optional, Tuple

_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from colors import (
    ANSI,
    hook_status,
    get_agent_theme,
)


def extract_json_from_response(response: str) -> Optional[dict]:
    """Extract JSON block from agent response text."""
    # Try markdown code fence first
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, response)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try raw JSON at end
    brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(brace_pattern, response)
    
    for match in reversed(matches):
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and "agent" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue
    
    return None


def format_plan_approval(agent_name: str, response_data: dict) -> str:
    """Format plan for user approval."""
    fg, bg, category = get_agent_theme(agent_name)
    
    present = response_data.get("present_to_user", "No details provided.")
    scope = response_data.get("scope", {})
    
    output = f"""
{fg}{bg}{ANSI.BOLD}+{'='*58}+{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{' '*20}PLAN APPROVAL{' '*25}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}|{' '*18}Agent: {agent_name:<31}|{ANSI.RESET}
{fg}{bg}{ANSI.BOLD}+{'='*58}+{ANSI.RESET}

{present}
"""
    
    if scope:
        output += f"""
{ANSI.BOLD}Scope:{ANSI.RESET}
"""
        for key, value in scope.items():
            output += f"  {key}: {value}\n"
    
    output += f"""
{ANSI.BOLD}Options:{ANSI.RESET}
  [Y] Approve and execute
  [N] Cancel
  [M] Modify scope (explain changes)
"""
    return output


def format_next_agents(agent_name: str, next_agents: list) -> str:
    """Format next agent suggestions for user."""
    output = f"""
{ANSI.BOLD}Agent '{agent_name}' suggests running:{ANSI.RESET}
"""
    for i, agent in enumerate(next_agents, 1):
        name = agent.get("agent", "unknown")
        reason = agent.get("reason", "")
        parallel = agent.get("can_parallel", False)
        
        fg, bg, category = get_agent_theme(name)
        output += f"  {i}. {fg}{bg} {name} {ANSI.RESET}"
        if parallel:
            output += " (can run parallel)"
        output += f"\n     {reason}\n"
    
    output += f"""
{ANSI.BOLD}Options:{ANSI.RESET}
  [A] Run all suggested agents
  [1-{len(next_agents)}] Run specific agent
  [S] Skip suggestions
"""
    return output


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print('{"continue": true}')
        return

    # Get transcript to find agent response
    transcript_path = input_data.get("transcript_path")
    if not transcript_path:
        print('{"continue": true}')
        return

    # Read transcript
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError):
        print('{"continue": true}')
        return

    # Find last assistant response
    last_response = None
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            if entry.get("type") == "assistant":
                content = entry.get("message", {}).get("content", [])
                for block in content:
                    if block.get("type") == "text":
                        last_response = block.get("text", "")
                        break
                if last_response:
                    break
        except json.JSONDecodeError:
            continue

    if not last_response:
        print('{"continue": true}')
        return

    # Extract JSON response
    response_data = extract_json_from_response(last_response)
    
    if not response_data:
        hook_status("agent-response-handler", "OK", "No protocol response")
        print('{"continue": true}')
        return

    agent_name = response_data.get("agent", "unknown")
    status = response_data.get("status", "")
    execution_mode = response_data.get("execution_mode", "")
    next_agents = response_data.get("next_agents", [])

    # Handle needs_approval status
    if status == "needs_approval":
        hook_status("agent-response-handler", "WARN", f"{agent_name} needs approval")
        
        approval_prompt = format_plan_approval(agent_name, response_data)
        
        result = {
            "decision": "ask",
            "message": approval_prompt,
            "agentResponse": response_data
        }
        print(json.dumps(result))
        return

    # Handle complete with next_agents
    if status == "complete" and next_agents:
        hook_status("agent-response-handler", "OK", f"{agent_name} complete, {len(next_agents)} suggested")
        
        suggestion_prompt = format_next_agents(agent_name, next_agents)
        
        result = {
            "continue": True,
            "hookSpecificOutput": {
                "additionalContext": suggestion_prompt
            }
        }
        print(json.dumps(result))
        return

    # Handle blocked status
    if status == "blocked":
        blockers = response_data.get("blockers", [])
        hook_status("agent-response-handler", "BLOCK", f"{agent_name} blocked")
        
        blocker_text = "\n".join([f"  - {b.get('description', str(b))}" for b in blockers])
        
        result = {
            "continue": True,
            "hookSpecificOutput": {
                "additionalContext": f"\n{ANSI.BG_RED}{ANSI.BRIGHT_WHITE} AGENT BLOCKED {ANSI.RESET}\n{blocker_text}\n"
            }
        }
        print(json.dumps(result))
        return

    # Default: complete, pass through
    hook_status("agent-response-handler", "OK", f"{agent_name} {status}")
    print('{"continue": true}')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('{"continue": true}')
