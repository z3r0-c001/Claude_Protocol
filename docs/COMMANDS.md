# Command Reference

Complete reference for all Claude Bootstrap Protocol slash commands.

> **Note:** Commands invoke Claude-powered workflows that inherit Claude's limitations. Commands may occasionally fail, produce incorrect output, or misunderstand requirements. Always review command output.

## Initialization Commands

### /proto-init

Initialize the protocol for a new or existing project.

**Usage:**
```
/proto-init
```

**Process:**
1. Asks if project is new or existing
2. For new projects: asks name, description, type, tech stack
3. For existing projects: scans codebase, asks about goals
4. **For existing projects: runs comprehensive audit** (code quality, security, docs, tests, dependencies, architecture)
5. Asks about persistence preferences (JSON or SQLite)
6. Builds MCP server if persistence enabled
7. Creates directory structure
8. Generates project-specific CLAUDE.md
9. Validates all files
10. **Offers permissions configuration** (keep/restrict/audit/custom)

**Interactive Flow:**
- Questions are asked ONE AT A TIME
- Wait for response before proceeding
- Summarizes before generating files

**Comprehensive Audit (Existing Projects):**
- Code quality: placeholder detection, TODOs, stubs
- Security: hardcoded credentials, SQL injection, XSS
- Documentation: README, API docs, inline comments
- Tests: framework detection, coverage estimation
- Dependencies: outdated packages, vulnerabilities
- Architecture: pattern detection, anti-patterns

**Permissions Configuration:**
- `keep` - Keep permissive settings (recommended for dev)
- `restrict` - Prompt for Write/Edit/Bash operations
- `audit` - Review current permissions first
- `custom` - Manual editing with templates

---

### /bootstrap

Generate CLAUDE.md and project tooling based on codebase analysis.

**Usage:**
```
/bootstrap
```

**What it generates:**
- Customized CLAUDE.md with project details
- Project-specific skill if new project
- Updated settings.json if needed

---

### /proto-status

Show current protocol state and health.

**Usage:**
```
/proto-status
```

**Output includes:**
- Protocol version
- MCP server status
- Memory entry counts
- Hook status
- Recent errors (if any)

---

### /proto-help

List all available protocol commands.

**Usage:**
```
/proto-help
```

---

### /proto-update

Check for and apply protocol updates from GitHub.

**Usage:**
```
/proto-update [options]
```

**Examples:**
```
/proto-update                # Interactive update with approval
/proto-update --check        # Dry run - show available updates
/proto-update --analyze      # Full analysis with suggestions
/proto-update --auto         # Auto-accept non-breaking updates
/proto-update --component agents/core/architect  # Update specific component
```

**Options:**
| Option | Description |
|--------|-------------|
| (none) | Interactive update with approval for each change |
| `--check` | Dry run - show available updates without applying |
| `--analyze` | Run protocol-analyzer for smart suggestions |
| `--auto` | Accept all non-breaking updates automatically |
| `--force` | Reset to upstream (loses customizations) |
| `--component <name>` | Update specific component only |
| `--rollback` | Restore from most recent backup |

**Process:**
1. Fetch remote manifest from GitHub
2. Compare with local installation
3. Show available updates with diffs
4. Request approval for each change
5. Apply updates, preserving customizations
6. Verify checksums

**Startup Check:**
The protocol automatically checks for updates on startup (every 24 hours) and notifies you if updates are available.

**Agents invoked:**
- `protocol-updater` for fetching and applying updates
- `protocol-analyzer` for smart suggestions (with --analyze)

---

## Development Commands

### /feature

Implement a new feature using the standard workflow.

**Usage:**
```
/feature <description>
```

**Example:**
```
/feature Add dark mode toggle to settings page
```

**Workflow:**
1. Understand: Read related code, identify affected files
2. Plan: Break down into steps, identify risks
3. Implement: Write complete code (no placeholders)
4. Verify: Run syntax checks, tests
5. Report: Summarize changes

**Agents invoked:**
- `architect` for design decisions
- `security-scanner` if security-related
- `test-coverage-enforcer` for test coverage

---

### /fix

Fix a bug or issue.

**Usage:**
```
/fix <issue description or number>
```

**Example:**
```
/fix Login button not responding on mobile
/fix #123
```

**Workflow:**
1. Reproduce: Understand how to trigger the bug
2. Investigate: Trace code path, find root cause
3. Fix: Make minimal necessary changes
4. Verify: Confirm fix, no regressions
5. Test: Add test to prevent recurrence

---

### /refactor

Refactor code with full quality pipeline.

**Usage:**
```
/refactor <target>
```

**Example:**
```
/refactor authentication module
/refactor src/utils/helpers.ts
```

**Workflow:**
1. Assess: Identify what needs refactoring
2. Plan: Define target state, plan incremental steps
3. Refactor: Make atomic changes, preserve behavior
4. Verify: Run tests, compare before/after

**Agents invoked:**
- `architect` for design guidance
- `reviewer` for code review
- `performance-analyzer` if optimization involved

---

### /test

Run project tests.

**Usage:**
```
/test [pattern] [options]
```

**Examples:**
```
/test                    # Run all tests
/test auth               # Run tests matching "auth"
/test --coverage         # Run with coverage report
/test --watch            # Run in watch mode
```

