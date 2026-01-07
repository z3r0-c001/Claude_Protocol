#!/usr/bin/env python3
"""
model-audit.py - Checks agent model versions against current known models

Runs on first tool use of each session. Warns if agents use outdated/unknown models.

Hook Type: Notification (PreToolUse on first invocation)
"""

import json
import sys
import os
import glob
import re
from pathlib import Path
from datetime import datetime

# Session tracking - only run once per session
SESSION_FILE = "/tmp/.claude-model-audit-done"

def get_project_dir():
    """Get project directory from environment or current directory."""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

def load_models_config():
    """Load the centralized models configuration."""
    project_dir = get_project_dir()
    config_path = Path(project_dir) / '.claude' / 'config' / 'models.json'
    
    if not config_path.exists():
        return None
    
    with open(config_path) as f:
        return json.load(f)

def get_current_model_ids(config):
    """Extract list of current valid model IDs."""
    if not config:
        return set()
    
    model_ids = set()
    for model_info in config.get('current_models', {}).values():
        model_ids.add(model_info['model_id'])
    
    return model_ids

def get_deprecated_models(config):
    """Get mapping of deprecated model -> replacement."""
    if not config:
        return {}
    
    deprecated = {}
    for item in config.get('deprecated_models', []):
        deprecated[item['model_id']] = item.get('replacement', 'unknown')
    
    return deprecated

def scan_agent_models():
    """Scan all agent files and extract model strings."""
    project_dir = get_project_dir()
    agents_dir = Path(project_dir) / '.claude' / 'agents'
    
    agent_models = {}
    
    for agent_file in glob.glob(str(agents_dir / '**' / '*.md'), recursive=True):
        if 'AGENT_PROTOCOL' in agent_file:
            continue
        
        agent_name = Path(agent_file).stem
        
        with open(agent_file) as f:
            content = f.read()
        
        # Extract model from frontmatter
        match = re.search(r'^model:\s*(.+)$', content, re.MULTILINE)
        if match:
            agent_models[agent_name] = match.group(1).strip()
    
    return agent_models

def audit_models():
    """Main audit function. Returns issues found."""
    config = load_models_config()
    if not config:
        return {'error': 'models.json not found'}
    
    current_models = get_current_model_ids(config)
    deprecated_models = get_deprecated_models(config)
    agent_models = scan_agent_models()
    
    issues = {
        'outdated': [],      # Using deprecated model
        'unknown': [],       # Using unrecognized model
        'current': [],       # All good
    }
    
    for agent, model in agent_models.items():
        if model in current_models:
            issues['current'].append(agent)
        elif model in deprecated_models:
            issues['outdated'].append({
                'agent': agent,
                'current_model': model,
                'replacement': deprecated_models[model]
            })
        else:
            issues['unknown'].append({
                'agent': agent,
                'model': model
            })
    
    return issues

def format_warning(issues):
    """Format issues into a user-friendly warning message."""
    lines = []
    
    if issues.get('outdated'):
        lines.append("⚠️  OUTDATED MODELS DETECTED")
        lines.append("   The following agents use deprecated model versions:")
        for item in issues['outdated']:
            lines.append(f"   • {item['agent']}: {item['current_model']}")
            lines.append(f"     └─ Replace with: {item['replacement']}")
        lines.append("")
    
    if issues.get('unknown'):
        lines.append("❓ UNKNOWN MODELS DETECTED")
        lines.append("   The following agents use unrecognized model strings:")
        for item in issues['unknown']:
            lines.append(f"   • {item['agent']}: {item['model']}")
        lines.append("")
    
    if lines:
        lines.insert(0, "")
        lines.insert(0, "╔══════════════════════════════════════════════════════════════╗")
        lines.insert(1, "║              MODEL VERSION AUDIT                             ║")
        lines.insert(2, "╠══════════════════════════════════════════════════════════════╣")
        lines.append("╠══════════════════════════════════════════════════════════════╣")
        lines.append("║  Run /update-proto to update to latest model versions        ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        lines.append("")
    
    return '\n'.join(lines)

def should_run():
    """Check if we should run this session (once per session)."""
    # Check if already run this session
    if os.path.exists(SESSION_FILE):
        # Check if file is from today
        mtime = os.path.getmtime(SESSION_FILE)
        file_date = datetime.fromtimestamp(mtime).date()
        if file_date == datetime.now().date():
            return False
    
    return True

def mark_complete():
    """Mark audit as complete for this session."""
    Path(SESSION_FILE).touch()

def main():
    # Only run once per session
    if not should_run():
        print(json.dumps({"continue": True}))
        return
    
    try:
        issues = audit_models()
        
        if 'error' in issues:
            # Config not found - skip silently
            print(json.dumps({"continue": True}))
            return
        
        # Check if there are problems
        has_issues = issues.get('outdated') or issues.get('unknown')
        
        if has_issues:
            warning = format_warning(issues)
            # Output warning to stderr (visible to user)
            print(warning, file=sys.stderr)
        
        mark_complete()
        
        # Always continue - this is informational only
        print(json.dumps({"continue": True}))
        
    except Exception as e:
        # Don't block on audit errors
        print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
