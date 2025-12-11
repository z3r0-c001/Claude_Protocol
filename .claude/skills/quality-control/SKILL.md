---
name: quality-control
description: >
  Unified quality control combining laziness detection and hallucination checking.
  Enforces completeness, correctness, and best practices.
  Triggered by Stop, PostToolUse, and SubagentStop hooks.
  Use PROACTIVELY on every code generation.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Quality Control Skill

## Overview

This skill enforces zero-tolerance quality gates on all generated code. It runs automatically on Stop hooks and can be invoked manually via `/validate`.

## Quality Gates

All code must pass these checks:

### 1. Completeness (Zero Tolerance)

Run laziness checks to verify:

**Action vs Suggestion**
- Blocks suggestion-only responses when action expected
- Blocks "consider adding" without implementation
- Blocks delegation back to user

**Code Completeness**
- Blocks placeholder comments (ellipsis in comments)
- Blocks TODO/FIXME markers in new code
- Blocks stub implementations (empty pass, NotImplementedError)
- Blocks partial implementations

**Scope Integrity**
- All requested items addressed
- No silent scope reduction
- No shortcuts

### 2. Correctness (Hallucination Prevention)

Verify all claims are real:

**Packages**
```bash
# NPM packages exist
npm view <pkg> version 2>/dev/null && echo "FOUND" || echo "NOT_FOUND"

# PyPI packages exist
pip index versions <pkg> 2>/dev/null && echo "FOUND" || echo "NOT_FOUND"
```

**APIs**
- Methods exist in documentation
- Signatures are correct
- Version compatibility confirmed

**Paths**
- File paths resolve
- Directory structure correct
- No made-up paths

**Commands**
- CLI commands exist
- Flags are valid
- Syntax is correct

### 3. Syntax

- All files pass language-specific syntax checks
- JSON/YAML files are valid
- Shell scripts pass `bash -n`
- Python files pass `python3 -m py_compile`

### 4. Security

- No hardcoded secrets
- No SQL injection vulnerabilities
- No XSS risks in user-facing code
- Protected paths not modified

## Validation Process

### Automatic (Stop Hook)

1. Laziness check runs on every response
2. Honesty check validates claims
3. If issues found, response is blocked

### Manual (/validate)

1. Full syntax validation
2. Import/package verification
3. API method checking
4. Security scan

## Severity Levels

| Level | Action | Examples |
|-------|--------|----------|
| CRITICAL | Block | Placeholder code, non-existent packages |
| MAJOR | Block if 2+ | Wrong API, invalid paths |
| MINOR | Warn | Style issues, missing comments |

## Integration with Agents

| Agent | Check |
|-------|-------|
| laziness-destroyer | Completeness |
| hallucination-checker | Correctness |
| security-scanner | Security |
| fact-checker | Accuracy |

## Enforcement

**Pass threshold: 100%**

No exceptions. If quality gates fail:
1. Response is blocked
2. Issues are listed
3. Fixes are required
4. Re-validation runs automatically

## Self-Check Questions

Before finalizing any code:
- Did I implement everything asked?
- Are all packages/imports real?
- Did I verify API signatures?
- Is there any placeholder code?
- Would this pass a code review?

## Verification Scripts

Located in `quality-audit/verification-scripts/`:
- `npm-verify.sh`: NPM package verification
- `pip-verify.sh`: PyPI package verification
- `import-check.py`: Python import validation
- `path-check.sh`: File path verification
- `verify-all.sh`: Run all verification checks
