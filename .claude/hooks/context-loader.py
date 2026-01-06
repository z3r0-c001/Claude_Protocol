#!/usr/bin/env python3
"""
Context Loader Hook (UserPromptSubmit)

Loads pending violations, reminders, and checks for protocol updates.
"""
import json
import sys
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# How often to check for updates (in hours)
UPDATE_CHECK_INTERVAL_HOURS = 24

def get_project_dir():
    return Path(os.getcwd())

def load_json_file(filepath):
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except (json.JSONDecodeError, IOError):
        pass
    return None

def save_json_file(filepath, data):
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(data, indent=2))
    except (IOError, OSError):
        pass

def safe_delete(filepath):
    try:
        if filepath.exists():
            filepath.unlink()
    except (IOError, OSError):
        pass

def fetch_remote_manifest(url: str, timeout: int = 5) -> dict | None:
    """Fetch remote manifest from GitHub (with timeout)."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), url],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return None

def check_protocol_updates(claude_dir: Path) -> str | None:
    """Check for protocol updates, return notification if available."""
    cache_file = claude_dir / "memory" / "protocol-version-cache.json"
    local_manifest_file = claude_dir / "protocol-manifest.local.json"
    remote_manifest_file = claude_dir.parent / "protocol-manifest.json"

    # Load local manifest to get current version
    local_manifest = load_json_file(local_manifest_file)
    if not local_manifest:
        return None

    local_version = local_manifest.get("installed_version", "unknown")

    # Check cache
    cache = load_json_file(cache_file)
    now = datetime.now()

    # Determine if we need to fetch from remote
    should_fetch = False
    if not cache:
        should_fetch = True
    else:
        last_check = cache.get("last_check")
        if last_check:
            try:
                last_check_dt = datetime.fromisoformat(last_check)
                if now - last_check_dt > timedelta(hours=UPDATE_CHECK_INTERVAL_HOURS):
                    should_fetch = True
            except ValueError:
                should_fetch = True
        else:
            should_fetch = True

    remote_version = None
    updates_available = 0

    if should_fetch:
        # Try to get repository URL from local manifest
        source_url = local_manifest.get("source", {}).get("url", "")
        if source_url:
            # Convert GitHub URL to raw content URL
            # https://github.com/user/repo -> https://raw.githubusercontent.com/user/repo/main
            raw_url = source_url.replace("github.com", "raw.githubusercontent.com")
            manifest_url = f"{raw_url}/main/protocol-manifest.json"

            remote_manifest = fetch_remote_manifest(manifest_url)
            if remote_manifest:
                remote_version = remote_manifest.get("protocol", {}).get("version")

                # Count available updates by comparing components
                local_components = local_manifest.get("components", {})
                for category, components in remote_manifest.get("components", {}).items():
                    for comp_name, comp_data in components.items():
                        local_comp = local_components.get(f"{category}/{comp_name}", {})
                        if local_comp.get("version") != comp_data.get("version"):
                            updates_available += 1

                # Update cache
                cache = {
                    "last_check": now.isoformat(),
                    "remote_version": remote_version,
                    "updates_available": updates_available,
                    "local_version": local_version
                }
                save_json_file(cache_file, cache)
    else:
        # Use cached data
        remote_version = cache.get("remote_version")
        updates_available = cache.get("updates_available", 0)

    # Generate notification if updates are available
    if remote_version and (remote_version != local_version or updates_available > 0):
        if updates_available > 0:
            return (
                f"PROTOCOL UPDATES AVAILABLE: {local_version} → {remote_version} "
                f"({updates_available} components)\n"
                f"  Run /proto-update to review and apply updates."
            )
        elif remote_version != local_version:
            return (
                f"PROTOCOL UPDATE: {local_version} → {remote_version}\n"
                f"  Run /proto-update to review and apply."
            )

    return None

def main():
    # Read and discard stdin
    try:
        sys.stdin.read()
    except Exception:
        pass

    project_dir = get_project_dir()
    claude_dir = project_dir / ".claude"
    context_parts = []

    # Check for protocol updates (non-blocking, cached)
    try:
        update_notification = check_protocol_updates(claude_dir)
        if update_notification:
            context_parts.append(update_notification)
    except Exception:
        pass  # Don't block on update check errors

    # Load pending violations
    violations_file = claude_dir / "memory" / "pending-violations.json"
    violations = load_json_file(violations_file)
    if violations and violations.get("violations"):
        context_parts.append(
            "PENDING VIOLATIONS:\n" +
            "\n".join(f"  - {v}" for v in violations["violations"])
        )
        safe_delete(violations_file)

    # Load reminders
    reminders_file = claude_dir / "memory" / "reminders.json"
    reminders = load_json_file(reminders_file)
    if reminders and reminders.get("active"):
        context_parts.append(
            "REMINDERS:\n" +
            "\n".join(f"  - {r}" for r in reminders["active"])
        )

    # Output context if any
    if context_parts:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n---\n".join(context_parts)
            }
        }
        print(json.dumps(output))

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
