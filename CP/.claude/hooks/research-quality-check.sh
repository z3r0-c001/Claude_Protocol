#!/bin/bash
# PostToolUse hook: Check research quality (WebSearch/WebFetch)
# Ensures research is cited and verified

# Source shared logging
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh"
notify_hook_start "WebSearch"

TOOL_OUTPUT="$1"
OUTPUT_MODE="${2:-json}"

ISSUES=""
STATUS="pass"

# Check if sources are cited
if ! echo "$TOOL_OUTPUT" | grep -qiE "source:|according to|from:|reference:"; then
  ISSUES="${ISSUES}{\"type\":\"missing_citation\",\"severity\":\"suggest\",\"suggestion\":\"Consider citing the source of this information\"},"
  STATUS="suggest"
fi

# Check for potentially outdated information
if echo "$TOOL_OUTPUT" | grep -qiE "202[0-2]|201[0-9]"; then
  ISSUES="${ISSUES}{\"type\":\"potentially_outdated\",\"severity\":\"suggest\",\"suggestion\":\"Information may be outdated, verify current accuracy\"},"
  STATUS="suggest"
fi

# Check for conflicting information markers
if echo "$TOOL_OUTPUT" | grep -qiE "however|but|contrary|conflicting|disputed"; then
  ISSUES="${ISSUES}{\"type\":\"conflicting_info\",\"severity\":\"warn\",\"suggestion\":\"Research shows conflicting information, verify carefully\"},"
  STATUS="warning"
fi

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"research-quality-check","status":"pass"}'
  else
    echo "{\"hook\":\"research-quality-check\",\"status\":\"$STATUS\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$STATUS" != "pass" ]; then
    echo "Research quality issues: $STATUS"
  fi
fi

notify_hook_result "continue"
exit 0
