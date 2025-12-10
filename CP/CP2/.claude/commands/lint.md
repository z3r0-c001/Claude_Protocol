---
description: Run linters on the codebase. Usage: /lint [--fix] [path]
---

$ARGUMENTS

# LINT - Run Code Linters

Automatically detect and run appropriate linters for the project.

## Detection Strategy

```bash
# Detect linters based on project files
LINTERS=()

# JavaScript/TypeScript
if [ -f "package.json" ]; then
    grep -q '"eslint"' package.json && LINTERS+=("eslint")
    grep -q '"prettier"' package.json && LINTERS+=("prettier")
    grep -q '"biome"' package.json && LINTERS+=("biome")
fi

# Python
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || ls *.py 1>/dev/null 2>&1; then
    command -v ruff &>/dev/null && LINTERS+=("ruff")
    command -v black &>/dev/null && LINTERS+=("black")
    command -v flake8 &>/dev/null && LINTERS+=("flake8")
    command -v mypy &>/dev/null && LINTERS+=("mypy")
fi

# Rust
[ -f "Cargo.toml" ] && LINTERS+=("cargo clippy")

# Go
[ -f "go.mod" ] && LINTERS+=("golangci-lint")

# Shell
ls *.sh 1>/dev/null 2>&1 && command -v shellcheck &>/dev/null && LINTERS+=("shellcheck")
```

## Run Linters

### Check Mode (Default)
```bash
# ESLint
npx eslint . --ext .js,.jsx,.ts,.tsx

# Prettier (check)
npx prettier --check .

# Ruff
ruff check .

# Black (check)
black --check .

# Flake8
flake8 .

# MyPy
mypy .

# Clippy
cargo clippy -- -D warnings

# golangci-lint
golangci-lint run

# ShellCheck
shellcheck .claude/scripts/*.sh
```

### Fix Mode (--fix)
```bash
# ESLint
npx eslint . --ext .js,.jsx,.ts,.tsx --fix

# Prettier
npx prettier --write .

# Ruff
ruff check . --fix

# Black
black .

# Clippy
cargo clippy --fix

# golangci-lint
golangci-lint run --fix
```

## Output Format

```markdown
## Lint Results

### Linters Run
- ESLint: ✓ passed (0 errors, 2 warnings)
- Prettier: ✗ 5 files need formatting
- TypeScript: ✓ no type errors

### Issues Found

#### Errors (must fix)
| File | Line | Rule | Message |
|------|------|------|---------|
| src/app.ts | 42 | no-unused-vars | 'x' is defined but never used |

#### Warnings
| File | Line | Rule | Message |
|------|------|------|---------|
| src/utils.ts | 15 | prefer-const | Use 'const' instead of 'let' |

### Summary
- Errors: X
- Warnings: Y
- Files checked: Z

### Auto-fixable
Run `/lint --fix` to automatically fix Y issues.
```

## Integration

After linting:
1. If errors found → Block commit
2. If warnings only → Allow commit with note
3. If clean → Proceed

```bash
# Save lint status
bash .claude/scripts/save-memory.sh project-learnings "lint" "$(date): X errors, Y warnings"
```
