---
description: Search memory for information. Usage: /recall <topic or keyword>
---

$ARGUMENTS

# RECALL FROM MEMORY

Search all memory files for the requested information.

## Process

1. Search using MCP memory tool:
```
Use the mcp__memory__memory_search tool with:
- query: <user's search term>
- categories: (optional, omit to search all)
```

The MCP tool performs fuzzy search using Fuse.js across all memory categories.

2. If more specific lookup needed:
```
Use mcp__memory__memory_read tool with:
- category: <specific category>
- key: <specific key>
```

3. To list all entries in a category:
```
Use mcp__memory__memory_list tool with:
- category: <category name>
```

## Fallback (CLI usage)

If MCP tools unavailable:
```bash
bash .claude/scripts/load-memory.sh
```

## Search Strategy

The MCP memory_search tool handles:
1. **Fuzzy matching** - Finds related terms (e.g., "database" matches "postgresql")
2. **Cross-category search** - Searches all categories simultaneously
3. **Relevance scoring** - Results sorted by match quality

## Output Format

```markdown
## Memory Search: "<query>"

### Found in User Preferences
- [key]: [value]

### Found in Project Learnings
- [key]: [value]
  Reason: [reason]

### Found in Decisions
- [key]: [value]
  Reason: [reason]

### Found in Corrections
- WRONG: [what was wrong]
- CORRECT: [correct approach]

### No matches in: [list categories with no matches]
```

If nothing found:
```
No memories found for "<query>"

Would you like me to:
1. Search with different terms?
2. Remember something new about this topic?
```
