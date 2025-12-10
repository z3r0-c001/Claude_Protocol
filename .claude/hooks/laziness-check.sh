#!/bin/bash
# Laziness Check - Stop Hook
# Validates Claude's response for lazy patterns before completion
# Uses watcher IPC when available, falls back to transcript parsing

# Source shared logger (write to watcher.log with hook name)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/hook-logger.sh" ]; then
    source "${SCRIPT_DIR}/hook-logger.sh"
else
    hook_log() { :; }  # No-op if logger not available
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
IPC_SCRIPT="${PROJECT_DIR}/.claude/watcher/ipc.sh"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops - if we're already in a stop hook, approve
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"decision": "approve"}'
    exit 0
fi

# Get transcript path from input
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
if [ -z "$TRANSCRIPT_PATH" ]; then
    # Try to find transcript from Claude's project dir
    TRANSCRIPT_PATH=$(ls -t "$HOME/.claude/projects/"*/*.jsonl 2>/dev/null | head -1)
fi

hook_log "INFO" "Checking response for lazy patterns"

# Try watcher first (has real-time validation)
if [ -x "$IPC_SCRIPT" ]; then
    WATCHER_RESPONSE=$("$IPC_SCRIPT" get_pending 2>/dev/null)
    
    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == true' >/dev/null 2>&1; then
        # Filter for laziness-related issue types
        LAZY_ISSUES=$(echo "$WATCHER_RESPONSE" | jq -r '.issues[] | select(.type == "SUGGESTION" or .type == "DELEGATION" or .type == "SCOPE_REDUCTION") | .pattern' 2>/dev/null | tr '\n' '; ')
        
        if [ -n "$LAZY_ISSUES" ]; then
            hook_log "BLOCK" "Lazy patterns found: ${LAZY_ISSUES}"
            echo "[LAZINESS CHECK] Detected lazy patterns: ${LAZY_ISSUES}" >&2
            cat << EOF
{"decision": "block", "reason": "Lazy response detected: ${LAZY_ISSUES}"}
EOF
            exit 2
        fi
    fi
    
    # Watcher running but no laziness issues
    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == false' >/dev/null 2>&1; then
        hook_log "OK" "No lazy patterns (watcher)"
        echo '{"decision": "approve"}'
        exit 0
    fi
fi

# Fallback: Parse transcript directly if watcher unavailable
if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    hook_log "OK" "No transcript, approving"
    echo '{"decision": "approve"}'
    exit 0
fi

# Get the most recent assistant response from transcript
LAST_RESPONSE=$(tac "$TRANSCRIPT_PATH" | jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text' 2>/dev/null | head -1)

if [ -z "$LAST_RESPONSE" ]; then
    hook_log "OK" "No response text found"
    echo '{"decision": "approve"}'
    exit 0
fi

# Check for work-done indicators (past tense = actually did something)
WORK_DONE=false
if echo "$LAST_RESPONSE" | grep -qiE '\b(completed|fixed|updated|created|implemented|edited|wrote|modified|added|removed|refactored)\b'; then
    WORK_DONE=true
fi

# Check for user-choice context (offering options is OK)
USER_CHOICE_CONTEXT=false
if echo "$LAST_RESPONSE" | grep -qiE '(which would you prefer|do you want me to|should I|would you like)'; then
    USER_CHOICE_CONTEXT=true
fi

# Skip laziness check if work was done or offering choices
if [ "$WORK_DONE" = "true" ] || [ "$USER_CHOICE_CONTEXT" = "true" ]; then
    hook_log "OK" "Work done or choice offered, approving"
    echo '{"decision": "approve"}'
    exit 0
fi

# Lazy patterns to detect
LAZY_FOUND=""

# Suggestion patterns (telling user what to do instead of doing it)
if echo "$LAST_RESPONSE" | grep -qiE '\b(you could|you might want to|i recommend you|i suggest you|consider adding)\b'; then
    LAZY_FOUND="${LAZY_FOUND}suggestion; "
fi

# Delegation patterns (pushing work back to user)
if echo "$LAST_RESPONSE" | grep -qiE '\b(you need to|you have to|you.ll need to|make sure to|now you|go ahead and)\b'; then
    LAZY_FOUND="${LAZY_FOUND}delegation; "
fi

# Scope reduction patterns (avoiding work)
if echo "$LAST_RESPONSE" | grep -qiE '\b(for brevity|beyond the scope|i.ll leave|as an exercise|left as)\b'; then
    LAZY_FOUND="${LAZY_FOUND}scope_reduction; "
fi

if [ -n "$LAZY_FOUND" ]; then
    hook_log "BLOCK" "Lazy patterns: ${LAZY_FOUND}"
    echo "[LAZINESS CHECK] Detected: ${LAZY_FOUND}" >&2
    cat << EOF
{"decision": "block", "reason": "Lazy response patterns detected: ${LAZY_FOUND}"}
EOF
    exit 2
fi

hook_log "OK" "No lazy patterns (fallback)"
echo '{"decision": "approve"}'
exit 0
