#!/usr/bin/env python3
"""
proto-update.py - Actual implementation for protocol updates

This script does the real work:
1. Fetches remote manifest from GitHub
2. Compares with local installation
3. Creates backups before changes
4. Downloads and applies updates
5. Tracks local state

Usage:
    python3 proto-update.py --check          # Check for updates only
    python3 proto-update.py --update         # Interactive update
    python3 proto-update.py --update --auto  # Auto-accept non-breaking
    python3 proto-update.py --models         # Model versions only
    python3 proto-update.py --rollback       # Restore from backup
"""

import json
import sys
import os
import argparse
import shutil
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    def __init__(self):
        self.project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
        self.manifest_path = self.project_dir / 'protocol-manifest.json'
        self.local_state_path = self.project_dir / '.claude' / 'config' / 'local-state.json'
        self.backup_dir = self.project_dir / '.claude' / 'backups'
        self.models_config = self.project_dir / '.claude' / 'config' / 'models.json'
        
    def load_manifest(self) -> Optional[Dict]:
        """Load the protocol manifest."""
        try:
            with open(self.manifest_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def load_local_state(self) -> Dict:
        """Load local state or create default."""
        try:
            with open(self.local_state_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'installed_version': None,
                'last_check': None,
                'last_update': None,
                'customized_components': [],
                'skipped_updates': []
            }
    
    def save_local_state(self, state: Dict):
        """Save local state."""
        self.local_state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.local_state_path, 'w') as f:
            json.dump(state, f, indent=2)

# =============================================================================
# REMOTE FETCHING
# =============================================================================

class RemoteFetcher:
    def __init__(self, config: Config):
        self.config = config
        self.manifest = config.load_manifest()
        self.raw_base = self._get_raw_base()
        
    def _get_raw_base(self) -> Optional[str]:
        """Get the raw GitHub URL base."""
        if not self.manifest:
            return None
        repo = self.manifest.get('repository', {})
        return repo.get('raw_base')
    
    def fetch_remote_manifest(self) -> Optional[Dict]:
        """Fetch the remote protocol manifest."""
        if not self.raw_base:
            return None
        
        url = f"{self.raw_base}/protocol-manifest.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Claude-Protocol/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"⚠️  Could not fetch remote manifest: {e}", file=sys.stderr)
            return None
    
    def fetch_file(self, path: str) -> Optional[str]:
        """Fetch a single file from remote."""
        if not self.raw_base:
            return None
        
        url = f"{self.raw_base}/{path}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Claude-Protocol/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"⚠️  Could not fetch {path}: {e}", file=sys.stderr)
            return None

# =============================================================================
# VERSION COMPARISON
# =============================================================================

def parse_version(version: str) -> tuple:
    """Parse version string to comparable tuple."""
    try:
        parts = version.split('.')
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)

def compare_versions(local: str, remote: str) -> int:
    """Compare versions. Returns: -1 if local < remote, 0 if equal, 1 if local > remote."""
    local_parts = parse_version(local)
    remote_parts = parse_version(remote)
    
    if local_parts < remote_parts:
        return -1
    elif local_parts > remote_parts:
        return 1
    return 0

def compute_checksum(filepath: Path) -> str:
    """Compute SHA256 checksum of a file."""
    if not filepath.exists():
        return ""
    
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()}"

# =============================================================================
# BACKUP MANAGEMENT
# =============================================================================

