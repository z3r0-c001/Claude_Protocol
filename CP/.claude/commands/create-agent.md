---
description: Create a new agent with automatic registry integration
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion
---

# Create Agent Command

Create a new specialized agent that integrates with auto-invocation and enforcement systems.

## Arguments

$ARGUMENTS

## Process

### 1. Gather Agent Information

If not provided in arguments, ask for:
- **Name**: kebab-case identifier (e.g., `react-specialist`)
- **Description**: One-line purpose description
- **Category Group**: core | quality | domain | workflow
- **Categories**: List of categories for enforcement matching (e.g., frontend, security, testing)
- **Tools**: Which tools the agent needs (Read, Write, Edit, Grep, Glob, Bash, WebSearch, etc.)
- **Model Tier**: standard | high (high = opus for complex reasoning)

### 2. Check for Conflicts

Before creating, verify:
```bash
# Check if agent already exists
ls -la .claude/agents/*/$NAME.md 2>/dev/null
```

If exists, ask user whether to:
- Update existing agent
- Create with different name
- Cancel

### 3. Create Agent File

Create `.claude/agents/{category_group}/{name}.md`:

```markdown
---
name: {name}
description: "{description}"
tools:
  - {tools...}
model: claude-sonnet-4-5-20250929
model_tier: {tier}
---

# {Name} Agent

{Generated agent instructions based on purpose}

## Capabilities

{What this agent can do}

## When to Use

{Trigger conditions}

## Output Format

{Expected output structure}
```

### 4. Register in Agent Registry

**CRITICAL: Merge, don't overwrite!**

Read existing `.claude/agents/agent-registry.json`, then add new entry:

```json
"{name}": {
  "name": "{name}",
  "path": "{category_group}/{name}.md",
  "description": "{description}",
  "category_group": "{category_group}",
  "categories": [{categories}],
  "model_tier": "{tier}",
  "supports_plan_mode": true,
  "triggers": {
    "exact_keywords": [{keywords based on purpose}],
    "phrase_patterns": [{patterns based on purpose}],
    "file_patterns": [{if applicable}],
    "negation_patterns": []
  },
  "orchestration": {
    "typical_position": "middle",
    "often_follows": [],
    "often_precedes": [],
    "can_parallel_with": []
  }
}
```

### 5. Validation

After creation:
1. Verify agent file exists and has valid YAML frontmatter
2. Verify registry entry was added (not replaced)
3. Test that agent can be loaded

### 6. Output Summary

```
Agent Created Successfully
===========================
Name: {name}
Location: .claude/agents/{category_group}/{name}.md
Registry: Updated with {n} total agents

Categories: {categories}
Auto-invocation: Will trigger on keywords: {keywords}
Enforcement: Satisfies rules requiring: {categories}

Test with:
  Task tool -> subagent_type: "{name}"
```

## Safety Rules

1. **NEVER overwrite agent-registry.json entirely** - always read, merge, write
2. **NEVER modify existing agent entries** without explicit user approval
3. **ALWAYS backup before modifying registry**:
   ```bash
   cp .claude/agents/agent-registry.json .claude/agents/agent-registry.json.bak
   ```
4. **Preserve user customizations** in existing entries
5. **Validate JSON** before writing registry

## Example Usage

```
/create-agent react-specialist

# Interactive prompts:
Description: Expert in React patterns, hooks, and component architecture
Category Group: domain
Categories: frontend, design
Tools: Read, Write, Grep, Glob
Model Tier: standard
Keywords: react, hooks, useState, useEffect, component
```

## Trigger Keywords Generation

Based on agent purpose, auto-generate relevant:

| Purpose Contains | Suggested Keywords |
|------------------|-------------------|
| react | react, hooks, useState, useEffect, component, JSX |
| api | endpoint, REST, route, controller, handler |
| database | schema, migration, query, model, entity |
| security | auth, vulnerability, credential, encrypt |
| test | test, spec, coverage, mock, assert |
| performance | optimize, slow, cache, memory, benchmark |

## Category Mapping Reference

| Category | Satisfies Enforcement Rules |
|----------|----------------------------|
| security | security_code |
| testing | test_changes |
| frontend | frontend_component |
| data | database_changes |
| design, architecture | architecture_change |
| workflow, coordination | multi_step_task |
