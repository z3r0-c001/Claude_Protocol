# Claude Bootstrap Protocol

A self-invoking protocol that generates customized Claude Code tooling for any project.

## Important Notice

**This protocol is designed specifically for Claude and Claude Code.** It was developed in Claude Code, for Claude Code, leveraging Claude's unique capabilities including tool use, agent orchestration, and contextual understanding. While the concepts may inspire similar systems for other AI assistants, this implementation is tailored to Claude's architecture.

### Caveat Emptor

**No AI system is infallible.** Despite the extensive quality checks, validation hooks, and guardrails implemented in this protocol:

- Claude may still make mistakes, generate incorrect code, or misunderstand requirements
- Hooks and validation scripts may have bugs or edge cases not covered
- Generated tooling should always be reviewed by a human before use in production
- The protocol provides guardrails, not guarantees
- Always verify critical code, security-sensitive operations, and architectural decisions

**Use this protocol as a productivity enhancement, not a replacement for human judgment.**

## Overview

This protocol automatically:
1. **Discovers** project structure, languages, frameworks
2. **Generates** CLAUDE.md, skills, agents, hooks, commands
3. **Validates** all generated files with zero-error tolerance
4. **Enforces** quality via laziness-destroyer and hallucination-checker
5. **Remembers** user preferences, learnings, decisions across sessions
6. **Updates** itself from GitHub with interactive approval

## Quick Start

```bash
# Clone the repository
git clone https://github.com/z3r0-c001/Claude_Protocol.git

# Copy to your project
cp -r Claude_Protocol/.claude /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/
cp Claude_Protocol/.mcp.json /path/to/your/project/

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
- Auto-invokes appropriate agents based on file context

### Self-Updating Protocol
- Automatic update checks on startup (every 24 hours)
- Interactive approval for each change with diffs
- Smart analysis for optimization suggestions
- Preserves user customizations
- Run `/proto-update` to check for and apply updates

### Persistent Memory (Optional)
- MCP-based memory server for cross-session persistence
- Stores user preferences, learnings, corrections
- Auto-loads context at session start
- Protocol works without MCP - memory features are optional

### Quality Enforcement
- Zero-tolerance for placeholder code
- Package/API verification before suggesting
- Security scanning on sensitive code
- Code review automation
- Honesty guardrails to prevent overclaiming

### Smart Agent Invocation
- Context-aware agent suggestions
- Automatic security scanning on auth code
- Performance analysis on hot paths
- Frontend design assistance on UI files

### Skill Auto-Activation
- Skills suggest themselves based on prompt keywords
- Pattern matching for intent detection
- File-based triggers for domain-specific assistance

## Directory Structure

```
your-project/
├── CLAUDE.md                    # Project documentation
├── .mcp.json                    # MCP server configuration (optional)
├── .claude/
│   ├── settings.json            # Hooks and permissions
│   ├── protocol-manifest.local.json  # Local installation state
│   ├── configs/                 # Permission templates
│   │   ├── permissions-permissive.json
│   │   └── permissions-restricted.json
│   ├── agents/
│   │   ├── core/                # architect, reviewer, tester
│   │   ├── quality/             # laziness-destroyer, hallucination-checker
│   │   ├── domain/              # security-scanner, frontend-designer, protocol-updater
│   │   └── workflow/            # fact-checker, brainstormer
│   ├── commands/                # Slash commands (25+)
│   ├── hooks/                   # Hook scripts (18+)
│   ├── skills/                  # Skill definitions
│   │   ├── skill-rules.json     # Auto-activation config
│   │   ├── frontend-design/     # UI/UX workflow
│   │   ├── design-system/       # Design tokens
│   │   └── ...
│   ├── scripts/                 # Utility scripts
│   ├── mcp/
│   │   └── memory-server/       # MCP memory server (optional)
│   └── memory/                  # Persistent storage (runtime)
├── scripts/                     # Utility scripts
└── docs/                        # Documentation
```

## Commands

### Initialization
| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol for a project |
| `/bootstrap` | Generate CLAUDE.md and tooling |
| `/proto-status` | Show protocol state and health |

### Development
| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement a feature with TDD |
| `/fix <issue>` | Fix a bug with test-first approach |
| `/refactor <target>` | Refactor code with agent pipeline |
| `/test [pattern]` | Run tests |
| `/lint [--fix]` | Run linters |
| `/search <query>` | Search codebase |

### Quality
| Command | Description |
|---------|-------------|
| `/validate` | Run full validation suite |
| `/verify` | Research verification |
| `/audit` | Quality audit |

### Git & Docs
| Command | Description |
|---------|-------------|
| `/commit <msg>` | Commit with validation |
| `/pr [title]` | Create pull request |
| `/docs` | Generate documentation |

### Session Management
| Command | Description |
|---------|-------------|
| `/leftoff [summary]` | Save session state |
| `/resume [id]` | Resume saved session |
| `/remember <cat> <text>` | Save to memory |
| `/recall <query>` | Search memory |

### Protocol Management
| Command | Description |
|---------|-------------|
| `/proto-update` | Check for and apply updates |
| `/proto-update --check` | Dry run - show available updates |
| `/proto-update --analyze` | Full analysis with suggestions |

### Specialized
| Command | Description |
|---------|-------------|
| `/reposanitizer` | Sanitize for public release |
| `/manage-tools` | Manage protocol tooling |

See [Commands Reference](docs/COMMANDS.md) for complete list.

## Agents

### Quality Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| laziness-destroyer | Blocks placeholder code | Stop hook |
| hallucination-checker | Verifies packages/APIs exist | Stop hook |
| honesty-evaluator | Checks for overclaiming | Stop hook |
| security-scanner | Finds vulnerabilities | Auto on auth files |
| fact-checker | Verifies factual claims | `/verify` |
| reviewer | Code review | `/pr` |
| tester | Test generation | `/feature`, `/fix` |

### Core Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| architect | System design and planning | `/refactor`, manual |
| research-analyzer | Synthesizes research findings | `/verify` |
| performance-analyzer | Performance optimization | Auto on hot paths |
| codebase-analyzer | Project structure analysis | `/proto-init` |
| protocol-generator | Generates protocol artifacts | `/bootstrap` |

### Domain Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| frontend-designer | UI/UX design and components | Auto on frontend files |
| ui-researcher | Research UI patterns and libraries | Via frontend-designer |
| protocol-updater | Fetch and apply protocol updates | `/proto-update` |
| protocol-analyzer | Smart optimization suggestions | `/proto-update --analyze` |

### Workflow Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| brainstormer | Socratic design refinement | "I want to build..." |

See [Agents Reference](docs/AGENTS.md) for details.

## Skills

### Auto-Activated Skills
Skills suggest themselves based on prompts via `skill-rules.json`:

| Trigger Keywords | Skill | Type |
|------------------|-------|------|
| `implement`, `create`, `build`, `refactor` | dev-guidelines | Domain |
| `UI`, `component`, `button`, `form`, `layout` | frontend-design | Domain |
| `design system`, `tokens`, `theme` | design-system | Domain |
| `I want to build`, `help me plan`, `brainstorm` | brainstormer | Workflow |
| `best practice`, `should I`, `correct way` | research-verifier | Workflow |
| `security`, `vulnerability`, `authentication` | security-scanner | Domain |
| `performance`, `optimize`, `slow` | performance-analyzer | Domain |

### Core Skills
| Skill | Purpose |
|-------|---------|
| project-bootstrap | Discovery and initialization |
| quality-control | Validation suite |
| workflow | Feature/fix/commit workflows |
| memorizer | Memory management |
| honesty-guardrail | Always-active honesty protocol |
| dev-guidelines | Development patterns |

### Frontend Skills
| Skill | Purpose |
|-------|---------|
| frontend-design | Complete frontend workflow |
| design-system | Design tokens and consistency |

See [Skills Reference](docs/SKILLS.md) for details.

## Hooks

| Hook Event | Scripts | Purpose |
|------------|---------|---------|
| UserPromptSubmit | context-loader.py, skill-activation-prompt.py | Load context, skill activation |
| PreToolUse (Write) | pre-write-check.sh, completeness-check.sh | Block protected dirs, check completeness |
| PreToolUse (Bash) | dangerous-command-check.sh | Block dangerous commands |
| PostToolUse (Write) | file-edit-tracker.sh, post-write-validate.sh | Track edits, validate |
| PostToolUse (Task) | subagent-output-check.sh | Validate subagent output |
| PostToolUse (Web) | research-quality-check.sh | Validate research quality |
| Stop | laziness-check.sh, honesty-check.sh, stop-verify.sh | Quality gates |
| SubagentStop | research-validator.sh | Validate research |

**Note:** Hooks are shell scripts and Python scripts that may contain bugs. If you encounter unexpected behavior, please check the hook implementation and report issues.

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
5. **Honesty** - No overclaiming capabilities

**Pass threshold: 100% (zero errors tolerated)**

## Self-Updating Protocol

The protocol can update itself from GitHub:

```bash
# Check for updates (dry run)
/proto-update --check

