#!/bin/bash
# hook-colors.sh - Colored output utility for bash hooks
# Source this file to get colored hook status indicators
#
# Supports NO_COLOR environment variable (https://no-color.org/)

# Check if colors should be enabled
_colors_enabled() {
    # NO_COLOR standard
    [[ -n "${NO_COLOR:-}" ]] && return 1
    # Check if stderr is a TTY
    [[ ! -t 2 ]] && return 1
    # Check TERM
    [[ "${TERM:-}" == "dumb" ]] && return 1
    return 0
}

if _colors_enabled; then
    COLORS_ENABLED=1
else
    COLORS_ENABLED=0
fi

# ANSI codes (empty if colors disabled)
if [[ "$COLORS_ENABLED" -eq 1 ]]; then
    RESET=$'\033[0m'
    BOLD=$'\033[1m'
    
    # Foreground
    BLACK=$'\033[30m'
    RED=$'\033[31m'
    GREEN=$'\033[32m'
    YELLOW=$'\033[33m'
    BLUE=$'\033[34m'
    MAGENTA=$'\033[35m'
    CYAN=$'\033[36m'
    WHITE=$'\033[37m'
    BRIGHT_WHITE=$'\033[97m'
    
    # Background
    BG_RED=$'\033[41m'
    BG_GREEN=$'\033[42m'
    BG_YELLOW=$'\033[43m'
    BG_BLUE=$'\033[44m'
    BG_MAGENTA=$'\033[45m'
    BG_CYAN=$'\033[46m'
    BG_WHITE=$'\033[47m'
    BG_BRIGHT_BLACK=$'\033[100m'
    BG_BRIGHT_RED=$'\033[101m'
    BG_BRIGHT_GREEN=$'\033[102m'
    BG_BRIGHT_YELLOW=$'\033[103m'
    BG_BRIGHT_BLUE=$'\033[104m'
    BG_BRIGHT_MAGENTA=$'\033[105m'
    BG_BRIGHT_CYAN=$'\033[106m'
    BG_BRIGHT_WHITE=$'\033[107m'
else
    RESET=""
    BOLD=""
    BLACK=""
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    MAGENTA=""
    CYAN=""
    WHITE=""
    BRIGHT_WHITE=""
    BG_RED=""
    BG_GREEN=""
    BG_YELLOW=""
    BG_BLUE=""
    BG_MAGENTA=""
    BG_CYAN=""
    BG_WHITE=""
    BG_BRIGHT_BLACK=""
    BG_BRIGHT_RED=""
    BG_BRIGHT_GREEN=""
    BG_BRIGHT_YELLOW=""
    BG_BRIGHT_BLUE=""
    BG_BRIGHT_MAGENTA=""
    BG_BRIGHT_CYAN=""
    BG_BRIGHT_WHITE=""
fi

# Hook color schemes - must match colors.py
declare -A HOOK_COLORS=(
    # PreToolUse hooks
    ["pre-write-check"]="${BRIGHT_WHITE}${BG_RED}${BOLD}"
    ["pretool-laziness-check"]="${BLACK}${BG_YELLOW}${BOLD}"
    ["pretool-hallucination-check"]="${BRIGHT_WHITE}${BG_MAGENTA}${BOLD}"
    ["dangerous-command-check"]="${BRIGHT_WHITE}${BG_BRIGHT_RED}${BOLD}"
    ["agent-announce"]="${BLACK}${BG_BRIGHT_BLUE}${BOLD}"
    
    # PostToolUse hooks
    ["post-write-validate"]="${BRIGHT_WHITE}${BG_BLUE}${BOLD}"
    ["file-edit-tracker"]="${BLACK}${BG_CYAN}${BOLD}"
    ["context-detector"]="${BLACK}${BG_GREEN}${BOLD}"
    ["research-quality-check"]="${BRIGHT_WHITE}${BG_BRIGHT_BLUE}${BOLD}"
    ["doc-size-detector"]="${BLACK}${BG_BRIGHT_CYAN}${BOLD}"
    
    # UserPromptSubmit hooks
    ["context-loader"]="${BLACK}${BG_BRIGHT_GREEN}${BOLD}"
    ["skill-activation-prompt"]="${BRIGHT_WHITE}${BG_GREEN}${BOLD}"
    
    # Stop hooks
    ["laziness-check"]="${BLACK}${BG_BRIGHT_YELLOW}${BOLD}"
    ["honesty-check"]="${BRIGHT_WHITE}${BG_BRIGHT_MAGENTA}${BOLD}"
    ["stop-verify"]="${BLACK}${BG_WHITE}${BOLD}"
    
    # SubagentStop hooks
    ["research-validator"]="${BRIGHT_WHITE}${BG_BRIGHT_GREEN}${BOLD}"
    ["agent-handoff-validator"]="${BLACK}${BG_BRIGHT_WHITE}${BOLD}"
)

# Default for unknown hooks
DEFAULT_HOOK_COLOR="${BRIGHT_WHITE}${BG_BRIGHT_BLACK}${BOLD}"

# Get hook name from script name
get_hook_name() {
    local script_path="$1"
    local name
    name=$(basename "$script_path" .sh)
    name=$(basename "$name" .py)
    echo "$name"
}

# Get color for a hook
get_hook_color() {
    local hook_name="$1"
    local color="${HOOK_COLORS[$hook_name]}"
    if [[ -z "$color" ]]; then
        color="$DEFAULT_HOOK_COLOR"
    fi
    echo "$color"
}

# Get status symbol
get_status_symbol() {
    local status="$1"
    case "${status^^}" in
        "START"|"CHECKING"|"RUNNING") echo ">" ;;
        "OK"|"PASS"|"CONTINUE") echo "+" ;;
        "BLOCK"|"FAIL"|"ERROR") echo "X" ;;
        "WARN"|"SKIP") echo "!" ;;
        *) echo "*" ;;
    esac
}

# Output colored hook status to stderr
# Usage: hook_status "pre-write-check" "CHECKING" "file.py"
hook_status() {
    local hook_name="$1"
    local status="$2"
    local detail="${3:-}"
    
    local color
    color=$(get_hook_color "$hook_name")
    local symbol
    symbol=$(get_status_symbol "$status")
    
    # Format display name (convert dashes to spaces, title case)
    local display_name
    display_name=$(echo "$hook_name" | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
    
    if [[ -n "$detail" ]]; then
        echo -e "${color} ${symbol} ${display_name}: ${status} ${RESET} ${detail}" >&2
    else
        echo -e "${color} ${symbol} ${display_name}: ${status} ${RESET}" >&2
    fi
}

# Compact one-liner status
hook_compact() {
    local hook_name="$1"
    local status="$2"
    local color
    color=$(get_hook_color "$hook_name")
    echo -e "${color} ${status} ${RESET}" >&2
}
