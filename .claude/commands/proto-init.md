---
description: Initialize Claude Bootstrap Protocol. Comprehensive setup for any project, any skill level.
---

# Protocol Initialization

You are conducting an interactive intake session to set up Claude Bootstrap Protocol for this project.

## CRITICAL INSTRUCTIONS

1. **ASK ONE QUESTION AT A TIME** - Do not dump all questions at once
2. **WAIT FOR RESPONSE** - Do not proceed until user answers
3. **DO NOT ASSUME** - If unclear, ask for clarification
4. **SUMMARIZE** - After each section, confirm understanding before moving on
5. **BUILD MCP** - Automatically build the MCP server when setting up persistence

---

## START HERE

---

## STEP 0: INSTALLATION SCOPE

**First, check for existing protocol:**

Check if `.claude/settings.json` exists in project OR `~/.claude/hooks/` has protocol files.

**If protocol NOT found, ASK:**
> This appears to be your first time using Claude Protocol.
>
> Where would you like to install the protocol tooling?
>
> - `global` - Install to `~/.claude/` (available in ALL projects)
> - `project` - Install to `./.claude/` (only THIS project, git-trackable)
> - `hybrid` - Core quality hooks global, project customizations local
>
> **Best for:**
> - `global` → Personal use, consistent experience everywhere
> - `project` → Team projects, shared config via git
> - `hybrid` → Power users, maximum flexibility

**WAIT FOR RESPONSE**

**Based on choice:**

- If `global`:
  - Set `INSTALL_TARGET="$HOME/.claude"`
  - Run install script: `scripts/install-to-scope.sh global`
  - SAY: "Installing to ~/.claude/ - protocol will be active in all projects"

- If `project`:
  - Set `INSTALL_TARGET="./.claude"`
  - Continue with normal setup below
  - SAY: "Installing to ./.claude/ - protocol specific to this project"

- If `hybrid`:
  - Install core hooks to `~/.claude/hooks/`
  - Install customizations to `./.claude/`
  - SAY: "Core quality hooks installed globally, project customizations local"

**If protocol ALREADY found:**
> Protocol detected at [location]. Proceeding with configuration...

**THEN continue to STEP 1**

---

First, create the tracking directory:
```bash
mkdir -p .claude/memory
```

---

## STEP 1: PROJECT TYPE

**ASK:**
> Is this a **new project** (no code exists yet) or an **existing codebase**?
>
> Reply: `new` or `existing`

**WAIT FOR RESPONSE**

- If `new` → Go to SECTION A (New Project)
- If `existing` → Go to SECTION B (Existing Project)

---

## SECTION A: NEW PROJECT

Ask these questions ONE AT A TIME. Wait for response after each.

### A1. Project Identity
**ASK:**
> What is the name of this project? (kebab-case preferred, e.g., `my-app`)

**WAIT** → Continue

### A2. Description
**ASK:**
> Describe this project in one sentence. What problem does it solve?

**WAIT** → Continue

### A2b. Description Audit
**EVALUATE** the user's description for:
- Clarity: Does it explain what the project does?
- Specificity: Does it mention the core functionality?
- Brevity: Is it one clear sentence?
- Value proposition: Does it explain why someone would use it?

**IF description could be improved, SAY:**
> Let me suggest a refined version:
>
> **Original:** "[user's description]"
> **Suggested:** "[your improved version]"
>
> Changes made:
> - [specific improvement 1]
> - [specific improvement 2]
>
> Would you like to use the suggested version, keep yours, or provide a new one?

**WAIT FOR APPROVAL** → Use approved version, then continue

**IF description is already clear and effective:**
> Great description! Clear and actionable. Moving on...

→ Continue

### A3. Project Type
**ASK:**
> What type of project is this?
> - `web` - Web application (frontend/backend)
> - `cli` - Command-line tool
> - `library` - Reusable library/package
> - `embedded` - Microcontrollers, firmware, hardware
> - `data` - Data processing, ML, analytics
> - `ops` - DevOps, automation, infrastructure
> - `hybrid` - Combination (describe)

