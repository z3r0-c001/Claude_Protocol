#!/bin/bash
# pre-commit-sanitize.sh - Run before any commit to catch dangerous content

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                    PRE-COMMIT SANITIZATION CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Get staged files (or all files if not in git context)
if git rev-parse --git-dir > /dev/null 2>&1; then
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || find . -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" | grep -v node_modules | grep -v __pycache__)
else
    STAGED_FILES=$(find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" \) | grep -v node_modules | grep -v __pycache__ | grep -v .git)
fi

if [ -z "$STAGED_FILES" ]; then
    echo -e "${GREEN}No files to check${NC}"
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 1: SECRETS AND CREDENTIALS
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 1: Secrets & Credentials"
echo "─────────────────────────────────────────────────────────────────────────────"

SECRET_PATTERNS=(
    # API Keys
    'api[_-]?key\s*[=:]\s*["\x27][a-zA-Z0-9]{16,}'
    'apikey\s*[=:]\s*["\x27][a-zA-Z0-9]{16,}'
    
    # AWS
    'AKIA[0-9A-Z]{16}'
    'aws[_-]?secret[_-]?access[_-]?key'
    
    # GitHub
    'ghp_[a-zA-Z0-9]{36}'
    'gho_[a-zA-Z0-9]{36}'
    'github[_-]?token'
    
    # Generic secrets
    'password\s*[=:]\s*["\x27][^\s"'\'']{8,}'
    'secret\s*[=:]\s*["\x27][a-zA-Z0-9]{16,}'
    'private[_-]?key'
    'BEGIN RSA PRIVATE KEY'
    'BEGIN OPENSSH PRIVATE KEY'
    'BEGIN PGP PRIVATE KEY'
    
    # Database
    'postgres://[^:]+:[^@]+@'
    'mysql://[^:]+:[^@]+@'
    'mongodb://[^:]+:[^@]+@'
    'redis://[^:]+:[^@]+@'
    
    # Tokens
    'bearer\s+[a-zA-Z0-9_-]{20,}'
    'token\s*[=:]\s*["\x27][a-zA-Z0-9_-]{20,}'
    
    # Stripe
    'sk_live_[a-zA-Z0-9]{24}'
    'rk_live_[a-zA-Z0-9]{24}'
    
    # Slack
    'xox[baprs]-[0-9]{10,}'
    
    # Twilio
    'SK[a-f0-9]{32}'
    
    # SendGrid
    'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}'
    
    # Hardcoded IPs (internal)
    '192\.168\.[0-9]{1,3}\.[0-9]{1,3}'
    '10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
)

for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -iEn "$pattern" "$file" 2>/dev/null | grep -v "example\|sample\|test\|mock\|fake\|dummy" | head -3; then
            echo -e "${RED}  ✗ BLOCKED: Potential secret in $file${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    done
done

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}  ✓ No secrets detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 2: LAZY/UNFINISHED CODE
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 2: Unfinished Code"
echo "─────────────────────────────────────────────────────────────────────────────"

LAZY_PATTERNS=(
    '# TODO'
    '// TODO'
    '# FIXME'
    '// FIXME'
    '# HACK'
    '// HACK'
    '# XXX'
    '// XXX'
    'NotImplementedError'
    'raise NotImplemented'
    'throw new Error.*not implemented'
    'panic!.*not implemented'
    'unimplemented!()'
    'todo!()'
    '\.\.\..*implement'
    'pass\s*#'
    '# implement'
    '// implement'
    'PLACEHOLDER'
    'CHANGEME'
    'REPLACE_ME'
    'YOUR_.*_HERE'
    '<YOUR_'
    '\.\.\. your code here'
    '# add .* here'
    '// add .* here'
)

