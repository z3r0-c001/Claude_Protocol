---
name: protocol-generator
description: "Generate project-specific Claude artifacts including CLAUDE.md, agents, skills, and commands. Use after codebase analysis to create tailored protocol configuration."
---

# Protocol Generator Skill

This skill generates project-specific Claude Code artifacts based on codebase analysis.

## When to Use

- After `codebase-analyzer` completes
- When asked to "set up Claude" for a project
- When asked to create project-specific tooling
- When initializing protocol for a new repository

## Prerequisites

Requires `memories/codebase-analysis.json` from codebase-analyzer skill.

## Generation Process

### Step 1: Load Analysis

```bash
# Load and parse analysis
analysis=$(cat memories/codebase-analysis.json)
```

### Step 2: Generate CLAUDE.md

Based on analysis, generate tailored CLAUDE.md with:
- Project-specific commands
- Code style guidelines from detected patterns
- Testing instructions for detected framework
- Key files and their purposes

### Step 3: Generate Agents

Create project-specific agents based on:
- **Framework**: React specialist, Django expert, etc.
- **Complexity**: API specialist, database expert
- **Patterns**: Component generator, route creator

### Step 4: Generate Skills

Create project-specific skills for:
- Build/deploy procedures
- Common debugging scenarios
- Project-specific workflows

### Step 5: Generate Commands

Create slash commands for:
- `/component` - Generate components (React/Vue)
- `/route` - Create API routes
- `/test` - Generate tests
- `/deploy` - Deploy procedures

### Step 6: Update Hooks

Add project-specific hooks:
- Pre-commit type checking
- Build verification
- Test coverage enforcement

## Templates

### CLAUDE.md Template

```markdown
# {project.name}

## Quick Commands
{commands formatted}

## Structure
{structure description}

## Code Style
{patterns formatted}

## Key Files
{key_files formatted}

## Testing
{test framework info}
```

### Agent Template

```yaml
---
name: {framework}-specialist
description: "{description}"
tools: Read, Write, Grep, Glob
model: sonnet
---
{framework-specific instructions}
```

## Output

Creates files in:
- `CLAUDE.md` (project root)
- `.claude/agents/{name}.md`
- `.claude/skills/{name}/SKILL.md`
- `.claude/commands/{name}.md`
- `.claude/settings.json` (merged)

## Files

- `templates/claude-md.template`
- `templates/agent.template`
- `templates/skill.template`
- `templates/command.template`
