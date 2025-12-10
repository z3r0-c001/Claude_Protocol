---
name: security-scanner
description: "Scan code for security vulnerabilities including injection, auth issues, data exposure, and dependency vulnerabilities. Use before deployments, PRs, or when security audit requested."
---

# Security Scanner Skill

This skill provides automated security vulnerability scanning.

## When to Use

- Before deploying to production
- When reviewing pull requests
- When security audit requested
- After adding new dependencies
- When handling user input

## Scan Categories

### 1. Injection Vulnerabilities

**SQL Injection:**
```bash
# Detect potential SQL injection
grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E 'execute\(.*\+|execute\(.*\$|execute\(.*f"|query\(.*\+' .
```

**Command Injection:**
```bash
# Detect potential command injection
grep -rn --include="*.py" \
  -E 'os\.system|subprocess.*shell=True|eval\(|exec\(' .
```

**XSS:**
```bash
# Detect potential XSS
grep -rn --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" \
  -E 'innerHTML|dangerouslySetInnerHTML|document\.write' .
```

### 2. Authentication Issues

```bash
# Detect hardcoded secrets
grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.env*" \
  -E 'password\s*=\s*["\x27]|api_key\s*=\s*["\x27]|secret\s*=\s*["\x27]|token\s*=\s*["\x27]' .
```

### 3. Dependency Vulnerabilities

**NPM:**
```bash
npm audit --json > security-report.json
```

**Python:**
```bash
pip-audit --format json > security-report.json
# or
safety check --json > security-report.json
```

### 4. Configuration Issues

```bash
# Check for debug mode
grep -rn -E 'DEBUG\s*=\s*True|debug:\s*true|NODE_ENV.*development' .

# Check for permissive CORS
grep -rn -E 'cors\(\*\)|Access-Control-Allow-Origin.*\*' .
```

## Scanning Process

1. Run pattern-based detection for each category
2. Run dependency audit
3. Check configuration files
4. Search for secrets
5. Generate report

## Output Format

```json
{
  "scan_date": "2025-01-01T00:00:00Z",
  "vulnerabilities": [
    {
      "id": "SEC-001",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "category": "injection|auth|exposure|dependency|config",
      "file": "path/to/file",
      "line": 45,
      "description": "Description of issue",
      "recommendation": "How to fix"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }
}
```

## Integration

Integrates with:
- `security-scanner` agent for detailed analysis
- PreToolUse hooks for dangerous command blocking
- CI/CD pipelines for automated scanning

## Files

- `scan-injections.sh`: Injection vulnerability scanner
- `scan-secrets.sh`: Hardcoded secrets scanner
- `scan-deps.sh`: Dependency vulnerability scanner
- `scan-config.sh`: Configuration issue scanner
