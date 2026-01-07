#!/bin/bash
#
# Claude Protocol Installation Script
# ====================================
# Sets up Claude Protocol in your project directory
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           Claude Protocol Installation Script             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get the directory where this script is located (source)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in the cloned repo directory
if [ -f "$SCRIPT_DIR/CLAUDE.md" ] && [ -d "$SCRIPT_DIR/.claude" ]; then
    IN_REPO=true
else
    echo -e "${RED}Error: Cannot find Claude Protocol files in $SCRIPT_DIR${NC}"
    echo -e "Make sure you're running this script from the cloned repository."
    exit 1
fi

# Prompt for target directory
echo -e "${YELLOW}Where would you like to install Claude Protocol?${NC}"
echo ""
echo "  1) Current directory ($(pwd))"
echo "  2) Parent directory ($(dirname "$(pwd)"))"
echo "  3) Specify a different directory"
echo ""
read -p "Choice [1/2/3]: " choice

case "$choice" in
    1|"")
        TARGET_DIR="$(pwd)"
        ;;
    2)
        TARGET_DIR="$(dirname "$(pwd)")"
        ;;
    3)
        read -p "Enter target directory path: " TARGET_DIR
        # Expand ~ to home directory
        TARGET_DIR="${TARGET_DIR/#\~/$HOME}"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
    echo -e "${YELLOW}Directory '$TARGET_DIR' does not exist.${NC}"
    read -p "Create it? [y/N]: " create_dir
    if [[ "$create_dir" =~ ^[Yy]$ ]]; then
        mkdir -p "$TARGET_DIR"
        TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
        echo -e "${GREEN}Created directory: $TARGET_DIR${NC}"
    else
        echo -e "${RED}Exiting.${NC}"
        exit 1
    fi
}

# Check if source and target are the same
if [ "$SCRIPT_DIR" = "$TARGET_DIR" ]; then
    echo ""
    echo -e "${GREEN}You're already in the Claude Protocol directory!${NC}"
    echo ""
    echo -e "The protocol is ready to use. No installation needed."
    echo ""
    echo -e "To copy to another project, run:"
    echo -e "  ${BLUE}./install.sh${NC}"
    echo -e "  Then choose option 3 and specify your project path."
    echo ""
    echo -e "Or manually copy these files to your project:"
    echo -e "  ${BLUE}cp -r .claude /path/to/your/project/${NC}"
    echo -e "  ${BLUE}cp CLAUDE.md .mcp.json /path/to/your/project/${NC}"
    echo ""

    # Still verify dependencies
    echo -e "${BLUE}Checking dependencies...${NC}"

    ERRORS=0
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}  ✗ Python 3 not found (required for hooks)${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if command -v jq &> /dev/null; then
        echo -e "${GREEN}  ✓ jq installed${NC}"
    else
        echo -e "${RED}  ✗ jq not found (required for hooks)${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1)
        echo -e "${GREEN}  ✓ Node.js $NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}  ! Node.js not found (optional, for MCP server)${NC}"
    fi

    if command -v claude &> /dev/null; then
        echo -e "${GREEN}  ✓ Claude Code CLI installed${NC}"
    else
        echo -e "${YELLOW}  ! Claude Code CLI not found${NC}"
        echo -e "${YELLOW}    Install: npm install -g @anthropic-ai/claude-code${NC}"
    fi

    echo ""
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}Ready to use! Run 'claude' then '/proto-init'${NC}"
    else
        echo -e "${YELLOW}Please install missing dependencies first.${NC}"
    fi
    exit 0
fi

# Check if .claude already exists in target
MERGE_MODE=false
if [ -d "$TARGET_DIR/.claude" ] || [ -f "$TARGET_DIR/CLAUDE.md" ]; then
    echo ""
    echo -e "${YELLOW}Existing Claude configuration detected:${NC}"
    [ -d "$TARGET_DIR/.claude" ] && echo -e "  - .claude/ directory"
    [ -f "$TARGET_DIR/CLAUDE.md" ] && echo -e "  - CLAUDE.md"
    [ -f "$TARGET_DIR/.mcp.json" ] && echo -e "  - .mcp.json"
    echo ""
    echo -e "${YELLOW}How would you like to proceed?${NC}"
    echo ""
    echo "  1) Merge - Keep existing customizations, add missing protocol components"
    echo "  2) Overwrite - Replace everything with fresh protocol (backup created)"
    echo "  3) Exit - Cancel installation"
    echo ""
    read -p "Choice [1/2/3]: " merge_choice

    case "$merge_choice" in
        1)
            MERGE_MODE=true
            echo -e "${BLUE}Merge mode: Preserving existing customizations${NC}"
            ;;
        2)
            # Create backup before overwriting
            BACKUP_DIR="$TARGET_DIR/.claude-backup-$(date +%Y%m%d-%H%M%S)"
            echo -e "${BLUE}Creating backup at: $BACKUP_DIR${NC}"
            mkdir -p "$BACKUP_DIR"
            [ -d "$TARGET_DIR/.claude" ] && cp -r "$TARGET_DIR/.claude" "$BACKUP_DIR/"
            [ -f "$TARGET_DIR/CLAUDE.md" ] && cp "$TARGET_DIR/CLAUDE.md" "$BACKUP_DIR/"
            [ -f "$TARGET_DIR/.mcp.json" ] && cp "$TARGET_DIR/.mcp.json" "$BACKUP_DIR/"
            rm -rf "$TARGET_DIR/.claude"
            echo -e "${GREEN}Backup created. Proceeding with fresh install.${NC}"
            ;;
        3|*)
            echo -e "${RED}Exiting.${NC}"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${BLUE}Installing Claude Protocol to: $TARGET_DIR${NC}"
