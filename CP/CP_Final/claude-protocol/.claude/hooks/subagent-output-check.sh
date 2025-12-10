#!/bin/bash
# PostToolUse hook: Check subagent output quality
OUTPUT="$1"
issues=""
echo "$OUTPUT" | grep -qiE "you could|you might want to|consider" && issues="suggestion;"
echo "$OUTPUT" | grep -qE "// \.\.\.|TODO|pass$" && issues="${issues}incomplete;"
echo "$OUTPUT" | grep -qiE "you'll need to|make sure to" && issues="${issues}delegation;"
[ -n "$issues" ] && echo "{\"warning\": \"$issues\"}" || echo '{"status": "ok"}'
