#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
INPUT="$1"
DANGEROUS=("rm -rf /" "rm -rf ~" "sudo rm" "chmod 777" "curl.*|.*sh" "wget.*|.*sh" "mkfs" ":(){:|:&};:")
for p in "${DANGEROUS[@]}"; do
    if echo "$INPUT" | grep -qE "$p"; then
        echo '{"decision": "block", "reason": "Dangerous command blocked"}'
        exit 0
    fi
done
echo '{"decision": "allow"}'
