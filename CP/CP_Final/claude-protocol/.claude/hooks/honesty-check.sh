#!/bin/bash
# Stop hook: Check for honesty issues
RESPONSE="$1"
flags=""
echo "$RESPONSE" | grep -qiE "definitely|certainly|absolutely|always|never" && flags="overconfident;"
echo "$RESPONSE" | grep -qiE "I believe|I think|probably|might be" || flags="${flags}missing_uncertainty;"
[ -n "$flags" ] && echo "{\"flags\": \"$flags\"}" || echo '{"status": "pass"}'
