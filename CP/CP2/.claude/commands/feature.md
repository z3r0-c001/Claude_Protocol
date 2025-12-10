---
description: Implement a new feature. Usage: /feature <feature description>
---

$ARGUMENTS

# FEATURE WORKFLOW

You are implementing a new feature. Follow this exact process:

## Phase 1: Understand

1. **Load context**
```bash
bash .claude/scripts/load-memory.sh
```

2. **Clarify requirements**
- What exactly should this feature do?
- What are the acceptance criteria?
- Are there edge cases to consider?

3. **Explore existing code**
```bash
# Find related patterns
grep -rn "similar_feature" --include="*.py" --include="*.ts" .
find . -name "*.py" -o -name "*.ts" | head -20
```

## Phase 2: Design (use `ultrathink` for complex features)

Output an architecture plan:
```markdown
## Feature Design: [Name]

### Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Architecture
[How it fits into existing system]

### Files to Create/Modify
| File | Action | Purpose |
|------|--------|---------|
| src/feature.ts | CREATE | Main implementation |
| src/feature.test.ts | CREATE | Tests |

### API/Interface
[Function signatures, endpoints, etc.]

### Dependencies
- [Any new packages needed]

### Edge Cases
- [Edge case 1]: [How handled]
- [Edge case 2]: [How handled]
```

## Phase 3: Implement

Follow TDD:
1. **Write tests first**
2. **Verify tests fail**
3. **Implement feature** - Complete, no placeholders
4. **Verify tests pass**
5. **Add integration tests if needed**

Rules:
- No `// TODO` comments
- No `pass` statements
- No placeholder code
- Complete error handling
- Complete documentation

## Phase 4: Verify

```bash
# Run all checks
bash .claude/scripts/laziness-check.sh .
bash .claude/scripts/hallucination-check.sh .

# Run tests
npm test  # or pytest, go test, etc.

# Lint
npm run lint  # or equivalent
```

## Phase 5: Sanitize & Commit

**ALWAYS sanitize before committing:**

```bash
# Run sanitization
bash .claude/scripts/pre-commit-sanitize.sh
```

If sanitization passes:
```bash
# Commit
git add -A
git commit -m "feat: [feature name]

- [bullet point 1]
- [bullet point 2]"
```

If sanitization fails:
- Fix all errors listed
- Re-run sanitization
- Only commit when PASS

## Memory

Save patterns learned:
```bash
bash .claude/scripts/save-memory.sh patterns "[pattern_name]" "[description]"
bash .claude/scripts/save-memory.sh decisions "[decision]" "[rationale]"
```

## Output

```markdown
## Feature Complete: [Name]

### Implemented
- [x] [Requirement 1]
- [x] [Requirement 2]

### Files Created/Modified
| File | Changes |
|------|---------|
| ... | ... |

### Tests
- Unit tests: X passing
- Integration tests: Y passing

### Usage
\`\`\`
[How to use the feature]
\`\`\`

### Commit
[commit hash]
```
