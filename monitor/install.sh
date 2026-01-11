#!/bin/bash
#
# install.sh - Install Claude Protocol Monitor
#
# This script:
#   1. Installs npm dependencies for server
#   2. Optionally installs Electron for native window
#   3. Creates symlink for claude-monitor command
#   4. Sets up log directories
#   5. Generates app icons (if tools available)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.claude-monitor"
BIN_DIR="${HOME}/.local/bin"
CLAUDE_DIR="${HOME}/.claude"
ELECTRON_DIR="${SCRIPT_DIR}/electron"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║       Claude Protocol Monitor - Installation          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗${NC} Node.js is required but not installed."
    echo "  Install from: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo -e "${RED}✗${NC} Node.js 16+ required. Found: $(node -v)"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node -v) found"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗${NC} npm is required but not installed."
    exit 1
fi
echo -e "${GREEN}✓${NC} npm $(npm -v) found"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}!${NC} Python 3 not found. Monitor agent will not work."
else
    echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2) found"
fi

# Create directories
echo -e "${BLUE}▶${NC} Creating directories..."
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${CLAUDE_DIR}/logs"
mkdir -p "${CLAUDE_DIR}/pids"
mkdir -p "${CLAUDE_DIR}/hooks"

# Copy monitor files
echo -e "${BLUE}▶${NC} Installing monitor files..."
cp -r "${SCRIPT_DIR}/web" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/server" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/hooks" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/electron" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/package.json" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/monitor-agent.py" "${INSTALL_DIR}/"
cp "${SCRIPT_DIR}/enforcement-rules.json" "${INSTALL_DIR}/"

# Install server npm dependencies
echo -e "${BLUE}▶${NC} Installing server dependencies..."
cd "${INSTALL_DIR}"
npm install --silent

# Ask about Electron
echo ""
echo -e "${YELLOW}?${NC} Install Electron for native window? (recommended)"
echo "  This provides a standalone app window instead of browser."
read -p "  Install Electron? [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}▶${NC} Installing Electron dependencies..."
    cd "${INSTALL_DIR}/electron"
    npm install --silent
    echo -e "${GREEN}✓${NC} Electron installed"
    
    # Generate icons if tools available
    if command -v rsvg-convert &> /dev/null || command -v convert &> /dev/null; then
        echo -e "${BLUE}▶${NC} Generating app icons..."
        chmod +x "${INSTALL_DIR}/electron/icons/generate-icons.sh"
        "${INSTALL_DIR}/electron/icons/generate-icons.sh" 2>/dev/null || true
    else
        echo -e "${YELLOW}!${NC} Icon generation skipped (install librsvg or ImageMagick)"
    fi
else
    echo -e "${YELLOW}!${NC} Skipping Electron (will use browser)"
fi

# Create launcher symlink
echo -e "${BLUE}▶${NC} Creating claude-monitor command..."
cp "${SCRIPT_DIR}/claude-monitor" "${INSTALL_DIR}/claude-monitor"
chmod +x "${INSTALL_DIR}/claude-monitor"
ln -sf "${INSTALL_DIR}/claude-monitor" "${BIN_DIR}/claude-monitor"

# Copy log-emitter hook to .claude/hooks
echo -e "${BLUE}▶${NC} Installing hooks..."
cp "${SCRIPT_DIR}/hooks/log-emitter.py" "${CLAUDE_DIR}/hooks/"
chmod +x "${CLAUDE_DIR}/hooks/log-emitter.py"

# Check if BIN_DIR is in PATH
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    echo ""
    echo -e "${YELLOW}!${NC} Add ${BIN_DIR} to your PATH:"
    echo ""
    echo "    export PATH=\"\$PATH:${BIN_DIR}\""
    echo ""
    echo "  Add this line to your ~/.bashrc or ~/.zshrc"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Installation Complete!                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Usage:"
echo "  ${BLUE}claude-monitor${NC}                Start with monitoring"
echo "  ${BLUE}claude-monitor stop${NC}           Stop all services"
echo "  ${BLUE}claude-monitor status${NC}         Check status"
echo "  ${BLUE}claude-monitor browser${NC}        Open in browser (not Electron)"
echo "  ${BLUE}claude-monitor build${NC}          Build standalone app"
echo ""
echo "Dashboard URL: http://localhost:3847"
echo ""
if [ -d "${INSTALL_DIR}/electron/node_modules/electron" ]; then
    echo -e "Mode: ${GREEN}Electron (native window)${NC}"
else
    echo -e "Mode: ${YELLOW}Browser (fallback)${NC}"
fi
echo ""
