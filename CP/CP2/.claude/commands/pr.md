---
description: Create a pull request with all checks. Usage: /pr [title]
---

$ARGUMENTS

# PR - Pull Request Workflow

Create a pull request after running all quality checks.

## Process

### Step 1: Pre-PR Checks

Run all validations before creating PR:

```bash
echo "Running pre-PR checks..."

# 1. Sanitization
bash .claude/scripts/pre-commit-sanitize.sh
[ $? -ne 0 ] && echo "BLOCKED: Fix sanitization issues first" && exit 1

# 2. Tests
npm test || pytest || go test ./... || cargo test
[ $? -ne 0 ] && echo "BLOCKED: Tests failing" && exit 1

# 3. Lint
npm run lint || ruff check . || cargo clippy
[ $? -ne 0 ] && echo "BLOCKED: Lint errors" && exit 1

# 4. Type check (if applicable)
npx tsc --noEmit || mypy . || echo "No type checker configured"

# 5. Documentation check
/update-docs --check-only
```

### Step 2: Ensure Clean State

```bash
# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes found. Commit first with /commit"
    exit 1
fi

# Check branch is pushed
git push -u origin $(git branch --show-current)
```

### Step 3: Generate PR Description

Based on commits since branch point:

```markdown
## Description

[Auto-generated from commit messages]

## Changes

### Files Modified
- `src/feature.ts` - Added new feature
- `src/feature.test.ts` - Tests for feature

### Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [x] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing

- [x] Tests pass locally
- [x] Lint passes
- [x] Sanitization passes

## Checklist

- [x] Code follows project style
- [x] Self-review completed
- [x] Comments added for complex code
- [x] Documentation updated
- [x] No new warnings introduced
```

### Step 4: Create PR

```bash
# Using GitHub CLI
gh pr create \
    --title "$ARGUMENTS" \
    --body "$(cat pr_description.md)" \
    --base main

# Or output for manual creation
echo "Create PR at: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/compare/$(git branch --show-current)"
```

## Output Format

```markdown
## Pull Request Created

### Pre-PR Checks
- [x] Sanitization: PASS
- [x] Tests: PASS (42 passed)
- [x] Lint: PASS
- [x] Type check: PASS

### PR Details
- **Title**: $ARGUMENTS
- **Branch**: feature/my-feature → main
- **Commits**: 3
- **Files changed**: 5

### Link
[View PR](https://github.com/user/repo/pull/123)

### Next Steps
1. Request reviewers
2. Address feedback
3. Merge when approved
```

## On Failure

If any check fails:

```markdown
## PR Blocked

### Failed Checks
| Check | Status | Details |
|-------|--------|---------|
| Tests | ✗ FAIL | 2 tests failing |
| Lint | ✗ FAIL | 3 errors |

### How to Fix
1. Run `/test` to see failing tests
2. Run `/lint --fix` to fix lint issues
3. Run `/pr` again when fixed
```

## Save State

```bash
bash .claude/scripts/save-memory.sh project-learnings "pr-created" "$(date): PR for $ARGUMENTS"
```
