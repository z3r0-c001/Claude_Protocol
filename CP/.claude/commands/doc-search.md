---
description: Search processed documents for relevant sections. Usage: /doc-search <query>
---

$ARGUMENTS

# Document Search

Search across all processed documentation for sections matching the query.

## Process

1. **Load** the docs index from `.claude/docs/index.json`
2. **Search** keywords and content across all processed docs
3. **Rank** results by relevance
4. **Return** matching chunks with context

## Steps

### Step 1: Parse Query

Extract search terms from: $ARGUMENTS

### Step 2: Search Index

Search the docs index for matching:
- Keywords in chunk metadata
- Section titles
- Document names

### Step 3: Search Chunk Content

For promising matches, grep chunk files for query terms:

```bash
grep -l -i "<query>" .claude/docs/processed/*/chunks/*.md
```

### Step 4: Rank Results

Order by:
1. Exact keyword match in metadata
2. Title/heading match
3. Content frequency match

### Step 5: Present Results

```markdown
## Search Results for: "{query}"

### 1. {Doc Name} - {Section Title}
**Relevance:** High | **Path:** .claude/docs/processed/{id}/chunks/003-section.md
> {First 2-3 lines of matching content...}

### 2. {Doc Name} - {Section Title}
**Relevance:** Medium | **Path:** .claude/docs/processed/{id}/chunks/007-section.md
> {First 2-3 lines of matching content...}

---
Use: Read .claude/docs/processed/{id}/chunks/{chunk}.md to view full section
```

## No Results

If no matches found:
```
No results found for "{query}"

Suggestions:
- Try different keywords
- Check /doc-list for available documents
- Process additional docs with /doc-ingest
```

## Tips

- Use specific technical terms for better results
- Search for concepts, not exact phrases
- Combine with /doc-read to view full sections
