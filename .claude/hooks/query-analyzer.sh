#!/bin/bash
# UserPromptSubmit hook: Analyze user query
# Detects intent and suggests appropriate agents/skills

QUERY="$1"
OUTPUT_MODE="${2:-json}"

SUGGESTIONS=""
INTENT=""

# Intent detection patterns
# Security-related
if echo "$QUERY" | grep -qiE "security|vulnerability|secure|attack|exploit|injection|xss|csrf|auth"; then
  INTENT="security"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"security-scanner\",\"reason\":\"Security-related query detected\"},"
fi

# Performance-related
if echo "$QUERY" | grep -qiE "performance|slow|optimize|fast|speed|latency|memory|cpu"; then
  INTENT="performance"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"performance-analyzer\",\"reason\":\"Performance-related query detected\"},"
fi

# Testing-related
if echo "$QUERY" | grep -qiE "test|coverage|spec|unit|integration|e2e"; then
  INTENT="testing"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"test-coverage-enforcer\",\"reason\":\"Testing-related query detected\"},"
fi

# Architecture-related
if echo "$QUERY" | grep -qiE "architect|design|pattern|structure|refactor|redesign"; then
  INTENT="architecture"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"architect\",\"reason\":\"Architecture-related query detected\"},"
fi

# Documentation-related
if echo "$QUERY" | grep -qiE "document|readme|api doc|comment|explain"; then
  INTENT="documentation"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"skill\",\"name\":\"dev-guidelines\",\"reason\":\"Documentation-related query detected\"},"
fi

# Research-related
if echo "$QUERY" | grep -qiE "research|find out|look up|search|what is|how does"; then
  INTENT="research"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"research-analyzer\",\"reason\":\"Research query detected\"},"
fi

# Verification-related
if echo "$QUERY" | grep -qiE "verify|check|validate|confirm|is this correct"; then
  INTENT="verification"
  SUGGESTIONS="${SUGGESTIONS}{\"type\":\"agent\",\"name\":\"fact-checker\",\"reason\":\"Verification query detected\"},"
fi

# Remove trailing comma
SUGGESTIONS="${SUGGESTIONS%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$SUGGESTIONS" ]; then
    echo "{\"hook\":\"query-analyzer\",\"status\":\"pass\",\"intent\":\"general\"}"
  else
    echo "{\"hook\":\"query-analyzer\",\"status\":\"suggest\",\"intent\":\"$INTENT\",\"suggestions\":[$SUGGESTIONS]}"
  fi
else
  if [ -n "$INTENT" ]; then
    echo "Query intent: $INTENT"
  fi
fi

exit 0
