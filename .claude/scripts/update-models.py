#!/usr/bin/env python3
"""
update-models.py - Update models.json with latest model versions

Can fetch from remote source or accept manual updates.
Used by /update-proto command.

Usage:
    python3 update-models.py --check          # Check for updates only
    python3 update-models.py --update         # Apply updates
    python3 update-models.py --set opus=claude-opus-4-6-20260101  # Manual set
"""

import json
import sys
import os
import argparse
import re
import glob
from pathlib import Path
from datetime import datetime

def get_project_dir():
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

def load_models_config():
    config_path = Path(get_project_dir()) / '.claude' / 'config' / 'models.json'
    with open(config_path) as f:
        return json.load(f)

def save_models_config(config):
    config_path = Path(get_project_dir()) / '.claude' / 'config' / 'models.json'
    config['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def get_agent_files():
    """Get all agent markdown files."""
    project_dir = get_project_dir()
    agents_dir = Path(project_dir) / '.claude' / 'agents'
    return glob.glob(str(agents_dir / '**' / '*.md'), recursive=True)

def update_agent_model(agent_file, old_model, new_model):
    """Update model string in an agent file."""
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Replace model line in frontmatter
    updated = re.sub(
        rf'^model:\s*{re.escape(old_model)}$',
        f'model: {new_model}',
        content,
        flags=re.MULTILINE
    )
    
    if updated != content:
        with open(agent_file, 'w') as f:
            f.write(updated)
        return True
    return False

def check_updates(config):
    """Check what updates are available."""
    updates = []
    
    # Scan agents for deprecated models
    deprecated = {d['model_id']: d['replacement'] for d in config.get('deprecated_models', [])}
    current_ids = {m['model_id'] for m in config.get('current_models', {}).values()}
    
    for agent_file in get_agent_files():
        if 'AGENT_PROTOCOL' in agent_file:
            continue
            
        with open(agent_file) as f:
            content = f.read()
        
        match = re.search(r'^model:\s*(.+)$', content, re.MULTILINE)
        if match:
            model = match.group(1).strip()
            if model in deprecated:
                updates.append({
                    'file': agent_file,
                    'agent': Path(agent_file).stem,
                    'old_model': model,
                    'new_model': deprecated[model]
                })
    
    return updates

def apply_updates(updates):
    """Apply model updates to agent files."""
    results = []
    for update in updates:
        success = update_agent_model(
            update['file'],
            update['old_model'],
            update['new_model']
        )
        results.append({
            'agent': update['agent'],
            'success': success,
            'old': update['old_model'],
            'new': update['new_model']
        })
    return results

def set_model(config, tier, model_id):
    """Manually set a model for a tier."""
    if tier not in config['current_models']:
        print(f"Error: Unknown tier '{tier}'. Valid: opus, sonnet, haiku")
        return False
    
    old_model = config['current_models'][tier]['model_id']
    config['current_models'][tier]['model_id'] = model_id
    config['current_models'][tier]['status'] = 'current'
    
    # Move old model to deprecated if different
    if old_model != model_id:
        # Check if already in deprecated
        existing = [d for d in config['deprecated_models'] if d['model_id'] == old_model]
        if not existing:
            config['deprecated_models'].append({
                'model_id': old_model,
                'deprecated_date': datetime.now().strftime('%Y-%m-%d'),
                'replacement': model_id
            })
    
    save_models_config(config)
    print(f"Updated {tier}: {old_model} → {model_id}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Update Claude model versions')
    parser.add_argument('--check', action='store_true', help='Check for available updates')
    parser.add_argument('--update', action='store_true', help='Apply updates to agent files')
    parser.add_argument('--set', metavar='TIER=MODEL', help='Manually set model (e.g., opus=claude-opus-4-6-20260101)')
    parser.add_argument('--list', action='store_true', help='List current model configuration')
    
    args = parser.parse_args()
    
    try:
        config = load_models_config()
    except FileNotFoundError:
        print("Error: models.json not found. Run from project root.")
        sys.exit(1)
    
    if args.list:
        print("\nCurrent Model Configuration:")
        print("=" * 50)
        for tier, info in config['current_models'].items():
            print(f"  {tier:8} → {info['model_id']}")
        print(f"\nLast updated: {config.get('last_updated', 'unknown')}")
        print(f"Deprecated models tracked: {len(config.get('deprecated_models', []))}")
        return
    
    if args.set:
        if '=' not in args.set:
            print("Error: Use format TIER=MODEL (e.g., --set opus=claude-opus-4-6-20260101)")
            sys.exit(1)
        tier, model = args.set.split('=', 1)
        set_model(config, tier, model)
        
        # Also check if agents need updating
        updates = check_updates(config)
        if updates:
            print(f"\n{len(updates)} agent(s) need updating. Run with --update to apply.")
        return
    
    if args.check:
        updates = check_updates(config)
        if not updates:
            print("✓ All agents using current models")
        else:
            print(f"\n{len(updates)} agent(s) need model updates:\n")
            for u in updates:
                print(f"  {u['agent']:25} {u['old_model']}")
                print(f"  {'':25} └─ {u['new_model']}")
            print(f"\nRun with --update to apply changes.")
        return
    
    if args.update:
        updates = check_updates(config)
        if not updates:
            print("✓ All agents already using current models")
            return
        
        print(f"Updating {len(updates)} agent(s)...")
        results = apply_updates(updates)
        
        success = sum(1 for r in results if r['success'])
        print(f"\n✓ Updated {success}/{len(results)} agents")
        
        for r in results:
            status = "✓" if r['success'] else "✗"
            print(f"  {status} {r['agent']}: {r['old']} → {r['new']}")
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main()
