---
description: Run project tests. Usage: /test [pattern] [--coverage] [--watch]
---

$ARGUMENTS

# TEST - Run Project Tests

Automatically detect and run the project's test suite.

## Detection Strategy

```bash
# Detect test runner
if [ -f "package.json" ]; then
    if grep -q '"test"' package.json; then
        TEST_CMD="npm test"
    elif grep -q '"vitest"' package.json; then
        TEST_CMD="npx vitest"
    elif grep -q '"jest"' package.json; then
        TEST_CMD="npx jest"
    fi
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] || [ -d "tests" ]; then
    TEST_CMD="pytest"
elif [ -f "Cargo.toml" ]; then
    TEST_CMD="cargo test"
elif [ -f "go.mod" ]; then
    TEST_CMD="go test ./..."
elif [ -f "Makefile" ] && grep -q "^test:" Makefile; then
    TEST_CMD="make test"
fi
```

## Run Tests

Based on arguments:

### Basic Run
```bash
$TEST_CMD
```

### With Pattern Filter
```bash
# If $ARGUMENTS contains a pattern
$TEST_CMD -k "$ARGUMENTS"  # pytest
$TEST_CMD --grep "$ARGUMENTS"  # jest
$TEST_CMD -run "$ARGUMENTS"  # go
```

### With Coverage
```bash
# If --coverage in $ARGUMENTS
pytest --cov=. --cov-report=term-missing
npm test -- --coverage
go test -cover ./...
```

### Watch Mode
```bash
# If --watch in $ARGUMENTS
pytest-watch
npm test -- --watch
cargo watch -x test
```

## Output Format

```markdown
## Test Results

### Summary
- **Total**: X tests
- **Passed**: Y ✓
- **Failed**: Z ✗
- **Skipped**: W ⊘
- **Duration**: N.NNs

### Failed Tests
| Test | Error |
|------|-------|
| test_name | AssertionError: ... |

### Coverage (if requested)
| File | Coverage |
|------|----------|
| src/main.py | 85% |
| src/utils.py | 92% |

**Total Coverage**: XX%
```

## On Failure

If tests fail:
1. Show failed test details
2. Offer to investigate: "Want me to look at the failing tests?"
3. If obvious fix, suggest it

## Save Results

```bash
# Record test run in memory
bash .claude/scripts/save-memory.sh project-learnings "test-run" "$(date): X passed, Y failed"
```
