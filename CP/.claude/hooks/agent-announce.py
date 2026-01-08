#!/usr/bin/env python3
"""
agent-announce.py - PreToolUse hook for Task tool

Displays agent banners when agents are invoked and tracks invocations
for the enforcement system.

Note: ANSI colors do NOT work in hook output. Uses plain text formatting.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

_hooks_dir = os.path.dirname(os.path.abspath(__file__))
if _hooks_dir not in sys.path:
    sys.path.insert(0, _hooks_dir)

from colors import (
    format_agent_banner,
    format_status,
    json_output,
    BOX,
    ICONS,
)


# Fallback category mappings (used when registry unavailable)
FALLBACK_CATEGORIES = {
    "Explore": "EXPLORATION",
    "Plan": "PLANNING",
    "general-purpose": "GENERAL",
}

# Category group to display name mapping
CATEGORY_GROUP_DISPLAY = {
    "core": "CORE",
    "quality": "QUALITY",
    "domain": "DOMAIN",
    "workflow": "WORKFLOW",
}


def load_agent_registry() -> dict:
    """Load agent registry for dynamic category lookup."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        registry_path = Path(project_dir) / ".claude" / "agents" / "agent-registry.json"
    else:
        hooks_dir = Path(__file__).parent
        registry_path = hooks_dir.parent / "agents" / "agent-registry.json"

    if registry_path.exists():
        try:
            with open(registry_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"agents": {}}


def get_agent_category(agent_name: str) -> str:
    """
    Get display category for an agent - dynamically from registry.

    Falls back to category_group or default if not found.
    """
    # Check fallback first for built-in agents
    if agent_name in FALLBACK_CATEGORIES:
        return FALLBACK_CATEGORIES[agent_name]

    # Load from registry for dynamic lookup
    registry = load_agent_registry()
    agents = registry.get("agents", {})

    if agent_name in agents:
        agent_def = agents[agent_name]
        # Use category_group for display
        category_group = agent_def.get("category_group", "")
        if category_group:
            return CATEGORY_GROUP_DISPLAY.get(category_group, category_group.upper())
        # Fall back to first category
        categories = agent_def.get("categories", [])
        if categories:
            return categories[0].upper()

    return "AGENT"  # Default for unknown agents


def get_session_tracker_path() -> Path:
    """Get path to session-agents.json tracker."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        return Path(project_dir) / ".claude" / "memory" / "session-agents.json"
    # Fallback to relative path
    hooks_dir = Path(__file__).parent
    return hooks_dir.parent / "memory" / "session-agents.json"


def load_session_tracker() -> dict:
    """Load or initialize session tracker."""
    tracker_path = get_session_tracker_path()

    if tracker_path.exists():
        try:
            with open(tracker_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Return default structure
    return {
        "session_id": None,
        "started_at": None,
        "last_updated": None,
        "detected_context": {
            "prompt_analysis": None,
            "suggested_agents": [],
            "detected_patterns": [],
            "files_touched": [],
            "content_patterns_found": []
        },
        "invoked_agents": [],
        "enforcement": {
            "rules_triggered": [],
            "agents_required": [],
            "agents_satisfied": [],
            "pending_requirements": []
        }
    }


def save_session_tracker(tracker: dict) -> bool:
    """Save session tracker to disk."""
    tracker_path = get_session_tracker_path()

    try:
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tracker_path, "w") as f:
            json.dump(tracker, f, indent=2)
        return True
    except IOError:
        return False


def track_agent_invocation(agent_name: str, execution_mode: str, prompt: str) -> None:
    """Record an agent invocation in the session tracker."""
    tracker = load_session_tracker()

    # Update timestamp
    now = datetime.now().isoformat()
    if not tracker.get("started_at"):
        tracker["started_at"] = now
    tracker["last_updated"] = now

    # Add invocation record
    invocation = {
        "agent": agent_name,
        "mode": execution_mode,
        "timestamp": now,
        "prompt_snippet": prompt[:100] + "..." if len(prompt) > 100 else prompt
    }
    tracker["invoked_agents"].append(invocation)

    # Update enforcement tracking
    enforcement = tracker.get("enforcement", {})
    agents_required = enforcement.get("agents_required", [])
    agents_satisfied = enforcement.get("agents_satisfied", [])
    pending = enforcement.get("pending_requirements", [])

    # Mark agent as satisfied if it was required
    if agent_name in agents_required and agent_name not in agents_satisfied:
        agents_satisfied.append(agent_name)
        enforcement["agents_satisfied"] = agents_satisfied

        # Remove from pending
        pending = [p for p in pending if p.get("agent") != agent_name]
        enforcement["pending_requirements"] = pending

    tracker["enforcement"] = enforcement

    save_session_tracker(tracker)


def extract_execution_mode(prompt: str) -> str:
    """Extract execution_mode from prompt if specified."""
    prompt_lower = prompt.lower()
    if "execution_mode: plan" in prompt_lower or "execution_mode:plan" in prompt_lower:
        return "PLAN"
    elif "execution_mode: execute" in prompt_lower or "execution_mode:execute" in prompt_lower:
        return "EXECUTE"
    return ""


def format_banner_plain(agent_name: str, execution_mode: str = "") -> str:
    """Format a plain text agent banner with category."""
    category = get_agent_category(agent_name)
    display_name = agent_name.replace("-", " ").upper()

    width = 56

    lines = [
        f"{BOX['dtl']}{BOX['dh'] * width}{BOX['dtr']}",
        f"{BOX['dv']}{f'[{category}]':^{width}}{BOX['dv']}",
        f"{BOX['dv']}{display_name:^{width}}{BOX['dv']}",
    ]

    if execution_mode:
        lines.append(f"{BOX['dv']}{f'({execution_mode})':^{width}}{BOX['dv']}")

    lines.append(f"{BOX['dbl']}{BOX['dh'] * width}{BOX['dbr']}")

    return "\n".join(lines)


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

        # Track this invocation
        track_agent_invocation(subagent_type, execution_mode, prompt)

        # Check if banners are suppressed
        no_banners = os.environ.get("CLAUDE_NO_BANNERS", "") == "1"
        no_color = os.environ.get("NO_COLOR", "") == "1"

        if not no_banners and not no_color:
            # Print banner to stderr (plain text - colors don't work in hooks)
            banner = format_banner_plain(subagent_type, execution_mode)
            print(banner, file=sys.stderr)

        # Build context message for Claude
        category = get_agent_category(subagent_type)
        mode_str = f" ({execution_mode})" if execution_mode else ""
        context_msg = f"{ICONS['agent']} AGENT INVOKED: {subagent_type} [{category}]{mode_str}"

        # Output JSON with additional context
        print(json_output(
            additional_context=context_msg,
            hook_event="PreToolUse"
        ))

    except json.JSONDecodeError:
        print('{"continue": true}')
    except Exception as e:
        # Log error but don't block
        print(f"agent-announce error: {e}", file=sys.stderr)
        print('{"continue": true}')


if __name__ == "__main__":
    main()
