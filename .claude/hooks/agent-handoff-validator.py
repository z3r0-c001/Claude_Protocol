#!/usr/bin/env python3
"""
Agent Handoff Validator for Claude Code
=========================================
SubagentStop hook that validates agent responses match the AGENT_PROTOCOL.md standard.

Validates:
1. Response contains required fields (agent, execution_mode, status, present_to_user)
2. Status is valid value
3. JSON is well-formed
4. Extracts present_to_user for display

Output:
- If valid: {"continue": true, "hookSpecificOutput": {"additionalContext": "..."}}
- If invalid: {"decision": "block", "reason": "..."}
"""

import json
import sys
import re
from typing import Optional, Tuple

# Required fields in agent response
REQUIRED_FIELDS = ["agent", "execution_mode", "status", "present_to_user"]

# Valid values for status field
VALID_STATUS = ["complete", "blocked", "needs_approval", "needs_input"]

# Valid values for execution_mode field
VALID_EXECUTION_MODE = ["plan", "execute"]


def extract_json_from_response(response: str) -> Optional[dict]:
    """Extract JSON block from agent response text."""
    # Try to find JSON block in markdown code fence
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, response)

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # Try to find raw JSON object at end of response
    # Look for { ... } pattern that could be JSON
    brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(brace_pattern, response)

    # Try matches from end of response (most likely to be the final output)
    for match in reversed(matches):
        try:
            parsed = json.loads(match)
            # Check if it looks like an agent response
            if isinstance(parsed, dict) and "agent" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    return None


def validate_agent_response(response_data: dict) -> Tuple[bool, list]:
    """Validate agent response against AGENT_PROTOCOL.md standard."""
    issues = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in response_data:
            issues.append(f"Missing required field: {field}")

    # Validate status value
    if "status" in response_data:
        if response_data["status"] not in VALID_STATUS:
            issues.append(f"Invalid status '{response_data['status']}'. Must be one of: {VALID_STATUS}")

    # Validate execution_mode value
    if "execution_mode" in response_data:
        if response_data["execution_mode"] not in VALID_EXECUTION_MODE:
            issues.append(f"Invalid execution_mode '{response_data['execution_mode']}'. Must be one of: {VALID_EXECUTION_MODE}")

    # Validate present_to_user is a string
    if "present_to_user" in response_data:
        if not isinstance(response_data["present_to_user"], str):
            issues.append("present_to_user must be a string")

    # Validate findings structure if present
    if "findings" in response_data:
        findings = response_data["findings"]
        if not isinstance(findings, dict):
            issues.append("findings must be an object")
        elif "summary" not in findings:
            issues.append("findings.summary is required")

    # Validate next_agents structure if present
    if "next_agents" in response_data:
        next_agents = response_data["next_agents"]
        if not isinstance(next_agents, list):
            issues.append("next_agents must be an array")
        else:
            for i, agent in enumerate(next_agents):
                if not isinstance(agent, dict):
                    issues.append(f"next_agents[{i}] must be an object")
                elif "agent" not in agent:
                    issues.append(f"next_agents[{i}].agent is required")

    return len(issues) == 0, issues


def format_handoff_context(response_data: dict) -> str:
    """Format agent response for handoff to primary agent."""
    parts = []

    agent_name = response_data.get("agent", "Unknown Agent")
    execution_mode = response_data.get("execution_mode", "unknown")
    status = response_data.get("status", "unknown")

    parts.append(f"AGENT HANDOFF: {agent_name} ({execution_mode} mode) - Status: {status}")

    # Add present_to_user content
    if "present_to_user" in response_data:
        parts.append(f"\n{response_data['present_to_user']}")

    # Add next_agents if present
    if "next_agents" in response_data and response_data["next_agents"]:
        agents = [a.get("agent", "?") for a in response_data["next_agents"]]
        parts.append(f"\nSuggested next agents: {', '.join(agents)}")

    # Add blockers if present
    if "blockers" in response_data and response_data["blockers"]:
        blockers = [b.get("description", str(b)) for b in response_data["blockers"]]
        parts.append(f"\nBlockers: {'; '.join(blockers)}")

    return "".join(parts)


def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # No input or invalid JSON - allow through
        print('{"continue": true}')
        sys.exit(0)

    # Get transcript path to read agent output
    transcript_path = input_data.get("transcript_path")
    if not transcript_path:
        print('{"continue": true}')
        sys.exit(0)

    # Try to read the transcript to get last assistant response
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError):
        print('{"continue": true}')
        sys.exit(0)

    # Find the last assistant message
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
        sys.exit(0)

    # Try to extract and validate JSON response
    response_data = extract_json_from_response(last_response)

    if response_data is None:
        # No JSON found - this might be a legacy agent or non-protocol response
        # Allow through but don't provide structured handoff
        print('{"continue": true}')
        sys.exit(0)

    # Validate the response
    is_valid, issues = validate_agent_response(response_data)

    if not is_valid:
        # Response doesn't match protocol - warn but don't block
        # Blocking would break legacy agents
        context = f"AGENT PROTOCOL WARNING: Response missing required fields: {'; '.join(issues)}"
        result = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "SubagentStop",
                "additionalContext": context
            }
        }
        print(json.dumps(result))
        sys.exit(0)

    # Valid response - format for handoff
    handoff_context = format_handoff_context(response_data)

    result = {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "SubagentStop",
            "additionalContext": handoff_context
        }
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Absolute fallback - always output valid JSON
        print('{"continue": true}')
        sys.exit(0)
