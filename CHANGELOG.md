# Changelog

**Current Version:** 1.1.5
**Date:** 2026-01-06

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.5 - Documentation Accuracy Audit

Fixed discrepancies between documented claims and actual codebase implementation.

### Critical Fixes

| Issue | Location | Fix |
|-------|----------|-----|
| "80+ specialized agents" claim | README.md line 3 | Changed to "21 specialized agents" (actual count) |
| `/verify` command referenced | README.md, CLAUDE.md | Removed - command doesn't exist |
| `/coverage` command referenced | README.md, CLAUDE.md | Changed to `/test --coverage` |
| `research-verifier` skill | CLAUDE.md | Removed - skill directory doesn't exist |

### Hook Documentation Updates

| File | Change |
|------|--------|
| README.md | Added PreToolUse (Write): pretool-laziness-check.py, pretool-hallucination-check.py |
| README.md | Added PostToolUse (Read): doc-size-detector.py |
| README.md | Fixed SubagentStop: added agent-handoff-validator.py |
| CLAUDE.md | Same hook documentation updates as README.md |

### Agent Trigger Corrections

| Agent | Old Trigger | New Trigger |
|-------|-------------|-------------|
| fact-checker | `/verify` | Manual |
| research-analyzer | `/verify` | SubagentStop hook |
| test-coverage-enforcer | `/coverage` | `/test --coverage` |

### Version Bump

| File | Change |
|------|--------|
| CLAUDE.md | 1.1.4 → 1.1.5 |
| protocol-manifest.json | 1.1.4 → 1.1.5 |

---

## v1.1.4 - Existing CLAUDE.md Preservation

Added intelligent handling of existing CLAUDE.md files during protocol initialization to prevent accidental overwrites.

### Changes

| File | Change |
|------|--------|
| `proto-init.md` | Added B0 section: Analyze Existing CLAUDE.md (CRITICAL - DO FIRST) |
| `proto-init.md` | B0 reads entire file, extracts/categorizes content |
| `proto-init.md` | B0 offers 3 options: `merge`, `review`, `replace` (requires CONFIRM) |
| `proto-init.md` | Updated C3 to merge intelligently: user content as base |
