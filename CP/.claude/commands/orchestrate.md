---
description: Coordinate multi-agent workflows with the orchestrator agent
---

# Orchestrate Multi-Agent Workflow

Invoke the orchestrator agent to coordinate complex, multi-agent tasks.

## Usage

```
/orchestrate [task description or workflow name]
```

## Examples

```
/orchestrate full quality check on auth module
/orchestrate security and performance review
/orchestrate prepare for PR
```

## Built-in Workflows

### Quality Audit
```
/orchestrate quality
```
Runs: laziness-destroyer, hallucination-checker, honesty-evaluator (parallel)

### Security Review
```
/orchestrate security
```
Runs: security-scanner, dependency-auditor (if package files exist)

### PR Readiness
```
/orchestrate pr
```
Runs: reviewer, test-coverage-enforcer, security-scanner (if auth files changed)

### Performance Check
```
/orchestrate perf
```
Runs: performance-analyzer

### Full Audit
```
/orchestrate full
```
Runs: All quality + security + performance agents

## Instructions

When this command is invoked:

1. **Invoke the orchestrator agent** using the Task tool:
   ```
   Use Task tool with subagent_type="orchestrator"
   Prompt: "Orchestrate: [user's task description]"
   ```

2. **Let orchestrator plan the workflow**:
   - Orchestrator will identify which agents are needed
   - Determine execution order (parallel vs sequential)
   - Estimate scope

3. **Present the plan** to the user:
   - Show which agents will run
   - Show execution strategy
   - Get approval if needed

4. **Execute the workflow**:
   - Orchestrator invokes agents via Task tool
   - Collects results from each
   - Synthesizes into unified report

5. **Present unified results**:
   - Combined findings from all agents
   - Priority-ranked recommendations
   - Any blockers or issues

## Orchestrator Agent Details

The orchestrator agent:
- Lives at `.claude/agents/workflow/orchestrator.md`
- Can invoke any other agent
- Supports plan mode for workflow assessment
- Synthesizes multi-agent results

## Auto-Invocation

The orchestrator is automatically invoked on:
- `/validate` - Quality check workflow
- `/pr` - PR readiness workflow
- `/security` - Security review workflow

Manual invocation via `/orchestrate` gives more control over which agents to run.

## Output Format

The orchestrator returns a unified report:

```markdown
# Orchestration Report

## Workflow Summary
- Task: [description]
- Agents invoked: [count]
- Execution: [parallel/sequential]

## Agent Results

### [Agent 1 Name]
[Summary of findings]

### [Agent 2 Name]
[Summary of findings]

## Combined Metrics
| Agent | Critical | High | Medium | Low |
|-------|----------|------|--------|-----|
| ...   | ...      | ...  | ...    | ... |

## Recommended Actions
1. [Highest priority]
2. [Second priority]

## Blockers
[Any blockers preventing completion]
```

## Integration

The orchestrator respects the AGENT_PROTOCOL.md standard:
- Agents run in plan mode first (if supported)
- Structured JSON responses collected
- `present_to_user` content synthesized into report
