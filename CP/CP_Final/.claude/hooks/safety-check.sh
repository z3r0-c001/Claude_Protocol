#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
# Receives JSON input via stdin with tool_input field

# Read JSON input from stdin
INPUT=$(cat)

# Extract command from JSON
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# If no command, allow through
if [ -z "$COMMAND" ]; then
    echo '{"decision": "allow"}'
    exit 0
fi

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
        echo "[SAFETY CHECK] Blocking dangerous command: $pattern matched" >&2
        cat << EOF
{
    "decision": "block",
    "reason": "Dangerous command pattern detected: $pattern. This command could cause system damage."
}
EOF
        exit 0
    fi
done

echo '{"decision": "allow"}'
exit 0
