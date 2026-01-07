#!/bin/bash
#
# Commit Message Validator Hook
# =============================
# Blocks generic/placeholder commit messages
# Ensures each commit has specific, meaningful descriptions
#

# Get the commit message from stdin or argument
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG=$(cat)
fi

# Generic patterns that should NEVER appear as the entire commit message
GENERIC_PATTERNS=(
    "^[Uu]pdated? files?\.?$"
    "^[Ff]ixed? bugs?\.?$"
    "^[Vv]arious (changes|improvements|updates|fixes)\.?$"
    "^[Mm]isc\.? (changes|updates|fixes)?\.?$"
    "^WIP\.?$"
    "^[Cc]hanges\.?$"
    "^[Uu]pdates?\.?$"
    "^[Ff]ixes?\.?$"
    "^[Ii]mprovements?\.?$"
    "^[Mm]inor (changes|updates|fixes)\.?$"
    "^[Ss]mall (changes|updates|fixes)\.?$"
    "^[Qq]uick fix\.?$"
    "^[Bb]ug fix\.?$"
    "^[Cc]ode (changes|updates|cleanup)\.?$"
    "^[Rr]efactor\.?$"
    "^[Cc]leanup\.?$"
    "^[Ss]tuff\.?$"
    "^[Ww]ork in progress\.?$"
    "^[Aa]dded? (files?|stuff|things)\.?$"
    "^[Rr]emoved? (files?|stuff|things)\.?$"
    "^[Mm]odified? files?\.?$"
    "^\.+$"
    "^-+$"
    "^_+$"
    "^\s*$"
)

# Extract first line (summary)
FIRST_LINE=$(echo "$COMMIT_MSG" | head -1)

# Check against generic patterns
for pattern in "${GENERIC_PATTERNS[@]}"; do
    if echo "$FIRST_LINE" | grep -qE "$pattern"; then
        echo '{"status": "block", "message": "Generic commit message detected. Must be specific. Bad: \"Updated files\" Good: \"Add JWT authentication with token refresh\""}'
        exit 1
    fi
done

# Check minimum length (too short = probably generic)
if [ ${#FIRST_LINE} -lt 10 ]; then
    echo '{"status": "block", "message": "Commit message too short. Must be at least 10 characters with specific description."}'
    exit 1
fi

# Check for file-specific details when multiple files changed
STAGED_COUNT=$(git diff --cached --name-only 2>/dev/null | wc -l)
if [ "$STAGED_COUNT" -gt 3 ]; then
    # For 4+ files, should have file breakdown or reference a changelog
    if ! echo "$COMMIT_MSG" | grep -qE "(^- |CHANGELOG|See .* for|Key changes:)"; then
        echo '{"status": "suggest", "message": "Multiple files staged but no file-by-file breakdown found. Consider adding per-file descriptions."}'
    fi
fi

# Passed all checks
echo '{"status": "pass", "message": "Commit message validation passed"}'
exit 0
