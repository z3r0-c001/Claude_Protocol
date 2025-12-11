#!/bin/bash
# Save Memory Script
# Adds entries to memory files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$SCRIPT_DIR/../memory"

# Usage: save-memory.sh <category> <key> <value> [reason]
# Categories: user-preferences, project-learnings, decisions, corrections, patterns

CATEGORY="$1"
KEY="$2"
VALUE="$3"
REASON="${4:-}"

if [ -z "$CATEGORY" ] || [ -z "$KEY" ] || [ -z "$VALUE" ]; then
  echo "Usage: save-memory.sh <category> <key> <value> [reason]"
  echo ""
  echo "Categories:"
  echo "  user-preferences   - User communication/work preferences"
  echo "  project-learnings  - Technical discoveries about the project"
  echo "  decisions          - Architectural choices and rationale"
  echo "  corrections        - Mistakes to avoid repeating"
  echo "  patterns           - Recurring code/workflow patterns"
  exit 1
fi

# Validate category
VALID_CATEGORIES=("user-preferences" "project-learnings" "decisions" "corrections" "patterns")
if [[ ! " ${VALID_CATEGORIES[*]} " =~ " ${CATEGORY} " ]]; then
  echo "Error: Invalid category '$CATEGORY'"
  echo "Valid categories: ${VALID_CATEGORIES[*]}"
  exit 1
fi

MEMORY_FILE="$MEMORY_DIR/$CATEGORY.json"

# Ensure directory exists
mkdir -p "$MEMORY_DIR"

# Ensure file exists with valid JSON
if [ ! -f "$MEMORY_FILE" ] || [ ! -s "$MEMORY_FILE" ]; then
  echo '{"entries": [], "updated": null}' > "$MEMORY_FILE"
fi

# Validate JSON before modifying
if ! python3 -m json.tool "$MEMORY_FILE" > /dev/null 2>&1; then
  echo "Warning: Corrupted memory file, resetting..."
  echo '{"entries": [], "updated": null}' > "$MEMORY_FILE"
fi

# Add entry using Python (handles escaping properly)
python3 << EOF
import json
import sys
from datetime import datetime

memory_file = "$MEMORY_FILE"
key = """$KEY"""
value = """$VALUE"""
reason = """$REASON""" if """$REASON""" else None

try:
    with open(memory_file) as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    data = {"entries": [], "updated": None}

# Ensure entries list exists
if 'entries' not in data or not isinstance(data['entries'], list):
    data['entries'] = []

# Check if key exists
existing_idx = None
for idx, e in enumerate(data['entries']):
    if e.get('key') == key:
        existing_idx = idx
        break

entry = {
    "key": key,
    "value": value,
    "timestamp": datetime.utcnow().isoformat() + "Z"
}
if reason:
    entry["reason"] = reason

if existing_idx is not None:
    # Update existing entry
    data['entries'][existing_idx] = entry
    print(f"✓ Updated: {key}")
else:
    # Add new entry
    data['entries'].append(entry)
    print(f"✓ Added: {key}")

data['updated'] = datetime.utcnow().isoformat() + "Z"

with open(memory_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"  Category: $CATEGORY")
print(f"  Value: {value[:100]}{'...' if len(value) > 100 else ''}")
EOF