echo ""

# Copy files
if [ "$MERGE_MODE" = true ]; then
    echo -e "${GREEN}[1/6]${NC} Merging .claude directory (preserving existing)..."
    # Create .claude if it doesn't exist
    mkdir -p "$TARGET_DIR/.claude"

    # Copy subdirectories, only adding missing files
    for subdir in agents commands hooks skills scripts mcp docs; do
        if [ -d "$SCRIPT_DIR/.claude/$subdir" ]; then
            mkdir -p "$TARGET_DIR/.claude/$subdir"
            # Copy files that don't exist in target
            find "$SCRIPT_DIR/.claude/$subdir" -type f | while read src_file; do
                rel_path="${src_file#$SCRIPT_DIR/.claude/}"
                dst_file="$TARGET_DIR/.claude/$rel_path"
                if [ ! -f "$dst_file" ]; then
                    mkdir -p "$(dirname "$dst_file")"
                    cp "$src_file" "$dst_file"
                    echo -e "    ${GREEN}+ Added: $rel_path${NC}"
                fi
            done
        fi
    done

    # Copy settings.json only if it doesn't exist
    if [ ! -f "$TARGET_DIR/.claude/settings.json" ]; then
        cp "$SCRIPT_DIR/.claude/settings.json" "$TARGET_DIR/.claude/"
        echo -e "    ${GREEN}+ Added: settings.json${NC}"
    else
        echo -e "    ${YELLOW}Kept existing: settings.json${NC}"
    fi

    echo -e "${GREEN}[2/6]${NC} Merging configuration files..."

    # CLAUDE.md - analyze and merge
    if [ -f "$TARGET_DIR/CLAUDE.md" ]; then
        echo -e "    ${YELLOW}Existing CLAUDE.md detected - preserving${NC}"
        echo -e "    ${BLUE}Run /proto-init to analyze and enhance it${NC}"
    else
        cp "$SCRIPT_DIR/CLAUDE.md" "$TARGET_DIR/"
        echo -e "    ${GREEN}+ Added: CLAUDE.md${NC}"
    fi

    # .mcp.json - merge if exists
    if [ -f "$TARGET_DIR/.mcp.json" ]; then
        echo -e "    ${YELLOW}Existing .mcp.json detected - preserving${NC}"
        echo -e "    ${BLUE}Protocol servers will be added on /proto-init${NC}"
    else
        cp "$SCRIPT_DIR/.mcp.json" "$TARGET_DIR/" 2>/dev/null || true
        echo -e "    ${GREEN}+ Added: .mcp.json${NC}"
    fi

    # .gitignore - don't overwrite
    if [ ! -f "$TARGET_DIR/.gitignore" ]; then
        cp "$SCRIPT_DIR/.gitignore" "$TARGET_DIR/" 2>/dev/null || true
        echo -e "    ${GREEN}+ Added: .gitignore${NC}"
    else
        echo -e "    ${YELLOW}Kept existing: .gitignore${NC}"
    fi
else
    echo -e "${GREEN}[1/6]${NC} Copying .claude directory..."
    cp -r "$SCRIPT_DIR/.claude" "$TARGET_DIR/"

    echo -e "${GREEN}[2/6]${NC} Copying configuration files..."
    cp "$SCRIPT_DIR/CLAUDE.md" "$TARGET_DIR/"
    cp "$SCRIPT_DIR/.mcp.json" "$TARGET_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/.gitignore" "$TARGET_DIR/" 2>/dev/null || true
fi

echo -e "${GREEN}[3/6]${NC} Copying documentation..."
cp "$SCRIPT_DIR/README.md" "$TARGET_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/LICENSE" "$TARGET_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/CHANGELOG"*.md "$TARGET_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/protocol-manifest.json" "$TARGET_DIR/" 2>/dev/null || true
if [ -d "$SCRIPT_DIR/docs" ]; then
    cp -r "$SCRIPT_DIR/docs" "$TARGET_DIR/"
