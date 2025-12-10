---
description: Show Claude Bootstrap Protocol state, memory status, and project health
---

# PROTO-STATUS - Protocol Health Check

Display comprehensive status of the Claude Bootstrap Protocol.

## Run Status Checks

```bash
#!/bin/bash

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                    CLAUDE BOOTSTRAP PROTOCOL - STATUS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Protocol Version
if [ -f ".claude-plugin/plugin.json" ]; then
    VERSION=$(grep '"version"' .claude-plugin/plugin.json | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    echo "Protocol Version: $VERSION"
else
    echo "Protocol Version: NOT INSTALLED"
fi
echo ""

# Memory Status
echo "MEMORY STATUS"
echo "─────────────────────────────────────────────────────────────────────────────"
if [ -d ".claude/memory" ]; then
    for f in .claude/memory/*.json; do
        [ -f "$f" ] || continue
        name=$(basename "$f" .json)
        count=$(grep -c '"key"' "$f" 2>/dev/null || echo "0")
        printf "  %-20s %s entries\n" "$name:" "$count"
    done
else
    echo "  Memory directory not found"
fi
echo ""

# Git Status
echo "GIT STATUS"
echo "─────────────────────────────────────────────────────────────────────────────"
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
    STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l)
    COMMITS_AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "?")
    echo "  Branch: $BRANCH"
    echo "  Uncommitted changes: $CHANGES"
    echo "  Staged files: $STAGED"
    echo "  Commits ahead of origin: $COMMITS_AHEAD"
    
    # Check hooks
    if [ -f ".git/hooks/pre-commit" ]; then
        echo "  Pre-commit hook: ✓ installed"
    else
        echo "  Pre-commit hook: ✗ not installed"
    fi
else
    echo "  Not a git repository"
fi
echo ""

# Component Status
echo "COMPONENTS"
echo "─────────────────────────────────────────────────────────────────────────────"
AGENTS=$(ls .claude/agents/*.md 2>/dev/null | wc -l)
COMMANDS=$(ls .claude/commands/*.md 2>/dev/null | wc -l)
SCRIPTS=$(ls .claude/scripts/*.sh 2>/dev/null | wc -l)
SKILLS=$(find .claude/skills -name 'SKILL.md' 2>/dev/null | wc -l)
echo "  Agents: $AGENTS"
echo "  Commands: $COMMANDS"
echo "  Scripts: $SCRIPTS"
echo "  Skills: $SKILLS"
echo ""

# Last Checks
echo "VALIDATION STATUS"
echo "─────────────────────────────────────────────────────────────────────────────"
if [ -f ".claude/memory/protocol-state.json" ]; then
    LAST_VALIDATION=$(grep 'last_validation' .claude/memory/protocol-state.json 2>/dev/null | head -1)
    echo "  $LAST_VALIDATION"
else
    echo "  No validation history"
fi
echo ""

# Quick Health Checks
echo "HEALTH CHECKS"
echo "─────────────────────────────────────────────────────────────────────────────"

# Check JSON validity
JSON_OK=true
for f in .claude/settings.json .claude-plugin/plugin.json .mcp.json; do
    if [ -f "$f" ]; then
        python3 -m json.tool "$f" > /dev/null 2>&1 || { echo "  ✗ $f - invalid JSON"; JSON_OK=false; }
    fi
done
$JSON_OK && echo "  ✓ All JSON files valid"

# Check scripts
SCRIPT_OK=true
for f in .claude/scripts/*.sh; do
    bash -n "$f" 2>/dev/null || { echo "  ✗ $(basename $f) - syntax error"; SCRIPT_OK=false; }
done
$SCRIPT_OK && echo "  ✓ All scripts valid syntax"

# Check CLAUDE.md exists
[ -f "CLAUDE.md" ] && echo "  ✓ CLAUDE.md present" || echo "  ✗ CLAUDE.md missing - run /bootstrap"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
```

## Output

Present the status clearly. Highlight any issues that need attention.

If issues found, suggest fixes:
- Missing CLAUDE.md → "Run /bootstrap"
- Hooks not installed → "Run bash .claude/scripts/install-git-hooks.sh"
- Invalid JSON → "Check file syntax"
