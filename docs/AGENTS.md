# Agent Reference

Complete reference for all Claude Bootstrap Protocol agents.

## Overview

Agents are specialized subagents that handle specific tasks. They are invoked:
- **Automatically** by hooks based on context
- **Manually** via commands
- **By other agents** when specialized knowledge is needed

## Quality Agents

### laziness-destroyer

**Purpose:** Enforce zero-tolerance policy for incomplete, placeholder, or delegated code.

**Location:** `.claude/agents/quality/laziness-destroyer.md`

**Invocation:**
- Automatically on every Stop hook
- Via `/validate` command
- Via `/audit` command

**Detection Categories:**
1. **Placeholder Code** (CRITICAL)
   - `// ...`, `# ...`, `/* ... */`

2. **TODO/FIXME Markers** (CRITICAL)
   - `// TODO`, `# TODO`, `// FIXME`

3. **Stub Implementations** (CRITICAL)
   - `pass`, `raise NotImplementedError`
   - `throw new NotImplementedError()`

4. **Delegation to User** (CRITICAL)
   - "You could...", "You'll need to..."
   - "Consider adding...", "Left as an exercise..."

5. **Scope Reduction** (MAJOR)
   - Asked for 10 items, delivered 3
   - Partial implementations

**Output Format:**
```json
{
  "decision": "approve|block",
  "laziness_score": 0,
  "violations": [...],
  "required_actions": [...]
}
```

**Decision Rules:**
| Condition | Decision |
|-----------|----------|
| laziness_score >= 3 | BLOCK |
| ANY critical violation | BLOCK |
| 2+ major violations | BLOCK |
| Only minor violations | APPROVE with warnings |

---

### hallucination-checker

**Purpose:** Verify all packages, APIs, and technical claims are real.

**Location:** `.claude/agents/quality/hallucination-checker.md`

**Invocation:**
- Automatically on Stop hook
- Via `/validate` command
- When code references external packages

**Verification Categories:**
1. **Package Verification**
   - npm packages exist on registry
   - Python packages exist on PyPI
   - Go modules are valid

2. **API Verification**
   - Method signatures match documentation
   - Function parameters are correct
   - Return types are accurate

3. **CLI Verification**
   - Command flags are valid
   - Tool versions support used features

**Output Format:**
```json
{
  "decision": "approve|block",
  "verified": [...],
  "hallucinations": [...],
  "suggestions": [...]
}
```

---

### security-scanner

**Purpose:** Identify security vulnerabilities before they reach production.

**Location:** `.claude/agents/quality/security-scanner.md`

**Invocation:**
- Automatically when editing auth/security files
- Via `/security` command
- Before commits via `/commit`

**Security Categories:**
1. **Injection Vulnerabilities**
   - SQL Injection
   - Command Injection
   - NoSQL Injection

2. **Authentication Issues**
   - Hardcoded credentials
   - Weak password handling
   - Missing auth checks

3. **Sensitive Data Exposure**
   - Unencrypted data
   - Logging sensitive info
   - Exposed API keys

4. **XSS (Cross-Site Scripting)**
   - Reflected XSS
   - Stored XSS
   - DOM-based XSS

5. **Access Control**
   - Missing authorization
   - Privilege escalation
   - IDOR vulnerabilities

**Severity Levels:**
| Severity | Action |
|----------|--------|
| Critical | Block merge |
| High | Block merge |
| Medium | Require review |
| Low | Suggest fix |

**Output Format:**
```json
{
  "scan_complete": true,
  "findings": [...],
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 2
  }
}
```

---

### fact-checker

**Purpose:** Verify factual claims in responses and documentation.

**Location:** `.claude/agents/quality/fact-checker.md`

**Invocation:**
- Via `/verify` command
- When documentation is modified
- For research tasks

**Verification Process:**
1. Extract factual claims
2. Search for authoritative sources
3. Compare claims against sources
4. Report discrepancies

---

### reviewer

**Purpose:** Code review with focus on quality, security, and maintainability.

**Location:** `.claude/agents/quality/reviewer.md`

