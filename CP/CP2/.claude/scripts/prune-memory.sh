#!/bin/bash
# prune-memory.sh - Remove old memory entries to prevent unbounded growth

set -e

MEMORY_DIR=".claude/memory"
CONFIG_FILE=".claude/config.json"

# Default thresholds (can be overridden by config)
MAX_ENTRIES=100
PRUNE_DAYS=90

# Load from config if exists
if [ -f "$CONFIG_FILE" ]; then
    MAX_ENTRIES=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('thresholds',{}).get('memory',{}).get('max_entries_per_category', 100))" 2>/dev/null || echo "100")
    PRUNE_DAYS=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('thresholds',{}).get('memory',{}).get('prune_after_days', 90))" 2>/dev/null || echo "90")
fi

echo "Memory Pruning"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "Max entries per category: $MAX_ENTRIES"
echo "Prune entries older than: $PRUNE_DAYS days"
echo ""

# Calculate cutoff date
CUTOFF_DATE=$(date -d "$PRUNE_DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v-${PRUNE_DAYS}d +%Y-%m-%d)

prune_memory_file() {
    local file="$1"
    local name=$(basename "$file" .json)
    
    if [ ! -f "$file" ]; then
        return
    fi
    
    # Count current entries
    local count_before=$(python3 -c "
import json
try:
    data = json.load(open('$file'))
    print(len(data.get('entries', [])))
except:
    print(0)
" 2>/dev/null || echo "0")
    
    if [ "$count_before" -eq 0 ]; then
        echo "  $name: empty, skipping"
        return
    fi
    
    # Prune old entries and keep only MAX_ENTRIES most recent
    python3 << EOF
import json
from datetime import datetime, timedelta

try:
    with open('$file', 'r') as f:
        data = json.load(f)
    
    entries = data.get('entries', [])
    cutoff = datetime.now() - timedelta(days=$PRUNE_DAYS)
    
    # Filter by date
    filtered = []
    for entry in entries:
        try:
            ts = entry.get('timestamp', '')
            if ts:
                entry_date = datetime.fromisoformat(ts.replace('Z', '+00:00').split('+')[0])
                if entry_date >= cutoff:
                    filtered.append(entry)
            else:
                filtered.append(entry)  # Keep entries without timestamp
        except:
            filtered.append(entry)  # Keep on parse error
    
    # Keep only most recent MAX_ENTRIES
    if len(filtered) > $MAX_ENTRIES:
        # Sort by timestamp descending and keep most recent
        filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        filtered = filtered[:$MAX_ENTRIES]
    
    data['entries'] = filtered
    
    with open('$file', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"  $name: {$count_before} → {len(filtered)} entries")
    
except Exception as e:
    print(f"  $name: error - {e}")
EOF
}

# Prune each memory file
for file in "$MEMORY_DIR"/*.json; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "protocol-state.json" ] && continue  # Skip state file
    prune_memory_file "$file"
done

echo ""
echo "Pruning complete"
