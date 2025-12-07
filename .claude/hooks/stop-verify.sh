#!/bin/bash
# Stop hook: Final verification before response
# Combines multiple quality checks

OUTPUT_MODE="${1:-json}"

ISSUES=""
STATUS="pass"

# Check for environment variables that indicate verification needed
if [ -n "$CLAUDE_NEEDS_VERIFICATION" ]; then
  ISSUES="${ISSUES}{\"type\":\"verification_pending\",\"flag\":\"$CLAUDE_NEEDS_VERIFICATION\",\"severity\":\"suggest\"},"
  STATUS="suggest"
fi

# Check for any files modified in this session that need review
if [ -n "$CLAUDE_MODIFIED_FILES" ]; then
  # Count modified files
  FILE_COUNT=$(echo "$CLAUDE_MODIFIED_FILES" | tr ',' '\n' | wc -l)
  if [ "$FILE_COUNT" -gt 5 ]; then
    ISSUES="${ISSUES}{\"type\":\"many_files_modified\",\"count\":$FILE_COUNT,\"severity\":\"suggest\",\"suggestion\":\"Consider reviewing changes before finalizing\"},"
    STATUS="suggest"
  fi
fi

# Check for research flags
if [ -n "$CLAUDE_RESEARCH_NEEDED" ]; then
  ISSUES="${ISSUES}{\"type\":\"research_incomplete\",\"topic\":\"$CLAUDE_RESEARCH_NEEDED\",\"severity\":\"warn\"},"
  STATUS="warning"
fi

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"stop-verify","status":"pass","verified":true}'
  else
    echo "{\"hook\":\"stop-verify\",\"status\":\"$STATUS\",\"verified\":false,\"issues\":[$ISSUES]}"
  fi
else
  if [ "$STATUS" != "pass" ]; then
    echo "Verification issues found"
  fi
fi

exit 0
