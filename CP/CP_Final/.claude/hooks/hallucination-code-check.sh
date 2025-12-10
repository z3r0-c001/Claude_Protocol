#!/bin/bash
# PostToolUse hook: Check for hallucination patterns in written code
# Receives JSON input via stdin with tool_input and tool_output fields

# Read JSON input from stdin
INPUT=$(cat)

# Extract content from tool input
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')

# If no content, pass through
if [ -z "$CONTENT" ]; then
    exit 0
fi

issues=()

# Check for suspicious auto-generated package names
if echo "$CONTENT" | grep -qE "from ['\"][^'\"]*(-auto-|-magic-|-smart-|-easy-|auto[A-Z]|magic[A-Z])"; then
    issues+=("Suspicious package name pattern")
fi

# Check for non-existent popular package variations
if echo "$CONTENT" | grep -qE "require\(['\"]express-magic|import.*from ['\"]react-auto-|from lodash-extra"; then
    issues+=("Possibly hallucinated package")
fi

# Check for API patterns that look made-up
if echo "$CONTENT" | grep -qE "\.autoGenerate\(|\.magicCreate\(|\.smartBuild\("; then
    issues+=("Suspicious API method pattern")
fi

# Check for URLs that look hallucinated
if echo "$CONTENT" | grep -qE "api\.example\.ai|api\.generated\.|service\.auto-"; then
    issues+=("Potentially hallucinated URL/endpoint")
fi

# Output result
if [ ${#issues[@]} -gt 0 ]; then
    issue_text=$(printf '%s; ' "${issues[@]}")
    echo "[HALLUCINATION CHECK] Warning: $issue_text - verify these exist" >&2
    echo "{\"warning\": \"$issue_text - verify packages/APIs exist before using\"}"
    exit 0
else
    exit 0
fi
