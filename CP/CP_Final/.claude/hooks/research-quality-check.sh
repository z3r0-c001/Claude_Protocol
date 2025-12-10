#!/bin/bash
# PostToolUse hook: Evaluate research source quality
# Receives JSON input via stdin with tool_output field

# Read JSON input from stdin
INPUT=$(cat)

# Extract output from tool
OUTPUT=$(echo "$INPUT" | jq -r '.tool_output // empty')

# If no output, pass through
if [ -z "$OUTPUT" ]; then
    exit 0
fi

warnings=()

# Check for low-tier sources
if echo "$OUTPUT" | grep -qiE "reddit\.com|quora\.com|yahoo answers|answers\.com"; then
    warnings+=("LOW_TIER: Reddit/Quora/Yahoo sources may be unreliable")
fi

# Check for outdated content (more than 2 years old in 2025)
if echo "$OUTPUT" | grep -qiE "2019|2020|2021|2022"; then
    warnings+=("OUTDATED: Content from 2022 or earlier may be stale")
fi

# Check for AI-generated content indicators
if echo "$OUTPUT" | grep -qiE "as an AI|I cannot|language model"; then
    warnings+=("AI_CONTENT: Source may be AI-generated, verify elsewhere")
fi

# Check for blog vs official docs
if echo "$OUTPUT" | grep -qiE "medium\.com|dev\.to|hashnode" && ! echo "$OUTPUT" | grep -qiE "official|documentation"; then
    warnings+=("UNOFFICIAL: Blog source - verify against official docs")
fi

# Output result
if [ ${#warnings[@]} -gt 0 ]; then
    warning_text=$(printf '%s; ' "${warnings[@]}")
    echo "[RESEARCH CHECK] Warning: $warning_text" >&2
    echo "{\"warning\": \"$warning_text\"}"
    exit 0
else
    exit 0
fi
