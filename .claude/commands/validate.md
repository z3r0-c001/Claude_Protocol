---
description: Validate all Claude Code hooks, skills, and infrastructure configuration
---

# Validate Infrastructure

Run comprehensive validation of all Claude Code infrastructure components.

## Instructions

Execute these validation checks in order:

### 1. Hook Exit Code Protocol

Claude Code hooks use exit codes, not JSON output:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Continue (allow operation) |
| 2 | Block (with stderr message explaining why) |
| Other | Error (operation continues but logged) |

### 2. Hook Syntax Validation

Verify all hooks have valid syntax:

**Python hooks:**
```bash
python3 -m py_compile .claude/hooks/skill-activation-prompt.py
python3 -m py_compile .claude/hooks/context-loader.py
python3 -m py_compile .claude/hooks/dangerous-command-check.py
python3 -m py_compile .claude/hooks/pretool-laziness-check.py
python3 -m py_compile .claude/hooks/pretool-hallucination-check.py
```

**Bash hooks:**
```bash
bash -n .claude/hooks/pre-write-check.sh
bash -n .claude/hooks/file-edit-tracker.sh
bash -n .claude/hooks/context-detector.sh
```

All should exit 0 (no syntax errors).

### 3. Hook Behavior Tests

**Test UserPromptSubmit hooks output valid JSON:**
```bash
echo '{"user_prompt": "test"}' | python3 .claude/hooks/skill-activation-prompt.py
echo '{"user_prompt": "test"}' | python3 .claude/hooks/context-loader.py
```
Expected: Valid JSON with `{"decision": "continue"}` format.

**Test PreToolUse hooks allow safe operations:**
```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/tmp/test.txt"}}' | bash .claude/hooks/pre-write-check.sh
echo $?
```
Expected: Exit 0

**Test PreToolUse hooks block dangerous operations:**
```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "sudo rm -rf /"}}' | python3 .claude/hooks/dangerous-command-check.py
echo $?
```
Expected: Exit 2 with stderr message

**Test path protection:**
```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/etc/passwd"}}' | bash .claude/hooks/pre-write-check.sh
echo $?
```
Expected: Exit 2 (blocked)

### 4. Edge Case Testing

Test hooks handle edge cases gracefully:

```bash
echo '' | python3 .claude/hooks/skill-activation-prompt.py && echo "OK: empty input"
echo '{}' | python3 .claude/hooks/skill-activation-prompt.py && echo "OK: empty JSON"
echo 'not json' | python3 .claude/hooks/skill-activation-prompt.py && echo "OK: invalid JSON"
```

All should output valid JSON and exit 0 (not crash).

### 5. Skills Validation

```bash
ls -la .claude/skills/*/SKILL.md
cat .claude/skills/skill-rules.json | jq . > /dev/null && echo "skill-rules.json: valid"
```

### 6. Settings Validation

```bash
cat .claude/settings.json | jq . > /dev/null && echo "settings.json: valid"
```

### 7. Agent Validation

```bash
ls .claude/agents/core/*.md .claude/agents/quality/*.md .claude/agents/domain/*.md .claude/agents/workflow/*.md 2>/dev/null | wc -l
```

### 8. Generate Report

Create a validation report with this structure:

```
# Infrastructure Validation Report

## Hook Status

| Hook | Type | Syntax | Safe Allow | Dangerous Block |
|------|------|--------|------------|-----------------|
| skill-activation-prompt.py | UserPromptSubmit | [OK/FAIL] | N/A | N/A |
| context-loader.py | UserPromptSubmit | [OK/FAIL] | N/A | N/A |
| pre-write-check.sh | PreToolUse | [OK/FAIL] | [OK/FAIL] | [OK/FAIL] |
| dangerous-command-check.py | PreToolUse | [OK/FAIL] | [OK/FAIL] | [OK/FAIL] |
| pretool-laziness-check.py | PreToolUse | [OK/FAIL] | [OK/FAIL] | N/A |
| pretool-hallucination-check.py | PreToolUse | [OK/FAIL] | [OK/FAIL] | N/A |
| file-edit-tracker.sh | PostToolUse | [OK/FAIL] | N/A | N/A |
| context-detector.sh | PostToolUse | [OK/FAIL] | N/A | N/A |

## Config Status

| File | Valid JSON | Notes |
|------|------------|-------|
| settings.json | [OK/FAIL] | |
| skill-rules.json | [OK/FAIL] | |

## Summary

- Hooks: [X] valid / [Y] total
- Skills: [count] found
- Agents: [count] found
- Configs: [OK/FAIL]

## Issues Found
[List any issues]

## Recommendations
[List any recommendations]
```

## Usage

```
/validate
```

Run this after:
- Creating new hooks
- Modifying hook logic
- Setting up infrastructure with /proto-init
- Before committing hook changes
