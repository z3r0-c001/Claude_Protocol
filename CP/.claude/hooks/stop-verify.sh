#!/bin/bash
# Stop hook: Final verification and cleanup before session ends
# Cleans up watcher daemon and log file

# Source shared logger
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/hook-logger.sh" ]; then
    source "${SCRIPT_DIR}/hook-logger.sh"
else
    hook_log() { :; }
    notify_hook_start() { :; }
    notify_hook_result() { :; }
fi

notify_hook_start "Stop"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
FLAGS_DIR="${PROJECT_DIR}/.claude/flags"
LOGS_DIR="${PROJECT_DIR}/.claude/logs"
LOG_FILE="${LOGS_DIR}/watcher.log"

OUTPUT_MODE="${1:-json}"

# Cleanup function for watcher
cleanup_watcher() {
    hook_log "INFO" "Session ending - cleaning up watcher"
    
    # Kill watcher process if running
    if [ -f "${FLAGS_DIR}/watcher.pid" ]; then
        PID=$(cat "${FLAGS_DIR}/watcher.pid" 2>/dev/null)
        if [ -n "$PID" ]; then
            if kill -0 "$PID" 2>/dev/null; then
                hook_log "INFO" "Killing watcher daemon (PID: $PID)"
                kill "$PID" 2>/dev/null || true
                sleep 0.5
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
        rm -f "${FLAGS_DIR}/watcher.pid"
    fi
    
    # Kill any orphaned watcher processes
    pkill -f "session-watcher.py" 2>/dev/null || true
    
    # Kill tmux viewer session
    tmux kill-session -t claude-watcher 2>/dev/null || true
    
    # Remove socket file
    rm -f "${FLAGS_DIR}/watcher.socket" 2>/dev/null
    
    # Clear the log file completely
    if [ -f "$LOG_FILE" ]; then
        hook_log "INFO" "Clearing session log"
        > "$LOG_FILE"
    fi
    
    hook_log "OK" "Cleanup complete"
}

# Check if this looks like session end (empty input or special signal)
INPUT=$(cat 2>/dev/null || echo "{}")

# Check for session end indicators
IS_EXIT=$(echo "$INPUT" | jq -r '.session_end // .is_exit // false' 2>/dev/null)
if [ "$IS_EXIT" = "true" ]; then
    cleanup_watcher
fi

# Standard verification checks
ISSUES=""
STATUS="pass"

if [ -n "$CLAUDE_NEEDS_VERIFICATION" ]; then
    ISSUES="${ISSUES}{\"type\":\"verification_pending\",\"flag\":\"$CLAUDE_NEEDS_VERIFICATION\",\"severity\":\"suggest\"},"
    STATUS="suggest"
fi

if [ -n "$CLAUDE_MODIFIED_FILES" ]; then
    FILE_COUNT=$(echo "$CLAUDE_MODIFIED_FILES" | tr ',' '\n' | wc -l)
    if [ "$FILE_COUNT" -gt 5 ]; then
        ISSUES="${ISSUES}{\"type\":\"many_files_modified\",\"count\":$FILE_COUNT,\"severity\":\"suggest\",\"suggestion\":\"Consider reviewing changes before finalizing\"},"
        STATUS="suggest"
    fi
fi

if [ -n "$CLAUDE_RESEARCH_NEEDED" ]; then
    ISSUES="${ISSUES}{\"type\":\"research_incomplete\",\"topic\":\"$CLAUDE_RESEARCH_NEEDED\",\"severity\":\"warn\"},"
    STATUS="warning"
fi

ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
    if [ -z "$ISSUES" ]; then
        echo '{"hook":"stop-verify","status":"pass","verified":true}'
    else
        echo "{\"hook\":\"stop-verify\",\"status\":\"$STATUS\",\"verified\":false,\"issues\":[$ISSUES]}"
    fi
else
    if [ "$STATUS" != "pass" ]; then
        echo "Verification issues found"
    fi
fi

notify_hook_result "continue"
exit 0
