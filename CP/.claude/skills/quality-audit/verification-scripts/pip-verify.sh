#!/bin/bash
# Verify PyPI package exists
# Usage: ./pip-verify.sh <package-name>

if [ -z "$1" ]; then
    echo "Usage: $0 <package-name>"
    exit 1
fi

# Try pip index first (newer pip versions)
result=$(pip index versions "$1" 2>/dev/null | head -1)
if [ -n "$result" ]; then
    echo "FOUND: $result"
    exit 0
fi

# Fallback: try pip show on a search
result=$(pip search "$1" 2>/dev/null | grep "^$1 " | head -1)
if [ -n "$result" ]; then
    echo "FOUND: $result"
    exit 0
fi

# Last resort: check PyPI API
status=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$1/json")
if [ "$status" = "200" ]; then
    version=$(curl -s "https://pypi.org/pypi/$1/json" | grep -o '"version":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "FOUND: $1@$version"
    exit 0
fi

echo "NOT_FOUND: $1"
exit 1
