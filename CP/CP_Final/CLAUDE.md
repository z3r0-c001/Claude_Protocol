# Claude Protocol System

This is an automated Claude Code protocol that provides quality control, codebase analysis, and intelligent artifact generation for any project.

## CRITICAL BEHAVIORS

**YOU MUST:**
- ALWAYS investigate code before answering questions about it
- ALWAYS implement changes rather than suggesting them
- ALWAYS verify your work compiles/runs before claiming completion
- ALWAYS use parallel tool calls for independent operations
- NEVER use placeholders like `// ...`, `# TODO`, `pass`, `...rest`
- NEVER speculate about code you haven't read
- NEVER claim completion without verification

## Quick Commands

```bash
# Initialize protocol for a new project
./scripts/init-protocol.sh [repo-url]

# Run full quality audit
./scripts/audit.sh

# Verify all claims and code
./scripts/verify-all.sh

# Analyze codebase
./scripts/analyze-codebase.sh
```

## Memory Protocol

**ASSUME INTERRUPTION** - Context may reset at any time.

1. Check `/memories` directory at session start
2. Record progress as you work
3. Save state before any complex operation
4. Write checkpoint files for multi-step tasks

## Available Agents

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

## Available Skills

| Skill | Trigger |
|-------|---------|
| `quality-control` | Fact verification, claim checking |
| `quality-audit` | Laziness + hallucination audit |
| `codebase-analyzer` | Project analysis, pattern detection |
| `protocol-generator` | Generate CLAUDE.md, agents, skills |
| `security-scanner` | Security audit, vulnerability scan |
| `performance-analyzer` | Performance profiling, bottleneck detection |
| `test-coverage` | Coverage analysis, test gap identification |

## Code Style

- Write concise, production-ready code
- No verbose variable names or redundant operations
- No unnecessary print/log statements unless debugging
- Prefer composition over inheritance
- Use early returns to reduce nesting

## Testing Requirements

Before claiming any task complete:
1. Code compiles without errors
2. All existing tests pass
3. New functionality has tests
4. Edge cases are covered

## Git Workflow

```bash
# Check status before any commit
git status && git diff --staged

# Commit format
git commit -m "type(scope): description"
# types: feat, fix, docs, refactor, test, chore
```

## Error Handling

When errors occur:
1. Read the full error message
2. Check the referenced file/line
3. Search for similar patterns in codebase
4. Fix root cause, not symptoms
