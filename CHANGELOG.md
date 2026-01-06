# Changelog

**Current Version:** 1.1.9
**Date:** 2026-01-06

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.9 - Project Analysis Phase in Proto-Init

Enhanced `/proto-init` command with intelligent project analysis and Socratic questioning.

### Project Analysis & Refinement

| File | Change |
|------|--------|
| `.claude/commands/proto-init.md` | Added A2.5 section: Project Analysis & Refinement |
| `.claude/commands/proto-init.md` | Extracts domain keywords, security indicators, functionality hints |
| `.claude/commands/proto-init.md` | Asks clarifying questions based on detected patterns |
| `.claude/commands/proto-init.md` | Generates project-specific agent/skill suggestions |
| `.claude/commands/proto-init.md` | Confirms understanding before proceeding to bootstrap |

### Why This Matters

When users provide project descriptions like "An application for my farm with sensitive encrypted data", the protocol now:
1. Identifies domain (agriculture), security requirements, functionality scope
2. Asks targeted clarifying questions (data types, encryption needs, compliance)
3. Suggests custom agents (farm-manager, encryption-handler, compliance-auditor)
4. Recommends project-specific skills before generating configuration

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
