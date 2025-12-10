---
description: Initialize Claude protocol for a project (analyze codebase and generate artifacts)
---
$ARGUMENTS

Initialize the Claude protocol for this project:

1. **Analyze Codebase**: Invoke the `codebase-analyzer` agent to:
   - Detect languages and frameworks
   - Map project structure
   - Identify coding patterns
   - Find key files
   - Discover commands

2. **Generate Protocol Artifacts**: Invoke the `protocol-generator` agent to create:
   - Tailored CLAUDE.md with project context
   - Framework-specific agents
   - Project-specific skills
   - Useful slash commands
   - Appropriate hooks

3. **Save State**: Write analysis to memory:
   - Create `memories/codebase-analysis.json`
   - Create `memories/protocol-state.json`

4. **Verify Setup**: Confirm all artifacts created:
   - CLAUDE.md exists and is valid
   - .claude/ directory populated
   - Hooks configured in settings.json

**Arguments:**
- No arguments: Analyze current directory
- `--repo <url>`: Clone and analyze repository
- `--update`: Re-analyze and update existing artifacts
- `--minimal`: Generate only CLAUDE.md

**Output:**

```
## Protocol Initialization Complete

### Codebase Analysis
- Project: {name}
- Type: {type}
- Languages: {languages}
- Frameworks: {frameworks}

### Generated Artifacts
- CLAUDE.md ✓
- Agents: {count} created
- Skills: {count} created  
- Commands: {count} created
- Hooks: {count} configured

### Memory State
- Analysis saved to memories/codebase-analysis.json
- Protocol state saved to memories/protocol-state.json

### Next Steps
1. Review generated CLAUDE.md
2. Test slash commands
3. Run /audit to verify setup
```