# Interactive update with approval
/proto-update

# Full analysis with optimization suggestions
/proto-update --analyze

# Auto-accept non-breaking updates
/proto-update --auto
```

On startup, Claude will notify you if updates are available (checked every 24 hours).

## Requirements

- **Python**: Version 3.8 or higher (for hooks)
- **Claude Code**: Latest version
- **Node.js**: Version 18.0.0 or higher (only if using MCP memory server)

## Known Limitations

- Hooks may have edge cases not covered - review unexpected behavior
- Quality checks catch common issues but aren't exhaustive
- Memory server is optional and requires Node.js
- Self-updating requires network access to GitHub
- Agent suggestions are based on patterns and may not always be optimal

## Acknowledgments

The **brainstormer** agent's Socratic questioning approach was inspired by the excellent work in [obra/superpowers](https://github.com/obra/superpowers). We appreciate the creative methodology shared in that project which influenced our design refinement workflow.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the protocol guidelines
4. Run `/validate` to ensure quality
5. Submit a pull request

## License

This work is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/) with clarifications.

**Permitted:**
- Personal use, learning, research, hobby projects
- Internal use by companies and organizations
- Use by educational, government, and nonprofit organizations
- Modifications (must use same license)

**Prohibited:**
- Selling this work or derivatives
- Including in commercial products for sale
- Offering as a paid service (SaaS, consulting)

See the [LICENSE](LICENSE) file for full details including attribution requirements.

## Support

- **Issues**: [GitHub Issues](https://github.com/z3r0-c001/Claude_Protocol/issues)
- **Docs**: [Documentation](docs/)
