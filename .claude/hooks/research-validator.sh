#!/bin/bash
# SubagentStop hook: Validate research subagent output
# Reads JSON from stdin

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="research-validator"

hook_status "$HOOK_NAME" "RUNNING" "Validating research"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get transcript to analyze subagent output
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get last response from subagent
LAST_OUTPUT=$(tac "$TRANSCRIPT_PATH" 2>/dev/null | while read -r line; do
    TYPE=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
    if [ "$TYPE" = "assistant" ]; then
        echo "$line" | jq -r '.message.content[]? | select(.type=="text") | .text' 2>/dev/null
        break
    fi
done)

if [ -z "$LAST_OUTPUT" ]; then
    echo '{"continue": true}'
    exit 0
fi

ISSUES=""

# Check for unsourced claims
if ! echo "$LAST_OUTPUT" | grep -qiE "source|reference|according to|based on|from"; then
    ISSUES="${ISSUES}unsourced; "
fi

# Check for overconfidence
if echo "$LAST_OUTPUT" | grep -qiE "definitely|certainly|guaranteed|always|never" && \
   ! echo "$LAST_OUTPUT" | grep -qiE "may|might|could|uncertain"; then
    ISSUES="${ISSUES}overconfident; "
fi

if [ -n "$ISSUES" ]; then
    hook_status "$HOOK_NAME" "BLOCK" "Issues: ${ISSUES}"
    cat << ENDJSON
{"decision": "block", "reason": "RESEARCH QUALITY ISSUE: ${ISSUES}. Please cite sources and acknowledge uncertainty."}
ENDJSON
    exit 0
fi

# No issues
hook_status "$HOOK_NAME" "OK" "Research validated"
echo '{"continue": true}'
exit 0
