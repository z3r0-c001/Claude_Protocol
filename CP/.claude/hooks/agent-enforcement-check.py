#!/usr/bin/env python3
"""
agent-enforcement-check.py - Stop hook for agent usage enforcement

Validates that required agents were used based on:
1. File patterns modified during session
2. Content patterns detected
3. Prompt patterns that triggered rules
4. Multi-file thresholds

Strictness levels:
- block: Stop completion until agent is used
- warn: Show warning but allow completion
- off: No enforcement

Configuration: .claude/config/enforcement-rules.json
Session state: .claude/memory/session-agents.json
"""

import json
import sys
import os
import re
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from colors import (
        format_banner,
        format_status,
        json_output,
        ICONS,
        BOX,
    )
except ImportError:
    def format_banner(title, width=50): return f"=== {title} ==="
    def format_status(hook, status, detail=""): return f"{hook}: {status} {detail}"
    def json_output(**kwargs): return json.dumps(kwargs)
    ICONS = {"warning": "!", "error": "X", "success": "OK", "blocked": "X"}
    BOX = {"dh": "=", "dv": "|", "dtl": "+", "dtr": "+", "dbl": "+", "dbr": "+"}


def get_project_dir() -> str:
    """Get project directory from environment or cwd."""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())


def load_enforcement_rules() -> dict:
    """Load enforcement-rules.json configuration."""
    project_dir = get_project_dir()
    rules_path = Path(project_dir) / ".claude" / "config" / "enforcement-rules.json"

    if rules_path.exists():
        try:
            return json.loads(rules_path.read_text())
        except (json.JSONDecodeError, IOError):
            pass

    return {"enabled": False, "rules": {}}


def load_session_tracker() -> dict:
    """Load session-agents.json tracker."""
    project_dir = get_project_dir()
    tracker_path = Path(project_dir) / ".claude" / "memory" / "session-agents.json"

    if tracker_path.exists():
        try:
            return json.loads(tracker_path.read_text())
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "detected_context": {},
        "invoked_agents": [],
        "enforcement": {
            "rules_triggered": [],
            "agents_required": [],
            "agents_satisfied": [],
            "pending_requirements": []
        }
    }


def load_file_edit_tracker() -> List[str]:
    """Load list of files edited during session from file-edit-tracker."""
    project_dir = get_project_dir()
    tracker_path = Path(project_dir) / ".claude" / "memory" / "edited-files.txt"

    if tracker_path.exists():
        try:
            return [
                line.strip()
                for line in tracker_path.read_text().splitlines()
                if line.strip()
            ]
        except IOError:
            pass

    return []


def check_file_patterns(files: List[str], patterns: List[str]) -> bool:
    """Check if any files match the given glob patterns."""
    for filepath in files:
        for pattern in patterns:
            # Normalize paths for matching
            filepath_normalized = filepath.replace("\\", "/")
            if fnmatch.fnmatch(filepath_normalized, pattern):
                return True
            # Also check basename
            if fnmatch.fnmatch(os.path.basename(filepath), pattern.split("/")[-1]):
                return True
    return False


def get_invoked_agent_names(tracker: dict) -> List[str]:
    """Extract list of invoked agent names from tracker."""
    invoked = tracker.get("invoked_agents", [])
    return [inv.get("agent", "") for inv in invoked if inv.get("agent")]


