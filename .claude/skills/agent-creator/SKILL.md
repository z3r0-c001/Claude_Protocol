---
name: agent-creator
description: Safely create and register new agents with automatic system integration
triggers:
  - create agent
  - new agent
  - add agent
  - register agent
---

# Agent Creator Skill

This skill provides safe agent creation with automatic registry integration.

## Core Principle: MERGE, NEVER OVERWRITE

When modifying `agent-registry.json`:

```python
# CORRECT - Safe merge
existing = json.load(open('agent-registry.json'))
existing['agents'][new_agent_name] = new_agent_def
json.dump(existing, open('agent-registry.json', 'w'), indent=2)

# WRONG - Destructive overwrite
json.dump({'agents': {new_agent_name: new_agent_def}}, ...)
```

## Agent Definition Template

```json
{
  "name": "agent-name",
  "path": "category_group/agent-name.md",
  "description": "What this agent does",
  "category_group": "domain",
  "categories": ["relevant", "categories"],
  "model_tier": "standard",
  "supports_plan_mode": true,
  "triggers": {
    "exact_keywords": ["keyword1", "keyword2"],
    "phrase_patterns": [
      "(verb).*?(noun)",
      "(action).*?(target)"
    ],
    "file_patterns": ["**/relevant/**"],
    "negation_patterns": ["don't.*?keyword", "skip.*?keyword"]
  },
  "orchestration": {
    "typical_position": "middle",
    "often_follows": [],
    "often_precedes": [],
    "can_parallel_with": []
  }
}
```

## Category Groups

| Group | Purpose | Example Agents |
|-------|---------|----------------|
| core | Fundamental capabilities | architect, debugger, documenter |
| quality | Code quality enforcement | tester, reviewer, security-scanner |
| domain | Domain-specific expertise | frontend-designer, api-designer, data-modeler |
| workflow | Process coordination | orchestrator, brainstormer |

## Categories for Enforcement

These categories determine which enforcement rules an agent can satisfy:

| Category | Enforcement Rule | Description |
|----------|------------------|-------------|
| security | security_code | Auth, credentials, encryption code |
| testing | test_changes | Test file modifications |
| frontend | frontend_component | UI components, styling |
| data | database_changes | Schema, migrations, queries |
| design | architecture_change | Multi-file architectural changes |
| architecture | architecture_change | System design decisions |
| workflow | multi_step_task | Complex multi-step tasks |
| coordination | multi_step_task | Agent coordination |

## Auto-Generated Triggers

Based on agent description, generate appropriate triggers:

### Keyword Extraction
```
Description: "Expert in React component architecture and hooks"
Keywords: ["react", "component", "hooks", "architecture"]
```

### Pattern Generation
```
Description: "Handles authentication and authorization"
Patterns: [
  "(implement|add|fix).*?(auth|login|session)",
  "(secure|protect).*?(endpoint|route|api)"
]
```

### File Pattern Inference
```
Categories include "frontend" → ["**/*.tsx", "**/*.jsx", "**/components/**"]
Categories include "testing" → ["**/*.test.*", "**/*.spec.*", "**/tests/**"]
Categories include "data" → ["**/migrations/**", "**/*.sql", "**/models/**"]
```

## Agent File Template

```markdown
---
name: {name}
description: "{description}"
tools:
  - Read
  - Write
  - Grep
  - Glob
  {additional tools as needed}
model: claude-sonnet-4-5-20250929
model_tier: {standard|high}
---

# {Display Name} Agent

{Expanded description of agent's purpose and expertise}

## Capabilities

- {Capability 1}
- {Capability 2}
- {Capability 3}

## When to Use This Agent

Use this agent when:
- {Trigger condition 1}
- {Trigger condition 2}
- {Trigger condition 3}

## Approach

1. {Step 1 of how agent works}
2. {Step 2}
3. {Step 3}

## Output Format

{Description of expected output}

## Example Invocation

Task tool with:
- subagent_type: "{name}"
- prompt: "{example prompt}"
```

## Validation Checklist

Before completing agent creation:

- [ ] Agent file has valid YAML frontmatter
- [ ] Registry JSON is valid after merge
- [ ] No existing agent was overwritten
- [ ] Categories are valid for enforcement rules
- [ ] Triggers don't conflict with existing agents
- [ ] File path matches category_group

## Rollback Procedure

If something goes wrong:

```bash
# Restore registry from backup
cp .claude/agents/agent-registry.json.bak .claude/agents/agent-registry.json

# Remove created agent file
rm .claude/agents/{category_group}/{name}.md
```

## Integration Points

After creation, the new agent will automatically:

1. **Auto-Invocation**: Appear in suggestions when prompts match triggers
2. **Enforcement**: Satisfy rules requiring its categories
3. **Announcements**: Display with correct category banner when invoked
4. **Task Tool**: Be invocable via `subagent_type: "agent-name"`
