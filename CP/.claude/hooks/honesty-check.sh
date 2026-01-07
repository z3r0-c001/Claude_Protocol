#!/bin/bash
# Stop hook: Check for honesty issues in responses
# Reads JSON from stdin, outputs JSON to stdout for blocking

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="honesty-check"

hook_status "$HOOK_NAME" "RUNNING" "Checking honesty"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get transcript path
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get last response
LAST_RESPONSE=$(tac "$TRANSCRIPT_PATH" 2>/dev/null | while read -r line; do
    TYPE=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
    if [ "$TYPE" = "assistant" ]; then
        echo "$line" | jq -r '.message.content[]? | select(.type=="text") | .text' 2>/dev/null
        break
    fi
done)

if [ -z "$LAST_RESPONSE" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Check for overconfident language
OVERCONFIDENT=""
PATTERNS=(
    "definitely will"
    "certainly will"
    "guaranteed to"
    "100% certain"
    "without question"
    "no doubt about"
    "absolutely certain"
)

for pattern in "${PATTERNS[@]}"; do
    if echo "$LAST_RESPONSE" | grep -qiE "$pattern"; then
        OVERCONFIDENT="${OVERCONFIDENT}${pattern}; "
    fi
done

# Check for false certainty about external facts
if echo "$LAST_RESPONSE" | grep -qiE "this will (always|never)" || \
   echo "$LAST_RESPONSE" | grep -qiE "it is (impossible|guaranteed)"; then
    OVERCONFIDENT="${OVERCONFIDENT}absolute_claim; "
fi

if [ -n "$OVERCONFIDENT" ]; then
    hook_status "$HOOK_NAME" "BLOCK" "Overconfident: ${OVERCONFIDENT}"
    cat << ENDJSON
{"decision": "block", "reason": "OVERCONFIDENT LANGUAGE DETECTED: ${OVERCONFIDENT}. Rephrase with appropriate uncertainty (e.g., 'should', 'likely', 'in most cases')."}
ENDJSON
    exit 0
fi

# No issues
hook_status "$HOOK_NAME" "OK" "Honesty verified"
echo '{"continue": true}'
exit 0
