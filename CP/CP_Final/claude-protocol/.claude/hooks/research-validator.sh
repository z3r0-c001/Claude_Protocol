#!/bin/bash
# SubagentStop hook: Validate research completeness
OUTPUT="$1"
issues=""
sources=$(echo "$OUTPUT" | grep -coE "https?://" || echo 0)
[ "$sources" -lt 2 ] && issues="few_sources;"
echo "$OUTPUT" | grep -qiE "could not find|no results|unable to" && issues="${issues}incomplete;"
[ -n "$issues" ] && echo "{\"issues\": \"$issues\"}" || echo '{"status": "pass"}'
