#!/bin/bash
# UserPromptSubmit hook: Analyze query type and add context for Claude
# Receives JSON input via stdin with prompt field
# Output to stdout appears in conversation for UserPromptSubmit hooks

# Read JSON input from stdin
INPUT=$(cat)

# Extract prompt from JSON
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')

# If no prompt, allow through
if [ -z "$PROMPT" ]; then
    exit 0
fi

type="general"
context=""

# Determine query type
if echo "$PROMPT" | grep -qiE "code|function|implement|write.*script|create.*class|add.*feature"; then
    type="coding"
    context="[Query Analyzer: CODING task detected - implement fully, no placeholders]"
fi

if echo "$PROMPT" | grep -qiE "research|find out|what is|who is|when did|explain|how does"; then
    type="research"
    context="[Query Analyzer: RESEARCH task detected - verify facts before stating]"
fi

if echo "$PROMPT" | grep -qiE "review|check|audit|verify|validate"; then
    type="verification"
    context="[Query Analyzer: VERIFICATION task detected - be thorough and specific]"
fi

if echo "$PROMPT" | grep -qiE "fix|bug|error|broken|not working|failing"; then
    type="debugging"
    context="[Query Analyzer: DEBUGGING task detected - investigate root cause]"
fi

# Output context that will be visible to Claude
if [ -n "$context" ]; then
    echo "$context"
fi

exit 0
