# Installation Guide

Complete installation guide for Claude Bootstrap Protocol.

## Prerequisites

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 9.0.0 or higher
- **Python**: Version 3.8 or higher (for PreToolUse hooks)
- **Claude Code**: Latest version installed

### Check Prerequisites

```bash
node --version     # Should be v18.0.0+
npm --version      # Should be 9.0.0+
python3 --version  # Should be 3.8+
claude --version   # Verify Claude Code is installed
```

## Installation Methods

### Method 1: Copy to Existing Project

Copy the protocol files to your project root:

```bash
# Clone or download the protocol
git clone https://github.com/z3r0-c001/Claude_Protocol.git

# Copy to your project
cp -r Claude_Protocol/.claude /path/to/your/project/
cp Claude_Protocol/.mcp.json /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/
```

### Method 2: Initialize New Project

```bash
# Create project directory
mkdir my-project && cd my-project

# Copy protocol
cp -r /path/to/Claude_Protocol/.claude .
cp /path/to/Claude_Protocol/.mcp.json .
cp /path/to/Claude_Protocol/CLAUDE.md .

# Initialize with Claude Code
claude
# Then run: /proto-init
```

## Build the MCP Memory Server

The MCP server provides persistent memory across sessions.

```bash
cd .claude/mcp/memory-server
npm install
npm run build
```

### Verify Build

```bash
ls dist/index.js  # Should exist after build
```

### Expected Output

```
added 15 packages in 2s
```

## Set Hook Permissions

Make hook scripts executable:

```bash
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py
```

## Verify Installation

### 1. Check File Structure

```bash
ls -la .claude/
```

Expected directories:
- `agents/`
- `commands/`
- `hooks/`
- `mcp/`
- `memory/`
- `skills/`
- `settings.json`

### 2. Validate JSON Files

```bash
# Check settings.json
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "settings.json: OK"

# Check .mcp.json
python3 -c "import json; json.load(open('.mcp.json'))" && echo ".mcp.json: OK"

# Check skill-rules.json
python3 -c "import json; json.load(open('.claude/skills/skill-rules.json'))" && echo "skill-rules.json: OK"
```

### 3. Test MCP Server

```bash
cd .claude/mcp/memory-server
node dist/index.js
# Should output: "Claude Memory Server running on stdio"
# Press Ctrl+C to exit
```

## Initialize Protocol

Start Claude Code and run initialization:

```bash
claude
```

Then in Claude Code:

```
/proto-init
```

This will:
1. Ask about your project (new or existing)
2. Gather project details
3. Configure memory preferences
4. Generate project-specific settings
5. Validate all files

## Post-Installation

### Restart Claude Code

After installation, restart Claude Code to load:
- MCP servers from `.mcp.json`
- Hooks from `.claude/settings.json`
- Commands from `.claude/commands/`

### Verify MCP Connection

In Claude Code, check MCP tools are available:

```
What MCP tools are available?
```

You should see:
- `mcp__memory__memory_read`
- `mcp__memory__memory_write`
- `mcp__memory__memory_search`
- `mcp__memory__memory_list`
- `mcp__memory__memory_delete`
- `mcp__memory__memory_prune`

## Directory Structure After Installation

```
your-project/
├── CLAUDE.md                    # Project documentation
├── .mcp.json                    # MCP server configuration
├── .claude/
│   ├── settings.json            # Hooks and permissions
│   ├── agents/
│   │   ├── core/
│   │   │   ├── architect.md
│   │   │   ├── research-analyzer.md
│   │   │   └── performance-analyzer.md
│   │   └── quality/
│   │       ├── laziness-destroyer.md
│   │       ├── hallucination-checker.md
│   │       ├── security-scanner.md
│   │       ├── fact-checker.md
│   │       ├── reviewer.md
│   │       ├── tester.md
│   │       └── test-coverage-enforcer.md
│   ├── commands/
│   │   ├── proto-init.md
│   │   ├── leftoff.md          # Session save
│   │   ├── resume.md           # Session restore
│   │   └── ... (18 total)
│   ├── hooks/
│   │   ├── pretool-laziness-check.py    # BLOCKING: stops lazy code
│   │   ├── pretool-hallucination-check.py # BLOCKING: verifies packages
│   │   ├── dangerous-command-check.py   # BLOCKING: stops dangerous cmds
│   │   └── ... (24 total)
│   ├── skills/
│   │   ├── skill-rules.json
│   │   ├── quality-control/
│   │   ├── workflow/
│   │   └── ... (6 total)
│   ├── mcp/
│   │   └── memory-server/
│   │       ├── package.json
│   │       ├── tsconfig.json
│   │       ├── src/
│   │       └── dist/           # Created after build
│   └── memory/                  # Created at runtime
└── scripts/
    ├── validate-all.sh
    ├── session-init.sh
    ├── protocol-init.sh
    └── audit.sh
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

1. Run `/proto-status` to check protocol health
2. Run `/validate` to run full validation suite
3. Try `/remember architecture My project uses...` to test memory
4. Read [COMMANDS.md](./COMMANDS.md) for all available commands
