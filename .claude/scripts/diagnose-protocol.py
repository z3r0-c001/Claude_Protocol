#!/usr/bin/env python3
"""
diagnose-protocol.py - Identify what's broken in Claude Protocol

Run: python3 .claude/scripts/diagnose-protocol.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Colors (direct ANSI, no imports)
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def ok(msg): print(f"{GREEN}✓{RESET} {msg}")
def fail(msg): print(f"{RED}✗{RESET} {msg}")
def warn(msg): print(f"{YELLOW}⚠{RESET} {msg}")
def info(msg): print(f"{BLUE}ℹ{RESET} {msg}")

def section(title):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

def main():
    project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
    claude_dir = project_dir / '.claude'
    
    print(f"\n{BOLD}CLAUDE PROTOCOL DIAGNOSTIC{RESET}")
    print(f"Project: {project_dir}\n")
    
    issues = []
    
    # =========================================================================
    # 1. BASIC STRUCTURE
    # =========================================================================
    section("1. Basic Structure")
    
    required_files = [
        ('CLAUDE.md', project_dir / 'CLAUDE.md'),
        ('settings.json', claude_dir / 'settings.json'),
        ('health-check.py', claude_dir / 'scripts' / 'health-check.py'),
        ('run-hook.sh', claude_dir / 'hooks' / 'run-hook.sh'),
        ('models.json', claude_dir / 'config' / 'models.json'),
    ]
    
    for name, path in required_files:
        if path.exists():
            ok(f"{name} exists")
        else:
            fail(f"{name} MISSING: {path}")
            issues.append(f"Missing: {name}")
    
    # =========================================================================
    # 2. SETTINGS.JSON VALIDATION
    # =========================================================================
    section("2. Settings Validation")
    
    settings_path = claude_dir / 'settings.json'
    if settings_path.exists():
        try:
            with open(settings_path) as f:
                settings = json.load(f)
            ok("settings.json is valid JSON")
            
            # Check hooks structure
            hooks = settings.get('hooks', {})
            if not hooks:
                fail("No hooks defined in settings.json")
                issues.append("No hooks configured")
            else:
                ok(f"Hooks configured: {list(hooks.keys())}")
                
                # Validate each hook type
                for hook_type, hook_list in hooks.items():
                    if not isinstance(hook_list, list):
                        fail(f"{hook_type}: Expected array, got {type(hook_list).__name__}")
                        issues.append(f"Invalid hook format: {hook_type}")
                        continue
                    
                    for i, hook in enumerate(hook_list):
                        if 'matcher' not in hook:
                            fail(f"{hook_type}[{i}]: Missing 'matcher' field")
                            issues.append(f"{hook_type}[{i}] missing matcher")
                        if 'hooks' not in hook:
                            fail(f"{hook_type}[{i}]: Missing 'hooks' array")
                            issues.append(f"{hook_type}[{i}] missing hooks array")
                        else:
                            ok(f"{hook_type}[{i}]: Valid structure")
            
            # Check if hooks disabled
            if settings.get('hooksDisabled', False):
                warn("hooksDisabled is TRUE - hooks won't run!")
                issues.append("Hooks are disabled")
            else:
                ok("Hooks are enabled")
                
        except json.JSONDecodeError as e:
            fail(f"settings.json is INVALID JSON: {e}")
            issues.append("Invalid settings.json")
    
    # =========================================================================
    # 3. HOOK SCRIPTS
    # =========================================================================
    section("3. Hook Scripts")
    
    hooks_dir = claude_dir / 'hooks'
    if hooks_dir.exists():
        # Check run-hook.sh
        run_hook = hooks_dir / 'run-hook.sh'
        if run_hook.exists():
            # Check if executable
            if os.access(run_hook, os.X_OK):
                ok("run-hook.sh is executable")
            else:
                warn("run-hook.sh is NOT executable - run: chmod +x .claude/hooks/run-hook.sh")
                issues.append("run-hook.sh not executable")
            
            # Check shebang
            with open(run_hook) as f:
                first_line = f.readline()
            if first_line.startswith('#!/'):
                ok(f"run-hook.sh has shebang: {first_line.strip()}")
            else:
                warn("run-hook.sh missing shebang")
        
        # Check individual hook files
        hook_files = [
            'laziness-check.sh',
            'pretool-laziness-check.py', 
            'model-audit.py',
            'colors.py',
        ]
        
        for hf in hook_files:
            hp = hooks_dir / hf
            if hp.exists():
                ok(f"{hf} exists")
                # Test if Python files are syntactically valid
                if hf.endswith('.py'):
                    result = subprocess.run(
                        ['python3', '-m', 'py_compile', str(hp)],
                        capture_output=True
                    )
                    if result.returncode == 0:
                        ok(f"{hf} syntax OK")
                    else:
                        fail(f"{hf} has syntax errors")
                        issues.append(f"{hf} syntax error")
            else:
                warn(f"{hf} not found")
    
    # =========================================================================
    # 4. COLOR OUTPUT TEST
    # =========================================================================
    section("4. Color Output Test")
    
    print("Direct ANSI test:")
    print(f"  {RED}RED{RESET} {GREEN}GREEN{RESET} {YELLOW}YELLOW{RESET} {BLUE}BLUE{RESET}")
    
    # Test colors.py
    colors_py = hooks_dir / 'colors.py'
    if colors_py.exists():
        result = subprocess.run(
            ['python3', str(colors_py)],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"colors.py stdout: {result.stdout[:100]}")
        if result.stderr:
            print(f"colors.py stderr: {result.stderr[:100]}")
        if not result.stdout and not result.stderr:
            warn("colors.py produced no output")
    
    # Test via run-hook.sh
    info("Testing run-hook.sh output routing...")
    result = subprocess.run(
        ['bash', str(hooks_dir / 'run-hook.sh'), 'model-audit.py'],
        capture_output=True,
        text=True,
        env={**os.environ, 'CLAUDE_PROJECT_DIR': str(project_dir)}
    )
    print(f"  stdout: {result.stdout[:200] if result.stdout else '(empty)'}")
    print(f"  stderr: {result.stderr[:200] if result.stderr else '(empty)'}")
    print(f"  return: {result.returncode}")
    
    # =========================================================================
    # 5. HEALTH CHECK TEST
    # =========================================================================
    section("5. Health Check Test")
    
    health_check = claude_dir / 'scripts' / 'health-check.py'
    if health_check.exists():
        result = subprocess.run(
            ['python3', str(health_check), '--force', '--no-network', '--no-ack'],
            capture_output=True,
            text=True,
            env={**os.environ, 'CLAUDE_PROJECT_DIR': str(project_dir)}
        )
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"stdout:\n{result.stdout}")
        if result.stderr:
            print(f"stderr:\n{result.stderr}")
    
    # =========================================================================
    # 6. LAZINESS CHECK TEST
    # =========================================================================
    section("6. Laziness Check Analysis")
    
    laziness_py = hooks_dir / 'pretool-laziness-check.py'
    if laziness_py.exists():
        with open(laziness_py) as f:
            content = f.read()
        
        # Check what patterns it's looking for
        if 'TODO' in content:
            info("Laziness check looks for TODO patterns")
        if 'GENERATOR' in content or 'template' in content.lower():
            ok("Laziness check has template/generator exceptions")
        else:
            warn("Laziness check may NOT have template/generator exceptions")
            issues.append("Laziness check needs template exceptions")
        
        # Check for file path exceptions
        if 'generator' in content.lower() or '_gen' in content:
            ok("Has generator file path exceptions")
        else:
            warn("No generator file path exceptions found")
    
    # =========================================================================
    # 7. AGENT CONFIGURATION
    # =========================================================================
    section("7. Agent Configuration")
    
    agents_dir = claude_dir / 'agents'
    if agents_dir.exists():
        agent_files = list(agents_dir.glob('**/*.md'))
        agent_files = [a for a in agent_files if 'AGENT_PROTOCOL' not in str(a)]
        
        ok(f"Found {len(agent_files)} agents")
        
        # Check orchestrator
        orchestrator = agents_dir / 'workflow' / 'orchestrator.md'
        if orchestrator.exists():
            with open(orchestrator) as f:
                content = f.read()
            if 'model_tier' in content:
                ok("Orchestrator has model_tier support")
            else:
                warn("Orchestrator missing model_tier")
            if 'Task' in content:
                ok("Orchestrator uses Task tool for sub-agents")
            else:
                warn("Orchestrator may not invoke sub-agents via Task")
        else:
            fail("Orchestrator agent not found")
            issues.append("Missing orchestrator")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    section("SUMMARY")
    
    if issues:
        print(f"{RED}{BOLD}Found {len(issues)} issue(s):{RESET}\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\n{YELLOW}Run the suggested fixes above.{RESET}")
        return 1
    else:
        print(f"{GREEN}{BOLD}All checks passed!{RESET}")
        print("\nIf things still don't work, the issue may be:")
        print("  - Claude Code not reading CLAUDE.md startup instruction")
        print("  - Hooks running but output not visible in UI")
        print("  - Terminal not supporting ANSI colors")
        return 0

if __name__ == "__main__":
    sys.exit(main())
