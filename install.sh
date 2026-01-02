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
if [ -d "$TARGET_DIR/.claude" ]; then
    echo -e "${YELLOW}Warning: $TARGET_DIR/.claude already exists.${NC}"
    read -p "Overwrite? [y/N]: " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo -e "${RED}Exiting.${NC}"
        exit 1
    fi
    rm -rf "$TARGET_DIR/.claude"
fi

echo ""
echo -e "${BLUE}Installing Claude Protocol to: $TARGET_DIR${NC}"
echo ""

# Copy files
echo -e "${GREEN}[1/6]${NC} Copying .claude directory..."
cp -r "$SCRIPT_DIR/.claude" "$TARGET_DIR/"

echo -e "${GREEN}[2/6]${NC} Copying configuration files..."
cp "$SCRIPT_DIR/CLAUDE.md" "$TARGET_DIR/"
cp "$SCRIPT_DIR/.mcp.json" "$TARGET_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/.gitignore" "$TARGET_DIR/" 2>/dev/null || true

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
            echo ""
            echo -e "${BLUE}Changing to target directory...${NC}"
            cd "$TARGET_DIR"
            echo -e "${GREEN}✓ Now in: $TARGET_DIR${NC}"
        fi
        echo ""
        echo -e "Next steps:"
        echo -e "  1. ${BLUE}claude${NC}"
        echo -e "  2. Run ${BLUE}/proto-init${NC} to initialize for your project"
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
