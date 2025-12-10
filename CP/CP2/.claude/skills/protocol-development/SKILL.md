---
name: protocol-development
description: "Patterns for developing the Claude Bootstrap Protocol itself. Auto-invoked when modifying protocol files."
---

# Protocol Development Patterns

## Architecture

The Claude Bootstrap Protocol consists of:

1. **Slash Commands** (`.claude/commands/*.md`) - User-invokable workflows
2. **Agents** (`.claude/agents/*.md`) - Specialized subagents for quality/review
3. **Skills** (`.claude/skills/*/SKILL.md`) - Reusable behavior patterns
4. **Scripts** (`.claude/scripts/*.sh`) - Shell automation for hooks/validation
5. **Memory** (`.claude/memory/*.json`) - Persistent state across sessions
6. **Hooks** (`.claude/settings.json`) - Tool interception configuration

## File Patterns

### Slash Commands

Location: `.claude/commands/{name}.md`

Structure:
```markdown
# COMMAND_NAME - Description

Brief explanation of what this command does.

## Prerequisites
What must be true before running.

## Steps
1. First step
2. Second step
...

## Rules
- Must follow rule 1
- Must follow rule 2
```

### Agents

Location: `.claude/agents/{name}.md`

Structure:
```markdown
---
name: agent-name
description: "One-line description for Task tool matching"
---

# Agent Name

## Purpose
What this agent does.

## When to Invoke
Trigger conditions.

## Process
1. Step one
2. Step two

## Output Format
What the agent returns.
```

### Skills

Location: `.claude/skills/{name}/SKILL.md`

Structure:
```markdown
---
name: skill-name
description: "Description for Skill tool matching"
---

# Skill Name

## Overview
What this skill provides.

## Patterns
Reusable patterns for this domain.

## Examples
Concrete usage examples.
```

### Scripts

Location: `.claude/scripts/{name}.sh`

Requirements:
- Must be executable (`chmod +x`)
- Must have valid bash syntax
- Should use `set -e` for error handling
- Should provide colored output for UX

Pattern:
```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Implementation here
```

## Testing Changes

1. **Local validation**: `bash .claude/scripts/validate-all.sh`
2. **Copy to test project**: `cp -r .claude /tmp/test-project/`
3. **Run initialization**: In test project, run `/proto-init`
4. **Verify behavior**: Test the specific feature you changed

## Common Tasks

### Adding a New Slash Command

1. Create `.claude/commands/{name}.md`
2. Follow the command structure pattern above
3. Run validation to check syntax
4. Test by invoking `/{name}` in Claude Code

### Adding a New Agent

1. Create `.claude/agents/{name}.md`
2. Include frontmatter with `name` and `description`
3. The description is used by Task tool for matching
4. Test by invoking via Task tool

### Adding a New Script

1. Create `.claude/scripts/{name}.sh`
2. Make executable: `chmod +x .claude/scripts/{name}.sh`
3. Test locally: `bash .claude/scripts/{name}.sh`
4. Add to hooks in `settings.json` if needed

### Modifying Hooks

Edit `.claude/settings.json`:
- `PreToolUse` - Runs before tool execution
- `PostToolUse` - Runs after tool execution
- `Stop` - Runs when Claude stops responding

## Validation Checklist

Before considering work complete:

- [ ] `bash .claude/scripts/validate-all.sh` passes
- [ ] All JSON files are valid (`jq . file.json`)
- [ ] All scripts are executable
- [ ] New markdown files have correct structure
- [ ] Changes tested in a sample project
