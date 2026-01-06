#!/bin/bash
# PostToolUse hook: Track file edits
# Reads JSON from stdin with tool_input.file_path

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh" 2>/dev/null || { hook_log() { :; }; }

# Read JSON input from stdin
INPUT=$(cat)

# Extract file path from tool_input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Track file
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
TRACKER_FILE="${PROJECT_DIR}/.claude/memory/session-edits.json"
mkdir -p "$(dirname "$TRACKER_FILE")"

TIMESTAMP=$(date -Iseconds)

if [ -f "$TRACKER_FILE" ] && [ -s "$TRACKER_FILE" ]; then
    # Check if already tracked
    if ! jq -e ".files[] | select(.path == \"$FILE_PATH\")" "$TRACKER_FILE" >/dev/null 2>&1; then
        # Add to existing using jq for proper JSON handling
        jq --arg path "$FILE_PATH" --arg ts "$TIMESTAMP" \
           '.files += [{"path": $path, "timestamp": $ts}]' "$TRACKER_FILE" > "${TRACKER_FILE}.tmp" && \
        mv "${TRACKER_FILE}.tmp" "$TRACKER_FILE" 2>/dev/null || \
        echo "{\"session_start\":\"$TIMESTAMP\",\"files\":[{\"path\":\"$FILE_PATH\",\"timestamp\":\"$TIMESTAMP\"}]}" > "$TRACKER_FILE"
    fi
else
    echo "{\"session_start\":\"$TIMESTAMP\",\"files\":[{\"path\":\"$FILE_PATH\",\"timestamp\":\"$TIMESTAMP\"}]}" > "$TRACKER_FILE"
fi

# Output JSON for Claude Code
echo '{"continue": true}'
exit 0
