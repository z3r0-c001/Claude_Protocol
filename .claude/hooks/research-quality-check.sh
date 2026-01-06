#!/bin/bash
# PostToolUse hook: Check research quality (WebSearch/WebFetch)
# Reads JSON from stdin with tool_response

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="research-quality-check"

hook_status "$HOOK_NAME" "RUNNING" "Checking research"

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool response
OUTPUT=$(echo "$INPUT" | jq -r '.tool_response // empty')

if [ -z "$OUTPUT" ]; then
    echo '{"continue": true}'
    exit 0
fi

ISSUES=""

# Check for potentially outdated info
if echo "$OUTPUT" | grep -qiE "202[0-2]|201[0-9]"; then
    ISSUES="${ISSUES}potentially_outdated; "
fi

# Check for conflicting info markers
if echo "$OUTPUT" | grep -qiE "however|but|contrary|conflicting|disputed"; then
    ISSUES="${ISSUES}conflicting_info; "
fi

if [ -n "$ISSUES" ]; then
    hook_status "$HOOK_NAME" "WARN" "Issues: ${ISSUES}"
    echo "{\"continue\": true, \"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"RESEARCH NOTE: ${ISSUES}. Verify information accuracy.\"}}"
else
    hook_status "$HOOK_NAME" "OK" "Quality check passed"
    echo '{"continue": true}'
fi

exit 0
