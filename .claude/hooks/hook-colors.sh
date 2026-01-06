#!/bin/bash
# hook-colors.sh - Colored output utility for hooks
# Source this file to get colored hook status indicators

# ANSI Colors
declare -A HOOK_COLORS=(
    # PreToolUse hooks - warm colors
    ["pre-write-check"]=$'\033[1;97;41m'      # White on Red
    ["pretool-laziness-check"]=$'\033[1;30;43m'  # Black on Yellow
    ["pretool-hallucination-check"]=$'\033[1;97;45m'  # White on Magenta
    ["dangerous-command-check"]=$'\033[1;97;101m'  # White on Bright Red

    # PostToolUse hooks - cool colors
    ["post-write-validate"]=$'\033[1;97;44m'   # White on Blue
    ["file-edit-tracker"]=$'\033[1;30;46m'     # Black on Cyan
    ["context-detector"]=$'\033[1;30;42m'      # Black on Green
    ["research-quality-check"]=$'\033[1;97;104m'  # White on Bright Blue
    ["doc-size-detector"]=$'\033[1;30;106m'    # Black on Bright Cyan

    # Stop hooks - neutral/warning
    ["laziness-check"]=$'\033[1;30;103m'       # Black on Bright Yellow
    ["honesty-check"]=$'\033[1;97;105m'        # White on Bright Magenta
    ["stop-verify"]=$'\033[1;30;47m'           # Black on White

    # SubagentStop hooks
    ["research-validator"]=$'\033[1;97;102m'   # White on Bright Green
    ["agent-handoff-validator"]=$'\033[1;30;107m'  # Black on Bright White
)

RESET=$'\033[0m'
BOLD=$'\033[1m'

# Default color for unknown hooks
DEFAULT_HOOK_COLOR=$'\033[1;97;100m'  # White on Bright Black

# Get hook name from script name
get_hook_name() {
    local script_path="$1"
    local name=$(basename "$script_path" .sh)
    name=$(basename "$name" .py)
    echo "$name"
}

# Get color for a hook
get_hook_color() {
    local hook_name="$1"
    local color="${HOOK_COLORS[$hook_name]}"
    if [ -z "$color" ]; then
        color="$DEFAULT_HOOK_COLOR"
    fi
    echo "$color"
}

# Output colored hook status to stderr
# Usage: hook_status "pre-write-check" "CHECKING" "file.py"
hook_status() {
    local hook_name="$1"
    local status="$2"
    local detail="${3:-}"

    local color=$(get_hook_color "$hook_name")
    local icon="⚡"

    # Different icons for different statuses
    case "$status" in
        "START"|"CHECKING"|"RUNNING")
            icon="▶"
            ;;
        "OK"|"PASS"|"CONTINUE")
            icon="✓"
            ;;
        "BLOCK"|"FAIL"|"ERROR")
            icon="✗"
            ;;
        "WARN"|"SKIP")
            icon="⚠"
            ;;
    esac

    # Format output
    local display_name=$(echo "$hook_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')

    if [ -n "$detail" ]; then
        echo -e "${color} ${icon} ${display_name}: ${status} ${RESET} ${detail}" >&2
    else
        echo -e "${color} ${icon} ${display_name}: ${status} ${RESET}" >&2
    fi
}

# Compact one-liner status
hook_compact() {
    local hook_name="$1"
    local status="$2"
    local color=$(get_hook_color "$hook_name")
    echo -e "${color} ${status} ${RESET}" >&2
}
