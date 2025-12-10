#!/bin/bash
# Notification Logging Script
set -e
set +e  # Allow failures in logging
# Logs notifications for debugging and audit

NOTIFICATION_TYPE="$1"
MESSAGE="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../memory"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure log directory exists
mkdir -p "$LOG_DIR"

case "$NOTIFICATION_TYPE" in
  error)
    LOG_FILE="$LOG_DIR/errors.log"
    echo "[$TIMESTAMP] ERROR: $MESSAGE" >> "$LOG_FILE"
    ;;
  warning)
    LOG_FILE="$LOG_DIR/warnings.log"
    echo "[$TIMESTAMP] WARN: $MESSAGE" >> "$LOG_FILE"
    ;;
  info)
    LOG_FILE="$LOG_DIR/info.log"
    echo "[$TIMESTAMP] INFO: $MESSAGE" >> "$LOG_FILE"
    ;;
  validation_failed)
    LOG_FILE="$LOG_DIR/validation.log"
    echo "[$TIMESTAMP] VALIDATION_FAILED: $MESSAGE" >> "$LOG_FILE"
    ;;
  laziness_detected)
    LOG_FILE="$LOG_DIR/laziness.log"
    echo "[$TIMESTAMP] LAZINESS: $MESSAGE" >> "$LOG_FILE"
    ;;
  hallucination_detected)
    LOG_FILE="$LOG_DIR/hallucinations.log"
    echo "[$TIMESTAMP] HALLUCINATION: $MESSAGE" >> "$LOG_FILE"
    ;;
  *)
    LOG_FILE="$LOG_DIR/general.log"
    echo "[$TIMESTAMP] $NOTIFICATION_TYPE: $MESSAGE" >> "$LOG_FILE"
    ;;
esac

# Rotate logs if too large (> 1MB)
for log in "$LOG_DIR"/*.log; do
  if [ -f "$log" ]; then
    size=$(stat -f%z "$log" 2>/dev/null || stat -c%s "$log" 2>/dev/null || echo 0)
    if [ "$size" -gt 1048576 ]; then
      mv "$log" "${log}.old"
      tail -1000 "${log}.old" > "$log"
      rm "${log}.old"
    fi
  fi
done

exit 0
