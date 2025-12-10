# Claude Protocol System

Automated Claude Code protocol with quality control hooks, codebase analysis, and intelligent artifact generation.

## Quick Start

```bash
# 1. Copy to your project
cp -r claude-protocol/.claude your-project/
cp claude-protocol/CLAUDE.md your-project/
cp -r claude-protocol/scripts your-project/
cp -r claude-protocol/memories your-project/

# 2. Initialize
cd your-project
./scripts/init-protocol.sh

# 3. In Claude Code, run:
/init
```

## What's Included

### Agents (`.claude/agents/`)

| Agent | Purpose |
|-------|---------|
| `laziness-destroyer` | Enforces action over suggestion |
| `hallucination-checker` | Verifies APIs, packages, paths exist |
| `fact-checker` | Verifies factual claims |
| `research-analyzer` | Synthesizes multi-source research |
| `honesty-evaluator` | Audits epistemic honesty |
| `security-scanner` | Checks for security vulnerabilities |
| `performance-analyzer` | Identifies performance issues |
| `test-coverage-enforcer` | Ensures adequate test coverage |
| `codebase-analyzer` | Analyzes project structure |
| `protocol-generator` | Generates project-specific artifacts |

### Skills (`.claude/skills/`)

| Skill | Purpose |
|-------|---------|
| `quality-control` | Fact verification, claim checking |
| `quality-audit` | Laziness + hallucination audit |
| `codebase-analyzer` | Project analysis |
| `protocol-generator` | Artifact generation |
| `security-scanner` | Security scanning |
| `performance-analyzer` | Performance analysis |
| `test-coverage` | Coverage analysis |

### Commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/init` | Initialize protocol for project |
| `/verify` | Verify claims and research |
| `/audit` | Run quality audit |
| `/security` | Run security scan |
| `/perf` | Run performance analysis |
| `/coverage` | Analyze test coverage |

### Hooks (`.claude/hooks/`)

**PreToolUse:**
- `safety-check.sh` - Blocks dangerous commands
- `completeness-check.sh` - Warns on placeholders

**PostToolUse:**
- `hallucination-code-check.sh` - Checks for hallucinated packages
- `subagent-output-check.sh` - Validates subagent output
- `research-quality-check.sh` - Evaluates source quality

**Stop:**
- `laziness-check.sh` - Catches lazy patterns
- `honesty-check.sh` - Checks epistemic honesty

**Other:**
- `query-analyzer.sh` - Analyzes query type
- `research-validator.sh` - Validates research completeness

## Configuration

### settings.json

The `.claude/settings.json` configures:
- Permissions (allow/deny rules)
- Hook bindings
- Tool configurations

### CLAUDE.md

Project-specific instructions including:
- Quick commands
- Code style guidelines
- Testing requirements
- Critical rules

### CLAUDE.local.md

Local overrides (gitignored):
- Personal preferences
- Local paths
- Development notes

## Memory System

The `memories/` directory stores:
- `codebase-analysis.json` - Project analysis
- `protocol-state.json` - Session state
- `compaction-log.json` - Context compaction history

## Scripts

| Script | Purpose |
|--------|---------|
| `init-protocol.sh` | Initialize for new project |
| `audit.sh` | Run quality audit |
| `verify-all.sh` | Comprehensive verification |
| `analyze-codebase.sh` | Analyze project |
| `session-init.sh` | Session start hook |
| `session-cleanup.sh` | Session end hook |
| `save-state.sh` | Pre-compaction hook |

## License

MIT
