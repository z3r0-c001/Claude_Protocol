#!/bin/bash
# Spawn Session Watcher Hook (UserPromptSubmit)
#
# Auto-spawns the session watcher on first user prompt.
# Uses a guard file to prevent respawning within the same session.
#
# The guard file is cleared on session exit via the watcher itself.

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Source shared logging (but handle case where it might not exist yet)
SCRIPT_DIR="$(dirname "$0")"
if [ -f "$SCRIPT_DIR/hook-logger.sh" ]; then
    source "$SCRIPT_DIR/hook-logger.sh"
    notify_hook_start ""
else
    notify_hook_result() { :; }
fi
FLAGS_DIR="${PROJECT_DIR}/.claude/flags"
LOGS_DIR="${PROJECT_DIR}/.claude/logs"
WATCHER_DIR="${PROJECT_DIR}/.claude/watcher"
SPAWN_SCRIPT="${WATCHER_DIR}/spawn-watcher.sh"
GUARD_FILE="${FLAGS_DIR}/watcher-spawned.guard"
PID_FILE="${FLAGS_DIR}/watcher.pid"

# Ensure directories exist
mkdir -p "$FLAGS_DIR" "$LOGS_DIR"

# Check if spawn script exists
if [ ! -f "$SPAWN_SCRIPT" ]; then
    # Silent exit - watcher not configured
    notify_hook_result "continue"
    echo '{"decision":"continue"}'
    exit 0
fi

# Function to check if watcher is actually running
watcher_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Check guard file - but also verify watcher is actually running
if [ -f "$GUARD_FILE" ]; then
    if watcher_running; then
        # Already spawned and running - skip
        notify_hook_result "continue"
        echo '{"decision":"continue"}'
        exit 0
    else
        # Guard exists but watcher died - remove guard and respawn
        rm -f "$GUARD_FILE"
    fi
fi

# Spawn the watcher
bash "$SPAWN_SCRIPT" >/dev/null 2>&1 &

# Create guard file with timestamp
echo "$(date -Iseconds)" > "$GUARD_FILE"

# Output success message
notify_hook_result "continue"
echo '{"decision":"continue","reason":"Session watcher spawned"}'
exit 0
