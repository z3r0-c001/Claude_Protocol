#!/bin/bash
# Stop hook: Check for honesty issues in responses
# Flags overconfident or uncertain language

# Source shared logging
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh"
notify_hook_start "Stop"

RESPONSE="$1"
OUTPUT_MODE="${2:-json}"

FLAGS=""
STATUS="pass"

# Check for overconfident language
OVERCONFIDENT_PATTERNS=(
  "definitely"
  "certainly"
  "absolutely"
  "always"
  "never"
  "guaranteed"
  "100%"
  "without question"
  "no doubt"
)

for pattern in "${OVERCONFIDENT_PATTERNS[@]}"; do
  if echo "$RESPONSE" | grep -qiE "\b$pattern\b"; then
    FLAGS="${FLAGS}overconfident:$pattern;"
    STATUS="warning"
  fi
done

# Check for missing uncertainty markers (when they should be present)
# Only flag if response makes claims without hedging
if ! echo "$RESPONSE" | grep -qiE "I believe|I think|probably|might be|could be|it appears|seems like|based on|according to"; then
  # Check if the response makes factual claims
  if echo "$RESPONSE" | grep -qiE "is a|are the|will be|should be|must be|this is|that is"; then
    FLAGS="${FLAGS}missing_uncertainty:no_hedging;"
  fi
fi

# Check for deflection/delegation
DELEGATION_PATTERNS=(
  "you should"
  "you could"
  "you might want to"
  "consider"
  "you'll need to"
)

for pattern in "${DELEGATION_PATTERNS[@]}"; do
  if echo "$RESPONSE" | grep -qiE "$pattern"; then
    FLAGS="${FLAGS}delegation:$pattern;"
    STATUS="warning"
  fi
done

# Remove trailing semicolon
FLAGS="${FLAGS%;}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$FLAGS" ]; then
    echo '{"hook":"honesty-check","status":"pass"}'
  else
    echo "{\"hook\":\"honesty-check\",\"status\":\"$STATUS\",\"flags\":\"$FLAGS\"}"
  fi
else
  if [ -n "$FLAGS" ]; then
    echo "Honesty flags: $FLAGS"
  fi
fi

notify_hook_result "continue"
exit 0
