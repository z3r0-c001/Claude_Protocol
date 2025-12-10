#!/bin/bash
# Spawn the session watcher with a visible log tail
#
# Usage: spawn-watcher.sh [session_id]
#
# Environment:
#   CLAUDE_PROJECT_DIR - Project directory (default: pwd)
#   CLAUDE_SESSION_ID  - Session ID (optional)

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SESSION_ID="${CLAUDE_SESSION_ID:-$1}"
FLAGS_DIR="${PROJECT_DIR}/.claude/flags"
LOGS_DIR="${PROJECT_DIR}/.claude/logs"
WATCHER_DIR="${PROJECT_DIR}/.claude/watcher"
WATCHER_SCRIPT="${WATCHER_DIR}/session-watcher.py"
LOG_FILE="${LOGS_DIR}/watcher.log"

# Ensure directories exist
mkdir -p "$FLAGS_DIR" "$LOGS_DIR"

# Check if watcher script exists
if [ ! -f "$WATCHER_SCRIPT" ]; then
    echo "Error: Watcher script not found at $WATCHER_SCRIPT" >&2
    exit 1
fi

# Check if already running
if [ -f "${FLAGS_DIR}/watcher.pid" ]; then
    PID=$(cat "${FLAGS_DIR}/watcher.pid" 2>/dev/null)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "Watcher already running (PID: $PID)"
        exit 0
    fi
    # Stale PID file, remove it
    rm -f "${FLAGS_DIR}/watcher.pid"
fi

# Clear old log
> "$LOG_FILE"

# Build watcher command
WATCHER_CMD="CLAUDE_PROJECT_DIR='$PROJECT_DIR'"
if [ -n "$SESSION_ID" ]; then
    WATCHER_CMD="$WATCHER_CMD CLAUDE_SESSION_ID='$SESSION_ID'"
fi
WATCHER_CMD="$WATCHER_CMD python3 '$WATCHER_SCRIPT'"

# Start watcher daemon in background FIRST
nohup bash -c "$WATCHER_CMD" >> "$LOG_FILE" 2>&1 &
WATCHER_PID=$!
echo "Watcher daemon started (PID: $WATCHER_PID)"

# Give it a moment to start
sleep 0.5

# Now open a terminal/pane to tail the log
TAIL_CMD="tail -f '$LOG_FILE'"

if [ -n "$TMUX" ]; then
    # Inside tmux - create new pane on the right with tail -f
    tmux split-window -h -l 50 "$TAIL_CMD"
    # Switch back to original pane
    tmux select-pane -t :.!
    echo "Log viewer started in tmux pane"

elif command -v tmux &>/dev/null; then
    # Not in tmux - kill any existing viewer session first
    tmux kill-session -t claude-watcher 2>/dev/null || true

    # Create detached tmux session with tail -f
    tmux new-session -d -s claude-watcher "$TAIL_CMD"
    echo "Log viewer started in tmux session 'claude-watcher'"
    echo "Attach with: tmux attach -t claude-watcher"

else
    echo "No tmux available"
    echo "View log manually: tail -f $LOG_FILE"
fi

echo "Watcher log: $LOG_FILE"
exit 0
