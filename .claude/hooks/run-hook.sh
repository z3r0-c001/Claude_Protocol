#!/bin/bash
# run-hook.sh - Wrapper for hook execution with error handling
# Supports both project-specific and global hooks
# Project hooks take precedence over global (same-name replacement)
#
# Usage: bash run-hook.sh <hook-name>
# Example: bash run-hook.sh pretool-laziness-check.py

set -o pipefail

HOOK_NAME="$1"

# Validate input
if [ -z "$HOOK_NAME" ]; then
    echo "[HOOK ERROR] No hook name provided to run-hook.sh" >&2
    exit 0
fi

# Define search paths
PROJECT_HOOK="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/$HOOK_NAME"
GLOBAL_HOOK="$HOME/.claude/hooks/$HOOK_NAME"

# Project hooks take precedence over global (same-name replacement)
if [ -f "$PROJECT_HOOK" ]; then
    HOOK_PATH="$PROJECT_HOOK"
    HOOK_SCOPE="project"
elif [ -f "$GLOBAL_HOOK" ]; then
    HOOK_PATH="$GLOBAL_HOOK"
    HOOK_SCOPE="global"
else
    # Neither exists - report and exit gracefully
    echo "[HOOK] $HOOK_NAME not found" >&2
    if [ -n "$CLAUDE_PROJECT_DIR" ]; then
        echo "[HOOK] Checked: $PROJECT_HOOK" >&2
    fi
    echo "[HOOK] Checked: $GLOBAL_HOOK" >&2
    exit 0  # Don't block on missing hook
fi

# Check if script is executable (warn but continue)
if [ ! -x "$HOOK_PATH" ]; then
    echo "[HOOK WARNING] $HOOK_NAME is not executable, running anyway" >&2
fi

# Run the hook based on extension
if [[ "$HOOK_NAME" == *.py ]]; then
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo "[HOOK ERROR] python3 not found in PATH" >&2
        exit 0
    fi
    python3 "$HOOK_PATH"
    EXIT_CODE=$?
elif [[ "$HOOK_NAME" == *.sh ]]; then
    bash "$HOOK_PATH"
    EXIT_CODE=$?
else
    # Default to bash for unknown extensions
    bash "$HOOK_PATH"
    EXIT_CODE=$?
fi

# Report unexpected exit codes (0=success, 2=intentional block)
if [ $EXIT_CODE -ne 0 ] && [ $EXIT_CODE -ne 2 ]; then
    echo "[HOOK ERROR] $HOOK_NAME ($HOOK_SCOPE) exited with code: $EXIT_CODE" >&2
fi

exit $EXIT_CODE
