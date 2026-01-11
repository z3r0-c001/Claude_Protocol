#!/usr/bin/env python3
"""
monitor-agent.py - Impartial Protocol Enforcement Agent

Runs continuously alongside Claude Code, analyzing logs in real-time.
Detects:
- Protocol violations (not using agents when required)
- Skipped orchestration for complex tasks
- Missing hook executions
- Anomalous patterns
- Quality degradation

Can:
- STOP execution with blocking signal
- ASK for clarification by injecting prompts
- LOG violations for review
- ENFORCE agent/orchestrator usage

This is the "impartial observer" that ensures the protocol is followed.
"""

import json
import sys
import os
import time
import threading
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

# Configuration
LOG_DIR = Path(os.environ.get('CLAUDE_LOG_DIR', Path.home() / '.claude' / 'logs'))
MONITOR_LOG = LOG_DIR / 'monitor.jsonl'
ANOMALY_LOG = LOG_DIR / 'anomalies.jsonl'
ENFORCEMENT_LOG = LOG_DIR / 'enforcement.jsonl'
MONITOR_STATE = LOG_DIR / 'monitor-state.json'

# Thresholds
COMPLEXITY_THRESHOLD = 3  # Complexity score requiring orchestration
MULTI_STEP_WORDS = ['and then', 'after that', 'first', 'then', 'next', 'finally', 'once']
COLLAB_PHRASES = ['can we', "let's", 'how do we', 'help me', 'figure out', 'work on', 'let me know']
HOOK_TIMEOUT_MS = 5000
AGENT_TIMEOUT_MS = 60000


class Severity(Enum):
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'
    CRITICAL = 'critical'


class Action(Enum):
    LOG = 'log'
    WARN = 'warn'
    ASK = 'ask'
    STOP = 'stop'


@dataclass
class Violation:
    timestamp: int
    severity: Severity
    rule: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    action_taken: Action = Action.LOG


@dataclass 
class ExecutionContext:
    """Track current execution state"""
    prompt: Optional[str] = None
    prompt_time: Optional[int] = None
    complexity_score: int = 0
    orchestrator_active: bool = False
    active_agents: List[str] = field(default_factory=list)
    hooks_executed: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    subagents_spawned: List[str] = field(default_factory=list)
    violations: List[Violation] = field(default_factory=list)


