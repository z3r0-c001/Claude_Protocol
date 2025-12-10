---
description: Refactor code with full quality pipeline. Invokes architects, analyzers, testers, and validators.
allowed-tools: Bash(*), Read(*), Write(*), Grep(*), Glob(*)
---

$ARGUMENTS

# REFACTOR - Comprehensive Code Improvement Workflow

Refactor code while maintaining functionality. This workflow orchestrates multiple agents and validation steps to ensure safe, high-quality refactoring.

---

## PHASE 1: UNDERSTAND SCOPE
**Purpose**: Define what we're refactoring and why

### 1.1 Parse Request
Identify from user's request:
- **Target**: What code to refactor (file, module, function, pattern)
- **Goal**: Why refactor (readability, performance, maintainability, DRY, etc.)
- **Constraints**: What must NOT change (APIs, behavior, interfaces)

### 1.2 Load Context
```bash
# Load memory for past decisions about this code
bash .claude/scripts/load-memory.sh

# Check protocol state
cat .claude/memory/protocol-state.json
```

### 1.3 Locate Target Code
```bash
# Find the files to refactor
find . -type f -name "*.{js,ts,py,go,rs,java}" | head -50

# If specific file/pattern given, locate it
grep -rn "[PATTERN]" --include="*.{ts,js,py}" . | head -20
```

**Output**: Clear statement of what will be refactored and the goal.

---

## PHASE 2: ANALYZE CURRENT STATE
**Purpose**: Understand the code before changing it

### 2.1 Invoke Architect Agent
```
@architect Analyze the architecture of [TARGET]:
- Current structure and patterns
- Dependencies (what depends on this, what this depends on)
- Coupling and cohesion assessment
- Potential refactoring approaches
```

### 2.2 Invoke Performance Analyzer
```
@performance-analyzer Analyze [TARGET] for:
- Current performance characteristics
- Bottlenecks or inefficiencies
- Memory usage patterns
- Algorithmic complexity
```

### 2.3 Invoke Security Scanner
```
@security-scanner Check [TARGET] for:
- Security vulnerabilities that refactoring could fix
- Security patterns that must be preserved
- Input validation and sanitization
```

### 2.4 Check Test Coverage
```
@test-coverage-enforcer Analyze test coverage for [TARGET]:
- What tests exist?
- What's the coverage percentage?
- What's NOT covered that should be?
```

### 2.5 Document Current Behavior
Before any changes, document:
```bash
# Run existing tests to capture current behavior
[TEST_COMMAND] [TARGET_TESTS] 2>&1 | tee /tmp/pre-refactor-tests.log

# Note the test count and status
echo "Pre-refactor test status captured"
```

**Output**: Comprehensive analysis of current state.

---

## PHASE 3: CREATE REFACTORING PLAN
**Purpose**: Design the refactoring strategy before coding

### 3.1 Identify Refactoring Patterns
Based on analysis, identify applicable patterns:

| Pattern | When to Use |
|---------|-------------|
| Extract Method/Function | Long functions, repeated code |
| Extract Class/Module | Class doing too much |
| Inline | Over-abstraction, unnecessary indirection |
| Rename | Unclear naming |
| Move | Wrong location/module |
| Replace Conditional with Polymorphism | Complex switch/if chains |
| Introduce Parameter Object | Too many parameters |
| Replace Magic Numbers | Hardcoded values |
| Remove Dead Code | Unused code paths |
| Simplify Conditionals | Complex boolean logic |

### 3.2 Invoke Architect for Plan
```
@architect Create a refactoring plan for [TARGET]:
1. List specific changes in order of execution
2. Identify risks for each change
3. Define rollback strategy
4. Estimate impact on dependent code
```

### 3.3 Risk Assessment
For each planned change, assess:
- **Breaking change risk**: Could this break callers?
- **Behavior change risk**: Could this change output?
- **Performance risk**: Could this degrade performance?
- **Test coverage**: Do tests verify this change is safe?

### 3.4 User Confirmation
Present the plan:
```
REFACTORING PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: [FILE/MODULE]
Goal: [REFACTORING_GOAL]

Planned Changes:
1. [CHANGE_1] - Risk: [LOW/MED/HIGH]
2. [CHANGE_2] - Risk: [LOW/MED/HIGH]
...

Tests to verify: [TEST_COUNT] existing tests

Proceed? (yes/no/modify)
```

**Output**: Approved refactoring plan.

---

## PHASE 4: ENSURE TEST COVERAGE
**Purpose**: Cannot refactor safely without tests

### 4.1 Check Existing Coverage
```bash
# Run coverage analysis
[COVERAGE_COMMAND] 2>&1 | tee /tmp/coverage-report.log
```

### 4.2 Invoke Tester for Missing Tests
If coverage is insufficient:
```
@tester The following code paths in [TARGET] lack test coverage:
[UNCOVERED_PATHS]

Write tests that:
1. Capture current behavior (characterization tests)
2. Cover edge cases
3. Test error handling
4. Will detect if refactoring breaks something
```

### 4.3 Write Characterization Tests
For code without tests, create tests that capture current behavior:
```
@tester Write characterization tests for [TARGET]:
- Don't assume the code is correct
- Just capture what it currently does
- These tests will alert us if behavior changes
```

