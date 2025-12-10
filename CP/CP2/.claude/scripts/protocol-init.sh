#!/bin/bash
# Protocol Initialization Script
# Performs comprehensive project discovery for the Claude Bootstrap Protocol

set -e

PROTOCOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(pwd)"
STATE_FILE="$PROJECT_ROOT/.claude/memory/protocol-state.json"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       CLAUDE BOOTSTRAP PROTOCOL v1.2 - DISCOVERY              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Create required directories
mkdir -p "$PROJECT_ROOT/.claude"/{agents,skills,commands,memory,scripts,hooks}

# Initialize state
if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" << 'EOF'
{
  "initialized": false,
  "discovery_complete": false,
  "generation_complete": false,
  "validation_complete": false,
  "project": {
    "name": null,
    "type": null,
    "languages": [],
    "frameworks": [],
    "build_command": null,
    "test_command": null,
    "lint_command": null
  },
  "generated_files": [],
  "validation_results": [],
  "errors": []
}
EOF
fi

echo ""
echo "▶ PHASE 1: PROJECT DISCOVERY"
echo "─────────────────────────────────────────────────────────────────"

# Detect if this is a new or existing project
if [ -d ".git" ] || [ -f "package.json" ] || [ -f "pyproject.toml" ] || [ -f "Cargo.toml" ] || [ -f "go.mod" ] || [ -f "pom.xml" ]; then
  echo "  ✓ Existing project detected"
  PROJECT_TYPE="existing"
else
  echo "  ○ New project detected (no manifest files found)"
  PROJECT_TYPE="new"
fi

# Language detection
echo ""
echo "  Detecting languages..."
LANGUAGES=""

# Check for manifests first (more reliable)
[ -f "package.json" ] && LANGUAGES="$LANGUAGES javascript/typescript"
[ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ] && LANGUAGES="$LANGUAGES python"
[ -f "Cargo.toml" ] && LANGUAGES="$LANGUAGES rust"
[ -f "go.mod" ] && LANGUAGES="$LANGUAGES go"
[ -f "pom.xml" ] || [ -f "build.gradle" ] && LANGUAGES="$LANGUAGES java"

