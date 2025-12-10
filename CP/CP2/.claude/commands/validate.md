---
description: Run full validation suite on Claude protocol files and project code
---

$ARGUMENTS

# VALIDATION

Run the complete validation suite:

```bash
bash .claude/scripts/validate-all.sh
```

Then run code quality checks:

```bash
bash .claude/scripts/laziness-check.sh .
bash .claude/scripts/hallucination-check.sh .
```

Report all results. If any failures, provide specific fixes.

## Validation Gates

1. **Structure** - All required directories and files exist
2. **JSON** - All JSON files are valid
3. **Scripts** - All scripts have valid syntax and are executable
4. **Agents** - All agents have proper frontmatter
5. **Skills** - All skills have SKILL.md with frontmatter
6. **Hooks** - settings.json has all required hooks
7. **Laziness** - No placeholder code anywhere
8. **Hallucinations** - All imports and packages verified

## Requirements

- ALL gates must pass
- ZERO errors allowed
- Warnings should be addressed if possible
