---
name: performance-analyzer
description: "Analyze code for performance issues including algorithmic complexity, memory leaks, I/O bottlenecks, and database query problems. Use for performance-critical code or when slowness is reported."
---

# Performance Analyzer Skill

This skill provides automated performance issue detection.

## When to Use

- When performance issues reported
- Reviewing performance-critical code
- Before scaling up services
- During code review of hot paths
- When optimizing algorithms

## Analysis Categories

### 1. Algorithmic Complexity

**O(n²) Patterns:**
```bash
# Nested loops on same collection
grep -rn --include="*.js" --include="*.ts" --include="*.py" \
  -A5 'for.*{' | grep -E 'for.*{|\.includes\(|\.find\(|\.indexOf\('
```

**Inefficient Lookups:**
```bash
# Array methods in loops
grep -rn --include="*.js" --include="*.ts" \
  -E 'for.*\{' -A10 | grep -E '\.find\(|\.filter\(|\.includes\('
```

### 2. Memory Issues

**Unbounded Growth:**
```bash
# Arrays that only push, never clear
grep -rn --include="*.js" --include="*.ts" \
  -E '\.push\(' | grep -v -E '\.pop\(|\.shift\(|\.splice\(|= \[\]'
```

**Missing Cleanup:**
```bash
# addEventListener without removeEventListener
grep -rn --include="*.js" --include="*.ts" \
  'addEventListener' | grep -v 'removeEventListener'
```

### 3. I/O Bottlenecks

**Sequential Awaits:**
```bash
# Sequential awaits that could be parallel
grep -rn --include="*.js" --include="*.ts" \
  -B2 'await ' | grep -E 'for.*\{|forEach'
```

**Missing Caching:**
```bash
# File reads in functions (potential repeated reads)
grep -rn --include="*.js" --include="*.ts" \
  'readFileSync\|readFile' | grep -v -E 'cache|Cache'
```

### 4. Database Issues

**N+1 Queries:**
```bash
# ORM queries in loops
grep -rn --include="*.py" --include="*.js" --include="*.ts" \
  -E 'for.*:' -A5 | grep -E '\.query\(|\.find\(|\.filter\('
```

**SELECT *:**
```bash
# SELECT * queries
grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.sql" \
  'SELECT \*'
```

## Profiling Commands

### JavaScript/Node.js
```bash
# CPU profiling
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Memory profiling
node --inspect app.js
```

### Python
```bash
# CPU profiling
python -m cProfile -o output.prof script.py

# Memory profiling
python -m memory_profiler script.py
```

## Output Format

```json
{
  "analysis_date": "2025-01-01T00:00:00Z",
  "issues": [
    {
      "id": "PERF-001",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "category": "algorithmic|memory|io|database",
      "file": "path/to/file",
      "line": 23,
      "pattern": "O(n²) nested loop",
      "impact": "Description of performance impact",
      "suggestion": "How to fix",
      "estimated_improvement": "~10x faster"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },
  "recommendations": []
}
```

## Integration

Integrates with:
- `performance-analyzer` agent for detailed analysis
- CI/CD pipelines for performance regression detection
- Profiling tools for runtime analysis

## Files

- `detect-complexity.sh`: Algorithmic complexity detection
- `detect-memory.sh`: Memory issue detection
- `detect-io.sh`: I/O bottleneck detection
- `detect-db.sh`: Database issue detection
