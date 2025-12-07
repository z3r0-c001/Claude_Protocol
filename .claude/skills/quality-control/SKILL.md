---
name: quality-control
description: >
  Automated quality control for all generated code.
  Enforces completeness, correctness, and best practices.
  Triggers on: verify, fact-check, validate, is this correct, double-check, ensure quality.
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
- No placeholder comments (`// ...`, `# ...`, `/* ... */`)
- No TODO/FIXME markers in new code
- No stub implementations (`pass`, `raise NotImplementedError`)
- No delegation phrases ("you could...", "you'll need to...")

### 2. Correctness
- All imports/packages exist and are real
- API methods match actual documentation
- File paths resolve correctly
- CLI flags are valid

### 3. Syntax
- All files pass language-specific syntax checks
- JSON/YAML files are valid
- Shell scripts pass shellcheck/bash -n

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

### Manual (`/validate`)
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

## Commands

```bash
# Run full validation
/validate

# Run specific checks
/validate --syntax
/validate --imports
/validate --security
```

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
- [ ] Did I implement everything asked?
- [ ] Are all packages/imports real?
- [ ] Did I verify API signatures?
- [ ] Is there any placeholder code?
- [ ] Would this pass a code review?
