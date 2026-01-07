---
description: Check for and apply protocol updates. Usage: /proto-update [--check] [--auto] [--models] [--rollback]
---

$ARGUMENTS

# Protocol Update Command

Check for protocol updates and apply them with interactive approval.

## Quick Start

**Run the update script:**
```bash
python3 .claude/scripts/proto-update.py --check
```

## Usage

| Command | Description |
|---------|-------------|
| `/proto-update` | Check for updates (same as --check) |
| `/proto-update --check` | Show available updates without applying |
| `/proto-update --update` | Apply updates interactively |
| `/proto-update --update --auto` | Auto-accept all updates |
| `/proto-update --models` | Check/update model versions only |
| `/proto-update --rollback` | Restore from last backup |

## What the Script Does

### 1. Fetch Remote Manifest
```python
# Reads repository URL from protocol-manifest.json
# Fetches https://raw.githubusercontent.com/.../protocol-manifest.json
```

### 2. Compare Versions
- Compares local vs remote protocol version
- Identifies individual component updates (skills, hooks, commands)
- Detects customized components (modified checksums)

### 3. Create Backup
Before any changes:
```
.claude/backups/
└── 20260107_143022/
    ├── backup-metadata.json
    ├── .claude/agents/...
    └── protocol-manifest.json
```

### 4. Apply Updates
- Downloads changed files from GitHub
- Writes to local paths
- Verifies checksums

### 5. Update Model Versions
- Checks agent files for deprecated model strings
- Updates to current model versions

## Example Output

```
════════════════════════════════════════════════════════════════
  PROTOCOL UPDATE CHECK
════════════════════════════════════════════════════════════════

  Local:  1.1.0
  Remote: 1.2.0 ← UPDATE AVAILABLE

  Component updates: 5
    • skills/workflow: 1.0.0 → 1.1.0
    • hooks/laziness-check.sh: 1.0.0 → 1.0.1
    • agents/core/architect: 1.0.0 → 1.1.0
    ... and 2 more

  ⚠️  Model updates needed: 2
    • architect: claude-3-5-sonnet-20241022...
    • security-scanner: claude-3-opus-20240229...

Run with --update to apply changes
```

## Local State Tracking

Updates are tracked in `.claude/config/local-state.json`:
```json
{
  "installed_version": "1.2.0",
  "last_check": "2026-01-07T14:30:22",
  "last_update": "2026-01-07T14:32:15",
  "customized_components": [],
  "skipped_updates": []
}
```

## Rollback

If an update causes problems:
```bash
python3 .claude/scripts/proto-update.py --rollback
```

This restores from the most recent backup.

## Related Commands

| Command | Purpose |
|---------|---------|
| `/proto-status` | Show current protocol status |
| `/validate` | Validate protocol installation |
| `/proto-help` | Protocol documentation |
