# Changelog

**Current Version:** 1.2.0
**Date:** 2026-01-07

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.2.0 - Code Review Improvements

Comprehensive code review addressing concurrency, validation, robustness, and agent orchestration.

### Breaking Changes

- Memory server now requires `proper-lockfile` and `zod` dependencies
- `protocol-state` category is now explicitly read-only for write/delete operations
- All emoji characters removed from hook and agent output

### Plan Mode Enforcement (NEW)

Agents that support plan mode now get guided enforcement with user prompts:

| File | Change |
|------|--------|
| `.claude/hooks/agent-plan-enforcer.py` | NEW: Detects when plan mode should be used, prompts user |
| `.claude/hooks/agent-response-handler.py` | NEW: Handles approval flow, next_agents suggestions |
| `.claude/hooks/agent-announce.py` | Updated: Shows execution mode [PLAN] or [EXECUTE] in banner |

**Flow:**
```
User: /orchestrate security review
  |
  +-> agent-plan-enforcer detects orchestrator supports plan mode
  |   "Plan mode recommended. [P]lan / [E]xecute / [C]ancel?"
  |
  +-> User selects [P]
  |
  +-> Orchestrator runs in PLAN mode
  |   Banner: [ORCHESTRATE] ORCHESTRATOR [PLAN]
  |
  +-> agent-response-handler sees status: needs_approval
  |   "Approve this plan? [Y]es / [N]o / [M]odify"
  |
  +-> User approves, orchestrator invokes security-scanner
  |   (same plan->approve->execute flow for sub-agent)
  |
  +-> Results with next_agents suggestions
      "Run suggested agents? [A]ll / [1-N] / [S]kip"
```

### Color System Consolidation

| File | Change |
|------|--------|
| `.claude/hooks/colors.py` | NEW: Single source of truth for all terminal colors |
| `.claude/hooks/colors.py` | Supports NO_COLOR environment variable standard |
| `.claude/hooks/colors.py` | Automatic TTY detection for color enable/disable |
| `.claude/hooks/hook_colors.py` | Now a backward-compatibility wrapper around colors.py |
| `.claude/hooks/hook-colors.sh` | Updated to match colors.py definitions exactly |
| `.claude/hooks/agent-announce.py` | Refactored to use unified color system |
| All hooks | Removed all emoji characters - ASCII symbols only |

### Memory Server Improvements

| File | Change |
|------|--------|
| `package.json` | Bumped to v1.1.0, added `proper-lockfile` and `zod` dependencies |
| `src/types/memory.ts` | Added Zod schemas for runtime validation |
| `src/types/memory.ts` | Added `WRITABLE_CATEGORIES` export for consistent enum handling |
| `src/types/memory.ts` | Added `validateMemoryFile()` and `safeValidateMemoryFile()` helpers |
| `src/utils/file-ops.ts` | Replaced in-memory locks with `proper-lockfile` for true concurrency safety |
| `src/utils/file-ops.ts` | Added `withFileLock()` wrapper for all file operations |
| `src/index.ts` | Fixed category enum inconsistency (protocol-state now consistently handled) |
| `src/index.ts` | Server version bumped to 1.1.0 |

### Hook Robustness

| File | Change |
|------|--------|
| `.claude/settings.json` | Added timeouts to ALL hooks (5-30s depending on operation) |
| `.claude/settings.json` | Added `hooksDisabled` flag for debugging |
| `pretool-hallucination-check.py` | Increased timeout to 30s for network operations |

### Agent Model Strings

| Pattern | Fix |
|---------|-----|
| `model: opus` | Changed to `model: claude-opus-4-5-20251101` |
| `model: sonnet` | Changed to `model: claude-sonnet-4-5-20250929` |

Affected files: All 22 agent definition files in `.claude/agents/`

### Consistency Fixes

| File | Change |
|------|--------|
| `.claude/skills/frontend-design/skill.md` | Renamed to `SKILL.md` |
| `.claude/skills/design-system/skill.md` | Renamed to `SKILL.md` |

### Test Infrastructure

| File | Change |
|------|--------|
| `memory-server/jest.config.js` | Added Jest ESM configuration |
| `memory-server/src/__tests__/memory.test.ts` | Added unit tests for file-ops and search |
| `memory-server/package.json` | Added test script and dev dependencies |

### Summary of Issues Fixed

1. **Critical**: Race condition in file-ops.ts - in-memory locks don't survive process restarts
2. **Critical**: Missing schema validation on memory files
3. **High**: Hooks had no timeout recovery (only 1 of 20 had timeout)
4. **High**: `protocol-state` category inconsistency in tool enums
5. **High**: Hardcoded invalid model strings (`opus`, `sonnet`)
6. **Medium**: Inconsistent skill file naming (SKILL.md vs skill.md)
7. **Low**: No test coverage for MCP server

---

## v1.1.11 - Hook Path Resolution Fix

Fixed hooks not working on fresh git clone installations.

### Changes

| File | Change |
|------|--------|
| `.claude/hooks/run-hook.sh` | Use SCRIPT_DIR to find hooks relative to script location |
| `.claude/hooks/run-hook.sh` | No longer requires $CLAUDE_PROJECT_DIR to be set |
| `.claude/settings.json` | Changed from `$CLAUDE_PROJECT_DIR/.claude/hooks/` to `.claude/hooks/` |
| `.claude/settings.json` | Relative paths work from project root (Claude Code's working directory) |

---

## v1.1.10 - Dynamic Project Analysis

Rewrote A2.5 to use truly dynamic analysis instead of predefined question templates.

---

## v1.1.9 - Project Analysis Phase in Proto-Init

Added A2.5 section for project analysis (superseded by v1.1.10).

---

## v1.1.8 - Agent Protocol Enhancements

Enhanced agent protocol with plan mode support, improved documentation, and anti-hallucination safeguards.

---

## v1.1.7 - Hook Colored Output

Added colored visual feedback to all PreToolUse and PostToolUse hooks.

---

## v1.1.6 - Research Verifier Skill

Added new skill for verifying best practice claims against authoritative sources.

---

## v1.1.5 - Documentation Accuracy Audit

Fixed discrepancies between documented claims and actual codebase implementation.
