# Configuration Guide

Complete guide to configuring Claude Bootstrap Protocol.

## Configuration Files

| File | Purpose |
|------|---------|
| `.claude/settings.json` | Hooks, permissions, tool configuration |
| `.mcp.json` | MCP server configuration |
| `.claude/skills/skill-rules.json` | Skill auto-activation rules |
| `.claude/configs/permissions-permissive.json` | Permissive permissions template |
| `.claude/configs/permissions-restricted.json` | Restricted permissions template |
| `CLAUDE.md` | Project-specific instructions |

## .claude/settings.json

Main configuration file for hooks and permissions.

### Structure

```json
{
  "permissions": {
    "allow": [...],
    "deny": [...]
  },
  "hooks": {
    "UserPromptSubmit": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "SubagentStop": [...]
  }
}
```

### Permissions

Control which tools Claude can use. Two modes are available:

**Permissive Mode** (default, recommended for development):
- All Read/Write/Edit operations allowed
- 70+ common Bash patterns pre-approved
- MCP tools allowed

**Restricted Mode** (for security-conscious users):
- Read-only operations allowed
- Most Bash commands require prompts
- Write/Edit operations require prompts

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Bash",
      "Grep",
      "Glob",
      "Task",
      "WebSearch",
      "WebFetch",
      "mcp__memory__*",
      "Bash(npm *)",
      "Bash(git *)",
      "Edit(*)",
      "Write(*)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(sudo *)",
      "Bash(chmod 777 *)",
      "Bash(curl * | sh)",
      "Bash(wget * | sh)"
    ]
  }
}
```

### Permissions Templates

Pre-configured templates are available in `.claude/configs/`:

**permissions-permissive.json** - Full development permissions:
- All standard tools allowed
- 70+ Bash command patterns
- MCP memory tools with wildcards

**permissions-restricted.json** - Locked-down permissions:
- Read, Grep, Glob, Task allowed
- Memory read operations only
- Most modifications require prompts

To switch modes, copy the desired template to settings.json:
```bash
# Switch to restricted mode
cp .claude/configs/permissions-restricted.json .claude/settings.json
# (merge with hooks section manually)
```

### Hook Configuration

Each hook has:
- `matcher` - Tool pattern to match (empty = all)
- `hooks` - Array of commands to run

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-write-check.sh\" \"$TOOL_INPUT\""
          }
        ]
      }
    ]
  }
}
```

### Available Matchers

| Matcher | Matches |
|---------|---------|
| `""` (empty) | All tools |
| `Write` | Write tool only |
| `Write\|Edit` | Write OR Edit |
| `Bash` | Bash tool only |
| `Task` | Subagent tasks |
| `WebSearch\|WebFetch` | Web tools |

### Environment Variables in Hooks

| Variable | Available In | Description |
|----------|--------------|-------------|
| `$CLAUDE_PROJECT_DIR` | All | Project root |
| `$TOOL_NAME` | PreToolUse, PostToolUse | Tool being used |
| `$TOOL_INPUT` | PreToolUse, PostToolUse | Tool input as JSON |
| `$TOOL_INPUT_FILE_PATH` | PreToolUse, PostToolUse | File path for Write/Edit |
| `$TOOL_OUTPUT` | PostToolUse | Tool output |
| `$PROMPT` | UserPromptSubmit | User's input |
| `$ASSISTANT_RESPONSE` | Stop | Response text |

---

## .mcp.json

MCP server configuration.

### Structure

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "KEY": "value"
      },
      "description": "Server description"
    }
  },
  "mcpConfig": {
    "autoConnect": true,
    "persistMemory": true
  }
}
```

### Memory Server Configuration

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": [".claude/mcp/memory-server/dist/index.js"],
      "env": {
        "MEMORY_PATH": ".claude/memory"
      },
      "description": "Persistent memory server"
    }
  }
}
```

### Adding Additional MCP Servers

```json
{
  "mcpServers": {
    "memory": { ... },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem", "."],
      "description": "File system access"
    },
    "custom-server": {
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {
        "CUSTOM_VAR": "value"
      }
    }
  }
}
```

---

## skill-rules.json

Configure automatic skill activation.

### Structure

```json
{
  "version": "1.0.0",
  "rules": [
    {
      "skill": "skill-name",
      "triggers": {
        "keywords": ["word1", "word2"],
        "patterns": ["regex1", "regex2"],
        "file_patterns": ["*.ts", "*.py"]
      },
      "priority": 1,
      "auto_invoke": true
    }
  ]
}
```

