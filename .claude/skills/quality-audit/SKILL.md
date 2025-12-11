---
name: quality-audit
description: "Comprehensive audit combining laziness detection and hallucination checking. Use for code review, task completion verification, and output validation. Triggered by Stop, PostToolUse, and SubagentStop hooks."
---

# Quality Audit Skill

This skill coordinates laziness-destroyer and hallucination-checker agents for comprehensive output validation.

## When to Use

- After writing/editing code
- After subagent completes task
- Before claiming task completion
- During code review

## Audit Process

### Phase 1: Laziness Detection

Run `laziness-destroyer` agent to check:

1. **Action vs Suggestion**
   - No "You could..." when action expected
   - No "Consider..." without implementation
   - No delegation back to user

2. **Completeness**
   - No `// ...` placeholders
   - No `# TODO` markers
   - No `pass` without justification
   - No partial implementations

3. **Scope Integrity**
   - All requested items addressed
   - No silent scope reduction
   - No "for brevity" shortcuts

4. **Verification**
   - Code compiles
   - Tests pass
   - Linting passes

### Phase 2: Hallucination Check

Run `hallucination-checker` agent to verify:

1. **Packages**
   - NPM packages exist: `npm view <pkg>`
   - PyPI packages exist: `pip index versions <pkg>`
   - Cargo crates exist: `cargo search <crate>`

2. **APIs**
   - Methods exist in documentation
   - Signatures are correct
   - Version compatibility confirmed

3. **Paths**
   - File paths resolve
   - Directory structure correct
   - No made-up paths

4. **Commands**
   - CLI commands exist
   - Flags are valid
   - Syntax is correct

5. **Tools**
   - Claude tools are valid
   - Skills exist in project
   - Agent names correct

## Verification Scripts

### npm-verify.sh
```bash
#!/bin/bash
# Verify NPM package exists
npm view "$1" version 2>/dev/null && echo "FOUND" || echo "NOT_FOUND"
```

### pip-verify.sh
```bash
#!/bin/bash
# Verify PyPI package exists
pip index versions "$1" 2>/dev/null && echo "FOUND" || echo "NOT_FOUND"
```

### import-check.py
```python
#!/usr/bin/env python3
# Check if Python imports are valid
import sys
import ast

def check_imports(file_path):
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split('.')[0])
    
    return imports

if __name__ == "__main__":
    print(check_imports(sys.argv[1]))
```

### path-check.sh
```bash
#!/bin/bash
# Verify file paths exist
while read -r path; do
    [ -e "$path" ] && echo "EXISTS: $path" || echo "MISSING: $path"
done
```

## Combined Assessment

```json
{
  "audit_status": "PASS|WARN|FAIL",
  "laziness": {
    "score": 0.95,
    "issues": 0,
    "verified": true
  },
  "hallucinations": {
    "checked": 15,
    "found": 0,
    "verified_items": ["react", "lodash", "fs.readFileSync"]
  },
  "approval_status": "APPROVED|NEEDS_FIXES|REJECTED",
  "required_fixes": []
}
```

## Agents Used

- `laziness-destroyer`: Completeness enforcement
- `hallucination-checker`: Reality verification

## Files

- `verification-scripts/npm-verify.sh`
- `verification-scripts/pip-verify.sh`
- `verification-scripts/import-check.py`
- `verification-scripts/path-check.sh`
- `verification-scripts/verify-all.sh`
