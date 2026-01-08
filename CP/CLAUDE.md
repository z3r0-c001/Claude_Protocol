# Claude Protocol

Quality-enforced protocol with automated hooks, specialized agents, and persistent memory.

## ⚡ MANDATORY: Session Startup

**BEFORE responding to the user's first message, run:**
```bash
python3 .claude/scripts/health-check.py
```

This is NOT optional. Report any warnings to the user, then proceed.

---

## 🤖 Agent Delegation

This project uses specialized agents. **USE THEM via the Task tool:**

| When To Delegate | Agent | Invocation |
|------------------|-------|------------|
| Multi-step tasks | `orchestrator` | Task tool with agent name |
| Architecture decisions | `architect` | Task tool |
| Writing tests | `tester` | Task tool |
| Code review | `reviewer` | Task tool |
| Security concerns | `security-scanner` | Task tool |
| Documentation | `documenter` | Task tool |

**Example Task invocation:**
```
Tool: Task
Agent: tester
Input: "Write unit tests for the auth module"
```

**When to delegate:**
- Task requires specialized expertise
- Task involves multiple steps
- User explicitly asks for agent
- Commands like `/validate`, `/pr`, `/test`, `/orchestrate`

**Agents are in:** `.claude/agents/` (31 agents across core, quality, domain, workflow)

---

## Agent Auto-Invocation System

Agents are automatically suggested or invoked based on prompt analysis using a 3-layer matching pipeline:

### Matching Layers
| Layer | Weight | Description |
|-------|--------|-------------|
| Keywords | 25% | Exact keyword matching against agent triggers |
| Category | 35% | Task category classification |
| Patterns | 40% | Phrase pattern matching for intent |

### Confidence Thresholds
| Threshold | Action |
|-----------|--------|
| >= 70% | **Auto-invoke** - Agent runs automatically with banner notification |
| 45-69% | **Prompt** - User asked to confirm before invocation |
| < 45% | **Suggest** - Non-blocking tip shown |

### Disambiguation
When multiple agents score within **15%** of each other (and below auto-invoke threshold), the system presents options instead of picking one:

```
AGENT CHOICE: Multiple agents match this request.
Options: [1] debugger (24%), [2] error-handler (24%).
Ask the user which agent they prefer...
```

Configure in `.claude/config/invoke-config.json`:
```json
"disambiguation": {
  "enabled": true,
  "score_gap_threshold": 15,
  "max_options": 3,
  "min_score_for_option": 20
}
```

### Configuration
Use `/auto-agent-config` to customize:
- Adjust thresholds (auto-invoke, prompt)
- Change layer weights
- Disable/enable specific agents
- View current configuration

### Visual Feedback
When agents are invoked, colored banners display:
- Agent name and execution mode
- Confidence score
- Layer breakdown (optional)

Suppress with `CLAUDE_NO_BANNERS=1` or `NO_COLOR=1`.

---

## Agent Usage Enforcement

The protocol enforces that required agents are used for specific task types:

### Enforcement Rules
| Rule | Required Agent | Strictness |
|------|----------------|------------|
| Security code (`**/auth/**`, `**/*auth*`) | security-scanner | block |
| Architecture changes (5+ files) | architect | block |
| Multi-step tasks (implement/build feature) | orchestrator | block |
| Test file changes (`**/*.test.*`) | tester | block |
| Frontend components (`**/*.tsx`) | frontend-designer | warn |
| Database changes (`**/migrations/**`) | data-modeler | block |

### Strictness Levels
| Level | Behavior |
|-------|----------|
| `block` | Stops completion until agent is invoked |
| `warn` | Shows warning but allows completion |
| `off` | No enforcement |

### How It Works
1. **UserPromptSubmit**: `agent-auto-invoke.py` detects patterns and sets required agents
2. **PreToolUse(Task)**: `agent-announce.py` tracks agent invocations
3. **Stop**: `agent-enforcement-check.py` validates requirements were met

### Configuration
Edit `.claude/config/enforcement-rules.json` to customize rules, thresholds, and exemptions.

---

## Project Status

| Property | Value |
|----------|-------|
| Version | 1.2.12 |
| Philosophy | Research-first, quality-enforced |
| Validation | Zero-error tolerance |

## Critical Behaviors

### Research Before Acting
- NEVER claim capability without verification
- When uncertain: "I don't know. Let me research this first."

### Stop When Things Fail
- If an approach fails, STOP and research the cause
- Do not try random variations

### Default to Action
- Implement changes rather than suggesting them
- Never use placeholders: `// ...`, `# TODO`, `pass`

### Quality Enforcement
- Zero errors tolerated
- No placeholders, TODOs, or stubs
- All imports/packages verified to exist

### Thinking Triggers
| Trigger | Use Case |
|---------|----------|
| `think` | Standard reasoning |
| `think hard` | Deliberate analysis |
| `think harder` | Deep problem solving |
| `ultrathink` | Architecture/design decisions |

## Quick Reference

| Task | Command |
|------|---------|
| Initialize protocol | `/proto-init` |
| Generate tooling | `/bootstrap` |
| Protocol status | `/proto-status` |
| Check for updates | `/proto-update` |
| Validate all | `/validate` |
| Run tests | `/test` |

## Hooks

### UserPromptSubmit
| Script | Purpose |
|--------|---------|
| agent-auto-invoke.py | Auto-invoke agents based on prompt analysis |
| context-loader.py | Load context at session start |
| skill-activation-prompt.py | Auto-activate skills based on prompt |

