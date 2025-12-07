---
description: Remember something for future sessions. Usage: /remember <category> <what to remember>
---

# Remember Command

Store information in persistent memory for future sessions.

## Usage

`/remember [category] <what to remember>`

## Categories

- **user-preferences**: Coding style, output preferences, protected paths
- **project-learnings**: Codebase insights, patterns, architecture notes
- **decisions**: Major architectural choices (requires confirmation)
- **corrections**: Mistakes and their corrections
- **patterns**: Recurring solutions, common code patterns

## Process

1. Parse the input to extract:
   - Category (default: project-learnings if not specified)
   - Content to remember
   - Reason (why this is being saved)

2. Use the MCP memory tool:
   ```
   mcp__memory__memory_write
   - category: [extracted category]
   - key: [generated key from content]
   - value: [the content to remember]
   - reason: [why this is being saved]
   ```

3. Confirm the save:
   - For decisions category: Ask for confirmation first
   - For other categories: Auto-save and confirm

## Examples

`/remember user-preferences Uses tabs not spaces for indentation`
→ Saves to user-preferences category

`/remember The API rate limit is 100 requests per minute`
→ Saves to project-learnings category (default)

`/remember decisions Use PostgreSQL over MongoDB for this project`
→ Asks for confirmation, then saves to decisions

---

Parse the user's input and save to the appropriate memory category using the MCP memory tool.
