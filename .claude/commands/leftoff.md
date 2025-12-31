---
description: Save session state for seamless continuation. Keeps last 3 sessions. Usage: /leftoff [summary]
---

# Left Off Command

Save current session state for seamless continuation in a new session.

## Purpose

Unlike `/remember` (surgical facts) or `/recall` (topic search), `/leftoff` captures a **complete session snapshot** - what was done, what's pending, key context, and blockers.

## Prerequisites

This command requires the MCP memory server. If MCP is not available:
- Try MCP first: `mcp__memory__memory_write`, `mcp__memory__memory_search`, `mcp__memory__memory_delete`
- Fallback: Save to `.claude/memory/leftoff/[timestamp].json`

## Usage

`/leftoff [optional summary]`

If no summary provided, analyze the conversation to extract:
- Completed work
- Pending tasks
- Key files modified
- Current blockers
- Next steps

## Session Schema

Save to `project-learnings` category with key pattern `leftoff-YYYY-MM-DD-HH-MM`:

```
## Session: [timestamp]

### Summary
[Brief description of the session focus]

### Completed
- [List of completed tasks]

### Pending
- [List of unfinished tasks]

### Key Files
- [Files created/modified with brief notes]

### Blockers
- [Any issues preventing progress]

### Next Steps
- [What to do when resuming]

### Context
[Any important context for continuation]
```

## Process

1. **Analyze conversation** to extract session state
2. **Check existing leftoff entries**:
   ```
   mcp__memory__memory_search
   - query: "leftoff-"
   - categories: ["project-learnings"]
   ```
3. **Delete oldest if more than 2 exist** (keep max 3 sessions):
   ```
   mcp__memory__memory_delete
   - category: project-learnings
   - key: [oldest leftoff-* key]
   - confirm: true
   ```
4. **Save new session state**:
   ```
   mcp__memory__memory_write
   - category: project-learnings
   - key: leftoff-[YYYY-MM-DD-HH-MM]
   - value: [formatted session state]
   - reason: Session checkpoint for continuation
   ```
5. **Confirm save** with summary of what was captured

## Resuming

When starting a new session, check for leftoff state:
```
mcp__memory__memory_search
- query: "leftoff-"
- categories: ["protocol-state"]
```

If found, offer to resume: "I found a saved session from [date]. Would you like me to continue from there?"

## Size Management

- Each session state should be concise (under 2KB)
- Focus on actionable information, not full conversation history
- Use bullet points over paragraphs
- Reference file paths, not file contents

---

Execute this command by analyzing the current conversation and saving structured session state.
