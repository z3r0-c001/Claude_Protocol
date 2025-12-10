---
description: Validate all Claude Code hooks, skills, and infrastructure configuration
---

# Validate Infrastructure

Run comprehensive validation of all Claude Code infrastructure components.

## Instructions

Execute these validation checks in order:

### 1. Hook Validation

Test each hook outputs valid JSON. Run these commands and verify output:

**UserPromptSubmit hook:**
```bash
echo '{"prompt": "test prompt"}' | python3 .claude/hooks/skill-activation-prompt.py
```
Expected format: `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit"}}`

**PreToolUse hooks:**
```bash
echo '{"tool_input": {"command": "ls"}}' | bash .claude/hooks/safety-check.sh
echo '{"tool_input": {"content": "valid code"}}' | bash .claude/hooks/completeness-check.sh
```
Expected format: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}`

**PostToolUse hook:**
```bash
echo '{"tool_name": "Edit", "tool_input": {"file_path": "/test.js"}}' | bash .claude/hooks/file-edit-tracker.sh
```
Expected format: `{"hookSpecificOutput":{"hookEventName":"PostToolUse"}}`

**Stop hooks:**
```bash
echo '{}' | bash .claude/hooks/laziness-check.sh
echo '{}' | bash .claude/hooks/honesty-check.sh
echo '{}' | bash .claude/hooks/stop-verify.sh
```
Expected format: `{"decision": "approve"}`

### 2. JSON Format Requirements

Verify each hook output matches these required formats:

| Hook Type | Required Fields |
|-----------|-----------------|
| PreToolUse | `hookSpecificOutput.hookEventName` = "PreToolUse", `hookSpecificOutput.permissionDecision` = "allow"/"deny"/"ask" |
| PostToolUse | `hookSpecificOutput.hookEventName` = "PostToolUse" |
| UserPromptSubmit | `hookSpecificOutput.hookEventName` = "UserPromptSubmit" |
| Stop | `decision` = "approve"/"block" |

### 3. Edge Case Testing

Test hooks handle edge cases without crashing:

```bash
echo '' | python3 .claude/hooks/skill-activation-prompt.py
echo '{}' | bash .claude/hooks/safety-check.sh
echo 'not json' | python3 .claude/hooks/skill-activation-prompt.py
```

All must output valid JSON (never crash or output nothing).

### 4. Blocking Behavior Tests

Test hooks correctly block problematic content:

**Safety hook blocks dangerous commands:**
```bash
echo '{"tool_input": {"command": "sudo rm -rf /"}}' | bash .claude/hooks/safety-check.sh
```
Expected: `permissionDecision` = "deny"

**Laziness hook blocks lazy suggestions (without work context):**
```bash
echo '{"response": "You could try adding a function."}' | bash .claude/hooks/laziness-check.sh
```
Expected: `decision` = "block"

**Laziness hook allows summaries after work:**
```bash
echo '{"response": "I fixed the bug and updated the file."}' | bash .claude/hooks/laziness-check.sh
```
Expected: `decision` = "approve"

### 5. Skills Validation

```bash
ls -la .claude/skills/*/SKILL.md
cat .claude/skills/skill-rules.json | jq .
```

### 6. Settings Validation

```bash
cat .claude/settings.json | jq .
```

### 7. Generate Report

Create a validation report with this structure:

```
# Infrastructure Validation Report

## Hook Status

| Hook | Type | JSON Valid | Format OK | Blocking OK |
|------|------|------------|-----------|-------------|
| skill-activation-prompt.py | UserPromptSubmit | [status] | [status] | N/A |
| safety-check.sh | PreToolUse | [status] | [status] | [status] |
| completeness-check.sh | PreToolUse | [status] | [status] | [status] |
| file-edit-tracker.sh | PostToolUse | [status] | [status] | N/A |
| laziness-check.sh | Stop | [status] | [status] | [status] |
| honesty-check.sh | Stop | [status] | [status] | [status] |
| stop-verify.sh | Stop | [status] | [status] | N/A |

## Skills Status
[List skills and their status]

## Settings Status
[Verify settings.json is valid]

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
- Setting up infrastructure with /init-infrastructure
- Before committing hook changes
