---
description: Search the codebase. Usage: /search <query or pattern>
---

$ARGUMENTS

# CODEBASE SEARCH

Search the codebase for the specified query.

## Search Strategy

1. **Text search** - Find occurrences
```bash
grep -rn "$ARGUMENTS" --include="*.py" --include="*.ts" --include="*.js" --include="*.go" --include="*.rs" . 2>/dev/null | head -50
```

2. **File search** - Find files by name
```bash
find . -name "*$ARGUMENTS*" -type f 2>/dev/null | grep -v node_modules | grep -v __pycache__ | head -20
```

3. **Definition search** - Find function/class definitions
```bash
# Python
grep -rn "def $ARGUMENTS\|class $ARGUMENTS" --include="*.py" . 2>/dev/null

# TypeScript/JavaScript
grep -rn "function $ARGUMENTS\|const $ARGUMENTS\|class $ARGUMENTS" --include="*.ts" --include="*.js" . 2>/dev/null

# Go
grep -rn "func $ARGUMENTS\|type $ARGUMENTS" --include="*.go" . 2>/dev/null
```

4. **Import search** - Find where something is imported
```bash
grep -rn "import.*$ARGUMENTS\|from.*$ARGUMENTS\|require.*$ARGUMENTS" --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null
```

5. **Usage search** - Find where something is used
```bash
grep -rn "\.$ARGUMENTS\|$ARGUMENTS(" --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null | head -30
```

## Output Format

```markdown
## Search Results: "$ARGUMENTS"

### Definitions Found
| File | Line | Match |
|------|------|-------|
| ... | ... | ... |

### Usages Found
| File | Line | Context |
|------|------|---------|
| ... | ... | ... |

### Related Files
- [List of files containing the query]

### Summary
- Definitions: N
- Usages: M
- Files: K
```

## Follow-up Actions

After search, offer:
1. Open specific file for detailed view
2. Search for related terms
3. Show file structure around matches
