#!/bin/bash
# Laziness Check - Stop Hook
# Validates Claude's response for lazy patterns before completion
# Reads transcript directly to check the last assistant response

# Source shared logger
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/hook-logger.sh" ]; then
    source "${SCRIPT_DIR}/hook-logger.sh"
else
    hook_log() { :; }
    notify_hook_start() { :; }
    notify_hook_result() { :; }
fi

notify_hook_start "Stop"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops - if we're already in a stop hook, approve
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    notify_hook_result "continue"
    echo '{"decision": "approve"}'
    exit 0
fi

# Get transcript path from input
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    hook_log "OK" "No transcript, approving"
    notify_hook_result "continue"
    echo '{"decision": "approve"}'
    exit 0
fi

hook_log "INFO" "Checking transcript: $(basename "$TRANSCRIPT_PATH")"

# Get the most recent assistant response from transcript
# Use tac to read file in reverse, find first assistant message with text
LAST_RESPONSE=$(tac "$TRANSCRIPT_PATH" | while read -r line; do
    TYPE=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
    if [ "$TYPE" = "assistant" ]; then
        echo "$line" | jq -r '.message.content[]? | select(.type=="text") | .text' 2>/dev/null
        break
    fi
done)

if [ -z "$LAST_RESPONSE" ]; then
    hook_log "OK" "No response text found"
    notify_hook_result "continue"
    echo '{"decision": "approve"}'
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
    hook_log "OK" "Valid response (work=$WORK_DONE, choice=$USER_CHOICE, question=$ASKING_QUESTION)"
    notify_hook_result "continue"
    echo '{"decision": "approve"}'
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
    hook_log "BLOCK" "Lazy patterns: ${LAZY_FOUND}"
    notify_hook_result "block"

    # Write violation to file for next prompt injection
    VIOLATION_FILE="${PROJECT_DIR}/.claude/flags/laziness-violation.md"
    cat << VIOLATION > "$VIOLATION_FILE"
# LAZINESS VIOLATION DETECTED

Your previous response was flagged for lazy patterns: **${LAZY_FOUND}**

You told the user what to do instead of doing it yourself. This is unacceptable.

**REQUIRED ACTION**: In your next response, actually DO the work. Do not suggest, delegate, or tell the user to do things. Take action.

Timestamp: $(date -Iseconds)
VIOLATION

    # Exit 0 required for JSON to be processed by Claude Code
    cat << EOF
{"decision": "block", "reason": "LAZY RESPONSE BLOCKED. You used: ${LAZY_FOUND}. DO NOT suggest or delegate - actually DO the work yourself. Rewrite your response to take action instead of telling the user what to do."}
EOF
    exit 0
fi

hook_log "OK" "No lazy patterns detected"
notify_hook_result "continue"
echo '{"decision": "approve"}'
exit 0
