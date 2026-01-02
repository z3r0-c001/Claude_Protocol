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
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

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

def get_local_manifest(project_dir: Path) -> tuple[dict | None, str]:
    """
    Get local manifest data. Returns (manifest_data, version).
    Tries protocol-manifest.local.json first, then protocol-manifest.json.
    """
    claude_dir = project_dir / ".claude"

    # Try local manifest first (tracks installation state)
    local_manifest_file = claude_dir / "protocol-manifest.local.json"
    local_manifest = load_json_file(local_manifest_file)
    if local_manifest:
        # Local manifest format
        version = local_manifest.get("installed_version",
                  local_manifest.get("protocol", {}).get("version", "unknown"))
        return local_manifest, version

    # Fall back to main manifest
    main_manifest_file = project_dir / "protocol-manifest.json"
    main_manifest = load_json_file(main_manifest_file)
    if main_manifest:
        version = main_manifest.get("protocol", {}).get("version", "unknown")
        return main_manifest, version

    return None, "unknown"

def get_repo_url(manifest: dict) -> str | None:
    """Extract repository URL from manifest (handles both formats)."""
    # New format: repository.raw_base or repository.url
    repo = manifest.get("repository", {})
    if repo.get("raw_base"):
        return repo["raw_base"]
    if repo.get("url"):
        url = repo["url"]
        # Convert GitHub URL to raw content URL
        return url.replace("github.com", "raw.githubusercontent.com")

    # Old format: source.url
    source = manifest.get("source", {})
    if source.get("url"):
        url = source["url"]
        return url.replace("github.com", "raw.githubusercontent.com")

    return None

def count_component_updates(local_manifest: dict, remote_manifest: dict) -> int:
    """Count number of components with version differences."""
    updates = 0

    remote_components = remote_manifest.get("components", {})
    local_components = local_manifest.get("components", {})

    for category, components in remote_components.items():
        if isinstance(components, dict):
            local_category = local_components.get(category, {})
            for comp_name, comp_data in components.items():
                if isinstance(comp_data, dict):
                    remote_version = comp_data.get("version", "0")

                    # Handle nested structure
                    if isinstance(local_category, dict):
                        local_comp = local_category.get(comp_name, {})
                        local_version = local_comp.get("version", "0") if isinstance(local_comp, dict) else "0"
                    else:
                        local_version = "0"

                    if remote_version != local_version:
                        updates += 1

    return updates

def check_protocol_updates(project_dir: Path) -> str | None:
    """Check for protocol updates, return notification if available."""
    claude_dir = project_dir / ".claude"
    cache_file = claude_dir / "memory" / "protocol-version-cache.json"

    # Get local manifest and version
    local_manifest, local_version = get_local_manifest(project_dir)
    if not local_manifest or local_version == "unknown":
        return None

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
        # Get repository URL from manifest
        raw_base = get_repo_url(local_manifest)
        if raw_base:
            manifest_url = f"{raw_base}/main/protocol-manifest.json"

            remote_manifest = fetch_remote_manifest(manifest_url)
            if remote_manifest:
                remote_version = remote_manifest.get("protocol", {}).get("version")

                # Count available updates
                updates_available = count_component_updates(local_manifest, remote_manifest)

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
        update_notification = check_protocol_updates(project_dir)
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
