---
description: Search memory for information. Usage: /recall <topic or keyword>
---

# Recall Command

Search persistent memory for relevant information.

## Usage

`/recall <topic or keyword>`

## Process

1. Parse the search query from user input

2. Use the MCP memory search tool:
   ```
   mcp__memory__memory_search
   - query: [the search term]
   - fuzzy: true
   - limit: 20
   ```

3. Display results:
   - Category
   - Key
   - Value
   - When it was saved
   - Relevance score

## Search Tips

- Use specific keywords for better results
- Search is fuzzy by default (finds similar matches)
- Results are sorted by relevance

## Examples

`/recall coding style`
→ Searches all categories for coding style preferences

`/recall authentication`
→ Finds any learnings or decisions about authentication

`/recall error handling`
→ Finds patterns and corrections related to error handling

---

Search the memory using the MCP memory tool and display relevant results.