**Invocation:**
- Via `/pr` command
- Via `/review` command
- During feature implementation

**Review Categories:**
1. Code quality
2. Security concerns
3. Performance issues
4. Maintainability
5. Test coverage

---

### tester

**Purpose:** Generate comprehensive tests for code.

**Location:** `.claude/agents/quality/tester.md`

**Invocation:**
- Via `/test` command
- During `/feature` implementation
- During `/fix` workflow

**Test Types:**
- Unit tests
- Integration tests
- Edge case tests
- Error handling tests

---

### test-coverage-enforcer

**Purpose:** Ensure adequate test coverage for all new code.

**Location:** `.claude/agents/quality/test-coverage-enforcer.md`

**Invocation:**
- After code implementation
- Before commits
- Via `/coverage` command

**Coverage Requirements:**
| Code Type | Required Coverage |
|-----------|------------------|
| New features | 80% |
| Bug fixes | 100% (for the fix) |
| Utilities | 90% |
| API endpoints | 85% |
| Critical paths | 95% |

**Decision Rules:**
| Condition | Decision |
|-----------|----------|
| New code < 80% coverage | BLOCK |
| Critical path < 95% | BLOCK |
| No tests for new function | BLOCK |

---

## Core Agents

### architect

**Purpose:** System design, architecture decisions, and technical planning.

**Location:** `.claude/agents/core/architect.md`

**Invocation:**
- Via `/refactor` command
- During major feature planning
- When architectural decisions needed

**Responsibilities:**
- Evaluate design options
- Consider trade-offs
- Recommend patterns
- Plan implementation strategy

---

### research-analyzer

**Purpose:** Analyze and synthesize research findings.

**Location:** `.claude/agents/core/research-analyzer.md`

**Invocation:**
- After web research
- When comparing approaches
- Before making recommendations

**Analysis Process:**
1. Gather all research findings
2. Identify patterns and themes
3. Find contradictions
4. Note information gaps
5. Synthesize recommendations

**Output Format:**
```markdown
## Summary
[Overview]

## Key Findings
1. [Finding] - Source: [source]

## Contradictions Found
| Topic | Source A | Source B | Resolution |

## Recommendations
1. [Recommendation]

## Confidence Level
[High/Medium/Low]
```

---

### performance-analyzer

**Purpose:** Identify performance issues and suggest optimizations.

**Location:** `.claude/agents/core/performance-analyzer.md`

**Invocation:**
- When code involves loops/data processing
- Via `/perf` command
- When user mentions "slow" or "optimize"

**Analysis Categories:**
1. **Algorithmic Complexity**
   - O(n²) patterns
   - Inefficient data structures

2. **Database Performance**
   - N+1 queries
   - Missing indexes

3. **Memory Usage**
   - Memory leaks
   - Unbounded caches

4. **I/O Operations**
   - Blocking operations
   - Missing caching

**Common Patterns Detected:**
```javascript
// N+1 Query - FLAGGED
for (const user of users) {
  const posts = await db.posts.find({ userId: user.id });
}

// Recommendation
const posts = await db.posts.find({ userId: { $in: userIds } });
```

---

## Agent Invocation Matrix

| Context | Agent Invoked |
|---------|---------------|
| Stop hook | laziness-destroyer, hallucination-checker |
| Auth file edited | security-scanner |
| Package file edited | dependency-auditor |
| Test file edited | test-coverage-enforcer |
| Documentation edited | fact-checker |
| Performance code | performance-analyzer |
| Architecture change | architect |
| Research complete | research-analyzer |

## Creating Custom Agents

To create a custom agent:

1. Create markdown file in `.claude/agents/`:
```yaml
---
name: my-agent
description: "What this agent does"
tools:
  - Read
  - Grep
  - Glob
model: claude-opus-4-5-20251101
---

# My Agent

## Purpose
[Description]

## When to Use
[Triggers]

## Process
[Steps]

## Output Format
[Expected output]
```

2. Add to settings.json hooks if auto-invocation needed
3. Reference in commands if manual invocation needed
