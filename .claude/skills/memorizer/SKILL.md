---
name: memorizer
description: >
  INVOKE AUTOMATICALLY to persist learnings, user preferences, patterns, and decisions.
  Use PROACTIVELY after every significant interaction.
  Triggers on: remember, learned, preference, pattern, decision, don't forget, keep track, note that.
allowed-tools:
  - mcp__memory__memory_write
  - mcp__memory__memory_read
  - mcp__memory__memory_search
---

# Memorizer Skill

## Overview

This skill enables Claude to remember information across sessions using the MCP memory server. It should be invoked AUTOMATICALLY when important information needs to be persisted.

## Memory Categories

### Auto-Save (No Permission Required)
| Category | When to Use |
|----------|-------------|
| `user-preferences` | User's coding style, tool preferences, communication style |
| `project-learnings` | Discovered patterns, codebase insights, architecture notes |
| `corrections` | When Claude was wrong and corrected |
| `patterns` | Recurring patterns, common solutions, frequently-used code |

### Permission Required
| Category | When to Use |
|----------|-------------|
| `decisions` | Major architectural choices, technology selections |

## When to Auto-Save

### User Preferences
- User prefers specific coding style → save to `user-preferences`
- User requests verbose/concise output → save to `user-preferences`
- User specifies protected paths → save to `user-preferences`

### Project Learnings
- Discovered how a component works → save to `project-learnings`
- Found undocumented behavior → save to `project-learnings`
- Identified codebase patterns → save to `project-learnings`

### Corrections
- User corrects a mistake → save to `corrections`
- Research shows initial assumption wrong → save to `corrections`
- A different approach was needed → save to `corrections`

### Patterns
- Same solution used multiple times → save to `patterns`
- User has consistent way of doing things → save to `patterns`
- Discovered reusable code pattern → save to `patterns`

## How to Save

```markdown
I'll remember this for future sessions.

[Use mcp__memory__memory_write tool]
- category: user-preferences
- key: coding-style-preference
- value: User prefers functional programming over OOP
- reason: User explicitly stated preference in this conversation
```

## How to Recall

At session start or when relevant:

```markdown
[Use mcp__memory__memory_search tool]
- query: [relevant topic]
- categories: [relevant categories]
```

## Best Practices

### DO
- Save immediately when user states a preference
- Record corrections right after being corrected
- Note patterns when you notice them
- Ask for confirmation on major decisions

### DON'T
- Save trivial or temporary information
- Save sensitive data (passwords, API keys)
- Save without context (always include reason)
- Save duplicate entries (search first)

## Example Flows

### User States Preference
```
User: "I prefer tabs over spaces"

Claude:
1. Acknowledge preference
2. Save to memory:
   - category: user-preferences
   - key: indentation-style
   - value: Uses tabs, not spaces
   - reason: User explicitly stated preference
3. Apply preference going forward
```

### Correction Received
```
User: "That's wrong, the API uses POST not GET"

Claude:
1. Acknowledge mistake
2. Save to memory:
   - category: corrections
   - key: api-method-for-[endpoint]
   - value: API uses POST, not GET
   - reason: Corrected by user
3. Apply correct information
```

### Pattern Discovered
```
Claude notices: User always wants error handling with logging

Claude:
1. Save to memory:
   - category: patterns
   - key: error-handling-pattern
   - value: User wants all error handlers to include logging
   - reason: Observed in 3+ interactions
```

## Integration

This skill works with:
- MCP Memory Server (for persistence)
- `/remember` command (manual save)
- `/recall` command (manual search)
- Session start (auto-load context)
