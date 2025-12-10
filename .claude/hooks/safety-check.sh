#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
# Receives JSON input via stdin with tool_input field

# Source shared logger
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/hook-logger.sh"

# Read JSON input from stdin
INPUT=$(cat)

# Extract command from JSON
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow through
if [ -z "$COMMAND" ]; then
    hook_log "OK" "No command to check"
    cat << 'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
EOF
    exit 0
fi

# Log what we're checking
COMMAND_PREVIEW="${COMMAND:0:60}"
hook_log "INFO" "Checking: ${COMMAND_PREVIEW}..."

# Dangerous patterns
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \*"
    "sudo rm"
    "chmod 777"
    "curl.*\|.*sh"
    "wget.*\|.*sh"
    "curl.*\|.*bash"
    "wget.*\|.*bash"
    "mkfs"
    "dd if=.* of=/dev"
    ":(){:|:&};:"
    "> /dev/sd"
    "mv .* /dev/null"
    "chmod -R 777 /"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        hook_log "BLOCK" "Dangerous pattern: $pattern"
        cat << EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Dangerous command pattern detected: $pattern. This command could cause system damage."}}
EOF
        exit 0
    fi
done

hook_log "OK" "Command approved"
cat << 'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
EOF
exit 0
