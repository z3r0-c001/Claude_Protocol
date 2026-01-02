#!/bin/bash
# PostToolUse hook: Track file edits
# Reads JSON from stdin with tool_input.file_path

set -o pipefail

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

# Use jq for safe JSON construction (prevents injection via special chars in paths)
if [ -f "$TRACKER_FILE" ] && [ -s "$TRACKER_FILE" ]; then
    # Check if already tracked using jq for safe comparison
    if ! jq -e --arg path "$FILE_PATH" '.files[]? | select(.path == $path)' "$TRACKER_FILE" > /dev/null 2>&1; then
        # Add to existing using jq for safe JSON manipulation
        jq --arg path "$FILE_PATH" --arg ts "$TIMESTAMP" \
            '.files += [{"path": $path, "timestamp": $ts}]' \
            "$TRACKER_FILE" > "${TRACKER_FILE}.tmp" && mv "${TRACKER_FILE}.tmp" "$TRACKER_FILE"
    fi
else
    # Create new tracker file using jq
    jq -n --arg path "$FILE_PATH" --arg ts "$TIMESTAMP" \
        '{session_start: $ts, files: [{path: $path, timestamp: $ts}]}' > "$TRACKER_FILE"
fi

# Output JSON for Claude Code
echo '{"continue": true}'
exit 0
