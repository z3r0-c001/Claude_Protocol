---
description: Analyze test coverage and identify gaps
---
$ARGUMENTS

Run test coverage analysis:

1. **Generate Coverage Report**: Run:
   - Jest with coverage for JS/TS
   - Pytest with coverage for Python
   - Go test with coverage for Go

2. **Threshold Check**: Verify:
   - Line coverage ≥ 80%
   - Branch coverage ≥ 75%
   - Function coverage ≥ 85%
   - Critical paths = 100%

3. **Gap Identification**: Find:
   - Untested files
   - Uncovered functions
   - Missing branch coverage
   - Untested error paths

4. **Quality Check**: Identify:
   - Weak assertions
   - Test interdependence
   - Missing edge cases
   - Flaky test patterns

**Arguments:**
- No arguments: Analyze current directory
- `--path <dir>`: Analyze specific directory
- `--threshold <pct>`: Set custom threshold
- `--strict`: Fail on any gap

**Output:**

```
## Test Coverage Report

### Coverage Summary
- Lines: X% (threshold: 80%)
- Branches: Y% (threshold: 75%)
- Functions: Z% (threshold: 85%)
- Status: PASS/FAIL

### Critical Path Coverage
[List of critical paths with coverage status]

### Gaps Identified
[Files/functions with insufficient coverage]

### Test Quality Issues
[Weak assertions, interdependence, etc.]

### Recommended Tests
1. [Test to add for highest impact]
2. [Additional test recommendations]
```
