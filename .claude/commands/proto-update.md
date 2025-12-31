---
description: Check for and apply protocol updates with interactive approval. Usage: /proto-update [--check] [--analyze] [--auto]
---

$ARGUMENTS

# Protocol Update Command

Check for protocol updates from the upstream repository and apply them with interactive approval.

## Usage

```
/proto-update              # Interactive update check and apply
/proto-update --check      # Check only, don't apply (dry run)
/proto-update --analyze    # Full analysis with smart suggestions
/proto-update --auto       # Accept all non-breaking updates
/proto-update --component <name>  # Update specific component only
```

## Process

### Step 1: Check GitHub Connection

Verify the upstream repository is reachable and fetch the remote manifest.

```bash
# Test connectivity
curl -sL -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/{user}/{repo}/main/protocol-manifest.json"
```

### Step 2: Compare Versions

Invoke the `protocol-updater` agent in plan mode to:
1. Fetch remote manifest
2. Compare with local installation
3. Identify available updates
4. Detect customized components

Display summary:
```
Claude Protocol Update Check
============================

Local Version:  1.0.0
Remote Version: 1.1.0

Components Status:
  Agents:    2 updates available (20 total)
  Skills:    1 update available (16 total)
  Commands:  0 updates available (23 total)
  Hooks:     1 update available (18 total)
  Config:    1 update available (2 total)

Customized (will skip): 3 components
```

### Step 3: Interactive Approval (if not --check)

For each available update, invoke `protocol-updater` agent to:
1. Show component name and version change
2. Display summary of changes
3. Show diff on request
4. Assess risk level
5. Present approval options

### Step 4: Apply Updates

For approved updates:
1. Create backup of current files
2. Fetch new content from GitHub
3. Write to local paths
4. Verify checksums
5. Update local manifest

### Step 5: Post-Update Verification

1. Run basic health checks
2. Suggest running `/validate`
3. Display summary of changes

## Options

| Option | Description |
|--------|-------------|
| (none) | Interactive update with approval for each change |
| `--check` | Dry run - show available updates without applying |
| `--analyze` | Run protocol-analyzer for smart suggestions |
| `--auto` | Accept all non-breaking updates automatically |
| `--force` | Reset to upstream (requires confirmation, loses customizations) |
| `--component <name>` | Update only the specified component |
| `--rollback` | Restore from most recent backup |

## Agent Integration

**Uses these agents:**
- `protocol-updater` - Fetches and applies updates
- `protocol-analyzer` - Provides smart suggestions (with --analyze)

## Memory Integration

Records to memory:
- `project-learnings/protocol-version`: Current installed version
- `project-learnings/protocol-last-update`: Timestamp of last update
- `decisions/protocol-customizations`: Components marked as customized

## Examples

### Check for Updates (Dry Run)
```
User: /proto-update --check

Claude: Checking for updates...

Protocol Update Check
=====================
Local: 1.0.0 | Remote: 1.1.0

Available Updates:
• agents/core/architect (1.0.0 → 1.1.0) - Added plan mode
• hooks/laziness-check.sh (1.0.0 → 1.0.1) - Fixed JSON output
• skills/workflow (1.0.0 → 1.1.0) - New commit workflow

Run /proto-update to apply these updates.
```

### Full Analysis
```
User: /proto-update --analyze

Claude: Running protocol analysis...

[Invokes protocol-analyzer agent]

Analysis Report
===============
Health Score: 85/100

Issues Found:
• 3 agents missing supports_plan_mode (auto-fixable)
• 1 unused skill detected
• 2 configuration optimizations available

Recommendations:
1. [High] Update to version 1.1.0 for plan mode support
2. [Medium] Enable security-scanner on /pr command
3. [Low] Remove unused research-verifier skill
```

### Update Specific Component
```
User: /proto-update --component agents/core/architect

Claude: Updating agents/core/architect...

Current: 1.0.0 → New: 1.1.0

Changes:
• Added supports_plan_mode: true
• New execution modes section
• Updated response format

[Shows diff]

Apply this update? (y/n)
```

## Backup Location

Backups are stored in:
```
.claude/backups/
└── 2025-12-31T10-00-00/
    ├── manifest.local.json
    ├── agents/
    ├── hooks/
    └── ...
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Network unreachable | Use cached manifest if available |
| Checksum mismatch | Abort update, restore backup |
| Permission denied | Check file permissions |
| Invalid manifest | Report error, suggest manual review |
