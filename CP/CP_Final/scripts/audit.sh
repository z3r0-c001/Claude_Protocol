#!/bin/bash
# Run full quality audit
set -e

echo "=== Quality Audit ==="

ERRORS=0

# Check for placeholders
echo "Checking for placeholders..."
if grep -rn --include="*.ts" --include="*.js" --include="*.py" -E '// \.\.\.|# \.\.\.|TODO|FIXME' . 2>/dev/null | grep -v node_modules; then
    echo "WARNING: Placeholders found"
    ((ERRORS++))
fi

# Check syntax
echo "Checking syntax..."
for f in $(find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null); do
    python3 -m py_compile "$f" 2>/dev/null || { echo "Syntax error: $f"; ((ERRORS++)); }
done

# Run tests if available
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo "Running tests..."
    npm test || ((ERRORS++))
fi

echo ""
[ "$ERRORS" -gt 0 ] && echo "AUDIT: FAIL ($ERRORS issues)" && exit 1
echo "AUDIT: PASS"
