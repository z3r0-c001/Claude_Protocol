---
description: Safely commit changes after running sanitization. Usage: /commit <message>
---

# Commit Command

Safely commit changes with validation.

## Process

1. **Pre-Commit Checks**
   - Run laziness check on staged files
   - Verify no placeholder code
   - Check for accidental secrets

2. **Review Changes**
   - Show git status
   - Display diff summary
   - List files to be committed

3. **Create Commit**
   - Use provided message
   - Add standard footer
   - Sign-off if configured

4. **Post-Commit**
   - Verify commit was successful
   - Show commit hash
   - Remind about push if needed

## Commit Message Format

```
<type>: <short description>

<body if needed>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Safety Checks

Will BLOCK commit if:
- Placeholder code detected
- Potential secrets found
- Syntax errors in staged files

---

Run pre-commit checks and create the commit if all pass.
