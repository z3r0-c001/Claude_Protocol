# Claude Bootstrap Protocol

Self-invoking protocol that generates customized Claude Code tooling for any project.

## Project Status

| Property | Value |
|----------|-------|
| Mode | Protocol Development |
| User Level | Expert (be concise) |
| Validation | Full (all checks enabled) |
| Languages | Shell, Markdown, JSON |
| Components | 18 commands, 12 agents, 4 skills, 13 scripts |

## Quick Reference

| Task | Command |
|------|---------|
| Validate all | `bash .claude/scripts/validate-all.sh` |
| Laziness check | `bash .claude/scripts/laziness-check.sh .` |
| Hallucination check | `bash .claude/scripts/hallucination-check.sh .` |
| Load memory | `bash .claude/scripts/load-memory.sh` |
| Save memory | `bash .claude/scripts/save-memory.sh <category> <key> <value>` |
| Install git hooks | `bash .claude/scripts/install-git-hooks.sh` |

## Project Structure

```
CP2/
├── CLAUDE.md                    # This file - project context for Claude
├── README.md                    # User-facing documentation
├── QUICKSTART.md                # Quick setup guide
├── CLAUDE.local.md.template     # Template for user overrides
├── .mcp.json                    # MCP server configuration
├── github-workflow.yml          # CI/CD template
├── gitignore-template.txt       # Gitignore template
├── .claude/
│   ├── settings.json            # Hooks and permissions config
│   ├── commands/                # 18 slash commands
│   │   ├── proto-init.md        # Initialize protocol
│   │   ├── bootstrap.md         # Generate tooling
│   │   ├── feature.md           # Implement feature
│   │   ├── fix.md               # Fix bug
│   │   ├── refactor.md          # Refactor code
│   │   ├── test.md              # Run tests
│   │   ├── commit.md            # Safe commit
│   │   ├── pr.md                # Create PR
│   │   ├── docs.md              # Generate docs
│   │   ├── lint.md              # Run linters
│   │   ├── validate.md          # Validate protocol
│   │   ├── search.md            # Search codebase
│   │   ├── remember.md          # Save to memory
│   │   ├── recall.md            # Query memory
│   │   ├── proto-status.md      # Show status
│   │   ├── proto-help.md        # List commands
│   │   ├── update-docs.md       # Update stale docs
│   │   └── reposanitizer.md     # Sanitize before publish
│   ├── agents/                  # 12 specialized agents
│   │   ├── laziness-destroyer.md
│   │   ├── hallucination-checker.md
│   │   ├── architect.md
│   │   ├── reviewer.md
│   │   ├── tester.md
│   │   ├── security-scanner.md
│   │   ├── performance-analyzer.md
│   │   ├── fact-checker.md
│   │   ├── honesty-evaluator.md
│   │   ├── research-analyzer.md
│   │   ├── test-coverage-enforcer.md
│   │   └── dependency-auditor.md
│   ├── skills/                  # 4 skills
│   │   ├── project-bootstrap/   # Main bootstrapping
│   │   ├── memorizer/           # Memory management
│   │   ├── workflow/            # Dev workflows
│   │   └── quality-control/     # Validation gates
│   ├── scripts/                 # 14 shell scripts
│   │   ├── validate-all.sh
│   │   ├── laziness-check.sh
│   │   ├── hallucination-check.sh
│   │   ├── load-memory.sh
│   │   ├── save-memory.sh
│   │   ├── prune-memory.sh
│   │   ├── protocol-init.sh
│   │   ├── install-git-hooks.sh
│   │   ├── pre-commit-sanitize.sh
│   │   ├── pre-write-check.sh
│   │   ├── post-write-validate.sh
│   │   ├── dangerous-command-check.sh
│   │   ├── context-detector.sh
│   │   └── log-notification.sh
│   ├── hooks/                   # Hook implementations
│   │   ├── hook-logger.sh       # Shared logging helper
│   │   ├── pre-tool-template.sh # Template for PreToolUse hooks
│   │   └── stop-template.sh     # Template for Stop hooks
│   ├── watcher/                 # Session watcher daemon
│   │   ├── session-watcher.py   # Real-time transcript monitor
│   │   ├── spawn-watcher.sh     # Auto-spawn script
│   │   ├── ipc.sh               # Hook IPC helper
│   │   └── README.md            # Watcher documentation
│   ├── mcp/                     # MCP servers
│   │   └── memory-server/       # TypeScript memory MCP server
│   └── memory/                  # Runtime state (gitignored)
│       ├── protocol-state.json
│       ├── user-preferences.json
│       ├── project-learnings.json
│       ├── decisions.json
│       ├── corrections.json
│       └── patterns.json
└── .claude-plugin/
    └── plugin.json              # Plugin manifest
```

