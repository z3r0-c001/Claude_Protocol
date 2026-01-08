---
description: List all processed documentation files. Usage: /doc-list
---

# List Processed Documents

Display all documentation files that have been processed for reference.

## Process

1. **Read** the docs index from `.claude/docs/index.json`
2. **Format** document information
3. **Display** summary for each processed doc

## Steps

### Step 1: Load Index

Read `.claude/docs/index.json` to get list of processed documents.

### Step 2: Format Output

For each document, display:
- Document ID (short hash)
- Original source path
- Document title/name
- Processing date
- Number of chunks
- Key topics/keywords

### Step 3: Present Results

```markdown
## Processed Documents

| ID | Name | Source | Chunks | Processed |
|----|------|--------|--------|-----------|
| abc123 | API Reference | /docs/api.md | 12 | 2025-12-31 |
| def456 | User Manual | /docs/manual.md | 8 | 2025-12-30 |

### abc123 - API Reference
**Source:** /docs/api.md
**Lines:** 3500 | **Chunks:** 12
**Keywords:** API, REST, authentication, endpoints
**Summary:** .claude/docs/processed/abc123/summary.md

### def456 - User Manual
**Source:** /docs/manual.md
**Lines:** 1800 | **Chunks:** 8
**Keywords:** setup, configuration, usage
**Summary:** .claude/docs/processed/def456/summary.md

---
Commands:
  /doc-search <query>     - Search across all docs
  /doc-read <id> [section] - Read specific section
  /doc-ingest <path>      - Process new document
```

## Empty State

If no documents processed:
```
No documents have been processed yet.

To process a document:
  /doc-ingest /path/to/documentation.md

This will create searchable summaries and chunks.
```

## Tips

- Use document ID with /doc-read for quick access
- Keywords help identify which doc to search
- Re-run /doc-ingest to update stale docs
