# Installation Guide

Complete installation guide for Claude Bootstrap Protocol.

## Prerequisites

- **Python**: Version 3.8 or higher (for hooks)
- **Claude Code**: Latest version installed
- **Node.js**: Version 18.0.0 or higher (only if using MCP memory server)

### Check Prerequisites

```bash
python3 --version  # Should be 3.8+
claude --version   # Verify Claude Code is installed

# Only needed if using MCP memory server:
node --version     # Should be v18.0.0+
npm --version      # Should be 9.0.0+
```

## Installation Methods

### Method 1: Copy to Existing Project

Copy the protocol files to your project root:

```bash
# Clone or download the protocol
git clone https://github.com/z3r0-c001/Claude_Protocol.git

# Copy to your project
cp -r Claude_Protocol/.claude /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/
cp Claude_Protocol/.mcp.json /path/to/your/project/
```

### Method 2: Initialize New Project

```bash
# Create project directory
mkdir my-project && cd my-project

# Copy protocol
cp -r /path/to/Claude_Protocol/.claude .
cp /path/to/Claude_Protocol/CLAUDE.md .
cp /path/to/Claude_Protocol/.mcp.json .

# Initialize with Claude Code
claude
# Then run: /proto-init
```

## Set Hook Permissions

Make hook scripts executable:

```bash
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py
chmod +x scripts/*.sh
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
- `skills/`
- `settings.json`
- `mcp/` (optional - for memory server)

### 2. Validate JSON Files

```bash
# Check settings.json
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "settings.json: OK"

# Check skill-rules.json
python3 -c "import json; json.load(open('.claude/skills/skill-rules.json'))" && echo "skill-rules.json: OK"
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
- Hooks from `.claude/settings.json`
- Commands from `.claude/commands/`
- MCP servers from `.mcp.json` (if configured)

## Optional: Enable Persistent Memory (MCP Server)

The MCP memory server provides persistent memory across sessions. This is optional - the protocol works without it.

**MCP is set up automatically by `/proto-init`** when you choose to enable persistent memory. The initialization command will:
1. Copy the MCP configuration
2. Install and build the memory server
3. Verify the connection

No manual setup required.

## Directory Structure After Installation

```
your-project/
├── CLAUDE.md                    # Project documentation
├── .mcp.json                    # MCP server configuration (optional)
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
│   │   ├── bootstrap.md
│   │   ├── validate.md
│   │   └── ... (14 total)
│   ├── hooks/
│   │   ├── laziness-check.sh
│   │   ├── dangerous-command-check.sh
│   │   └── ... (13 total)
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
