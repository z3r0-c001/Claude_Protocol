#!/bin/bash
# Full validation suite for Claude Bootstrap Protocol
# Exit on any error
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           CLAUDE PROTOCOL VALIDATION SUITE                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to report pass/fail
check() {
  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} $1"
  else
    echo -e "  ${RED}✗${NC} $1"
    ((ERRORS++))
  fi
}

warn() {
  echo -e "  ${YELLOW}⚠${NC} $1"
  ((WARNINGS++))
}

# ============================================================
echo "▶ [1/6] STRUCTURE VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Required directories
[ -d "$CLAUDE_DIR" ] && check ".claude/ directory exists" || { echo -e "  ${RED}✗${NC} .claude/ directory missing"; ((ERRORS++)); }
[ -d "$CLAUDE_DIR/agents" ] && check ".claude/agents/ exists" || { echo -e "  ${RED}✗${NC} .claude/agents/ missing"; ((ERRORS++)); }
[ -d "$CLAUDE_DIR/skills" ] && check ".claude/skills/ exists" || { echo -e "  ${RED}✗${NC} .claude/skills/ missing"; ((ERRORS++)); }
[ -d "$CLAUDE_DIR/scripts" ] && check ".claude/scripts/ exists" || { echo -e "  ${RED}✗${NC} .claude/scripts/ missing"; ((ERRORS++)); }
[ -d "$CLAUDE_DIR/memory" ] && check ".claude/memory/ exists" || { echo -e "  ${RED}✗${NC} .claude/memory/ missing"; ((ERRORS++)); }

# Required files
[ -f "$CLAUDE_DIR/settings.json" ] && check "settings.json exists" || { echo -e "  ${RED}✗${NC} settings.json missing"; ((ERRORS++)); }

# CLAUDE.md (optional but recommended)
[ -f "$PROJECT_ROOT/CLAUDE.md" ] && check "CLAUDE.md exists" || warn "CLAUDE.md not found (recommended)"

echo ""

# ============================================================
echo "▶ [2/6] JSON VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Validate all JSON files
for json_file in $(find "$CLAUDE_DIR" -name "*.json" 2>/dev/null); do
  if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
    check "$(basename "$json_file") is valid JSON"
  else
    echo -e "  ${RED}✗${NC} $(basename "$json_file") has invalid JSON"
    ((ERRORS++))
  fi
done

echo ""

# ============================================================
echo "▶ [3/6] SCRIPT VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Check all shell scripts have valid syntax
for script in $(find "$CLAUDE_DIR/scripts" -name "*.sh" 2>/dev/null); do
  script_name=$(basename "$script")
  if bash -n "$script" 2>/dev/null; then
    check "$script_name has valid syntax"
  else
    echo -e "  ${RED}✗${NC} $script_name has syntax errors"
    ((ERRORS++))
  fi
done

# Check scripts are executable
for script in $(find "$CLAUDE_DIR/scripts" -name "*.sh" 2>/dev/null); do
  script_name=$(basename "$script")
  if [ -x "$script" ]; then
    check "$script_name is executable"
  else
    warn "$script_name is not executable (run: chmod +x $script)"
  fi
done

echo ""

# ============================================================
echo "▶ [4/6] AGENT VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Check agents have required frontmatter
REQUIRED_AGENTS=("laziness-destroyer" "hallucination-checker")

for agent in "${REQUIRED_AGENTS[@]}"; do
  agent_file="$CLAUDE_DIR/agents/$agent.md"
  if [ -f "$agent_file" ]; then
    check "$agent.md exists"
    # Check for frontmatter
    if head -1 "$agent_file" | grep -q "^---"; then
      check "$agent.md has frontmatter"
    else
      echo -e "  ${RED}✗${NC} $agent.md missing frontmatter"
      ((ERRORS++))
    fi
    # Check for required fields
    if grep -q "^name:" "$agent_file"; then
      check "$agent.md has name field"
    else
      warn "$agent.md missing name field"
    fi
    if grep -q "^description:" "$agent_file"; then
      check "$agent.md has description field"
    else
      warn "$agent.md missing description field"
    fi
  else
    echo -e "  ${RED}✗${NC} $agent.md NOT FOUND (CRITICAL)"
    ((ERRORS++))
  fi
done

# Check optional agents
OPTIONAL_AGENTS=("architect" "reviewer" "tester")
for agent in "${OPTIONAL_AGENTS[@]}"; do
  agent_file="$CLAUDE_DIR/agents/$agent.md"
  [ -f "$agent_file" ] && check "$agent.md exists (optional)" || warn "$agent.md not found (optional)"
done

echo ""

# ============================================================
echo "▶ [5/6] SKILL VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Check skills have SKILL.md
for skill_dir in $(find "$CLAUDE_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null); do
  skill_name=$(basename "$skill_dir")
  skill_file="$skill_dir/SKILL.md"
  if [ -f "$skill_file" ]; then
    check "$skill_name/SKILL.md exists"
    # Check frontmatter
    if head -1 "$skill_file" | grep -q "^---"; then
      check "$skill_name has frontmatter"
    else
      warn "$skill_name missing frontmatter"
    fi
  else
    echo -e "  ${RED}✗${NC} $skill_name/SKILL.md NOT FOUND"
    ((ERRORS++))
  fi
done

echo ""

# ============================================================
echo "▶ [6/6] HOOKS VALIDATION"
echo "─────────────────────────────────────────────────────────────────"

# Check settings.json has hooks section
if [ -f "$CLAUDE_DIR/settings.json" ]; then
  if grep -q '"hooks"' "$CLAUDE_DIR/settings.json"; then
    check "settings.json has hooks section"
    
    # Check for required hook types
    grep -q '"Stop"' "$CLAUDE_DIR/settings.json" && check "Stop hooks configured" || warn "Stop hooks not configured"
    grep -q '"PreToolUse"' "$CLAUDE_DIR/settings.json" && check "PreToolUse hooks configured" || warn "PreToolUse hooks not configured"
    grep -q '"PostToolUse"' "$CLAUDE_DIR/settings.json" && check "PostToolUse hooks configured" || warn "PostToolUse hooks not configured"
  else
    echo -e "  ${RED}✗${NC} settings.json missing hooks section"
    ((ERRORS++))
  fi
fi

echo ""

# ============================================================
echo "═════════════════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║  VALIDATION PASSED - ALL CHECKS SUCCESSFUL                     ║${NC}"
  echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
  if [ $WARNINGS -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}  Warnings: $WARNINGS (non-blocking)${NC}"
  fi
  exit 0
else
  echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${RED}║  VALIDATION FAILED - $ERRORS ERROR(S) FOUND                          ║${NC}"
  echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo "  Errors: $ERRORS"
  echo "  Warnings: $WARNINGS"
  echo ""
  echo "  Fix all errors before proceeding."
  exit 1
fi
