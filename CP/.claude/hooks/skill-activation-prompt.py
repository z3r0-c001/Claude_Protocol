#!/usr/bin/env python3
"""
Skill Auto-Activation Hook (UserPromptSubmit)

Analyzes user prompts and suggests relevant skills based on:
- Keyword matching
- Intent pattern matching
- Context detection for agent invocation
- Verification trigger detection

Configuration: .claude/skills/skill-rules.json
"""
import json
import sys
import re
import os
from pathlib import Path
from datetime import datetime

# Verification trigger keywords
VERIFY_TRIGGERS = [
    "best practice",
    "should i",
    "how should",
    "correct way",
    "recommended",
    "standard",
    "pattern",
    "convention",
    "proper way",
    "official",
    "according to",
    "the right way",
    "implementation",
    "architecture"
]

def get_project_dir():
    """Get project directory from environment or current directory"""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

def load_skill_rules():
    """Load skill activation rules from skill-rules.json"""
    project_dir = get_project_dir()
    rules_path = Path(project_dir) / ".claude" / "skills" / "skill-rules.json"

    if rules_path.exists():
        try:
            return json.loads(rules_path.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def check_prompt_triggers(prompt: str, rules: dict) -> list:
    """Check prompt against keyword and intent triggers"""
    matched = []
    prompt_lower = prompt.lower()

    for skill_name, config in rules.items():
        triggers = config.get("promptTriggers", {})

        # Check keywords
        keywords = triggers.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched.append({
                    "skill": skill_name,
                    "trigger": f"keyword: {kw}",
                    "priority": config.get("priority", "medium"),
                    "type": config.get("type", "domain")
                })
                break

        # Check intent patterns (if not already matched by keyword)
        if skill_name not in [m["skill"] for m in matched]:
            patterns = triggers.get("intentPatterns", [])
            for pattern in patterns:
                try:
                    if re.search(pattern, prompt_lower, re.IGNORECASE):
                        matched.append({
                            "skill": skill_name,
                            "trigger": f"pattern: {pattern[:30]}...",
                            "priority": config.get("priority", "medium"),
                            "type": config.get("type", "domain")
                        })
                        break
                except re.error:
                    continue

    return matched

def should_verify(prompt: str) -> bool:
    """Check if prompt contains verification triggers"""
    prompt_lower = prompt.lower()
    return any(trigger in prompt_lower for trigger in VERIFY_TRIGGERS)

def set_verify_flag(prompt: str):
    """Set flag file for Stop hook to pick up"""
    project_dir = get_project_dir()
    flags_dir = Path(project_dir) / ".claude" / "flags"
    flags_dir.mkdir(parents=True, exist_ok=True)

    flag_file = flags_dir / "verify-pending.json"
    flag_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt[:500]  # Truncate long prompts
    }
    flag_file.write_text(json.dumps(flag_data))

def get_agent_suggestions(matched_skills: list) -> list:
    """Get agent suggestions based on matched skills"""
    agent_map = {
        "security-scanner": ["security-scanner"],
        "performance-analyzer": ["performance-analyzer"],
        "test-coverage": ["test-coverage-enforcer", "tester"],
        "quality-audit": ["laziness-destroyer", "hallucination-checker"],
        "research-verifier": ["fact-checker", "research-analyzer"]
    }

    agents = []
    for skill in matched_skills:
        skill_name = skill["skill"]
        if skill_name in agent_map:
            for agent in agent_map[skill_name]:
                if agent not in agents:
                    agents.append(agent)

    return agents

def main():
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # Always output valid JSON even on error
        print(json.dumps({"decision": "continue"}))
        sys.exit(0)

    # Claude Code sends "user_prompt" for UserPromptSubmit hooks
    prompt = input_data.get("user_prompt", input_data.get("prompt", ""))

    if not prompt:
        print(json.dumps({"decision": "continue"}))
        sys.exit(0)

    # Check for skill triggers
    rules = load_skill_rules()
    matched_skills = check_prompt_triggers(prompt, rules)

    # Check for verification triggers
    needs_verification = should_verify(prompt)

    # Build output
    messages = []

    if matched_skills:
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        matched_skills.sort(key=lambda x: priority_order.get(x["priority"], 1))

        skills_list = ", ".join([m["skill"] for m in matched_skills])
        messages.append(f"SKILL ACTIVATION: Load skill(s): {skills_list}")

        # Get agent suggestions
        agents = get_agent_suggestions(matched_skills)
        if agents:
            agents_list = ", ".join(agents)
            messages.append(f"AGENT SUGGESTIONS: Consider invoking: {agents_list}")

    if needs_verification:
        set_verify_flag(prompt)
        messages.append("VERIFICATION QUEUED: Answer will be checked against docs")

    # Always output valid JSON using Claude Code's hookSpecificOutput format
    output = {"decision": "continue"}

    if messages:
        output["hookSpecificOutput"] = {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(messages)
        }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
