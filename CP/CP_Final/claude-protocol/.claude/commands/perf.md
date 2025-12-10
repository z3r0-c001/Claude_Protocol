---
description: Analyze code for performance issues
---
$ARGUMENTS

Run performance analysis:

1. **Algorithmic Analysis**: Detect:
   - O(n²) or worse patterns
   - Inefficient lookups
   - Redundant iterations
   - Suboptimal data structures

2. **Memory Analysis**: Detect:
   - Memory leaks
   - Unbounded growth
   - Missing cleanup
   - Excessive allocation

3. **I/O Analysis**: Detect:
   - Sequential operations that could be parallel
   - Missing caching
   - Repeated file reads
   - Inefficient network calls

4. **Database Analysis**: Detect:
   - N+1 queries
   - Missing indexes (check query patterns)
   - SELECT * usage
   - Unoptimized joins

**Arguments:**
- No arguments: Analyze current directory
- `--path <dir>`: Analyze specific directory
- `--file <file>`: Analyze specific file
- `--profile`: Include profiling suggestions

**Output:**

```
## Performance Analysis Report

### Summary
- Critical: X issues
- High: Y issues
- Medium: Z issues

### Issues Found
[Detailed list with file, line, pattern, impact, suggestion]

### Optimization Opportunities
1. [Highest impact change]
2. [Additional improvements]

### Profiling Recommendations
- [How to profile specific hotspots]
```
