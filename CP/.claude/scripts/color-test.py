#!/usr/bin/env python3
"""Test script to debug color output in Claude Code."""
import sys

# Raw ANSI codes - no abstraction
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"

print("=== STDOUT COLOR TEST ===")
print(f"{RED}RED{RESET} {GREEN}GREEN{RESET} {YELLOW}YELLOW{RESET} {BLUE}BLUE{RESET}")
print(f"{BG_RED}{BOLD} WHITE ON RED {RESET}")
print(f"{BG_GREEN}{BOLD} WHITE ON GREEN {RESET}")
print(f"{BG_YELLOW}{BOLD} BLACK ON YELLOW {RESET}")
print(f"{BG_BLUE}{BOLD} WHITE ON BLUE {RESET}")

print("\n=== STDERR COLOR TEST ===", file=sys.stderr)
print(f"{RED}RED{RESET} {GREEN}GREEN{RESET} {YELLOW}YELLOW{RESET} {BLUE}BLUE{RESET}", file=sys.stderr)
print(f"{BG_RED}{BOLD} WHITE ON RED {RESET}", file=sys.stderr)
print(f"{BG_GREEN}{BOLD} WHITE ON GREEN {RESET}", file=sys.stderr)
print(f"{BG_YELLOW}{BOLD} BLACK ON YELLOW {RESET}", file=sys.stderr)
print(f"{BG_BLUE}{BOLD} WHITE ON BLUE {RESET}", file=sys.stderr)

# Also test with escape sequence written differently
print("\n=== ALT ESCAPE SEQUENCES ===")
print("\x1b[92mGREEN via hex\x1b[0m")
print("\033[92mGREEN via octal\033[0m")

# Test if maybe Claude Code needs a flush
sys.stdout.flush()
sys.stderr.flush()

print("\n=== UNICODE + COLOR ===")
print(f"{GREEN}✓{RESET} Success with checkmark")
print(f"{RED}✗{RESET} Failure with X")
print(f"{YELLOW}⚠{RESET} Warning with triangle")
