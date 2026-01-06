# Agent Protocol Standard

This document defines the standard protocol all agents must follow for consistent orchestration, handoff, and execution.

## Agent Definition Structure

All agents are defined as Markdown files with YAML frontmatter:

```yaml
---
name: agent-name
description: "When to use this agent"
tools:
  - Read
  - Write
  - Grep
  - Task
model: claude-opus-4-5-20251101
supports_plan_mode: true
---
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Kebab-case identifier (e.g., `security-scanner`) |
| `description` | Yes | When to use, starts with action verb |
| `tools` | Yes | Array of tools agent can use |
| `model` | Yes | Claude model version |
| `supports_plan_mode` | No | Boolean, enables two-phase execution |

## Execution Modes

Agents that support plan mode operate in two phases:

### Plan Mode

Invoked with `execution_mode: plan`:

1. **Assess scope** - What will be examined/changed
2. **Identify targets** - Specific files, functions, areas
3. **Estimate impact** - How much work, what dependencies
4. **Propose approach** - How the agent will proceed
5. **Request approval** - If needed, or auto-proceed for small scope

**Plan mode is lightweight** - No file modifications, minimal tool usage.

### Execute Mode

Invoked with `execution_mode: execute`:

1. **Perform work** - Full analysis, modifications, scanning
2. **Document findings** - Structured results
3. **Provide recommendations** - Actionable next steps
4. **Suggest next agents** - Who should run after

## Response Format

All agents MUST return structured JSON at the end of their response:

```json
{
  "agent": "agent-name",
  "execution_mode": "plan|execute",
  "status": "complete|blocked|needs_approval|needs_input",
  "scope": {
    "files_analyzed": 12,
    "complexity": "low|medium|high",
    "estimated_changes": 3
  },
  "findings": {
    "summary": "Brief 1-2 sentence summary",
    "details": [
      {
        "category": "category-name",
        "severity": "critical|high|medium|low|info",
        "description": "What was found",
        "location": "file:line or general area",
        "recommendation": "What to do about it"
      }
    ],
    "metrics": {
      "issues_found": 5,
      "critical": 1,
      "high": 2,
      "medium": 2
    }
  },
  "recommendations": [
    {
      "action": "Description of recommended action",
      "priority": "high|medium|low",
      "rationale": "Why this is recommended"
    }
  ],
  "blockers": [
    {
      "type": "approval_needed|error|missing_info|dependency",
      "description": "What is blocking progress"
    }
  ],
  "next_agents": [
    {
      "agent": "agent-name",
      "reason": "Why this agent should run next",
      "can_parallel": true,
      "data_dependency": "Optional: what data to pass"
    }
  ],
  "present_to_user": "Formatted markdown summary for user presentation"
}
```

### Response Fields

| Field | Required | Description |
|-------|----------|-------------|
| `agent` | Yes | Agent's own name |
| `execution_mode` | Yes | Which mode was executed |
| `status` | Yes | Execution outcome |
| `scope` | Plan mode | Scope assessment |
| `findings` | Execute mode | What was discovered |
| `recommendations` | No | Suggested actions |
| `blockers` | If blocked | What's preventing completion |
| `next_agents` | No | Follow-up agents to invoke |
| `present_to_user` | Yes | User-friendly summary |

### Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `complete` | Work finished successfully | Present findings, run next agents |
| `blocked` | Cannot proceed | Address blockers first |
| `needs_approval` | Requires user sign-off | Wait for approval |
| `needs_input` | Missing information | Ask user for details |

## Integration with Orchestrator

The orchestrator agent coordinates multi-agent workflows:

### Orchestration Patterns

**Sequential with approval:**
```
orchestrator → agent1(plan) → approval → agent1(execute) → agent2(plan) → ...
```

**Parallel independent:**
```
orchestrator → [security, performance, tests](plan) in parallel
           → collect plans
           → [security, performance, tests](execute) in parallel
           → synthesize results
