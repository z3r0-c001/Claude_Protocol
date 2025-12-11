---
name: project-bootstrap
description: >
  INVOKE AUTOMATICALLY when protocol is detected.
  Generates customized Claude Code tooling for any project (new or existing).
  Triggers on: bootstrap, init, setup claude, configure claude, protocol init.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Project Bootstrap Skill

## Overview

This skill generates customized Claude Code tooling for any project. It analyzes the codebase and creates appropriate agents, commands, hooks, and configuration.

## When to Use

- New project setup
- Adding Claude support to existing project
- Regenerating configuration after project changes
- `/proto-init` or `/bootstrap` commands

## Bootstrap Process

### Phase 1: Discovery

Analyze the project to understand:

```
1. PROJECT TYPE
   - Single language or monorepo
   - Frontend, backend, fullstack
   - Library, application, CLI

2. LANGUAGES
   - Primary language(s)
   - Configuration files present
   - Build tools used

3. FRAMEWORKS
   - Frontend: React, Vue, Angular, etc.
   - Backend: Express, FastAPI, etc.
   - Testing: Jest, pytest, etc.

4. STRUCTURE
   - Source directory layout
   - Test location
   - Build output
```

### Phase 2: Generation

Create project-specific tooling:

```
1. CLAUDE.md
   - Project context
   - Build/test commands
   - Key patterns
   - Important files

2. COMMANDS
   - /build, /test, /lint
   - Project-specific commands
   - Workflow shortcuts

3. AGENTS (if needed)
   - Project-specific agents
   - Framework-specific helpers

4. HOOKS
   - Language-specific validation
   - Project-specific checks
```

### Phase 3: Validation

Verify generated configuration:

```
1. SYNTAX CHECK
   - All generated files valid
   - JSON/YAML parseable

2. COMMAND TEST
   - Build command works
   - Test command works
   - Lint command works

3. HOOK TEST
   - Hooks execute correctly
   - No errors on sample files
```

## Detection Rules

### Package Managers
| File | Language | Build |
|------|----------|-------|
| package.json | JavaScript/TypeScript | npm/yarn/pnpm |
| requirements.txt | Python | pip |
| Cargo.toml | Rust | cargo |
| go.mod | Go | go build |
| pom.xml | Java | maven |
| build.gradle | Kotlin/Java | gradle |

### Frameworks
| Indicator | Framework |
|-----------|-----------|
| next.config.js | Next.js |
| vite.config.* | Vite |
| angular.json | Angular |
| vue.config.js | Vue |
| fastapi | FastAPI |
| express | Express |
| django | Django |

### Testing
| File/Dir | Framework |
|----------|-----------|
| jest.config.* | Jest |
| vitest.config.* | Vitest |
| pytest.ini | pytest |
| __tests__ | Jest convention |
| test_*.py | pytest convention |

## Generated CLAUDE.md Template

```markdown
# [Project Name]

[Auto-generated description]

## Build Commands
- Build: [detected command]
- Test: [detected command]
- Lint: [detected command]

## Key Files
- [Entry point]
- [Config files]
- [Test setup]

## Patterns
[Detected patterns]

## Important Notes
[Any special considerations]
```

## Post-Bootstrap

After bootstrap completes:

1. Review generated CLAUDE.md
2. Verify commands work
3. Add project-specific sections
4. Run `/validate` to ensure quality

## Regeneration

To regenerate configuration:

```
/bootstrap --force
```

This will:
1. Backup existing configuration
2. Re-run discovery
3. Generate fresh configuration
4. Preserve custom sections (if marked)

## Integration

This skill works with:
- `/proto-init` command
- `/bootstrap` command
- Protocol initialization hooks
