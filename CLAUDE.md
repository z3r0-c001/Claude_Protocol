# Claude Protocol (Unified)

The definitive Claude Code infrastructure protocol combining quality enforcement, honesty guardrails, and autonomous operation.

## Project Status

| Property | Value |
|----------|-------|
| Version | 1.1.0 |
| Mode | Unified Protocol |
| Philosophy | Research-first + Quality-enforced |
| Validation | Zero-error tolerance |

## CRITICAL: Repository Structure

**THIS IS MANDATORY - NEVER VIOLATE THESE RULES:**

| Directory | Purpose | Git Status |
|-----------|---------|------------|
| `/` (root) | Working development directory | DO NOT PUSH TO GITHUB |
| `CP/` | Clean distribution for GitHub | ONLY THIS GOES TO GITHUB |
| `test/` | Testing directory | NEVER TOUCH |

**Workflow:**
1. Make all edits in root directory
2. Sync changes to `CP/` directory
3. Push ONLY `CP/` contents to GitHub

**Commands to sync and push:**
```bash
# Sync all protocol files to CP
cp .claude/hooks/*.sh CP/.claude/hooks/
cp .claude/hooks/*.py CP/.claude/hooks/
cp .claude/settings.json CP/.claude/settings.json
cp .claude/skills/skill-rules.json CP/.claude/skills/
cp -r .claude/agents/* CP/.claude/agents/
cp -r .claude/skills/* CP/.claude/skills/
cp CLAUDE.md CP/

# Commit and push from CP
cd CP && git add -A && git commit -m "message" && git push
```

**Note:** Hooks use `$CLAUDE_PROJECT_DIR` which Claude Code sets automatically to the project root.

## Critical Behaviors

### 1. Research Before Acting
- NEVER claim capability without verification
- NEVER say "yes I can do that" unless you've verified the approach works
- When uncertain, say: "I don't know. Let me research this first."

### 2. Stop When Things Fail
- If an approach fails, STOP
- Do not try random variations hoping one works
- Research the actual cause before attempting again
- Say: "That didn't work. Let me research why."

### 3. Default to Action
- Implement changes rather than suggesting them
- Do the work, don't describe the work
- Never use placeholders: `// ...`, `# TODO`, `pass`, `throw new NotImplementedError()`

### 4. Quality Enforcement
- All code must pass 100% of checks (zero errors tolerated)
- Completeness: No placeholders, TODOs, stubs
- Correctness: All imports/packages verified to exist
- Syntax: All files pass syntax validation
- Lint: All files pass linting rules

### 5. Thinking Triggers
- `think` - Standard reasoning
- `think hard` - More deliberate analysis
- `think harder` - Deep problem solving
- `ultrathink` - Maximum reasoning for architecture/design

### 6. Commit Message Standards
**NEVER use generic or placeholder commit messages.** Every commit must have:

1. **Specific summary** - What was changed, not "Updated files"
2. **Per-file details** - When multiple files, list what changed in each
3. **Context** - Why the change was made

**BAD Examples (NEVER use):**
- "Updated files"
- "Fixed bugs"
- "Various improvements"
- "WIP"
- "Changes"

**GOOD Examples:**
```
Add self-updating protocol system with manifest tracking

- protocol-manifest.json: Master manifest with 81 components, SHA-256 checksums
- .claude/agents/domain/protocol-updater.md: Agent for GitHub updates with interactive approval
- .claude/commands/proto-update.md: Command with --check, --analyze, --auto options
- .claude/hooks/context-loader.py: Added 24-hour cached startup update check
```

```
Fix authentication token refresh in session handler

- src/auth/session.ts: Added token expiry check before API calls (fixes #123)
- src/utils/token.ts: New refreshToken() function with retry logic
- tests/auth.test.ts: Added tests for token refresh edge cases
```

**For large changes:** Create a CHANGELOG-vX.X.X.md documenting all changes with file-by-file details.

## Quick Reference

| Task | Command |
|------|---------|
| Initialize protocol | `/init` |
| Generate tooling | `/bootstrap` |
| Validate all | `/validate` |
| Security scan | `/security` |
| Performance analysis | `/perf` |
| Test coverage | `/coverage` |

## Autonomous Behaviors

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
| Security-sensitive files | security-scanner | "Running security scan on {file}..." |
| Dependency files | dependency-auditor | "Auditing dependencies..." |
| Test files | test-coverage-enforcer | "Checking test coverage..." |
| Architecture components | architect | "Analyzing architectural implications..." |

## Hooks Configuration

| Hook Event | Scripts | Purpose |
|------------|---------|---------|
| UserPromptSubmit | skill-activation-prompt.py, query-analyzer.sh | Skill activation, query analysis |
| PreToolUse (Write) | pre-write-check.sh, completeness-check.sh | Block protected dirs, check completeness |
| PreToolUse (Bash) | dangerous-command-check.sh | Block dangerous commands |
| PostToolUse (Write) | file-edit-tracker.sh, post-write-validate.sh, context-detector.sh | Track edits, validate, suggest agents |
| PostToolUse (Task) | subagent-output-check.sh | Validate subagent output |
| PostToolUse (Web) | research-quality-check.sh | Validate research quality |
| Stop | laziness-check.sh, honesty-check.sh, stop-verify.sh | Quality gates |
| SubagentStop | research-validator.sh | Validate research from subagents |

## Agents

### Quality Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| laziness-destroyer | Block incomplete/placeholder code | Stop hook |
| hallucination-checker | Verify packages/APIs exist | Stop hook |
| honesty-evaluator | Check for overclaiming | Stop hook |

