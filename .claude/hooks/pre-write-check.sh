#!/bin/bash
# PreToolUse hook: Check before writing files
# Validates target path and content

FILE_PATH="$1"
CONTENT="$2"
OUTPUT_MODE="${3:-json}"

ISSUES=""
DECISION="approve"

# Protected paths that should not be written
PROTECTED_PATHS=(
  "/etc/"
  "/usr/"
  "/bin/"
  "/sbin/"
  "/boot/"
  "/var/log/"
  ".git/objects"
  ".git/refs"
  "node_modules/"
  "__pycache__/"
  ".env"
  "*.pem"
  "*.key"
  "credentials.*"
  "secrets.*"
)

# Check protected paths
for pattern in "${PROTECTED_PATHS[@]}"; do
  if echo "$FILE_PATH" | grep -qE "$pattern"; then
    DECISION="block"
    ISSUES="${ISSUES}{\"type\":\"protected_path\",\"path\":\"$FILE_PATH\",\"pattern\":\"$pattern\",\"severity\":\"block\",\"suggestion\":\"Cannot write to protected path\"},"
  fi
done

# Check for secrets in content
SECRET_PATTERNS=(
  "password.*=.*['\"][^'\"]+['\"]"
  "api[_-]?key.*=.*['\"][^'\"]+['\"]"
  "secret.*=.*['\"][^'\"]+['\"]"
  "token.*=.*['\"][^'\"]+['\"]"
  "aws_access_key"
  "private_key"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
  if echo "$CONTENT" | grep -qiE "$pattern"; then
    ISSUES="${ISSUES}{\"type\":\"potential_secret\",\"pattern\":\"$pattern\",\"severity\":\"warn\",\"suggestion\":\"Content may contain sensitive information\"},"
  fi
done

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"pre-write-check","status":"pass","decision":"approve"}'
  else
    STATUS="warning"
    [ "$DECISION" = "block" ] && STATUS="blocked"
    echo "{\"hook\":\"pre-write-check\",\"status\":\"$STATUS\",\"decision\":\"$DECISION\",\"file\":\"$FILE_PATH\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$DECISION" = "block" ]; then
    echo "BLOCKED: Cannot write to protected path"
    exit 1
  fi
fi

[ "$DECISION" = "block" ] && exit 1
exit 0
