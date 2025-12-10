#!/bin/bash
# IPC helper for hooks to communicate with watcher
#
# Usage: ipc.sh <command>
#
# Commands:
#   status       - Check if watcher is running
#   get_pending  - Get pending validation issues
#   clear_pending - Clear pending issues
#
# Returns JSON response or error

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SOCKET_PATH="${PROJECT_DIR}/.claude/flags/watcher.socket"

CMD="${1:-status}"

# Check if socket exists
if [ ! -S "$SOCKET_PATH" ]; then
    echo '{"error": "watcher not running", "running": false}'
    exit 1
fi

# Send command via netcat (nc)
# Use timeout to avoid hanging
RESPONSE=$(echo "{\"cmd\": \"$CMD\"}" | timeout 2 nc -U "$SOCKET_PATH" 2>/dev/null)

if [ -z "$RESPONSE" ]; then
    echo '{"error": "no response from watcher", "running": false}'
    exit 1
fi

echo "$RESPONSE"
exit 0
