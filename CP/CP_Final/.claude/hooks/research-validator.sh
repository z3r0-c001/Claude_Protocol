#!/bin/bash
# SubagentStop hook: Validate research completeness
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

# Count sources (URLs)
sources=$(echo "$OUTPUT" | grep -oE "https?://" | wc -l)
sources=${sources:-0}
if [ "$sources" -lt 2 ]; then
    issues+=("FEW_SOURCES: Only $sources source(s) found - need more verification")
fi

# Check for research failure indicators
if echo "$OUTPUT" | grep -qiE "could not find|no results|unable to|not found|doesn't exist"; then
    issues+=("INCOMPLETE: Research may be incomplete")
fi

# Check for speculation without evidence
if echo "$OUTPUT" | grep -qiE "I assume|I think|probably|might be|it seems"; then
    if [ "$sources" -lt 1 ]; then
        issues+=("SPECULATION: Claims without source verification")
    fi
fi

# Check for conflicting information
if echo "$OUTPUT" | grep -qiE "however|but.*different|conflicting|contradicts"; then
    issues+=("CONFLICTING: Found conflicting information - verify further")
fi

# Output result
if [ ${#issues[@]} -gt 0 ]; then
    issue_text=$(printf '%s; ' "${issues[@]}")
    echo "[RESEARCH VALIDATOR] Warning: $issue_text" >&2
    echo "{\"warning\": \"$issue_text\"}"
    exit 0
else
    exit 0
fi