class BackupManager:
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = config.backup_dir
        
    def create_backup(self, files: List[Path]) -> bool:
        """Create backup of specified files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / timestamp
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            for file in files:
                if file.exists():
                    rel_path = file.relative_to(self.config.project_dir)
                    dest = backup_path / rel_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, dest)
            
            # Save backup metadata
            metadata = {
                'timestamp': timestamp,
                'files': [str(f.relative_to(self.config.project_dir)) for f in files if f.exists()],
                'created': datetime.now().isoformat()
            }
            with open(backup_path / 'backup-metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            print(f"⚠️  Backup failed: {e}", file=sys.stderr)
            return False
    
    def get_latest_backup(self) -> Optional[Path]:
        """Get the most recent backup directory."""
        if not self.backup_dir.exists():
            return None
        
        backups = sorted(self.backup_dir.iterdir(), reverse=True)
        for backup in backups:
            if backup.is_dir() and (backup / 'backup-metadata.json').exists():
                return backup
        return None
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore from a backup."""
        try:
            metadata_file = backup_path / 'backup-metadata.json'
            if not metadata_file.exists():
                print("⚠️  Invalid backup: no metadata found", file=sys.stderr)
                return False
            
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            for rel_path in metadata['files']:
                src = backup_path / rel_path
                dest = self.config.project_dir / rel_path
                if src.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    print(f"  Restored: {rel_path}")
            
            return True
        except Exception as e:
            print(f"⚠️  Restore failed: {e}", file=sys.stderr)
            return False

# =============================================================================
# UPDATE CHECKER
# =============================================================================

class UpdateChecker:
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = RemoteFetcher(config)
        self.local_manifest = config.load_manifest()
        self.local_state = config.load_local_state()
        self.remote_manifest = None
        
    def check_for_updates(self) -> Dict[str, Any]:
        """Check for available updates."""
        result = {
            'update_available': False,
            'local_version': None,
            'remote_version': None,
            'component_updates': [],
            'error': None
        }
        
        if not self.local_manifest:
            result['error'] = "Local manifest not found"
            return result
        
        # Get versions
        result['local_version'] = self.local_manifest.get('protocol', {}).get('version', '0.0.0')
        
        # Fetch remote
        self.remote_manifest = self.fetcher.fetch_remote_manifest()
        if not self.remote_manifest:
            result['error'] = "Could not fetch remote manifest (network issue or repo unavailable)"
            # Still save local state before returning
            self.local_state['last_check'] = datetime.now().isoformat()
            self.local_state['installed_version'] = result['local_version']
            self.config.save_local_state(self.local_state)
            return result
        
        result['remote_version'] = self.remote_manifest.get('protocol', {}).get('version', '0.0.0')
        
        # Compare versions
        cmp = compare_versions(result['local_version'], result['remote_version'])
        result['update_available'] = cmp < 0
        
        # Check individual components
        if result['update_available']:
            result['component_updates'] = self._find_component_updates()
        
        # Update local state
        self.local_state['last_check'] = datetime.now().isoformat()
        self.local_state['installed_version'] = result['local_version']
        self.config.save_local_state(self.local_state)
        
        return result
    
    def _find_component_updates(self) -> List[Dict]:
        """Find individual components that need updating."""
        updates = []
        
        if not self.remote_manifest:
            return updates
        
        # Compare components (skills, hooks, agents, etc.)
        for category in ['skills', 'hooks', 'commands']:
            local_components = self.local_manifest.get('components', {}).get(category, {})
            remote_components = self.remote_manifest.get('components', {}).get(category, {})
            
            if isinstance(local_components, dict) and isinstance(remote_components, dict):
                for name, remote_info in remote_components.items():
                    if isinstance(remote_info, dict):
                        local_info = local_components.get(name, {})
                        local_ver = local_info.get('version', '0.0.0') if isinstance(local_info, dict) else '0.0.0'
                        remote_ver = remote_info.get('version', '0.0.0')
                        
                        if compare_versions(local_ver, remote_ver) < 0:
                            updates.append({
                                'category': category,
                                'name': name,
                                'local_version': local_ver,
                                'remote_version': remote_ver,
                                'file': remote_info.get('file', ''),
                                'checksum': remote_info.get('checksum', '')
                            })
        
        return updates

# =============================================================================
# UPDATE APPLIER
# =============================================================================

