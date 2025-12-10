#!/bin/bash
# PreCompact hook: Save state before compaction
mkdir -p memories
echo "{\"compacted_at\": \"$(date -Iseconds)\", \"note\": \"Context was compacted\"}" >> memories/compaction-log.json
