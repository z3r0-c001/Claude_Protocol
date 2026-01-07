#!/usr/bin/env python3
"""
health-check.py - Startup health check for Claude Protocol

Runs on session startup to check:
1. Model versions - Are agents using current models?
2. Protocol version - Is there an update available?
3. Hook integrity - Do all referenced hook files exist?

Usage:
    python3 health-check.py              # Full check, require acknowledgment
    python3 health-check.py --quiet      # Silent if OK, show only issues
    python3 health-check.py --no-network # Skip remote version check
    python3 health-check.py --no-ack     # Don't require acknowledgment (for hooks)

Exit codes:
    0 - All OK (or user acknowledged warnings)
    1 - Issues found and not acknowledged
    2 - Critical error
"""

import json
import sys
import os
import glob
import re
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# =============================================================================
# CONFIGURATION
# =============================================================================

CACHE_HOURS = 24  # Cache remote version check
CACHE_FILE = Path("/tmp/.claude-protocol-version-cache")
SESSION_FILE = Path("/tmp/.claude-health-check-session")

class Config:
    def __init__(self):
        self.project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
        self.manifest_path = self.project_dir / 'protocol-manifest.json'
        self.models_config = self.project_dir / '.claude' / 'config' / 'models.json'
        self.settings_path = self.project_dir / '.claude' / 'settings.json'
        self.agents_dir = self.project_dir / '.claude' / 'agents'
        self.hooks_dir = self.project_dir / '.claude' / 'hooks'

# =============================================================================
# HEALTH CHECKS
# =============================================================================

class HealthChecker:
    def __init__(self, config: Config, no_network: bool = False):
        self.config = config
        self.no_network = no_network
        self.issues: List[Dict] = []      # Critical - should block
        self.warnings: List[Dict] = []    # Important - require ack
        self.info: List[Dict] = []        # Informational
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        self.check_models()
        if not self.no_network:
            self.check_protocol_version()
        self.check_hook_integrity()
        
        return {
            'healthy': len(self.issues) == 0 and len(self.warnings) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def check_models(self):
        """Check if agents use current model versions."""
        if not self.config.models_config.exists():
            return
        
        try:
            with open(self.config.models_config) as f:
                model_cfg = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.issues.append({
                'type': 'config_error',
                'message': 'Could not read models.json',
                'fix': 'Check .claude/config/models.json syntax'
            })
            return
        
        current_ids = {m['model_id'] for m in model_cfg.get('current_models', {}).values()}
        deprecated = {d['model_id']: d['replacement'] for d in model_cfg.get('deprecated_models', [])}
        
        outdated = []
        for agent_file in glob.glob(str(self.config.agents_dir / '**' / '*.md'), recursive=True):
            if 'AGENT_PROTOCOL' in agent_file:
                continue
            
            try:
                with open(agent_file) as f:
                    content = f.read()
            except IOError:
                continue
            
            match = re.search(r'^model:\s*(.+)$', content, re.MULTILINE)
            if match:
                model = match.group(1).strip()
                if model in deprecated:
                    outdated.append({
                        'agent': Path(agent_file).stem,
                        'current': model,
                        'replacement': deprecated[model]
                    })
        
        if outdated:
            self.warnings.append({
                'type': 'outdated_models',
                'message': f'{len(outdated)} agent(s) using deprecated models',
                'details': outdated,
                'fix': '/proto-update --models'
            })
    
    def check_protocol_version(self):
        """Check if protocol update is available."""
        if not self.config.manifest_path.exists():
            return
        
        try:
            with open(self.config.manifest_path) as f:
                local_manifest = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        
        local_version = local_manifest.get('protocol', {}).get('version', '0.0.0')
        raw_base = local_manifest.get('repository', {}).get('raw_base', '')
        
        if not raw_base:
            return
        
        # Check cache first
        remote_version = self._get_cached_version()
        
        if remote_version is None:
            remote_version = self._fetch_remote_version(raw_base)
            if remote_version:
                self._cache_version(remote_version)
        
        if remote_version and self._version_gt(remote_version, local_version):
            self.info.append({
                'type': 'update_available',
                'message': f'Protocol update: {local_version} → {remote_version}',
                'fix': '/proto-update --update'
            })
    
    def _get_cached_version(self) -> Optional[str]:
        try:
            if not CACHE_FILE.exists():
                return None
            with open(CACHE_FILE) as f:
                cache = json.load(f)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=CACHE_HOURS):
                return cache.get('version')
        except:
            pass
        return None
    
    def _cache_version(self, version: str):
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'version': version
                }, f)
        except:
            pass
    
    def _fetch_remote_version(self, raw_base: str) -> Optional[str]:
        try:
            url = f"{raw_base}/protocol-manifest.json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Claude-Protocol/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                remote = json.load(response)
                return remote.get('protocol', {}).get('version')
        except:
            return None
    
    def _version_gt(self, v1: str, v2: str) -> bool:
        def parse(v):
            try:
                return tuple(int(x) for x in v.split('.'))
            except:
                return (0, 0, 0)
        return parse(v1) > parse(v2)
    
    def check_hook_integrity(self):
        """Check that all configured hooks exist."""
        if not self.config.settings_path.exists():
            return
        
        try:
            with open(self.config.settings_path) as f:
                settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.issues.append({
                'type': 'config_error',
                'message': 'Could not read settings.json',
                'fix': 'Check .claude/settings.json syntax'
            })
            return
        
        hooks = settings.get('hooks', {})
        missing = []
        
        for hook_type, hook_list in hooks.items():
            if not isinstance(hook_list, list):
                continue
            
            for hook in hook_list:
                if not isinstance(hook, dict):
                    continue
                
                command = hook.get('command', '')
                match = re.search(r'run-hook\.sh["\s]+([a-zA-Z0-9_-]+\.(?:py|sh))', command)
                if match:
                    hook_file = match.group(1)
                    hook_path = self.config.hooks_dir / hook_file
                    if not hook_path.exists():
                        missing.append(hook_file)
        
        if missing:
            self.issues.append({
                'type': 'missing_hooks',
                'message': f'{len(missing)} hook file(s) not found',
                'details': missing,
                'fix': 'Reinstall protocol or restore missing files'
            })

# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_results(results: Dict) -> str:
    """Format health check results for display."""
    if results['healthy'] and not results['info']:
        return ""
    
    lines = []
    lines.append("")
    lines.append("╔════════════════════════════════════════════════════════════════╗")
    lines.append("║              CLAUDE PROTOCOL HEALTH CHECK                      ║")
    lines.append("╠════════════════════════════════════════════════════════════════╣")
    
    if results['issues']:
        lines.append("║  ❌ CRITICAL ISSUES                                            ║")
        lines.append("╠────────────────────────────────────────────────────────────────╣")
        for issue in results['issues']:
            msg = issue['message'][:54]
            lines.append(f"║  • {msg:<56} ║")
            if 'details' in issue:
                for d in issue['details'][:3]:
                    lines.append(f"║    - {str(d)[:52]:<54} ║")
            if 'fix' in issue:
                lines.append(f"║    → {issue['fix']:<54} ║")
    
    if results['warnings']:
        if results['issues']:
            lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║  ⚠️  WARNINGS (require acknowledgment)                          ║")
        lines.append("╠────────────────────────────────────────────────────────────────╣")
        for warning in results['warnings']:
            msg = warning['message'][:54]
            lines.append(f"║  • {msg:<56} ║")
            if 'details' in warning and isinstance(warning['details'], list):
                for detail in warning['details'][:3]:
                    if isinstance(detail, dict):
                        agent = detail.get('agent', str(detail))[:52]
                        lines.append(f"║    - {agent:<54} ║")
                if len(warning['details']) > 3:
                    more = len(warning['details']) - 3
                    lines.append(f"║    ... and {more} more{' '*43} ║")
            if 'fix' in warning:
                lines.append(f"║    → {warning['fix']:<54} ║")
    
    if results['info']:
        if results['issues'] or results['warnings']:
            lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("║  ℹ️  INFO                                                       ║")
        lines.append("╠────────────────────────────────────────────────────────────────╣")
        for info in results['info']:
            msg = info['message'][:54]
            lines.append(f"║  • {msg:<56} ║")
            if 'fix' in info:
                lines.append(f"║    → {info['fix']:<54} ║")
    
    lines.append("╚════════════════════════════════════════════════════════════════╝")
    lines.append("")
    
    return '\n'.join(lines)

# =============================================================================
# ACKNOWLEDGMENT
# =============================================================================

def require_acknowledgment(results: Dict) -> bool:
    """Require user acknowledgment. Returns True if acknowledged."""
    if results['healthy']:
        return True
    
    # Non-interactive (piped) - can't get input
    if not sys.stdin.isatty():
        print("\n⚠️  Issues require acknowledgment. Run interactively to acknowledge.", file=sys.stderr)
        return False
    
    print("\n" + "─" * 64)
    if results['issues']:
        print("❌ Critical issues found. Please address before continuing.")
        response = input("\nAcknowledge and continue anyway? (yes/no): ")
    else:
        print("⚠️  Warnings found. Recommended to address these.")
        response = input("\nAcknowledge and continue? (yes/no): ")
    
    return response.lower().strip() in ('yes', 'y')

# =============================================================================
# SESSION TRACKING
# =============================================================================

def already_checked() -> bool:
    """Check if already run this session."""
    if SESSION_FILE.exists():
        try:
            mtime = datetime.fromtimestamp(SESSION_FILE.stat().st_mtime)
            if datetime.now() - mtime < timedelta(hours=1):
                return True
        except:
            pass
    return False

def mark_checked():
    """Mark health check as done for this session."""
    try:
        SESSION_FILE.touch()
    except:
        pass

# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Protocol Health Check')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--no-network', action='store_true', help='Skip remote check')
    parser.add_argument('--force', action='store_true', help='Run even if already checked')
    parser.add_argument('--no-ack', action='store_true', help='Skip acknowledgment')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    # Skip if already checked this session
    if not args.force and already_checked():
        if not args.quiet:
            print("✓ Already checked this session", file=sys.stderr)
        return 0
    
    # Run checks
    config = Config()
    checker = HealthChecker(config, no_network=args.no_network)
    results = checker.run_all_checks()
    
    # JSON output for hooks
    if args.json:
        print(json.dumps(results, indent=2))
        return 0 if results['healthy'] else 1
    
    # Format and display
    output = format_results(results)
    if output:
        print(output, file=sys.stderr)
    elif not args.quiet:
        print("✓ Protocol health check passed", file=sys.stderr)
    
    # Require acknowledgment
    if not args.no_ack and not results['healthy']:
        if not require_acknowledgment(results):
            print("\n❌ Please address issues before continuing.", file=sys.stderr)
            return 1
    
    mark_checked()
    return 0

if __name__ == "__main__":
    sys.exit(main())