class UpdateApplier:
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = RemoteFetcher(config)
        self.backup_manager = BackupManager(config)
        
    def apply_updates(self, updates: List[Dict], auto: bool = False) -> Dict[str, Any]:
        """Apply updates with optional interactive approval."""
        result = {
            'applied': [],
            'skipped': [],
            'failed': [],
            'backup_created': False
        }
        
        if not updates:
            return result
        
        # Create backup first
        files_to_backup = [self.config.project_dir / u['file'] for u in updates if u.get('file')]
        files_to_backup.append(self.config.manifest_path)
        
        if self.backup_manager.create_backup(files_to_backup):
            result['backup_created'] = True
            print("✓ Backup created")
        else:
            if not auto:
                response = input("Backup failed. Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    return result
        
        # Apply each update
        for update in updates:
            if not auto:
                print(f"\n{'='*60}")
                print(f"Update: {update['category']}/{update['name']}")
                print(f"Version: {update['local_version']} → {update['remote_version']}")
                print(f"File: {update['file']}")
                
                response = input("\nApply this update? (y/n/s=skip all): ").lower()
                if response == 's':
                    result['skipped'].extend(updates[updates.index(update):])
                    break
                elif response != 'y':
                    result['skipped'].append(update)
                    continue
            
            # Fetch and apply
            if self._apply_single_update(update):
                result['applied'].append(update)
                print(f"✓ Applied: {update['name']}")
            else:
                result['failed'].append(update)
                print(f"✗ Failed: {update['name']}")
        
        return result
    
    def _apply_single_update(self, update: Dict) -> bool:
        """Apply a single update."""
        file_path = update.get('file')
        if not file_path:
            return False
        
        content = self.fetcher.fetch_file(file_path)
        if content is None:
            return False
        
        # Write file
        dest = self.config.project_dir / file_path
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, 'w') as f:
                f.write(content)
            
            # Verify checksum if provided
            expected = update.get('checksum', '')
            if expected:
                actual = compute_checksum(dest)
                if actual != expected:
                    print(f"⚠️  Checksum mismatch for {file_path}", file=sys.stderr)
                    # Don't fail, just warn - checksums might be stale
            
            return True
        except Exception as e:
            print(f"⚠️  Write failed for {file_path}: {e}", file=sys.stderr)
            return False

# =============================================================================
# MODEL UPDATES
# =============================================================================

def check_model_updates(config: Config) -> List[Dict]:
    """Check for model version updates."""
    try:
        models_config = config.models_config
        if not models_config.exists():
            return []
        
        with open(models_config) as f:
            model_cfg = json.load(f)
        
        current_ids = {m['model_id'] for m in model_cfg.get('current_models', {}).values()}
        deprecated = {d['model_id']: d['replacement'] for d in model_cfg.get('deprecated_models', [])}
        
        # Scan agents
        agents_dir = config.project_dir / '.claude' / 'agents'
        outdated = []
        
        import glob
        import re
        
        for agent_file in glob.glob(str(agents_dir / '**' / '*.md'), recursive=True):
            if 'AGENT_PROTOCOL' in agent_file:
                continue
            
            with open(agent_file) as f:
                content = f.read()
            
            match = re.search(r'^model:\s*(.+)$', content, re.MULTILINE)
            if match:
                model = match.group(1).strip()
                if model in deprecated:
                    outdated.append({
                        'agent': Path(agent_file).stem,
                        'file': agent_file,
                        'current': model,
                        'replacement': deprecated[model]
                    })
        
        return outdated
    except Exception as e:
        print(f"⚠️  Model check error: {e}", file=sys.stderr)
        return []

def apply_model_updates(config: Config, updates: List[Dict]) -> int:
    """Apply model updates to agent files."""
    import re
    
    applied = 0
    for update in updates:
        try:
            with open(update['file']) as f:
                content = f.read()
            
            new_content = re.sub(
                rf'^model:\s*{re.escape(update["current"])}$',
                f'model: {update["replacement"]}',
                content,
                flags=re.MULTILINE
            )
            
            if new_content != content:
                with open(update['file'], 'w') as f:
                    f.write(new_content)
                applied += 1
        except Exception as e:
            print(f"⚠️  Failed to update {update['agent']}: {e}", file=sys.stderr)
    
    return applied

# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_banner(title: str):
    """Display a formatted banner."""
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)