## Slash Commands

### Setup & Status
| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize protocol, discover project, gather preferences |
| `/bootstrap` | Generate CLAUDE.md and project-specific tooling |
| `/proto-status` | Show protocol state, memory status, health |
| `/proto-help` | List all protocol commands |
| `/validate` | Run full validation suite |

### Development Workflow
| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement feature with TDD workflow |
| `/fix <issue>` | Fix bug with test-first approach |
| `/refactor <target>` | Refactor with full agent pipeline |
| `/test [pattern]` | Run tests with optional pattern |
| `/lint [--fix]` | Run linters, optionally auto-fix |

### Git & Documentation
| Command | Description |
|---------|-------------|
| `/commit <msg>` | Safe commit after sanitization |
| `/pr [title]` | Create pull request with checks |
| `/docs [--api\|--readme\|--all]` | Generate documentation |
| `/update-docs` | Update stale documentation |
| `/reposanitizer` | Sanitize repo before publishing |

### Memory
| Command | Description |
|---------|-------------|
| `/remember <category> <what>` | Save to persistent memory |
| `/recall <topic>` | Search memory for information |
| `/search <query>` | Search codebase |

## Agents

| Agent | Purpose | Invocation |
|-------|---------|------------|
| `laziness-destroyer` | Blocks placeholder/incomplete code | Stop hook, manual |
| `hallucination-checker` | Verifies packages/APIs exist | Stop hook, manual |
| `architect` | System design and architecture | `/refactor`, manual |
| `reviewer` | Code review | `/pr`, manual |
| `tester` | Test generation | `/feature`, `/fix` |
| `security-scanner` | Security vulnerability detection | Pre-commit, manual |
| `performance-analyzer` | Performance issue detection | Manual |
| `fact-checker` | Verify factual claims | Manual |
| `honesty-evaluator` | Check for overclaiming | Manual |
| `research-analyzer` | Synthesize research findings | Manual |
| `test-coverage-enforcer` | Ensure test coverage | `/feature`, `/fix` |
| `dependency-auditor` | Check dependency health | Manual |

## Session Watcher & Unified Logging

All hooks write to a centralized log file (`.claude/logs/watcher.log`) for real-time visibility.

### Session Watcher

The watcher daemon monitors the transcript in real-time and validates responses before Stop hooks run:

```bash
# View live logs
tail -f .claude/logs/watcher.log

# Or attach to tmux viewer
tmux attach -t claude-watcher
```

### Creating New Hooks with Logging

All hooks should use the shared logger. Templates are provided:

**Bash hooks** - Source the logger:
```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/hook-logger.sh"

hook_log "INFO" "Checking something"
hook_log "OK" "Check passed"
hook_log "BLOCK" "Issue found"
```

**Stop hooks** - Query watcher for real-time validation:
```bash
WATCHER_RESPONSE=$(.claude/watcher/ipc.sh get_pending)
if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == true' >/dev/null; then
    # Block based on watcher findings
fi
```

See `.claude/hooks/pre-tool-template.sh` and `.claude/hooks/stop-template.sh` for complete examples.

### Log Lifecycle
- Cleared on session start (by `spawn-watcher.sh`)
- Cleared on session end (by cleanup hook)
- Ephemeral - not persisted across sessions

## Hooks Configuration

Current hooks in `.claude/settings.json`:

| Hook | Matcher | Script | Purpose |
|------|---------|--------|---------|
| PreToolUse | Write\|Edit\|MultiEdit | pre-write-check.sh | Block protected dirs, warn on sensitive files |
| PreToolUse | Bash | dangerous-command-check.sh | Block/warn on dangerous commands |
| PostToolUse | Write\|Edit\|MultiEdit | post-write-validate.sh | Syntax check, lint, suggest agents |
| PostToolUse | Write\|Edit\|MultiEdit | context-detector.sh | Detect context for agent invocation |
| Stop | * | laziness-check.sh | Block placeholder/incomplete code |

All hooks output **structured JSON** with severity levels for autonomous action.

## Quality Gates

All code must pass before completion:

1. **Completeness** - No placeholders, TODOs, stubs, `...`, `// implement`
2. **Correctness** - All imports/packages verified to exist
3. **Syntax** - All files pass syntax validation
4. **Lint** - All files pass linting rules
5. **Tests** - All tests pass

**Pass threshold: 100% (zero errors tolerated)**

## Critical Behaviors

### Thinking Triggers
- `think` - Standard reasoning
- `think hard` - More deliberate analysis
- `think harder` - Deep problem solving
- `ultrathink` - Maximum reasoning for architecture/design

### Core Rules
```
ALWAYS read files before editing - never guess at contents.
Do the work, don't describe the work.
Call multiple independent tools in parallel.
Never use placeholders - complete all work.
```

## Autonomous Behaviors

The protocol operates silently without requiring manual command invocation. Claude automatically:

### Memory Operations (via MCP)
- **Auto-save** (silent): corrections, project-learnings, patterns, user-preferences
- **Ask permission**: decisions (major architectural choices)
- Use MCP tools: `mcp__memory__memory_write`, `mcp__memory__memory_read`, `mcp__memory__memory_search`

### On Hook Output
When hooks return structured JSON with issues:

| Severity | Action |
|----------|--------|
| `auto_fix` | Fix immediately, inform user: "Fixed {issue}" |
| `suggest` | Offer to fix: "I noticed {issue}. Would you like me to {action}?" |
| `ask` | Always ask permission before any action |
| `block` | Explain why action was blocked, offer alternatives |

### Agent Invocations
Agents auto-invoke based on file context with **verbose announcements**:

| Context | Agent | Announcement |
|---------|-------|--------------|
| Security-sensitive files (`*auth*`, `*token*`) | security-scanner | "Running security scan on {file}..." |
| Dependency files (`package.json`, etc.) | dependency-auditor | "Auditing dependencies..." |
| Test files (`*test*`, `*spec*`) | test-coverage-enforcer | "Checking test coverage..." |
| Architecture components | architect | "Analyzing architectural implications..." |

### Auto-Fix with Audit
When auto-fixing issues:
1. Fix the issue
2. Inform user: "Fixed {issue} in {file}"
3. If user wants audit: Show diff before each change

### Session Start
1. MCP memory server provides context automatically
2. Never ask for information already in memory
3. Load protocol-state.json for project configuration

## Memory System

Memory persists across sessions via MCP server (`.claude/mcp/memory-server/`).

### MCP Memory Tools
| Tool | Purpose | Permission |
|------|---------|------------|
| `mcp__memory__memory_read` | Read entries from memory | Silent |
| `mcp__memory__memory_write` | Save entries to memory | Auto for learnings, ask for decisions |
| `mcp__memory__memory_search` | Fuzzy search across memory | Silent |
| `mcp__memory__memory_list` | List entries with summaries | Silent |
| `mcp__memory__memory_delete` | Remove entries | Ask confirmation |
| `mcp__memory__memory_prune` | Clean old entries | Ask confirmation |

### Memory Categories
| Category | Auto-save | Purpose |
|----------|-----------|---------|
| `user-preferences` | Yes | Skill level, verbosity, goals |
| `project-learnings` | Yes | Lessons learned about this project |
| `corrections` | Yes | Mistakes to avoid repeating |
| `patterns` | Yes | Detected code patterns |
| `decisions` | Ask | Architecture and design decisions |
| `protocol-state` | Read-only | Protocol initialization state |

### Legacy Shell Scripts (fallback)
```bash
bash .claude/scripts/load-memory.sh     # Human-readable output
bash .claude/scripts/save-memory.sh <category> <key> <value>
```

## Development Guidelines

When developing the protocol itself:

1. **Test changes** - Copy to a sample project and run `/proto-init`
2. **Scripts must be executable** - `chmod +x .claude/scripts/*.sh`
3. **Validate JSON** - `jq . file.json` before committing
4. **Follow patterns** - Match existing formatting in markdown/scripts
5. **Memory is user-specific** - `.claude/memory/` is gitignored

## Installation (for other projects)

```bash
# Copy protocol to target project
cp -r .claude /path/to/project/
cp -r .claude-plugin /path/to/project/
cp .mcp.json /path/to/project/

# Add to gitignore
echo ".claude/memory/*.json" >> /path/to/project/.gitignore
echo "CLAUDE.local.md" >> /path/to/project/.gitignore

# Initialize
cd /path/to/project && claude
# Then run: /proto-init
```