### 4.4 Verify Tests Pass
```bash
# All tests must pass before refactoring
[TEST_COMMAND]
```

**STOP if tests fail** - fix tests first, then refactor.

**Output**: Adequate test coverage confirmed.

---

## PHASE 5: EXECUTE REFACTORING
**Purpose**: Make the changes incrementally

### 5.1 Incremental Changes
Execute each planned change ONE AT A TIME:

```
For each change in plan:
  1. Make the change
  2. Run tests immediately
  3. If tests fail → revert and reassess
  4. If tests pass → commit this atomic change
  5. Move to next change
```

### 5.2 Small Commits
After each successful atomic refactoring:
```bash
# Stage the change
git add [CHANGED_FILES]

# Commit with descriptive message
git commit -m "refactor: [SPECIFIC_CHANGE]"
```

### 5.3 Invoke Reviewer After Each Change
```
@reviewer Review this refactoring change:
- Does it preserve behavior?
- Does it improve the code?
- Are there any issues?
```

### 5.4 Handle Failures
If tests fail after a change:
```bash
# Revert the change
git checkout -- [CHANGED_FILES]

# Or if committed
git revert HEAD
```

Then reassess the approach.

**Output**: All refactoring changes applied and tested.

---

## PHASE 6: VALIDATE REFACTORING
**Purpose**: Ensure refactoring was successful

### 6.1 Run Full Test Suite
```bash
[TEST_COMMAND] 2>&1 | tee /tmp/post-refactor-tests.log
```

### 6.2 Compare Test Results
```bash
# Ensure same tests pass
diff /tmp/pre-refactor-tests.log /tmp/post-refactor-tests.log || echo "Test output changed - investigate"
```

### 6.3 Invoke All Quality Agents
```
@reviewer Final review of all refactored code

@security-scanner Verify no security regressions

@performance-analyzer Compare performance before/after

@hallucination-checker Verify all code is real and functional
```

### 6.4 Run Linting
```bash
[LINT_COMMAND] --fix
```

### 6.5 Type Checking (if applicable)
```bash
# TypeScript
npx tsc --noEmit

# Python
mypy [TARGET]
```

**Output**: All validations passed.

---

## PHASE 7: DOCUMENTATION
**Purpose**: Update docs to reflect changes

### 7.1 Update Code Comments
Review and update:
- Function/method docstrings
- Inline comments explaining complex logic
- TODO/FIXME cleanup

### 7.2 Update External Docs
If public APIs changed:
```bash
# Check for doc updates needed
bash .claude/scripts/post-write-validate.sh
```

### 7.3 Save Learnings to Memory
```bash
# Record what we learned
bash .claude/scripts/save-memory.sh patterns "refactoring" "[PATTERN_APPLIED]: [DESCRIPTION]"
bash .claude/scripts/save-memory.sh decisions "refactoring" "Refactored [TARGET] using [APPROACH] because [REASON]"
```

**Output**: Documentation updated.

---

## PHASE 8: SANITIZE & COMMIT
**Purpose**: Final cleanup and commit

### 8.1 Pre-commit Sanitization
```bash
bash .claude/scripts/pre-commit-sanitize.sh
```

### 8.2 Final Validation
```bash
bash .claude/scripts/validate-all.sh
```

### 8.3 Create Summary Commit (if not done incrementally)
```bash
git add -A
git commit -m "refactor: [SUMMARY_OF_CHANGES]

- [CHANGE_1]
- [CHANGE_2]
- [CHANGE_3]

Improves: [GOAL_ACHIEVED]
Tests: All passing"
```

---

## PHASE 9: COMPLETION REPORT

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                         REFACTORING COMPLETE                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

TARGET: [FILE/MODULE]
GOAL: [REFACTORING_GOAL]

CHANGES MADE:
  ✓ [CHANGE_1]
  ✓ [CHANGE_2]
  ✓ [CHANGE_3]

METRICS:
  Lines changed: [+X / -Y]
  Complexity: [BEFORE] → [AFTER]
  Test coverage: [BEFORE]% → [AFTER]%

VALIDATIONS:
  ✓ All tests passing ([N] tests)
  ✓ Linting clean
  ✓ Type checking passed
  ✓ Security scan clear
  ✓ No behavior changes detected

COMMITS: [N] atomic commits created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## CRITICAL RULES

1. **Tests first** - Never refactor without test coverage
2. **Incremental changes** - One refactoring at a time, test after each
3. **Preserve behavior** - Refactoring changes structure, NOT functionality
4. **Revert on failure** - If tests break, undo immediately
5. **Document decisions** - Save learnings to memory
6. **Use all agents** - Architect, reviewer, security, performance, tester
7. **No shortcuts** - Every phase matters for safe refactoring

---

## COMMON REFACTORING GOALS

| Goal | Approach |
|------|----------|
| "Make it readable" | Rename, extract methods, simplify conditionals |
| "Make it faster" | Profile first, optimize hot paths, consider algorithms |
| "Make it testable" | Dependency injection, extract interfaces, reduce coupling |
| "Remove duplication" | Extract shared code, create utilities, DRY |
| "Reduce complexity" | Split large functions, simplify conditionals, early returns |
| "Modernize" | Update patterns, use new language features, update deps |
| "Prepare for feature X" | Extract extension points, add interfaces, modularize |
