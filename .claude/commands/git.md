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

### 2. Commit Message Audit

Review the commit message for the push:
```bash
git log -1 --format="%B"
```

**BLOCK if ANY of these patterns found:**
- "Updated files"
- "Fixed bugs"
- "Various improvements"
- "WIP"
- "Changes"
- "Modified"
- Per-file descriptions that are just "updated", "changed", "fixed" without specifics

**REQUIRE:**
- Specific summary (what action + what changed + why)
- Per-file breakdown with UNIQUE, SPECIFIC descriptions
- Each file description explains WHAT function/class/feature changed

### 3. Version Check

Verify version was bumped:
```bash
grep '"version"' protocol-manifest.json | head -1
grep 'Version' CLAUDE.md | head -1
```

**If this is a release/fix:**
- Version MUST be incremented (MAJOR.MINOR.PATCH)
- Both files must match

### 4. Changelog Check

For ANY push with code changes:
```bash
ls -la CHANGELOG-v*.md | tail -1
```

**REQUIRE:**
- CHANGELOG-vX.X.X.md exists for current version
- Contains specific per-file breakdown
- Describes WHY changes were made

### 5. Tag Verification

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
- [x] Commit message: Specific per-file details ✓
- [ ] Version: NOT UPDATED - BLOCKING
- [ ] Changelog: NOT FOUND - BLOCKING
- [ ] Tag: Not created yet

## BLOCKED - Fix these issues:
1. Update version in protocol-manifest.json and CLAUDE.md
2. Create CHANGELOG-v1.1.1.md with per-file details
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
