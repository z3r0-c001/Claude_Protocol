#!/usr/bin/env python3
"""
monitor-startup.py - Auto-launch monitor on Claude startup (SessionStart)

Automatically starts the monitor server and optionally opens the dashboard
when Claude Code is invoked in a protocol-enabled directory.

Behavior:
1. Check if monitor server is already running on localhost:3847
2. If not running, check if dependencies are installed
3. Install npm dependencies if needed (first-time setup)
4. Start server in background
5. Report status to user via stderr
"""

import json
import os
import sys
import subprocess
import socket
import time
from pathlib import Path

# Configuration
MONITOR_PORT = int(os.environ.get('CLAUDE_MONITOR_PORT', 3847))
MONITOR_HOST = '127.0.0.1'
AUTO_OPEN_DASHBOARD = os.environ.get('CLAUDE_MONITOR_AUTO_OPEN', '0') == '1'
MONITOR_ENABLED = os.environ.get('CLAUDE_MONITOR_ENABLED', '1') == '1'

# Colors for terminal output
class Colors:
    PURPLE = '\033[0;35m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'
    BOLD = '\033[1m'


def log(msg: str, color: str = Colors.NC):
    """Print to stderr so user sees it."""
    sys.stderr.write(f"{color}{msg}{Colors.NC}\n")


def is_server_running() -> bool:
    """Check if monitor server is already running."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((MONITOR_HOST, MONITOR_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


def find_monitor_dir() -> Path | None:
    """Find the monitor directory in the project."""
    project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))

    # Check common locations
    candidates = [
        project_dir / 'monitor',
        project_dir / '.claude' / 'monitor',
        Path.home() / '.claude-monitor',
    ]

    for candidate in candidates:
        if (candidate / 'server' / 'index.js').exists():
            return candidate
        if (candidate / 'package.json').exists():
            return candidate

    return None


def check_npm_installed(monitor_dir: Path) -> bool:
    """Check if npm dependencies are installed."""
    node_modules = monitor_dir / 'node_modules'
    return node_modules.exists() and (node_modules / 'express').exists()


def install_npm_deps(monitor_dir: Path) -> bool:
    """Install npm dependencies."""
    log("  Installing monitor dependencies (first-time setup)...", Colors.YELLOW)
    try:
        result = subprocess.run(
            ['npm', 'install', '--silent'],
            cwd=monitor_dir,
            capture_output=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception as e:
        log(f"  Failed to install dependencies: {e}", Colors.RED)
        return False


def start_server(monitor_dir: Path) -> bool:
    """Start the monitor server in background."""
    server_path = monitor_dir / 'server' / 'index.js'

    if not server_path.exists():
        log(f"  Server not found at {server_path}", Colors.RED)
        return False

    try:
        # Start server as detached background process
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'monitor-server.log'

        with open(log_file, 'a') as f:
            subprocess.Popen(
                ['node', str(server_path)],
                cwd=monitor_dir,
                stdout=f,
                stderr=f,
                start_new_session=True
            )

        # Wait briefly for server to start
        for _ in range(5):
            time.sleep(0.5)
            if is_server_running():
                return True

        return is_server_running()
    except Exception as e:
        log(f"  Failed to start server: {e}", Colors.RED)
        return False


def open_dashboard(monitor_dir: Path):
    """Open the dashboard in browser."""
    dashboard_path = monitor_dir / 'web' / 'index.html'

    if not dashboard_path.exists():
        return

    try:
        # Try xdg-open on Linux, open on Mac
        if sys.platform == 'darwin':
            subprocess.Popen(['open', str(dashboard_path)])
        else:
            subprocess.Popen(['xdg-open', str(dashboard_path)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except Exception:
        pass


def main():
    # Skip if monitor is disabled
    if not MONITOR_ENABLED:
        sys.exit(0)

    # Read input (SessionStart provides session info)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}

    # Check if server is already running
    if is_server_running():
        log(f"{Colors.GRAY}[monitor] Server running on {MONITOR_HOST}:{MONITOR_PORT}{Colors.NC}")
        sys.exit(0)

    # Find monitor directory
    monitor_dir = find_monitor_dir()

    if not monitor_dir:
        # Monitor not installed in this project - silently skip
        sys.exit(0)

    log(f"{Colors.PURPLE}{Colors.BOLD}[monitor]{Colors.NC} Starting Claude Monitor...", Colors.PURPLE)

    # Check/install dependencies
    if not check_npm_installed(monitor_dir):
        if not install_npm_deps(monitor_dir):
            log("  Skipping monitor (dependency install failed)", Colors.YELLOW)
            sys.exit(0)

    # Start server
    if start_server(monitor_dir):
        log(f"  {Colors.GREEN}Server started on http://{MONITOR_HOST}:{MONITOR_PORT}{Colors.NC}")
        log(f"  {Colors.GRAY}Dashboard: {monitor_dir}/web/index.html{Colors.NC}")

        # Optionally open dashboard
        if AUTO_OPEN_DASHBOARD:
            open_dashboard(monitor_dir)
    else:
        log(f"  {Colors.YELLOW}Could not start monitor server{Colors.NC}")

    sys.exit(0)


if __name__ == '__main__':
    main()