**WAIT** → Continue

### A4a. Primary Language(s)
**ASK:**
> What primary programming language(s) will this project use?
> (e.g., Python, TypeScript, Go, Rust, Java)

**WAIT** → Continue

### A4b. Frameworks
**ASK:**
> What frameworks or libraries are central to this project?
> (e.g., React, FastAPI, Django, Express, Axum)

**WAIT** → Continue

### A4c. Database
**ASK:**
> What database or data storage will you use? (if any)
> (e.g., PostgreSQL, MongoDB, SQLite, Redis, None)

**WAIT** → Continue

### A5. Persistence Needs
**ASK:**
> Do you need persistent memory across sessions? (Things Claude should remember)
> - Architecture decisions
> - Conventions established
> - User preferences
> - Project learnings
>
> Reply: `yes` or `no`

**WAIT** → Continue

**If yes:**

### A6. Storage Type (only if persistence = yes)
**ASK:**
> What storage format would you like for memory?
> - `json` - Simple JSON files (recommended for most projects)
> - `sqlite` - SQLite database (better for large projects)

**WAIT** → Continue

**After A5/A6:** Go to SECTION C (Setup & Generation)

---

## SECTION B: EXISTING PROJECT

### B1. Run Discovery
**SAY:**
> I'll scan the codebase first to understand what exists.

**DO:**
- Check for package.json, requirements.txt, Cargo.toml, go.mod
- Identify primary language(s)
- Find build/test/lint commands
- Map directory structure

**Report findings to user**

### B2. Purpose Check
**ASK:**
> What's the goal here?
> - `maintain` - Add features, fix bugs, keep current patterns
> - `refactor` - Improve/modernize existing code
> - `migrate` - Change tech stack
> - `rescue` - Fix major issues, reduce tech debt

**WAIT** → Continue

### B3. Pain Points
**ASK:**
> What are the top 3 things you want Claude to help with on this project?

**WAIT** → Continue

### B4. Persistence Needs
**ASK:**
> Do you need persistent memory across sessions?
>
> Reply: `yes` or `no`

**WAIT** → Continue

**After B4:** Go to SECTION B-AUDIT (Comprehensive Audit)

---

## SECTION B-AUDIT: COMPREHENSIVE AUDIT (Existing Projects Only)

**SAY:**
> Now I'll run a comprehensive audit of your existing codebase. This will take a moment...

### BA1. Code Quality Analysis

**RUN the laziness-destroyer agent:**
- Scan for placeholder code (`// ...`, `# TODO`, `pass`, etc.)
- Identify incomplete implementations
- Find delegation patterns ("You could...", "You'll need to...")

**Report findings:**
> **Code Completeness Check:**
> - Placeholders found: [count]
> - TODOs/FIXMEs: [count]
> - Stub implementations: [count]

### BA2. Security Scan

**RUN the security-scanner agent:**
- Check for hardcoded credentials
- Identify SQL injection risks
- Find XSS vulnerabilities
- Check for exposed secrets in code

**Report findings:**
> **Security Scan Results:**
> - Critical issues: [count]
> - High severity: [count]
> - Medium severity: [count]
> - Recommendations: [list]

### BA3. Documentation Audit

**CHECK for existing docs:**
- README.md exists and is current?
- API documentation?
- Code comments adequate?
- Architecture docs?

**Report findings:**
> **Documentation Status:**
> - README: [exists/missing/outdated]
> - API docs: [exists/missing/outdated]
> - Inline comments: [adequate/sparse/none]

**ASK:**
> Would you like me to generate missing documentation now?
> - `yes` - Generate docs for the codebase
> - `no` - Skip, I'll do it later

**If yes:** Run `/docs --all` equivalent - generate README, API docs, architecture overview

### BA4. Test Coverage Check

**CHECK for tests:**
- Test files exist?
- Test framework detected?
- Estimate coverage level