### PreToolUse
| Matcher | Script | Purpose |
|---------|--------|---------|
| Write | pre-write-check.sh | Block protected directories |
| Write | pretool-laziness-check.py | Pre-validate for placeholders |
| Write | pretool-hallucination-check.py | Pre-validate packages/APIs |
| Bash | dangerous-command-check.py | Block dangerous commands |
| Task | agent-plan-enforcer.py | Enforce plan mode for capable agents |
| Task | agent-announce.py | Display colored agent banners |

### PostToolUse
| Matcher | Script | Purpose |
|---------|--------|---------|
| Read | doc-size-detector.py | Detect large files, suggest chunking |
| Write | file-edit-tracker.sh | Track file edits |
| Write | post-write-validate.sh | Validate written files |
| Write | context-detector.sh | Suggest relevant agents |
| WebFetch/WebSearch | research-quality-check.sh | Validate research quality |

### Stop
| Script | Purpose |
|--------|---------|
| laziness-check.sh | Block incomplete code |
| honesty-check.sh | Check for overclaiming |
| stop-verify.sh | Final quality gate |
| agent-enforcement-check.py | Enforce required agent usage |

### SubagentStop
| Script | Purpose |
|--------|---------|
| agent-response-handler.py | Handle approval flows and next_agents |
| research-validator.sh | Validate research from subagents |
| agent-handoff-validator.py | Validate agent output quality |

## Agents

### Quality Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| laziness-destroyer | Block placeholder code | Stop hook |
| hallucination-checker | Verify packages/APIs exist | Stop hook |
| honesty-evaluator | Check for overclaiming | Stop hook |
| fact-checker | Verify factual claims | Manual |
| reviewer | Code review | `/pr` |
| tester | Test generation | `/feature`, `/fix` |
| security-scanner | Security vulnerability detection | Auto on auth files |
| test-coverage-enforcer | Ensure test coverage | `/test --coverage` |

### Core Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| architect | System design and architecture | `/refactor`, manual |
| research-analyzer | Synthesize research findings | SubagentStop hook |
| performance-analyzer | Performance issue detection | Auto on hot paths |

### Domain Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| codebase-analyzer | Project structure analysis | `/proto-init` |
| protocol-generator | Generate protocol artifacts | `/bootstrap` |
| protocol-updater | Fetch and apply updates | `/proto-update` |
| protocol-analyzer | Smart optimization suggestions | `/proto-update --analyze` |
| frontend-designer | UI/UX design and components | Auto on frontend files |
| ui-researcher | Research UI patterns | Via frontend-designer |
| dependency-auditor | Check dependency health | Auto on package files |
| document-processor | Process large documentation | `/doc-ingest` |

### Workflow Agents
| Agent | Purpose | Trigger |
|-------|---------|---------|
| brainstormer | Socratic design refinement | "I want to build..." |
| orchestrator | Coordinate multi-agent workflows | `/orchestrate` |

### Agent Visual Banners
When agents run, colored banners display their status:
- Red: Security/quality agents
- Blue: Architecture/core agents
- Green: Domain/analysis agents
- Yellow: Review/planning agents
- Cyan: Exploration agents

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
| `/test [pattern]` | Run project tests |
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
| `/doc-ingest <path>` | Process large docs into searchable chunks |
| `/doc-search <query>` | Search processed documents |
| `/doc-list` | List processed documentation |

### Protocol Management
| Command | Description |
|---------|-------------|
| `/proto-update` | Check for and apply updates |
| `/proto-update --check` | Dry run - show available updates |
| `/proto-update --analyze` | Full analysis with suggestions |
| `/auto-agent-config` | Configure agent auto-invocation |
| `/create-agent` | Create and register a new agent |
| `/manage-tools` | Manage protocol tooling |

## Memory System

Memory persists across sessions via MCP server (optional).

### MCP Tools
| Tool | Purpose |
|------|---------|
| `mcp__memory__memory_read` | Read entries |
| `mcp__memory__memory_write` | Save entries |
| `mcp__memory__memory_search` | Fuzzy search |
| `mcp__memory__memory_list` | List entries |
| `mcp__memory__memory_delete` | Remove entries |

### Memory Categories
| Category | Auto-save | Purpose |
|----------|-----------|---------|
| user-preferences | Yes | Skill level, verbosity, goals |
| project-learnings | Yes | Technical discoveries |
| corrections | Yes | Mistakes to avoid |
| patterns | Yes | Detected code patterns |
| decisions | Ask | Architecture decisions |

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
| `best practice`, `should I`, `correct way`, `recommended` | research-verifier |

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
| doc-processor | Large document processing |

## Quality Gates

All code must pass:
1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified
3. **Syntax** - All files pass syntax validation
4. **Lint** - All files pass linting
5. **Tests** - All tests pass

**Pass threshold: 100% (zero errors tolerated)**

## Directory Structure

```
project-root/
├── CLAUDE.md                    # This file
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
│   ├── skills/
│   │   ├── skill-rules.json     # Auto-activation config
│   │   ├── frontend-design/
│   │   ├── design-system/
│   │   └── doc-processor/
│   ├── scripts/                 # Utility scripts
│   └── mcp/
│       └── memory-server/       # MCP memory server (optional)
└── docs/                        # Documentation
```

## Commit Message Standards

Every commit must have specific summary and per-file details:

**Good:**
```
Add agent visual banners with distinct colors

- agent-announce.py: PreToolUse hook for Task tool, displays colored banners
- CLAUDE.md: Updated hooks documentation with new agent-announce
```

**Bad:** "Updated files", "Fixed bugs", "WIP"

## Installation

```bash
# Clone and install
git clone https://github.com/z3r0-c001/Claude_Protocol.git
./install.sh

# Initialize in your project
cd /path/to/your/project
claude
# Run: /proto-init
```
