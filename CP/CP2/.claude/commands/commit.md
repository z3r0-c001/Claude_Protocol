---
description: Safely commit changes after running sanitization. Usage: /commit <message>
---

$ARGUMENTS

# SAFE COMMIT WORKFLOW

You are committing code changes. This ALWAYS runs sanitization first.

## Process

### Step 1: Run Sanitization

```bash
bash .claude/scripts/pre-commit-sanitize.sh
```

**If sanitization fails:**
- DO NOT COMMIT
- Fix all errors first
- Re-run sanitization

### Step 2: Review Changes

```bash
# Show what will be committed
git status
git diff --cached --stat
```

### Step 3: Commit

Only after sanitization passes:

```bash
git add -A
git commit -m "$ARGUMENTS"
```

### Step 4: Save to Memory

```bash
bash .claude/scripts/save-memory.sh project-learnings "commit" "Committed: $ARGUMENTS"
```

## Commit Message Format

Follow conventional commits:
- `feat: description` - New feature
- `fix: description` - Bug fix
- `docs: description` - Documentation
- `refactor: description` - Code refactoring
- `test: description` - Adding tests
- `chore: description` - Maintenance

## Output

```markdown
## Commit Result

### Sanitization
- [x] Secrets check: PASS
- [x] Unfinished code: PASS
- [x] Dangerous patterns: PASS
- [x] Sensitive files: PASS

### Committed
- Message: $ARGUMENTS
- Files: N files changed
- Hash: [commit hash]

### Next Steps
- Run `git push` to push changes
- Or continue working
```

## If Blocked

If sanitization blocks the commit, output:

```markdown
## ✗ Commit Blocked

### Issues Found
| File | Issue | Line |
|------|-------|------|
| ... | ... | ... |

### How to Fix
1. [Specific fix instructions]
2. [For each issue]

### After Fixing
Run `/commit $ARGUMENTS` again
```
