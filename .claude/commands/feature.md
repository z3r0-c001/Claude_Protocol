---
description: Implement a new feature. Usage: /feature <feature description>
---

# Feature Implementation

Implement a new feature using the standard workflow.

## Process

### 1. Understand
- Read the feature description
- Search codebase for related code
- Identify affected files and systems

### 2. Plan
- Break down into implementation steps
- Identify potential risks
- Create a checklist

### 3. Implement
- Follow existing code patterns
- Handle all error cases
- Write complete code (no placeholders)

### 4. Verify
- Run syntax checks
- Run existing tests
- Test the new functionality

### 5. Report
- Summarize what was implemented
- List files created/modified
- Note any follow-up items

## Quality Requirements

- Zero placeholder code
- All imports must be real packages
- Error handling must be complete
- Follow existing code style

## Agents to Use

Consider invoking:
- `architect` - For design decisions
- `security-scanner` - If auth/security related
- `test-coverage-enforcer` - To ensure test coverage

---

Begin by understanding the feature request and exploring related code in the codebase.
