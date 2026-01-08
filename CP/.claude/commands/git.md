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

## Step 3: Version Check

If this is a release, verify version is updated:

```bash
grep -E "Version.*[0-9]+\.[0-9]+\.[0-9]+" CLAUDE.md CP/CLAUDE.md protocol-manifest.json 2>/dev/null
```

**Version types - ask user if unclear:**
| Type | When |
|------|------|
| MAJOR (x.0.0) | Breaking changes |
| MINOR (0.x.0) | New features |
| PATCH (0.0.x) | Bug fixes |

## Step 4: Push

```bash
git push origin <branch>
```

## Step 5: Create Release (if versioned)

```bash
gh release create v<version> --title "v<version>" --notes-file RELEASE_NOTES.md
```

Or with inline notes:
```bash
gh release create v<version> --title "v<version>" --notes "Release notes here"
```

---

## Quick Reference

| Check | Command |
|-------|---------|
| Run guard | `python3 .claude/hooks/git-push-guard.py` |
| View commits | `git log origin/main..HEAD --oneline` |
| View changes | `git diff origin/main..HEAD --stat` |
| Push | `git push origin <branch>` |
| Release | `gh release create v<version>` |

## Workflow Reminder

```
1. DEVELOP  →  Edit in root .claude/
2. TEST     →  Verify changes work
3. SYNC     →  Copy to CP/.claude/ (if distributable)
4. COMMIT   →  Per-file comments, no bulk
5. PUSH     →  After guard passes
6. RELEASE  →  Tag + GitHub release
```

**CP Protection:** Never edit CP directly. Changes flow from root → CP.
