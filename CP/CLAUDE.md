# Claude Protocol

Quality-enforced, research-first protocol for Claude Code.

## Project Status

| Property | Value |
|----------|-------|
| Version | 1.0.0 |
| Mode | Quality Enforced |
| Philosophy | Research-first |
| Validation | Zero-error tolerance |

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

## Quick Reference

| Task | Command |
|------|---------|
| Initialize protocol | `/proto-init` |
| Implement feature | `/feature <description>` |
| Fix bug | `/fix <issue>` |
| Run tests | `/test [pattern]` |
| Commit safely | `/commit <message>` |
| Validate all | `/validate` |
| Save session | `/leftoff [summary]` |
| Resume session | `/resume` |
| Remember fact | `/remember <category> <text>` |
| Search memory | `/recall <topic>` |

## Autonomous Behaviors

### Memory Operations (via MCP)
- **Auto-save** (silent): corrections, project-learnings, patterns, user-preferences
- **Ask permission**: decisions (major architectural choices)

### On Hook Output
When hooks return issues:

| Severity | Action |
|----------|--------|
| `block` | Stop and fix before proceeding |
| `suggest` | Offer to fix: "I noticed {issue}. Would you like me to {action}?" |
| `auto_fix` | Fix immediately, inform user |

## Hooks Configuration

| Hook Event | Scripts | Purpose |
|------------|---------|---------|
| PreToolUse (Write) | `pretool-laziness-check.py`, `pretool-hallucination-check.py` | Block lazy/incomplete code, verify packages |
| PreToolUse (Bash) | `dangerous-command-check.py` | Block dangerous commands |
| PostToolUse (Write) | `post-write-validate.sh`, `context-detector.sh` | Validate syntax, suggest agents |
| Stop | `laziness-check.sh`, `honesty-check.sh` | Final quality gates |

## Quality Gates

All code must pass before completion:

1. **Completeness** - No placeholders, TODOs, stubs
2. **Correctness** - All imports/packages verified to exist
3. **Syntax** - All files pass syntax validation
4. **Lint** - All files pass linting rules
5. **Tests** - All tests pass

**Pass threshold: 100% (zero errors tolerated)**

## Thinking Triggers

- `think` - Standard reasoning
- `think hard` - More deliberate analysis
- `think harder` - Deep problem solving
- `ultrathink` - Maximum reasoning for architecture/design
