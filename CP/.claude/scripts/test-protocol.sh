#!/bin/bash
# test-protocol.sh - Comprehensive tests for Claude Protocol
# Run from project root: bash .claude/scripts/test-protocol.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

export CLAUDE_PROJECT_DIR="$PROJECT_DIR"

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✓ $1"; ((PASS++)); }
fail() { echo "  ✗ $1"; ((FAIL++)); }
warn() { echo "  ! $1"; ((WARN++)); }

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           CLAUDE PROTOCOL TEST SUITE                          ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Project: $PROJECT_DIR"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
echo "═══ TEST 1: Agent Frontmatter Validation ═══"
for agent in .claude/agents/*/*.md; do
  name=$(basename "$agent" .md)
  [ "$name" = "AGENT_PROTOCOL" ] && continue
  
  if ! head -1 "$agent" | grep -q "^---$"; then
    fail "$name: Missing frontmatter"
    continue
  fi
  
  fm=$(sed -n '2,/^---$/p' "$agent" | head -n -1)
  missing=""
  echo "$fm" | grep -q "^name:" || missing="$missing name"
  echo "$fm" | grep -q "^description:" || missing="$missing description"
  echo "$fm" | grep -q "^tools:" || missing="$missing tools"
  echo "$fm" | grep -q "^model:" || missing="$missing model"
  
  if [ -n "$missing" ]; then
    fail "$name: Missing fields:$missing"
  else
    pass "$name"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 2: Model String Validation ═══"
VALID_MODELS="claude-opus-4-5-20251101 claude-sonnet-4-5-20250929 claude-haiku-4-5-20251001"
for agent in .claude/agents/*/*.md; do
  name=$(basename "$agent" .md)
  [ "$name" = "AGENT_PROTOCOL" ] && continue
  
  model=$(grep "^model:" "$agent" | head -1 | sed 's/model: *//')
  if echo "$VALID_MODELS" | grep -q "$model"; then
    pass "$name: $model"
  else
    fail "$name: Invalid model '$model'"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 3: Tool Validation ═══"
VALID_TOOLS="Read Write Edit MultiEdit Bash Grep Glob Task WebSearch WebFetch Think TodoRead TodoWrite NotebookEdit"
for agent in .claude/agents/*/*.md; do
  name=$(basename "$agent" .md)
  [ "$name" = "AGENT_PROTOCOL" ] && continue
  
  tools=$(sed -n '/^tools:/,/^[a-z]/p' "$agent" | grep "^  - " | sed 's/^  - //')
  invalid=""
  for tool in $tools; do
    echo "$tool" | grep -q "^mcp__" && continue
    echo "$VALID_TOOLS" | grep -q "\b$tool\b" || invalid="$invalid $tool"
  done
  
  if [ -n "$invalid" ]; then
    fail "$name: Unknown tools:$invalid"
  else
    pass "$name"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 4: settings.json Validation ═══"
if python3 -m json.tool .claude/settings.json > /dev/null 2>&1; then
  pass "settings.json is valid JSON"
else
  fail "settings.json is invalid JSON"
fi
echo ""

# ============================================================================
echo "═══ TEST 5: Python Hook Syntax ═══"
for hook in .claude/hooks/*.py; do
  name=$(basename "$hook")
  if python3 -m py_compile "$hook" 2>/dev/null; then
    pass "$name"
  else
    fail "$name: syntax error"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 6: Shell Hook Syntax ═══"
for hook in .claude/hooks/*.sh; do
  name=$(basename "$hook")
  if bash -n "$hook" 2>/dev/null; then
    pass "$name"
  else
    fail "$name: syntax error"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 7: Agent Plan Enforcer Detection ═══"
for agent in orchestrator security-scanner debugger documenter; do
  result=$(echo "{\"tool_name\": \"Task\", \"tool_input\": {\"subagent_type\": \"$agent\", \"prompt\": \"test\"}}" | python3 .claude/hooks/agent-plan-enforcer.py 2>/dev/null)
  if echo "$result" | grep -q "permissionDecision"; then
    pass "$agent: Plan mode detected"
  else
    fail "$agent: Plan mode NOT detected"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 8: Agent Response Handler ═══"
cat > /tmp/test-transcript.jsonl << 'EOF'
{"type": "assistant", "message": {"content": [{"type": "text", "text": "```json\n{\"agent\": \"test\", \"status\": \"needs_approval\", \"present_to_user\": \"Plan ready\"}\n```"}]}}
EOF
result=$(echo '{"transcript_path": "/tmp/test-transcript.jsonl"}' | python3 .claude/hooks/agent-response-handler.py 2>/dev/null)
if echo "$result" | grep -q '"decision": "block"'; then
  pass "Correctly blocks needs_approval status"
else
  fail "Did not block needs_approval status"
fi
rm -f /tmp/test-transcript.jsonl
echo ""

# ============================================================================
echo "═══ TEST 9: MCP Memory Server Files ═══"
required_files=(
  ".claude/mcp/memory-server/package.json"
  ".claude/mcp/memory-server/tsconfig.json"
  ".claude/mcp/memory-server/src/index.ts"
  ".claude/mcp/memory-server/src/types/memory.ts"
)
for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    pass "$file"
  else
    fail "$file: NOT FOUND"
  fi
done
echo ""

# ============================================================================
echo "═══ TEST 10: Documentation Files ═══"
required_docs=(
  "README.md"
  "CHANGELOG.md"
  "CLAUDE.md"
  "docs/INSTALLATION.md"
  "docs/AGENTS.md"
  "docs/HOOKS.md"
)
for doc in "${required_docs[@]}"; do
  if [ -f "$doc" ]; then
    pass "$doc"
  else
    fail "$doc: NOT FOUND"
  fi
done
echo ""

# ============================================================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                             ║"
echo "╠════════════════════════════════════════════════════════════════╣"
printf "║  PASSED: %-5d                                               ║\n" $PASS
printf "║  FAILED: %-5d                                               ║\n" $FAIL
printf "║  WARNINGS: %-3d                                               ║\n" $WARN
echo "╚════════════════════════════════════════════════════════════════╝"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
exit 0

# =============================================================================
# MODEL TIER VALIDATION
# =============================================================================

echo ""
echo "=== Model Tier Validation ==="

# Check all agents have model_tier
MISSING_TIER=0
for agent in .claude/agents/**/*.md; do
    [[ "$agent" == *"AGENT_PROTOCOL"* ]] && continue
    if ! grep -q "^model_tier:" "$agent"; then
        echo "MISSING model_tier: $agent"
        MISSING_TIER=$((MISSING_TIER + 1))
    fi
