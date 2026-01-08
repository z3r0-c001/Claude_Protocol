# Test Cases

## Directive: Dynamic Execution

- No pre-determined answers
- Respond to prompts in real-time
- Log every prompt/answer/result
- Validate based on actual outcomes

---

## TEST A: New Project Initialization

### Purpose
Verify `/proto-init` works correctly for new projects.

### Preconditions
- Fresh clone from GitHub
- Protocol installed
- No prior `/proto-init` run

### Execution

```
1. Run /proto-init
2. When prompted, respond with reasonable choices
3. Log each interaction:
   PROMPT: [what was asked]
   ANSWER: [what I chose]
   RESULT: [what happened]
4. Continue until initialization complete
```

### Validations

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| CLAUDE.md exists | `test -f CLAUDE.md` | File exists |
| .claude/ structure | `ls .claude/` | Expected dirs present |
| Hooks executable | `ls -la .claude/hooks/*.sh` | All have +x |
| JSON valid | `jq empty .claude/settings.json` | No errors |

---

## TEST B: Existing Project - Merge Mode

### Purpose
Verify B0 detects existing CLAUDE.md and merge preserves content.

### Preconditions
- TEST A completed (or CLAUDE.md exists)
- Custom content injected

### Custom Content to Inject

```markdown
## My Custom Section

This content MUST survive re-initialization.

### Custom Commands
| Command | Purpose |
|---------|---------|
| `make custom` | My special build |

### Project Rules
- NEVER modify /legacy/
- Always use tabs
```

### Execution

```
1. Inject custom content: cat >> CLAUDE.md
2. Run /proto-init
3. When B0 detection appears:
   PROMPT: [shows existing CLAUDE.md detected]
   ANSWER: merge
   RESULT: [content flagged for preservation]
4. Complete initialization
5. Verify preservation
```

### Validations

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| Custom section | `grep "My Custom Section" CLAUDE.md` | Found |
| Custom commands | `grep "make custom" CLAUDE.md` | Found |
| Custom rules | `grep "NEVER modify" CLAUDE.md` | Found |
| Protocol sections | `grep "## Hooks" CLAUDE.md` | Found |

---

## TEST C: Proto-Update Version Detection

### Purpose
Verify `/proto-update` detects and handles version differences.

### Preconditions
- Protocol installed

### Execution

```
1. Record current version
2. Modify version to simulate outdated:
   sed -i 's/"version": "X.X.X"/"version": "1.0.0"/' protocol-manifest.json
3. Run /proto-update --check
   PROMPT: [what updates available]
   LOG: [detected changes]
4. Run /proto-update
   PROMPT: [apply updates?]
   ANSWER: [respond to prompts]
   RESULT: [what was updated]
5. Verify version restored
```

---

## TEST D1: Review Mode

### Purpose
Verify section-by-section review allows selective preservation.

### Preconditions
- Custom content exists in CLAUDE.md

### Execution

```
1. Run /proto-init
2. When B0 appears:
   PROMPT: [merge/review/replace options]
   ANSWER: review
3. For EACH section shown:
   PROMPT: "Keep [section name]? yes/no/edit"
   ANSWER: [varied - some yes, some no]
   LOG: decision for each
4. Complete initialization
5. Verify only kept sections present
```

### Validations
- Sections answered "yes" → present in final CLAUDE.md
- Sections answered "no" → absent from final CLAUDE.md

---

## TEST D2: Replace Mode

### Purpose
Verify replace mode requires CONFIRM and removes content.

### Preconditions
- Custom content exists in CLAUDE.md

### Execution

```
1. Run /proto-init
2. When B0 appears:
   PROMPT: [merge/review/replace options]
   ANSWER: replace
3. When CONFIRM prompt appears:
   PROMPT: "Type CONFIRM to proceed or back"
   ANSWER: back
   RESULT: [should return to options]
4. Select replace again:
   ANSWER: replace
5. When CONFIRM prompt appears:
   ANSWER: CONFIRM
   RESULT: [should proceed]
6. Verify custom content removed
```

### Validations

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| Custom section gone | `grep "My Custom Section" CLAUDE.md` | NOT found |
| Protocol fresh | `grep "## Hooks" CLAUDE.md` | Found |

---

## TEST E: Edge Cases

### E1: Empty CLAUDE.md

```
1. Create empty file: > CLAUDE.md
2. Run /proto-init
3. LOG: How does it handle 0 lines?
4. Expected: Proceeds normally or asks to create fresh
```

### E2: Malformed CLAUDE.md

```
1. Create broken markdown:
   echo "# Unclosed
   \`\`\`no closing
   | broken | table" > CLAUDE.md
2. Run /proto-init
3. LOG: How does it handle corruption?
4. Expected: Graceful handling, not crash
```

### E3: Large CLAUDE.md

```
1. Create 1000+ line file
2. Run /proto-init
3. LOG: Performance and handling
4. Expected: Reads entire file correctly
```

### E4: No Write Permissions

```
1. chmod 444 CLAUDE.md
2. Run /proto-init
3. LOG: Error message shown
4. Expected: Clear error, not silent failure
5. chmod 644 CLAUDE.md (restore)
```

---

## Logging Requirements

Every prompt interaction MUST be logged:

```
═══════════════════════════════════════
TEST [X] - Step [N]
═══════════════════════════════════════
PROMPT: [exact text received]
───────────────────────────────────────
ANSWER: [my response]
───────────────────────────────────────
RESULT: [outcome observed]
═══════════════════════════════════════
```

No fabricated results. No skipped prompts.
