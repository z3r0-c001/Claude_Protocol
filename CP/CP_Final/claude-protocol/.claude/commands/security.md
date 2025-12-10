---
description: Run security vulnerability scan on code
---
$ARGUMENTS

Run comprehensive security scan:

1. **Injection Scan**: Check for:
   - SQL injection vulnerabilities
   - Command injection
   - XSS vulnerabilities
   - Template injection

2. **Authentication Scan**: Check for:
   - Hardcoded credentials
   - Weak authentication patterns
   - Session management issues
   - JWT vulnerabilities

3. **Data Exposure Scan**: Check for:
   - Sensitive data in logs
   - PII exposure
   - Credentials in version control
   - Debug information leakage

4. **Dependency Scan**: Run:
   - `npm audit` for Node.js projects
   - `pip-audit` for Python projects
   - Check for known CVEs

5. **Configuration Scan**: Check for:
   - Debug mode in production
   - Permissive CORS
   - Missing security headers
   - Insecure defaults

**Arguments:**
- No arguments: Scan current directory
- `--path <dir>`: Scan specific directory
- `--deps-only`: Only scan dependencies
- `--quick`: Skip deep analysis

**Output:**

```
## Security Scan Report

### Summary
- Critical: X
- High: Y
- Medium: Z
- Low: W

### Vulnerabilities
[Detailed list with file, line, description, recommendation]

### Dependency Audit
[List of vulnerable packages with fix versions]

### Recommendations
1. [Priority fix]
2. [Additional hardening]
```