fi
if [ -d "$SCRIPT_DIR/scripts" ]; then
    cp -r "$SCRIPT_DIR/scripts" "$TARGET_DIR/"
fi

echo -e "${GREEN}[4/6]${NC} Copying install script..."
cp "$SCRIPT_DIR/install.sh" "$TARGET_DIR/" 2>/dev/null || true

echo -e "${GREEN}[5/6]${NC} Setting executable permissions on hooks..."
chmod +x "$TARGET_DIR/.claude/hooks/"*.sh 2>/dev/null || true
chmod +x "$TARGET_DIR/.claude/hooks/"*.py 2>/dev/null || true

echo -e "${GREEN}[6/6]${NC} Setting executable permissions on scripts..."
chmod +x "$TARGET_DIR/.claude/scripts/"*.sh 2>/dev/null || true
chmod +x "$TARGET_DIR/install.sh" 2>/dev/null || true

# Verify installation
echo ""
echo -e "${BLUE}Verifying installation...${NC}"

ERRORS=0

if [ ! -d "$TARGET_DIR/.claude" ]; then
    echo -e "${RED}  ✗ .claude directory missing${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ .claude directory${NC}"
fi

if [ ! -f "$TARGET_DIR/CLAUDE.md" ]; then
    echo -e "${RED}  ✗ CLAUDE.md missing${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ CLAUDE.md${NC}"
fi

if [ ! -f "$TARGET_DIR/.claude/settings.json" ]; then
    echo -e "${RED}  ✗ settings.json missing${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}  ✓ settings.json${NC}"
fi

HOOK_COUNT=$(ls -1 "$TARGET_DIR/.claude/hooks/"*.{sh,py} 2>/dev/null | wc -l)
if [ "$HOOK_COUNT" -lt 10 ]; then
    echo -e "${YELLOW}  ! Only $HOOK_COUNT hooks found (expected 14+)${NC}"
else
    echo -e "${GREEN}  ✓ $HOOK_COUNT hooks installed${NC}"
fi

# Check dependencies
echo ""
echo -e "${BLUE}Checking dependencies...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}  ✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}  ✗ Python 3 not found (required for hooks)${NC}"
    ERRORS=$((ERRORS + 1))
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    echo -e "${GREEN}  ✓ Node.js $NODE_VERSION${NC}"
else
    echo -e "${YELLOW}  ! Node.js not found (optional, for MCP server)${NC}"
fi

if command -v jq &> /dev/null; then
    echo -e "${GREEN}  ✓ jq installed${NC}"
else
    echo -e "${RED}  ✗ jq not found (required for hooks)${NC}"
    ERRORS=$((ERRORS + 1))
fi

if command -v claude &> /dev/null; then
    echo -e "${GREEN}  ✓ Claude Code CLI installed${NC}"
else
    echo -e "${YELLOW}  ! Claude Code CLI not found${NC}"
    echo -e "${YELLOW}    Install: npm install -g @anthropic-ai/claude-code${NC}"
fi

# Final status
echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Complete!                       ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Prompt to delete origin directory
    echo -e "${YELLOW}Delete the source directory (cloned repo)?${NC}"
    echo -e "  Source: ${BLUE}$SCRIPT_DIR${NC}"
    echo ""
    read -p "Delete source directory? [y/N]: " delete_source
    if [[ "$delete_source" =~ ^[Yy]$ ]]; then
        # Safety check: make sure we're not deleting the target
        if [ "$SCRIPT_DIR" != "$TARGET_DIR" ]; then
            echo -e "${BLUE}Removing source directory...${NC}"
            rm -rf "$SCRIPT_DIR"
            echo -e "${GREEN}✓ Source directory deleted${NC}"
        fi
        echo ""
        echo -e "${YELLOW}NOTE: Your shell is still in the deleted directory.${NC}"
        echo -e "${YELLOW}Run this command to move to your project:${NC}"
        echo ""
        echo -e "  ${BLUE}cd $TARGET_DIR && claude${NC}"
        echo ""
        echo -e "Then run ${BLUE}/proto-init${NC} to initialize for your project"
    else
        echo -e "${YELLOW}Source directory kept at: $SCRIPT_DIR${NC}"
        echo ""
        echo -e "Next steps:"
        echo -e "  1. ${BLUE}cd $TARGET_DIR${NC}"
        echo -e "  2. ${BLUE}claude${NC}"
        echo -e "  3. Run ${BLUE}/proto-init${NC} to initialize for your project"
    fi
    echo ""
else
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║     Installation completed with $ERRORS warning(s)            ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "Please resolve the warnings above before using Claude Protocol."
fi
