#!/bin/bash
# PreToolUse hook: Check content completeness before write
# Blocks placeholder code from being written

CONTENT="$1"
FILE_PATH="${2:-unknown}"
OUTPUT_MODE="${3:-json}"

ISSUES=""
DECISION="approve"
SCORE=0

# Placeholder patterns
PLACEHOLDER_PATTERNS=(
  "// \\.\\.\\.":"Ellipsis placeholder"
  "# \\.\\.\\.":"Ellipsis placeholder"
  "/\\* \\.\\.\\. \\*/":"Block comment placeholder"
  "\\.\\.\\. more":"Incomplete content"
  "etc\\.\\.\\.":"Incomplete content"
)

# Stub patterns
STUB_PATTERNS=(
  "pass$":"Python stub"
  "raise NotImplementedError":"Not implemented"
  "throw new NotImplementedError":"Not implemented"
  "// implement":"Unimplemented"
  "# implement":"Unimplemented"
  "// add implementation":"Unimplemented"
  "// fill in":"Unimplemented"
  "TODO":"Unfinished task"
  "FIXME":"Unfinished fix"
)

# Check placeholder patterns
for item in "${PLACEHOLDER_PATTERNS[@]}"; do
  pattern="${item%%:*}"
  description="${item##*:}"
  if echo "$CONTENT" | grep -qE "$pattern"; then
    DECISION="block"
    SCORE=$((SCORE + 3))
    ISSUES="${ISSUES}{\"type\":\"placeholder\",\"pattern\":\"$pattern\",\"description\":\"$description\",\"severity\":\"block\"},"
  fi
done

# Check stub patterns
for item in "${STUB_PATTERNS[@]}"; do
  pattern="${item%%:*}"
  description="${item##*:}"
  if echo "$CONTENT" | grep -qE "$pattern"; then
    DECISION="block"
    SCORE=$((SCORE + 2))
    ISSUES="${ISSUES}{\"type\":\"stub\",\"pattern\":\"$pattern\",\"description\":\"$description\",\"severity\":\"block\"},"
  fi
done

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"completeness-check","status":"pass","decision":"approve","score":0}'
  else
    echo "{\"hook\":\"completeness-check\",\"status\":\"incomplete\",\"decision\":\"$DECISION\",\"file\":\"$FILE_PATH\",\"score\":$SCORE,\"issues\":[$ISSUES]}"
  fi
else
  if [ "$DECISION" = "block" ]; then
    echo "BLOCKED: Content contains placeholder or incomplete code (score: $SCORE)"
    exit 1
  fi
fi

[ "$DECISION" = "block" ] && exit 1
exit 0
