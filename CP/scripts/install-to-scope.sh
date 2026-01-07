#!/bin/bash
# install-to-scope.sh - Install Claude Protocol to specified scope
# Usage: bash install-to-scope.sh <scope> [source_dir]
#   scope: global | project | hybrid
#   source_dir: Optional path to protocol source (defaults to script's parent dir)

set -e

SCOPE="${1:-project}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${2:-$(dirname "$SCRIPT_DIR")}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verify source exists
if [ ! -d "$SOURCE_DIR/.claude" ]; then
    log_error "Source .claude directory not found at: $SOURCE_DIR/.claude"
    exit 1
fi

install_to_target() {
    local target="$1"
    local scope_name="$2"

    log_info "Installing to $target ($scope_name scope)..."

    # Create directory structure
    mkdir -p "$target"/{hooks,agents/core,agents/quality,agents/domain,agents/workflow}
    mkdir -p "$target"/{skills,commands,scripts,memory,mcp/memory-server}

    # Copy hooks
    if [ -d "$SOURCE_DIR/.claude/hooks" ]; then
        cp -r "$SOURCE_DIR/.claude/hooks/"* "$target/hooks/" 2>/dev/null || true
        chmod +x "$target/hooks/"*.sh 2>/dev/null || true
        chmod +x "$target/hooks/"*.py 2>/dev/null || true
        log_info "  Copied hooks"
    fi

    # Copy agents
    if [ -d "$SOURCE_DIR/.claude/agents" ]; then
        cp -r "$SOURCE_DIR/.claude/agents/"* "$target/agents/" 2>/dev/null || true
        log_info "  Copied agents"
    fi

    # Copy skills
    if [ -d "$SOURCE_DIR/.claude/skills" ]; then
        cp -r "$SOURCE_DIR/.claude/skills/"* "$target/skills/" 2>/dev/null || true
        log_info "  Copied skills"
    fi

    # Copy commands
    if [ -d "$SOURCE_DIR/.claude/commands" ]; then
        cp -r "$SOURCE_DIR/.claude/commands/"* "$target/commands/" 2>/dev/null || true
        log_info "  Copied commands"
    fi

    # Copy settings.json
    if [ -f "$SOURCE_DIR/.claude/settings.json" ]; then
        cp "$SOURCE_DIR/.claude/settings.json" "$target/settings.json"
        log_info "  Copied settings.json"
    fi

    # Copy MCP server if exists
    if [ -d "$SOURCE_DIR/.claude/mcp/memory-server" ]; then
        cp -r "$SOURCE_DIR/.claude/mcp/memory-server/"* "$target/mcp/memory-server/" 2>/dev/null || true
        log_info "  Copied MCP memory server"
    fi
}

install_core_only() {
    local target="$1"

    log_info "Installing core quality hooks to $target..."

    mkdir -p "$target/hooks"

    # Core quality hooks only
    local core_hooks=(
        "run-hook.sh"
        "laziness-check.sh"
        "honesty-check.sh"
        "stop-verify.sh"
        "pretool-laziness-check.py"
        "pretool-hallucination-check.py"
    )

    for hook in "${core_hooks[@]}"; do
        if [ -f "$SOURCE_DIR/.claude/hooks/$hook" ]; then
            cp "$SOURCE_DIR/.claude/hooks/$hook" "$target/hooks/"
            chmod +x "$target/hooks/$hook" 2>/dev/null || true
        fi
    done

    log_info "  Copied core hooks: ${core_hooks[*]}"
}

case "$SCOPE" in
    global)
        TARGET="$HOME/.claude"
        install_to_target "$TARGET" "global"

        # Copy root-level files
        if [ -f "$SOURCE_DIR/.mcp.json" ]; then
            cp "$SOURCE_DIR/.mcp.json" "$HOME/.mcp.json"
            log_info "Copied .mcp.json to home directory"
        fi

        log_info "Installation complete!"
        log_info "Protocol is now available in ALL projects."
        log_info "Run 'claude' in any project directory to use."
        ;;

    project)
        TARGET="${CLAUDE_PROJECT_DIR:-.}/.claude"
        install_to_target "$TARGET" "project"

        # Copy root-level files to project
        if [ -f "$SOURCE_DIR/.mcp.json" ]; then
            cp "$SOURCE_DIR/.mcp.json" "${CLAUDE_PROJECT_DIR:-.}/.mcp.json"
            log_info "Copied .mcp.json to project root"
        fi
        if [ -f "$SOURCE_DIR/CLAUDE.md" ]; then
            cp "$SOURCE_DIR/CLAUDE.md" "${CLAUDE_PROJECT_DIR:-.}/CLAUDE.md"
            log_info "Copied CLAUDE.md to project root"
        fi

        log_info "Installation complete!"
        log_info "Protocol is now available in THIS project only."
        log_info "Run 'claude' in this directory to use."
        ;;

    hybrid)
        # Core to global
        install_core_only "$HOME/.claude"

        # Everything to project
        PROJECT_TARGET="${CLAUDE_PROJECT_DIR:-.}/.claude"
        install_to_target "$PROJECT_TARGET" "project"

        # Copy root-level files to project
        if [ -f "$SOURCE_DIR/.mcp.json" ]; then
            cp "$SOURCE_DIR/.mcp.json" "${CLAUDE_PROJECT_DIR:-.}/.mcp.json"
        fi
        if [ -f "$SOURCE_DIR/CLAUDE.md" ]; then
            cp "$SOURCE_DIR/CLAUDE.md" "${CLAUDE_PROJECT_DIR:-.}/CLAUDE.md"
        fi

        log_info "Hybrid installation complete!"
        log_info "Core quality hooks installed to ~/.claude/ (all projects)"
        log_info "Full protocol installed to ./.claude/ (this project)"
        log_info "Project hooks take precedence over global."
        ;;

    *)
        log_error "Unknown scope: $SCOPE"
        echo ""
        echo "Usage: bash install-to-scope.sh <scope> [source_dir]"
        echo ""
        echo "Scopes:"
        echo "  global  - Install to ~/.claude/ (available in all projects)"
        echo "  project - Install to ./.claude/ (this project only)"
        echo "  hybrid  - Core hooks global, full protocol local"
        echo ""
        exit 1
        ;;
esac

echo ""
log_info "Next steps:"
echo "  1. Restart Claude Code to load the protocol"
echo "  2. Run /proto-init to complete setup"
echo "  3. Use /proto-status to verify installation"
