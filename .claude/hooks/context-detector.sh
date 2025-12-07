#!/bin/bash
# PostToolUse hook: Detect context and suggest agents
# Auto-invokes agents based on file patterns

FILE_PATH="$1"
OUTPUT_MODE="${2:-json}"

SUGGESTIONS=""

# Pattern-based agent suggestions
# Format: pattern:agent:reason

RULES=(
  "auth|password|token|credential|login|session:security-scanner:File contains authentication logic"
  "encrypt|decrypt|hash|crypto|secret:security-scanner:File contains cryptographic operations"
  "api|endpoint|route|controller:security-scanner:File handles API endpoints"
  "test|spec|__tests__|.test.|.spec.:test-coverage-enforcer:Test file modified"
  "package.json|requirements.txt|Cargo.toml|go.mod:dependency-auditor:Dependency file modified"
  "Dockerfile|docker-compose|kubernetes|k8s:security-scanner:Container configuration modified"
  "sql|query|database|migration:security-scanner:Database operations detected"
  "config|settings|env:security-scanner:Configuration file modified"
  "performance|cache|optimize|index:performance-analyzer:Performance-related code"
  "README|CHANGELOG|docs/:fact-checker:Documentation modified"
)

# Check each rule
for rule in "${RULES[@]}"; do
  pattern="${rule%%:*}"
  rest="${rule#*:}"
  agent="${rest%%:*}"
  reason="${rest#*:}"

  if echo "$FILE_PATH" | grep -qiE "$pattern"; then
    SUGGESTIONS="${SUGGESTIONS}{\"agent\":\"$agent\",\"reason\":\"$reason\",\"file\":\"$FILE_PATH\"},"
  fi
done

# Remove trailing comma
SUGGESTIONS="${SUGGESTIONS%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$SUGGESTIONS" ]; then
    echo "{\"hook\":\"context-detector\",\"status\":\"pass\",\"file\":\"$FILE_PATH\",\"agent_suggestions\":[]}"
  else
    echo "{\"hook\":\"context-detector\",\"status\":\"suggest\",\"file\":\"$FILE_PATH\",\"agent_suggestions\":[$SUGGESTIONS]}"
  fi
else
  if [ -n "$SUGGESTIONS" ]; then
    echo "Suggested agents for $FILE_PATH:"
    echo "$SUGGESTIONS" | tr ',' '\n'
  fi
fi

exit 0
