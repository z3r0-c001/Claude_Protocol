---
name: memorizer
description: "INVOKE AUTOMATICALLY to persist learnings, user preferences, patterns, and decisions. Use PROACTIVELY after every significant interaction. Triggers on: remember, learned, preference, pattern, decision, don't forget, keep track, note that."
allowed-tools: Read, Write, Bash
---

# Memorizer Skill

Persistent memory system that ensures Claude never forgets and users never repeat themselves.

## Purpose

1. **User Preferences** - Communication style, formatting preferences, technical level
2. **Project Learnings** - Discovered patterns, gotchas, successful approaches
3. **Decisions** - Architectural choices, trade-offs made, rationale
4. **Corrections** - Things Claude got wrong and the correct answer
5. **Context** - Ongoing tasks, blockers, next steps

## Memory Protocol

```
MEMORY PROTOCOL:
1. ALWAYS check memory first: cat .claude/memory/*.json
2. Work on task
3. Record any new learnings/preferences/decisions
4. ASSUME INTERRUPTION - context may reset anytime
```

## Memory Structure

```
.claude/memory/
├── user-preferences.json      # How user likes to work
├── project-learnings.json     # Technical discoveries
├── decisions.json             # Choices made and why
├── corrections.json           # Things to not repeat
├── context.json               # Current state
└── patterns.json              # Recurring patterns
```

## When to Memorize

### ALWAYS memorize:
- User corrections ("No, I meant X not Y")
- User preferences ("I prefer TypeScript over JavaScript")
- Successful approaches ("That worked, remember this")
- Failed approaches ("Don't do X again")
- Explicit requests ("Remember that...")
- Architectural decisions ("We decided to use X because...")

### Auto-detect and memorize:
- Communication style preferences
- Code style preferences
- Frequently referenced files
- Common workflows
- Error patterns and fixes

## Memory Operations

### Read Memory (Start of Session)
```bash
#!/bin/bash
# Read all memory files
for f in .claude/memory/*.json; do
  [ -f "$f" ] && echo "=== $(basename $f) ===" && cat "$f"
done
```

### Write Memory (After Significant Events)
```python
import json
from datetime import datetime

def memorize(category, key, value, reason=None):
    """Add to persistent memory"""
    memory_file = f".claude/memory/{category}.json"
    
    try:
        with open(memory_file) as f:
            memory = json.load(f)
    except:
        memory = {"entries": [], "updated": None}
    
    entry = {
        "key": key,
        "value": value,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Update or append
    existing = next((e for e in memory["entries"] if e["key"] == key), None)
    if existing:
        existing.update(entry)
    else:
        memory["entries"].append(entry)
    
    memory["updated"] = datetime.utcnow().isoformat()
    
    with open(memory_file, 'w') as f:
        json.dump(memory, f, indent=2)
```

## Memory File Formats

### user-preferences.json
```json
{
  "entries": [
    {
      "key": "code_style",
      "value": "Prefer functional over OOP",
      "reason": "User stated preference",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "key": "communication",
      "value": "Brief, technical, no fluff",
      "reason": "Observed from interactions",
      "timestamp": "2024-01-15T10:35:00Z"
    },
    {
      "key": "formatting",
      "value": "Minimal markdown, code over prose",
      "reason": "User correction",
      "timestamp": "2024-01-15T11:00:00Z"
    }
  ],
  "updated": "2024-01-15T11:00:00Z"
}
```

### project-learnings.json
```json
{
  "entries": [
    {
      "key": "test_database",
      "value": "Must run docker-compose up -d before tests",
      "reason": "Tests failed without this",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "key": "api_auth",
      "value": "Bearer token in X-Auth-Token header, not Authorization",
      "reason": "Non-standard API discovered",
      "timestamp": "2024-01-15T10:45:00Z"
    }
  ],
  "updated": "2024-01-15T10:45:00Z"
}
```

### decisions.json
```json
{
  "entries": [
    {
      "key": "database_choice",
      "value": "PostgreSQL over MongoDB",
      "reason": "Need ACID transactions for financial data",
      "alternatives_considered": ["MongoDB", "MySQL"],
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "updated": "2024-01-15T10:30:00Z"
}
```

### corrections.json
```json
{
  "entries": [
    {
      "key": "api_endpoint_format",
      "value": "Use /api/v2/ not /api/v1/",
      "wrong": "Used deprecated v1 endpoint",
      "correct": "Always use v2 for new code",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "updated": "2024-01-15T10:30:00Z"
}
```

### patterns.json
```json
{
  "entries": [
    {
      "key": "error_handling",
      "value": "Project uses Result<T, E> pattern, not exceptions",
      "frequency": 15,
      "files": ["src/api.ts", "src/db.ts"],
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "updated": "2024-01-15T10:30:00Z"
}
```

## Integration with Hooks

### SessionStart Hook
```json
{
  "matcher": "startup",
  "hooks": [{
    "type": "command",
    "command": "bash .claude/scripts/load-memory.sh"
  }]
}
```

### PostToolUse Hook (Auto-memorize patterns)
```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "prompt",
    "prompt": "Check if this write reveals a pattern worth memorizing..."
  }]
}
```

### Stop Hook (Memorize session learnings)
```json
{
  "hooks": [{
    "type": "prompt",
    "prompt": "Review session for learnings to memorize..."
  }]
}
```

## Slash Commands

- `/remember <what>` - Explicitly memorize something
- `/forget <key>` - Remove from memory
- `/recall <topic>` - Search memory for topic
- `/preferences` - Show user preferences
- `/learnings` - Show project learnings

## Critical Rules

1. **ALWAYS check memory at session start**
2. **NEVER ask user something already in memory**
3. **Auto-memorize corrections immediately**
4. **Memorize successful patterns for reuse**
5. **Keep memory concise - summarize, don't dump**
