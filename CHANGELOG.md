# Changelog

**Current Version:** 1.1.2
**Date:** 2026-01-02

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.2 - Changelog & Install Improvements

Consolidate versioned changelogs into single file, integrate /commit with /git skill, add install.sh origin cleanup.

### Changes

| File | Change |
|------|--------|
| `.claude/commands/commit.md` | Lines 126-127: Changed `CHANGELOG-vX.X.X.md` to single `CHANGELOG.md`; Lines 145-156: Added "Before Pushing" section mandating `/git` before push |
| `.claude/commands/git.md` | Lines 64-70: Changed changelog check from `ls -la CHANGELOG-v*.md` to `cat CHANGELOG.md`; Line 101: Updated fix instruction to reference single CHANGELOG.md |
| `CLAUDE.md` | Line 9: Version 1.1.1 → 1.1.2; Line 109: Changed changelog reference from versioned to single file |
| `protocol-manifest.json` | Line 3: Version 1.1.1 → 1.1.2; Line 4: Date updated to 2026-01-02 |
| `CHANGELOG.md` | Replaced versioned files (CHANGELOG-v1.1.0.md, CHANGELOG-v1.1.1.md) with single overwritten file |
| `install.sh` | Lines 256-270: Added prompt after successful install to delete origin (cloned repo) directory |

### Deleted

| File | Reason |
|------|--------|
| `CHANGELOG-v1.1.0.md` | Consolidated into single CHANGELOG.md |
| `CP/CHANGELOG-v1.1.0.md` | Consolidated into single CHANGELOG.md |
| `CP/CHANGELOG-v1.1.1.md` | Consolidated into single CHANGELOG.md |

---

## v1.1.1 - Protocol Fixes

Fix protocol documentation inconsistencies, standardize hook output format, and add missing manifest entries.

### Changes

| File | Change |
|------|--------|
| docs/TROUBLESHOOTING.md | Node.js version requirement: v20 → v18 for consistency |
| docs/INSTALLATION.md | Updated counts: commands (14→24), hooks (13→20), skills (6→15) |
| protocol-manifest.json | Fixed repository URL, added missing component descriptions |
| .claude/hooks/dangerous-command-check.py | Standardized JSON output format |
| .claude/commands/commit.md | Single CHANGELOG.md instead of versioned files |
| CLAUDE.md | Updated version to 1.1.1 |

---

## v1.1.0 - Protocol Enhancement Release

Major update adding self-updating protocol, frontend design system, document processing, and comprehensive documentation overhaul.

### New Features

**Self-Updating Protocol System**
- `protocol-manifest.json` - Master manifest with 81 components, SHA-256 checksums
- `.claude/agents/domain/protocol-updater.md` - Agent for GitHub updates with interactive approval
- `.claude/commands/proto-update.md` - Command with --check, --analyze, --auto options

**Frontend Design System**
- `.claude/agents/domain/frontend-designer.md` - UI/UX design agent
- `.claude/agents/domain/ui-researcher.md` - Research agent for UI patterns
- `.claude/skills/frontend-design/SKILL.md` - Complete frontend workflow skill
- `.claude/skills/design-system/SKILL.md` - Design tokens and consistency

**Document Processing System**
- `.claude/agents/domain/document-processor.md` - Large document chunking agent
- `.claude/hooks/doc-size-detector.py` - Detect large files, suggest chunking
- `.claude/commands/doc-ingest.md`, `doc-search.md`, `doc-list.md` - Document commands

**Workflow Agents**
- `.claude/agents/workflow/brainstormer.md` - Socratic questioning agent
- `.claude/agents/workflow/orchestrator.md` - Multi-agent coordination

### Updated Components

- All quality agents: Standardized JSON output per AGENT_PROTOCOL.md
- All core agents: Added plan mode support
- All hooks: Enhanced validation, JSON output format
- Documentation: Moved to docs/ directory with disclaimers

### License Change

CC BY-NC-SA 4.0 with clarifications:
- Internal business use: PERMITTED
- Selling, SaaS, commercial products: PROHIBITED
