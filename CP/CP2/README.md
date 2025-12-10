# Claude Bootstrap Protocol

A self-invoking protocol that generates customized Claude Code tooling for any project. Enforces quality, prevents laziness, catches hallucinations, and never forgets context.

## Features

- **🧠 Persistent Memory** - Never repeat yourself. Claude remembers preferences, decisions, learnings, and patterns across sessions.
- **🛡️ Quality Gates** - Every response passes through laziness detection, hallucination checking, and fact verification.
- **🔒 Pre-commit Sanitization** - Blocks secrets, unfinished code, and dangerous patterns before they reach git.
- **📝 Auto-documentation** - Generates and updates documentation to match your code.
- **🔄 Standardized Workflows** - Consistent patterns for features, fixes, tests, and PRs.

## Quick Start

```bash
# 1. Copy protocol to your project
cp -r claude-protocol/.claude /path/to/your/project/
cp -r claude-protocol/.claude-plugin /path/to/your/project/
cp claude-protocol/.mcp.json /path/to/your/project/

# 2. Add memory files to gitignore
echo ".claude/memory/*.json" >> .gitignore
echo "CLAUDE.local.md" >> .gitignore

# 3. Start Claude Code
cd /path/to/your/project
claude

# 4. Initialize the protocol (REQUIRED first step)
/proto-init
```

**Note**: You must run `/proto-init` to start the protocol. It walks through project discovery and generates your CLAUDE.md.

## Commands

### Setup & Status
| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol + auto-bootstrap |
| `/bootstrap` | Generate CLAUDE.md, skills, agents, hooks |
| `/proto-status` | Show protocol state and health |
| `/proto-help` | List protocol commands |

### Development
| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement a feature (full TDD workflow) |
| `/fix <issue>` | Fix a bug with test-first approach |
| `/refactor <target>` | Refactor code with full agent pipeline |
| `/test [pattern]` | Run project tests |
| `/lint [--fix]` | Run linters |
| `/search <query>` | Search codebase |

### Quality & Git
| Command | Description |
|---------|-------------|
| `/validate` | Run full validation suite |
| `/commit <msg>` | Sanitize and commit |
| `/pr [title]` | Create PR with all checks |

### Memory
| Command | Description |
|---------|-------------|
| `/remember <what>` | Save to persistent memory |
| `/recall <topic>` | Search memory |

### Documentation
| Command | Description |
|---------|-------------|
| `/docs` | Generate documentation |
| `/update-docs` | Sync docs with code |

## Architecture

```
.claude/
├── agents/           # 12 specialized subagents
│   ├── laziness-destroyer.md
│   ├── hallucination-checker.md
│   ├── fact-checker.md
│   ├── security-scanner.md
│   └── ...
├── commands/         # 14 slash commands
├── skills/           # 4 skill modules
│   ├── memorizer/
│   ├── workflow/
│   ├── quality-control/
│   └── project-bootstrap/
├── scripts/          # 13 automation scripts
├── memory/           # Persistent storage
├── config.json       # Customizable thresholds
└── settings.json     # Hooks and permissions
```

## Quality Enforcement

### Pre-Response Checks
1. **Laziness Destroyer** - Blocks placeholder code, TODOs, incomplete implementations
2. **Hallucination Checker** - Verifies packages, APIs, and file paths exist
3. **Honesty Evaluator** - Ensures appropriate uncertainty and attribution

### Pre-Commit Sanitization
- Secrets & credentials (API keys, passwords, tokens)
- Unfinished code (TODO, FIXME, NotImplementedError)
- Dangerous patterns (SQL injection, eval, XSS)
- Sensitive files (.env, .pem, private keys)
- Merge conflict markers

## Memory System

Claude automatically remembers:

| Category | Examples |
|----------|----------|
| `user-preferences` | Code style, communication preferences |
| `project-learnings` | Technical discoveries, gotchas |
| `decisions` | Architectural choices with rationale |
| `corrections` | Mistakes to avoid repeating |
| `patterns` | Recurring code patterns |

Memory persists across sessions. Use `/remember` to add, `/recall` to search.

## Configuration

Edit `.claude/config.json` to customize:

```json
{
  "thresholds": {
    "coverage": { "minimum_percent": 80 },
    "file_size": { "max_file_kb": 500 },
    "memory": { "max_entries_per_category": 100 }
  },
  "sanitization": {
    "block_on_secrets": true,
    "block_on_todos": true
  },
  "agents": {
    "model": "claude-opus-4-5-20251101"
  }
}
```

## CI/CD Integration

Copy `github-workflow.yml` to `.github/workflows/claude-checks.yml` for automated:
- Sanitization checks
- Protocol validation
- Laziness detection
- Tests and linting
- Security scanning

## Thinking Triggers

For complex tasks, use thinking triggers:

| Trigger | Use For |
|---------|---------|
| `think` | Basic planning |
| `think hard` | Detailed design |
| `think harder` | Complex problems |
| `ultrathink` | Architecture decisions |

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run `/validate` before committing
4. Submit a PR with `/pr`
