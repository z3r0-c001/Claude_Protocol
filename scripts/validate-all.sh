#!/bin/bash
# Full validation suite for Claude Bootstrap Protocol
# Runs all quality checks and reports results

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

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

print_header() {
  echo ""
  echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_check() {
  local status=$1
  local message=$2
  case $status in
    pass)
      echo -e "${GREEN}✓${NC} $message"
      ((PASS_COUNT++))
      ;;
    fail)
      echo -e "${RED}✗${NC} $message"
      ((FAIL_COUNT++))
      ;;
    warn)
      echo -e "${YELLOW}⚠${NC} $message"
      ((WARN_COUNT++))
      ;;
  esac
}

print_header "Claude Bootstrap Protocol Validation"

# Check 1: Protocol structure
print_header "1. Protocol Structure"

if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
  print_check pass "CLAUDE.md exists"
else
  print_check fail "CLAUDE.md not found"
fi

if [ -f "$CLAUDE_DIR/settings.json" ]; then
  print_check pass "settings.json exists"
  # Validate JSON
  if python3 -c "import json; json.load(open('$CLAUDE_DIR/settings.json'))" 2>/dev/null; then
    print_check pass "settings.json is valid JSON"
  else
    print_check fail "settings.json is not valid JSON"
  fi
else
  print_check fail "settings.json not found"
fi

if [ -f "$PROJECT_DIR/.mcp.json" ]; then
  print_check pass ".mcp.json exists"
  if python3 -c "import json; json.load(open('$PROJECT_DIR/.mcp.json'))" 2>/dev/null; then
    print_check pass ".mcp.json is valid JSON"
  else
    print_check fail ".mcp.json is not valid JSON"
  fi
else
  print_check warn ".mcp.json not found (MCP server may not be configured)"
fi

# Check 2: Hooks
print_header "2. Hook Scripts"

HOOKS_DIR="$CLAUDE_DIR/hooks"
if [ -d "$HOOKS_DIR" ]; then
  HOOK_COUNT=$(find "$HOOKS_DIR" -name "*.sh" -o -name "*.py" | wc -l)
  print_check pass "Found $HOOK_COUNT hook scripts"

  # Check each hook for syntax
  for hook in "$HOOKS_DIR"/*.sh; do
    if [ -f "$hook" ]; then
      if bash -n "$hook" 2>/dev/null; then
        print_check pass "$(basename "$hook") syntax OK"
      else
        print_check fail "$(basename "$hook") has syntax errors"
      fi
    fi
  done

  for hook in "$HOOKS_DIR"/*.py; do
    if [ -f "$hook" ]; then
      if python3 -m py_compile "$hook" 2>/dev/null; then
        print_check pass "$(basename "$hook") syntax OK"
      else
        print_check fail "$(basename "$hook") has syntax errors"
      fi
    fi
  done
else
  print_check fail "Hooks directory not found"
fi

# Check 3: Commands
print_header "3. Slash Commands"

COMMANDS_DIR="$CLAUDE_DIR/commands"
if [ -d "$COMMANDS_DIR" ]; then
  COMMAND_COUNT=$(find "$COMMANDS_DIR" -name "*.md" | wc -l)
  print_check pass "Found $COMMAND_COUNT commands"
else
  print_check warn "Commands directory not found"
fi

# Check 4: Agents
print_header "4. Agents"

AGENTS_DIR="$CLAUDE_DIR/agents"
if [ -d "$AGENTS_DIR" ]; then
  AGENT_COUNT=$(find "$AGENTS_DIR" -name "*.md" | wc -l)
  print_check pass "Found $AGENT_COUNT agents"
else
  print_check warn "Agents directory not found"
fi

# Check 5: Skills
print_header "5. Skills"

SKILLS_DIR="$CLAUDE_DIR/skills"
if [ -d "$SKILLS_DIR" ]; then
  SKILL_COUNT=$(find "$SKILLS_DIR" -name "SKILL.md" | wc -l)
  print_check pass "Found $SKILL_COUNT skills"

  # Check skill-rules.json
  if [ -f "$SKILLS_DIR/skill-rules.json" ]; then
    if python3 -c "import json; json.load(open('$SKILLS_DIR/skill-rules.json'))" 2>/dev/null; then
      print_check pass "skill-rules.json is valid JSON"
    else
      print_check fail "skill-rules.json is not valid JSON"
    fi
  fi
else
  print_check warn "Skills directory not found"
fi

# Check 6: MCP Server
print_header "6. MCP Memory Server"

MCP_DIR="$CLAUDE_DIR/mcp/memory-server"
if [ -d "$MCP_DIR" ]; then
  print_check pass "MCP server directory exists"

  if [ -f "$MCP_DIR/package.json" ]; then
    print_check pass "package.json exists"
  else
    print_check fail "package.json not found"
  fi

  if [ -f "$MCP_DIR/src/index.ts" ]; then
    print_check pass "index.ts exists"
  else
    print_check fail "index.ts not found"
  fi

  if [ -d "$MCP_DIR/dist" ]; then
    print_check pass "Built (dist directory exists)"
  else
    print_check warn "Not built (run npm run build in memory-server)"
  fi
else
  print_check warn "MCP server not found"
fi

# Check 7: Laziness check
print_header "7. Laziness Check (Code Quality)"

if [ -f "$CLAUDE_DIR/hooks/laziness-check.sh" ]; then
  LAZINESS_RESULT=$("$CLAUDE_DIR/hooks/laziness-check.sh" "$PROJECT_DIR" json 2>/dev/null || echo '{"status":"error"}')
  if echo "$LAZINESS_RESULT" | grep -q '"status":"pass"'; then
    print_check pass "No placeholder code found"
  else
    ISSUE_COUNT=$(echo "$LAZINESS_RESULT" | grep -o '"issue_count":[0-9]*' | grep -o '[0-9]*' || echo "?")
    print_check warn "Found $ISSUE_COUNT laziness issues"
  fi
else
  print_check warn "Laziness check script not found"
fi

# Summary
print_header "Summary"

TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
echo ""
echo -e "Total checks: $TOTAL"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
  echo -e "${GREEN}✓ All critical checks passed${NC}"
  exit 0
else
  echo -e "${RED}✗ $FAIL_COUNT critical checks failed${NC}"
  exit 1
fi
