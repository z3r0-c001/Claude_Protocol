# Hooks Reference

Complete reference for all Claude Bootstrap Protocol hooks.

## Overview

Hooks are scripts that run at specific points in Claude's operation:
- **UserPromptSubmit** - Before processing user input
- **PreToolUse** - Before a tool is executed
- **PostToolUse** - After a tool completes
- **Stop** - Before finalizing a response
- **SubagentStop** - When a subagent completes

## Hook Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "SubagentStop": [...]
  }
}
```

## Hook Events

### UserPromptSubmit

Runs before processing user input.

**Available Variables:**
- `$PROMPT` - User's input text

**Hooks:**
| Script | Purpose |
|--------|---------|
| `skill-activation-prompt.py` | Detect keywords to suggest skills |
| `query-analyzer.sh` | Analyze query intent |

**Example Configuration:**
```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.py\""
    }
  ]
}
```

---

### PreToolUse

Runs before a tool executes. Can block dangerous operations.

**Available Variables:**
- `$TOOL_NAME` - Name of the tool being used
- `$TOOL_INPUT` - JSON input to the tool
- `$TOOL_INPUT_FILE_PATH` - For Write/Edit, the target file path

**Matchers:**
- `Write|Edit|MultiEdit` - File modification tools
- `Bash` - Command execution

**Hooks for Write/Edit:**
| Script | Purpose |
|--------|---------|
| `pre-write-check.sh` | Block writes to protected paths |
| `completeness-check.sh` | Block placeholder code before write |

**Hooks for Bash:**
| Script | Purpose |
|--------|---------|
| `dangerous-command-check.sh` | Block dangerous commands |

**Protected Paths (pre-write-check.sh):**
- `.git/` - Git internals
- `node_modules/` - Dependencies
- `.env` files - Secrets
- Lock files - Package locks

**Dangerous Commands (dangerous-command-check.sh):**
- `rm -rf /`
- `sudo rm -rf`
- `chmod 777`
- `curl | sh`
- `wget | sh`

**Example Configuration:**
```json
{
  "matcher": "Write|Edit|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-write-check.sh\" \"$TOOL_INPUT\""
    }
  ]
}
```

---

### PostToolUse

Runs after a tool completes. Used for validation and context detection.

**Available Variables:**
- `$TOOL_NAME` - Name of the tool used
- `$TOOL_OUTPUT` - Output from the tool
- `$TOOL_INPUT_FILE_PATH` - For Write/Edit, the target file path

**Matchers:**
- `Write|Edit|MultiEdit` - File modifications
- `Task` - Subagent completions
- `WebSearch|WebFetch` - Research tools

**Hooks for Write/Edit:**
| Script | Purpose |
|--------|---------|
| `file-edit-tracker.sh` | Track modified files |
| `post-write-validate.sh` | Validate syntax after write |
| `context-detector.sh` | Suggest agents based on file content |

**Hooks for Task:**
| Script | Purpose |
|--------|---------|
| `subagent-output-check.sh` | Validate subagent output quality |

**Hooks for WebSearch/WebFetch:**
| Script | Purpose |
|--------|---------|
| `research-quality-check.sh` | Ensure research is thorough |

**Example Configuration:**
```json
{
  "matcher": "Write|Edit|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-write-validate.sh\" \"$TOOL_INPUT_FILE_PATH\" json"
    },
    {
      "type": "command",
      "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/context-detector.sh\" \"$TOOL_INPUT_FILE_PATH\""
    }
  ]
}
```

---

### Stop

Runs before finalizing a response. Quality gates.

**Available Variables:**
- `$ASSISTANT_RESPONSE` - The response being finalized

**Hooks:**
| Script | Purpose |
|--------|---------|
| `laziness-check.sh` | Detect placeholder/incomplete code |
| `honesty-check.sh` | Flag overconfident language |
| `stop-verify.sh` | Final verification checks |

**Example Configuration:**
```json
{
  "hooks": [
    {
      "type": "command",
      "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/laziness-check.sh\" . json"
    },
    {
      "type": "command",
      "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/honesty-check.sh\" \"$ASSISTANT_RESPONSE\""
    }
  ]
}
```

---

### SubagentStop

Runs when a subagent completes.

**Available Variables:**
- `$TOOL_OUTPUT` - Subagent's final output

**Hooks:**
| Script | Purpose |
|--------|---------|
| `research-validator.sh` | Validate research quality from subagents |

---

## Hook Scripts

### laziness-check.sh

Detects placeholder code, TODOs, and incomplete implementations.

**Usage:**
```bash
.claude/hooks/laziness-check.sh <target> [output_mode]
# target: directory or file to check
# output_mode: "json" or "human" (default: human)
```

**Detection Patterns:**
```
Placeholders:  // ...  # ...  /* ... */
TODOs:         // TODO  # TODO  // FIXME
Stubs:         pass  raise NotImplementedError
Delegation:    "You could..."  "You'll need to..."
```

**JSON Output:**
```json
{
  "hook": "laziness-check",
  "status": "warning",
  "decision": "block",
  "issue_count": 3,
  "issues": [
    {
      "type": "placeholder",
      "file": "src/utils.ts",
      "line": 42,
      "message": "Placeholder comment found",
      "severity": "block"
    }
  ]
}
```

---

### dangerous-command-check.sh

Blocks dangerous bash commands.

**Usage:**
```bash
.claude/hooks/dangerous-command-check.sh "$TOOL_INPUT"
```

**Blocked Patterns:**
- `rm -rf /` or `rm -rf ~`
- `sudo rm -rf`
- `chmod 777`
- `curl|wget ... | sh|bash`
- `mkfs`
- `dd if=/dev/zero`
- `:(){:|:&};:` (fork bomb)

**JSON Output:**
```json
{
  "hook": "dangerous-command-check",
  "status": "block",
  "command": "rm -rf /",
  "reason": "Recursive deletion of root filesystem",
  "suggestion": "Use specific path instead of /"
}
```

---

### context-detector.sh

Suggests agents based on file patterns.

**Usage:**
```bash
.claude/hooks/context-detector.sh "$FILE_PATH"
```

**Detection Rules:**
| File Pattern | Agent Suggested |
|--------------|-----------------|
| `*auth*`, `*password*`, `*token*` | security-scanner |
| `*test*`, `*spec*` | test-coverage-enforcer |
| `package.json`, `requirements.txt` | dependency-auditor |
| `*config*`, `*settings*` | security-scanner |
| `*performance*`, `*cache*` | performance-analyzer |

**JSON Output:**
```json
{
  "hook": "context-detector",
  "status": "suggest",
  "file": "src/auth/login.ts",
  "agent_suggestions": [
    {
      "agent": "security-scanner",
      "reason": "File contains authentication logic"
    }
  ]
}
```

---

### post-write-validate.sh

Validates file syntax after write operations.

**Usage:**
```bash
.claude/hooks/post-write-validate.sh "$FILE_PATH" [output_mode]
```

**Validation by Extension:**
| Extension | Validator |
|-----------|-----------|
| `.json` | `python -m json.tool` |
| `.yaml`, `.yml` | `python -c "import yaml; yaml.safe_load(...)"` |
| `.py` | `python -m py_compile` |
| `.ts`, `.tsx`, `.js`, `.jsx` | `node --check` (syntax only) |
| `.sh` | `bash -n` |

---

### honesty-check.sh

Flags overconfident or inaccurate language.

**Usage:**
```bash
.claude/hooks/honesty-check.sh "$ASSISTANT_RESPONSE"
```

**Flagged Patterns:**
- "I'm 100% sure"
- "This will definitely work"
- "There's no way this could fail"
- "This is the only solution"

**Recommended Alternatives:**
- "Based on my analysis..."
- "This should work because..."
- "I'm confident this will work"

---

## Hook Output Format

All hooks should output structured JSON for Claude to act on:

```json
{
  "hook": "hook-name",
  "status": "pass|warning|block|suggest",
  "issues": [
    {
      "type": "issue-type",
      "file": "path/to/file",
      "line": 42,
      "message": "Description of issue",
      "severity": "auto_fix|suggest|ask|block",
      "suggestion": "How to fix"
    }
  ],
  "agent_suggestions": [
    {
      "agent": "agent-name",
      "reason": "Why this agent should run"
    }
  ]
}
```

**Severity Levels:**
| Severity | Claude's Action |
|----------|-----------------|
| `auto_fix` | Fix immediately, inform user |
| `suggest` | Offer to fix: "I noticed X. Want me to fix it?" |
| `ask` | Always ask permission |
| `block` | Prevent action, explain why |

---

## Creating Custom Hooks

1. Create script in `.claude/hooks/`:

```bash
#!/bin/bash
# my-custom-hook.sh

INPUT="$1"

# Your logic here

# Output JSON
echo '{"hook":"my-custom-hook","status":"pass"}'
exit 0
```

2. Make executable:
```bash
chmod +x .claude/hooks/my-custom-hook.sh
```

3. Add to `.claude/settings.json`:
```json
{
  "PostToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/my-custom-hook.sh\" \"$TOOL_INPUT\""
        }
      ]
    }
  ]
}
```

## Environment Variables

Available in all hooks:
- `$CLAUDE_PROJECT_DIR` - Project root directory
- `$TOOL_NAME` - Current tool name
- `$TOOL_INPUT` - Tool input as JSON
- `$TOOL_OUTPUT` - Tool output (PostToolUse only)
- `$PROMPT` - User prompt (UserPromptSubmit only)
- `$ASSISTANT_RESPONSE` - Response text (Stop only)
