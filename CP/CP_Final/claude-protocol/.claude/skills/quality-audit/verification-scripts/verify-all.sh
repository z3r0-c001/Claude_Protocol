#!/bin/bash
# Comprehensive verification script
# Usage: ./verify-all.sh [directory]

set -e

DIR="${1:-.}"
SCRIPT_DIR="$(dirname "$0")"
ERRORS=0

echo "=== Quality Audit: $DIR ==="
echo ""

# 1. Check for placeholder patterns
echo "--- Checking for placeholders ---"
placeholders=$(grep -rn --include="*.ts" --include="*.js" --include="*.py" --include="*.go" --include="*.rs" \
    -E '(// *\.\.\.)|(/\* *\.\.\. *\*/)|# *\.\.\.|TODO|FIXME|pass$|return null;?\s*(//|$)|throw new Error\(['\''"]Not implemented' \
    "$DIR" 2>/dev/null || true)

if [ -n "$placeholders" ]; then
    echo "FOUND PLACEHOLDERS:"
    echo "$placeholders"
    ((ERRORS++))
else
    echo "No placeholders found ✓"
fi
echo ""

# 2. Check Python imports
echo "--- Checking Python imports ---"
py_files=$(find "$DIR" -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null || true)
if [ -n "$py_files" ]; then
    for f in $py_files; do
        if ! python3 -m py_compile "$f" 2>/dev/null; then
            echo "SYNTAX ERROR: $f"
            ((ERRORS++))
        fi
    done
    echo "Python syntax check complete ✓"
else
    echo "No Python files found"
fi
echo ""

# 3. Check TypeScript/JavaScript
echo "--- Checking TypeScript/JavaScript ---"
if [ -f "$DIR/package.json" ]; then
    if [ -f "$DIR/tsconfig.json" ]; then
        # TypeScript project
        if command -v npx &>/dev/null; then
            if ! npx tsc --noEmit 2>/dev/null; then
                echo "TypeScript errors found"
                ((ERRORS++))
            else
                echo "TypeScript check passed ✓"
            fi
        else
            echo "npx not available, skipping TypeScript check"
        fi
    else
        # JavaScript project - check syntax with node
        js_files=$(find "$DIR" -name "*.js" -not -path "*/node_modules/*" 2>/dev/null || true)
        for f in $js_files; do
            if ! node --check "$f" 2>/dev/null; then
                echo "SYNTAX ERROR: $f"
                ((ERRORS++))
            fi
        done
        echo "JavaScript syntax check complete ✓"
    fi
else
    echo "No package.json found"
fi
echo ""

# 4. Check for missing dependencies
echo "--- Checking dependencies ---"
if [ -f "$DIR/package.json" ]; then
    if [ ! -d "$DIR/node_modules" ]; then
        echo "WARNING: node_modules not found. Run npm install."
    else
        echo "node_modules present ✓"
    fi
fi

if [ -f "$DIR/requirements.txt" ]; then
    echo "Python requirements.txt found"
    if command -v pip &>/dev/null; then
        missing=$(pip freeze 2>/dev/null | grep -v "^-e" | cut -d= -f1 | sort > /tmp/installed_pkgs.txt && \
            grep -v "^#" "$DIR/requirements.txt" | cut -d= -f1 | cut -d'>' -f1 | cut -d'<' -f1 | sort | \
            comm -23 - /tmp/installed_pkgs.txt 2>/dev/null || true)
        if [ -n "$missing" ]; then
            echo "Missing packages: $missing"
        else
            echo "All Python packages installed ✓"
        fi
    fi
fi
echo ""

# 5. Check file references
echo "--- Checking file references ---"
# Extract file paths from imports and check they exist
imports=$(grep -rh --include="*.ts" --include="*.js" \
    -E "from ['\"]\..*['\"]|require\(['\"]\..*['\"]\)" "$DIR" 2>/dev/null | \
    sed -E "s/.*from ['\"]([^'\"]+)['\"].*/\1/; s/.*require\(['\"]([^'\"]+)['\"]\).*/\1/" | \
    grep "^\." | sort -u || true)

for imp in $imports; do
    # Try common extensions
    base="${imp#./}"
    found=false
    for ext in "" ".ts" ".tsx" ".js" ".jsx" "/index.ts" "/index.js"; do
        if [ -f "$DIR/$base$ext" ]; then
            found=true
            break
        fi
    done
    if ! $found; then
        echo "MISSING: $imp"
        ((ERRORS++))
    fi
done
echo "File reference check complete ✓"
echo ""

# Summary
echo "=== AUDIT COMPLETE ==="
if [ "$ERRORS" -gt 0 ]; then
    echo "RESULT: FAIL ($ERRORS issues found)"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi
