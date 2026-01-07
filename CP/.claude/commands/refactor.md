---
description: Refactor code with full quality pipeline. Invokes architects, analyzers, testers, and validators.
---

# Code Refactoring

Refactor code while maintaining behavior and quality.

## Process

### 1. Assess
- Identify what needs refactoring
- Understand current behavior
- Ensure tests exist (or create them first)

### 2. Plan
- Define target state
- Plan incremental steps
- Identify risk areas

### 3. Refactor
- Make small, atomic changes
- Preserve behavior at each step
- Keep tests passing

### 4. Verify
- Run full test suite
- Compare before/after behavior
- Check performance impact

### 5. Report
- Summarize changes made
- Note any behavioral differences
- List files modified

## Quality Gates

Before refactoring:
- [ ] Tests exist for affected code
- [ ] Current behavior is understood

During refactoring:
- [ ] Each change is atomic
- [ ] Tests pass after each change

After refactoring:
- [ ] All tests pass
- [ ] No placeholder code
- [ ] Code is cleaner

## Agents to Use

- `architect` - For design decisions
- `reviewer` - To review changes
- `test-coverage-enforcer` - To ensure coverage

---

Begin by assessing the current state and planning the refactoring steps.
