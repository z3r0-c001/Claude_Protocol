#!/bin/bash
# SessionEnd hook: Clean up session
if [ -f "memories/current-session.json" ]; then
    # Merge into protocol state
    echo "{\"last_session\": \"$(date -Iseconds)\"}" > memories/protocol-state.json
    rm memories/current-session.json
fi
