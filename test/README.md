# Protocol Test Framework

Reusable test infrastructure for validating Claude Protocol installations.

## Location

This directory contains the test framework for validating protocol installations.

## Status

**NOT pushed to GitHub** - Development infrastructure only.

## Usage

```bash
# From Claude Code, run:
# "Run protocol tests"
# or reference framework/runner.md
```

## Structure

```
test/
├── README.md              ← This file
└── framework/
    ├── test_cases.md      ← Test definitions (A, B, C, D, E)
    ├── guardrails.md      ← Anti-hallucination + anti-boasting rules
    ├── reporting.md       ← Report templates
    └── runner.md          ← Execution workflow
```

## Test Run Directories

Each test run creates a fresh directory with a randomized camelCase name.

Examples: `silverFox/`, `blueSky/`, `ironBolt/`
