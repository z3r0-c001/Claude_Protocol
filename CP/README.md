# Claude Protocol

A quality-enforced, research-first protocol for Claude Code that prevents lazy code, hallucinations, and overclaiming.

## What This Does

- **Blocks lazy code** - No placeholders, TODOs, stubs, or incomplete implementations
- **Catches hallucinations** - Verifies packages, APIs, and file paths actually exist
- **Enforces honesty** - Prevents overclaiming capabilities or completion
- **Quality gates** - All code must pass completeness, syntax, and lint checks

## Quick Start

```bash
# 1. Copy to your project
cp -r .claude /path/to/your/project/
cp .mcp.json /path/to/your/project/
cp CLAUDE.md /path/to/your/project/

# 2. Install MCP memory server
cd /path/to/your/project/.claude/mcp/memory-server
npm install && npm run build

# 3. Start Claude Code
cd /path/to/your/project
claude
```

## Directory Structure

```
.claude/
├── agents/           # Specialized AI agents
│   ├── core/         # architect, performance-analyzer, research-analyzer
│   ├── quality/      # laziness-destroyer, hallucination-checker, etc.
│   └── domain/       # codebase-analyzer, protocol-generator
├── skills/           # Activatable skill modules
├── commands/         # Slash commands (/feature, /fix, /commit, etc.)
├── hooks/            # Quality enforcement hooks
├── configs/          # Permission configurations
├── mcp/              # MCP memory server
│   └── memory-server/
└── settings.json     # Hook configuration
```

## Key Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `pretool-laziness-check.py` | PreToolUse | Blocks TODOs, placeholders, stubs before write |
| `pretool-hallucination-check.py` | PreToolUse | Verifies packages exist on PyPI/npm |
| `dangerous-command-check.py` | PreToolUse | Blocks dangerous bash commands |
| `laziness-check.sh` | Stop | Final check for lazy patterns |
| `honesty-check.sh` | Stop | Catches overclaiming |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol for a project |
| `/feature <desc>` | Implement a feature with TDD |
| `/fix <issue>` | Fix a bug with test-first approach |
| `/commit <msg>` | Safe commit after sanitization |
| `/validate` | Run full validation suite |
| `/leftoff` | Save session state for continuation |
| `/resume` | Resume from saved session |
| `/remember <cat> <text>` | Save to persistent memory |
| `/recall <topic>` | Search memory |

## Requirements

- Node.js 18+
- Python 3.8+ (for PreToolUse hooks)
- Claude Code CLI
- bash, jq (for shell hooks)

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [HOOKS.md](HOOKS.md) - Hook development guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## Philosophy

1. **Research before acting** - Never claim capability without verification
2. **Stop when things fail** - Don't try random variations, research the cause
3. **Default to action** - Implement changes, don't just suggest them
4. **Zero tolerance** - All code must pass all quality checks
