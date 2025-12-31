#!/bin/bash
# PostToolUse hook: Validate written files
# Reads JSON from stdin, checks syntax, outputs error to stderr on failure

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh" 2>/dev/null || { hook_log() { :; }; }

# Read JSON input from stdin
INPUT=$(cat)

# Extract file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    echo '{"continue": true}'
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Syntax validation based on file type
case "$EXT" in
    py)
        if command -v python3 &> /dev/null; then
            RESULT=$(python3 -m py_compile "$FILE_PATH" 2>&1)
            if [ $? -ne 0 ]; then
                ERRMSG=$(echo "$RESULT" | jq -Rs .)
                echo "{\"decision\": \"block\", \"message\": $ERRMSG}"
                exit 0
            fi
        fi
        ;;
    js|jsx)
        if command -v node &> /dev/null; then
            RESULT=$(node --check "$FILE_PATH" 2>&1)
            if [ $? -ne 0 ]; then
                ERRMSG=$(echo "$RESULT" | jq -Rs .)
                echo "{\"decision\": \"block\", \"message\": $ERRMSG}"
                exit 0
            fi
        fi
        ;;
    json)
        if command -v python3 &> /dev/null; then
            RESULT=$(python3 -c "import json, sys; json.load(open(sys.argv[1]))" "$FILE_PATH" 2>&1)
            if [ $? -ne 0 ]; then
                ERRMSG=$(echo "$RESULT" | jq -Rs .)
                echo "{\"decision\": \"block\", \"message\": $ERRMSG}"
                exit 0
            fi
        fi
        ;;
    sh|bash)
        if command -v bash &> /dev/null; then
            RESULT=$(bash -n "$FILE_PATH" 2>&1)
            if [ $? -ne 0 ]; then
                ERRMSG=$(echo "$RESULT" | jq -Rs .)
                echo "{\"decision\": \"block\", \"message\": $ERRMSG}"
                exit 0
            fi
        fi
        ;;
esac

# Success - output JSON
echo '{"continue": true}'
exit 0