# Fall back to file extension detection
if [ -z "$LANGUAGES" ]; then
  [ -n "$(find . -maxdepth 3 -name '*.py' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES python"
  [ -n "$(find . -maxdepth 3 -name '*.ts' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES typescript"
  [ -n "$(find . -maxdepth 3 -name '*.js' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES javascript"
  [ -n "$(find . -maxdepth 3 -name '*.go' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES go"
  [ -n "$(find . -maxdepth 3 -name '*.rs' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES rust"
  [ -n "$(find . -maxdepth 3 -name '*.java' -type f 2>/dev/null | head -1)" ] && LANGUAGES="$LANGUAGES java"
fi

LANGUAGES=$(echo "$LANGUAGES" | xargs)
echo "  ✓ Languages: ${LANGUAGES:-none detected}"

# Framework detection
echo ""
echo "  Detecting frameworks..."
FRAMEWORKS=""

if [ -f "package.json" ]; then
  [ -n "$(grep -l '"react"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS react"
  [ -n "$(grep -l '"next"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS nextjs"
  [ -n "$(grep -l '"vue"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS vue"
  [ -n "$(grep -l '"express"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS express"
  [ -n "$(grep -l '"fastify"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS fastify"
  [ -n "$(grep -l '"nest"' package.json 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS nestjs"
fi

if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  REQ_FILE="${pyproject.toml:-requirements.txt}"
  [ -n "$(grep -li 'django' $REQ_FILE 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS django"
  [ -n "$(grep -li 'flask' $REQ_FILE 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS flask"
  [ -n "$(grep -li 'fastapi' $REQ_FILE 2>/dev/null)" ] && FRAMEWORKS="$FRAMEWORKS fastapi"
fi

FRAMEWORKS=$(echo "$FRAMEWORKS" | xargs)
echo "  ✓ Frameworks: ${FRAMEWORKS:-none detected}"

# Build system detection
echo ""
echo "  Detecting build system..."
BUILD_CMD=""
TEST_CMD=""
LINT_CMD=""

if [ -f "package.json" ]; then
  BUILD_CMD=$(node -pe "JSON.parse(require('fs').readFileSync('package.json')).scripts?.build || ''" 2>/dev/null)
  [ -n "$BUILD_CMD" ] && BUILD_CMD="npm run build"
  TEST_CMD=$(node -pe "JSON.parse(require('fs').readFileSync('package.json')).scripts?.test || ''" 2>/dev/null)
  [ -n "$TEST_CMD" ] && TEST_CMD="npm test"
  LINT_CMD=$(node -pe "JSON.parse(require('fs').readFileSync('package.json')).scripts?.lint || ''" 2>/dev/null)
  [ -n "$LINT_CMD" ] && LINT_CMD="npm run lint"
fi

if [ -f "pyproject.toml" ]; then
  BUILD_CMD="${BUILD_CMD:-pip install -e .}"
  TEST_CMD="${TEST_CMD:-pytest}"
  LINT_CMD="${LINT_CMD:-ruff check .}"
fi

if [ -f "Makefile" ]; then
  [ -n "$(grep '^build:' Makefile)" ] && BUILD_CMD="${BUILD_CMD:-make build}"
  [ -n "$(grep '^test:' Makefile)" ] && TEST_CMD="${TEST_CMD:-make test}"
  [ -n "$(grep '^lint:' Makefile)" ] && LINT_CMD="${LINT_CMD:-make lint}"
fi

echo "  ✓ Build: ${BUILD_CMD:-not detected}"
echo "  ✓ Test: ${TEST_CMD:-not detected}"
echo "  ✓ Lint: ${LINT_CMD:-not detected}"

# Git info
echo ""
echo "  Checking git info..."
if [ -d ".git" ]; then
  REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
  BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
  echo "  ✓ Remote: ${REMOTE:-none}"
  echo "  ✓ Branch: $BRANCH"
else
  echo "  ○ No git repository"
fi

# Existing Claude config
echo ""
echo "  Checking existing Claude configuration..."
[ -f "CLAUDE.md" ] && echo "  ✓ CLAUDE.md exists" || echo "  ○ No CLAUDE.md"
[ -d ".claude" ] && echo "  ✓ .claude/ directory exists" || echo "  ○ No .claude/ directory"

# Key directories
echo ""
echo "  Project structure:"
ls -la 2>/dev/null | head -20

echo ""
echo "─────────────────────────────────────────────────────────────────"
echo "  DISCOVERY COMPLETE"
echo "─────────────────────────────────────────────────────────────────"
echo ""
echo "  Project Type: $PROJECT_TYPE"
echo "  Languages: ${LANGUAGES:-unknown}"
echo "  Frameworks: ${FRAMEWORKS:-none}"
echo ""

# Update state
cat > "$STATE_FILE" << EOF
{
  "initialized": true,
  "discovery_complete": true,
  "generation_complete": false,
  "validation_complete": false,
  "project": {
    "name": "$(basename "$PROJECT_ROOT")",
    "type": "$PROJECT_TYPE",
    "languages": [$(echo "$LANGUAGES" | tr ' ' '\n' | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')],
    "frameworks": [$(echo "$FRAMEWORKS" | tr ' ' '\n' | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')],
    "build_command": "${BUILD_CMD:-null}",
    "test_command": "${TEST_CMD:-null}",
    "lint_command": "${LINT_CMD:-null}"
  },
  "generated_files": [],
  "validation_results": [],
  "errors": []
}
EOF

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DISCOVERY COMPLETE                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Detected:"
echo "  Project: $(basename "$PROJECT_ROOT")"
echo "  Type: $PROJECT_TYPE"
echo "  Languages: ${LANGUAGES:-unknown}"
echo "  Frameworks: ${FRAMEWORKS:-none}"
echo "  Build: ${BUILD_CMD:-not detected}"
echo "  Test: ${TEST_CMD:-not detected}"
echo ""
