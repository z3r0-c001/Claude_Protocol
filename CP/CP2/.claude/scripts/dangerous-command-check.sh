#!/bin/bash
# Dangerous Command Check Script
# Blocks potentially destructive bash commands
# Outputs structured JSON with severity levels and alternatives

COMMAND="$1"

output_json() {
  local decision="$1"
  local severity="$2"
  local type="$3"
  local message="$4"
  local suggestion="$5"

  if [ "$decision" = "allow" ]; then
    echo '{"hook":"dangerous-command-check","decision":"allow","status":"pass","issues":[]}'
  else
    echo "{\"hook\":\"dangerous-command-check\",\"decision\":\"$decision\",\"status\":\"$( [ "$decision" = "block" ] && echo "error" || echo "warning" )\",\"severity\":\"$severity\",\"issues\":[{\"type\":\"$type\",\"command\":\"$COMMAND\",\"message\":\"$message\",\"suggestion\":\"$suggestion\"}]}"
  fi
}

# Extremely dangerous patterns - ALWAYS BLOCK
CRITICAL_PATTERNS=(
  "rm -rf /"
  "rm -rf /*"
  "rm -rf ~"
  "rm -rf \$HOME"
  ":(){ :|:& };:"
  "mkfs\."
  "dd if=.* of=/dev/"
  "> /dev/sda"
  "chmod -R 777 /"
  "chown -R .* /"
  "wget .* | sh"
  "curl .* | sh"
  "wget .* | bash"
  "curl .* | bash"
)

for pattern in "${CRITICAL_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    output_json "block" "block" "critical_danger" "CRITICAL: This command could destroy your system or data" "This command is too dangerous to execute. If you need to perform this operation, do it manually with extreme caution."
    exit 0
  fi
done

# Dangerous patterns - BLOCK with alternatives
declare -A DANGEROUS_ALTERNATIVES=(
  ["sudo rm"]="Consider using 'rm' without sudo, or be very specific about the path"
  ["sudo chmod"]="Consider using 'chmod' without sudo, or specify exact file paths"
  ["sudo chown"]="Consider using 'chown' without sudo, or specify exact file paths"
  ["rm -rf"]="Use 'rm -ri' for interactive mode, or be very specific about paths"
  ["rm -r /"]="Never delete from root. Specify the exact subdirectory to delete"
  ["> /etc/"]="Don't redirect to system config files directly"
  [">> /etc/"]="Don't append to system config files directly"
  ["shutdown"]="Use proper shutdown procedures through your system's interface"
  ["reboot"]="Use proper reboot procedures through your system's interface"
  ["init 0"]="Use 'shutdown' command instead for cleaner shutdown"
  ["init 6"]="Use 'reboot' command instead for cleaner reboot"
  ["kill -9 1"]="Never kill PID 1 (init). This will crash your system"
  ["killall"]="Use 'pkill' with specific process names for safer termination"
  ["pkill -9"]="Try 'pkill' without -9 first to allow graceful shutdown"
)

for pattern in "${!DANGEROUS_ALTERNATIVES[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    output_json "block" "ask" "dangerous" "DANGEROUS: $pattern detected in command" "${DANGEROUS_ALTERNATIVES[$pattern]}"
    exit 0
  fi
done

# Suspicious patterns - WARN
declare -A SUSPICIOUS_ALTERNATIVES=(
  ["sudo"]="Consider if root privileges are really needed"
  ["rm -r"]="Make sure you're deleting the intended directory"
  ["chmod 777"]="777 permissions are rarely needed. Consider 755 for directories, 644 for files"
  ["eval"]="eval can execute arbitrary code. Verify the input is trusted"
  ["\$("]="Command substitution can be dangerous with untrusted input"
  ["base64 -d"]="Decoding base64 could execute hidden commands"
  ["base64 --decode"]="Decoding base64 could execute hidden commands"
)

for pattern in "${!SUSPICIOUS_ALTERNATIVES[@]}"; do
  if echo "$COMMAND" | grep -qiE "$pattern"; then
    output_json "warn" "suggest" "suspicious" "CAUTION: $pattern - ${SUSPICIOUS_ALTERNATIVES[$pattern]}" "Proceed with caution. ${SUSPICIOUS_ALTERNATIVES[$pattern]}"
    exit 0
  fi
done

# Command appears safe
output_json "allow" "" "" "" ""
exit 0
