---
name: workflow
description: >
  Standard development workflows. Use PROACTIVELY for any multi-step task.
  Triggers on: implement, build, create, develop, fix, refactor.
allowed-tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Bash
  - Grep
  - Glob
  - Task
---

# Workflow Skill

## Overview

This skill defines standard workflows for common development tasks. Use these workflows to ensure consistent, high-quality implementations.

## Available Workflows

### 1. Feature Implementation

When implementing a new feature:

```
1. UNDERSTAND
   - Read related code to understand patterns
   - Identify affected files
   - Check for existing similar implementations

2. PLAN
   - Define implementation steps
   - Identify potential risks
   - Determine testing approach

3. IMPLEMENT
   - Write code following existing patterns
   - Handle all error cases
   - No placeholders or TODOs

4. VERIFY
   - Run syntax checks
   - Run existing tests
   - Test new functionality

5. CLEANUP
   - Remove debug code
   - Ensure consistent style
   - Update related documentation
```

### 2. Bug Fix

When fixing a bug:

```
1. REPRODUCE
   - Understand how to trigger the bug
   - Identify expected vs actual behavior

2. INVESTIGATE
   - Trace code path
   - Identify root cause
   - Understand why it happens

3. FIX
   - Make minimal necessary changes
   - Don't introduce new issues
   - Handle edge cases

4. VERIFY
   - Confirm bug is fixed
   - Ensure no regressions
   - Add test to prevent recurrence
```

### 3. Refactoring

When refactoring code:

```
1. ASSESS
   - Identify what needs refactoring
   - Understand current behavior
   - Ensure tests exist

2. PLAN
   - Define target state
   - Plan incremental steps
   - Identify risk areas

3. REFACTOR
   - Make small, atomic changes
   - Preserve behavior
   - Maintain tests passing

4. VERIFY
   - Run full test suite
   - Compare before/after behavior
   - Check performance impact
```

### 4. Code Review

When reviewing code:

```
1. CONTEXT
   - Understand the purpose
   - Read related code

2. CHECK
   - Completeness (no placeholders)
   - Correctness (logic is sound)
   - Security (no vulnerabilities)
   - Performance (no obvious issues)
   - Style (consistent with codebase)

3. FEEDBACK
   - Be specific and actionable
   - Explain the "why"
   - Suggest alternatives
```

## Workflow Selection

| User Request | Workflow |
|--------------|----------|
| "Add [feature]" | Feature Implementation |
| "Fix [issue]" | Bug Fix |
| "Refactor [code]" | Refactoring |
| "Review [code]" | Code Review |

## Quality Gates (All Workflows)

Before completing ANY workflow:

- [ ] No placeholder code
- [ ] All imports verified
- [ ] Error handling complete
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if needed)

## Integration with Agents

| Workflow Step | Agent |
|--------------|-------|
| Planning | architect |
| Implementation | laziness-destroyer (for completeness) |
| Verification | test-coverage-enforcer |
| Security Check | security-scanner |
| Final Review | reviewer |

## Best Practices

### DO
- Follow the workflow steps in order
- Verify each step before proceeding
- Document decisions made
- Ask for clarification when needed

### DON'T
- Skip verification steps
- Leave work incomplete
- Assume understanding without reading code
- Make unnecessary changes

## Example: Feature Implementation

User: "Add a dark mode toggle to the settings page"

```
1. UNDERSTAND
   - Read settings page code
   - Check existing theme handling
   - Identify state management approach

2. PLAN
   - Add toggle component to settings
   - Create theme context/state
   - Update CSS variables
   - Persist preference

3. IMPLEMENT
   - Create ThemeProvider
   - Add toggle to SettingsPage
   - Implement CSS variable switching
   - Save to localStorage

4. VERIFY
   - Toggle works as expected
   - Preference persists
   - No style regressions

5. CLEANUP
   - Remove any debug logs
   - Ensure consistent naming
```
