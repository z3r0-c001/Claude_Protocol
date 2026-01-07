# Changelog

**Current Version:** 1.2.9
**Date:** 2026-01-07

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.2.9 - Version Consolidation

Version bump to consolidate all 1.2.x improvements and documentation updates.

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
7. **Low**: Minimal test coverage for MCP server (added basic unit tests, not integration)

---

## v1.1.11 - Hook Path Resolution Fix

Fixed hooks not working on fresh git clone installations.

### Changes

| File | Change |
|------|--------|
| `.claude/hooks/run-hook.sh` | Enhanced to use SCRIPT_DIR for hook discovery |
| `.claude/settings.json` | Updated paths to use `$CLAUDE_PROJECT_DIR` for robustness |

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

### Agent Workflow Fixes

**Hook API Corrections:**

The following hooks have been updated to use the official Claude Code hook API format:

| Hook | Before | After |
|------|--------|-------|
| agent-plan-enforcer.py | Custom `decision: "ask"` | Official `permissionDecision: "ask"` |
| agent-response-handler.py | Custom format | Official `decision: "block"` with reason |

**Official PreToolUse format:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "User-facing explanation"
  }
}
```

**Official SubagentStop format:**
```json
{
  "decision": "block",
  "reason": "This text is fed back to Claude"
}
```

See `docs/AGENT_WORKFLOW_ANALYSIS.md` for complete analysis of gaps and solutions.

### New Agents Added

Ten new agents to address identified blind spots:

| Agent | Category | Purpose |
|-------|----------|---------|
| debugger | core | Systematic debugging and root cause analysis |
| documenter | core | Generate README, API docs, ADRs, docstrings |
| refactorer | core | Safe code refactoring with pattern application |
| api-designer | domain | REST/GraphQL API design and documentation |
| data-modeler | domain | Database schema, migrations, query optimization |
| devops-engineer | domain | CI/CD, Docker, deployment configuration |
| accessibility-auditor | quality | WCAG compliance, keyboard navigation, screen readers |
| error-handler | quality | Error types, structured logging, observability |
| tech-debt-tracker | workflow | Catalog, prioritize, and report technical debt |
| git-strategist | workflow | Merge conflicts, branch strategy, history cleanup |

All new agents support plan mode for user approval workflows.

### Model Version Management System

Added centralized model version tracking with startup audit:

**Files Added:**
- `.claude/config/models.json` - Central model registry
- `.claude/hooks/model-audit.py` - Startup hook for version checking
- `.claude/scripts/update-models.py` - Model update utility

**Features:**
- Automatic model version audit on Claude Code startup
- Detects deprecated/outdated model strings in agents
- Single config file to update when new models release
- Integration with `/update-proto` command
- Manual model setting: `--set-model opus=claude-opus-4-6-20260101`

**Workflow:**
1. Claude Code starts → model-audit.py runs
2. If outdated models found → warning displayed
3. User runs `/update-proto --models` or `--update`
4. All agent files updated automatically

### Unified Health Check System

Added startup health check that requires acknowledgment:

**Files:**
- `.claude/scripts/health-check.py` - Unified startup checker
- `.claude/scripts/proto-update.py` - Fixed early return bug
- `CLAUDE.md` - Startup instruction added

**Startup Flow:**
```
Claude Code starts
       ↓
Reads CLAUDE.md
       ↓
Runs health-check.py
       ↓
Checks: models, protocol version, hook integrity
       ↓
If issues → Display warning, require acknowledgment
       ↓
Continue to user request
```

**Acknowledgment Required:**
- Warnings block until user types "yes"
- Prevents accidentally running with outdated config
- Once per session (1 hour cache)

### Intelligent Model Routing (v1.2.0)

Added tiered model selection for cost/performance optimization:

**New Files:**
- `.claude/config/model-routing.json` - Task complexity mapping and routing rules

**Agent Updates:**
- All 31 agents now have `model_tier` field (fast/standard/high)
- 7 agents can be downgraded with `min_tier: fast`
- Updated `AGENT_PROTOCOL.md` with tier guidelines

**Tier Distribution:**
- `high` (Opus): 7 agents - orchestrator, architect, debugger, brainstormer, fact-checker, hallucination-checker, research-analyzer
- `standard` (Sonnet): 24 agents - most development tasks
- `fast` (Haiku): 0 default, 7 downgrade-capable

**Orchestrator Enhancement:**
- Added intelligent model selection section
- Complexity assessment guidelines
- Cost optimization strategies
- Model override in task invocation

**Downgrade-Capable Agents:**
These agents can run on Haiku for simple tasks:
- tester, reviewer, laziness-destroyer
- documenter, document-processor
- git-strategist, tech-debt-tracker

**Cost Savings Example:**
```
Before (all Sonnet): 5x × 7 agents = 35x baseline
After (mixed):       1x×3 + 5x×3 + 25x×1 = 43x (complex) or 18x (simple)
```
