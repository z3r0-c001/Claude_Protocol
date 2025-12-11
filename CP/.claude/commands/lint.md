---
description: Run linters on the codebase. Usage: /lint [--fix] [path]
---

# Lint Command

Run code linters to check for style and quality issues.

## Usage

- `/lint` - Run linter on entire project
- `/lint src/` - Run linter on specific path
- `/lint --fix` - Auto-fix issues where possible

## Process

1. **Detect Linter**
   - Check for eslint, prettier, flake8, clippy, etc.
   - Determine the lint command from package.json or equivalent

2. **Build Lint Command**
   - Base: detected lint command
   - Add path if specified
   - Add --fix flag if requested

3. **Run Linter**
   - Execute the lint command
   - Capture output

4. **Report Results**
   - Issue count by severity
   - File-by-file breakdown
   - Auto-fixed issues (if --fix used)

## Common Linters

| Language | Linter | Command |
|----------|--------|---------|
| JavaScript/TypeScript | ESLint | npm run lint |
| Python | flake8/ruff | flake8 . |
| Rust | Clippy | cargo clippy |
| Go | golint | golint ./... |

---

Detect the linter and run the appropriate command.
