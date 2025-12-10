---
name: project-bootstrap
description: "INVOKE AUTOMATICALLY when protocol is detected. Generates customized Claude Code tooling for any project (new or existing). Triggers on: bootstrap, init, setup claude, configure claude, protocol init."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task
---

# Project Bootstrap Skill

This skill generates customized Claude Code tooling for any project.

## Trigger Conditions

Automatically invoke when:
1. Protocol file detected in repo
2. User runs `/bootstrap` or `/proto-init`
3. User asks to "set up Claude" or "configure Claude"
4. New project without `.claude/` directory

## Phase 1: Discovery

Read the protocol state from `.claude/memory/protocol-state.json` or run discovery:

```bash
bash .claude/scripts/protocol-init.sh
```

If state shows `discovery_complete: false`, run discovery first.

### Discovery Questions (if automated detection insufficient)

Ask the user:
1. What is this project? (brief description)
2. Primary language(s) if not detected?
3. Frameworks if not detected?
4. Build/test commands if not detected?
5. Any specific patterns or workflows to enforce?

## Phase 2: Generation

Generate ALL of the following:

### 2.1 CLAUDE.md (Project Root)

Create `CLAUDE.md` with:
- Project overview
- Tech stack
- Build/test/lint commands
- Code style rules
- Key directories and files
- Project-specific warnings
- Common tasks

### 2.2 Skills

Generate project-specific skills in `.claude/skills/`:

**For Python projects:**
- `python-dev/SKILL.md` - Python conventions, virtual envs, pytest

**For TypeScript/JavaScript projects:**
- `node-dev/SKILL.md` - npm/yarn, ESLint, testing

**For Go projects:**
- `go-dev/SKILL.md` - Go conventions, modules, testing

**For React projects:**
- `react-dev/SKILL.md` - Component patterns, hooks, testing

**For API projects:**
- `api-dev/SKILL.md` - REST/GraphQL patterns, validation

### 2.3 Commands

Generate slash commands in `.claude/commands/`:

- `fix.md` - Fix a bug or issue
- `feature.md` - Implement a new feature
- `test.md` - Write tests for code
- `review.md` - Review code changes
- `deploy.md` - Deployment tasks

### 2.4 Hooks

Ensure `.claude/settings.json` has all hooks:
- PreToolUse (dangerous command check, completeness check)
- PostToolUse (lint, format, validate)
- Stop (laziness-destroyer, hallucination-checker)
- Notification (logging)

### 2.5 Scripts

Create validation scripts in `.claude/scripts/`:
- `validate-all.sh` - Full validation suite
- `laziness-check.sh` - Check for placeholders
- `hallucination-check.sh` - Verify packages/APIs
- `pre-write-check.sh` - Pre-write validation
- `post-write-validate.sh` - Post-write validation
- `dangerous-command-check.sh` - Block dangerous bash

## Phase 3: Validation

Run ALL validation to ensure zero errors:

```bash
bash .claude/scripts/validate-all.sh
```

Must verify:
1. All files created successfully
2. All scripts are executable
3. JSON files are valid
4. Hooks fire correctly
5. Skills are loadable
6. Agents are loadable
7. No syntax errors anywhere

## Phase 4: Report

Output completion report:

```markdown
## Bootstrap Complete

### Generated Files
- [x] CLAUDE.md
- [x] .claude/settings.json
- [x] .claude/agents/ (N agents)
- [x] .claude/skills/ (N skills)
- [x] .claude/commands/ (N commands)
- [x] .claude/scripts/ (N scripts)

### Validation Results
- Structure: ✓
- JSON validity: ✓
- Script execution: ✓
- Hook tests: ✓

### Ready to Use
- Run `/fix <issue>` to fix bugs
- Run `/feature <feature>` to add features
- Run `/test <module>` to write tests
- Run `/review` to review changes
```

## Error Handling

If ANY error occurs:
1. Log to `.claude/memory/errors.log`
2. Report specific error
3. Suggest fix
4. DO NOT mark as complete until resolved

## Files

See `.claude/scripts/` for implementation scripts.
