# Agent Auto-Invocation Configuration

Configure the agent auto-invocation system thresholds, weights, and agent-specific settings.

## Overview

The auto-invocation system uses a 3-layer matching pipeline to determine which agents to invoke:
- **Layer 1 (25%)**: Keyword matching against agent triggers
- **Layer 2 (35%)**: Category classification based on task type
- **Layer 3 (40%)**: Phrase pattern matching (LLM intent heuristics)

Combined scores determine the action:
- **>= 85%**: Auto-invoke the agent
- **60-84%**: Prompt user for confirmation
- **< 60%**: Non-blocking suggestion

## Usage

```
/auto-agent-config [action] [options]
```

### Actions

| Action | Description |
|--------|-------------|
| `show` | Display current configuration (default) |
| `thresholds` | Adjust confidence thresholds |
| `weights` | Adjust layer weights |
| `agent` | Configure specific agent settings |
| `disable` | Disable auto-invocation for an agent |
| `enable` | Enable auto-invocation for an agent |
| `reset` | Reset to default configuration |

### Examples

```bash
# Show current configuration
/auto-agent-config show

# Lower auto-invoke threshold to 80%
/auto-agent-config thresholds --auto 80

# Increase keyword weight to 30%
/auto-agent-config weights --keyword 0.30 --category 0.35 --llm 0.35

# Disable auto-invoke for brainstormer
/auto-agent-config disable brainstormer

# Enable auto-invoke for architect
/auto-agent-config enable architect

# Reset to defaults
/auto-agent-config reset
```

## Instructions for Claude

When the user runs `/auto-agent-config`, follow these steps:

### 1. Parse Arguments

Parse the action and options from the user's command:
- `show` or no action: Display current configuration
- `thresholds --auto N --prompt N`: Update thresholds
- `weights --keyword N --category N --llm N`: Update weights (must sum to 1.0)
- `disable AGENT_NAME`: Add agent to never_auto_invoke list
- `enable AGENT_NAME`: Remove agent from never_auto_invoke list
- `reset`: Reset configuration to defaults

### 2. Load Current Configuration

Read the configuration file:
```
.claude/config/invoke-config.json
```

### 3. Display Current Configuration (show)

Format the current configuration as a readable summary:

```
Agent Auto-Invocation Configuration
===================================

Thresholds:
  Auto-invoke: >= 85%
  Prompt user: 60-84%
  Suggest only: < 60%

Layer Weights:
  Keyword matching:    25%
  Category match:      35%
  LLM intent:          40%

Visibility:
  Show banners: true
  Show confidence breakdown: true

Safety:
  Max auto-invokes per prompt: 1
  Disabled agents: [none]

Memory Learning:
  Enabled: true
  Max boost: +20%
  Max penalty: -25%
```

### 4. Update Thresholds

When updating thresholds:
1. Validate values are 0-100
2. Ensure auto_invoke > prompt_user
3. Update invoke-config.json
4. Confirm change to user

### 5. Update Weights

When updating weights:
1. Validate values are 0-1.0
2. Ensure sum equals 1.0 (warn if not)
3. Update invoke-config.json
4. Confirm change to user

### 6. Disable/Enable Agent

When disabling an agent:
1. Verify agent exists in registry
2. Add to `safety.never_auto_invoke` list
3. Confirm change to user

When enabling:
1. Remove from `safety.never_auto_invoke` list
2. Confirm change to user

### 7. Reset to Defaults

Reset invoke-config.json to default values:
- Thresholds: auto=85, prompt=60, suggest=0
- Weights: keyword=0.25, category=0.35, llm_intent=0.40
- All agents enabled

## Configuration File Location

```
.claude/config/invoke-config.json
```

## Related Files

| File | Purpose |
|------|---------|
| `.claude/config/invoke-config.json` | Main configuration |
| `.claude/config/invoke-config.schema.json` | Configuration schema |
| `.claude/agents/agent-registry.json` | Agent trigger definitions |
| `.claude/hooks/agent-auto-invoke.py` | Main hook implementation |
| `.claude/hooks/agent-visibility.py` | Terminal output formatting |

## Notes

- Changes take effect immediately on next prompt
- Memory learning adjustments persist across sessions
- Use `CLAUDE_NO_BANNERS=1` to suppress all visual output
- Use `NO_COLOR=1` to disable colored output
