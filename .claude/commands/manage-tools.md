# /manage-tools

Manage Claude Protocol components between global (~/.claude/) and project (./.claude/) scope.

## Usage

```
/manage-tools              # Interactive mode - show menu
/manage-tools list         # List all components and their locations
/manage-tools promote <type> <name>   # Copy component to global scope
/manage-tools localize <type> <name>  # Copy component to project scope
/manage-tools disable <hook-name>     # Create no-op override in project
```

## Component Types

| Type | Description | Location |
|------|-------------|----------|
| `hook` | Hook scripts (.sh, .py) | `hooks/` |
| `agent` | Agent definitions (.md) | `agents/` |
| `skill` | Skill definitions | `skills/` |
| `command` | Slash commands (.md) | `commands/` |

## Commands

### list
Show all components in both scopes with override indicators.

**Output format:**
```
GLOBAL (~/.claude/):
  hooks/
    ✓ run-hook.sh
    ✓ laziness-check.sh
  agents/
    ✓ architect.md

PROJECT (./.claude/):
  hooks/
    ✓ pre-write-check.sh
    ⊘ laziness-check.sh (overrides global)
  agents/
    ✓ frontend-designer.md
```

### promote <type> <name>
Copy a component from project to global scope, making it available in all projects.

**Examples:**
```
/manage-tools promote hook pre-write-check.sh
/manage-tools promote agent frontend-designer
/manage-tools promote skill frontend-design
```

**Behavior:**
1. Find component in project .claude/
2. Copy to ~/.claude/ (same relative path)
3. Report success

### localize <type> <name>
Copy a component from global to project scope, allowing project-specific customization.

**Examples:**
```
/manage-tools localize hook laziness-check.sh
/manage-tools localize agent architect
```

**Behavior:**
1. Find component in ~/.claude/
2. Copy to project .claude/
3. Project version now takes precedence (same-name replacement)

### disable <hook-name>
Create a no-op version of a hook in project scope to disable a global hook.

**Example:**
```
/manage-tools disable laziness-check.sh
```

**Creates:**
```bash
#!/bin/bash
# Disabled for this project
# Original: ~/.claude/hooks/laziness-check.sh
exit 0
```

## Scope Precedence

Project components **always** take precedence over global:

1. When a hook runs, `run-hook.sh` checks project first
2. If found in project, uses project version
3. If not in project, falls back to global
4. If not in either, gracefully skips

This enables:
- **Override**: Customize a global hook for one project
- **Disable**: Create empty hook to skip global behavior
- **Extend**: Add project-specific hooks alongside global

## Examples

### Make frontend-designer available globally
```
> /manage-tools promote agent frontend-designer
Copying .claude/agents/domain/frontend-designer.md
     → ~/.claude/agents/domain/frontend-designer.md
✓ frontend-designer is now available in all projects
```

### Customize laziness-check for a project
```
> /manage-tools localize hook laziness-check.sh
Copying ~/.claude/hooks/laziness-check.sh
     → .claude/hooks/laziness-check.sh
✓ laziness-check.sh copied to project
  Edit .claude/hooks/laziness-check.sh to customize
```

### Disable honesty-check for a legacy project
```
> /manage-tools disable honesty-check.sh
Creating no-op override at .claude/hooks/honesty-check.sh
✓ honesty-check.sh disabled for this project
  Global version at ~/.claude/hooks/honesty-check.sh is unchanged
```

## Implementation Notes

When executing this command:

1. **For `list`**:
   - Scan both `~/.claude/` and `./.claude/`
   - For each component type, list files
   - Mark overrides where project shadows global

2. **For `promote`**:
   - Validate component exists in project
   - Create target directory if needed
   - Copy file preserving structure
   - Set executable permission for hooks

3. **For `localize`**:
   - Validate component exists in global
   - Create target directory if needed
   - Copy file preserving structure
   - Warn that this creates an override

4. **For `disable`**:
   - Create minimal bash script that exits 0
   - Include comment about what it disables
   - Set executable permission
