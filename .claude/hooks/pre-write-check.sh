#!/bin/bash
# PreToolUse hook: Check before writing files
# Validates target path - blocks protected dirs and sensitive files
# Exit code 2 + stderr = BLOCK

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-colors.sh" 2>/dev/null || true
HOOK_NAME="pre-write-check"

# Read JSON input from stdin
INPUT=$(cat)

# Extract file path and content
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty' 2>/dev/null)

# If no file path, allow through
if [ -z "$FILE_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

hook_status "$HOOK_NAME" "CHECKING" "$(basename "$FILE_PATH")"

ISSUES=""

# Protected paths that should not be written
PROTECTED_PATTERNS=(
    "^/etc/"
    "^/usr/"
    "^/bin/"
    "^/sbin/"
    "^/boot/"
    "^/var/log/"
    "\.git/objects"
    "\.git/refs"
    "node_modules/"
    "__pycache__/"
    "\.env$"
    "\.pem$"
    "\.key$"
    "credentials\."
    "secrets\."
    "id_rsa"
    "id_ed25519"
    "\.\./\.\."
    "\.\./"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
    if echo "$FILE_PATH" | grep -qE -- "$pattern"; then
        ISSUES="${ISSUES}• Protected path: $pattern\n"
    fi
done

# Check for secrets in content
if [ -n "$CONTENT" ]; then
    SECRET_PATTERNS=(
        "password.*=.*['\"][^'\"]{8,}['\"]"
        "api[_-]?key.*=.*['\"][^'\"]{16,}['\"]"
        "secret.*=.*['\"][^'\"]{8,}['\"]"
        "token.*=.*['\"][^'\"]{16,}['\"]"
        "aws_access_key"
        "private_key"
        "-----BEGIN.*PRIVATE KEY-----"
    )

    for pattern in "${SECRET_PATTERNS[@]}"; do
        if echo "$CONTENT" | grep -qiE -- "$pattern"; then
            ISSUES="${ISSUES}• Potential secret in content: $pattern\n"
        fi
    done
fi

if [ -n "$ISSUES" ]; then
    hook_status "$HOOK_NAME" "BLOCK" "$FILE_PATH"

    # Output JSON block decision
    BLOCK_MSG=$(echo -e "BLOCKED: Cannot write to this location.\n\nIssues:\n${ISSUES}" | jq -Rs .)
    echo "{\"decision\": \"block\", \"message\": $BLOCK_MSG}"
    exit 0
fi

hook_status "$HOOK_NAME" "OK" "$(basename "$FILE_PATH")"
echo '{"continue": true}'
exit 0
