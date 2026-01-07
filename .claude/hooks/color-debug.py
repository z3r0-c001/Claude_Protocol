#!/usr/bin/env python3
"""
color-debug.py - Minimal color test for Claude Code hook rendering
Run as: python3 .claude/hooks/color-debug.py
Or it will run automatically as a PreToolUse hook
"""
import sys
import json

# Raw ANSI - no dependencies, no logic
RED = "\033[91m"
GREEN = "\033[92m" 
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_BLUE = "\033[44m"
BG_YELLOW = "\033[43m"

# Output to STDERR (where hook status goes)
print(f"{BG_RED}{BOLD} RED BACKGROUND {RESET}", file=sys.stderr)
print(f"{BG_GREEN}{BOLD} GREEN BACKGROUND {RESET}", file=sys.stderr)
print(f"{BG_BLUE}{BOLD} BLUE BACKGROUND {RESET}", file=sys.stderr)
print(f"{BG_YELLOW}{BOLD} YELLOW BACKGROUND {RESET}", file=sys.stderr)
print(f"{RED}Red text{RESET} {GREEN}Green text{RESET} {YELLOW}Yellow text{RESET}", file=sys.stderr)

# Also try STDOUT
print(f"{CYAN}CYAN via stdout{RESET}")

# Flush both
sys.stdout.flush()
sys.stderr.flush()

# If running as hook, output valid JSON
# Check if we got JSON input (means we're running as a hook)
try:
    # Non-blocking check for stdin
    import select
    if select.select([sys.stdin], [], [], 0.0)[0]:
        input_data = sys.stdin.read()
        if input_data.strip():
            # We're a hook - output continue
            print('{"continue": true}')
except:
    pass
