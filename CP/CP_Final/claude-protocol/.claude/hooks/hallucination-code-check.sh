#!/bin/bash
# PostToolUse hook: Check for hallucination patterns
INPUT="$1"
if echo "$INPUT" | grep -qE "from ['\"][^'\"]*(-auto-|-magic-|-smart-|-easy-)"; then
    echo '{"warning": "Suspicious package names - verify they exist"}'
else
    echo '{"status": "ok"}'
fi
