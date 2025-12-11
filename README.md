# Claude Bootstrap Protocol

A self-invoking protocol that generates customized Claude Code tooling for any project.

## Overview

This protocol automatically:
1. **Discovers** project structure, languages, frameworks
2. **Generates** CLAUDE.md, skills, agents, hooks, commands
3. **Validates** all generated files with zero-error tolerance
4. **Enforces** quality via laziness-destroyer and hallucination-checker
5. **Remembers** user preferences, learnings, decisions across sessions

## Quick Start

```bash
# Clone the repository
git clone https://github.com/z3r0-c001/Claude_Protocol.git

# Copy to your project
cp -r Claude_Protocol/.claude /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/

# Set permissions
cd /path/to/your/project
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py

# Initialize with Claude Code
claude
# Then run: /proto-init
```

The `/proto-init` command will guide you through setup, including optional MCP memory server configuration for persistent memory across sessions.

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICKSTART.md) | Get running in 5 minutes |
| [Installation](docs/INSTALLATION.md) | Complete installation guide |
| [Commands](docs/COMMANDS.md) | All slash commands |
| [Agents](docs/AGENTS.md) | Specialized agent reference |
| [Hooks](docs/HOOKS.md) | Hook scripts reference |
| [Skills](docs/SKILLS.md) | Skills reference |
| [MCP Server](docs/MCP.md) | Memory server documentation |
| [Configuration](docs/CONFIGURATION.md) | Configuration options |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |

## Features

### Autonomous Operation
- Claude automatically knows what to do based on context
- Asks permission for major decisions
- Notices failures and provides suggestions

### Persistent Memory (Optional)
- MCP-based memory server for cross-session persistence
- Stores user preferences, learnings, corrections
- Auto-loads context at session start
- Protocol works without MCP - memory features are optional

### Quality Enforcement
- Zero-tolerance for placeholder code
- Package/API verification
- Security scanning
- Code review automation

### Smart Agent Invocation
- Context-aware agent suggestions
- Automatic security scanning on auth code
- Performance analysis on hot paths

## Directory Structure

```
your-project/
├── CLAUDE.md                    # Project documentation
├── .mcp.json                    # MCP server configuration (optional)
├── .claude/
│   ├── settings.json            # Hooks and permissions
│   ├── configs/                 # Permission templates
│   │   ├── permissions-permissive.json
│   │   └── permissions-restricted.json
│   ├── agents/
│   │   ├── core/                # architect, research-analyzer, performance-analyzer
│   │   └── quality/             # laziness-destroyer, security-scanner, etc.
│   ├── commands/                # Slash commands (16 total)
│   ├── hooks/                   # Hook scripts (13 total)
│   ├── skills/                  # Skill definitions (6 total)
│   │   └── skill-rules.json     # Auto-activation config
│   ├── mcp/
│   │   └── memory-server/       # MCP memory server (optional)
│   └── memory/                  # Persistent storage (runtime, optional)
├── scripts/                     # Utility scripts
└── docs/                        # Documentation
```

## Commands

| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol for a project |
| `/bootstrap` | Generate CLAUDE.md and tooling |
| `/validate` | Run full validation suite |
| `/proto-status` | Show protocol state |
| `/feature <desc>` | Implement a feature |
| `/fix <issue>` | Fix a bug |
| `/refactor <target>` | Refactor code |
| `/test` | Run tests |
| `/lint [--fix]` | Run linters |
| `/search <query>` | Search codebase |
| `/commit <msg>` | Commit with validation |
| `/pr [title]` | Create pull request |
| `/leftoff [summary]` | Save session state |
| `/resume [id]` | Resume saved session |
| `/remember <cat> <text>` | Save to memory (requires MCP) |
| `/recall <query>` | Search memory (requires MCP) |
| `/docs` | Generate documentation |
| `/reposanitizer` | Sanitize for public release |

See [Commands Reference](docs/COMMANDS.md) for complete list.

## Agents

### Quality Agents
- **laziness-destroyer** - Blocks placeholder code
- **hallucination-checker** - Verifies packages/APIs
- **security-scanner** - Finds vulnerabilities
- **fact-checker** - Verifies claims
- **reviewer** - Code review
- **tester** - Test generation

### Core Agents
- **architect** - System design
- **research-analyzer** - Synthesizes findings
- **performance-analyzer** - Optimization

See [Agents Reference](docs/AGENTS.md) for details.

## Hooks

| Hook Event | Purpose |
|------------|---------|
| UserPromptSubmit | Skill activation, query analysis |
| PreToolUse | Block dangerous commands, protected paths |
| PostToolUse | Syntax validation, context detection |
| Stop | Laziness check, honesty check |
| SubagentStop | Research validation |

See [Hooks Reference](docs/HOOKS.md) for details.

## Memory Categories (Optional - requires MCP server)

| Category | Auto-Save | Description |
|----------|-----------|-------------|
| user-preferences | Yes | Coding style, preferences |
| project-learnings | Yes | Codebase insights |
| corrections | Yes | Mistakes and fixes |
| patterns | Yes | Recurring solutions |
| decisions | No (ask) | Major choices |

See [MCP Server Documentation](docs/MCP.md) for setup details.

## Quality Gates

All generated code must pass:
1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified
3. **Syntax** - All files pass syntax checks
4. **Security** - No vulnerabilities

**Pass threshold: 100% (zero errors tolerated)**

## Requirements

- **Python**: Version 3.8 or higher (for hooks)
- **Claude Code**: Latest version
- **Node.js**: Version 18.0.0 or higher (only if using MCP memory server)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the protocol guidelines
4. Run `/validate` to ensure quality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/z3r0-c001/Claude_Protocol/issues)
- **Docs**: [Documentation](docs/)
