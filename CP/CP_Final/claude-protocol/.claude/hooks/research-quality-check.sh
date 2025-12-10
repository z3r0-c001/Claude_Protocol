#!/bin/bash
# PostToolUse hook: Evaluate research source quality
OUTPUT="$1"
warnings=""
echo "$OUTPUT" | grep -qiE "reddit\.com|quora\.com|yahoo answers" && warnings="low_tier_source;"
echo "$OUTPUT" | grep -qiE "2019|2020|2021" && warnings="${warnings}potentially_outdated;"
[ -n "$warnings" ] && echo "{\"warning\": \"$warnings\"}" || echo '{"status": "ok"}'