done

if [ $MISSING_TIER -eq 0 ]; then
    echo "✓ All agents have model_tier defined"
else
    echo "✗ $MISSING_TIER agents missing model_tier"
fi

# Validate tier values
INVALID_TIER=0
for agent in .claude/agents/**/*.md; do
    [[ "$agent" == *"AGENT_PROTOCOL"* ]] && continue
    tier=$(grep "^model_tier:" "$agent" | awk '{print $2}')
    if [[ ! "$tier" =~ ^(fast|standard|high)$ ]]; then
        echo "INVALID tier '$tier': $agent"
        INVALID_TIER=$((INVALID_TIER + 1))
    fi
done

if [ $INVALID_TIER -eq 0 ]; then
    echo "✓ All model_tier values are valid (fast|standard|high)"
else
    echo "✗ $INVALID_TIER agents have invalid tier values"
fi

# Check model matches tier
MODEL_MISMATCH=0
declare -A tier_models=(
    ["fast"]="claude-haiku-4-5-20251001"
    ["standard"]="claude-sonnet-4-5-20250929"
    ["high"]="claude-opus-4-5-20251101"
)

for agent in .claude/agents/**/*.md; do
    [[ "$agent" == *"AGENT_PROTOCOL"* ]] && continue
    tier=$(grep "^model_tier:" "$agent" | awk '{print $2}')
    model=$(grep "^model:" "$agent" | awk '{print $2}')
    expected="${tier_models[$tier]}"
    
    if [[ -n "$tier" && -n "$expected" && "$model" != "$expected" ]]; then
        echo "MISMATCH: $agent has tier=$tier but model=$model (expected $expected)"
        MODEL_MISMATCH=$((MODEL_MISMATCH + 1))
    fi
done

if [ $MODEL_MISMATCH -eq 0 ]; then
    echo "✓ All models match their declared tier"
else
    echo "✗ $MODEL_MISMATCH model/tier mismatches"
fi

# Summary by tier
echo ""
echo "=== Tier Distribution ==="
echo "  high (Opus):     $(grep -l "model_tier: high" .claude/agents/**/*.md 2>/dev/null | wc -l) agents"
echo "  standard (Sonnet): $(grep -l "model_tier: standard" .claude/agents/**/*.md 2>/dev/null | wc -l) agents"
echo "  fast (Haiku):    $(grep -l "model_tier: fast" .claude/agents/**/*.md 2>/dev/null | wc -l) agents"
echo "  min_tier: fast:  $(grep -l "min_tier: fast" .claude/agents/**/*.md 2>/dev/null | wc -l) agents (can be downgraded)"
