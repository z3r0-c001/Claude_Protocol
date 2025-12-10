---
description: Fix a bug or issue. Usage: /fix <issue description or number>
---

$ARGUMENTS

# FIX WORKFLOW

You are fixing a bug or issue. Follow this exact process:

## Phase 1: Understand

1. **Load context**
```bash
bash .claude/scripts/load-memory.sh
```

2. **Parse the issue**
- If a number: Look up in issue tracker or git
- If description: Identify the problem

3. **Reproduce the bug**
```bash
# Run failing test or reproduce steps
```

4. **Locate the source**
```bash
# Search for relevant code
grep -rn "error_pattern" --include="*.py" --include="*.ts" .
```

## Phase 2: Plan (use `think hard`)

Before coding, output:
```markdown
## Bug Analysis

### Symptoms
- [What's happening]

### Root Cause
- [Why it's happening]

### Affected Files
- [List files to modify]

### Fix Approach
- [How to fix]

### Test Strategy
- [How to verify fix]
```

## Phase 3: Fix

1. **Write a failing test first** (if none exists)
2. **Implement the fix** - No placeholders
3. **Run the test** - Must pass
4. **Check for regressions**
```bash
# Run full test suite
npm test  # or pytest, go test, etc.
```

## Phase 4: Verify

```bash
# Laziness check
bash .claude/scripts/laziness-check.sh .

# Hallucination check  
bash .claude/scripts/hallucination-check.sh .
```

## Phase 5: Sanitize & Commit

**ALWAYS sanitize before committing:**

```bash
# Run sanitization
bash .claude/scripts/pre-commit-sanitize.sh
```

If sanitization passes:
```bash
# Commit with reference
git add -A
git commit -m "fix: [description]

Fixes #[issue_number]"
```

If sanitization fails:
- Fix all errors listed
- Re-run sanitization
- Only commit when PASS

## Memory

Save the fix for future reference:
```bash
bash .claude/scripts/save-memory.sh corrections "[bug_type]" "[what was wrong and how fixed]"
```

## Output

```markdown
## Fix Complete: [Issue]

### Problem
[What was wrong]

### Solution
[What was changed]

### Files Modified
- [file1]: [change]
- [file2]: [change]

### Tests
- [x] New test added
- [x] All tests pass

### Commit
[commit hash]
```
