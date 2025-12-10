---
description: Run full quality audit (laziness check + hallucination check) on code or response
---
$ARGUMENTS

Run comprehensive quality audit on the specified content:

1. **Laziness Check**: Invoke the `laziness-destroyer` agent to verify:
   - No suggestions instead of implementations
   - No placeholders (// ..., # TODO, pass)
   - No premature stopping
   - No scope reduction
   - No delegation back to user
   - Verification actually performed

2. **Hallucination Check**: Invoke the `hallucination-checker` agent to verify:
   - All NPM packages exist (`npm view <pkg>`)
   - All PyPI packages exist (pip check)
   - All API methods exist with correct signatures
   - All file paths resolve
   - All CLI commands and flags are valid
   - All Claude tools referenced are valid

3. **Code Verification**: Run verification scripts:
   - Check for placeholder patterns in code
   - Verify imports compile
   - Check file references exist
   - Validate dependencies installed

**Output a combined audit report:**

```
## Quality Audit Report

### Laziness Score: X/100
- Suggestions vs Actions: PASS/FAIL
- Completeness: PASS/FAIL
- Scope Integrity: PASS/FAIL
- Verification: PASS/FAIL
- Issues: [list]

### Hallucination Count: X
- Packages checked: Y (Z hallucinated)
- APIs verified: Y (Z hallucinated)
- Paths checked: Y (Z missing)
- Commands verified: Y (Z invalid)

### Code Quality
- Placeholders found: X
- Import errors: Y
- Missing files: Z

### Overall Status: APPROVED/NEEDS_FIXES/REJECTED

### Required Fixes
1. [specific fix needed]
2. [specific fix needed]
```

If $ARGUMENTS is empty, audit the most recent code written in this conversation.
If $ARGUMENTS is a file path, audit that specific file.
If $ARGUMENTS is a directory, audit all code files in that directory.
