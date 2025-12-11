# Quick Start Guide

Get up and running with Claude Bootstrap Protocol in 5 minutes.

## Prerequisites

- Python 3.8+ installed (for hooks)
- Claude Code installed
- Node.js 18+ (only if using MCP memory server)

## Step 1: Copy Protocol Files

```bash
# Clone the repository
git clone https://github.com/z3r0-c001/Claude_Protocol.git

# Copy to your project
cp -r Claude_Protocol/.claude /path/to/your/project/
cp Claude_Protocol/CLAUDE.md /path/to/your/project/
```

## Step 2: Set Permissions

```bash
cd /path/to/your/project
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py
```

## Step 3: Initialize

```bash
# Start Claude Code
claude

# Run initialization
/proto-init
```

Answer the interactive questions:
1. New or existing project?
2. Project name and description
3. Tech stack
4. Memory preferences (JSON or SQLite)

## Step 4: Verify

```bash
# Check status
/proto-status

# Run validation
/validate
```

## You're Ready!

### Quick Commands

| Command | Purpose |
|---------|---------|
| `/feature <desc>` | Implement a feature |
| `/fix <issue>` | Fix a bug |
| `/test` | Run tests |
| `/commit <msg>` | Commit changes |
| `/remember <cat> <text>` | Save to memory |
| `/recall <topic>` | Search memory |
| `/leftoff` | Save session for later |
| `/resume` | Resume saved session |

### Example Session

```
You: /feature Add user authentication with JWT

Claude: I'll implement JWT authentication. Let me first explore
the existing codebase to understand the patterns...

[Claude reads files, plans implementation, writes code]

Claude: I've implemented JWT authentication:
- Created auth middleware in src/middleware/auth.ts
- Added login endpoint in src/routes/auth.ts
- Added JWT utilities in src/utils/jwt.ts

Running security scan on authentication code...
Running test coverage check...

All quality gates passed.
```

## Next Steps

1. **Read the docs:**
   - [COMMANDS.md](./COMMANDS.md) - All available commands
   - [AGENTS.md](./AGENTS.md) - Specialized agents
   - [CONFIGURATION.md](./CONFIGURATION.md) - Customization

2. **Customize:**
   - Edit `CLAUDE.md` for project-specific instructions
   - Add custom hooks in `.claude/hooks/`
   - Create custom skills in `.claude/skills/`

3. **Use memory:**
   ```
   /remember conventions We use camelCase for variables
   /remember architecture API follows REST with JSON:API spec
   /recall authentication
   ```

## Optional: Enable Persistent Memory

For cross-session memory persistence, set up the MCP server:

```bash
# Copy MCP config
cp Claude_Protocol/.mcp.json /path/to/your/project/

# Build memory server
cd /path/to/your/project/.claude/mcp/memory-server
npm install && npm run build
```

After setup, restart Claude Code to enable memory commands (`/remember`, `/recall`).

## Troubleshooting

### Hooks not running?
- Verify: `chmod +x .claude/hooks/*.sh && chmod +x .claude/hooks/*.py`
- Check settings.json is valid JSON

### MCP tools not available? (if using memory server)
- Restart Claude Code after installation
- Check: `node .claude/mcp/memory-server/dist/index.js`

### More help?
- See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Run `/proto-status` for diagnostics
