---
description: Show Claude Bootstrap Protocol state, memory status, and project health
---

# Protocol Status

Display the current state of the Claude Bootstrap Protocol.

## Information to Show

### 1. Protocol State
- Initialized: Yes/No
- Bootstrap complete: Yes/No
- Last validation: timestamp

### 2. Memory Status
Read from memory to show:
- User preferences count
- Project learnings count
- Decisions count
- Corrections count
- Patterns count

### 3. Project Health
- CLAUDE.md exists: Yes/No
- settings.json valid: Yes/No
- Hooks configured: count
- Commands available: count

### 4. Recent Activity
- Files modified this session
- Memory entries added
- Agents invoked

## Output Format

```
Claude Bootstrap Protocol Status
================================

Protocol:
  Initialized: ✓
  Bootstrap: ✓
  Last Validation: 2024-01-15 10:30:00

Memory:
  user-preferences: 5 entries
  project-learnings: 12 entries
  decisions: 3 entries
  corrections: 2 entries
  patterns: 8 entries

Project:
  CLAUDE.md: ✓
  settings.json: ✓
  Hooks: 12 configured
  Commands: 15 available

Session:
  Files modified: 3
  Memory writes: 2
```

---

Read protocol state and memory to display current status.
