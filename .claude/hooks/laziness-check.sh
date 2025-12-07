#!/bin/bash
# Laziness Check Script (Merged from CP2 + CP_Final)
# Detects placeholder code, TODOs, incomplete implementations
# Supports both JSON output (for hooks) and human-readable output (for CLI)

TARGET="${1:-.}"
OUTPUT_MODE="${2:-human}"  # json or human

# Arrays to collect issues
declare -a ISSUES=()
ERRORS=0

add_issue() {
  local type="$1"
  local message="$2"
  local file="$3"
  local line="${4:-0}"
  local severity="${5:-suggest}"

  ISSUES+=("{\"type\":\"$type\",\"file\":\"$file\",\"line\":$line,\"message\":\"$message\",\"severity\":\"$severity\",\"suggestion\":\"Replace with actual implementation\"}")
  ((ERRORS++))
}

# Colors for human output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# File types to check
FILE_TYPES="*.py *.ts *.js *.tsx *.jsx *.go *.rs *.java"

# Directories to exclude
EXCLUDE_DIRS="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=vendor --exclude-dir=.next --exclude-dir=coverage --exclude-dir=.cache"

# Pattern definitions
PLACEHOLDER_PATTERNS=(
  "// \.\.\."
  "# \.\.\."
  "/\* \.\.\. \*/"
)

TODO_PATTERNS=(
  "// TODO"
  "# TODO"
  "/\* TODO"
  "// FIXME"
  "# FIXME"
)

STUB_PATTERNS=(
  "^\s*pass$"
  "throw new NotImplementedError"
  "raise NotImplementedError"
  "// implement"
  "# implement"
  "// add implementation"
  "// fill in"
  "# fill in"
)

LAZY_PHRASES=(
  "You could"
  "You might want to"
  "Consider adding"
  "You'll need to"
  "Left as an exercise"
  "Implementation details"
  "Add your logic here"
)

if [ "$OUTPUT_MODE" = "human" ]; then
  echo "═══════════════════════════════════════════════════════════════"
  echo "  LAZINESS CHECK"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo "▶ Checking for placeholder comments..."
  echo "─────────────────────────────────────────────────────────────────"
fi

# Check placeholder patterns
for pattern in "${PLACEHOLDER_PATTERNS[@]}"; do
  while IFS=: read -r file line content; do
    if [ -n "$file" ]; then
      add_issue "placeholder" "Placeholder comment found: $pattern" "$file" "$line" "block"
      if [ "$OUTPUT_MODE" = "human" ]; then
        echo -e "${RED}FOUND:${NC} $file:$line: $content"
      fi
    fi
  done < <(grep -rn $EXCLUDE_DIRS --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.rs" --include="*.java" "$pattern" "$TARGET" 2>/dev/null || true)
done

if [ "$OUTPUT_MODE" = "human" ]; then
  if [ ${#ISSUES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No placeholder comments found"
  fi
  echo ""
  echo "▶ Checking for TODO/FIXME markers..."
  echo "─────────────────────────────────────────────────────────────────"
fi

# Check TODO patterns
PREV_ERRORS=$ERRORS
for pattern in "${TODO_PATTERNS[@]}"; do
  while IFS=: read -r file line content; do
    if [ -n "$file" ]; then
      add_issue "todo" "TODO/FIXME marker found" "$file" "$line" "suggest"
      if [ "$OUTPUT_MODE" = "human" ]; then
        echo -e "${YELLOW}FOUND:${NC} $file:$line: $content"
      fi
    fi
  done < <(grep -rn $EXCLUDE_DIRS --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.rs" --include="*.java" "$pattern" "$TARGET" 2>/dev/null || true)
done

if [ "$OUTPUT_MODE" = "human" ]; then
  TODO_COUNT=$((ERRORS - PREV_ERRORS))
  if [ $TODO_COUNT -gt 0 ]; then
    echo -e "${RED}✗${NC} Found $TODO_COUNT TODO/FIXME markers (must be implemented)"
  else
    echo -e "${GREEN}✓${NC} No unimplemented TODOs found"
  fi
  echo ""
  echo "▶ Checking for stub implementations..."
  echo "─────────────────────────────────────────────────────────────────"
fi

# Check stub patterns
PREV_ERRORS=$ERRORS
for pattern in "${STUB_PATTERNS[@]}"; do
  while IFS=: read -r file line content; do
    if [ -n "$file" ]; then
      add_issue "stub" "Stub implementation found" "$file" "$line" "block"
      if [ "$OUTPUT_MODE" = "human" ]; then
        echo -e "${RED}FOUND:${NC} $file:$line: $content"
      fi
    fi
  done < <(grep -rn $EXCLUDE_DIRS --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.rs" --include="*.java" -E "$pattern" "$TARGET" 2>/dev/null || true)
done

if [ "$OUTPUT_MODE" = "human" ]; then
  STUB_COUNT=$((ERRORS - PREV_ERRORS))
  if [ $STUB_COUNT -gt 0 ]; then
    echo -e "${RED}✗${NC} Found stub implementations (must be completed)"
  else
    echo -e "${GREEN}✓${NC} No stub implementations found"
  fi
  echo ""
  echo "▶ Checking for lazy delegation phrases..."
  echo "─────────────────────────────────────────────────────────────────"
fi

# Check lazy phrases in assistant responses
PREV_ERRORS=$ERRORS
for phrase in "${LAZY_PHRASES[@]}"; do
  if echo "$TARGET" | grep -qi "$phrase" 2>/dev/null; then
    add_issue "delegation" "Lazy delegation detected: '$phrase'" "response" "0" "block"
    if [ "$OUTPUT_MODE" = "human" ]; then
      echo -e "${RED}FOUND:${NC} Delegation phrase: '$phrase'"
    fi
  fi
done

if [ "$OUTPUT_MODE" = "human" ]; then
  LAZY_COUNT=$((ERRORS - PREV_ERRORS))
  if [ $LAZY_COUNT -gt 0 ]; then
    echo -e "${RED}✗${NC} Found lazy delegation (must implement instead of suggesting)"
  else
    echo -e "${GREEN}✓${NC} No lazy delegation found"
  fi
fi

# Output based on mode
if [ "$OUTPUT_MODE" = "json" ]; then
  # Build JSON output
  STATUS="pass"
  DECISION="approve"
  if [ $ERRORS -gt 0 ]; then
    STATUS="warning"
    DECISION="block"
  fi

  ISSUES_JSON=$(IFS=,; echo "[${ISSUES[*]}]")
  echo "{\"hook\":\"laziness-check\",\"status\":\"$STATUS\",\"decision\":\"$DECISION\",\"target\":\"$TARGET\",\"issue_count\":$ERRORS,\"issues\":$ISSUES_JSON}"
else
  # Human-readable summary
  echo ""
  echo "═══════════════════════════════════════════════════════════════"

  if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}LAZINESS CHECK PASSED${NC}"
  else
    echo -e "${RED}LAZINESS CHECK FAILED - $ERRORS ISSUE(S) FOUND${NC}"
    echo ""
    echo "All placeholder code and TODOs must be replaced with"
    echo "actual implementations before this code is acceptable."
  fi
fi

exit $ERRORS
