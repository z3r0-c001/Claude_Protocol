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

# Guard file for spawn-watcher-hook.sh
GUARD_FILE="${FLAGS_DIR}/watcher-spawned.guard"

# Check if watcher script exists
if [ ! -f "$WATCHER_SCRIPT" ]; then
    echo "Error: Watcher script not found at $WATCHER_SCRIPT" >&2
    exit 1
fi

# Kill any existing watcher processes first (clean slate)
if [ -f "${FLAGS_DIR}/watcher.pid" ]; then
    OLD_PID=$(cat "${FLAGS_DIR}/watcher.pid" 2>/dev/null)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Killing old watcher (PID: $OLD_PID)"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 0.3
        kill -9 "$OLD_PID" 2>/dev/null || true
    fi
    rm -f "${FLAGS_DIR}/watcher.pid"
fi

# NOTE: Don't clear guard file here - it's managed by spawn-watcher-hook.sh
# The hook creates the guard AFTER calling this script

# Kill any orphaned watcher processes
pkill -f "session-watcher.py" 2>/dev/null || true

# Kill old tmux viewer session
tmux kill-session -t claude-watcher 2>/dev/null || true

# Remove stale socket
rm -f "${FLAGS_DIR}/watcher.socket" 2>/dev/null

# Clear log file completely for fresh session
> "$LOG_FILE"
echo "[$(date '+%H:%M:%S')] Session started - log cleared" >> "$LOG_FILE"

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

# Check if we're on WSL and can use Windows Terminal
if grep -qi microsoft /proc/version 2>/dev/null && command -v wt.exe &>/dev/null; then
    # WSL - spawn Windows Terminal window with tail -f
    wt.exe -w 0 nt --title "Claude Watcher" wsl.exe -d "$WSL_DISTRO_NAME" --cd "$PROJECT_DIR" -- bash -c "$TAIL_CMD" &
    echo "Log viewer started in Windows Terminal"

elif [ -n "$TMUX" ]; then
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
