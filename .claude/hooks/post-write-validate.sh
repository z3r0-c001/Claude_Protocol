#!/bin/bash
# PostToolUse hook: Validate written files
# Checks syntax based on file extension

# Source shared logging
SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh"
notify_hook_start "Write"

FILE_PATH="$1"
OUTPUT_MODE="${2:-json}"

ISSUES=""
STATUS="pass"

# Get file extension
EXT="${FILE_PATH##*.}"

# Syntax validation based on file type
case "$EXT" in
  py)
    # Python syntax check
    if command -v python3 &> /dev/null; then
      RESULT=$(python3 -m py_compile "$FILE_PATH" 2>&1)
      if [ $? -ne 0 ]; then
        STATUS="error"
        ISSUES="${ISSUES}{\"type\":\"syntax_error\",\"language\":\"python\",\"message\":\"$(echo "$RESULT" | head -1 | sed 's/"/\\"/g')\",\"severity\":\"auto_fix\"},"
      fi
    fi
    ;;
  js|ts|jsx|tsx)
    # JavaScript/TypeScript syntax check
    if command -v node &> /dev/null; then
      RESULT=$(node --check "$FILE_PATH" 2>&1)
      if [ $? -ne 0 ]; then
        STATUS="error"
        ISSUES="${ISSUES}{\"type\":\"syntax_error\",\"language\":\"javascript\",\"message\":\"$(echo "$RESULT" | head -1 | sed 's/"/\\"/g')\",\"severity\":\"auto_fix\"},"
      fi
    fi
    ;;
  json)
    # JSON syntax check
    if command -v python3 &> /dev/null; then
      RESULT=$(python3 -c "import json; json.load(open('$FILE_PATH'))" 2>&1)
      if [ $? -ne 0 ]; then
        STATUS="error"
        ISSUES="${ISSUES}{\"type\":\"syntax_error\",\"language\":\"json\",\"message\":\"$(echo "$RESULT" | head -1 | sed 's/"/\\"/g')\",\"severity\":\"auto_fix\"},"
      fi
    fi
    ;;
  yaml|yml)
    # YAML syntax check
    if command -v python3 &> /dev/null; then
      RESULT=$(python3 -c "import yaml; yaml.safe_load(open('$FILE_PATH'))" 2>&1)
      if [ $? -ne 0 ]; then
        STATUS="error"
        ISSUES="${ISSUES}{\"type\":\"syntax_error\",\"language\":\"yaml\",\"message\":\"$(echo "$RESULT" | head -1 | sed 's/"/\\"/g')\",\"severity\":\"auto_fix\"},"
      fi
    fi
    ;;
  sh|bash)
    # Shell syntax check
    if command -v bash &> /dev/null; then
      RESULT=$(bash -n "$FILE_PATH" 2>&1)
      if [ $? -ne 0 ]; then
        STATUS="error"
        ISSUES="${ISSUES}{\"type\":\"syntax_error\",\"language\":\"bash\",\"message\":\"$(echo "$RESULT" | head -1 | sed 's/"/\\"/g')\",\"severity\":\"auto_fix\"},"
      fi
    fi
    ;;
esac

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo "{\"hook\":\"post-write-validate\",\"status\":\"pass\",\"file\":\"$FILE_PATH\"}"
  else
    echo "{\"hook\":\"post-write-validate\",\"status\":\"$STATUS\",\"file\":\"$FILE_PATH\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$STATUS" = "error" ]; then
    echo "Syntax error in $FILE_PATH"
    exit 1
  fi
fi

notify_hook_result "continue"
exit 0
