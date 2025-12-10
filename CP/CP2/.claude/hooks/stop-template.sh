#!/bin/bash
# Template: Stop Hook with Unified Logging
# Validates assistant response before completion
#
# Stop hooks can use the Session Watcher for real-time validation

# Source shared logger
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/hook-logger.sh"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
IPC_SCRIPT="${PROJECT_DIR}/.claude/watcher/ipc.sh"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"decision": "approve"}'
    exit 0
fi

hook_log "INFO" "Checking response"

# Try watcher first (has real-time validation)
if [ -x "$IPC_SCRIPT" ]; then
    WATCHER_RESPONSE=$("$IPC_SCRIPT" get_pending 2>/dev/null)
    
    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == true' >/dev/null 2>&1; then
        # Filter for your specific issue types
        # Change "MY_RULE" to match your validation rule type
        MY_ISSUES=$(echo "$WATCHER_RESPONSE" | jq -r '.issues[] | select(.type == "MY_RULE") | .pattern' 2>/dev/null | tr '\n' '; ')
        
        if [ -n "$MY_ISSUES" ]; then
            hook_log "BLOCK" "Issues found: ${MY_ISSUES}"
            echo "[MY HOOK BLOCK] ${MY_ISSUES}" >&2
            cat << EOF
{"decision": "block", "reason": "Validation failed: ${MY_ISSUES}"}
EOF
            exit 2
        fi
    fi
    
    # Watcher running, no issues
    if echo "$WATCHER_RESPONSE" | jq -e '.has_issues == false' >/dev/null 2>&1; then
        hook_log "OK" "No issues (watcher)"
        echo '{"decision": "approve"}'
        exit 0
    fi
fi

# Fallback: watcher not available
# Add your own transcript-based validation here if needed
hook_log "OK" "Approved (fallback)"
echo '{"decision": "approve"}'
exit 0
