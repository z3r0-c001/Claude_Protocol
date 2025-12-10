#!/bin/bash
# Stop hook: Check for lazy response patterns
RESPONSE="$1"
issues=""
echo "$RESPONSE" | grep -qiE "you could|you might want to|consider adding|I recommend" && issues="suggestion;"
echo "$RESPONSE" | grep -qE "// \.\.\.|# \.\.\.|TODO|FIXME" && issues="${issues}placeholder;"
echo "$RESPONSE" | grep -qiE "you'll need to|make sure to|don't forget" && issues="${issues}delegation;"
echo "$RESPONSE" | grep -qiE "for brevity|to keep this short|I'll focus on" && issues="${issues}scope_reduction;"
[ -n "$issues" ] && echo "{\"issues\": \"$issues\", \"action\": \"review\"}" || echo '{"status": "pass"}'
