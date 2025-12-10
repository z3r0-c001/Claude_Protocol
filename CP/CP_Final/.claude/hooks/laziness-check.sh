#!/bin/bash
# Stop hook: Check for lazy response patterns (suggestions instead of implementation)
# Receives JSON input via stdin with transcript_path

# Read JSON input from stdin
INPUT=$(cat)

# Extract transcript path and check for infinite loop prevention
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // empty')
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

# Prevent infinite loop
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    exit 0
fi

# Get assistant response from transcript (last assistant message)
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
    RESPONSE=$(tail -200 "$TRANSCRIPT_PATH" 2>/dev/null)
else
    RESPONSE=$(echo "$INPUT" | jq -r '.response // empty')
fi

# If no response found, allow stop
if [ -z "$RESPONSE" ]; then
    exit 0
fi

issues=()

# Check for suggestion patterns (lazy - not implementing)
if echo "$RESPONSE" | grep -qiE "you could|you might want to|consider adding|I recommend you|I suggest you"; then
    issues+=("SUGGESTION: Telling user what to do instead of doing it")
fi

# Check for placeholder code
if echo "$RESPONSE" | grep -qE '// \.\.\.|# \.\.\.|TODO|FIXME|pass$|NotImplementedError|\.\.\.rest'; then
    issues+=("PLACEHOLDER: Incomplete code with placeholders")
fi

# Check for delegation patterns
if echo "$RESPONSE" | grep -qiE "you'll need to|make sure to|don't forget to|you should then"; then
    issues+=("DELEGATION: Delegating work back to user")
fi

# Check for scope reduction
if echo "$RESPONSE" | grep -qiE "for brevity|to keep this short|I'll focus on|I won't cover|beyond the scope|I'll leave"; then
    issues+=("SCOPE_REDUCTION: Artificially limiting scope of work")
fi

# Output result
if [ ${#issues[@]} -gt 0 ]; then
    issue_text=$(printf '%s; ' "${issues[@]}")
    # Exit code 2 = blocking error, stderr shown to user
    echo "[LAZINESS CHECK FAILED] $issue_text - Implement directly instead of suggesting!" >&2
    exit 2
else
    exit 0
fi
