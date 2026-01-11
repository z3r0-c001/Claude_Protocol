#!/usr/bin/env python3
"""
hook-status-emitter.py - Emit hook execution status to monitor

Call this from other hooks to report their status:
    from hook_status_emitter import emit_hook_status
    emit_hook_status('my-hook', 'RUNNING', 'Starting validation')
    emit_hook_status('my-hook', 'OK', 'Passed')
"""

import json
import os
import time
import urllib.request
import urllib.error
import sys

MONITOR_URL = os.environ.get('CLAUDE_MONITOR_URL', 'http://localhost:3847/log')


def emit_hook_status(hook_name: str, status: str, message: str = '', 
                     event: str = '', duration_ms: int = None, 
                     details: dict = None):
    """
    Emit hook status to monitor.
    
    Args:
        hook_name: Name of the hook (e.g., 'laziness-check')
        status: RUNNING, OK, ERROR, BLOCKED, WARN
        message: Brief status message
        event: Hook event type (UserPromptSubmit, PreToolUse, etc.)
        duration_ms: Execution time in milliseconds
        details: Additional structured data
    """
    entry = {
        'type': 'hook',
        'hook': hook_name,
        'status': status,
        'message': message,
        'event': event,
        'timestamp': int(time.time() * 1000)
    }
    
    if duration_ms is not None:
        entry['duration'] = duration_ms
    
    if details:
        entry['details'] = details
    
    try:
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(
            MONITOR_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=0.5)
    except:
        pass  # Non-blocking


def emit_agent_status(agent_name: str, action: str, mode: str = 'execute',
                      status: str = None, details: dict = None):
    """Emit agent invocation status."""
    entry = {
        'type': 'agent',
        'agent': agent_name,
        'action': action,
        'mode': mode,
        'timestamp': int(time.time() * 1000)
    }
    
    if status:
        entry['status'] = status
    if details:
        entry['details'] = details
    
    try:
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(
            MONITOR_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=0.5)
    except:
        pass


def emit_intent(prompt: str, route: str, confidence: int, 
                agents: list = None, reasoning: str = ''):
    """Emit intent evaluation result."""
    entry = {
        'type': 'intent',
        'prompt': prompt[:200],
        'route': route,
        'confidence': confidence,
        'suggested_agents': agents or [],
        'reasoning': reasoning,
        'timestamp': int(time.time() * 1000)
    }
    
    try:
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(
            MONITOR_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=0.5)
    except:
        pass


def emit_error(source: str, message: str, stack: str = None):
    """Emit error event."""
    entry = {
        'type': 'error',
        'source': source,
        'message': message,
        'timestamp': int(time.time() * 1000)
    }
    
    if stack:
        entry['stack'] = stack
    
    try:
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(
            MONITOR_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=0.5)
    except:
        pass


# CLI interface
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: hook-status-emitter.py <hook_name> <status> <message>')
        sys.exit(1)
    
    emit_hook_status(sys.argv[1], sys.argv[2], sys.argv[3])
