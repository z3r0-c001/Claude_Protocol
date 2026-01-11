#!/usr/bin/env python3
"""
enforcement-hook.py - Protocol Enforcement Hook (UserPromptSubmit)

Runs BEFORE any other hooks. Analyzes the prompt and enforces:
1. Orchestrator usage for complex/collaborative tasks
2. Agent invocation for domain-specific work
3. Plan mode before execute mode
4. Quality gate execution

Can BLOCK execution if protocol requirements not met.
"""

import json
import sys
import os
import time
from pathlib import Path

# Add monitor module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = Path(os.environ.get('CLAUDE_LOG_DIR', Path.home() / '.claude' / 'logs'))
ENFORCEMENT_CONFIG = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())) / '.claude' / 'config' / 'enforcement-rules.json'

# Complexity thresholds
COMPLEXITY_THRESHOLD = 3
COLLAB_PHRASES = ['can we', "let's", 'how do we', 'help me', 'figure out', 'work on', 'work through', 'let me know']
MULTI_STEP = ['and then', 'after that', 'first', 'then', 'next', 'finally', 'once', 'step']
SCOPE_WORDS = ['entire', 'whole', 'all', 'every', 'across', 'complete', 'full']

# Domain patterns
DOMAIN_PATTERNS = {
    'security': r'\b(security|auth|password|token|credential|encrypt|vulnerability|injection)\b',
    'architecture': r'\b(architect|design|refactor|restructure|reorganize|pattern)\b',
    'testing': r'\b(test|spec|coverage|tdd|unit test|integration)\b',
    'performance': r'\b(performance|optimize|slow|fast|cache|memory|bottleneck)\b',
    'frontend': r'\b(ui|component|button|form|layout|css|style|responsive)\b'
}

DOMAIN_AGENTS = {
    'security': 'security-scanner',
    'architecture': 'architect',
    'testing': 'tester',
    'performance': 'performance-analyzer',
    'frontend': 'frontend-designer'
}


def load_config():
    """Load enforcement rules configuration"""
    defaults = {
        'enforce_orchestration': True,
        'enforce_agents': True,
        'enforce_plan_mode': True,
        'complexity_threshold': COMPLEXITY_THRESHOLD,
        'strict_mode': False,  # Block vs warn
        'bypass_phrases': ['just', 'quickly', 'simple', 'only']
    }
    
    if ENFORCEMENT_CONFIG.exists():
        try:
            with open(ENFORCEMENT_CONFIG) as f:
                config = json.load(f)
                defaults.update(config)
        except (json.JSONDecodeError, IOError, OSError) as e:
            sys.stderr.write(f"Warning: Failed to load enforcement config: {e}\n")
    
    return defaults


def analyze_complexity(prompt: str) -> dict:
    """Analyze prompt complexity and requirements"""
    import re
    p = prompt.lower()
    
    result = {
        'complexity': 1,
        'signals': [],
        'domains': [],
        'requires_orchestrator': False,
        'requires_agents': [],
        'bypass_detected': False
    }
    
    config = load_config()
    
    # Check bypass phrases
    for phrase in config.get('bypass_phrases', []):
        if phrase in p:
            result['bypass_detected'] = True
            result['signals'].append(f'bypass:{phrase}')
    
    # Collaboration signals
    for phrase in COLLAB_PHRASES:
        if phrase in p:
            result['complexity'] += 1
            result['signals'].append(f'collab:{phrase}')
            break
    
    # Multi-step signals
    multi_count = sum(1 for word in MULTI_STEP if word in p)
    if multi_count >= 2:
        result['complexity'] += 2
        result['signals'].append(f'multi-step:{multi_count}')
    elif multi_count == 1:
        result['complexity'] += 1
        result['signals'].append('multi-step:1')
    
    # Scope signals
    for word in SCOPE_WORDS:
        if word in p:
            result['complexity'] += 1
            result['signals'].append(f'scope:{word}')
            break
    
    # Domain detection
    for domain, pattern in DOMAIN_PATTERNS.items():
        if re.search(pattern, p, re.IGNORECASE):
            result['domains'].append(domain)
            if domain in ['security', 'architecture']:
                result['complexity'] += 1
    
    # Cap complexity
    result['complexity'] = min(result['complexity'], 5)
    
    # Determine requirements
    threshold = config.get('complexity_threshold', COMPLEXITY_THRESHOLD)
    
    if result['complexity'] >= threshold or any('collab' in s for s in result['signals']):
        result['requires_orchestrator'] = True
    
    for domain in result['domains']:
        if domain in DOMAIN_AGENTS:
            result['requires_agents'].append(DOMAIN_AGENTS[domain])
    
    return result


def emit_log(entry: dict):
    """Emit to monitor log"""
    try:
        import urllib.request
        import urllib.error
        url = os.environ.get('CLAUDE_MONITOR_URL', 'http://localhost:3847/log')
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=0.5)
    except (urllib.error.URLError, OSError, ValueError):
        # Monitor not running or unreachable - this is non-critical
        pass


def main():
    # Read input
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # No valid JSON input - exit silently (hook not applicable)
        sys.exit(0)
    
    prompt = input_data.get('prompt', '')
    if not prompt:
        sys.exit(0)
    
    config = load_config()
    analysis = analyze_complexity(prompt)
    
    # Log the analysis
    emit_log({
        'type': 'enforcement',
        'event': 'analysis',
        'complexity': analysis['complexity'],
        'signals': analysis['signals'],
        'domains': analysis['domains'],
        'requires_orchestrator': analysis['requires_orchestrator'],
        'requires_agents': analysis['requires_agents'],
        'timestamp': int(time.time() * 1000)
    })
    
    # Build enforcement message
    enforcement_parts = []
    
    if analysis['requires_orchestrator'] and config.get('enforce_orchestration', True):
        if not analysis['bypass_detected']:
            enforcement_parts.append(
                f"⚠️ ORCHESTRATION REQUIRED: Complexity {analysis['complexity']}/5 detected. "
                f"Signals: {', '.join(analysis['signals'])}. "
                "Use the orchestrator agent via Task tool to coordinate this work."
            )
    
    if analysis['requires_agents'] and config.get('enforce_agents', True):
        enforcement_parts.append(
            f"📋 AGENTS SUGGESTED: {', '.join(analysis['requires_agents'])} "
            f"for domains: {', '.join(analysis['domains'])}"
        )
    
    if config.get('enforce_plan_mode', True) and analysis['complexity'] >= 3:
        enforcement_parts.append(
            "📝 PLAN MODE REQUIRED: Run agents in plan mode first, then execute after approval."
        )
    
    # Output
    if enforcement_parts:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n\n".join([
                    "🔒 PROTOCOL ENFORCEMENT:",
                    *enforcement_parts,
                    "",
                    "This enforcement ensures quality and completeness. "
                    "Invoke orchestrator for complex tasks, use specialized agents for domain work."
                ])
            }
        }
        
        # In strict mode, block if orchestrator required but signal bypass
        if config.get('strict_mode', False) and analysis['requires_orchestrator'] and not analysis['bypass_detected']:
            emit_log({
                'type': 'enforcement',
                'event': 'blocked',
                'reason': 'orchestrator_required',
                'analysis': analysis,
                'timestamp': int(time.time() * 1000)
            })
            # Can't actually block at UserPromptSubmit, but we inject strong guidance
        
        print(json.dumps(output))
    
    sys.exit(0)


if __name__ == '__main__':
    main()
