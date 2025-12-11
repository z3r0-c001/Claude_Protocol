---
name: quality-audit
description: "Verification scripts for quality control. Use quality-control skill for full functionality."
---

# Quality Audit Scripts

This directory contains verification scripts used by the `quality-control` skill.

## Redirect

For full quality control functionality, use the **quality-control** skill instead.
This directory only contains the verification helper scripts.

## Verification Scripts

Located in `verification-scripts/`:

### npm-verify.sh
Verify NPM package exists:
```bash
./verification-scripts/npm-verify.sh <package-name>
```

### pip-verify.sh
Verify PyPI package exists:
```bash
./verification-scripts/pip-verify.sh <package-name>
```

### import-check.py
Check Python imports are valid:
```bash
./verification-scripts/import-check.py <file.py>
```

### path-check.sh
Verify file paths exist:
```bash
echo "path/to/file" | ./verification-scripts/path-check.sh
```

### verify-all.sh
Run all verification checks on a directory:
```bash
./verification-scripts/verify-all.sh [directory]
```

## Usage

These scripts are called by the quality-control skill and PreToolUse hooks.
They can also be run directly for manual verification.
