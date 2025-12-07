#!/bin/bash
# Audit script - comprehensive code quality audit
# Combines laziness, hallucination, and security checks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$PROJECT_DIR/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"

TARGET="${1:-.}"
OUTPUT_MODE="${2:-human}"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Code Quality Audit${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

ISSUES=0

# 1. Laziness Check
echo -e "${BLUE}Running laziness check...${NC}"
if [ -f "$HOOKS_DIR/laziness-check.sh" ]; then
  LAZINESS_RESULT=$("$HOOKS_DIR/laziness-check.sh" "$TARGET" json 2>/dev/null || echo '{"issue_count":0}')
  LAZINESS_COUNT=$(echo "$LAZINESS_RESULT" | grep -o '"issue_count":[0-9]*' | grep -o '[0-9]*' || echo "0")

  if [ "$LAZINESS_COUNT" -gt 0 ]; then
    echo -e "${RED}✗${NC} Found $LAZINESS_COUNT laziness issues"
    ISSUES=$((ISSUES + LAZINESS_COUNT))
  else
    echo -e "${GREEN}✓${NC} No laziness issues found"
  fi
else
  echo -e "${YELLOW}⚠${NC} Laziness check script not found"
fi

echo ""

# 2. Completeness Check
echo -e "${BLUE}Running completeness check...${NC}"
if [ -f "$HOOKS_DIR/completeness-check.sh" ]; then
  # Check staged or modified files
  INCOMPLETE=0
  for file in $(find "$TARGET" -type f \( -name "*.ts" -o -name "*.js" -o -name "*.py" \) 2>/dev/null | head -50); do
    RESULT=$("$HOOKS_DIR/completeness-check.sh" "$(cat "$file")" "$file" json 2>/dev/null || echo '{}')
    if echo "$RESULT" | grep -q '"decision":"block"'; then
      ((INCOMPLETE++))
    fi
  done

  if [ "$INCOMPLETE" -gt 0 ]; then
    echo -e "${RED}✗${NC} Found $INCOMPLETE files with incomplete code"
    ISSUES=$((ISSUES + INCOMPLETE))
  else
    echo -e "${GREEN}✓${NC} All checked files are complete"
  fi
else
  echo -e "${YELLOW}⚠${NC} Completeness check script not found"
fi

echo ""

# 3. Security Patterns Check
echo -e "${BLUE}Checking for security patterns...${NC}"

# Check for hardcoded secrets
SECRET_PATTERNS=(
  "password.*=.*['\"][^'\"]+['\"]"
  "api[_-]?key.*=.*['\"][^'\"]+['\"]"
  "secret.*=.*['\"][^'\"]+['\"]"
  "token.*=.*['\"][^'\"]+['\"]"
)

SECRET_COUNT=0
for pattern in "${SECRET_PATTERNS[@]}"; do
  COUNT=$(grep -riE "$pattern" "$TARGET" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | grep -v "node_modules" | grep -v ".git" | wc -l || echo "0")
  SECRET_COUNT=$((SECRET_COUNT + COUNT))
done

if [ "$SECRET_COUNT" -gt 0 ]; then
  echo -e "${RED}✗${NC} Found $SECRET_COUNT potential hardcoded secrets"
  ISSUES=$((ISSUES + SECRET_COUNT))
else
  echo -e "${GREEN}✓${NC} No obvious hardcoded secrets found"
fi

echo ""

# 4. TODO/FIXME Count
echo -e "${BLUE}Counting TODO/FIXME markers...${NC}"
TODO_COUNT=$(grep -riE "TODO|FIXME" "$TARGET" --include="*.ts" --include="*.js" --include="*.py" 2>/dev/null | grep -v "node_modules" | grep -v ".git" | wc -l || echo "0")

if [ "$TODO_COUNT" -gt 0 ]; then
  echo -e "${YELLOW}⚠${NC} Found $TODO_COUNT TODO/FIXME markers"
else
  echo -e "${GREEN}✓${NC} No TODO/FIXME markers found"
fi

echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Audit Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$ISSUES" -eq 0 ]; then
  echo -e "${GREEN}✓ All checks passed - code quality is good${NC}"
  exit 0
else
  echo -e "${RED}✗ Found $ISSUES total issues that need attention${NC}"
  exit 1
fi
