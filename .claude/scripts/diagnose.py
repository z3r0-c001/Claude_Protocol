#!/usr/bin/env python3
"""
Claude Protocol Diagnostic Tool
Identifies issues with hooks, colors, agents, and configuration.
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class C:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def ok(msg): print(f"{C.GREEN}✓{C.RESET} {msg}")
def fail(msg): print(f"{C.RED}✗{C.RESET} {msg}")
def warn(msg): print(f"{C.YELLOW}⚠{C.RESET} {msg}")
def info(msg): print(f"{C.CYAN}ℹ{C.RESET} {msg}")
def header(msg): print(f"\n{C.BOLD}{C.BLUE}{'═'*60}{C.RESET}\n{C.BOLD}{msg}{C.RESET}\n{C.BOLD}{C.BLUE}{'═'*60}{C.RESET}")

def find_project_root():
    """Find .claude directory"""
    current = Path.cwd()
    for path in [current] + list(current.parents):
        if (path / '.claude').is_dir():
            return path
    return None

def check_directory_structure(root):
    """Check required directories and files exist"""
    header("1. DIRECTORY STRUCTURE")
    
    required = [
        '.claude/settings.json',
        '.claude/hooks/run-hook.sh',
        '.claude/hooks/colors.py',
        '.claude/scripts/health-check.py',
        '.claude/agents/AGENT_PROTOCOL.md',
        '.claude/config/models.json',
        'CLAUDE.md',
    ]
    
    optional = [
        '.claude/config/model-routing.json',
        '.claude/config/local-state.json',
        '.claude/mcp/memory-server/dist/index.js',
    ]
    
    all_ok = True
    for f in required:
        path = root / f
        if path.exists():
            ok(f"{f}")
        else:
            fail(f"{f} - MISSING")
            all_ok = False
    
    print()
    for f in optional:
        path = root / f
        if path.exists():
            ok(f"{f} (optional)")
        else:
            warn(f"{f} (optional) - not found")
    
    return all_ok

def check_settings_json(root):
    """Validate settings.json structure"""
    header("2. SETTINGS.JSON VALIDATION")
    
    settings_path = root / '.claude/settings.json'
    if not settings_path.exists():
        fail("settings.json not found")
        return False
    
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        ok("Valid JSON")
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON: {e}")
        return False
    
    # Check hooks structure
    hooks = settings.get('hooks', {})
    if not hooks:
        warn("No hooks defined")
        return True
    
    hook_types = ['UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'Stop', 'SubagentStop']
    errors = []
    
    for hook_type in hook_types:
        if hook_type not in hooks:
            continue
        
        hook_list = hooks[hook_type]
        if not isinstance(hook_list, list):
            errors.append(f"{hook_type}: Expected array")
            continue
        
        for i, hook in enumerate(hook_list):
            if 'matcher' not in hook:
                errors.append(f"{hook_type}[{i}]: Missing 'matcher' field")
            if 'hooks' not in hook:
                errors.append(f"{hook_type}[{i}]: Missing 'hooks' array")
            elif not isinstance(hook.get('hooks'), list):
                errors.append(f"{hook_type}[{i}]: 'hooks' should be array")
    
    if errors:
        for e in errors:
            fail(e)
        return False
    else:
        ok("Hook structure valid")
        info(f"Hook types configured: {[h for h in hook_types if h in hooks]}")
        return True

def check_colors(root):
    """Test color output"""
    header("3. COLOR OUTPUT")
    
    # Test raw ANSI
    print(f"  Raw ANSI: {C.RED}RED{C.RESET} {C.GREEN}GREEN{C.RESET} {C.YELLOW}YELLOW{C.RESET} {C.BLUE}BLUE{C.RESET}")
    
    # Test colors.py module
    colors_path = root / '.claude/hooks/colors.py'
    if not colors_path.exists():
        fail("colors.py not found")
        return False
    
    try:
        spec = importlib.util.spec_from_file_location("colors", colors_path)
        colors_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(colors_module)
        
        # Test functions if they exist
        if hasattr(colors_module, 'green'):
            print(f"  colors.py: {colors_module.green('GREEN')} {colors_module.red('RED')} {colors_module.yellow('YELLOW')}")
            ok("colors.py module works")
        else:
            warn("colors.py missing expected functions")
    except Exception as e:
        fail(f"colors.py error: {e}")
        return False
    
    # Check if terminal supports colors
    if os.environ.get('TERM') in ['dumb', None, '']:
        warn(f"TERM={os.environ.get('TERM')} may not support colors")
    else:
        ok(f"TERM={os.environ.get('TERM')}")
    
    # Check NO_COLOR env
    if os.environ.get('NO_COLOR'):
        warn("NO_COLOR is set - colors disabled")
    
    return True

def check_hooks_execution(root):
    """Test if hooks can actually run"""
    header("4. HOOK EXECUTION")
    
    run_hook = root / '.claude/hooks/run-hook.sh'
    if not run_hook.exists():
        fail("run-hook.sh not found")
        return False
    
    # Check if executable
    if not os.access(run_hook, os.X_OK):
        warn("run-hook.sh not executable, attempting chmod")
        os.chmod(run_hook, 0o755)
    
    # Test running a simple hook
    test_hooks = [
        ('colors.py', 'Color module'),
        ('model-audit.py', 'Model audit'),
    ]
    
    for hook, desc in test_hooks:
        hook_path = root / f'.claude/hooks/{hook}'
        if not hook_path.exists():
            warn(f"{hook} not found")
            continue
        
        try:
            result = subprocess.run(
                ['bash', str(run_hook), hook],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'CLAUDE_PROJECT_DIR': str(root)}
            )
            
            if result.returncode == 0:
                ok(f"{hook} runs successfully")
                if result.stdout.strip():
                    print(f"    Output: {result.stdout.strip()[:100]}")
            else:
                fail(f"{hook} failed (exit {result.returncode})")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            fail(f"{hook} timed out")
        except Exception as e:
            fail(f"{hook} error: {e}")
    
    return True

def check_health_check(root):
    """Test health check script"""
    header("5. HEALTH CHECK SCRIPT")
    
    script = root / '.claude/scripts/health-check.py'
    if not script.exists():
        fail("health-check.py not found")
        return False
    
    try:
        result = subprocess.run(
            ['python3', str(script), '--force', '--no-network', '--no-ack'],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, 'CLAUDE_PROJECT_DIR': str(root)}
        )
        
        print(f"  Exit code: {result.returncode}")
        if result.stdout:
            for line in result.stdout.strip().split('\n')[:10]:
                print(f"    {line}")
        if result.stderr:
            print(f"  Stderr: {result.stderr.strip()[:200]}")
        
        if result.returncode == 0:
            ok("Health check runs")
        else:
            warn(f"Health check returned {result.returncode}")
        
        return True
    except subprocess.TimeoutExpired:
        fail("Health check timed out")
        return False
    except Exception as e:
        fail(f"Health check error: {e}")
        return False

def check_agents(root):
    """Check agent configuration"""
    header("6. AGENT CONFIGURATION")
    
    agents_dir = root / '.claude/agents'
    if not agents_dir.exists():
        fail("agents directory not found")
        return False
    
    agent_files = list(agents_dir.rglob('*.md'))
    agent_files = [f for f in agent_files if f.name != 'AGENT_PROTOCOL.md']
    
    info(f"Found {len(agent_files)} agent files")
    
    # Check frontmatter
    issues = []
    tier_counts = {'high': 0, 'standard': 0, 'fast': 0, 'missing': 0}
    
    for agent_file in agent_files:
        with open(agent_file) as f:
            content = f.read()
        
        if not content.startswith('---'):
            issues.append(f"{agent_file.name}: Missing frontmatter")
            continue
        
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append(f"{agent_file.name}: Invalid frontmatter")
            continue
        
        frontmatter = parts[1]
        
        if 'model:' not in frontmatter:
            issues.append(f"{agent_file.name}: Missing model field")
        
        if 'model_tier:' in frontmatter:
            for tier in ['high', 'standard', 'fast']:
                if f'model_tier: {tier}' in frontmatter:
                    tier_counts[tier] += 1
                    break
        else:
            tier_counts['missing'] += 1
    
    if issues:
        for issue in issues[:5]:
            warn(issue)
        if len(issues) > 5:
            warn(f"... and {len(issues) - 5} more issues")
    else:
        ok("All agents have valid frontmatter")
    
    print(f"\n  Tier distribution:")
    print(f"    High (Opus):     {tier_counts['high']}")
    print(f"    Standard (Sonnet): {tier_counts['standard']}")
    print(f"    Fast (Haiku):    {tier_counts['fast']}")
    if tier_counts['missing']:
        print(f"    Missing tier:    {tier_counts['missing']}")
    
    return len(issues) == 0

def check_laziness_hook(root):
    """Check laziness check configuration"""
    header("7. LAZINESS CHECK")
    
    laziness_hooks = [
        root / '.claude/hooks/laziness-check.sh',
        root / '.claude/hooks/pretool-laziness-check.py',
    ]
    
    for hook in laziness_hooks:
        if not hook.exists():
            warn(f"{hook.name} not found")
            continue
        
        with open(hook) as f:
            content = f.read()
        
        # Check for exclusion patterns
        if 'template' in content.lower() or 'generator' in content.lower() or 'TEMPLATE_MARKER' in content:
            ok(f"{hook.name} has template exclusions")
        else:
            warn(f"{hook.name} may need template exclusions")
        
        # Check for configurable patterns
        if 'LAZINESS_PATTERNS' in content or 'patterns' in content.lower():
            info(f"{hook.name} has configurable patterns")
    
    return True

def check_environment(root):
    """Check environment variables"""
    header("8. ENVIRONMENT")
    
    env_vars = {
        'CLAUDE_PROJECT_DIR': str(root),
        'TERM': os.environ.get('TERM', 'not set'),
        'NO_COLOR': os.environ.get('NO_COLOR', 'not set'),
        'SHELL': os.environ.get('SHELL', 'not set'),
    }
    
    for var, value in env_vars.items():
        if value and value != 'not set':
            ok(f"{var}={value}")
        else:
            info(f"{var}={value}")
    
    return True

def generate_fix_commands(root, issues):
    """Generate commands to fix issues"""
    header("RECOMMENDED FIXES")
    
    fixes = []
    
    # Always suggest these
    fixes.append(("Make hooks executable", 
        f"chmod +x {root}/.claude/hooks/*.sh {root}/.claude/hooks/*.py {root}/.claude/scripts/*.py"))
    
    fixes.append(("Test color output",
        f"python3 {root}/.claude/hooks/colors.py"))
    
    fixes.append(("Force health check",
        f"python3 {root}/.claude/scripts/health-check.py --force"))
    
    fixes.append(("Run diagnostic again",
        f"python3 {root}/.claude/scripts/diagnose.py"))
    
    for desc, cmd in fixes:
        print(f"\n{C.CYAN}{desc}:{C.RESET}")
        print(f"  {cmd}")

def main():
    print(f"\n{C.BOLD}{C.CYAN}╔════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}║        CLAUDE PROTOCOL DIAGNOSTIC TOOL                     ║{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}╚════════════════════════════════════════════════════════════╝{C.RESET}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    root = find_project_root()
    if not root:
        # Check if we're in the .claude directory
        if Path('.claude').exists():
            root = Path.cwd()
        elif os.environ.get('CLAUDE_PROJECT_DIR'):
            root = Path(os.environ['CLAUDE_PROJECT_DIR'])
        else:
            fail("Could not find project root (no .claude directory)")
            print("Run from project root or set CLAUDE_PROJECT_DIR")
            sys.exit(1)
    
    info(f"Project root: {root}")
    
    issues = []
    
    # Run all checks
    if not check_directory_structure(root):
        issues.append("directory_structure")
    
    if not check_settings_json(root):
        issues.append("settings_json")
    
    check_colors(root)
    check_hooks_execution(root)
    check_health_check(root)
    check_agents(root)
    check_laziness_hook(root)
    check_environment(root)
    
    generate_fix_commands(root, issues)
    
    # Summary
    header("SUMMARY")
    if not issues:
        ok("No critical issues found")
    else:
        fail(f"Found issues in: {', '.join(issues)}")
    
    print()

if __name__ == '__main__':
    main()
