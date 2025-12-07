#!/bin/bash
# SubagentStop hook: Validate research subagent output
# Ensures research findings are well-structured and actionable

OUTPUT="$1"
OUTPUT_MODE="${2:-json}"

ISSUES=""
STATUS="pass"

# Check for proper structure
if ! echo "$OUTPUT" | grep -qiE "finding|conclusion|result|summary"; then
  ISSUES="${ISSUES}{\"type\":\"unstructured_output\",\"severity\":\"suggest\",\"suggestion\":\"Research output should include clear findings or conclusions\"},"
  STATUS="suggest"
fi

# Check for sources
if ! echo "$OUTPUT" | grep -qiE "source|reference|according to|based on|from"; then
  ISSUES="${ISSUES}{\"type\":\"unsourced_claims\",\"severity\":\"warn\",\"suggestion\":\"Research should cite sources for claims\"},"
  STATUS="warning"
fi

# Check for actionable next steps
if ! echo "$OUTPUT" | grep -qiE "recommend|suggest|next step|action|should"; then
  ISSUES="${ISSUES}{\"type\":\"no_recommendations\",\"severity\":\"suggest\",\"suggestion\":\"Research should include actionable recommendations\"},"
  [ "$STATUS" = "pass" ] && STATUS="suggest"
fi

# Check for uncertainty acknowledgment where appropriate
if echo "$OUTPUT" | grep -qiE "definitely|certainly|always|never|guaranteed" && ! echo "$OUTPUT" | grep -qiE "uncertain|unclear|may|might|could"; then
  ISSUES="${ISSUES}{\"type\":\"overconfident_research\",\"severity\":\"warn\",\"suggestion\":\"Research should acknowledge uncertainty where appropriate\"},"
  STATUS="warning"
fi

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"research-validator","status":"pass"}'
  else
    echo "{\"hook\":\"research-validator\",\"status\":\"$STATUS\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$STATUS" != "pass" ]; then
    echo "Research validation issues: $STATUS"
  fi
fi

exit 0
