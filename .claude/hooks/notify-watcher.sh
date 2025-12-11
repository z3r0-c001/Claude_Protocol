#!/bin/bash
# Notify the session watcher about hook events
# Usage: notify-watcher.sh <hook_name> [tool] [result]
#
# Examples:
#   notify-watcher.sh PreToolUse Write continue
#   notify-watcher.sh Stop "" block
#   notify-watcher.sh UserPromptSubmit

HOOK_NAME="${1:-unknown}"
TOOL="${2:-}"
RESULT="${3:-continue}"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SOCKET_PATH="${PROJECT_DIR}/.claude/flags/watcher.socket"

# Only notify if socket exists
[ ! -S "$SOCKET_PATH" ] && exit 0

# Build JSON payload
if [ -n "$TOOL" ]; then
    PAYLOAD="{\"cmd\":\"hook\",\"hook\":\"$HOOK_NAME\",\"tool\":\"$TOOL\",\"result\":\"$RESULT\"}"
else
    PAYLOAD="{\"cmd\":\"hook\",\"hook\":\"$HOOK_NAME\",\"result\":\"$RESULT\"}"
fi

# Send to socket (fire and forget)
echo "$PAYLOAD" | nc -U -q0 "$SOCKET_PATH" 2>/dev/null || true
