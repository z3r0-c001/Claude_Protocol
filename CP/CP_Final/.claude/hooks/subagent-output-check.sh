#!/bin/bash
# PostToolUse hook: Check subagent output quality
# Receives JSON input via stdin with tool_output field

# Read JSON input from stdin
INPUT=$(cat)

# Extract output from tool
OUTPUT=$(echo "$INPUT" | jq -r '.tool_output // empty')

# If no output, pass through
if [ -z "$OUTPUT" ]; then
    exit 0
fi

issues=()

# Check for lazy suggestion patterns
if echo "$OUTPUT" | grep -qiE "you could|you might want to|consider adding|I recommend"; then
    issues+=("SUGGESTION: Subagent suggested instead of implementing")
fi

# Check for incomplete code
if echo "$OUTPUT" | grep -qE '// \.\.\.|# \.\.\.|TODO|FIXME|pass$'; then
    issues+=("INCOMPLETE: Subagent left placeholders")
fi

# Check for delegation patterns
if echo "$OUTPUT" | grep -qiE "you'll need to|make sure to|don't forget"; then
    issues+=("DELEGATION: Subagent delegated work")
fi

# Check for scope reduction
if echo "$OUTPUT" | grep -qiE "for brevity|to keep this short|I'll focus on"; then
    issues+=("SCOPE_REDUCTION: Subagent artificially limited scope")
fi

# Output result
if [ ${#issues[@]} -gt 0 ]; then
    issue_text=$(printf '%s; ' "${issues[@]}")
    echo "[SUBAGENT CHECK] Warning: $issue_text" >&2
    echo "{\"warning\": \"$issue_text\"}"
    exit 0
else
    exit 0
fi
