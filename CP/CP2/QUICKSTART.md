# Claude Bootstrap Protocol - Quick Start Guide

## Installation

### Option 1: Copy to Existing Project

```bash
# Clone the protocol
git clone <protocol-repo-url> /tmp/claude-protocol

# Copy to your project
cp -r /tmp/claude-protocol/.claude /path/to/your/project/
cp -r /tmp/claude-protocol/.claude-plugin /path/to/your/project/
cp /tmp/claude-protocol/.mcp.json /path/to/your/project/

# Optional: Copy templates
cp /tmp/claude-protocol/gitignore-template.txt /path/to/your/project/
cp /tmp/claude-protocol/CLAUDE.local.md.template /path/to/your/project/

# Clean up
rm -rf /tmp/claude-protocol
```

### Option 2: Download and Extract

```bash
# Download the zip
curl -L -o claude-protocol.zip <url>

# Extract
unzip claude-protocol.zip

# Copy to your project
cp -r claude-protocol/.claude /path/to/your/project/
cp -r claude-protocol/.claude-plugin /path/to/your/project/
cp claude-protocol/.mcp.json /path/to/your/project/
```

---

## Initial Setup

### Step 1: Navigate to Your Project

```bash
cd /path/to/your/project
```

### Step 2: Start Claude Code

```bash
claude
```

### Step 3: Initialize the Protocol

Run the initialization command:

```
/proto-init
```

This will:
1. Detect if project is new or existing
2. Analyze languages and frameworks
3. Find build/test commands
4. Ask clarifying questions
5. Generate CLAUDE.md
6. Install git hooks

You'll see output like:
```
╔════════════════════════════════════════════════════════════════╗
║       CLAUDE BOOTSTRAP PROTOCOL v1.2 - DISCOVERY              ║
╚════════════════════════════════════════════════════════════════╝

▶ PHASE 1: PROJECT DISCOVERY
─────────────────────────────────────────────────────────────────
  ✓ Existing project detected
  ✓ Languages: typescript python
  ✓ Frameworks: react fastapi
  ✓ Build: npm run build
  ✓ Test: npm test
```

### Step 4: Answer Questions

The protocol will ask about:
- Project description
- Protected files/directories
- Coding conventions
- Testing approach
- Your skill level

### Step 5: Ready to Use

Once initialization completes, you can use all commands:

Claude will ask questions and generate:
- `CLAUDE.md` - Project context
- Project-specific skills
- Custom slash commands

### Step 5: Set Up Git Ignore (Recommended)

```bash
# Add memory files to gitignore
cat gitignore-template.txt >> .gitignore
```

### Step 6: Personal Preferences (Optional)

```bash
# Create personal config (gitignored)
cp CLAUDE.local.md.template CLAUDE.local.md
# Edit with your preferences
```

---

## Usage

### Slash Commands

| Command | Description |
|---------|-------------|
| `/proto-init` | Initialize + auto-bootstrap |
| `/bootstrap` | Generate all tooling |
| `/validate` | Run validation suite |
| `/fix <issue>` | Fix a bug |
| `/feature <name>` | Implement a feature |
| `/refactor <target>` | Refactor with agents |
| `/search <query>` | Search codebase |
| `/remember <what>` | Save to memory |
| `/recall <topic>` | Search memory |

### Examples

```
# Fix a bug
/fix the login form doesn't validate email

# Add a feature
/feature add password reset functionality

# Search code
/search handleSubmit

# Remember something
/remember we use Zod for validation, not Yup

# Recall context
/recall validation
```

---

## Memory System

The protocol automatically remembers:

| Memory Type | What It Stores |
|-------------|----------------|
| `user-preferences` | Your communication/code style |
| `project-learnings` | Technical discoveries |
| `decisions` | Architectural choices + rationale |
| `corrections` | Mistakes to not repeat |
| `patterns` | Recurring code patterns |

Memory persists across sessions. You never need to repeat yourself.

---

## Quality Enforcement

Every response is checked by:

1. **Laziness Destroyer** - Blocks placeholder code
2. **Hallucination Checker** - Verifies packages/APIs exist
3. **Honesty Evaluator** - Ensures appropriate uncertainty

If checks fail, Claude must fix before completing.

---

## Project Structure After Setup

```
your-project/
├── CLAUDE.md                 # Project context (commit this)
├── CLAUDE.local.md           # Personal prefs (gitignored)
├── .mcp.json                  # MCP config
├── .claude/
│   ├── settings.json         # Hooks + config
│   ├── agents/               # 12 subagents
│   ├── skills/               # 4 skills
│   ├── commands/             # 8 slash commands
│   ├── scripts/              # 10 validation scripts
│   └── memory/               # Persistent memory (gitignored)
└── .claude-plugin/
    └── plugin.json           # Plugin manifest
```

---

## Troubleshooting

### Protocol doesn't auto-start
```bash
# Run manually
bash .claude/scripts/protocol-init.sh
```

### Memory not loading
```bash
# Check memory files exist
ls -la .claude/memory/

# Manually load
bash .claude/scripts/load-memory.sh
```

### Validation failing
```bash
# Run full validation
bash .claude/scripts/validate-all.sh

# Check specific issues
bash .claude/scripts/laziness-check.sh .
bash .claude/scripts/hallucination-check.sh .
```

### Reset memory
```bash
# Clear all memory
rm .claude/memory/*.json

# Reinitialize
bash .claude/scripts/protocol-init.sh
```

---

## Updating the Protocol

```bash
# Get latest version
git pull origin main

# Or re-download and copy
cp -r new-protocol/.claude/* .claude/
cp -r new-protocol/.claude-plugin/* .claude-plugin/
```

---

## Support

- Check `/recall` for project-specific help
- Run `/validate` to diagnose issues
- Review `.claude/memory/errors.log` for error history
