# Troubleshooting Guide

Solutions for common issues with Claude Bootstrap Protocol.

## Installation Issues

### MCP Server Won't Build

**Symptoms:**
- `npm install` fails
- `npm run build` fails
- TypeScript errors

**Solutions:**

1. **Check Node.js version:**
```bash
node --version
# Must be v20.0.0 or higher
```

2. **Clean and reinstall:**
```bash
cd .claude/mcp/memory-server
rm -rf node_modules dist package-lock.json
npm install
npm run build
```

3. **Check for TypeScript errors:**
```bash
npx tsc --noEmit
```

4. **Verify package.json:**
```bash
cat package.json | python3 -m json.tool
```

---

### Hook Permission Errors

**Symptoms:**
- "Permission denied" when running hooks
- Hooks don't execute

**Solutions:**

1. **Set executable permissions:**
```bash
chmod +x .claude/hooks/*.sh
chmod +x scripts/*.sh
```

2. **Check shebang line:**
```bash
head -1 .claude/hooks/laziness-check.sh
# Should be: #!/bin/bash
```

3. **Verify file exists:**
```bash
ls -la .claude/hooks/
```

---

### "Tool not found" for MCP

**Symptoms:**
- `mcp__memory__*` tools not available
- "Unknown tool" errors

**Solutions:**

1. **Restart Claude Code:**
   - Close and reopen Claude Code
   - MCP servers load on startup

2. **Verify .mcp.json:**
```bash
cat .mcp.json | python3 -m json.tool
```

3. **Check server path:**
```bash
ls .claude/mcp/memory-server/dist/index.js
# File must exist
```

4. **Test server manually:**
```bash
node .claude/mcp/memory-server/dist/index.js
# Should output: "Claude Memory Server running on stdio"
```

5. **Check for port conflicts:**
   - MCP uses stdio, not ports
   - But other MCP servers might conflict

---

## Runtime Issues

### Hooks Not Running

**Symptoms:**
- No hook output
- Quality checks not happening

**Solutions:**

1. **Verify settings.json:**
```bash
python3 -c "import json; json.load(open('.claude/settings.json'))"
```

2. **Check hook paths use $CLAUDE_PROJECT_DIR:**
```json
{
  "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/laziness-check.sh\""
}
```

3. **Test hook manually:**
```bash
CLAUDE_PROJECT_DIR=$(pwd) bash .claude/hooks/laziness-check.sh . human
```

4. **Check for silent failures (2>/dev/null):**
   - Hooks have `2>/dev/null || true` to prevent blocking
   - Remove temporarily to see errors

---

### Memory Not Persisting

**Symptoms:**
- Memory entries disappear
- `/recall` returns nothing

**Solutions:**

1. **Check memory directory exists:**
```bash
ls -la .claude/memory/
```

2. **Create if missing:**
```bash
mkdir -p .claude/memory
```

3. **Check file permissions:**
```bash
chmod 755 .claude/memory
```

4. **Verify JSON files are valid:**
```bash
for f in .claude/memory/*.json; do
  python3 -c "import json; json.load(open('$f'))" && echo "$f: OK"
done
```

5. **Check MEMORY_PATH in .mcp.json:**
```json
{
  "env": {
    "MEMORY_PATH": ".claude/memory"
  }
}
```

---

### Laziness Check False Positives

**Symptoms:**
- Valid code flagged as lazy
- Blocking on legitimate patterns

**Solutions:**

1. **Check what's being flagged:**
```bash
bash .claude/hooks/laziness-check.sh . human
```

2. **Common false positives:**
   - Comments explaining `...` in documentation
   - TODO in test descriptions
   - "You could" in documentation

3. **Exclude directories:**
   Edit `laziness-check.sh`:
```bash
EXCLUDE_DIRS="--exclude-dir=docs --exclude-dir=examples"
```

---

### Context Detector Suggesting Wrong Agents

**Symptoms:**
- Irrelevant agent suggestions
- Too many suggestions

**Solutions:**

1. **Check detection rules:**
```bash
cat .claude/hooks/context-detector.sh
```

