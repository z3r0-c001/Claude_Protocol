---
name: test-coverage
description: "Analyze test coverage, identify gaps, enforce thresholds, and generate test recommendations. Use before merging PRs, after writing features, or when coverage audit requested."
---

# Test Coverage Skill

This skill provides test coverage analysis and gap identification.

## When to Use

- Before merging pull requests
- After writing new features
- When coverage audit requested
- During code review
- When test failures occur

## Coverage Analysis

### Generate Reports

**JavaScript/TypeScript (Jest):**
```bash
npx jest --coverage --coverageReporters=json-summary
cat coverage/coverage-summary.json
```

**Python (pytest):**
```bash
pytest --cov=. --cov-report=json
cat coverage.json
```

**Go:**
```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out
```

### Thresholds

**Minimum Requirements:**
- Line coverage: 80%
- Branch coverage: 75%
- Function coverage: 85%

**Critical Path (100% required):**
- Authentication
- Authorization
- Payment processing
- Data validation

## Gap Detection

### Missing Test Files

```bash
# Find source files without tests
find src -name "*.ts" -not -name "*.test.ts" -not -name "*.spec.ts" | while read f; do
  test_file="${f%.ts}.test.ts"
  [ ! -f "$test_file" ] && echo "Missing: $test_file"
done
```

### Uncovered Functions

```bash
# Parse coverage JSON for zero-coverage functions
jq '.[] | select(.functions.pct < 100) | .path' coverage-summary.json
```

### Missing Edge Cases

Common gaps to check:
- Empty inputs
- Null/undefined handling
- Boundary values
- Error conditions
- Timeout scenarios

## Test Quality Checks

### Weak Assertions

```bash
# Find weak assertions
grep -rn --include="*.test.ts" --include="*.test.js" \
  -E 'toBeDefined\(\)|toBeTruthy\(\)|toBeFalsy\(\)' .
```

### Test Interdependence

```bash
# Find shared state between tests
grep -rn --include="*.test.ts" --include="*.test.js" \
  -E 'beforeAll|afterAll' . | grep -v 'beforeEach\|afterEach'
```

## Output Format

```json
{
  "coverage": {
    "line": 78.5,
    "branch": 72.3,
    "function": 82.1,
    "statement": 79.2
  },
  "thresholds_met": false,
  "gaps": [
    {
      "file": "src/services/payment.ts",
      "type": "uncovered_branch",
      "line": 45,
      "description": "Error handling branch not tested",
      "priority": "HIGH",
      "suggested_test": "Test declined card scenario"
    }
  ],
  "quality_issues": [
    {
      "file": "test/auth.test.ts",
      "issue": "weak_assertion",
      "line": 23,
      "current": "expect(user).toBeDefined()",
      "recommended": "expect(user).toMatchObject({...})"
    }
  ],
  "recommendations": []
}
```

## Integration

Integrates with:
- `test-coverage-enforcer` agent for detailed analysis
- CI/CD pipelines for coverage gates
- PR checks for coverage requirements

## Notes

Analysis commands are documented inline above. Claude executes these directly.
No external scripts required - all logic is self-contained in this skill.
