#!/bin/bash
# Session initialization for Claude Bootstrap Protocol
# Runs at SessionStart hook

CLAUDE_DIR="${CLAUDE_PROJECT_DIR}/.claude"
MEMORY_DIR="$CLAUDE_DIR/memory"

# Ensure directories exist
mkdir -p "$MEMORY_DIR"

# Initialize session tracking
TIMESTAMP=$(date -Iseconds)
cat > "$MEMORY_DIR/session-state.json" << EOF
{
  "session_start": "$TIMESTAMP",
  "edits": [],
  "violations": []
}
EOF

# Load environment variables if CLAUDE_ENV_FILE is set
if [ -n "$CLAUDE_ENV_FILE" ]; then
    # Add any project-specific environment here
    # echo 'export MY_VAR=value' >> "$CLAUDE_ENV_FILE"
    :
fi

# Output context for Claude (this gets added to context)
echo "Session started at $TIMESTAMP"
echo "Protocol hooks active: laziness-check, hallucination-check, dangerous-command-check"

exit 0
