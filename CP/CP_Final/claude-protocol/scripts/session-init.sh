#!/bin/bash
# SessionStart hook: Initialize session state
mkdir -p memories

# Load previous state if exists
if [ -f "memories/protocol-state.json" ]; then
    echo "Previous session state found"
    cat memories/protocol-state.json
fi

# Record session start
echo "{\"session_start\": \"$(date -Iseconds)\"}" > memories/current-session.json
