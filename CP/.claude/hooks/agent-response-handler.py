#!/usr/bin/env python3
"""
agent-response-handler.py - SubagentStop hook
Handles agent responses according to AGENT_PROTOCOL.md using official Claude Code API.

When an agent returns with status: needs_approval, this hook:
1. Blocks the completion with decision: "block"
2. Provides reason that tells Claude to present plan and wait for approval

Uses official Claude Code SubagentStop format:
- decision: "block" prevents agent from stopping
- reason: fed back to Claude explaining what to do next
"""

import json
import sys
import os
import re
from typing import Optional

_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

try:
    from colors import hook_status, get_agent_theme
except ImportError:
    def hook_status(*args, **kwargs): pass
    def get_agent_theme(name): return ("", "", "AGENT")


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
    
    # Try raw JSON at end - look for complete objects
    # Match nested JSON properly
    try:
        # Find last { that might start a JSON object
        last_brace = response.rfind('{')
        while last_brace >= 0:
            try:
                # Try to parse from this position
                candidate = response[last_brace:]
                # Find matching closing brace
                depth = 0
                end_pos = 0
                for i, c in enumerate(candidate):
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            end_pos = i + 1
                            break
                
                if end_pos > 0:
                    json_str = candidate[:end_pos]
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and "agent" in parsed:
                        return parsed
            except json.JSONDecodeError:
                pass
            
            # Try earlier brace
            last_brace = response.rfind('{', 0, last_brace)
    except Exception:
        pass
    
    return None


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
    present_to_user = response_data.get("present_to_user", "")

    # Handle needs_approval status - BLOCK and tell Claude what to do
    if status == "needs_approval":
        hook_status("agent-response-handler", "WARN", f"{agent_name} needs approval")
        
        # Use official SubagentStop format
        # decision: "block" prevents completion, reason goes to Claude
        result = {
            "decision": "block",
            "reason": (
                f"AGENT REQUIRES APPROVAL\n\n"
                f"Agent '{agent_name}' returned status: needs_approval\n"
                f"Execution mode: {execution_mode}\n\n"
                f"You MUST present the following to the user and wait for explicit approval:\n\n"
                f"---\n{present_to_user}\n---\n\n"
                f"After user approves:\n"
                f"- Invoke the agent again with execution_mode: execute\n"
                f"- Include any modifications the user requested\n\n"
                f"If user denies:\n"
                f"- Report that the operation was cancelled\n"
                f"- Ask if they want to modify the scope"
            )
        }
        print(json.dumps(result))
        return

    # Handle blocked status
    if status == "blocked":
        blockers = response_data.get("blockers", [])
        hook_status("agent-response-handler", "BLOCK", f"{agent_name} blocked")
        
        blocker_text = "\n".join([f"- {b.get('description', str(b))}" for b in blockers])
        
        result = {
            "decision": "block",
            "reason": (
                f"AGENT BLOCKED\n\n"
                f"Agent '{agent_name}' cannot proceed due to blockers:\n"
                f"{blocker_text}\n\n"
                f"Address these blockers before continuing."
            )
        }
        print(json.dumps(result))
        return

    # Handle complete with next_agents suggestions
    if status == "complete" and next_agents:
        hook_status("agent-response-handler", "OK", f"{agent_name} complete, {len(next_agents)} suggested")
        
        suggestions = []
        for agent in next_agents:
            name = agent.get("agent", "unknown")
            reason = agent.get("reason", "")
            parallel = agent.get("can_parallel", False)
            suggestions.append(f"- {name}: {reason}" + (" (can run parallel)" if parallel else ""))
        
        suggestion_text = "\n".join(suggestions)
        
        # Continue but inject suggestion context
        result = {
            "continue": True,
            "hookSpecificOutput": {
                "additionalContext": (
                    f"\n\nAGENT SUGGESTIONS\n"
                    f"Agent '{agent_name}' suggests running:\n"
                    f"{suggestion_text}\n\n"
                    f"Consider invoking these agents if appropriate for the task."
                )
            }
        }
        print(json.dumps(result))
        return

    # Handle needs_input status
    if status == "needs_input":
        hook_status("agent-response-handler", "WARN", f"{agent_name} needs input")
        
        result = {
            "decision": "block",
            "reason": (
                f"AGENT NEEDS INPUT\n\n"
                f"Agent '{agent_name}' requires additional information.\n\n"
                f"Present to user:\n{present_to_user}\n\n"
                f"After getting user input, invoke the agent again with the additional context."
            )
        }
        print(json.dumps(result))
        return

    # Default: complete, pass through
    hook_status("agent-response-handler", "OK", f"{agent_name} {status}")
    print('{"continue": true}')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        print('{"continue": true}')
