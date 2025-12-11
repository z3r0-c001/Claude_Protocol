#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
# Reads JSON from stdin, checks command against dangerous patterns
# Exit code 2 + stderr = BLOCK

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh" 2>/dev/null || {
    hook_log() { :; }
    notify_hook_start() { :; }
    notify_hook_result() { :; }
}

notify_hook_start "Bash"

# Read JSON input from stdin
INPUT=$(cat)

# Extract command
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# If no command, allow through
if [ -z "$COMMAND" ]; then
    notify_hook_result "continue"
    exit 0
fi

# Dangerous patterns - BLOCK immediately
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \*"
    "rm -rf \$HOME"
    "sudo rm -rf"
    "> /dev/sda"
    "> /dev/nvme"
    "mkfs\."
    "dd if=.* of=/dev/"
    "chmod 777 /"
    "chmod -R 777 /"
    "curl .* \| sh"
    "curl .* \| bash"
    "wget .* \| sh"
    "wget .* \| bash"
    "eval.*curl"
    "eval.*wget"
    "mv .* /dev/null"
    ":\\(\\)\\{.*:\\|:&.*\\};"
    ":\\(\\) *\\{ *:\\|:& *\\};"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        hook_log "BLOCK" "Dangerous command: $pattern"
        notify_hook_result "block"

        echo "BLOCKED: Dangerous command detected." >&2
        echo "Pattern matched: $pattern" >&2
        echo "This command could cause system damage and has been blocked." >&2
        exit 2
    fi
done

# Warning patterns - allow but log
WARNING_PATTERNS=(
    "sudo"
    "rm -rf"
    "git push.*--force"
    "git reset --hard"
    "npm publish"
    "docker rm"
    "docker rmi"
)

for pattern in "${WARNING_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        hook_log "WARN" "Risky command: $pattern"
    fi
done

hook_log "OK" "Command approved"
notify_hook_result "continue"
exit 0
