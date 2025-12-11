#!/bin/bash
# UserPromptSubmit hook: Inject laziness violation feedback
# Reads violation file and outputs as system message, then clears it

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh" 2>/dev/null || true

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
VIOLATION_FILE="${PROJECT_DIR}/.claude/flags/laziness-violation.md"

# Check if violation file exists
if [ -f "$VIOLATION_FILE" ]; then
    VIOLATION_CONTENT=$(cat "$VIOLATION_FILE")

    # Clear the file immediately
    rm -f "$VIOLATION_FILE"

    hook_log "WARN" "Injecting laziness violation feedback"

    # Output JSON with system message for Claude
    cat << EOF
{"decision": "continue", "systemMessage": "$VIOLATION_CONTENT"}
EOF
else
    echo '{"decision": "continue"}'
fi

exit 0
