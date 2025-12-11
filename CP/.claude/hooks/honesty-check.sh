#!/bin/bash
# Stop hook: Check for honesty issues in responses
# Focuses on overconfidence detection (the primary honesty concern)
#
# Philosophy:
# - Overconfidence is bad (claiming certainty without evidence)
# - Hedging is GOOD (shows appropriate uncertainty)
# - Suggesting next steps to users is FINE (not delegation)
# - Avoiding implementation work IS bad (covered by laziness-check)

# Source shared logging
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh"
notify_hook_start "Stop"

RESPONSE="$1"
OUTPUT_MODE="${2:-json}"

FLAGS=""
STATUS="pass"

# Check for overconfident language (the main honesty concern)
# These are absolute claims that are rarely justified
OVERCONFIDENT_PATTERNS=(
  "definitely will"
  "certainly will"
  "guaranteed to"
  "100% certain"
  "without question"
  "no doubt about"
  "absolutely certain"
)

for pattern in "${OVERCONFIDENT_PATTERNS[@]}"; do
  if echo "$RESPONSE" | grep -qiE "$pattern"; then
    FLAGS="${FLAGS}overconfident:$pattern;"
    STATUS="warning"
  fi
done

# Check for false certainty about external facts
# Pattern: "X is Y" without "I believe", "according to", etc.
# Only flag strong declarative claims about uncertain topics
if echo "$RESPONSE" | grep -qiE "this will (always|never)" || \
   echo "$RESPONSE" | grep -qiE "it is (impossible|guaranteed)"; then
  FLAGS="${FLAGS}false_certainty:absolute_claim;"
  STATUS="warning"
fi

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