2. **Modify patterns:**
```bash
RULES=(
  # Remove or modify overly broad rules
  "auth|password|token:security-scanner:..."
)
```

---

## JSON Errors

### Invalid JSON in settings.json

**Symptoms:**
- "JSON parse error"
- Hooks not loading

**Solutions:**

1. **Validate JSON:**
```bash
python3 -m json.tool < .claude/settings.json
```

2. **Common issues:**
   - Trailing commas
   - Missing quotes
   - Unescaped characters

3. **Fix with jq:**
```bash
jq '.' .claude/settings.json > temp.json && mv temp.json .claude/settings.json
```

---

### Corrupted Memory Files

**Symptoms:**
- Memory read errors
- "Unexpected token" errors

**Solutions:**

1. **Identify corrupted file:**
```bash
for f in .claude/memory/*.json; do
  python3 -c "import json; json.load(open('$f'))" 2>&1 || echo "CORRUPTED: $f"
done
```

2. **Reset specific category:**
```bash
rm .claude/memory/corrupted-category.json
# Will be recreated on next write
```

3. **Reset all memory (data loss):**
```bash
rm .claude/memory/*.json
```

---

## Performance Issues

### Hooks Running Slowly

**Symptoms:**
- Delay after each tool use
- Sluggish response

**Solutions:**

1. **Identify slow hooks:**
```bash
time bash .claude/hooks/laziness-check.sh .
time bash .claude/hooks/context-detector.sh test.ts
```

2. **Reduce grep scope:**
   - Add more exclusions
   - Target specific directories

3. **Disable non-essential hooks:**
   - Comment out in settings.json

---

### MCP Server High Memory

**Symptoms:**
- Memory server consuming resources
- Slow memory operations

**Solutions:**

1. **Prune old entries:**
```
mcp__memory__memory_prune max_age_days=30 dry_run=false confirm=true
```

2. **Limit entries per category:**
```
mcp__memory__memory_prune max_entries=50 dry_run=false confirm=true
```

---

## Common Error Messages

### "ENOENT: no such file or directory"

**Cause:** File path doesn't exist

**Solution:**
```bash
# Create missing directories
mkdir -p .claude/memory
mkdir -p .claude/mcp/memory-server/dist
```

---

### "EACCES: permission denied"

**Cause:** Insufficient permissions

**Solution:**
```bash
chmod +x .claude/hooks/*.sh
chmod 755 .claude/memory
```

---

### "Command failed with exit code 1"

**Cause:** Hook script error

**Solution:**
1. Run hook manually to see error:
```bash
bash -x .claude/hooks/problematic-hook.sh
```

2. Check for missing dependencies (jq, python3, etc.)

---

### "TypeError: Cannot read properties of undefined"

**Cause:** TypeScript/JavaScript error in MCP server

**Solution:**
1. Rebuild MCP server:
```bash
cd .claude/mcp/memory-server
npm run build
```

2. Check for missing type definitions

---

## Reset Procedures

### Soft Reset (Keep Memory)

```bash
# Rebuild MCP server
cd .claude/mcp/memory-server
rm -rf node_modules dist
npm install
npm run build

# Reset permissions
chmod +x .claude/hooks/*.sh

# Validate JSON files
python3 -m json.tool < .claude/settings.json > /dev/null
python3 -m json.tool < .mcp.json > /dev/null
```

### Hard Reset (Fresh Start)

```bash
# Remove generated files
rm -rf .claude/memory/*.json
rm -rf .claude/mcp/memory-server/node_modules
rm -rf .claude/mcp/memory-server/dist

# Reinstall
cd .claude/mcp/memory-server
npm install
npm run build

# Reinitialize
claude
# Then: /proto-init
```

---

## Getting Help

1. **Check protocol status:**
```
/proto-status
```

2. **Run validation:**
```
/validate
```

3. **Check logs:**
```bash
# MCP server logs to stderr
node .claude/mcp/memory-server/dist/index.js 2>&1
```

4. **Report issues:**
   - GitHub Issues: https://github.com/z3r0-c001/Claude_Protocol/issues
   - Include: Error message, steps to reproduce, environment info
