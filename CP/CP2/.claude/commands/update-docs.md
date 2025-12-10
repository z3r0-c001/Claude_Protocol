---
description: Update existing documentation to match current code. Finds and fixes stale docs.
---

$ARGUMENTS

# UPDATE-DOCS - Synchronize Documentation with Code

Find and fix documentation that has drifted from the actual code.

## Process

### Step 1: Identify Documentation Files

```bash
# Find all documentation
find . -type f \( -name "*.md" -o -name "*.rst" -o -name "*.txt" \) \
    | grep -v node_modules | grep -v __pycache__

# Common locations
ls -la README.md CHANGELOG.md CONTRIBUTING.md docs/*.md 2>/dev/null
```

### Step 2: Detect Staleness

For each doc file, check for:

#### Code References
- Function/class names that no longer exist
- File paths that have moved
- Import statements that are outdated
- CLI commands/flags that changed

#### Version Mismatches
- Package versions in examples vs actual
- API versions referenced
- Dependency versions

#### Broken Examples
- Code snippets that don't compile/run
- Outdated API usage
- Missing required parameters

#### Missing Information
- New functions not documented
- New config options not listed
- New CLI commands not shown

### Step 3: Generate Diff Report

```markdown
## Documentation Audit Report

### Stale References Found

#### README.md
| Line | Issue | Current Code | Doc Says |
|------|-------|--------------|----------|
| 45 | Function renamed | `fetchData()` | `getData()` |
| 72 | Parameter added | `init(config, options)` | `init(config)` |
| 103 | File moved | `src/utils/` | `lib/utils/` |

#### docs/API.md
| Line | Issue | Current Code | Doc Says |
|------|-------|--------------|----------|
| 23 | Function removed | (deleted) | `oldFunction()` |
| 89 | Return type changed | `Promise<User[]>` | `User[]` |

### Missing Documentation
- `src/newModule.ts` - No documentation exists
- `fetchUsers()` - New function, not in API.md
- `--verbose` flag - New CLI option, not documented

### Broken Examples
| File | Line | Error |
|------|------|-------|
| README.md | 55 | `import { old } from 'pkg'` - 'old' not exported |
| docs/API.md | 120 | Example uses removed parameter |
```

### Step 4: Apply Fixes

For each issue, either:
1. **Auto-fix** - Clear mapping from old → new
2. **Suggest fix** - Ambiguous, show options
3. **Flag for review** - Needs human decision

```markdown
## Fixes Applied

### Auto-fixed (5 issues)
- README.md:45 - Updated `getData()` → `fetchData()`
- README.md:72 - Added missing `options` parameter
- docs/API.md:89 - Updated return type

### Manual Review Needed (2 issues)
- README.md:103 - File moved but new location unclear
- docs/API.md:23 - Function removed, decide whether to remove docs

### Suggestions
- Add documentation for `src/newModule.ts`
- Add `--verbose` to CLI reference
```

### Step 5: Validate Fixes

After updates:
```bash
# Check markdown syntax
npx markdownlint docs/*.md README.md

# Verify code blocks compile (if possible)
# Extract and test code snippets

# Check internal links
npx markdown-link-check README.md
```

## Output Format

```markdown
## Documentation Update Complete

### Summary
- Files scanned: 8
- Issues found: 12
- Auto-fixed: 9
- Manual review: 3

### Files Modified
| File | Changes |
|------|---------|
| README.md | 4 updates |
| docs/API.md | 5 updates |

### Still Needs Attention
1. `docs/API.md:23` - Removed function documentation decision
2. `README.md:103` - Verify new file path

### Validation
- [x] Markdown syntax valid
- [x] Internal links working
- [ ] Code examples tested (run `/test` to verify)
```

## Integration with Workflow

This command should be run:
- Before releases
- After major refactors
- As part of PR review
- When `/docs` detects existing documentation

## Save State

```bash
bash .claude/scripts/save-memory.sh project-learnings "docs-updated" "$(date): Fixed X stale references"
```
