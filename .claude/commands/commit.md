---
description: Safely commit changes after running sanitization. Usage: /commit <message>
---

# Commit Command

Safely commit changes with validation and **specific per-file commit messages**.

## CRITICAL REQUIREMENT

**Every commit MUST have specific, unique descriptions for each changed file.**

This is NOT optional. Generic messages like "Updated files" or "Fixed bugs" will be BLOCKED.

## Process

1. **Analyze Changes**
   - Run `git status` to identify all changed files
   - Run `git diff --staged` and `git diff` to understand EACH file's changes
   - Read each changed file to understand what specifically changed

2. **Generate Specific Commit Message**
   For EACH file, write what specifically changed:
   - What functions/classes were added/modified?
   - What bug was fixed and how?
   - What feature was implemented?
   - What configuration changed?

3. **Validate Message**
   - Run commit-message-validator.sh
   - BLOCK if generic patterns detected
   - BLOCK if message too short (<10 chars)
   - WARN if 4+ files without per-file breakdown

4. **Pre-Commit Checks**
   - Run laziness check on staged files
   - Verify no placeholder code
   - Check for accidental secrets

5. **Create Commit**
   - Use detailed message with file-by-file breakdown

## Commit Message Format (MANDATORY)

```
<Specific summary: action + what + context>

- path/to/file1.ts: <SPECIFIC change - what function/class/feature>
- path/to/file2.py: <SPECIFIC change - what was fixed/added/modified>
- path/to/file3.md: <SPECIFIC change - what section/content>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Examples

### GOOD - Specific Per-File Messages:
```
Add user authentication with JWT tokens and rate limiting

- src/auth/jwt.ts: New generateToken() and validateToken() functions with RS256 signing
- src/middleware/auth.ts: Authentication middleware checking Authorization header, 401 on invalid
- src/routes/login.ts: POST /login endpoint with bcrypt password verification, rate limited to 5/min
- src/config/auth.ts: JWT secret and expiry configuration (24h tokens)
- tests/auth.test.ts: 15 unit tests covering token generation, validation, and expiry

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### BAD - Will Be BLOCKED:
```
Updated files
```
```
Fixed bugs
```
```
Various improvements
```
```
WIP
```
```
Changes to auth
```
```
- file1.ts: updated
- file2.ts: changes
- file3.ts: fixed
```

### BAD - Too Vague (Even with file list):
```
Update authentication

- src/auth/jwt.ts: Updated
- src/middleware/auth.ts: Modified
- src/routes/login.ts: Changed
```

### GOOD - Same files, specific:
```
Fix token expiry bug causing premature logout

- src/auth/jwt.ts: Changed expiry from 1h to 24h, added refresh token support
- src/middleware/auth.ts: Added token refresh logic when <1h remaining
- src/routes/login.ts: Return both access and refresh tokens on login
```

## Validation Rules

Will **BLOCK** commit if:
- Generic message pattern detected (Updated files, Fixed bugs, WIP, etc.)
- Message summary < 10 characters
- Per-file descriptions are just "updated", "changed", "modified"
- Placeholder code in staged files

Will **WARN** if:
- 4+ files without per-file breakdown
- No specific action verbs (add, fix, remove, update, implement)

## For Large Changes (10+ files)

1. Create CHANGELOG-vX.X.X.md with complete file-by-file details
2. Reference changelog in commit:

```
Release v1.2.0: Feature name and key highlights

See CHANGELOG-v1.2.0.md for complete file-by-file breakdown (47 files).

Key changes:
- New authentication system with JWT and refresh tokens
- Admin dashboard with user management
- API rate limiting and caching layer

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**REMEMBER**: Read each changed file, understand what SPECIFICALLY changed, write UNIQUE descriptions. Never copy-paste the same description for multiple files.
