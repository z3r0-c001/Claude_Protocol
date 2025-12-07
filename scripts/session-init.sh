#!/bin/bash
# Session initialization script
# Called at the start of each Claude session

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$PROJECT_DIR/.claude"
MEMORY_DIR="$CLAUDE_DIR/memory"

# Ensure memory directory exists
mkdir -p "$MEMORY_DIR"

# Initialize session tracker
SESSION_FILE="$MEMORY_DIR/session-edits.json"
TIMESTAMP=$(date -Iseconds)

cat > "$SESSION_FILE" << EOF
{
  "session_start": "$TIMESTAMP",
  "files": []
}
EOF

# Load protocol state
STATE_FILE="$MEMORY_DIR/protocol-state.json"
if [ -f "$STATE_FILE" ]; then
  echo "Protocol state loaded from: $STATE_FILE"
else
  # Initialize protocol state
  cat > "$STATE_FILE" << EOF
{
  "entries": [],
  "updated": "$TIMESTAMP"
}
EOF
  echo "Protocol state initialized"
fi

# Check for pending actions from last session
PENDING_FILE="$MEMORY_DIR/pending-actions.json"
if [ -f "$PENDING_FILE" ]; then
  PENDING_COUNT=$(grep -c '"action"' "$PENDING_FILE" 2>/dev/null || echo "0")
  if [ "$PENDING_COUNT" -gt 0 ]; then
    echo "Note: $PENDING_COUNT pending actions from last session"
  fi
fi

# Report status
echo ""
echo "Session initialized at: $TIMESTAMP"
echo "Memory directory: $MEMORY_DIR"
echo ""
