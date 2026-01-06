#!/bin/bash
# Stop hook: Final verification before session ends
# Reads JSON from stdin, outputs JSON to stdout if blocking needed

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="stop-verify"

hook_status "$HOOK_NAME" "RUNNING" "Final check"

# Read JSON input from stdin
INPUT=$(cat)

# Prevent infinite loops
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"continue": true}'
    exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
FLAGS_DIR="${PROJECT_DIR}/.claude/flags"

# Check for pending verification flags
ISSUES=""

if [ -n "$CLAUDE_NEEDS_VERIFICATION" ]; then
    ISSUES="${ISSUES}verification_pending; "
fi

if [ -n "$CLAUDE_RESEARCH_NEEDED" ]; then
    ISSUES="${ISSUES}research_incomplete; "
fi

# Check if too many files modified without review
if [ -n "$CLAUDE_MODIFIED_FILES" ]; then
    FILE_COUNT=$(echo "$CLAUDE_MODIFIED_FILES" | tr ',' '\n' | wc -l)
    if [ "$FILE_COUNT" -gt 10 ]; then
        ISSUES="${ISSUES}many_files_modified($FILE_COUNT); "
    fi
fi

if [ -n "$ISSUES" ]; then
    hook_status "$HOOK_NAME" "BLOCK" "Issues: ${ISSUES}"
    cat << ENDJSON
{"decision": "block", "reason": "VERIFICATION NEEDED: ${ISSUES}. Please address these before completing."}
ENDJSON
    exit 0
fi

# No issues
hook_status "$HOOK_NAME" "OK" "Verified"
echo '{"continue": true}'
exit 0
