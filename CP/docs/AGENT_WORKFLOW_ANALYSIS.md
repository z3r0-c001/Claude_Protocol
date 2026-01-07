# Claude Protocol Agent Workflow Analysis

## Executive Summary

The agent system has a well-designed specification but relies heavily on Claude's voluntary compliance. The hooks system provides enforcement points but the current implementation has gaps between what's documented, what's enforced, and what Claude Code actually supports.

---

## Part 1: Official Claude Code Capabilities

### Task Tool Interface

```typescript
// Official Task tool schema
{
  "description": str,      // Short 3-5 word task description
  "prompt": str,           // Full task for agent to perform  
  "subagent_type": str     // Agent name (matches .claude/agents/*.md)
}

// Returns
{
  "result": str,           // Final result from subagent
  "usage": dict | null,    // Token usage
  "total_cost_usd": float, // Cost in USD
  "duration_ms": int       // Execution time
}
```

### Hook System Capabilities

| Hook | Trigger | Can Block? | Can Modify? | Feedback To Claude? |
|------|---------|------------|-------------|---------------------|
| PreToolUse | Before tool | Yes (exit 2 or deny) | Yes (updatedInput) | stderr on exit 2, reason on deny |
| PostToolUse | After tool | Yes (decision: block) | No | reason field |
| SubagentStop | Agent completes | Yes (decision: block) | No | reason field → Claude |
| UserPromptSubmit | Prompt submitted | Yes | Yes (stdout injection) | stdout injected |

### PreToolUse Decision Control (Official)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Explanation",
    "updatedInput": { "field": "new_value" }
  }
}
```

**Key Finding:** `"permissionDecision": "ask"` prompts user in UI! This is exactly what we need.

### SubagentStop Decision Control (Official)

```json
{
  "decision": "block",
  "reason": "This goes to Claude and tells it what to do next"
}
```

---

## Part 2: Current Protocol Implementation

### Agent Categories

| Category | Count | Plan Mode | Purpose |
|----------|-------|-----------|---------|
| Core | 3 | 2/3 | Strategic work (architect, performance) |
| Quality | 8 | 1/8 | Validation (security, tests, honesty) |
| Domain | 8 | 5/8 | Specialized tasks (frontend, protocols) |
| Workflow | 2 | 2/2 | Coordination (orchestrator, brainstormer) |
| **Total** | **21** | **10/21** | |

### Agents Supporting Plan Mode

1. orchestrator
2. brainstormer  
3. architect
4. security-scanner
5. performance-analyzer
6. frontend-designer
7. ui-researcher
8. protocol-analyzer
9. protocol-updater
10. document-processor

### Current Enforcement Hooks

| Hook | Purpose | Enforcement Level |
|------|---------|-------------------|
| agent-plan-enforcer.py | Detect missing plan mode | Warn only (decision: ask not working) |
| agent-announce.py | Display banners | Visual only |
| agent-handoff-validator.py | Validate response format | Warn only |
| agent-response-handler.py | Handle approvals | Not integrated |

---

## Part 3: Gap Analysis

### Critical Gap 1: "ask" Decision Not Implemented

**Problem:** The `agent-plan-enforcer.py` outputs custom JSON format:
```json
{"decision": "ask", "message": "...", "options": {...}}
```

**Reality:** Claude Code expects:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse", 
    "permissionDecision": "ask",
    "permissionDecisionReason": "Plan mode recommended for orchestrator"
  }
}
```

**Fix:** Update hook to use official format.

### Critical Gap 2: updatedInput Not Used

**Problem:** When user approves plan mode, nothing actually modifies the prompt.

