---
name: codebase-analyzer
description: "Analyze project structure, detect languages/frameworks, identify patterns and conventions. Use when initializing protocol for a new project or when asked to understand a codebase."
---

# Codebase Analyzer Skill

This skill provides systematic codebase analysis for protocol initialization.

## When to Use

- When initializing protocol for a new project
- When asked to "understand" or "analyze" a codebase
- When onboarding to an existing project
- Before generating project-specific artifacts

## Analysis Steps

### Step 1: Project Type Detection

```bash
# Run detection script
./scripts/detect-project.sh
```

Detects:
- Package manager (npm, yarn, pnpm, pip, cargo, go mod)
- Primary language (by file count and package.json/pyproject.toml)
- Project type (web app, API, library, CLI, monorepo)

### Step 2: Framework Detection

```bash
# Check for framework indicators
./scripts/detect-framework.sh
```

Detects:
- Frontend: React, Vue, Angular, Svelte, Next.js, Nuxt
- Backend: Express, FastAPI, Django, Flask, Gin
- Testing: Jest, Pytest, Go test, Vitest
- ORM: Prisma, Drizzle, SQLAlchemy, GORM

### Step 3: Structure Mapping

```bash
# Map directory structure
./scripts/map-structure.sh
```

Maps:
- Source directories
- Test directories
- Configuration files
- Documentation
- Build outputs

### Step 4: Pattern Detection

```bash
# Detect coding patterns
./scripts/detect-patterns.sh
```

Detects:
- Naming conventions (files, functions, classes)
- Import style (absolute, relative, barrel)
- Export style (named, default)
- Component patterns (functional, class)

### Step 5: Key File Identification

```bash
# Find important files
./scripts/find-key-files.sh
```

Finds:
- Entry points
- Configuration files
- Documentation
- CI/CD configuration

## Output Format

Analysis outputs to `memories/codebase-analysis.json`:

```json
{
  "timestamp": "2025-01-01T00:00:00Z",
  "project": {...},
  "frameworks": {...},
  "structure": {...},
  "patterns": {...},
  "key_files": {...},
  "commands": {...}
}
```

## Integration

This skill is used by:
- `protocol-generator` agent for artifact generation
- `codebase-analyzer` agent for detailed analysis
- Protocol initialization script

## Files

- `detect-project.sh`: Project type detection
- `detect-framework.sh`: Framework detection
- `map-structure.sh`: Structure mapping
- `detect-patterns.sh`: Pattern detection
- `find-key-files.sh`: Key file identification
