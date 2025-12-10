---
description: List all Claude Bootstrap Protocol commands (use /help for built-in commands)
---

# PROTO-HELP - Protocol Commands

Display all Claude Bootstrap Protocol commands. For built-in Claude Code commands, use `/help`.

```bash
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                CLAUDE BOOTSTRAP PROTOCOL - COMMANDS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "SETUP & INITIALIZATION"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  /proto-init        Initialize protocol + auto-bootstrap"
echo "  /bootstrap         Generate CLAUDE.md, skills, agents, hooks"
echo "  /proto-status      Show protocol state and health"
echo "  /proto-help        Show this help message"
echo ""
echo "DEVELOPMENT WORKFLOWS"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  /feature <desc>    Implement a new feature (full TDD workflow)"
echo "  /fix <issue>       Fix a bug or issue"
echo "  /refactor <target> Refactor code with full agent pipeline"
echo "  /test [pattern]    Run project tests"
echo "  /lint [--fix]      Run linters (--fix to auto-fix)"
echo "  /search <query>    Search codebase for code/patterns"
echo ""
echo "QUALITY & GIT"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  /validate          Run full validation suite"
echo "  /commit <msg>      Sanitize and commit changes"
echo "  /pr [title]        Create pull request with checks"
echo ""
echo "MEMORY"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  /remember <what>   Save to persistent memory"
echo "  /recall <topic>    Search memory for past context"
echo ""
echo "DOCUMENTATION"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  /docs              Generate project documentation"
echo "  /update-docs       Update existing docs to match code"
echo ""
echo "THINKING TRIGGERS"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  think              Basic planning"
echo "  think hard         Detailed design"
echo "  think harder       Complex problem solving"
echo "  ultrathink         Architecture decisions"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  For built-in Claude Code commands, use: /help"
echo "═══════════════════════════════════════════════════════════════════════════════"
```

## Output Format

Present the commands in a clean, readable format. Group by category.

If user asks about a specific command, provide detailed usage:

```markdown
## /feature <description>

Implements a new feature using the full TDD workflow.

### Usage
```
/feature add user authentication
/feature implement dark mode toggle
```

### Workflow
1. Load memory and context
2. Design with `ultrathink`
3. Write tests first
4. Implement feature
5. Run sanitization
6. Commit

### See Also
- /fix - for bug fixes
- /test - to run tests only
```
