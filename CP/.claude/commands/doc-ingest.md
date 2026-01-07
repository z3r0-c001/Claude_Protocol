---
description: Process a large documentation file into searchable chunks. Usage: /doc-ingest <path>
---

$ARGUMENTS

# Document Ingestion

Process the specified documentation file for efficient reference.

## Process

1. **Analyze** the document structure
2. **Generate** executive summary (200-500 lines)
3. **Create** semantic chunks by section
4. **Build** searchable index with keywords
5. **Store** in `.claude/docs/processed/`

## Steps

### Step 1: Validate Input

Ensure the file path is provided and the file exists. Check if already processed.

### Step 2: Invoke Document Processor Agent

Use the Task tool to invoke the `document-processor` agent:

```
Task(
  subagent_type="document-processor",
  prompt="Process the document at: $ARGUMENTS

  1. Analyze structure and identify document type
  2. Generate executive summary
  3. Create semantic chunks (150-400 lines each)
  4. Build searchable index
  5. Store in .claude/docs/processed/"
)
```

### Step 3: Confirm Completion

Report to user:
- Document ID for future reference
- Number of chunks created
- Summary location
- Available commands (/doc-search, /doc-list)

## Output

After successful processing:

```
Document processed successfully!

ID: {doc-hash}
Source: {file_path}
Summary: .claude/docs/processed/{doc-hash}/summary.md
Chunks: {count} sections

Commands:
  /doc-search <query>  - Search this document
  /doc-list            - List all processed docs
  /doc-read {doc-hash} [section] - Read specific section
```

## Error Handling

- **File not found:** Report error, suggest checking path
- **Already processed:** Ask if re-processing desired
- **Processing failed:** Report error, suggest manual chunking
