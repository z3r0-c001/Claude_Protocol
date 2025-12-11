---
description: Generate CLAUDE.md and project tooling. Usually called automatically by /proto-init.
---

# Bootstrap Project Tooling

Generate customized Claude Code tooling for this project.

## Process

1. **Read Project Configuration**
   - Examine package.json, requirements.txt, or equivalent
   - Check for existing CLAUDE.md
   - Identify framework and tooling

2. **Generate CLAUDE.md**
   Create a comprehensive CLAUDE.md with:
   - Project description
   - Build/test/lint commands
   - Key files and patterns
   - Important notes

3. **Configure Hooks**
   Ensure settings.json has:
   - Appropriate PreToolUse hooks
   - PostToolUse validation
   - Stop hooks for quality

4. **Initialize Memory**
   Set up memory with:
   - protocol-state
   - project-learnings (empty)
   - user-preferences (empty)

5. **Validate**
   Run validation on all generated files

## Options

If CLAUDE.md already exists:
- Preserve custom sections
- Update detected information
- Merge configurations

## Output

Report:
- Files created/updated
- Commands configured
- Any issues found

---

Begin by reading the project root for configuration files.
