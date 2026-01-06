# Changelog

**Current Version:** 1.1.11
**Date:** 2026-01-06

> This file is overwritten with each release. For historical changes, see git history.

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

### Root Cause

The previous settings.json used `$CLAUDE_PROJECT_DIR` which may not be set in all environments. Combined with run-hook.sh defaulting to `.` when the variable wasn't set, hooks failed to locate their scripts on fresh installations.

---

## v1.1.10 - Dynamic Project Analysis

Rewrote A2.5 to use truly dynamic analysis instead of predefined question templates.

### Changes

| File | Change |
|------|--------|
| `.claude/commands/proto-init.md` | Replaced templated questions with dynamic 5-step analysis |
| `.claude/commands/proto-init.md` | Step 1: Parse description for What/Who/Why/How/Constraints |
| `.claude/commands/proto-init.md` | Step 2: Identify gaps and ambiguities in ANY description |
| `.claude/commands/proto-init.md` | Step 3: Generate questions SPECIFIC to user's actual words |
| `.claude/commands/proto-init.md` | Step 4: Synthesize understanding and suggest components |
| `.claude/commands/proto-init.md` | Step 5: Iterate until user confirms understanding |

### Before vs After

**Before (v1.1.9):** Predefined question sets for specific domains (security, farm, forms, research)

**After (v1.1.10):** Dynamic analysis that generates unique questions based on whatever the user describes

---

## v1.1.9 - Project Analysis Phase in Proto-Init

Added A2.5 section for project analysis (superseded by v1.1.10).

---

## v1.1.8 - Agent Protocol Enhancements

Enhanced agent protocol with plan mode support, improved documentation, and anti-hallucination safeguards.

### Plan Mode Support (10 agents)

Added `supports_plan_mode: true` to all agents that document plan/execute modes:

| File | Change |
|------|--------|
| `.claude/agents/core/architect.md` | Added supports_plan_mode: true |
| `.claude/agents/core/performance-analyzer.md` | Added supports_plan_mode: true |
| `.claude/agents/domain/document-processor.md` | Added supports_plan_mode: true |
| `.claude/agents/domain/frontend-designer.md` | Added supports_plan_mode: true |
| `.claude/agents/domain/protocol-analyzer.md` | Added supports_plan_mode: true |
| `.claude/agents/domain/protocol-updater.md` | Added supports_plan_mode: true |
| `.claude/agents/domain/ui-researcher.md` | Added supports_plan_mode: true |
| `.claude/agents/quality/security-scanner.md` | Added supports_plan_mode: true |
| `.claude/agents/workflow/brainstormer.md` | Added supports_plan_mode: true |
| `.claude/agents/workflow/orchestrator.md` | Added supports_plan_mode: true |

### Protocol Documentation

| File | Change |
|------|--------|
| `.claude/agents/AGENT_PROTOCOL.md` | Added Plan→Approval→Execute flow documentation |
| `.claude/agents/AGENT_PROTOCOL.md` | Added EnterPlanMode vs Agent Plan Mode clarification |
| `.claude/agents/AGENT_PROTOCOL.md` | Added Primary Agent Coordination section |

### Anti-Hallucination Safeguards

| File | Change |
|------|--------|
| `.claude/agents/quality/security-scanner.md` | Added mandatory file verification before reporting findings |
| `.claude/agents/quality/security-scanner.md` | Added verified field and context_lines requirements |
| `.claude/agents/quality/security-scanner.md` | Added CRITICAL CONSTRAINTS section with quality checklist |

### Random Agent Coloring

| File | Change |
|------|--------|
| `.claude/hooks/agent-announce.py` | Added RANDOM_COLOR_POOL with 14 vibrant color schemes |
| `.claude/hooks/agent-announce.py` | Added get_random_theme_for_agent() using MD5 hash |
| `.claude/hooks/agent-announce.py` | Unknown agents now get deterministic random colors |

---

## v1.1.7 - Hook Colored Output

Added colored visual feedback to all PreToolUse and PostToolUse hooks.

---

## v1.1.6 - Research Verifier Skill

Added new skill for verifying best practice claims against authoritative sources with scientific rigor.

---

## v1.1.5 - Documentation Accuracy Audit

Fixed discrepancies between documented claims and actual codebase implementation.