**Solution:** Use `updatedInput` to inject `execution_mode: plan`:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "prompt": "execution_mode: plan\n\n" + original_prompt
    }
  }
}
```

### Critical Gap 3: Subagent Response Not Validated

**Problem:** Agent returns JSON but nothing ensures primary Claude reads it correctly.

**Current:** `agent-handoff-validator.py` warns but doesn't enforce.

**Solution:** SubagentStop hook should:
1. Parse agent JSON response
2. If `status: needs_approval` → block with reason telling Claude to present plan
3. If `next_agents` present → inject suggestion into Claude's context

### Gap 4: Orchestrator Doesn't Actually Orchestrate

**Problem:** Orchestrator is just documentation - nothing forces it to:
- Invoke agents in plan mode first
- Wait for approval between phases
- Actually deploy sub-agents

**Solution:** This requires prompt engineering in the orchestrator agent itself, PLUS enforcement via hooks.

### Gap 5: Skills Not Available to Agents

**Official Documentation:**
> Built-in agents (Explore, Plan, Verify) and the Task tool do not have access to your Skills. Only custom subagents you define in .claude/agents/ with an explicit skills field can use Skills.

**Current Implementation:** No agent has `skills` field in frontmatter.

**Solution:** Add skills field to agents:
```yaml
---
name: security-scanner
skills:
  - security-scanner
  - quality-audit
---
```

---

## Part 4: Corrected Implementation

### Fixed agent-plan-enforcer.py

```python
def main():
    # ... detection logic ...
    
    if supports_plan_mode and current_mode is None:
        # Use OFFICIAL Claude Code format
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Agent '{agent_name}' supports plan mode. Recommend running in plan mode first to assess scope before execution."
            }
        }
        print(json.dumps(result))
        return
```

### Fixed Plan Mode Injection

When user approves (if "ask" works), or we need to force it:

```python
def inject_plan_mode():
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {
                "prompt": f"execution_mode: plan\n\n{original_prompt}"
            }
        }
    }
    print(json.dumps(result))
```

### Fixed SubagentStop Handler

```python
def handle_agent_response():
    # Parse agent's JSON response
    response_data = extract_json_from_response(transcript)
    
    if response_data.get("status") == "needs_approval":
        # Block and tell Claude what to do
        result = {
            "decision": "block",
            "reason": f"""Agent returned status: needs_approval

Present this to the user and wait for approval:

{response_data.get('present_to_user')}

After user approves, invoke the agent again with execution_mode: execute"""
        }
        print(json.dumps(result))
        return
        
    if response_data.get("next_agents"):
        # Suggest next agents to Claude
        suggestions = format_suggestions(response_data["next_agents"])
        result = {
            "continue": True,
            "hookSpecificOutput": {
                "additionalContext": f"Agent suggests running: {suggestions}"
            }
        }
        print(json.dumps(result))
