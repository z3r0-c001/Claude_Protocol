#!/bin/bash
# Load Memory Script
set -e
set +e  # Allow failures in informational script
# Reads all memory files at session start

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$SCRIPT_DIR/../memory"

echo "═══════════════════════════════════════════════════════════════"
echo "  LOADING MEMORY"
echo "═══════════════════════════════════════════════════════════════"

# Ensure memory directory exists
mkdir -p "$MEMORY_DIR"

# Initialize memory files if they don't exist
MEMORY_FILES=("user-preferences" "project-learnings" "decisions" "corrections" "patterns")

for name in "${MEMORY_FILES[@]}"; do
  file="$MEMORY_DIR/$name.json"
  if [ ! -f "$file" ]; then
    cat > "$file" << EOF
{
  "entries": [],
  "updated": null
}
EOF
    echo "  ○ Initialized $name.json"
  fi
done

# Load and display each memory file
echo ""
echo "▶ User Preferences"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "$MEMORY_DIR/user-preferences.json" ]; then
  entries=$(python3 -c "import json; d=json.load(open('$MEMORY_DIR/user-preferences.json')); print(len(d.get('entries', [])))" 2>/dev/null || echo "0")
  if [ "$entries" != "0" ]; then
    python3 -c "
import json
with open('$MEMORY_DIR/user-preferences.json') as f:
    data = json.load(f)
for e in data.get('entries', [])[:5]:
    print(f\"  • {e['key']}: {e['value']}\")
if len(data.get('entries', [])) > 5:
    print(f\"  ... and {len(data['entries']) - 5} more\")
" 2>/dev/null || echo "  (none)"
  else
    echo "  (none)"
  fi
fi

echo ""
echo "▶ Project Learnings"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "$MEMORY_DIR/project-learnings.json" ]; then
  python3 -c "
import json
with open('$MEMORY_DIR/project-learnings.json') as f:
    data = json.load(f)
for e in data.get('entries', [])[:5]:
    print(f\"  • {e['key']}: {e['value']}\")
if len(data.get('entries', [])) > 5:
    print(f\"  ... and {len(data['entries']) - 5} more\")
if not data.get('entries'):
    print('  (none)')
" 2>/dev/null || echo "  (none)"
fi

echo ""
echo "▶ Decisions"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "$MEMORY_DIR/decisions.json" ]; then
  python3 -c "
import json
with open('$MEMORY_DIR/decisions.json') as f:
    data = json.load(f)
for e in data.get('entries', [])[:5]:
    reason = e.get('reason', 'no reason recorded')
    print(f\"  • {e['key']}: {e['value']}\")
    print(f\"    Reason: {reason}\")
if len(data.get('entries', [])) > 5:
    print(f\"  ... and {len(data['entries']) - 5} more\")
if not data.get('entries'):
    print('  (none)')
" 2>/dev/null || echo "  (none)"
fi

echo ""
echo "▶ Corrections (Don't Repeat These Mistakes)"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "$MEMORY_DIR/corrections.json" ]; then
  python3 -c "
import json
with open('$MEMORY_DIR/corrections.json') as f:
    data = json.load(f)
for e in data.get('entries', []):
    print(f\"  ✗ WRONG: {e.get('wrong', 'N/A')}\")
    print(f\"  ✓ CORRECT: {e.get('correct', e.get('value', 'N/A'))}\")
    print()
if not data.get('entries'):
    print('  (none)')
" 2>/dev/null || echo "  (none)"
fi

echo ""
echo "▶ Patterns"
echo "─────────────────────────────────────────────────────────────────"
if [ -f "$MEMORY_DIR/patterns.json" ]; then
  python3 -c "
import json
with open('$MEMORY_DIR/patterns.json') as f:
    data = json.load(f)
for e in data.get('entries', [])[:5]:
    freq = e.get('frequency', '?')
    print(f\"  • {e['key']}: {e['value']} (seen {freq}x)\")
if len(data.get('entries', [])) > 5:
    print(f\"  ... and {len(data['entries']) - 5} more\")
if not data.get('entries'):
    print('  (none)')
" 2>/dev/null || echo "  (none)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  MEMORY LOADED - Do not ask user for info already here"
echo "═══════════════════════════════════════════════════════════════"
