#!/bin/bash
# Laziness Check - Stop Hook
# Validates Claude's response for lazy patterns before completion
# Reads JSON from stdin, outputs JSON to stdout

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="laziness-check"

hook_status "$HOOK_NAME" "RUNNING" "Checking response"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops - if we're already in a stop hook, allow through
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get transcript path from input
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get the most recent assistant response from transcript
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

# Check for work-done indicators (past tense = actually did something)
WORK_DONE=false
if echo "$LAST_RESPONSE" | grep -qiE '\b(completed|fixed|updated|created|implemented|edited|wrote|modified|added|removed|refactored|changed|installed|configured|set up|ran|executed)\b'; then
    WORK_DONE=true
fi

# Check for user-choice context (offering options is OK)
USER_CHOICE=false
if echo "$LAST_RESPONSE" | grep -qiE '(which would you prefer|do you want me to|should I|would you like|what would you like)'; then
    USER_CHOICE=true
fi

# Check for question context (asking for clarification is OK)
ASKING_QUESTION=false
if echo "$LAST_RESPONSE" | grep -qiE '\?$|\? |can you clarify|could you tell me|what do you mean'; then
    ASKING_QUESTION=true
fi

# Skip laziness check if work was done, offering choices, or asking questions
if [ "$WORK_DONE" = "true" ] || [ "$USER_CHOICE" = "true" ] || [ "$ASKING_QUESTION" = "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Lazy patterns to detect
LAZY_FOUND=""

# Suggestion patterns (telling user what to do instead of doing it)
if echo "$LAST_RESPONSE" | grep -qiE '\b(you could|you might want to|i recommend you|i suggest you|consider adding|consider reading|consider checking)\b'; then
    LAZY_FOUND="${LAZY_FOUND}suggestion; "
fi

# Delegation patterns (pushing work back to user)
if echo "$LAST_RESPONSE" | grep -qiE '\b(you need to|you have to|you.ll need to|make sure to|now you|go ahead and|you should then|you can then)\b'; then
    LAZY_FOUND="${LAZY_FOUND}delegation; "
fi

# Scope reduction patterns (avoiding work)
if echo "$LAST_RESPONSE" | grep -qiE '\b(for brevity|beyond the scope|i.ll leave|as an exercise|left as|i won.t cover)\b'; then
    LAZY_FOUND="${LAZY_FOUND}scope_reduction; "
fi

if [ -n "$LAZY_FOUND" ]; then
    hook_status "$HOOK_NAME" "BLOCK" "Lazy patterns: ${LAZY_FOUND}"
    # Block with reason - forces Claude to continue
    cat << ENDJSON
{"decision": "block", "reason": "LAZY RESPONSE DETECTED: ${LAZY_FOUND}. You must DO the work, not tell the user what to do. Rewrite your response to take action."}
ENDJSON
    exit 0
fi

# No issues - continue
hook_status "$HOOK_NAME" "OK" "No lazy patterns"
echo '{"continue": true}'
exit 0
