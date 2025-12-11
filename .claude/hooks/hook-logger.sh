#!/bin/bash
# Shared logging for all hooks
# Source this file: source "$(dirname "$0")/hook-logger.sh"
#
# Usage:
#   hook_log "INFO" "Message here"
#   hook_log "WARN" "Warning message"
#   hook_log "BLOCK" "Blocked because..."
#   hook_log "OK" "Approved"

PROJECT_DIR="$(pwd)"
HOOK_LOG="${PROJECT_DIR}/.claude/logs/hooks.log"

# Ensure log directory exists
mkdir -p "$(dirname "$HOOK_LOG")" 2>/dev/null

# Get hook name from script name
HOOK_NAME="${HOOK_NAME:-$(basename "$0" .sh)}"

hook_log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Format: [timestamp] [LEVEL] [hook-name] message
    local log_line="[${timestamp}] [${level}] [${HOOK_NAME}] ${message}"

    # Append to hook log (silently fail if can't write)
    echo "$log_line" >> "$HOOK_LOG" 2>/dev/null || true
}

# Stub functions for compatibility (watcher not included in CP)
notify_hook_start() { :; }
notify_hook_result() { :; }
