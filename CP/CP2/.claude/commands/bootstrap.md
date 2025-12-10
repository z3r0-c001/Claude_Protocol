---
description: Generate CLAUDE.md and project tooling. Usually called automatically by /proto-init.
---

$ARGUMENTS

# BOOTSTRAP - GENERATE PROJECT TOOLING

This command generates project-specific Claude tooling. It's usually called automatically after `/proto-init` completes discovery.

## Prerequisites

Before running, ensure:
1. Protocol files are installed (.claude/ directory)
2. Project discovery has been run (protocol-state.json populated)

If discovery hasn't run:
```bash
cat .claude/memory/protocol-state.json
```

If empty or missing, run `/proto-init` first.

---

## STEP 1: Load Discovered Context

```bash
# Load memory
bash .claude/scripts/load-memory.sh

# Read what proto-init discovered
cat .claude/memory/protocol-state.json
```

Use this information for all generation steps.

---

## STEP 2: Generate CLAUDE.md

Create `CLAUDE.md` at project root using the project-bootstrap skill template.

**Required sections:**
1. Project name and description (from discovery)
2. Quick command reference table
3. Project structure overview
4. Tech stack summary
5. Coding conventions and patterns
6. Protected paths (files Claude should never modify)
7. Development workflow
8. Instructions for Claude

**Quality rules:**
- NO placeholder text like "[describe here]"
- NO generic content - everything specific to THIS project
- Use actual detected values
- Include real file paths from the project

---

## STEP 3: Generate Project Skill (if needed)

If project has unique patterns, create `.claude/skills/{project-name}/SKILL.md`:

```markdown
---
name: {project-name}
description: "Project-specific patterns for {name}. Auto-invoked for all tasks."
---

# {Project Name} Patterns

## Architecture
[Actual architecture from discovery]

## Code Patterns
[Patterns found in codebase]

## Testing Patterns
[How tests are structured]

## Common Tasks
[Frequent operations with commands]
```

---

## STEP 4: Update Protocol State

Mark bootstrap as complete:
```bash
# Update protocol-state.json with:
# - bootstrap_complete: true
# - bootstrap_at: timestamp
# - files_generated: list
```

---

## STEP 5: Install Git Hooks

```bash
bash .claude/scripts/install-git-hooks.sh
```

---

## STEP 6: Run Validation

```bash
bash .claude/scripts/validate-all.sh
```

**If validation fails**: Fix issues before completing.

---

## STEP 7: Output Summary

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                         BOOTSTRAP COMPLETE                                     ║
╚════════════════════════════════════════════════════════════════════════════════╝

FILES GENERATED:
  ✓ CLAUDE.md
  ✓ .claude/skills/{name}/SKILL.md (if applicable)
  ✓ Git hooks installed

VALIDATION: ✓ Passed

You're ready to use:
  /feature <desc>  - Build a feature
  /fix <issue>     - Fix a bug
  /test            - Run tests
  /commit <msg>    - Commit safely

What would you like to work on?
```

---

## RULES

1. **Use discovered data** - Don't re-ask questions proto-init already asked
2. **No placeholders** - All content must be real and specific
3. **Validate everything** - Don't complete until validation passes
4. **Keep it actionable** - Generated files should be immediately useful
