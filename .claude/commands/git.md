---
description: MANDATORY pre-push checklist. MUST run before ANY git push. Usage: /git
---

# Git Push Mandates

**THIS IS MANDATORY BEFORE ANY GIT PUSH. NO EXCEPTIONS.**

## Trigger

This skill MUST be invoked:
- Before `git push`
- Before `git push origin`
- Before `git push --force`
- Before ANY push operation

**If you are about to push and have NOT run /git, STOP and run it first.**

## Pre-Push Checklist

### 1. Location Verification
```bash
pwd
```
**MUST be in CP directory.** If not, STOP. Do not push from root.

### 2. Individual Commits Per File (MANDATORY)

**Each file MUST be committed separately with its own specific message.**

This ensures GitHub displays unique descriptions next to each file/folder.

```bash
# Check commits being pushed
git log origin/main..HEAD --oneline
```

**BLOCK if:**
- Multiple files in a single commit
- Same commit message appears for different files

**CORRECT approach:**
```bash
git add file1.md && git commit -m "file1.md: Specific description of changes"
git add file2.py && git commit -m "file2.py: Specific description of changes"
```

**WRONG approach:**
```bash
git add -A && git commit -m "Updated multiple files"  # BLOCKED
```

### 3. Commit Message Audit

Review each commit message:
```bash
git log origin/main..HEAD --format="%s"
```

**BLOCK if ANY of these patterns found:**
- "Updated files"
- "Fixed bugs"
- "Various improvements"
- "WIP"
- "Changes"
- "Modified"
- Generic descriptions like "updated", "changed", "fixed" without specifics

**REQUIRE for each commit:**
- Format: `filename: Specific description of what changed`
- Explains WHAT function/class/feature/line changed
- Unique message per file

### 4. Version Check

Verify version was bumped:
```bash
grep '"version"' protocol-manifest.json | head -1
grep 'Version' CLAUDE.md | head -1
```

**If this is a release/fix:**
- Version MUST be incremented (MAJOR.MINOR.PATCH)
- Both files must match

### 5. Changelog Check

For ANY push with code changes:
```bash
cat CHANGELOG.md | head -20
```

**REQUIRE:**
- CHANGELOG.md updated with current version
- Contains specific per-file breakdown
- Describes WHY changes were made

### 6. Tag Verification

Check existing tags:
```bash
git tag -l
```

**For version releases:**
- Tag MUST be created: `git tag vX.X.X`
- Tag MUST be pushed: `git push origin vX.X.X`

## Execution Flow

When /git is invoked:

1. **Run all checks above**
2. **Display results as checklist:**

```
## Pre-Push Verification

- [x] Location: CP directory confirmed
- [x] Individual commits: Each file has separate commit ✓
- [x] Commit messages: Specific per-file details ✓
- [ ] Version: NOT UPDATED - BLOCKING
- [ ] Changelog: NOT UPDATED - BLOCKING
- [ ] Tag: Not created yet

## BLOCKED - Fix these issues:
1. Update version in protocol-manifest.json and CLAUDE.md
2. Update CHANGELOG.md with per-file details for current version
```

3. **If ANY check fails: BLOCK and list what needs fixing**
4. **If ALL checks pass: Display approval message and proceed**

## Version Numbering

- **PATCH** (1.1.0 → 1.1.1): Bug fixes, typo corrections, minor updates
- **MINOR** (1.1.0 → 1.2.0): New features, significant additions
- **MAJOR** (1.1.0 → 2.0.0): Breaking changes, major rewrites

## Changelog Format

```markdown
# Changelog v1.1.1

## Summary
<One sentence describing the release>

## Changes

### <filename>
- <Specific change 1>
- <Specific change 2>

### <filename>
- <Specific change 1>
```

## After Approval

Once all checks pass:

```bash
git push origin main
git tag vX.X.X
git push origin vX.X.X
```

---

**REMEMBER: This checklist is NON-NEGOTIABLE. Every push must pass ALL checks.**
