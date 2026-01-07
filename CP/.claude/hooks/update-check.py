#!/usr/bin/env python3
"""
SessionStart hook: Check for Claude Protocol updates
Compares local version against latest GitHub release
"""

import json
import sys
import os
import urllib.request
import urllib.error

REPO_API = "https://api.github.com/repos/z3r0-c001/Claude_Protocol/releases/latest"
REPO_URL = "https://github.com/z3r0-c001/Claude_Protocol"

def get_local_version():
    """Get version from protocol-manifest.json"""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    manifest_path = os.path.join(project_dir, "protocol-manifest.json")
    
    if not os.path.exists(manifest_path):
        return None
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
            return manifest.get("version")
    except (json.JSONDecodeError, IOError):
        return None

def get_latest_release():
    """Fetch latest release from GitHub API"""
    try:
        req = urllib.request.Request(
            REPO_API,
            headers={"User-Agent": "Claude-Protocol-Update-Check"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "")
            # Strip 'v' prefix if present
            return tag.lstrip("v") if tag else None
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None

def parse_version(v):
    """Parse version string to tuple for comparison"""
    if not v:
        return (0, 0, 0)
    try:
        parts = v.lstrip("v").split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return (0, 0, 0)

def main():
    local = get_local_version()
    latest = get_latest_release()
    
    if not local:
        # Can't determine local version, skip check
        sys.exit(0)
    
    if not latest:
        # Network issue or no releases, skip silently
        sys.exit(0)
    
    local_tuple = parse_version(local)
    latest_tuple = parse_version(latest)
    
    if latest_tuple > local_tuple:
        # Output update notice - this gets added to context on SessionStart
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  📦 Claude Protocol Update Available                         ║
║                                                              ║
║  Current: v{local}                                           ║
║  Latest:  v{latest}                                          ║
║                                                              ║
║  Run: /proto-update  or visit:                               ║
║  {REPO_URL}/releases/latest  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
