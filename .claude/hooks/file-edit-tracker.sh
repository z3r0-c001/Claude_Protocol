#!/bin/bash
# PostToolUse hook: Track file edits
# Maintains list of modified files for session awareness

FILE_PATH="$1"
OUTPUT_MODE="${2:-json}"

# Get existing modified files from environment or file
TRACKER_FILE="${CLAUDE_TRACKER_FILE:-.claude/memory/session-edits.json}"

# Ensure directory exists
mkdir -p "$(dirname "$TRACKER_FILE")"

# Initialize or read existing tracker
if [ -f "$TRACKER_FILE" ]; then
  # Add file to existing list if not already present
  if ! grep -q "\"$FILE_PATH\"" "$TRACKER_FILE" 2>/dev/null; then
    # Read current JSON, add new entry
    TIMESTAMP=$(date -Iseconds)

    # Simple append approach - add to files array
    if [ -s "$TRACKER_FILE" ]; then
      # Remove trailing ] and add new entry
      sed -i '$ s/]$/,{"path":"'"$FILE_PATH"'","timestamp":"'"$TIMESTAMP"'"}]/' "$TRACKER_FILE" 2>/dev/null || \
      echo "{\"session_start\":\"$TIMESTAMP\",\"files\":[{\"path\":\"$FILE_PATH\",\"timestamp\":\"$TIMESTAMP\"}]}" > "$TRACKER_FILE"
    else
      echo "{\"session_start\":\"$TIMESTAMP\",\"files\":[{\"path\":\"$FILE_PATH\",\"timestamp\":\"$TIMESTAMP\"}]}" > "$TRACKER_FILE"
    fi
  fi
else
  # Create new tracker
  TIMESTAMP=$(date -Iseconds)
  echo "{\"session_start\":\"$TIMESTAMP\",\"files\":[{\"path\":\"$FILE_PATH\",\"timestamp\":\"$TIMESTAMP\"}]}" > "$TRACKER_FILE"
fi

# Count files
FILE_COUNT=$(grep -o '"path"' "$TRACKER_FILE" 2>/dev/null | wc -l)

if [ "$OUTPUT_MODE" = "json" ]; then
  echo "{\"hook\":\"file-edit-tracker\",\"status\":\"pass\",\"tracked\":\"$FILE_PATH\",\"total_files\":$FILE_COUNT}"
else
  echo "Tracked: $FILE_PATH (total: $FILE_COUNT files this session)"
fi

exit 0
