#!/bin/bash
# Template: PreToolUse Hook with Unified Logging
# Copy this file and customize for your hook
#
# Hook types:
#   PreToolUse - Before a tool executes (can block)
#   PostToolUse - After a tool executes (logging only)
#   UserPromptSubmit - Before user prompt processed
#   Stop - Before assistant response finishes (can block)

# Source shared logger - writes to .claude/logs/watcher.log
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/hook-logger.sh"

# Read JSON input from stdin (required by hook contract)
INPUT=$(cat)

# Extract relevant fields based on hook type
# PreToolUse example:
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // {}')

# Log what we're checking
hook_log "INFO" "Checking tool: ${TOOL_NAME}"

# Your validation logic here
# Example: check for something
SHOULD_BLOCK=false
BLOCK_REASON=""

# if [[ some_condition ]]; then
#     SHOULD_BLOCK=true
#     BLOCK_REASON="Reason for blocking"
# fi

if [ "$SHOULD_BLOCK" = "true" ]; then
    hook_log "BLOCK" "$BLOCK_REASON"
    cat << EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"$BLOCK_REASON"}}
EOF
    exit 0
fi

# Allow through
hook_log "OK" "Tool approved"
cat << 'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
EOF
exit 0
