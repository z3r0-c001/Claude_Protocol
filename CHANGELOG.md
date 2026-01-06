# Changelog

**Current Version:** 1.1.4
**Date:** 2026-01-06

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.4 - Existing CLAUDE.md Preservation

Added intelligent handling of existing CLAUDE.md files during protocol initialization to prevent accidental overwrites.

### Changes

| File | Change |
|------|--------|
| `proto-init.md` | Added B0 section: Analyze Existing CLAUDE.md (CRITICAL - DO FIRST) |
| `proto-init.md` | B0 reads entire file, extracts/categorizes content (identity, tech stack, commands, patterns, rules, custom sections) |
| `proto-init.md` | B0 offers 3 options: `merge` (keep all, add protocol), `review` (section-by-section approval), `replace` (requires CONFIRM) |
| `proto-init.md` | Updated C3 to merge intelligently: user content as base, protocol sections added around it |
| `CLAUDE.md` | Version bump 1.1.3 → 1.1.4 |
| `protocol-manifest.json` | Version bump 1.1.3 → 1.1.4, date updated |

### Why This Matters

Previously, running `/proto-init` on an existing codebase with a `CLAUDE.md` would prompt to overwrite without analyzing the existing content. Users could lose:
- Project-specific patterns and conventions
- Custom behavioral rules
- Tech stack documentation
- Build/test/deploy commands

Now the protocol preserves all existing content by default.

---

## v1.1.3 - Proto-Init Improvements & Minimal Colorization

Enhanced initialization flow, simplified visual styling, and project summary updates.

### Proto-Init Enhancements

| File | Change |
|------|--------|
| `proto-init.md` | Split A4 (Tech Stack) into 3 separate questions: A4a (Languages), A4b (Frameworks), A4c (Database) |
| `proto-init.md` | Added A2b (Description Audit) - Claude reviews and suggests improvements to project description |
| `proto-init.md` | Each question now includes helpful examples |

### Agent Colorization (Simplified)

| File | Change |
|------|--------|
| `agent-announce.py` | Removed background colors, now uses text colors only |
| `agent-announce.py` | Semantic coloring: quality=red, core=blue, domain=green, workflow=yellow, explore=cyan |
| `agent-announce.py` | Simple icons: for agents, for sub-agents |
| `agent-announce.py` | Reduced from 268 to 147 lines |

### Project Summary Updates

| File | Change |
|------|--------|
| `CLAUDE.md` | Updated summary: "Quality-enforced protocol with automated hooks, specialized agents, and persistent memory" |
| `README.md` | Updated summary with clear value proposition and feature highlights |
| `protocol-manifest.json` | Updated description to match new branding |