**Auto-detection:**
- Detects test framework (Jest, Pytest, Go test, etc.)
- Uses appropriate commands for the project

---

### /lint

Run linters on the codebase.

**Usage:**
```
/lint [options] [path]
```

**Examples:**
```
/lint                    # Lint entire project
/lint --fix              # Auto-fix issues
/lint src/               # Lint specific directory
```

---

### /search

Search the codebase.

**Usage:**
```
/search <query or pattern>
```

**Examples:**
```
/search handleAuth       # Find references to handleAuth
/search "async function" # Find all async functions
/search TODO             # Find all TODOs
```

---

## Quality Commands

### /validate

Run full validation suite.

**Usage:**
```
/validate [options]
```

**Examples:**
```
/validate                # Run all validations
/validate --syntax       # Syntax only
/validate --imports      # Import verification only
/validate --security     # Security scan only
```

**Checks performed:**
1. Completeness: No placeholders, TODOs
2. Correctness: All imports/packages verified
3. Syntax: All files pass syntax validation
4. Security: No vulnerabilities
5. Lint: All files pass linting

**Pass threshold:** 100% (zero errors tolerated)

---

## Memory Commands

### /remember

Save information to persistent memory.

**Usage:**
```
/remember <category> <what to remember>
```

**Categories:**
- `architecture` - Code structure decisions
- `decisions` - Why X over Y (requires confirmation)
- `conventions` - Patterns, naming
- `preferences` - Your coding preferences
- `learnings` - Project discoveries

**Examples:**
```
/remember architecture We use a hexagonal architecture pattern
/remember conventions All API endpoints use kebab-case
/remember preferences Prefer functional components over classes
```

---

### /recall

Search memory for information.

**Usage:**
```
/recall <topic or keyword>
```

**Examples:**
```
/recall architecture
/recall authentication
/recall why we chose
```

**Features:**
- Fuzzy matching
- Searches across all categories
- Returns most relevant results

---

## Session Commands

### /leftoff

Save session state for seamless continuation later.

**Usage:**
```
/leftoff [summary]
```

**Examples:**
```
/leftoff                           # Auto-generate summary
/leftoff Working on auth module    # Manual summary
```

**What it saves:**
- Current working context
- Files being edited
- In-progress tasks
- Recent decisions

**Note:** Keeps last 3 sessions automatically.

---

### /resume

Resume from a saved session state.

**Usage:**
```
/resume [session-id]
```

**Examples:**
```
/resume                    # Resume most recent session
/resume 2024-01-15-auth    # Resume specific session
```

**Process:**
1. Lists available sessions if no ID given
2. Loads session context
3. Restores working state
4. Continues from where you left off

---

## Git Commands

### /commit

Safely commit changes after running sanitization.

**Usage:**
```
/commit <message>
```

**Example:**
```
/commit Add user authentication feature
```

**Process:**
1. Run validation suite
2. Check for sensitive data
3. Stage relevant files
4. Create commit with message

---

### /pr

Create a pull request with all checks.

**Usage:**
```
/pr [title]
```

**Example:**
```
/pr Add dark mode support
```

**Process:**
1. Push current branch
2. Run validation
3. Create PR with description
4. Include test plan

---

## Documentation Commands

### /docs

Generate project documentation from code.

**Usage:**
```
/docs [options]
```

**Examples:**
```
/docs                    # Generate all docs
/docs --api              # API documentation only
/docs --readme           # Update README
/docs --all              # Everything
```

---

### /update-docs

Update existing documentation to match current code.

**Usage:**
```
/update-docs
```

**Process:**
1. Scans all documentation files (*.md)
2. Detects stale references (renamed functions, moved files)
3. Finds missing documentation for new code
4. Auto-fixes clear mappings
5. Flags ambiguous changes for review

---

### /reposanitizer

Sanitize a codebase before making it public.

**Usage:**
```
/reposanitizer
```

**Process:**
1. Requires or creates sanitization_workflow.md
2. Performs nuclear rebuild (fresh clone + file-by-file copy)
3. Applies pattern replacements (IPs, credentials, internal refs)
4. Verifies all sensitive data removed
5. Validates sanitized codebase

---

## Command Quick Reference

| Command | Purpose |
|---------|---------|
| `/proto-init` | Initialize protocol |
| `/bootstrap` | Generate tooling |
| `/proto-status` | Check health |
| `/proto-help` | List commands |
| `/proto-update` | Check for/apply updates |
| `/feature <desc>` | Implement feature |
| `/fix <issue>` | Fix bug |
| `/refactor <target>` | Refactor code |
| `/test [pattern]` | Run tests |
| `/lint [--fix]` | Run linters |
| `/search <query>` | Search codebase |
| `/validate` | Run validations |
| `/remember <cat> <text>` | Save to memory (requires MCP) |
| `/recall <topic>` | Search memory (requires MCP) |
| `/leftoff [summary]` | Save session state |
| `/resume [id]` | Resume saved session |
| `/commit <msg>` | Commit changes |
| `/pr [title]` | Create PR |
| `/docs` | Generate docs |
| `/update-docs` | Sync docs with code |
| `/reposanitizer` | Sanitize for public release |
