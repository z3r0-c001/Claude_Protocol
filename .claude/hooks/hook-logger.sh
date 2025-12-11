#!/bin/bash
# Shared logging for all hooks
# Source this file: source "$(dirname "$0")/hook-logger.sh"
#
# Usage:
#   hook_log "INFO" "Message here"
#   hook_log "WARN" "Warning message"
#   hook_log "BLOCK" "Blocked because..."
#   hook_log "OK" "Approved"
#
# Auto-notify on source:
#   notify_hook_start [tool_name]  - Call at start of hook
#   notify_hook_result "continue"  - Call before exit with result

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
WATCHER_LOG="${PROJECT_DIR}/.claude/logs/watcher.log"
SOCKET_PATH="${PROJECT_DIR}/.claude/flags/watcher.socket"

# Ensure log directory exists
mkdir -p "$(dirname "$WATCHER_LOG")"

# Get hook name from script name
HOOK_NAME="${HOOK_NAME:-$(basename "$0" .sh)}"

# Track tool name for notify
_HOOK_TOOL=""

# Color codes
COLOR_RESET="\033[0m"
COLOR_INFO="\033[36m"    # Cyan
COLOR_WARN="\033[33m"    # Yellow
COLOR_ERROR="\033[31m"   # Red
COLOR_BLOCK="\033[31;1m" # Bold Red
COLOR_OK="\033[32m"      # Green
COLOR_EVENT="\033[35m"   # Magenta

hook_log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%H:%M:%S.%3N')

    local color=""
    case "$level" in
        INFO)  color="$COLOR_INFO" ;;
        WARN)  color="$COLOR_WARN" ;;
        ERROR) color="$COLOR_ERROR" ;;
        BLOCK) color="$COLOR_BLOCK" ;;
        OK)    color="$COLOR_OK" ;;
        EVENT) color="$COLOR_EVENT" ;;
    esac

    # Format: [timestamp] [LEVEL] [hook-name] message
    local log_line="[${timestamp}] ${color}[${level}]${COLOR_RESET} [${HOOK_NAME}] ${message}"

    # Append to watcher log
    echo -e "$log_line" >> "$WATCHER_LOG"
}

# Notify watcher about hook event via socket
notify_watcher() {
    local hook="$1"
    local tool="$2"
    local result="$3"

    [ ! -S "$SOCKET_PATH" ] && return 0

    local payload
    if [ -n "$tool" ]; then
        payload="{\"cmd\":\"hook\",\"hook\":\"$hook\",\"tool\":\"$tool\",\"result\":\"$result\"}"
    else
        payload="{\"cmd\":\"hook\",\"hook\":\"$hook\",\"result\":\"$result\"}"
    fi

    echo "$payload" | nc -U -q0 "$SOCKET_PATH" 2>/dev/null || true
}

# Call at start of hook to register tool
notify_hook_start() {
    _HOOK_TOOL="${1:-}"
}

# Call before exit to send result to watcher
notify_hook_result() {
    local result="${1:-continue}"
    notify_watcher "$HOOK_NAME" "$_HOOK_TOOL" "$result"
}
