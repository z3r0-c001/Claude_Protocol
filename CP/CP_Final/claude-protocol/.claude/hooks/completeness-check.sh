#!/bin/bash
# PreToolUse hook: Warn on placeholder patterns
INPUT="$1"
if echo "$INPUT" | grep -qE '// \.\.\.|# \.\.\.|TODO|FIXME|pass$|NotImplementedError'; then
    echo '{"decision": "allow", "warning": "Incomplete code patterns detected"}'
else
    echo '{"decision": "allow"}'
fi
