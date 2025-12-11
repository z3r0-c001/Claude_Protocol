#!/bin/bash
# Verify file paths exist
# Usage: ./path-check.sh <file-with-paths>
# Or: echo "path1\npath2" | ./path-check.sh

found=0
missing=0

check_path() {
    local path="$1"
    # Skip empty lines and comments
    [[ -z "$path" || "$path" =~ ^# ]] && return
    
    # Expand home directory
    path="${path/#\~/$HOME}"
    
    if [ -e "$path" ]; then
        echo "EXISTS: $path"
        ((found++))
    else
        echo "MISSING: $path"
        ((missing++))
    fi
}

if [ -n "$1" ] && [ -f "$1" ]; then
    # Read from file
    while IFS= read -r path; do
        check_path "$path"
    done < "$1"
else
    # Read from stdin
    while IFS= read -r path; do
        check_path "$path"
    done
fi

echo ""
echo "Summary: $found found, $missing missing"

[ "$missing" -gt 0 ] && exit 1
exit 0
