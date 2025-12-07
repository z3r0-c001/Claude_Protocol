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
cp Claude_Protocol/.mcp.json /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/

# Build MCP server
cd /path/to/your/project/.claude/mcp/memory-server
npm install
npm run build

# Set permissions
cd /path/to/your/project
chmod +x .claude/hooks/*.sh

# Initialize with Claude Code
claude
# Then run: /proto-init
```

See [Quick Start Guide](docs/QUICKSTART.md) for detailed instructions.

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

### Persistent Memory
- MCP-based memory server
- Stores user preferences, learnings, corrections
- Auto-loads context at session start

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
├── .mcp.json                    # MCP server configuration
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
│   │   └── memory-server/       # MCP memory server
│   └── memory/                  # Persistent storage (runtime)
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
| `/commit <msg>` | Commit with validation |
| `/remember <cat> <text>` | Save to memory |
| `/recall <query>` | Search memory |
| `/update-docs` | Sync docs with code |
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

## Memory Categories

| Category | Auto-Save | Description |
|----------|-----------|-------------|
| user-preferences | Yes | Coding style, preferences |
| project-learnings | Yes | Codebase insights |
| corrections | Yes | Mistakes and fixes |
| patterns | Yes | Recurring solutions |
| decisions | No (ask) | Major choices |

See [MCP Server Documentation](docs/MCP.md) for details.

## Quality Gates

All generated code must pass:
1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified
3. **Syntax** - All files pass syntax checks
4. **Security** - No vulnerabilities

**Pass threshold: 100% (zero errors tolerated)**

## Requirements

- **Node.js**: Version 20.0.0 or higher
- **npm**: Version 9.0.0 or higher
- **Claude Code**: Latest version

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
