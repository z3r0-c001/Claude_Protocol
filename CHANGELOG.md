# Changelog

**Current Version:** 1.1.3
**Date:** 2026-01-02

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.3 - Protocol Audit & Official Spec Alignment

Comprehensive audit against official Claude Code documentation. Aligned agents, cleaned distribution, fixed command references.

### Distribution Hygiene

| File | Change |
|------|--------|
| `.gitignore` | Added `protocol-manifest.local.json` to excluded files |
| `.claude/protocol-manifest.local.json` | Removed from git (per-installation state, not distribution) |

### Install Script Improvements

| File | Change |
|------|--------|
| `install.sh` | Step [6/8]: Generate `protocol-manifest.local.json` with installation timestamp |
| `install.sh` | Step [8/8]: Automatically build MCP memory server (`npm install && npm run build`) |
| `install.sh` | Updated step numbering from 6 to 8 steps |

### Schema Compliance

| File | Change |
|------|--------|
| `.mcp.json` | Removed non-standard `mcpConfig` section and `description` field |

### Agent Alignment (22 files)

All agent files updated to match official Claude Code agent specification:

| Change | Files Affected |
|--------|----------------|
| Removed `supports_plan_mode: true` | All 21 agents |
| Changed `model: claude-opus-4-5-20251101` → `model: opus` | 6 agents |
| Changed `model: claude-sonnet-4-20250514` → `model: sonnet` | 15 agents |
| Updated format documentation | `AGENT_PROTOCOL.md` |

**Agents updated:**
- `core/`: architect, performance-analyzer, research-analyzer
- `domain/`: codebase-analyzer, dependency-auditor, document-processor, frontend-designer, protocol-analyzer, protocol-generator, protocol-updater, ui-researcher
- `quality/`: fact-checker, hallucination-checker, honesty-evaluator, laziness-destroyer, reviewer, security-scanner, test-coverage-enforcer, tester
- `workflow/`: brainstormer, orchestrator

### Documentation Updates

| File | Change |
|------|--------|
| `skill-rules.json` | Added `_meta` field documenting as custom protocol extension |
| `CLAUDE.md` | Fixed 7 invalid command references (`/init` → `/proto-init`, removed non-existent commands) |
| `CLAUDE.md` | Added missing commands: `/proto-status`, `/proto-update`, `/git`, `/search`, `/orchestrate` |
| `CLAUDE.md` | Added new sections: Documentation Processing, Session commands |
| `CLAUDE.md` | Updated agent trigger references to match actual commands |
| `CLAUDE.md` | Version 1.1.2 → 1.1.3 |
| `protocol-manifest.json` | Version 1.1.2 → 1.1.3 |

### Verified Correct (No Changes Needed)

| Item | Finding |
|------|---------|
| Python shebangs | Already `#!/usr/bin/env python3` |
| Hook overlap | Complementary, not duplicative |
| `run-hook.sh` wrapper | Kept for project/global fallback |
| Skill field names | `tools:` in agents, `allowed-tools:` in skills (distinct) |
