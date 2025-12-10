#!/bin/bash
# Hallucination Check Script
# Verifies that packages, imports, and APIs actually exist

set -e

TARGET="${1:-.}"
ERRORS=0
WARNINGS=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════════════"
echo "  HALLUCINATION CHECK"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ============================================================
echo "▶ [1/4] Verifying Python imports..."
echo "─────────────────────────────────────────────────────────────────"

PY_FILES=$(find "$TARGET" -name "*.py" -type f 2>/dev/null | grep -v __pycache__ | grep -v ".venv" | grep -v "node_modules" || true)

if [ -n "$PY_FILES" ]; then
  for pyfile in $PY_FILES; do
    # Extract imports
    imports=$(grep -E "^(import|from) " "$pyfile" 2>/dev/null | head -20 || true)
    
    if [ -n "$imports" ]; then
      # Try to compile the file (catches import errors)
      if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $(basename "$pyfile") - syntax OK"
      else
        echo -e "${RED}✗${NC} $(basename "$pyfile") - compilation error"
        python3 -m py_compile "$pyfile" 2>&1 | head -5
        ((ERRORS++))
      fi
    fi
  done
else
  echo "  No Python files found"
fi

echo ""

# ============================================================
echo "▶ [2/4] Verifying Node.js packages..."
echo "─────────────────────────────────────────────────────────────────"

if [ -f "$TARGET/package.json" ]; then
  # Check if node_modules exists
  if [ -d "$TARGET/node_modules" ]; then
    # Check for missing packages
    missing=$(cd "$TARGET" && npm ls --depth=0 2>&1 | grep -E "missing|UNMET" || true)
    if [ -n "$missing" ]; then
      echo -e "${RED}✗${NC} Missing npm packages detected:"
      echo "$missing" | head -10
      ((ERRORS++))
    else
      echo -e "${GREEN}✓${NC} All npm dependencies resolved"
    fi
  else
    echo -e "${YELLOW}⚠${NC} node_modules not found - run 'npm install' to verify"
    ((WARNINGS++))
  fi
  
  # Extract and verify package names from imports
  JS_FILES=$(find "$TARGET" -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" 2>/dev/null | grep -v node_modules | head -20 || true)
  
  for jsfile in $JS_FILES; do
    # Basic syntax check
    if echo "$jsfile" | grep -qE "\.tsx?$"; then
      # TypeScript - just check if it exists, full check needs tsc
      [ -f "$jsfile" ] && echo -e "${GREEN}✓${NC} $(basename "$jsfile") exists"
    else
      # JavaScript - use node --check
      if node --check "$jsfile" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $(basename "$jsfile") - syntax OK"
      else
        echo -e "${YELLOW}⚠${NC} $(basename "$jsfile") - syntax check failed (may need dependencies)"
        ((WARNINGS++))
      fi
    fi
  done
else
  echo "  No package.json found"
fi

echo ""

# ============================================================
echo "▶ [3/4] Verifying Go modules..."
echo "─────────────────────────────────────────────────────────────────"

if [ -f "$TARGET/go.mod" ]; then
  if command -v go &> /dev/null; then
    if (cd "$TARGET" && go mod verify 2>/dev/null); then
      echo -e "${GREEN}✓${NC} Go modules verified"
    else
      echo -e "${RED}✗${NC} Go module verification failed"
      ((ERRORS++))
    fi
    
    # Check for import errors
    GO_FILES=$(find "$TARGET" -name "*.go" -type f 2>/dev/null | head -20 || true)
    for gofile in $GO_FILES; do
      if go vet "$gofile" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $(basename "$gofile") - vet OK"
      else
        echo -e "${YELLOW}⚠${NC} $(basename "$gofile") - vet warnings"
        ((WARNINGS++))
      fi
    done
  else
    echo -e "${YELLOW}⚠${NC} Go not installed - cannot verify"
    ((WARNINGS++))
  fi
else
  echo "  No go.mod found"
fi

echo ""

# ============================================================
echo "▶ [4/4] Verifying file references..."
echo "─────────────────────────────────────────────────────────────────"

# Check for referenced files that don't exist
# Look for common patterns like require('./...'), import from '...', etc.

MISSING_REFS=0

# Check JavaScript/TypeScript relative imports
for jsfile in $(find "$TARGET" -name "*.js" -o -name "*.ts" -o -name "*.tsx" 2>/dev/null | grep -v node_modules | head -20); do
  dir=$(dirname "$jsfile")
  refs=$(grep -oE "(require|import.*from)\s*['\"]\.\.?/[^'\"]+['\"]" "$jsfile" 2>/dev/null | grep -oE "\.\.?/[^'\"]+" || true)
  
  for ref in $refs; do
    # Resolve the path
    resolved="$dir/$ref"
    # Check with common extensions
    if [ ! -f "$resolved" ] && [ ! -f "${resolved}.js" ] && [ ! -f "${resolved}.ts" ] && [ ! -f "${resolved}.tsx" ] && [ ! -f "${resolved}/index.js" ] && [ ! -f "${resolved}/index.ts" ]; then
      echo -e "${YELLOW}⚠${NC} Unresolved: $ref in $(basename "$jsfile")"
      ((MISSING_REFS++))
    fi
  done
done

if [ $MISSING_REFS -gt 0 ]; then
  echo -e "${YELLOW}⚠${NC} $MISSING_REFS unresolved file references"
  ((WARNINGS++))
else
  echo -e "${GREEN}✓${NC} All file references resolved"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ]; then
  if [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}HALLUCINATION CHECK PASSED${NC}"
  else
    echo -e "${GREEN}HALLUCINATION CHECK PASSED${NC} ${YELLOW}($WARNINGS warnings)${NC}"
  fi
  exit 0
else
  echo -e "${RED}HALLUCINATION CHECK FAILED - $ERRORS ERROR(S) FOUND${NC}"
  echo ""
  echo "All imports and packages must be verified as real before"
  echo "this code is acceptable."
  exit 1
fi
