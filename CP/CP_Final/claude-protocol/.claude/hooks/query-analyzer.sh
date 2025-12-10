#!/bin/bash
# UserPromptSubmit hook: Analyze query type
PROMPT="$1"
type="general"
echo "$PROMPT" | grep -qiE "code|function|implement|write.*script" && type="coding"
echo "$PROMPT" | grep -qiE "research|find out|what is|who is|when did" && type="research"
echo "$PROMPT" | grep -qiE "review|check|audit|verify" && type="verification"
echo "{\"query_type\": \"$type\"}"