### Example Configuration

```json
{
  "version": "1.0.0",
  "rules": [
    {
      "skill": "quality-control",
      "triggers": {
        "keywords": ["verify", "validate", "check", "ensure"],
        "patterns": ["is this correct", "double-check"]
      },
      "priority": 1,
      "auto_invoke": true
    },
    {
      "skill": "workflow",
      "triggers": {
        "keywords": ["implement", "build", "create", "fix", "refactor"],
        "patterns": ["add feature", "fix bug"]
      },
      "priority": 2,
      "auto_invoke": true
    },
    {
      "skill": "memorizer",
      "triggers": {
        "keywords": ["remember", "save", "store", "note"],
        "patterns": ["don't forget", "keep track"]
      },
      "priority": 1,
      "auto_invoke": true
    }
  ]
}
```

### Trigger Types

| Type | Description | Example |
|------|-------------|---------|
| `keywords` | Exact word matches (case-insensitive) | `["implement", "create"]` |
| `patterns` | Regex patterns | `["add.*feature", "fix.*bug"]` |
| `file_patterns` | File glob patterns | `["*.ts", "src/**/*.py"]` |

---

## CLAUDE.md

Project-specific instructions for Claude.

### Recommended Sections

```markdown
# Project Name

## Overview
Brief project description.

## Tech Stack
- Language: TypeScript
- Framework: Next.js
- Database: PostgreSQL

## Build Commands
```bash
npm run build
npm run test
npm run lint
```

## Code Style
- Use functional components
- Prefer TypeScript strict mode
- Follow existing patterns

## Architecture
Describe key architectural decisions.

## Critical Behaviors
### Do
- Read code before modifying
- Run tests after changes

### Don't
- Use deprecated APIs
- Skip error handling
```

---

## Customization Examples

### Disable a Hook

Comment out or remove from settings.json:

```json
{
  "hooks": {
    "Stop": [
      // {
      //   "type": "command",
      //   "command": "bash ... laziness-check.sh ..."
      // }
    ]
  }
}
```

### Add Custom Protected Paths

Edit `.claude/hooks/pre-write-check.sh`:

```bash
PROTECTED_PATHS=(
  ".git/"
  "node_modules/"
  ".env"
  "package-lock.json"
  "yarn.lock"
  # Add your paths:
  "src/generated/"
  "vendor/"
)
```

### Change Memory Storage Path

Edit `.mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "env": {
        "MEMORY_PATH": "/custom/path/to/memory"
      }
    }
  }
}
```

### Add Custom Skill

1. Create skill directory:
```bash
mkdir -p .claude/skills/my-skill
```

2. Create SKILL.md:
```markdown
---
name: my-skill
description: My custom skill
allowed-tools:
  - Read
  - Write
---

# My Skill

## Purpose
Description of what this skill does.

## When to Use
- Condition 1
- Condition 2

## Process
1. Step 1
2. Step 2
```

3. Add to skill-rules.json:
```json
{
  "skill": "my-skill",
  "triggers": {
    "keywords": ["my-keyword"]
  },
  "auto_invoke": true
}
```

### Add Custom Agent

1. Create agent file:
```markdown
---
name: my-agent
description: "What this agent does"
tools:
  - Read
  - Grep
model: claude-opus-4-5-20251101
---

# My Agent

## Purpose
[Description]

## Process
[Steps]
```

2. Reference in commands or hooks as needed.

---

## Validation

### Validate All Configuration

```bash
# Check JSON syntax
python3 -c "import json; json.load(open('.claude/settings.json'))"
python3 -c "import json; json.load(open('.mcp.json'))"
python3 -c "import json; json.load(open('.claude/skills/skill-rules.json'))"

# Check hook scripts
bash -n .claude/hooks/*.sh
```

### Test Hooks Manually

```bash
# Test laziness check
bash .claude/hooks/laziness-check.sh . human

# Test dangerous command check
echo '{"command": "ls -la"}' | bash .claude/hooks/dangerous-command-check.sh

# Test context detector
bash .claude/hooks/context-detector.sh "src/auth/login.ts"
```

---

## Best Practices

1. **Keep settings.json valid JSON** - Use a JSON validator
2. **Test hooks before enabling** - Run manually first
3. **Use relative paths** - Use `$CLAUDE_PROJECT_DIR` variable
4. **Add error handling** - Hooks should fail gracefully with `|| true`
5. **Document changes** - Update CLAUDE.md when adding features