```

**Pipeline with handoff:**
```
brainstormer → architect(data=findings) → tester(data=plan) → reviewer
```

### Parallel Execution Rules

Agents can run in parallel when:
- No data dependencies between them
- `can_parallel: true` in `next_agents`
- Independent scopes (different files/areas)

Agents must run sequentially when:
- Output of one is input to another
- Modifying same files
- Decision gates (approval needed)

## Agent Categories

### Core Agents (Strategic)
- `architect` - System design, planning
- `research-analyzer` - Synthesize findings
- `performance-analyzer` - Performance optimization

### Quality Agents (Validation)
- `security-scanner` - Security vulnerabilities
- `laziness-destroyer` - Incomplete code detection
- `hallucination-checker` - Verify real packages/APIs
- `honesty-evaluator` - Overclaiming detection
- `reviewer` - Code review
- `tester` - Test generation
- `test-coverage-enforcer` - Coverage requirements

### Domain Agents (Specialized)
- `codebase-analyzer` - Project structure
- `protocol-generator` - Claude artifacts
- `frontend-designer` - UI/UX design
- `ui-researcher` - Design research
- `dependency-auditor` - Dependency health

### Workflow Agents (Process)
- `brainstormer` - Requirements refinement
- `orchestrator` - Multi-agent coordination

## Primary Agent Coordination

The primary agent (Claude in the main conversation) coordinates sub-agents through a defined flow:

### Plan→Approval→Execute Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRIMARY AGENT FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User Request                                                │
│         │                                                       │
│         ▼                                                       │
│  2. Primary Agent analyzes task                                 │
│         │                                                       │
│         ├──[complex task]──► 3. Launch agent(plan)              │
│         │                         │                             │
│         │                         ▼                             │
│         │                    4. Agent returns plan              │
│         │                    (status: needs_approval)           │
│         │                         │                             │
│         │                         ▼                             │
│         │                    5. Primary presents to user        │
│         │                    "Plan: scan 47 files. Proceed?"    │
│         │                         │                             │
│         │                         ▼                             │
│         │                    6. User approves                   │
│         │                         │                             │
│         │                         ▼                             │
│         │                    7. Launch agent(execute)           │
│         │                         │                             │
│         │                         ▼                             │
│         │                    8. Agent returns results           │
│         │                         │                             │
│         └──[simple task]─────────►│                             │
│                                   ▼                             │
│                              9. Present to user                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Primary Agent Responsibilities

| Step | Action | How to Implement |
|------|--------|------------------|
| Detect plan-mode agent | Check `supports_plan_mode: true` in frontmatter | Read agent file or use registry |
| Invoke plan mode | Pass `execution_mode: plan` in prompt | Include in Task tool prompt |
| Interpret response | Parse agent's JSON response | Extract `status`, `present_to_user` |
| Request approval | If `status: needs_approval` | Show user the `present_to_user` content |
| Invoke execute mode | After approval | Pass `execution_mode: execute` in new Task |

### Invoking Plan Mode

When launching a plan-mode agent via Task tool:

```
Task(subagent_type="security-scanner", prompt="""
execution_mode: plan

Analyze the authentication code for security vulnerabilities.
""")
```

### Interpreting Agent Response

After agent completes, primary agent should:

1. **Parse JSON response** from agent's output
2. **Check status**:
   - `complete`: Present findings, check `next_agents`
   - `needs_approval`: Show `present_to_user`, wait for user
   - `blocked`: Report blockers, ask user how to proceed
   - `needs_input`: Ask user for missing information
3. **Handle next_agents**: Launch suggested agents if appropriate

### Auto-Proceed Rules

Agents can auto-proceed without approval when:
- Scope is small (< 10 files)
- Complexity is low
- No modifications will be made (read-only analysis)

Otherwise, agent should return `status: needs_approval`.

## EnterPlanMode vs Agent Plan Mode

These are **different concepts** that serve different purposes:

### EnterPlanMode (Claude Code Tool)

| Property | Description |
|----------|-------------|
| **What** | Built-in tool for primary agent to enter planning mode |
| **When** | Before implementing complex features requiring user sign-off |
| **Who** | Primary Claude agent uses this |
| **Purpose** | Get user approval before major code changes |
| **Scope** | Entire conversation enters plan mode |

### Agent Plan Mode (Protocol Feature)

| Property | Description |
|----------|-------------|
| **What** | Two-phase execution for sub-agents |
| **When** | When launching agents that support it |
| **Who** | Sub-agents implement this |
| **Purpose** | Lightweight scope assessment before full execution |
| **Scope** | Only that specific agent invocation |

### When to Use Which

| Scenario | Use |
|----------|-----|
| User says "implement feature X" | EnterPlanMode (plan the implementation) |
| Running security scan | Agent plan mode (assess scope, then scan) |
| Complex multi-step task | Both (EnterPlanMode first, then agents with plan mode) |
| Quick code review | Agent plan mode only |

### Interaction Pattern

```
User: "Implement user authentication"
        │
        ▼
Primary Agent uses EnterPlanMode
        │
        ▼
Primary creates implementation plan
        │
        ▼
User approves plan
        │
        ▼
Primary exits plan mode, begins implementation
        │
        ├──► Launch brainstormer(plan) → approval → brainstormer(execute)
        │
        ├──► Launch architect(plan) → approval → architect(execute)
        │
        └──► Launch security-scanner(plan) → approval → security-scanner(execute)
```

## Backward Compatibility

Agents without `supports_plan_mode: true`:
- Treated as execute-only by orchestrator
- Existing behavior unchanged
- Can be upgraded incrementally

## Examples

### Plan Mode Response

```json
{
  "agent": "security-scanner",
  "execution_mode": "plan",
  "status": "needs_approval",
  "scope": {
    "files_analyzed": 0,
    "files_to_scan": 47,
    "complexity": "medium",
    "areas": ["authentication", "API endpoints", "database queries"]
  },
  "findings": {
    "summary": "Will scan 47 files across 3 security-sensitive areas",
    "details": []
  },
  "recommendations": [],
  "blockers": [],
  "next_agents": [],
  "present_to_user": "**Security Scan Plan**\n\nI'll examine 47 files focusing on:\n- Authentication logic\n- API endpoint validation\n- Database query construction\n\nProceed with scan?"
}
```

### Execute Mode Response

```json
{
  "agent": "security-scanner",
  "execution_mode": "execute",
  "status": "complete",
  "scope": {
    "files_analyzed": 47,
    "complexity": "medium"
  },
  "findings": {
    "summary": "Found 3 security issues: 1 critical, 2 medium",
    "details": [
      {
        "category": "SQL Injection",
        "severity": "critical",
        "description": "Unsanitized user input in query",
        "location": "src/api/users.ts:142",
        "recommendation": "Use parameterized queries"
      }
    ],
    "metrics": {
      "issues_found": 3,
      "critical": 1,
      "medium": 2
    }
  },
  "recommendations": [
    {
      "action": "Fix SQL injection in users.ts immediately",
      "priority": "high",
      "rationale": "Critical vulnerability, exploitable"
    }
  ],
  "blockers": [],
  "next_agents": [
    {
      "agent": "tester",
      "reason": "Generate security regression tests",
      "can_parallel": false
    }
  ],
  "present_to_user": "**Security Scan Complete**\n\n| Severity | Count |\n|----------|-------|\n| Critical | 1 |\n| Medium | 2 |\n\n**Critical Issue:** SQL injection vulnerability in `src/api/users.ts:142`\n\nRecommended: Fix immediately and add security tests."
}
```
