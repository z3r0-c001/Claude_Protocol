#!/usr/bin/env python3
"""
Skill Auto-Activation Hook (UserPromptSubmit)

Analyzes user prompts and suggests relevant skills.
"""
import json
import sys
import os
from pathlib import Path

def get_project_dir():
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

def load_skill_rules():
    project_dir = get_project_dir()
    rules_path = Path(project_dir) / ".claude" / "skills" / "skill-rules.json"
    if rules_path.exists():
        try:
            return json.loads(rules_path.read_text())
        except json.JSONDecodeError:
            return {"rules": []}
    return {"rules": []}

def check_prompt_triggers(prompt, rules):
    prompt_lower = prompt.lower()
    matched = []
    for rule in rules.get("rules", []):
        keywords = rule.get("keywords", [])
        for kw in keywords:
            if kw.lower() in prompt_lower:
                matched.append({
                    "skill": rule.get("skill", "unknown"),
                    "priority": rule.get("priority", "medium"),
                    "reason": f"Matched keyword: {kw}"
                })
                break
    return matched

def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # No input or invalid - just continue silently
        sys.exit(0)

    prompt = input_data.get("prompt", "")
    if not prompt:
        sys.exit(0)

    # Check for skill triggers
    rules = load_skill_rules()
    matched_skills = check_prompt_triggers(prompt, rules)

    if matched_skills:
        skills_list = ", ".join([m["skill"] for m in matched_skills])
        context = f"SKILL SUGGESTION: Consider loading: {skills_list}"
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit", 
                "additionalContext": context
            }
        }
        print(json.dumps(output))
    
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
