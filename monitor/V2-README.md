# Protocol V2 - Evaluator LLM System for Claude Code

A comprehensive enforcement system that ensures Claude Code:
- Uses orchestration for complex tasks
- Invokes proper agents for domain-specific work  
- Runs quality gates before completing
- Never produces placeholder or incomplete code
- **Real-time monitoring dashboard with popup window**

## Quick Start

```bash
# Install the monitor
cd monitor
./install.sh

# Launch Claude Code with monitoring popup
claude-monitor
```

The dashboard will automatically open in your browser when you start `claude-monitor`.

## Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  LOG EMITTER → Sends to Dashboard (popup window)            │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  ENFORCEMENT HOOK (UserPromptSubmit)                        │
│  • Analyzes complexity (1-5 scale)                          │
│  • Detects collaboration phrases                            │
│  • Identifies domains (security, architecture, etc.)        │
│  • Injects orchestration requirements                       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR AGENT                                         │
│  • Creates execution plan                                   │
│  • Selects and invokes agents                              │
│  • Manages sub-agent spawning                              │
│  • Synthesizes results                                      │
└─────────────────────────────────────────────────────────────┘
    │
    ├── architect (plan → execute)
    ├── security-scanner
    ├── tester
    └── [other domain agents]
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  QUALITY GATES (Stop hooks)                                 │
│  • laziness-check: No TODOs, FIXMEs, placeholders          │
│  • honesty-check: Verify files exist, imports valid        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  MONITOR DASHBOARD (real-time popup)                        │
│  • Shows all activity with hierarchy                        │
│  • ORCH → AGENT → SUB/HOOK/TOOL                            │
│  • Blocked operations highlighted in red                    │
│  • Statistics and enforcement tracking                      │
└─────────────────────────────────────────────────────────────┘
```

## Monitor Dashboard

The dashboard is a popup window that opens automatically when you use `claude-monitor`:

**Features:**
- Real-time log streaming via WebSocket
- Hierarchy display: Orchestrator → Agent → SubAgent/Hook/Tool
- Color-coded badges for each type
- Filter by type (ORCH, AGENT, HOOK, TOOL, ERROR)
- Search functionality
- Execution tree visualization
- Enforcement tracking panel
- Statistics panel

**Tabs:**
- **Live Logs** - Real-time stream of all activity
- **Execution Tree** - Visual hierarchy of orchestrator → agents → subagents
- **Enforcement** - Quality gate status and blocked operations
- **Statistics** - Counts of orchestrations, agents, hooks, blocks

**Badge Colors:**
| Badge | Color | Meaning |
|-------|-------|---------|
| ORCH | Purple | Orchestrator |
| AGENT | Amber | Primary agent |
| SUB | Orange | Sub-agent |
| HOOK | Violet | Hook execution |
| TOOL | Green | Tool call |
| ERROR | Red | Blocked/failed |

## Installation

1. Copy to your project:
```bash
cp -r protocol-v2/.claude/agents your-project/.claude/
cp -r protocol-v2/.claude/hooks your-project/.claude/
cp -r protocol-v2/.claude/config your-project/.claude/
cp protocol-v2/settings.json your-project/.claude/settings.json
```

2. Verify structure:
```
your-project/.claude/
├── settings.json
├── agents/
│   ├── core/
│   │   └── codebase-analyzer.md
│   ├── domain/
│   │   ├── architect.md
│   │   ├── security-scanner.md
│   │   └── tester.md
│   ├── quality/
│   │   ├── laziness-destroyer.md
│   │   ├── honesty-evaluator.md
│   │   └── reviewer.md
│   └── workflow/
│       └── orchestrator.md
├── hooks/
│   ├── enforcement-hook.py
│   ├── laziness-check.py
│   ├── hallucination-check.py
│   └── stop/
│       ├── laziness-check.sh
│       └── honesty-check.sh
└── config/
    └── enforcement-rules.json
```

## Hook Execution Order

### UserPromptSubmit (runs on every prompt)
1. `enforcement-hook.py` - Analyzes and injects requirements (MUST run first)
2. `context-loader.py` - Loads project context
3. `skill-activation.py` - Suggests relevant skills

### PreToolUse (runs before each tool)
1. `agent-plan-enforcer.py` - Verifies plan exists
2. `laziness-check.py` - Blocks placeholder code
3. `hallucination-check.py` - Verifies files/packages exist
4. `dangerous-command-check.py` - Blocks dangerous bash commands

### PostToolUse (runs after each tool)
1. `file-tracker.py` - Tracks modifications
2. `quality-check.py` - Validates output quality

### Stop (runs before final response)
1. `laziness-check.sh` - Final scan for placeholders
2. `honesty-check.sh` - Verify all claims

## Agents

### Workflow
- **orchestrator** - Master coordinator for complex tasks

### Domain
- **architect** - System design and refactoring
- **security-scanner** - Vulnerability detection
- **tester** - Test creation and validation

### Quality
- **laziness-destroyer** - Blocks incomplete code
- **honesty-evaluator** - Verifies claims
- **reviewer** - Code review

### Core
- **codebase-analyzer** - Deep structural analysis

## Trigger Phrases

The system auto-triggers orchestration when detecting:

**Collaboration signals:**
- "can we", "let's", "how do we", "help me"
- "figure out", "work on", "what if we"

**Planning signals:**
- "plan", "design", "architect", "approach"
- "strategy", "how should", "best way to"

**Complexity signals:**
- "and then", "after that", "multiple"
- "across", "entire", "all the", "whole"

## Configuration

Edit `.claude/config/enforcement-rules.json`:

```json
{
  "enforcement": {
    "enforce_orchestration": true,
    "enforce_agents": true,
    "enforce_plan_mode": true,
    "enforce_quality_gates": true
  },
  "thresholds": {
    "complexity_threshold": 3
  }
}
```

## How It Works

1. **User submits prompt** → enforcement-hook analyzes

2. **Complexity ≥ 3 or collaboration detected** → Injects:
   ```
   ⚠️ ORCHESTRATION REQUIRED
   You MUST use Task tool to invoke 'orchestrator' agent.
   ```

3. **Orchestrator invoked** → Creates plan, waits for approval

4. **Plan approved** → Orchestrator invokes agents in sequence

5. **Each agent output** → Quality hooks validate

6. **Before completion** → Stop hooks run final checks

7. **Any check fails** → BLOCKED, must fix before continuing

## Bypass

For simple tasks, bypass with phrases like:
- "just quickly check..."
- "simple question..."
- "skip enforcement..."

## Files Reference

| File | Purpose |
|------|---------|
| `enforcement-hook.py` | Injects orchestration requirements |
| `laziness-check.py` | Blocks placeholder code in Write/Edit |
| `hallucination-check.py` | Verifies files/packages exist |
| `laziness-check.sh` | Final scan of all modified files |
| `honesty-check.sh` | Verifies all claims are true |
| `orchestrator.md` | Master coordinator agent |
| `architect.md` | Architecture and design agent |
| `security-scanner.md` | Security vulnerability agent |
| `tester.md` | Testing and coverage agent |
| `enforcement-rules.json` | Configuration |