### Core Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| architect | System design and architecture | `/refactor`, manual |
| reviewer | Code review | `/pr`, manual |
| tester | Test generation | `/feature`, `/fix` |

### Domain Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| security-scanner | Security vulnerability detection | `/security`, auto |
| performance-analyzer | Performance issue detection | `/perf`, auto |
| codebase-analyzer | Project analysis | `/init` |
| protocol-generator | Generate protocol artifacts | `/bootstrap` |
| frontend-designer | UI/UX design, component architecture | Auto on frontend files |
| ui-researcher | Research UI patterns, libraries, best practices | Manual, via frontend-designer |

### Workflow Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| brainstormer | Socratic design refinement before implementation | "I want to build...", manual |

### Specialized Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| fact-checker | Verify factual claims | `/verify` |
| research-analyzer | Synthesize research | `/verify` |
| test-coverage-enforcer | Ensure test coverage | `/coverage` |
| dependency-auditor | Check dependency health | Auto on package files |
| build-error-resolver | Fix build errors | On build failure |

## Commands

### Initialization
| Command | Description |
|---------|-------------|
| `/init` | Initialize protocol, discover project |
| `/bootstrap` | Generate CLAUDE.md and project tooling |

### Development
| Command | Description |
|---------|-------------|
| `/feature <desc>` | Implement feature with TDD |
| `/fix <issue>` | Fix bug with test-first approach |
| `/refactor <target>` | Refactor with agent pipeline |
| `/test [pattern]` | Run project tests |
| `/lint [--fix]` | Run linters |

### Quality
| Command | Description |
|---------|-------------|
| `/validate` | Run full validation suite |
| `/verify` | Research verification (fact-check + honesty) |
| `/audit` | Quality audit (laziness + hallucination) |
| `/security` | Security scan (5 categories) |
| `/perf` | Performance analysis |
| `/coverage` | Test coverage analysis |

### Git & Docs
| Command | Description |
|---------|-------------|
| `/commit <msg>` | Safe commit after sanitization |
| `/pr [title]` | Create pull request |
| `/docs` | Generate documentation |
| `/dev-docs` | Create/update development context |

### Memory
| Command | Description |
|---------|-------------|
| `/remember <category> <what>` | Save to persistent memory |
| `/recall <topic>` | Search memory |

## Memory System

Memory persists across sessions via MCP server.

### MCP Memory Tools
| Tool | Purpose | Permission |
|------|---------|------------|
| `mcp__memory__memory_read` | Read entries | Silent |
| `mcp__memory__memory_write` | Save entries | Auto for learnings, ask for decisions |
| `mcp__memory__memory_search` | Fuzzy search | Silent |
| `mcp__memory__memory_list` | List entries | Silent |
| `mcp__memory__memory_delete` | Remove entries | Ask |
| `mcp__memory__memory_prune` | Clean old entries | Ask |

### Memory Categories
| Category | Auto-save | Purpose |
|----------|-----------|---------|
| `user-preferences` | Yes | Skill level, verbosity, goals |
| `project-learnings` | Yes | Technical discoveries |
| `corrections` | Yes | Mistakes to avoid |
| `patterns` | Yes | Detected code patterns |
| `decisions` | Ask | Architecture and design decisions |

## Skills

### Auto-Activated Skills
Skills suggest themselves based on prompts via `skill-rules.json`:

| Trigger Keywords | Skill | Type |
|------------------|-------|------|
| `implement`, `create`, `build`, `refactor` | dev-guidelines | Domain |
| `best practice`, `should I`, `correct way` | research-verifier | Workflow |
| `UI`, `component`, `button`, `form`, `layout` | frontend-design | Domain |
| `design system`, `tokens`, `theme`, `consistent` | design-system | Domain |
| `I want to build`, `help me plan`, `brainstorm` | brainstormer | Workflow |

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
| frontend-design | Complete frontend workflow: research, design, implement, validate |
| design-system | Establish and enforce design tokens, patterns, consistency |

## Quality Gates

All code must pass before completion:

1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified
3. **Syntax** - All files pass syntax validation
4. **Lint** - All files pass linting
5. **Tests** - All tests pass

**Pass threshold: 100% (zero errors tolerated)**

## Directory Structure

```
project-root/
├── CLAUDE.md                      # This file
├── .mcp.json                      # MCP server config
├── .claude/
│   ├── settings.json              # Hooks and permissions
│   ├── agents/
│   │   ├── core/                  # architect, reviewer, tester
│   │   ├── quality/               # laziness-destroyer, hallucination-checker
│   │   ├── domain/                # security-scanner, frontend-designer, ui-researcher
│   │   └── workflow/              # fact-checker, brainstormer
│   ├── skills/
│   │   ├── skill-rules.json       # Auto-activation config
│   │   ├── project-bootstrap/
│   │   ├── quality-control/
│   │   ├── workflow/
│   │   ├── memorizer/
│   │   ├── honesty-guardrail/
│   │   ├── dev-guidelines/
│   │   ├── frontend-design/       # Frontend workflow skill
│   │   └── design-system/         # Design tokens and consistency
│   ├── commands/                  # Slash commands
│   ├── hooks/                     # Hook scripts
│   ├── scripts/                   # Utility scripts
│   ├── memory/                    # Runtime state
│   └── mcp/
│       └── memory-server/         # MCP memory server
└── .claude-plugin/
    └── plugin.json
```

## Installation

```bash
# Copy protocol to target project
cp -r .claude /path/to/project/
cp -r .claude-plugin /path/to/project/
cp .mcp.json /path/to/project/
cp CLAUDE.md /path/to/project/

# Initialize
cd /path/to/project && claude
# Then run: /init
```
