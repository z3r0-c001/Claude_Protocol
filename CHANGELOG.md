# Changelog

**Current Version:** 1.1.3
**Date:** 2026-01-02

> This file is overwritten with each release. For historical changes, see git history.

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
| `agent-announce.py` | Simple icons: ● for agents, ◦ for sub-agents |
| `agent-announce.py` | Reduced from 268 to 147 lines |

### Project Summary Updates

| File | Change |
|------|--------|
| `CLAUDE.md` | Updated summary: "Quality-enforced protocol with automated hooks, specialized agents, and persistent memory" |
| `README.md` | Updated summary with clear value proposition and feature highlights |
| `protocol-manifest.json` | Updated description to match new branding |

### Proto-Update Fixes

| File | Change |
|------|--------|
| `context-loader.py` | Added fallback to main manifest when local manifest missing |
| `context-loader.py` | Handles both `repository.url` and `source.url` formats |
| `context-loader.py` | Fixed nested component structure counting |
| `protocol-manifest.json` | Added missing `git.md` command entry |
| `protocol-manifest.json` | Added missing `agent-announce.py` hook entry |

### Security Fixes

| File | Change |
|------|--------|
| `file-edit-tracker.sh` | Fixed command injection via FILE_PATH in sed - now uses jq --arg |
| `context-detector.sh` | Fixed unescaped JSON output - now uses jq for safe construction |
| `research-quality-check.sh` | Fixed unescaped JSON output - now uses jq for safe construction |
| All 3 scripts | Added `set -o pipefail` for better error handling |

### Statistics

| Metric | Value |
|--------|-------|
| Total lines | ~20,500 |
| Total files | 131 |
| Agents | 21 |
| Commands | 25 |
| Hooks | 20 |
| Skills | 16 |
