---
description: Search the codebase. Usage: /search <query or pattern>
---

# Search Command

Search the codebase for code, patterns, or text.

## Usage

- `/search functionName` - Search for exact text
- `/search "error handling"` - Search for phrase
- `/search pattern:TODO` - Search with regex
- `/search file:*.ts` - Find files by pattern

## Search Types

### Text Search (default)
Search for exact text in files:
```
/search handleSubmit
```

### Regex Search
Use `pattern:` prefix for regex:
```
/search pattern:function\s+\w+
```

### File Search
Use `file:` prefix to find files:
```
/search file:**/*.test.ts
```

### Definition Search
Use `def:` prefix to find definitions:
```
/search def:UserService
```

## Options

- `--type=js` - Filter by file type
- `--path=src/` - Limit to directory
- `--context=3` - Show surrounding lines

## Output

Results show:
- File path
- Line number
- Matching line with context

---

Execute the appropriate search based on the query type.