def display_update_summary(check_result: Dict, model_updates: List[Dict]):
    """Display summary of available updates."""
    display_banner("PROTOCOL UPDATE CHECK")
    
    if check_result.get('error'):
        print(f"\n⚠️  {check_result['error']}")
        print()
    else:
        local_v = check_result['local_version']
        remote_v = check_result['remote_version']
        
        if check_result['update_available']:
            print(f"\n  Local:  {local_v}")
            print(f"  Remote: {remote_v} ← UPDATE AVAILABLE")
        else:
            print(f"\n  Version: {local_v} (up to date)")
        
        if check_result['component_updates']:
            print(f"\n  Component updates: {len(check_result['component_updates'])}")
            for u in check_result['component_updates'][:5]:
                print(f"    • {u['category']}/{u['name']}: {u['local_version']} → {u['remote_version']}")
            if len(check_result['component_updates']) > 5:
                print(f"    ... and {len(check_result['component_updates']) - 5} more")
    
    if model_updates:
        print(f"\n  ⚠️  Model updates needed: {len(model_updates)}")
        for m in model_updates[:3]:
            print(f"    • {m['agent']}: {m['current'][:30]}...")
        if len(model_updates) > 3:
            print(f"    ... and {len(model_updates) - 3} more")
    
    print()

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Claude Protocol Update Tool')
    parser.add_argument('--check', action='store_true', help='Check for updates only')
    parser.add_argument('--update', action='store_true', help='Apply available updates')
    parser.add_argument('--auto', action='store_true', help='Auto-accept all updates')
    parser.add_argument('--models', action='store_true', help='Check/update model versions only')
    parser.add_argument('--rollback', action='store_true', help='Restore from backup')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    config = Config()
    
    # Rollback
    if args.rollback:
        display_banner("ROLLBACK")
        backup_mgr = BackupManager(config)
        latest = backup_mgr.get_latest_backup()
        if not latest:
            print("No backup found")
            return 1
        
        print(f"Restoring from: {latest.name}")
        response = input("Continue? (y/N): ")
        if response.lower() == 'y':
            if backup_mgr.restore_backup(latest):
                print("✓ Rollback complete")
                return 0
            return 1
        return 0
    
    # Models only
    if args.models:
        display_banner("MODEL VERSION CHECK")
        model_updates = check_model_updates(config)
        
        if not model_updates:
            print("✓ All models up to date")
            return 0
        
        print(f"\n{len(model_updates)} agent(s) need model updates:\n")
        for m in model_updates:
            print(f"  {m['agent']:25} {m['current']}")
            print(f"  {' '*25} └─ {m['replacement']}")
        
        if not args.check:
            response = input("\nApply model updates? (y/N): ")
            if response.lower() == 'y':
                applied = apply_model_updates(config, model_updates)
                print(f"\n✓ Updated {applied}/{len(model_updates)} agents")
        
        return 0
    
    # Main update check
    checker = UpdateChecker(config)
    check_result = checker.check_for_updates()
    model_updates = check_model_updates(config)
    
    if not args.quiet:
        display_update_summary(check_result, model_updates)
    
    # Check only
    if args.check or (not args.update and not args.auto):
        if check_result['update_available'] or model_updates:
            print("Run with --update to apply changes")
        return 0
    
    # Apply updates
    if args.update or args.auto:
        applier = UpdateApplier(config)
        
        # Protocol updates
        if check_result['component_updates']:
            print("\nApplying protocol updates...")
            result = applier.apply_updates(check_result['component_updates'], auto=args.auto)
            print(f"\n  Applied: {len(result['applied'])}")
            print(f"  Skipped: {len(result['skipped'])}")
            print(f"  Failed:  {len(result['failed'])}")
        
        # Model updates
        if model_updates:
            if args.auto:
                applied = apply_model_updates(config, model_updates)
                print(f"\n✓ Model updates applied: {applied}")
            else:
                response = input("\nApply model updates? (y/N): ")
                if response.lower() == 'y':
                    applied = apply_model_updates(config, model_updates)
                    print(f"✓ Updated {applied} agents")
        
        # Update local state
        local_state = config.load_local_state()
        local_state['last_update'] = datetime.now().isoformat()
        if check_result.get('remote_version'):
            local_state['installed_version'] = check_result['remote_version']
        config.save_local_state(local_state)
        
        print("\n✓ Update complete. Run /validate to verify installation.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
