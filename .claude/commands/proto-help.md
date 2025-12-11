---
description: List all Claude Bootstrap Protocol commands (use /help for built-in commands)
---

# Protocol Commands Help

List all available protocol commands.

## Core Commands

| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol for a project |
| `/bootstrap` | Generate CLAUDE.md and tooling |
| `/validate` | Run full validation suite |
| `/proto-status` | Show protocol state and health |

## Memory Commands

| Command | Description |
|---------|-------------|
| `/remember <cat> <text>` | Save to persistent memory |
| `/recall <query>` | Search memory |

## Development Commands

| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement a new feature |
| `/fix <issue>` | Fix a bug or issue |
| `/refactor` | Refactor code with quality gates |
| `/test [pattern]` | Run project tests |
| `/lint [--fix]` | Run code linters |

## Git Commands

| Command | Description |
|---------|-------------|
| `/commit <msg>` | Commit with validation |
| `/pr [title]` | Create a pull request |

## Categories for /remember

- `user-preferences` - Coding style, preferences
- `project-learnings` - Codebase insights
- `decisions` - Major choices (requires confirm)
- `corrections` - Mistakes and fixes
- `patterns` - Recurring solutions

## Getting Help

- `/proto-help` - This help (protocol commands)
- `/help` - Built-in Claude Code help
- Check CLAUDE.md for project-specific info

---

This is the protocol command reference.
