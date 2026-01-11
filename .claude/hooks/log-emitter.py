#!/usr/bin/env python3
"""
log-emitter.py - Universal logging hook for Claude Monitor

Captures all hook events and sends them to the monitor server.
Install as the FIRST hook in each event category.

Events captured:
- UserPromptSubmit: User prompts
- PreToolUse: Tool invocations before execution
- PostToolUse: Tool results after execution
- Stop: Response completion
- Notification: System events
"""

import json
import sys
import os
import time
import urllib.request
import urllib.error
from datetime import datetime

MONITOR_URL = os.environ.get('CLAUDE_MONITOR_URL', 'http://localhost:3847/log')
MONITOR_ENABLED = os.environ.get('CLAUDE_MONITOR_ENABLED', '1') == '1'


def emit_log(entry: dict) -> bool:
    """Send log entry to monitor server."""
    if not MONITOR_ENABLED:
        return False
    
    try:
        data = json.dumps(entry).encode('utf-8')
        req = urllib.request.Request(
            MONITOR_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=1)
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def get_hook_event() -> str:
    """Determine which hook event triggered this script."""
    # Check environment or parse from input
    return os.environ.get('CLAUDE_HOOK_EVENT', 'unknown')


def format_prompt_event(data: dict) -> dict:
    """Format UserPromptSubmit event."""
    # Do NOT truncate user prompts - full visibility in monitor
    return {
        'type': 'prompt',
        'event': 'UserPromptSubmit',
        'content': data.get('prompt', ''),
        'timestamp': int(time.time() * 1000)
    }


def format_tool_event(data: dict, phase: str) -> dict:
    """Format PreToolUse or PostToolUse event."""
    tool_input = data.get('tool_input', {})
    
    entry = {
        'type': 'tool',
        'event': f'{phase}ToolUse',
        'tool': data.get('tool_name', 'unknown'),
        'timestamp': int(time.time() * 1000)
    }
    
    # Extract relevant details based on tool type
    tool_name = data.get('tool_name', '')
    
    if tool_name in ['Read', 'Write', 'Edit']:
        entry['file'] = tool_input.get('file_path', tool_input.get('path', ''))
        entry['action'] = 'read' if tool_name == 'Read' else 'write'
    elif tool_name == 'Bash':
        entry['command'] = tool_input.get('command', '')[:100]
        entry['action'] = 'execute'
    elif tool_name == 'Task':
        entry['type'] = 'agent'
        entry['agent'] = tool_input.get('subagent_type', 'unknown')
        entry['action'] = 'invoke'
        entry['mode'] = tool_input.get('execution_mode', 'execute')
    elif tool_name == 'WebSearch':
        entry['action'] = 'search'
        entry['query'] = tool_input.get('query', '')[:100]
    
    if phase == 'Post':
        result = data.get('tool_result', {})
        entry['success'] = not result.get('is_error', False)
        if result.get('is_error'):
            entry['error'] = str(result.get('content', ''))[:200]
    
    return entry


def format_stop_event(data: dict) -> dict:
    """Format Stop event."""
    return {
        'type': 'response',
        'event': 'Stop',
        'summary': data.get('stop_reason', 'complete'),
        'timestamp': int(time.time() * 1000)
    }


def main():
    start_time = time.time()
    
    # Read input
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        input_data = {}
    
    # Determine event type from input structure
    if 'prompt' in input_data:
        event_type = 'UserPromptSubmit'
        entry = format_prompt_event(input_data)
    elif 'tool_name' in input_data:
        # Check if this is pre or post based on presence of result
        if 'tool_result' in input_data:
            event_type = 'PostToolUse'
            entry = format_tool_event(input_data, 'Post')
        else:
            event_type = 'PreToolUse'
            entry = format_tool_event(input_data, 'Pre')
    elif 'stop_reason' in input_data:
        event_type = 'Stop'
        entry = format_stop_event(input_data)
    else:
        event_type = 'unknown'
        entry = {
            'type': 'system',
            'event': event_type,
            'data': str(input_data)[:200],
            'timestamp': int(time.time() * 1000)
        }
    
    # Emit to monitor
    emit_log(entry)
    
    # Pass through - this hook is passive
    sys.exit(0)


if __name__ == '__main__':
    main()