**Report findings:**
> **Test Status:**
> - Test framework: [jest/pytest/go test/none]
> - Test files found: [count]
> - Estimated coverage: [high/medium/low/none]

**ASK:**
> Would you like me to generate tests for uncovered code?
> - `yes` - Generate test stubs for key functions
> - `no` - Skip for now

**If yes:** Invoke tester agent to generate test files

### BA5. Dependency Audit

**RUN dependency check:**
- Outdated packages?
- Known vulnerabilities?
- Unused dependencies?

**Report findings:**
> **Dependency Health:**
> - Outdated packages: [count]
> - Vulnerabilities: [count]
> - Unused: [count]

### BA6. Architecture Analysis

**RUN architect agent:**
- Identify architectural patterns in use
- Detect anti-patterns
- Map component relationships

**Report findings:**
> **Architecture Overview:**
> - Pattern detected: [MVC/microservices/monolith/etc.]
> - Key components: [list]
> - Potential issues: [list]

### BA7. Audit Summary

**SAY:**
> **Comprehensive Audit Complete**
>
> | Category | Status | Issues |
> |----------|--------|--------|
> | Code Quality | [PASS/WARN/FAIL] | [count] |
> | Security | [PASS/WARN/FAIL] | [count] |
> | Documentation | [PASS/WARN/FAIL] | [count] |
> | Tests | [PASS/WARN/FAIL] | [count] |
> | Dependencies | [PASS/WARN/FAIL] | [count] |
> | Architecture | [PASS/WARN/FAIL] | [count] |
>
> **Priority fixes recommended:**
> 1. [Most critical issue]
> 2. [Second priority]
> 3. [Third priority]

**ASK:**
> Would you like me to auto-fix any issues I can resolve safely?
> - `yes` - Fix safe issues (formatting, simple refactors)
> - `no` - Just save findings to memory for later

**If yes:** Run safe auto-fixes (formatting, unused imports, simple refactors)

### BA8. Save Audit to Memory

**AUTOMATICALLY save audit findings to memory:**
```
mcp__memory__memory_write category="project-learnings" key="initial-audit" value="[Full audit summary with all findings]"
```

**SAY:**
> Audit findings saved to memory. I'll reference these when working on the project.

**WAIT** → Continue to SECTION C

---

## SECTION C: SETUP & GENERATION

### C1. Summarize
**SAY:**
> Here's what I captured:
>
> [Summarize all answers in a clean format]
>
> **Is this correct?** Reply `yes` to proceed or tell me what to change.

**WAIT FOR CONFIRMATION**

### C2. Create Directory Structure

**RUN:**
```bash
mkdir -p .claude/hooks
mkdir -p .claude/commands
mkdir -p .claude/agents/core
mkdir -p .claude/agents/quality
mkdir -p .claude/skills
mkdir -p .claude/memory
mkdir -p .claude/mcp/memory-server
```

### C3. Generate CLAUDE.md

Create customized `CLAUDE.md` with:
1. Project name and description
2. Detected/specified tech stack
3. Build/test/lint commands
4. Key patterns and conventions
5. Behavioral mandates (from protocol)

### C4. Copy Protocol Files

Copy the core protocol files:
- settings.json (hooks configuration)
- skill-rules.json
- Core hooks (laziness-check.sh, etc.)
- Core agents

### C4.5. Set Hook Permissions

**RUN:**
```bash
chmod +x .claude/hooks/*.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
```

**SAY:**
> Hook scripts are now executable.

### C5. MCP Setup (if persistence = yes)

**SAY:**
> Setting up MCP memory server...

#### C5.1 Check Prerequisites
**RUN:**
```bash
node --version
npm --version
```

**If node not found:**
> Node.js is required for the MCP server. Please install Node.js 18+ first.
> https://nodejs.org/

#### C5.2 Copy MCP Server Files
Copy memory-server source files to `.claude/mcp/memory-server/`

#### C5.3 Install & Build
**RUN:**
```bash
cd .claude/mcp/memory-server && npm install && npm run build
```

