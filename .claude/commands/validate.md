---
description: Run full validation suite on Claude protocol files and project code
---

# Validation Suite

Run comprehensive validation on the project.

## Checks to Perform

### 1. Syntax Validation
- Validate all JSON files (settings.json, skill-rules.json, etc.)
- Validate YAML files
- Check shell script syntax (bash -n)
- Check Python syntax (py_compile)

### 2. Completeness Check
Run laziness-check.sh to detect:
- Placeholder code
- TODO/FIXME markers
- Stub implementations
- Delegation phrases

### 3. Import/Package Verification
Check that referenced packages exist:
- npm packages in package.json
- pip packages in requirements.txt
- Imported modules resolve

### 4. Hook Validation
Verify all hooks:
- Scripts exist at specified paths
- Scripts are executable
- Scripts return valid JSON

### 5. Memory Integrity
Check memory files:
- Valid JSON format
- Required categories exist
- No corrupted entries

## Output

For each check, report:
- Status: PASS, WARN, FAIL
- Details of any issues
- Suggestions for fixes

## Summary

At the end, provide:
- Total checks run
- Pass/fail counts
- Critical issues requiring attention

---

Begin by checking the protocol directory structure and then run each validation check.
