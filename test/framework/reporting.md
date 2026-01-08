# Report Templates

## Real-Time Progress

```
═══════════════════════════════════════════════════
 TEST A: New Project Initialization
═══════════════════════════════════════════════════

[A1] Creating test directory...          ✓ PASS
[A2] Cloning from GitHub...              ✓ PASS
[A3] Running install.sh...               ✓ PASS
[A4] Running /proto-init...              ⏳ IN PROGRESS
```

---

## Per-Test Summary

```
┌─────────────────────────────────────────────────┐
│ TEST A: New Project Initialization              │
├─────────────────────────────────────────────────┤
│ Status:     ✓ PASSED                            │
│ Duration:   [X] seconds                         │
│ Steps:      [N]/[N] completed                   │
├─────────────────────────────────────────────────┤
│ Validations:                                    │
│   ✓ CLAUDE.md exists                            │
│   ✓ .claude/ structure complete                 │
│   ✓ Hooks executable ([N]/[N])                  │
│   ✓ JSON files valid                            │
├─────────────────────────────────────────────────┤
│ Evidence:                                       │
│   $ [command]                                   │
│   [output]                                      │
└─────────────────────────────────────────────────┘
```

---

## Failure Report

```
┌─────────────────────────────────────────────────┐
│ TEST B: Existing Project - MERGE                │
├─────────────────────────────────────────────────┤
│ Status:     ✗ FAILED at step [X]                │
│ Duration:   [X] seconds                         │
│ Steps:      [N]/[N] completed                   │
├─────────────────────────────────────────────────┤
│ FAILURE DETAILS:                                │
│                                                 │
│ Step:       [Step description]                  │
│ Expected:   [What should happen]                │
│ Actual:     [What happened]                     │
│                                                 │
│ Evidence:                                       │
│   $ [command]                                   │
│   [output]                                      │
│                                                 │
│ Possible Causes:                                │
│   1. [Cause 1]                                  │
│   2. [Cause 2]                                  │
└─────────────────────────────────────────────────┘
```

---

## Final Report

```
╔═══════════════════════════════════════════════════════════════╗
║              PROTOCOL TEST SUITE - FINAL REPORT               ║
╠═══════════════════════════════════════════════════════════════╣
║ Test Environment                                              ║
║   Directory:  [path]                                          ║
║   Source:     github.com/z3r0-c001/Claude_Protocol            ║
║   Version:    [version]                                       ║
║   Date:       [timestamp]                                     ║
╠═══════════════════════════════════════════════════════════════╣
║ RESULTS                                                       ║
╠═══════════════════════════════════════════════════════════════╣
║   TEST A: [description]       [✓/✗] [status]    ([Xs])        ║
║   TEST B: [description]       [✓/✗] [status]    ([Xs])        ║
║   ...                                                         ║
╠═══════════════════════════════════════════════════════════════╣
║ TOTALS                                                        ║
║   Passed:     [N]/[N]                                         ║
║   Failed:     [N]                                             ║
║   Duration:   [total]                                         ║
╠═══════════════════════════════════════════════════════════════╣
║ LIMITATIONS                                                   ║
║   - Single run, single machine                                ║
║   - Controlled inputs                                         ║
║   - [Other limitations]                                       ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Failure Analysis Template

```
## Failure Analysis: TEST [X]

### Investigation

1. [Check performed]
   Result: [✓/✗] [Finding]

2. [Check performed]
   Result: [✓/✗] [Finding]

### Root Cause

[Description of what went wrong]

### Affected Code

File: [path]
Section: [name]
Line: [number]

### Evidence

$ [command]
[output]

### Recommended Fix

[What needs to change]
```

---

## Artifacts List

```
## Test Artifacts

Location: [test directory path]

├── test-results/
│   ├── TEST_A.json
│   ├── TEST_B.json
│   └── summary.json
│
├── snapshots/
│   ├── before_[test].md
│   └── after_[test].md
│
└── logs/
    ├── install.log
    └── proto-init.log
```
