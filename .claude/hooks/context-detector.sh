#!/bin/bash
# PostToolUse hook: Detect context and suggest agents
# Reads JSON from stdin, outputs context via hookSpecificOutput

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="context-detector"

# Read JSON input from stdin
INPUT=$(cat)

# Extract file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

hook_status "$HOOK_NAME" "CHECKING" "$(basename "$FILE_PATH")"

SUGGESTIONS=""

# Pattern-based agent suggestions
declare -A RULES=(
    ["auth|password|token|credential|login|session"]="security-scanner"
    ["encrypt|decrypt|hash|crypto|secret"]="security-scanner"
    ["test|spec|__tests__|.test.|.spec."]="test-coverage-enforcer"
    ["package.json|requirements.txt|Cargo.toml|go.mod"]="dependency-auditor"
    ["performance|cache|optimize|index"]="performance-analyzer"
)

for pattern in "${!RULES[@]}"; do
    if echo "$FILE_PATH" | grep -qiE "$pattern"; then
        agent="${RULES[$pattern]}"
        SUGGESTIONS="${SUGGESTIONS}${agent}, "
    fi
done

# Remove trailing comma
SUGGESTIONS="${SUGGESTIONS%, }"

if [ -n "$SUGGESTIONS" ]; then
    hook_status "$HOOK_NAME" "OK" "Suggest: $SUGGESTIONS"
    echo "{\"continue\": true, \"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"AGENT SUGGESTION for $FILE_PATH: Consider running $SUGGESTIONS\"}}"
else
    hook_status "$HOOK_NAME" "OK" "No suggestions"
    echo '{"continue": true}'
fi

exit 0
