#!/bin/bash
# PostToolUse hook: Check subagent output quality
# Ensures subagent responses are complete and actionable

# Source shared logging
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh"
notify_hook_start "Task"

OUTPUT="$1"
OUTPUT_MODE="${2:-json}"

ISSUES=""
STATUS="pass"

# Check for incomplete/placeholder patterns in subagent output
INCOMPLETE_PATTERNS=(
  "// \\.\\.\\.":"Placeholder code"
  "# \\.\\.\\.":"Placeholder code"
  "TODO":"Unfinished task"
  "FIXME":"Unfinished fix"
  "pass$":"Python stub"
  "raise NotImplementedError":"Not implemented"
)

for item in "${INCOMPLETE_PATTERNS[@]}"; do
  pattern="${item%%:*}"
  description="${item##*:}"
  if echo "$OUTPUT" | grep -qE "$pattern"; then
    ISSUES="${ISSUES}{\"type\":\"incomplete\",\"pattern\":\"$pattern\",\"description\":\"$description\",\"severity\":\"warn\"},"
    STATUS="warning"
  fi
done

# Check for delegation phrases (subagent should do work, not suggest)
DELEGATION_PATTERNS=(
  "you could":"Delegation"
  "you might want to":"Delegation"
  "consider":"Suggestion instead of action"
  "you'll need to":"Delegation"
  "make sure to":"Delegation"
  "don't forget to":"Delegation"
)

for item in "${DELEGATION_PATTERNS[@]}"; do
  pattern="${item%%:*}"
  description="${item##*:}"
  if echo "$OUTPUT" | grep -qiE "$pattern"; then
    ISSUES="${ISSUES}{\"type\":\"delegation\",\"pattern\":\"$pattern\",\"description\":\"$description\",\"severity\":\"warn\"},"
    STATUS="warning"
  fi
done

# Check for vague/uncertain language
VAGUE_PATTERNS=(
  "something like":"Vague suggestion"
  "probably":"Uncertainty"
  "might work":"Uncertainty"
  "should work":"Uncertainty"
)

for item in "${VAGUE_PATTERNS[@]}"; do
  pattern="${item%%:*}"
  description="${item##*:}"
  if echo "$OUTPUT" | grep -qiE "$pattern"; then
    ISSUES="${ISSUES}{\"type\":\"vague\",\"pattern\":\"$pattern\",\"description\":\"$description\",\"severity\":\"suggest\"},"
    [ "$STATUS" = "pass" ] && STATUS="suggest"
  fi
done

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"subagent-output-check","status":"pass"}'
  else
    echo "{\"hook\":\"subagent-output-check\",\"status\":\"$STATUS\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$STATUS" != "pass" ]; then
    echo "Subagent output issues: $ISSUES"
  fi
fi

notify_hook_result "continue"
exit 0
