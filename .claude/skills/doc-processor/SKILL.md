---
name: doc-processor
description: >
  Process and reference large documentation files.
  Auto-activates on large file reads.
  Enables /doc-ingest, /doc-search, /doc-list commands.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Task
  - Bash
---

# Document Processor Skill

Process large documentation files into searchable summaries and chunks for efficient reference within Claude Code's context limits.

## Problem Solved

- Claude Code Read tool has 2000-line limit
- Large docs crowd context window
- Users need to reference manuals/API docs during tasks
- Re-reading full docs wastes context

## Solution

1. **Auto-detect** large docs on Read operations
2. **Process** into summary + semantic chunks
3. **Store** in `.claude/docs/processed/`
4. **Search** processed docs for relevant sections

## Commands

### /doc-ingest <path>

Process a documentation file for efficient reference.

```bash
/doc-ingest /path/to/large-manual.md
```

Creates:
- Executive summary (200-500 lines)
- Semantic chunks (150-400 lines each)
- Searchable index with keywords

### /doc-search <query>

Search processed documents for relevant sections.

```bash
/doc-search authentication API
```

Returns:
- Matching chunks across all processed docs
- Relevance-ranked results
- Direct paths to read specific sections

### /doc-list

List all processed documents with summaries.

```bash
/doc-list
```

Shows:
- Document name and source path
- Processing date
- Number of chunks
- Keywords

### /doc-read <doc-id> [section]

Read a specific section from processed docs.

```bash
/doc-read abc123 authentication
/doc-read abc123 001  # By chunk number
```

## Automatic Behaviors

### On Large File Read (via hook)

When a file >2000 lines is read:
```
LARGE DOCUMENT: 'api-reference.md' has 3500 lines.
  This may exceed optimal context size.
  Recommendation: Run /doc-ingest "/path/to/api-reference.md"
```

### On Already Processed Doc

When reading a file that's been processed:
```
DOC AVAILABLE: 'api-reference.md' has been processed.
  Summary: .claude/docs/processed/abc123/summary.md
  Chunks: 12 sections available
  Use /doc-search <query> to find specific sections.
```

## Storage Structure

```
.claude/docs/
├── index.json                    # Master index
└── processed/
    └── {doc-hash}/
        ├── metadata.json         # Full metadata
        ├── summary.md            # Executive summary
        └── chunks/
            ├── 001-intro.md
            ├── 002-setup.md
            └── ...
```

## Size Thresholds

| Category | Lines | Behavior |
|----------|-------|----------|
| Small | < 500 | No action |
| Medium | 500-2000 | Suggest processing |
| Large | > 2000 | Recommend processing |

## Integration

- **Hook:** `doc-size-detector.py` (PostToolUse Read)
- **Agent:** `document-processor` (processing logic)
- **Storage:** `.claude/docs/` directory
- **Memory:** Integrates with MCP memory for metadata

## Best Practices

### When to Process

- API documentation you'll reference repeatedly
- Long manuals or guides
- Technical specifications
- Any doc >1000 lines you need during development

### When NOT to Process

- Code files (use normal Read)
- Small docs (<500 lines)
- One-time reference material
- Frequently changing docs (re-process needed)

## Workflow Example

```
1. User: "I need to reference this API doc while working"
2. Read large doc → Hook suggests /doc-ingest
3. User: /doc-ingest /path/to/api.md
4. Agent processes → Creates summary + chunks
5. Later: User working on auth feature
6. User: /doc-search authentication endpoints
7. Returns relevant chunks
8. User reads specific chunk for implementation details
```
