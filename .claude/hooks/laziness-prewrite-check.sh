#!/bin/bash
# PreToolUse hook: Block lazy code patterns before write
# Checks content for placeholders, TODOs, stubs, and delegation phrases
# Exit code 2 + stderr = BLOCK (Claude must retry)

SCRIPT_DIR="$(dirname "$0")"
source "$SCRIPT_DIR/hook-logger.sh" 2>/dev/null || {
    hook_log() { :; }
    notify_hook_start() { :; }
    notify_hook_result() { :; }
}

notify_hook_start "Write"

# Read JSON input from stdin
INPUT=$(cat)

# Extract content from tool input
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty' 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)

# If no content, allow through
if [ -z "$CONTENT" ]; then
    notify_hook_result "continue"
    exit 0
fi

ISSUES=""

# ===== PLACEHOLDER PATTERNS =====
if echo "$CONTENT" | grep -qE '// \.\.\.|\.\.\. more|etc\.\.\.'; then
    ISSUES="${ISSUES}• Ellipsis placeholder (// ... or ... more)\n"
fi

if echo "$CONTENT" | grep -qE '/\* \.\.\. \*/|# \.\.\.'; then
    ISSUES="${ISSUES}• Comment placeholder\n"
fi

# ===== STUB PATTERNS =====
if echo "$CONTENT" | grep -qE '^\s*pass\s*$'; then
    ISSUES="${ISSUES}• Python stub (pass)\n"
fi

if echo "$CONTENT" | grep -qE 'raise NotImplementedError|throw new NotImplementedError'; then
    ISSUES="${ISSUES}• NotImplementedError stub\n"
fi

if echo "$CONTENT" | grep -qiE '// TODO|# TODO|// FIXME|# FIXME'; then
    ISSUES="${ISSUES}• TODO/FIXME marker\n"
fi

if echo "$CONTENT" | grep -qiE '// implement|# implement|// add implementation|// fill in'; then
    ISSUES="${ISSUES}• Unimplemented marker\n"
fi

# ===== DELEGATION PATTERNS (in comments/docstrings) =====
if echo "$CONTENT" | grep -qiE '# you could|// you could|# you.ll need|// you.ll need'; then
    ISSUES="${ISSUES}• Delegation in comment (telling user what to do)\n"
fi

# ===== INCOMPLETE PATTERNS =====
if echo "$CONTENT" | grep -qiE 'add your .* here|insert .* here|your .* goes here'; then
    ISSUES="${ISSUES}• Placeholder instruction (add your X here)\n"
fi

if echo "$CONTENT" | grep -qE '^\s*\.\.\.\s*$'; then
    ISSUES="${ISSUES}• Bare ellipsis line\n"
fi

# Check for issues
if [ -n "$ISSUES" ]; then
    hook_log "BLOCK" "Incomplete code detected in $FILE_PATH"
    notify_hook_result "block"

    # Exit code 2 + stderr = BLOCK in PreToolUse
    echo -e "BLOCKED: Incomplete/lazy code detected.\n\nIssues found:\n${ISSUES}\nYou MUST write complete, working code. No placeholders, no TODOs, no stubs." >&2
    exit 2
fi

hook_log "OK" "Code passed completeness check"
notify_hook_result "continue"
exit 0
