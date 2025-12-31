---
description: Safely commit changes after running sanitization. Usage: /commit <message>
---

# Commit Command

Safely commit changes with validation and specific commit messages.

## Process

1. **Analyze Changes**
   - Run `git status` to identify all changed files
   - Run `git diff --staged` and `git diff` to understand changes
   - Categorize changes by type (new, modified, deleted)

2. **Generate Specific Commit Message**
   - Write a clear summary line describing WHAT changed
   - List each file with a specific description of its changes
   - NEVER use generic messages like "Updated files" or "Various changes"

3. **Pre-Commit Checks**
   - Run laziness check on staged files
   - Verify no placeholder code
   - Check for accidental secrets

4. **Create Commit**
   - Use detailed message with file-by-file breakdown
   - Add standard footer

5. **Post-Commit**
   - Verify commit was successful
   - Show commit hash

## Commit Message Format (REQUIRED)

```
<Summary: What was done, specific and actionable>

<File-by-file breakdown:>
- path/to/file1.ts: <Specific change description>
- path/to/file2.py: <Specific change description>
- path/to/file3.md: <Specific change description>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Examples

### GOOD Commit Message:
```
Add user authentication with JWT tokens

- src/auth/jwt.ts: New JWT token generation and validation utilities
- src/middleware/auth.ts: Authentication middleware with token refresh
- src/routes/login.ts: Login endpoint with rate limiting
- tests/auth.test.ts: Unit tests for JWT functions and middleware

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### BAD Commit Messages (NEVER USE):
- "Updated files"
- "Fixed bugs"
- "Various improvements"
- "WIP"
- "Changes"
- "Misc updates"

## Safety Checks

Will BLOCK commit if:
- Generic/placeholder commit message detected
- Placeholder code detected (`// ...`, `TODO`, `pass`)
- Potential secrets found
- Syntax errors in staged files

## For Large Changes

When committing many files (10+):
1. Create a CHANGELOG-vX.X.X.md with full details
2. Use summary commit message referencing the changelog
3. Include key highlights in commit body

Example:
```
Release v1.1.0: Self-updating protocol, frontend design, docs overhaul

See CHANGELOG-v1.1.0.md for complete file-by-file breakdown.

Key changes:
- Self-updating protocol system with manifest tracking
- Frontend design agents and skills
- Document processing system
- Comprehensive documentation with disclaimers
- License updated to CC BY-NC-SA 4.0 with clarifications

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

Analyze all changes, generate specific commit message, run checks, and create commit.
