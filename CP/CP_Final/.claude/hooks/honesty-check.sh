#!/bin/bash
# Stop hook: Check for honesty issues in assistant response
# Receives JSON input via stdin with transcript_path

# Read JSON input from stdin
INPUT=$(cat)

# Extract transcript path and read last assistant response
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

# Prevent infinite loop
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    exit 0
fi

# Get assistant response from transcript (last assistant message)
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
    RESPONSE=$(tail -100 "$TRANSCRIPT_PATH" 2>/dev/null | grep -o '"assistant":\s*"[^"]*"' | tail -1 | sed 's/"assistant":\s*"//' | sed 's/"$//')
else
    # Fallback - check if response passed directly
    RESPONSE=$(echo "$INPUT" | jq -r '.response // empty')
fi

# If no response found, allow stop
if [ -z "$RESPONSE" ]; then
    exit 0
fi

flags=""
issues=()

# Check for overconfident language
if echo "$RESPONSE" | grep -qiE "definitely|certainly|absolutely|always works|never fails|guaranteed"; then
    flags="overconfident;"
    issues+=("Overconfident language detected")
fi

# Check for missing uncertainty markers on claims
if echo "$RESPONSE" | grep -qiE "the (answer|solution|result|output) is" && ! echo "$RESPONSE" | grep -qiE "I believe|I think|probably|might|should|appears|seems"; then
    flags="${flags}missing_uncertainty;"
    issues+=("Missing uncertainty markers on definitive claims")
fi

# Output result
if [ -n "$flags" ]; then
    # Exit code 2 = blocking error, stderr shown to user
    echo "[HONESTY CHECK FAILED] ${issues[*]} - Add uncertainty markers to claims!" >&2
    exit 2
else
    exit 0
fi
