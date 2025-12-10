---
name: quality-control
description: "Automated quality control for all generated code. Triggers on: verify, fact-check, validate, is this correct, double-check, ensure quality. Use PROACTIVELY on every code generation."
allowed-tools: Read, Bash, Grep, Glob, Task
---

# Quality Control Skill

Systematic verification of code quality, correctness, and completeness.

## Automatic Triggers

This skill is invoked automatically by:
1. `Stop` hook - Before every response
2. `PostToolUse` hook - After Write/Edit
3. Manual `/verify` command

## Quality Gates

### Gate 1: Completeness (Laziness Check)

No response passes if it contains:

```
// ...           # Placeholder comment
# ...            # Placeholder comment
// TODO          # Unimplemented TODO
# TODO           # Unimplemented TODO
pass             # Empty Python function
NotImplementedError  # Unimplemented
return null      # Stub return
return None      # Stub return
// implement     # Deferred implementation
```

Run check:
```bash
bash .claude/scripts/laziness-check.sh [file_or_directory]
```

### Gate 2: Correctness (Hallucination Check)

All technical claims verified:

**Packages:**
```bash
# npm
npm view <package> version 2>/dev/null

# pip
pip index versions <package> 2>/dev/null

# cargo
cargo search <crate> --limit 1 2>/dev/null
```

**Imports:**
```bash
# Python
python3 -c "import <module>" 2>&1

# Node
node -e "require('<module>')" 2>&1
```

Run check:
```bash
bash .claude/scripts/hallucination-check.sh [file]
```

### Gate 3: Syntax Validation

All code must pass syntax checks:

```bash
# Python
python3 -m py_compile <file>

# JavaScript/TypeScript
npx tsc --noEmit <file>  # or
node --check <file>

# JSON
python3 -m json.tool <file>

# Bash
bash -n <script>
```

### Gate 4: Lint Check

All code must pass linting:

```bash
# Python
ruff check <file> || python3 -m flake8 <file>

# JavaScript/TypeScript
npx eslint <file>

# Go
go vet <file>
```

### Gate 5: Test Execution

If tests exist, they must pass:

```bash
# Detect and run tests
[ -f "pytest.ini" ] && pytest
[ -f "package.json" ] && npm test
[ -f "go.mod" ] && go test ./...
```

## Scoring

Each gate produces a score:

| Gate | Weight | Criteria |
|------|--------|----------|
| Completeness | 30% | No placeholders |
| Correctness | 30% | No hallucinations |
| Syntax | 20% | No syntax errors |
| Lint | 10% | No lint errors |
| Tests | 10% | Tests pass |

**Pass threshold: 90%**

## Output Format

```json
{
  "overall_score": 95,
  "passed": true,
  "gates": {
    "completeness": {"score": 100, "issues": []},
    "correctness": {"score": 100, "issues": []},
    "syntax": {"score": 100, "issues": []},
    "lint": {"score": 80, "issues": ["warning: unused variable"]},
    "tests": {"score": 100, "issues": []}
  },
  "blocking_issues": [],
  "warnings": ["lint warning: unused variable"]
}
```

## Integration

This skill integrates with:
- `laziness-destroyer` agent
- `hallucination-checker` agent
- `reviewer` agent

## Files

- `.claude/scripts/laziness-check.sh`
- `.claude/scripts/hallucination-check.sh`
- `.claude/scripts/validate-all.sh`