```

---

## Part 5: Creative Solutions

### Solution A: Prompt-Based Hooks (Official Feature)

Use Claude Code's prompt-based hooks for intelligent decisions:

```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if this subagent completed correctly. Input: $ARGUMENTS\n\nCheck:\n- Did agent return valid JSON with required fields?\n- Is status appropriate for the work done?\n- Should next_agents be invoked?\n\nReturn: {\"decision\": \"approve\" or \"block\", \"reason\": \"explanation\"}",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Pros:** LLM-powered validation, context-aware
**Cons:** Costs tokens, slower, non-deterministic

### Solution B: State Machine Tracking

Track execution state across hook invocations:

```python
# .claude/hooks/state/agent-state.json
{
  "active_workflows": {
    "workflow-123": {
      "orchestrator": "plan_approved",
      "security-scanner": "pending_plan",
      "agents_completed": ["laziness-destroyer"]
    }
  }
}
```

Hooks read/write this state to enforce proper sequencing.

### Solution C: CLAUDE.md Injection

Instead of hooks, inject orchestration rules into CLAUDE.md:

```markdown
## MANDATORY: Agent Orchestration Rules

When invoking ANY agent via Task tool:

1. **Check plan mode support**
   - Read agent file frontmatter
   - If `supports_plan_mode: true`, ALWAYS invoke with `execution_mode: plan` first

2. **Handle plan response**
   - Parse JSON at end of agent response
   - If `status: needs_approval`, present `present_to_user` to human
   - Wait for explicit approval before execute mode

3. **Never skip plan mode**
   - Even for "quick" tasks
   - Exception: Agent explicitly doesn't support plan mode
```

**Pros:** No hooks needed, just prompting
**Cons:** Claude can ignore it, no enforcement

### Solution D: Hybrid Approach (Recommended)

Combine all approaches:

1. **CLAUDE.md** - Document the expected behavior
2. **PreToolUse hook** - Use official `"permissionDecision": "ask"` format
3. **SubagentStop hook** - Use `"decision": "block"` with reason to Claude
4. **Prompt-based hook** - For complex validation (optional)
5. **State tracking** - For multi-agent workflows

---

## Part 6: Implementation Checklist

### Immediate Fixes

- [ ] Update `agent-plan-enforcer.py` to use official JSON format
- [ ] Test if `permissionDecision: "ask"` actually prompts user
- [ ] Update `agent-response-handler.py` to use `decision: "block"` 
- [ ] Add `skills` field to agent frontmatter

### Workflow Enforcement

- [ ] Create state tracking file for multi-agent workflows
- [ ] Add orchestrator-specific validation in SubagentStop
- [ ] Test full plan→approve→execute flow

### Documentation Updates

- [ ] Update AGENT_PROTOCOL.md with official hook formats
- [ ] Add troubleshooting guide for hook debugging
- [ ] Document creative workarounds

### Testing Required

- [ ] Test `permissionDecision: "ask"` in real Claude Code
- [ ] Test `updatedInput` actually modifies Task prompt
- [ ] Test SubagentStop `decision: "block"` feedback loop
- [ ] Test prompt-based hooks for SubagentStop

---

## Part 7: Unknown Behaviors (Need Testing)

1. **Does "ask" work for Task tool?**
   - Documentation shows it for generic PreToolUse
   - Unknown if it works specifically for Task matcher

2. **Does updatedInput work for Task?**
   - Should modify `prompt` field
   - Need to verify it doesn't break Task execution

3. **How does SubagentStop receive transcript?**
   - Current hook reads from `transcript_path`
   - Need to verify this is populated correctly

4. **Can hooks communicate with each other?**
   - State file approach is one method
   - Environment variables might work

5. **What's the hook timeout behavior?**
   - Does timeout cause allow or deny?
   - Important for longer validations

---

## Appendix A: Agent Frontmatter Template

```yaml
---
name: agent-name
description: "PROACTIVELY use when [trigger conditions]. Invoke with /command or automatically."
tools:
  - Read
  - Write
  - Grep
  - Glob
  - Task  # If agent can invoke other agents
model: claude-sonnet-4-5-20250929  # or claude-opus-4-5-20251101
color: blue  # For banner display
supports_plan_mode: true  # Enable two-phase execution
skills:
  - skill-name  # Skills this agent can access
---

# Agent Name

## Purpose

[What this agent does]

## Plan Mode (`execution_mode: plan`)

When invoked in plan mode:
1. Assess scope
2. Return `status: needs_approval` with `present_to_user`

## Execute Mode (`execution_mode: execute`)

When invoked in execute mode:
1. Perform full work
2. Return `status: complete` with findings

## Response Format

Always end with JSON block per AGENT_PROTOCOL.md
```

---

## Appendix B: Hook Output Reference

### PreToolUse - Allow with modification
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {"prompt": "execution_mode: plan\n\nOriginal prompt"}
  }
}
```

### PreToolUse - Ask user
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Agent supports plan mode. Run in plan mode first?"
  }
}
```

### PreToolUse - Deny
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Must specify execution_mode for plan-capable agents"
  }
}
```

### SubagentStop - Block and redirect
```json
{
  "decision": "block",
  "reason": "Agent returned needs_approval. Present plan to user before executing."
}
```

### SubagentStop - Continue with context
```json
{
  "continue": true,
  "hookSpecificOutput": {
    "additionalContext": "Agent suggests running: tester, reviewer"
  }
}
```
