#!/bin/bash
# PreToolUse hook: Block code with placeholder patterns
# Receives JSON input via stdin with tool_input field

# Read JSON input from stdin
INPUT=$(cat)

# Extract the content being written
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

# If no content, allow through
if [ -z "$CONTENT" ]; then
    echo '{"decision": "allow"}'
    exit 0
fi

# Check for placeholder patterns
issues=()

if echo "$CONTENT" | grep -qE '// \.\.\.'; then
    issues+=("JavaScript placeholder: // ...")
fi

if echo "$CONTENT" | grep -qE '# \.\.\.'; then
    issues+=("Python placeholder: # ...")
fi

if echo "$CONTENT" | grep -qE '\bTODO\b'; then
    issues+=("TODO comment found")
fi

if echo "$CONTENT" | grep -qE '\bFIXME\b'; then
    issues+=("FIXME comment found")
fi

if echo "$CONTENT" | grep -qE '\bpass$'; then
    issues+=("Empty pass statement")
fi

if echo "$CONTENT" | grep -qE 'NotImplementedError|raise NotImplemented'; then
    issues+=("NotImplementedError placeholder")
fi

if echo "$CONTENT" | grep -qE '\.\.\.rest|restOfCode|remainingCode'; then
    issues+=("Rest placeholder pattern")
fi

# Output result
if [ ${#issues[@]} -gt 0 ]; then
    issue_text=$(printf '%s, ' "${issues[@]}")
    # Exit code 2 = blocking error, stderr shown to user
    echo "[COMPLETENESS CHECK FAILED] $issue_text - No placeholders allowed!" >&2
    exit 2
else
    exit 0
fi
