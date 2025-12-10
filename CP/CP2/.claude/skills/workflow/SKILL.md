---
name: workflow
description: "Standard development workflows. Use PROACTIVELY for any multi-step task. Triggers on: implement, build, create, develop, fix, refactor."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Task, Think
---

# Development Workflow Skill

Standard workflows for reliable, high-quality development.

## Primary Workflow: Explore → Plan → Code → Commit

### 1. EXPLORE
Before writing any code:
```
- Read relevant files (don't guess contents)
- Understand existing patterns
- Check for related tests
- Review recent changes (git log)
- Load memory for context
```

Commands:
```bash
# Load project memory
bash .claude/scripts/load-memory.sh

# Explore codebase
find . -name "*.py" -o -name "*.ts" | head -20
grep -r "pattern" --include="*.py" .
```

### 2. PLAN
For complex tasks, use thinking:
- `think` - Basic planning
- `think hard` - Detailed design
- `ultrathink` - Architecture decisions

Output a plan before coding:
```markdown
## Plan: [Task Name]

### Understanding
- [What the task requires]
- [Relevant files found]

### Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Risks
- [Potential issues]

### Tests Needed
- [Test cases to write]
```

### 3. CODE
Follow these principles:
- **No placeholders** - Complete all code
- **No TODOs** - Implement everything
- **Parallel tools** - Call multiple tools at once when independent
- **Error handling** - Include from the start
- **Tests** - Write alongside code

### 4. SANITIZE (Before Any Commit)
**ALWAYS run before committing:**
```bash
# Full sanitization check
bash .claude/scripts/pre-commit-sanitize.sh
```

This checks for:
- Secrets & credentials (API keys, passwords, tokens)
- Unfinished code (TODO, FIXME, placeholders)
- Dangerous patterns (SQL injection, eval, etc.)
- Sensitive files (.env, .pem, keys)
- Large files (>500KB)
- Merge conflict markers

**If sanitization fails → FIX BEFORE COMMITTING**

### 5. COMMIT
After sanitization passes:
```bash
# Verify code works
python3 -m py_compile *.py  # or equivalent
npm test
pytest

# Check for laziness
bash .claude/scripts/laziness-check.sh .

# Commit if all passes
git add -A
git commit -m "feat: [description]"
```

## Alternative Workflows

### TDD Workflow
```
1. Write failing test
2. Verify it fails
3. Implement minimum code
4. Verify test passes
5. Refactor if needed
6. Commit
```

### Bug Fix Workflow
```
1. Reproduce the bug
2. Write test that fails due to bug
3. Fix the bug
4. Verify test passes
5. Check for regressions
6. Commit with issue reference
```

### Refactoring Workflow
```
1. Ensure tests exist and pass
2. Make incremental changes
3. Run tests after each change
4. Commit frequently
5. Never refactor without tests
```

## Anti-Patterns to Avoid

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| Guessing file contents | Read the file first |
| Suggesting instead of doing | Implement directly |
| Partial implementations | Complete everything |
| Skipping tests | Write tests with code |
| Large uncommitted changes | Commit incrementally |

## Memory Integration

At each phase:
```bash
# Start: Load context
bash .claude/scripts/load-memory.sh

# During: Save learnings
bash .claude/scripts/save-memory.sh project-learnings "key" "value"

# End: Record decisions
bash .claude/scripts/save-memory.sh decisions "choice" "rationale"
```
