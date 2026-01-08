#!/bin/bash
# Verify NPM package exists
# Usage: ./npm-verify.sh <package-name>

if [ -z "$1" ]; then
    echo "Usage: $0 <package-name>"
    exit 1
fi

result=$(npm view "$1" version 2>/dev/null)
if [ -n "$result" ]; then
    echo "FOUND: $1@$result"
    exit 0
else
    echo "NOT_FOUND: $1"
    exit 1
fi
