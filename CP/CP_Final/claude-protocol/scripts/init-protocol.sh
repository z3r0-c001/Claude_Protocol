#!/bin/bash
# Initialize Claude protocol for a project
set -e

REPO_URL="$1"
TARGET_DIR="${2:-.}"

echo "=== Claude Protocol Initialization ==="

# Clone if URL provided
if [ -n "$REPO_URL" ]; then
    echo "Cloning $REPO_URL..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# Create directories
mkdir -p .claude/{agents,skills,commands,hooks}
mkdir -p memories

# Detect project type
echo "Analyzing codebase..."

PROJECT_TYPE="unknown"
LANGUAGES=""
FRAMEWORKS=""

[ -f "package.json" ] && PROJECT_TYPE="node" && LANGUAGES="javascript"
[ -f "tsconfig.json" ] && LANGUAGES="typescript"
[ -f "pyproject.toml" ] || [ -f "requirements.txt" ] && PROJECT_TYPE="python" && LANGUAGES="python"
[ -f "Cargo.toml" ] && PROJECT_TYPE="rust" && LANGUAGES="rust"
[ -f "go.mod" ] && PROJECT_TYPE="go" && LANGUAGES="go"

# Detect frameworks
[ -f "next.config.js" ] || [ -f "next.config.ts" ] && FRAMEWORKS="nextjs"
[ -f "vite.config.ts" ] && FRAMEWORKS="vite"
grep -q "fastapi" requirements.txt 2>/dev/null && FRAMEWORKS="fastapi"
grep -q "django" requirements.txt 2>/dev/null && FRAMEWORKS="django"

# Save analysis
cat > memories/codebase-analysis.json << ANALYSIS
{
  "timestamp": "$(date -Iseconds)",
  "project_type": "$PROJECT_TYPE",
  "languages": "$LANGUAGES",
  "frameworks": "$FRAMEWORKS",
  "initialized": true
}
ANALYSIS

echo "Project type: $PROJECT_TYPE"
echo "Languages: $LANGUAGES"
echo "Frameworks: $FRAMEWORKS"

# Generate basic CLAUDE.md if not exists
if [ ! -f "CLAUDE.md" ]; then
    cat > CLAUDE.md << CLAUDE
# Project

## Quick Commands
\`\`\`bash
# Add project commands here
\`\`\`

## Code Style
Follow existing patterns in codebase.

## Testing
Run tests before committing.
CLAUDE
    echo "Created CLAUDE.md"
fi

echo ""
echo "=== Initialization Complete ==="
echo "Run /init in Claude to generate full protocol artifacts"
