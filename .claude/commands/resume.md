---
description: Resume from a saved session state. Usage: /resume [session-id]
---

# Resume Command

Retrieve and load a previously saved session state.

## Prerequisites

This command requires the MCP memory server. If MCP is not available:
- Try MCP first: `mcp__memory__memory_search`
- Fallback: Search local `.claude/memory/leftoff/` directory for JSON files

## Purpose

Complement to `/leftoff` - retrieves saved session snapshots and offers to continue work.

## Usage

`/resume` - Show available sessions and load most recent
`/resume [session-id]` - Load specific session (e.g., `leftoff-2025-12-11-14-30`)

## Process

1. **Search for leftoff entries**:
   ```
   mcp__memory__memory_search
   - query: "leftoff-"
   - categories: ["project-learnings"]
   ```

2. **If no sessions found**:
   - Inform user: "No saved sessions found. Use `/leftoff` to save your current session."

3. **If sessions found**:
   - List available sessions with dates and summaries
   - If specific session requested, load that one
   - Otherwise load most recent

4. **Display session state**:
   ```
   ## Resuming Session: [date]

   ### Summary
   [session summary]

   ### Pending Tasks
   [list pending items]

   ### Next Steps
   [what to do next]
   ```

5. **Offer to continue**:
   - "Ready to continue. What would you like to work on first?"
   - Or automatically start on first pending task if clear

## Examples

```
/resume
→ "Found 2 saved sessions:
   1. leftoff-2025-12-11-14-30 - PreToolUse hooks integration
   2. leftoff-2025-12-10-20-15 - Security hardening work

   Loading most recent session..."

/resume leftoff-2025-12-10-20-15
→ Loads the specific older session
```

---

Execute this command by searching for and displaying saved session states.
