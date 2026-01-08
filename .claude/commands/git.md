---
description: Git Pre-Push Checklist. Usage: /git
---

# Git Pre-Push Checklist

Run this before pushing to verify commit quality and workflow compliance.

## Step 1: Run Guard Check

```bash
python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/git-push-guard.py"
```

This automatically checks:
- Per-file commit comments present
- No bulk/lazy commit messages
- Root/.claude synced to CP/.claude (where applicable)
- No direct CP edits without root changes

## Step 2: Review Output

**If BLOCKED:** Fix commit messages before proceeding.

Required format:
```
<Summary line - what and why>

- <file1>: <specific change description>
- <file2>: <specific change description>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**If WARNINGS:** Review sync status, decide if sync needed.

## Step 3: CHANGELOG & Version (MANDATORY)

**EVERY commit to CP/ requires:**

1. **Update CHANGELOG.md** with new version entry:
   ```markdown
   ## vX.Y.Z - Title (Type)

   ### Changes
   - file.py: Description of change
   - other.json: Description of change
   ```

2. **Update version** in both files:
   ```bash
   # Check current versions
   grep -E "version.*[0-9]+\.[0-9]+\.[0-9]+" CP/CLAUDE.md CP/protocol-manifest.json
   ```

| Type | When | Example |
|------|------|---------|
| MAJOR (X.0.0) | Breaking changes | 2.0.0 |
| MINOR (x.Y.0) | New features | 1.3.0 |
| PATCH (x.y.Z) | Bug fixes, docs | 1.2.13 |

## Step 4: Push

```bash
git push origin <branch>
```

## Step 5: Create GitHub Release (MANDATORY)

**This step is NON-OPTIONAL. A version bump without a release is incomplete.**

```bash
gh release create vX.Y.Z --title "vX.Y.Z - Title" --notes "$(cat <<'EOF'
## Summary
- Change 1
- Change 2

**Full Changelog**: https://github.com/z3r0-c001/Claude_Protocol/compare/vPREV...vX.Y.Z
EOF
)"
```

## Step 6: Verify Release

```bash
gh release list --limit 3
```

Confirm new version shows as **Latest**.

---

## Quick Reference

| Check | Command |
|-------|---------|
| Run guard | `python3 .claude/hooks/git-push-guard.py` |
| View commits | `git log origin/main..HEAD --oneline` |
| View changes | `git diff origin/main..HEAD --stat` |
| Push | `git push origin <branch>` |
| Release | `gh release create v<version>` |

## Workflow Reminder (ALL STEPS MANDATORY)

```
1. DEVELOP    →  Edit in root .claude/
2. TEST       →  Verify changes work
3. SYNC       →  Copy to CP/.claude/
4. CHANGELOG  →  Update CP/CHANGELOG.md with changes
5. VERSION    →  Bump in protocol-manifest.json + CLAUDE.md
6. COMMIT     →  Per-file comments, no bulk
7. PUSH       →  After guard passes
8. RELEASE    →  gh release create (NEVER SKIP)
9. VERIFY     →  Confirm "Latest" on GitHub
```

**VIOLATIONS:**
- Skipping CHANGELOG = incomplete release
- Skipping VERSION = version mismatch
- Skipping RELEASE = orphaned commits

**CP Protection:** Never edit CP directly. Changes flow from root → CP.