**Expected:** `dist/index.js` created

#### C5.4 Create .mcp.json
Create `.mcp.json` in project root with memory server config.

#### C5.5 Initialize Memory
**ASK:**
> Would you like to store any initial facts now? Common categories:
> - `architecture` - Code structure decisions
> - `decisions` - Why X over Y
> - `conventions` - Patterns, naming
> - `preferences` - Your coding preferences
>
> Reply with facts to store, or `skip` to finish.

**WAIT FOR RESPONSE**

### C6. Generate Project-Specific Skill (if new project)

Create `.claude/skills/[project-name]/SKILL.md` with:
- Project patterns
- Tech stack conventions
- Anti-patterns to avoid

### C7. Validation

**SAY:**
> Let me verify everything is working...

**Run:**
1. Check all JSON files are valid
2. Check hooks have correct syntax
3. Verify MCP server responds (if installed)

**Report results**

### C8. Complete

**SAY:**
> Protocol initialization complete!
>
> **What was set up:**
> - [List files created]
> - [List features enabled]
>
> **Available commands:**
> - `/proto-status` - Check protocol health
> - `/validate` - Run validation suite
> - `/remember <text>` - Save to memory
> - `/recall <query>` - Search memory

---

### C9. Permissions Configuration

**ASK:**
> Your permissions are currently set to **permissive mode** for smooth operation during development.
>
> How would you like to manage permissions going forward?
> - `keep` - Keep current permissive settings (recommended for development)
> - `restrict` - Tighten permissions (prompt for sensitive operations)
> - `audit` - Review current permissions before deciding
> - `custom` - Manually customize allow/deny lists

**WAIT FOR RESPONSE**

**If `keep`:**
**SAY:**
> Permissions unchanged. All standard operations will run without prompts.
> You can change this anytime by editing `.claude/settings.json`.

**If `restrict`:**
**RUN:** Replace permissions section in `.claude/settings.json` with restricted template from `.claude/configs/permissions-restricted.json`

**SAY:**
> Permissions restricted. You'll now be prompted for:
> - Write and Edit operations
> - Most Bash commands
> - File deletions
>
> Read, Grep, Glob, and memory operations remain unrestricted.

**If `audit`:**
**SAY:**
> **Currently Allowed (70+ patterns):**
> - All Read/Write/Edit operations
> - Common Bash: npm, node, git, python, make, chmod +x, mkdir, etc.
> - MCP memory tools
> - Web search/fetch
>
> **Currently Denied (safety blocks):**
> - `rm -rf /`, `rm -rf ~` - Destructive deletion
> - `sudo *`, `su *` - Privilege escalation
> - `chmod 777` - Dangerous permissions
> - `curl|wget * | sh` - Remote code execution
> - Fork bombs, system commands
>
> Would you like to `keep`, `restrict`, or `custom`?

**WAIT FOR RESPONSE** → Handle as above

**If `custom`:**
**SAY:**
> Opening `.claude/settings.json` for manual editing.
>
> Key sections:
> - `permissions.allow` - Tools/commands that run without prompts
> - `permissions.deny` - Blocked patterns (safety)
>
> Templates available in `.claude/configs/`:
> - `permissions-permissive.json` - Current liberal settings
> - `permissions-restricted.json` - Locked-down settings
>
> After editing, restart Claude Code to apply changes.

---

### C10. Final Summary

**SAY:**
> **Setup Complete!**
>
> **Next steps:**
> - Review and customize `CLAUDE.md`
> - Try `/validate` to run full validation
> - Use `/proto-status` to check protocol health
>
> Happy coding!

---

## TROUBLESHOOTING

### MCP Build Errors
```bash
cd .claude/mcp/memory-server
rm -rf node_modules dist
npm install
npm run build
```

### Hook Permission Errors
```bash
chmod +x .claude/hooks/*.sh
```

### "Tool not found" for MCP
- Restart Claude Code after adding `.mcp.json`
- Verify `.mcp.json` syntax is valid JSON