class ProtocolEnforcer:
    """Enforces protocol rules and detects violations"""
    
    RULES = {
        'ORCH_REQUIRED': {
            'description': 'Orchestrator required for complex/collaborative tasks',
            'severity': Severity.ERROR,
            'action': Action.STOP
        },
        'AGENT_REQUIRED': {
            'description': 'Agent invocation required for domain-specific task',
            'severity': Severity.WARN,
            'action': Action.ASK
        },
        'HOOK_MISSING': {
            'description': 'Expected hook did not execute',
            'severity': Severity.WARN,
            'action': Action.LOG
        },
        'HOOK_TIMEOUT': {
            'description': 'Hook execution exceeded timeout',
            'severity': Severity.WARN,
            'action': Action.LOG
        },
        'SUBAGENT_EXPECTED': {
            'description': 'Task complexity suggests sub-agent needed',
            'severity': Severity.INFO,
            'action': Action.LOG
        },
        'QUALITY_GATE_SKIP': {
            'description': 'Quality gate hook was bypassed',
            'severity': Severity.ERROR,
            'action': Action.STOP
        },
        'LAZY_PATTERN': {
            'description': 'Lazy code pattern detected without laziness-destroyer',
            'severity': Severity.ERROR,
            'action': Action.STOP
        },
        'NO_PLAN_MODE': {
            'description': 'Agent executed without plan mode first',
            'severity': Severity.WARN,
            'action': Action.ASK
        }
    }
    
    def __init__(self):
        self.context = ExecutionContext()
        self.violation_history = deque(maxlen=1000)
        
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt for complexity and requirements"""
        p = prompt.lower()
        
        # Complexity scoring
        complexity = 1
        signals = []
        
        # Collaboration signals
        for phrase in COLLAB_PHRASES:
            if phrase in p:
                complexity += 1
                signals.append(f'collab:{phrase}')
                break
        
        # Multi-step signals
        multi_count = sum(1 for word in MULTI_STEP_WORDS if word in p)
        if multi_count >= 2:
            complexity += 2
            signals.append(f'multi-step:{multi_count}')
        elif multi_count == 1:
            complexity += 1
            signals.append('multi-step:1')
        
        # Scope signals
        if re.search(r'\b(entire|whole|all|every|across|complete)\b', p):
            complexity += 2
            signals.append('broad-scope')
        
        # Domain signals
        domains = []
        if re.search(r'\b(security|auth|password|token|encrypt)\b', p):
            domains.append('security')
            complexity += 1
        if re.search(r'\b(architect|design|refactor|restructure)\b', p):
            domains.append('architecture')
            complexity += 1
        if re.search(r'\b(test|coverage|spec)\b', p):
            domains.append('testing')
        if re.search(r'\b(performance|optimize|slow|fast)\b', p):
            domains.append('performance')
            complexity += 1
            
        complexity = min(complexity, 5)
        
        return {
            'complexity': complexity,
            'signals': signals,
            'domains': domains,
            'requires_orchestrator': complexity >= COMPLEXITY_THRESHOLD or 'collab' in str(signals),
            'suggested_agents': self._suggest_agents(domains, complexity)
        }
    
    def _suggest_agents(self, domains: List[str], complexity: int) -> List[str]:
        """Suggest agents based on detected domains"""
        agents = []
        domain_agents = {
            'security': 'security-scanner',
            'architecture': 'architect',
            'testing': 'tester',
            'performance': 'performance-analyzer'
        }
        for domain in domains:
            if domain in domain_agents:
                agents.append(domain_agents[domain])
        
        if complexity >= 4:
            if 'architect' not in agents:
                agents.insert(0, 'architect')
        
        return agents
    
    def check_orchestration_requirement(self, analysis: Dict) -> Optional[Violation]:
        """Check if orchestration should have been used"""
        if analysis['requires_orchestrator'] and not self.context.orchestrator_active:
            return Violation(
                timestamp=int(time.time() * 1000),
                severity=Severity.ERROR,
                rule='ORCH_REQUIRED',
                message=f"Complex task (score:{analysis['complexity']}) requires orchestrator but none active",
                context={'analysis': analysis},
                action_taken=self.RULES['ORCH_REQUIRED']['action']
            )
        return None
    
    def check_agent_requirement(self, analysis: Dict) -> Optional[Violation]:
        """Check if specific agents should have been invoked"""
        suggested = analysis['suggested_agents']
        missing = [a for a in suggested if a not in self.context.active_agents]
        
        if missing and analysis['complexity'] >= 2:
            return Violation(
                timestamp=int(time.time() * 1000),
                severity=Severity.WARN,
                rule='AGENT_REQUIRED',
                message=f"Domain-specific agents not invoked: {missing}",
                context={'suggested': suggested, 'active': self.context.active_agents},
                action_taken=self.RULES['AGENT_REQUIRED']['action']
            )
        return None
    
    def check_quality_gates(self) -> List[Violation]:
        """Check if quality gate hooks executed"""
        violations = []
        required_hooks = ['laziness-check', 'honesty-check']
        
        for hook in required_hooks:
            if hook not in self.context.hooks_executed:
                violations.append(Violation(
                    timestamp=int(time.time() * 1000),
                    severity=Severity.ERROR,
                    rule='QUALITY_GATE_SKIP',
                    message=f"Quality gate '{hook}' did not execute",
                    context={'executed': self.context.hooks_executed},
                    action_taken=self.RULES['QUALITY_GATE_SKIP']['action']
                ))
        
        return violations
    
    def process_event(self, event: Dict) -> List[Violation]:
        """Process a log event and check for violations"""
        violations = []
        event_type = event.get('type')
        
        if event_type == 'prompt':
            self.context = ExecutionContext()
            self.context.prompt = event.get('content', '')
            self.context.prompt_time = event.get('timestamp')
            
            analysis = self.analyze_prompt(self.context.prompt)
            self.context.complexity_score = analysis['complexity']
            
            # Check orchestration requirement
            v = self.check_orchestration_requirement(analysis)
            if v:
                violations.append(v)
        
        elif event_type == 'orchestrator':
            if event.get('action') == 'start':
                self.context.orchestrator_active = True
            elif event.get('action') == 'complete':
                self.context.orchestrator_active = False
        
        elif event_type == 'agent':
            agent = event.get('agent')
            action = event.get('action')
            
            if action in ['invoke', 'start']:
                self.context.active_agents.append(agent)
            elif action in ['complete', 'done']:
                if agent in self.context.active_agents:
                    self.context.active_agents.remove(agent)
        
        elif event_type == 'subagent':
            self.context.subagents_spawned.append(event.get('agent', 'unknown'))
        
        elif event_type == 'hook':
            hook = event.get('hook')
            self.context.hooks_executed.append(hook)
            
            # Check for blocked hooks
            if event.get('status') == 'BLOCKED':
                violations.append(Violation(
                    timestamp=event.get('timestamp', int(time.time() * 1000)),
                    severity=Severity.WARN,
                    rule='HOOK_BLOCKED',
                    message=f"Hook '{hook}' blocked execution: {event.get('message', '')}",
                    context={'hook': hook, 'event': event}
                ))
        
        elif event_type == 'tool':
            self.context.tools_used.append(event.get('tool', 'unknown'))
        
        elif event_type == 'response':
            # End of turn - check all requirements
            if self.context.complexity_score >= COMPLEXITY_THRESHOLD:
                analysis = self.analyze_prompt(self.context.prompt or '')
                
                # Agent check
                v = self.check_agent_requirement(analysis)
                if v:
                    violations.append(v)
                
                # Quality gates
                violations.extend(self.check_quality_gates())
        
        # Store violations
        for v in violations:
            self.context.violations.append(v)
            self.violation_history.append(v)
        
        return violations


class AnomalyDetector:
    """Detects anomalous patterns in execution"""
    
    def __init__(self):
        self.event_buffer = deque(maxlen=500)
        self.hook_timings: Dict[str, List[int]] = {}
        self.error_counts: Dict[str, int] = {}
        self.last_check = time.time()
    
    def add_event(self, event: Dict):
        self.event_buffer.append(event)
        
        # Track hook timings
        if event.get('type') == 'hook' and 'duration' in event:
            hook = event.get('hook', 'unknown')
            if hook not in self.hook_timings:
                self.hook_timings[hook] = []
            self.hook_timings[hook].append(event['duration'])
            # Keep last 100
            self.hook_timings[hook] = self.hook_timings[hook][-100:]
        
        # Track errors
        if event.get('type') == 'error' or event.get('status') in ['ERROR', 'BLOCKED']:
            source = event.get('source') or event.get('hook') or 'unknown'
            self.error_counts[source] = self.error_counts.get(source, 0) + 1
    
    def check_anomalies(self) -> List[Dict]:
        """Check for anomalous patterns"""
        anomalies = []
        now = time.time()
        
        # Check hook timing anomalies
        for hook, timings in self.hook_timings.items():
            if len(timings) >= 10:
                avg = sum(timings) / len(timings)
                recent = timings[-5:]
                recent_avg = sum(recent) / len(recent)
                
                # Spike detection
                if recent_avg > avg * 2:
                    anomalies.append({
                        'type': 'timing_spike',
                        'hook': hook,
                        'avg_ms': avg,
                        'recent_avg_ms': recent_avg,
                        'severity': 'warn'
                    })
        
        # Check error clustering
        for source, count in self.error_counts.items():
            if count >= 5:
                anomalies.append({
                    'type': 'error_cluster',
                    'source': source,
                    'count': count,
                    'severity': 'error'
                })
        
        # Reset counters periodically
        if now - self.last_check > 300:  # 5 minutes
            self.error_counts = {}
            self.last_check = now
        
        return anomalies


class LogManager:
    """Manages log storage, rotation, and archival"""
    
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    RETENTION_DAYS = 30
    
    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / 'archive').mkdir(exist_ok=True)
        (LOG_DIR / 'sessions').mkdir(exist_ok=True)
    
    def write_log(self, path: Path, entry: Dict):
        """Write entry to log file with rotation"""
        if path.exists() and path.stat().st_size > self.MAX_LOG_SIZE:
            self._rotate(path)
        
        with open(path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _rotate(self, path: Path):
        """Rotate log file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_path = LOG_DIR / 'archive' / f'{path.stem}_{timestamp}.jsonl'
        path.rename(archive_path)
        
        # Compress old archives
        self._compress_old_archives()
    
    def _compress_old_archives(self):
        """Compress archives older than 1 day"""
        import gzip
        import shutil
        
        cutoff = datetime.now() - timedelta(days=1)
        archive_dir = LOG_DIR / 'archive'
        
        for f in archive_dir.glob('*.jsonl'):
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                with open(f, 'rb') as src:
                    with gzip.open(f'{f}.gz', 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                f.unlink()
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        cutoff = datetime.now() - timedelta(days=self.RETENTION_DAYS)
        archive_dir = LOG_DIR / 'archive'
        
        for f in archive_dir.glob('*'):
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                f.unlink()


class MonitorAgent:
    """
    The impartial observer agent.
    Watches all activity and enforces protocol usage.
    """
    
    def __init__(self):
        self.enforcer = ProtocolEnforcer()
        self.anomaly_detector = AnomalyDetector()
        self.log_manager = LogManager()
        self.running = False
        self._last_position = 0
    
    def process_event(self, event: Dict) -> Dict[str, Any]:
        """Process single event through all checks"""
        result = {
            'violations': [],
            'anomalies': [],
            'action': None,
            'message': None
        }
        
        # Enforcement checks
        violations = self.enforcer.process_event(event)
        result['violations'] = [v.__dict__ for v in violations]
        
        # Anomaly detection
        self.anomaly_detector.add_event(event)
        anomalies = self.anomaly_detector.check_anomalies()
        result['anomalies'] = anomalies
        
        # Determine action
        for v in violations:
            if v.action_taken == Action.STOP:
                result['action'] = 'STOP'
                result['message'] = f"[MONITOR] STOPPING: {v.rule} - {v.message}"
                break
            elif v.action_taken == Action.ASK and result['action'] != 'STOP':
                result['action'] = 'ASK'
                result['message'] = f"[MONITOR] CLARIFICATION NEEDED: {v.message}"
        
        # Log violations
        for v in violations:
            self.log_manager.write_log(ENFORCEMENT_LOG, {
                'timestamp': v.timestamp,
                'severity': v.severity.value,
                'rule': v.rule,
                'message': v.message,
                'context': v.context,
                'action': v.action_taken.value
            })
        
        # Log anomalies
        for a in anomalies:
            self.log_manager.write_log(ANOMALY_LOG, {
                'timestamp': int(time.time() * 1000),
                **a
            })
        
        return result
    
    def watch_logs(self):
        """Watch log file for new entries"""
        self.running = True
        
        while self.running:
            try:
                if MONITOR_LOG.exists():
                    with open(MONITOR_LOG, 'r') as f:
                        f.seek(self._last_position)
                        for line in f:
                            if line.strip():
                                try:
                                    event = json.loads(line)
                                    result = self.process_event(event)
                                    
                                    if result['action'] == 'STOP':
                                        self._emit_stop_signal(result['message'])
                                    elif result['action'] == 'ASK':
                                        self._emit_clarification(result['message'])
                                        
                                except json.JSONDecodeError:
                                    pass
                        
                        self._last_position = f.tell()
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"Monitor error: {e}", file=sys.stderr)
                time.sleep(1)
    
    def _emit_stop_signal(self, message: str):
        """Emit stop signal to Claude Code"""
        signal = {
            'type': 'monitor_signal',
            'action': 'STOP',
            'message': message,
            'timestamp': int(time.time() * 1000)
        }
        self.log_manager.write_log(MONITOR_LOG, signal)
        print(f"\033[91m{message}\033[0m", file=sys.stderr)
    
    def _emit_clarification(self, message: str):
        """Emit clarification request"""
        signal = {
            'type': 'monitor_signal',
            'action': 'ASK',
            'message': message,
            'timestamp': int(time.time() * 1000)
        }
        self.log_manager.write_log(MONITOR_LOG, signal)
        print(f"\033[93m{message}\033[0m", file=sys.stderr)
    
    def get_status(self) -> Dict:
        """Get current monitor status"""
        return {
            'running': self.running,
            'context': {
                'complexity': self.enforcer.context.complexity_score,
                'orchestrator_active': self.enforcer.context.orchestrator_active,
                'active_agents': self.enforcer.context.active_agents,
                'hooks_executed': len(self.enforcer.context.hooks_executed),
                'violations': len(self.enforcer.context.violations)
            },
            'violation_count': len(self.enforcer.violation_history),
            'anomaly_detector': {
                'events_buffered': len(self.anomaly_detector.event_buffer),
                'error_sources': len(self.anomaly_detector.error_counts)
            }
        }


def main():
    """Run monitor agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Protocol Monitor Agent')
    parser.add_argument('--watch', action='store_true', help='Watch logs continuously')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--analyze', type=str, help='Analyze a prompt')
    args = parser.parse_args()
    
    monitor = MonitorAgent()
    
    if args.status:
        print(json.dumps(monitor.get_status(), indent=2))
    elif args.analyze:
        analysis = monitor.enforcer.analyze_prompt(args.analyze)
        print(json.dumps(analysis, indent=2))
    elif args.watch:
        print("Monitor Agent started. Watching logs...")
        monitor.watch_logs()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