LAZY_COUNT=0
for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    for pattern in "${LAZY_PATTERNS[@]}"; do
        matches=$(grep -iEn "$pattern" "$file" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo -e "${RED}  ✗ BLOCKED: Unfinished code in $file${NC}"
            echo "$matches" | head -3 | sed 's/^/      /'
            LAZY_COUNT=$((LAZY_COUNT + 1))
        fi
    done
done

if [ $LAZY_COUNT -gt 0 ]; then
    ERRORS=$((ERRORS + LAZY_COUNT))
else
    echo -e "${GREEN}  ✓ No unfinished code detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 3: DANGEROUS CODE PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 3: Dangerous Code Patterns"
echo "─────────────────────────────────────────────────────────────────────────────"

DANGEROUS_PATTERNS=(
    # SQL Injection
    'execute.*%s'
    'execute.*\$'
    'query.*\+.*\+.*query'
    'f"SELECT.*{.*}"'
    "f'SELECT.*{.*}'"
    
    # Command Injection
    'os\.system\s*\('
    'subprocess\.call\s*\(.*shell\s*=\s*True'
    'eval\s*\('
    'exec\s*\('
    'child_process\.exec\s*\('
    
    # XSS
    'innerHTML\s*='
    'dangerouslySetInnerHTML'
    'document\.write\s*\('
    '\$\(.*\)\.html\s*\('
    
    # Insecure
    'verify\s*=\s*False'
    'ssl\s*=\s*False'
    'insecure'
    'disable.*ssl'
    'allow_redirects\s*=\s*True.*verify\s*=\s*False'
    
    # Debug/Dev only
    'debugger;'
    'console\.log'
    'print\s*\(.*debug'
    'binding\.pry'
    'byebug'
    'import pdb'
    'breakpoint\(\)'
)

DANGEROUS_COUNT=0
for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    for pattern in "${DANGEROUS_PATTERNS[@]}"; do
        matches=$(grep -iEn "$pattern" "$file" 2>/dev/null || true)
        if [ -n "$matches" ]; then
            echo -e "${YELLOW}  ⚠ WARNING: Potentially dangerous pattern in $file${NC}"
            echo "$matches" | head -2 | sed 's/^/      /'
            WARNINGS=$((WARNINGS + 1))
        fi
    done
done

if [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}  ✓ No dangerous patterns detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 4: LARGE FILES
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 4: Large Files"
echo "─────────────────────────────────────────────────────────────────────────────"

MAX_SIZE_KB=500
LARGE_FILES=0
for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    size=$(du -k "$file" 2>/dev/null | cut -f1)
    if [ "$size" -gt "$MAX_SIZE_KB" ]; then
        echo -e "${YELLOW}  ⚠ WARNING: Large file ($size KB): $file${NC}"
        WARNINGS=$((WARNINGS + 1))
        LARGE_FILES=$((LARGE_FILES + 1))
    fi
done

if [ $LARGE_FILES -eq 0 ]; then
    echo -e "${GREEN}  ✓ No large files detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 5: SENSITIVE FILE TYPES
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 5: Sensitive Files"
echo "─────────────────────────────────────────────────────────────────────────────"

SENSITIVE_EXTENSIONS=(
    '.pem'
    '.key'
    '.p12'
    '.pfx'
    '.env'
    '.env.local'
    '.env.production'
    '.secrets'
    '.credentials'
    'id_rsa'
    'id_dsa'
    'id_ecdsa'
    'id_ed25519'
    '.htpasswd'
    '.netrc'
    '.npmrc'
    '.pypirc'
)

SENSITIVE_COUNT=0
for file in $STAGED_FILES; do
    for ext in "${SENSITIVE_EXTENSIONS[@]}"; do
        if [[ "$file" == *"$ext"* ]]; then
            echo -e "${RED}  ✗ BLOCKED: Sensitive file type: $file${NC}"
            ERRORS=$((ERRORS + 1))
            SENSITIVE_COUNT=$((SENSITIVE_COUNT + 1))
        fi
    done
done

if [ $SENSITIVE_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✓ No sensitive files detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 6: MERGE CONFLICTS
# ═══════════════════════════════════════════════════════════════════════════════
echo "▶ CHECK 6: Merge Conflicts"
echo "─────────────────────────────────────────────────────────────────────────────"

CONFLICT_COUNT=0
for file in $STAGED_FILES; do
    [ -f "$file" ] || continue
    if grep -En '^<{7}|^>{7}|^={7}' "$file" 2>/dev/null; then
        echo -e "${RED}  ✗ BLOCKED: Merge conflict markers in $file${NC}"
        ERRORS=$((ERRORS + 1))
        CONFLICT_COUNT=$((CONFLICT_COUNT + 1))
    fi
done

if [ $CONFLICT_COUNT -eq 0 ]; then
    echo -e "${GREEN}  ✓ No merge conflicts detected${NC}"
fi
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                           SANITIZATION RESULT"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "  Files checked: $(echo "$STAGED_FILES" | wc -w)"
echo "  Errors (blocking): $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}  ✗ COMMIT BLOCKED - Fix $ERRORS error(s) before committing${NC}"
    echo ""
    echo "  To bypass (NOT RECOMMENDED): git commit --no-verify"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}  ⚠ COMMIT ALLOWED WITH WARNINGS - Review $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${GREEN}  ✓ ALL CHECKS PASSED - Safe to commit${NC}"
    exit 0
fi
