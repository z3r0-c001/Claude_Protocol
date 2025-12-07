#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
# Outputs JSON for automated processing

COMMAND="$1"
OUTPUT_MODE="${2:-json}"

# Dangerous patterns
DANGEROUS_PATTERNS=(
  "rm -rf /"
  "rm -rf ~"
  "rm -rf *"
  "sudo rm"
  "> /dev/sda"
  "mkfs"
  "dd if="
  "chmod 777"
  "chmod -R 777"
  "curl .* | sh"
  "curl .* | bash"
  "wget .* | sh"
  "wget .* | bash"
  ":(){:|:&};:"
  "eval \$(curl"
  "eval \$(wget"
  "python -c.*__import__.*os.*system"
)

# Commands that need warning but not block
WARNING_PATTERNS=(
  "sudo"
  "rm -rf"
  "git push.*force"
  "git reset --hard"
  "npm publish"
  "pip install.*--user"
  "docker rm"
  "docker rmi"
)

DECISION="approve"
ISSUES=""
SEVERITY="pass"

# Check dangerous patterns
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    DECISION="block"
    SEVERITY="critical"
    ISSUES="${ISSUES}{\"type\":\"dangerous_command\",\"pattern\":\"$pattern\",\"severity\":\"block\",\"suggestion\":\"This command is potentially destructive and has been blocked\"},"
  fi
done

# Check warning patterns
for pattern in "${WARNING_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    if [ "$DECISION" != "block" ]; then
      SEVERITY="warning"
    fi
    ISSUES="${ISSUES}{\"type\":\"risky_command\",\"pattern\":\"$pattern\",\"severity\":\"warn\",\"suggestion\":\"Consider the implications of this command\"},"
  fi
done

# Remove trailing comma
ISSUES="${ISSUES%,}"

if [ "$OUTPUT_MODE" = "json" ]; then
  if [ -z "$ISSUES" ]; then
    echo '{"hook":"dangerous-command-check","status":"pass","decision":"approve"}'
  else
    echo "{\"hook\":\"dangerous-command-check\",\"status\":\"$SEVERITY\",\"decision\":\"$DECISION\",\"issues\":[$ISSUES]}"
  fi
else
  if [ "$DECISION" = "block" ]; then
    echo "BLOCKED: Dangerous command detected"
    exit 1
  elif [ "$SEVERITY" = "warning" ]; then
    echo "WARNING: Risky command detected"
  fi
fi

[ "$DECISION" = "block" ] && exit 1
exit 0
