# Claude Bootstrap Protocol

**Version 1.2.14** | [Changelog](CHANGELOG.md) | [Releases](https://github.com/z3r0-c001/Claude_Protocol/releases)

A self-invoking protocol that generates customized Claude Code tooling for any project.

## Notice

**This protocol is designed for Claude Code.** While concepts may inspire similar systems, this implementation is tailored to Claude's architecture.

### Caveat Emptor

**No AI system is infallible.** Despite extensive quality checks and guardrails:

- Claude may still make mistakes or misunderstand requirements
- Hooks and validation scripts may have bugs or uncovered edge cases
- Generated tooling should be reviewed before production use
- Always verify critical code and security-sensitive operations

**Use as a productivity enhancement, not a replacement for human judgment.**

## Overview

This protocol automatically:
1. **Discovers** project structure, languages, frameworks
2. **Generates** CLAUDE.md, skills, agents, hooks, commands
3. **Validates** all generated files with zero-error tolerance
4. **Enforces** quality via laziness-destroyer and hallucination-checker
5. **Remembers** preferences, learnings, decisions across sessions
6. **Updates** itself from GitHub with interactive approval

## Quick Start

```bash
# Clone the repository
git clone https://github.com/z3r0-c001/Claude_Protocol.git
cd Claude_Protocol

# Run the installer
./install.sh

# Initialize with Claude Code
cd /path/to/your/project
claude
# Run: /proto-init
```

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
- Context-aware actions without constant prompting
- Permission requests for major decisions
- Failure detection with suggestions
- Auto-invokes agents based on file context

### Self-Updating Protocol
- Automatic update checks on startup (every 24 hours)
- Interactive approval with diffs for each change
- Smart analysis for optimization suggestions
- Preserves user customizations

### Persistent Memory (Optional)
- MCP-based server for cross-session persistence
- Stores preferences, learnings, corrections
- Auto-loads context at session start

### Quality Enforcement
- Zero-tolerance for placeholder code
- Package/API verification before suggesting
- Security scanning on sensitive code
- Honesty guardrails prevent overclaiming

### Agent Visual Banners
- Colored terminal banners when agents run
- Distinct colors per agent category:
  - Red: Security/quality agents
  - Blue: Architecture/core agents
  - Green: Domain/analysis agents
  - Yellow: Review/planning agents
  - Cyan: Exploration agents

## Directory Structure

```
your-project/
├── CLAUDE.md                    # Project instructions
├── .mcp.json                    # MCP server config (optional)
├── .claude/
│   ├── settings.json            # Hooks and permissions
│   ├── agents/
│   │   ├── core/                # architect, performance-analyzer, research-analyzer
│   │   ├── quality/             # laziness-destroyer, hallucination-checker, etc.
│   │   ├── domain/              # codebase-analyzer, frontend-designer, etc.
│   │   └── workflow/            # brainstormer, orchestrator
│   ├── commands/                # Slash commands (25)
│   ├── hooks/                   # Hook scripts (20)
│   ├── skills/                  # Skill definitions
│   │   ├── skill-rules.json
│   │   ├── frontend-design/
│   │   ├── design-system/
│   │   └── doc-processor/
│   └── mcp/
│       └── memory-server/       # MCP memory server (optional)
└── docs/                        # Documentation
```

## Commands

### Initialization
| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol for project |
| `/bootstrap` | Generate CLAUDE.md and tooling |
| `/proto-status` | Show protocol state and health |
| `/proto-help` | List protocol commands |

### Development
| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement feature with TDD |
| `/fix <issue>` | Fix bug with test-first approach |
| `/refactor <target>` | Refactor with agent pipeline |
| `/test [pattern]` | Run tests |
| `/lint [--fix]` | Run linters |
| `/search <query>` | Search codebase |

### Quality
| Command | Description |
|---------|-------------|
| `/validate` | Run full validation suite |
| `/orchestrate` | Coordinate multi-agent workflows |

### Git & Docs
| Command | Description |
|---------|-------------|
| `/commit <msg>` | Commit with validation |
| `/git` | Pre-push checklist |
| `/pr [title]` | Create pull request |
| `/docs` | Generate documentation |

### Session Management
| Command | Description |
|---------|-------------|
| `/leftoff [summary]` | Save session state |
| `/resume [id]` | Resume saved session |
| `/remember <cat> <text>` | Save to memory |
| `/recall <query>` | Search memory |

### Documentation Processing
| Command | Description |
|---------|-------------|
| `/doc-ingest <path>` | Process large docs into chunks |
| `/doc-search <query>` | Search processed documents |
| `/doc-list` | List processed documentation |

### Protocol Management
| Command | Description |
|---------|-------------|
| `/proto-update` | Check for and apply updates |
| `/proto-update --check` | Dry run - show available |
| `/proto-update --analyze` | Analysis with suggestions |
| `/manage-tools` | Manage protocol tooling |

## Agents

### Quality Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| laziness-destroyer | Blocks placeholder code | Stop hook |
| hallucination-checker | Verifies packages/APIs | Stop hook |
| honesty-evaluator | Checks for overclaiming | Stop hook |
| security-scanner | Finds vulnerabilities | Auto on auth files |
| fact-checker | Verifies factual claims | `/verify` |
| reviewer | Code review | `/pr` |
| tester | Test generation | `/feature`, `/fix` |
| test-coverage-enforcer | Ensures test coverage | `/coverage` |

### Core Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| architect | System design and planning | `/refactor`, manual |
| research-analyzer | Synthesizes research | `/verify` |
| performance-analyzer | Performance optimization | Auto on hot paths |

### Domain Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| codebase-analyzer | Project structure analysis | `/proto-init` |
| protocol-generator | Generates protocol artifacts | `/bootstrap` |
| protocol-updater | Fetches and applies updates | `/proto-update` |
| protocol-analyzer | Smart optimization suggestions | `/proto-update --analyze` |
| frontend-designer | UI/UX design and components | Auto on frontend files |
| ui-researcher | Research UI patterns | Via frontend-designer |
| dependency-auditor | Check dependency health | Auto on package files |
| document-processor | Process large documentation | `/doc-ingest` |

### Workflow Agents
| Agent | Purpose | Invocation |
|-------|---------|------------|
| brainstormer | Socratic design refinement | "I want to build..." |
| orchestrator | Multi-agent coordination | `/orchestrate` |

## Skills

### Auto-Activated Skills
| Trigger Keywords | Skill |
|------------------|-------|
| `implement`, `create`, `build`, `refactor` | dev-guidelines |
| `UI`, `component`, `button`, `form`, `layout` | frontend-design |
| `design system`, `tokens`, `theme` | design-system |
| `I want to build`, `help me plan`, `brainstorm` | brainstormer |
| `security`, `vulnerability`, `authentication` | security-scanner |
| `performance`, `optimize`, `slow` | performance-analyzer |

### Core Skills
| Skill | Purpose |
|-------|---------|
| project-bootstrap | Discovery and initialization |
| quality-control | Validation suite |
| workflow | Feature/fix/commit workflows |
| memorizer | Memory management |
| honesty-guardrail | Always-active honesty |
| dev-guidelines | Development patterns |

### Frontend Skills
| Skill | Purpose |
|-------|---------|
| frontend-design | Complete frontend workflow |
| design-system | Design tokens and consistency |
| doc-processor | Large document processing |

## Hooks

| Hook Event | Scripts | Purpose |
|------------|---------|---------|
| UserPromptSubmit | context-loader.py, skill-activation-prompt.py | Load context, skill activation |
| PreToolUse (Write) | pre-write-check.sh | Block protected directories |
| PreToolUse (Bash) | dangerous-command-check.py | Block dangerous commands |
| PreToolUse (Task) | agent-announce.py | Display colored agent banners |
| PostToolUse (Write) | file-edit-tracker.sh, post-write-validate.sh, context-detector.sh | Track edits, validate |
| PostToolUse (Task) | agent-handoff-validator.py | Validate agent output |
| PostToolUse (Web) | research-quality-check.sh | Validate research quality |
| Stop | laziness-check.sh, honesty-check.sh, stop-verify.sh | Quality gates |
| SubagentStop | research-validator.sh | Validate research |

## Memory Categories (Optional)

| Category | Auto-Save | Description |
|----------|-----------|-------------|
| user-preferences | Yes | Coding style, preferences |
| project-learnings | Yes | Codebase insights |
| corrections | Yes | Mistakes and fixes |
| patterns | Yes | Recurring solutions |
| decisions | No (ask) | Major choices |

## Quality Gates

All generated code must pass:
1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified
3. **Syntax** - All files pass syntax checks
4. **Security** - No vulnerabilities
5. **Honesty** - No overclaiming capabilities

**Pass threshold: 100% (zero errors tolerated)**

## Requirements

- **Python**: 3.8+ (for hooks)
- **Claude Code**: Latest version
- **Node.js**: 18.0.0+ (only for MCP memory server)

## Known Limitations

- Hooks may have edge cases not covered
- Quality checks catch common issues but aren't exhaustive
- Memory server requires Node.js
- Self-updating requires network access to GitHub
- Agent suggestions are pattern-based and may not always be optimal

## Acknowledgments

The **brainstormer** agent's Socratic questioning approach was inspired by [obra/superpowers](https://github.com/obra/superpowers).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following protocol guidelines
4. Run `/validate` to ensure quality
5. Submit a pull request

## License

[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Permitted:** Personal use, learning, research, hobby projects, internal company use, educational/nonprofit use, modifications (same license)

**Prohibited:** Selling this work, including in commercial products, offering as paid service

See [LICENSE](LICENSE) for full details.

## Support

- **Issues**: [GitHub Issues](https://github.com/z3r0-c001/Claude_Protocol/issues)
- **Docs**: [Documentation](docs/)
