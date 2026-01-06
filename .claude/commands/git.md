---
description: Pre-push checklist for quality commits. Usage: /git
---

# Git Pre-Push Checklist

Run this before pushing to verify commit quality.

## Checklist

### 1. Commit Message Quality

```bash
git log origin/main..HEAD --format="%s" 2>/dev/null || git log -5 --format="%s"
```

**Block if generic messages:**
- "Updated files"
- "Fixed bugs"
- "WIP"
- "Changes"
- Single-word descriptions

**Good commit format:**
```
<summary line>

- <file>: <specific change>
- <file>: <specific change>
```

### 2. Review Changes

```bash
git diff origin/main..HEAD --stat 2>/dev/null || git diff HEAD~1 --stat
```

Verify:
- No unintended files included
- No secrets/credentials
- No large binary files

### 3. Version Check (if releasing)

If this is a versioned release:
```bash
# Check version files exist and are updated
grep -E 'version|Version' package.json pyproject.toml CLAUDE.md 2>/dev/null | head -5
```

### 4. Run Tests

```bash
# Project-specific - adapt to your setup
npm test 2>/dev/null || pytest 2>/dev/null || echo "No test command found"
```

## Output Format

```
## Pre-Push Verification

- [x] Commit messages: Specific and descriptive
- [x] Changes reviewed: No secrets or unwanted files
- [ ] Tests: FAILED - fix before pushing
- [x] Version: Updated (if applicable)

## Status: BLOCKED
Fix failing tests before pushing.
```

## After Approval

```bash
git push origin <branch>
```

---

**Note:** Customize this checklist to match your project's requirements.