def load_agent_registry() -> dict:
    """Load agent registry for category lookup."""
    project_dir = get_project_dir()
    registry_path = Path(project_dir) / ".claude" / "agents" / "agent-registry.json"

    if registry_path.exists():
        try:
            return json.loads(registry_path.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return {"agents": {}}


def get_agent_categories(agent_name: str, registry: dict) -> List[str]:
    """Get categories for an agent from the registry."""
    agents = registry.get("agents", {})
    if agent_name in agents:
        return agents[agent_name].get("categories", [])
    return []


def get_invoked_categories(invoked_agents: List[str], registry: dict) -> set:
    """Get all categories covered by invoked agents."""
    categories = set()
    for agent in invoked_agents:
        agent_cats = get_agent_categories(agent, registry)
        categories.update(agent_cats)
    return categories


def check_requirement_satisfied(
    required_agents: List[str],
    required_categories: List[str],
    invoked_agents: List[str],
    invoked_categories: set
) -> bool:
    """
    Check if a rule's requirements are satisfied.

    Satisfied if ANY of:
    - A required_agent was invoked, OR
    - An agent with a required_category was invoked
    """
    # Check specific agents
    for agent in required_agents:
        if agent in invoked_agents:
            return True

    # Check categories
    for category in required_categories:
        if category in invoked_categories:
            return True

    return False


def check_exemptions(
    rules_config: dict,
    files_edited: List[str],
    prompt: str
) -> Tuple[bool, str]:
    """
    Check if current session qualifies for exemption from enforcement.

    Returns (is_exempt, reason)
    """
    exemptions = rules_config.get("exemptions", {})

    # Check max files exemption
    max_files = exemptions.get("max_files", 1)
    if len(files_edited) <= max_files:
        return True, f"Only {len(files_edited)} file(s) modified (threshold: {max_files})"

    # Check prompt patterns for informational queries
    prompt_patterns = exemptions.get("prompt_patterns", [])
    prompt_lower = prompt.lower() if prompt else ""
    for pattern in prompt_patterns:
        try:
            if re.match(pattern, prompt_lower, re.IGNORECASE):
                return True, f"Informational query detected"
        except re.error:
            continue

    return False, ""


def evaluate_rules(
    rules_config: dict,
    tracker: dict,
    files_edited: List[str]
) -> List[dict]:
    """
    Evaluate all enforcement rules against current session.

    Supports both specific agent requirements and category-based matching.
    A rule is satisfied if ANY required agent OR any agent with a required category was invoked.

    Returns list of violations: [{rule, required_agent, strictness, message}]
    """
    violations = []
    rules = rules_config.get("rules", {})
    invoked_agents = get_invoked_agent_names(tracker)

    # Load registry for category matching
    registry = load_agent_registry()
    invoked_categories = get_invoked_categories(invoked_agents, registry)

    # Also check pre-computed requirements from prompt analysis
    enforcement = tracker.get("enforcement", {})
    pending_requirements = enforcement.get("pending_requirements", [])

    # Check each pending requirement (from prompt analysis)
    for req in pending_requirements:
        agent = req.get("agent", "")
        rule_name = req.get("rule", "unknown")

        # Get the full rule definition to check categories
        rule_def = rules.get(rule_name, {})
        required_agents = rule_def.get("required_agents", [agent] if agent else [])
        required_categories = rule_def.get("required_categories", [])

        if not check_requirement_satisfied(required_agents, required_categories, invoked_agents, invoked_categories):
            violations.append({
                "rule": rule_name,
                "required_agent": agent or "agent in category",
                "strictness": req.get("strictness", "warn"),
                "message": req.get("message", f"Required agent/category not invoked")
            })

    # Additionally check file-based rules
    for rule_name, rule_def in rules.items():
        if not rule_def.get("enabled", True):
            continue

        trigger = rule_def.get("trigger", {})
        required_agents = rule_def.get("required_agents", [])
        required_categories = rule_def.get("required_categories", [])
        strictness = rule_def.get("strictness", "warn")
        message = rule_def.get("message", "")

        triggered = False

        # Check file patterns
        file_patterns = trigger.get("file_patterns", [])
        if file_patterns and files_edited:
            if check_file_patterns(files_edited, file_patterns):
                triggered = True

        # Check file count threshold
        file_threshold = trigger.get("file_count_threshold", 0)
        if file_threshold > 0 and len(files_edited) >= file_threshold:
            triggered = True

        if triggered:
            # Check if satisfied by agent OR category
            if not check_requirement_satisfied(required_agents, required_categories, invoked_agents, invoked_categories):
                # Check if not already in violations
                already_added = any(
                    v.get("rule") == rule_name
                    for v in violations
                )
                if not already_added:
                    # Describe what's needed
                    needed = []
                    if required_agents:
                        needed.append(f"agents: {required_agents}")
                    if required_categories:
                        needed.append(f"categories: {required_categories}")

                    violations.append({
                        "rule": rule_name,
                        "required_agent": required_agents[0] if required_agents else f"[{required_categories[0]}]",
                        "strictness": strictness,
                        "message": message or f"Rule '{rule_name}' requires {' or '.join(needed)}"
                    })

    return violations


def format_violations_message(violations: List[dict]) -> str:
    """Format violations into a readable message."""
    lines = []
    lines.append(f"\n{BOX['dtl']}{BOX['dh'] * 56}{BOX['dtr']}")
    lines.append(f"{BOX['dv']}{'AGENT ENFORCEMENT VIOLATIONS':^56}{BOX['dv']}")
    lines.append(f"{BOX['dbl']}{BOX['dh'] * 56}{BOX['dbr']}")
    lines.append("")

    blocking = [v for v in violations if v.get("strictness") == "block"]
    warnings = [v for v in violations if v.get("strictness") == "warn"]

    if blocking:
        lines.append(f"{ICONS['blocked']} BLOCKING VIOLATIONS:")
        for v in blocking:
            lines.append(f"  • [{v['rule']}] {v['message']}")
            lines.append(f"    Required: {v['required_agent']}")
        lines.append("")

    if warnings:
        lines.append(f"{ICONS['warning']} WARNINGS:")
        for v in warnings:
            lines.append(f"  • [{v['rule']}] {v['message']}")
            lines.append(f"    Recommended: {v['required_agent']}")
        lines.append("")

    if blocking:
        lines.append(f"{ICONS['info']} To proceed: Invoke the required agent(s) using the Task tool")

    return "\n".join(lines)


def main():
    """Main enforcement check logic."""
    try:
        input_data = sys.stdin.read()
        # Stop hook may receive empty input or JSON
        if input_data.strip():
            try:
                data = json.loads(input_data)
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        # Load configuration
        rules_config = load_enforcement_rules()

        if not rules_config.get("enabled", True):
            # Enforcement disabled
            print('{}')
            return

        # Load session state
        tracker = load_session_tracker()
        files_edited = load_file_edit_tracker()

        # Get original prompt from context (if available)
        detected = tracker.get("detected_context", {})
        prompt_analysis = detected.get("prompt_analysis", {})
        original_prompt = prompt_analysis.get("prompt_snippet", "")

        # Check exemptions
        is_exempt, exempt_reason = check_exemptions(rules_config, files_edited, original_prompt)
        if is_exempt:
            # Session is exempt from enforcement
            print('{}')
            return

        # Evaluate rules
        violations = evaluate_rules(rules_config, tracker, files_edited)

        if not violations:
            # No violations - all good
            print('{}')
            return

        # Check for blocking violations
        blocking = [v for v in violations if v.get("strictness") == "block"]

        if blocking:
            # Block completion
            message = format_violations_message(violations)
            print(message, file=sys.stderr)

            output = {
                "decision": "block",
                "reason": f"Agent enforcement failed: {len(blocking)} required agent(s) not invoked. Use the Task tool to invoke: {', '.join(set(v['required_agent'] for v in blocking))}"
            }
            print(json.dumps(output))
        else:
            # Warnings only - allow but show message
            message = format_violations_message(violations)
            print(message, file=sys.stderr)

            # Add as context but don't block
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "Stop",
                    "additionalContext": f"AGENT WARNINGS: {len(violations)} recommended agent(s) were not used. Consider using: {', '.join(set(v['required_agent'] for v in violations))}"
                }
            }
            print(json.dumps(output))

    except Exception as e:
        # Don't block on errors - log and continue
        print(f"agent-enforcement-check error: {e}", file=sys.stderr)
        print('{}')


if __name__ == "__main__":
    main()
