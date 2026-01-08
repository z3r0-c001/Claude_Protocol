# Test Runner Workflow

## Directive: Dynamic Testing

- NO hardcoded answers
- NO pre-scripted responses
- Answer prompts as they appear
- Report actual prompts and actual answers

---

## Phase 1: Setup Test Environment

```bash
# 1.1 Generate random camelCase name at runtime
#     Use: $(cat /dev/urandom | tr -dc 'a-z' | fold -w 4 | head -n 2 | paste -sd '')
#     Or pick two random words: adjective + noun

# 1.2 Create directory
mkdir -p /home/great_ape/codeOne/<generated_name>

# 1.3 Clone fresh from GitHub
git clone https://github.com/z3r0-c001/Claude_Protocol.git /home/great_ape/codeOne/<generated_name>

# 1.4 Verify clone - report whatever version is found
grep "version" /home/great_ape/codeOne/<generated_name>/protocol-manifest.json

# 1.5 Create artifact directories
mkdir -p /home/great_ape/codeOne/<generated_name>/test-results
mkdir -p /home/great_ape/codeOne/<generated_name>/snapshots
mkdir -p /home/great_ape/codeOne/<generated_name>/logs
```

## Phase 2: Install Protocol

```bash
# 2.1 Make executable
chmod +x /home/great_ape/codeOne/<name>/install.sh

# 2.2 Run installer - ANSWER PROMPTS AS THEY APPEAR
cd /home/great_ape/codeOne/<name> && ./install.sh 2>&1 | tee logs/install.log

# 2.3 Verify - report actual state
test -f .claude/settings.json && echo "OK"
ls .claude/hooks/*.sh | wc -l
```

## Phase 3: Capture Baseline

```bash
# 3.1 Snapshot current CLAUDE.md
cp CLAUDE.md snapshots/baseline.md

# 3.2 Record counts
find .claude -type f | wc -l > test-results/baseline_count.txt
```

## Phase 4: Execute Tests

### TEST A: New Project

```
1. Run /proto-init
2. For EACH prompt that appears:
   - LOG: "PROMPT: [exact text]"
   - Decide reasonable answer
   - LOG: "ANSWER: [my choice]"
   - LOG: "RESULT: [what happened]"
3. Continue until complete
4. Validate results
```

### TEST B: Existing + Merge

```
1. Inject custom content into CLAUDE.md
2. Run /proto-init
3. When B0 detection appears:
   - LOG the prompt
   - ANSWER: "merge"
   - LOG result
4. Verify custom content preserved (grep for injected strings)
```

### TEST C: Proto-Update

```
1. Modify version in protocol-manifest.json to simulate outdated
2. Run /proto-update --check
3. LOG what is detected
4. Run /proto-update
5. ANSWER prompts as they appear
6. Verify version restored
```

### TEST D1: Review Mode

```
1. Ensure custom content exists
2. Run /proto-init
3. When B0 appears, ANSWER: "review"
4. For EACH section prompt:
   - LOG: "SECTION: [name]"
   - Make varied decisions (some yes, some no)
   - LOG: "DECISION: [keep/discard]"
5. Verify selective preservation
```

### TEST D2: Replace Mode

```
1. Ensure custom content exists
2. Run /proto-init
3. When B0 appears, ANSWER: "replace"
4. When CONFIRM prompt appears:
   - First: ANSWER "back" - verify returns to options
   - Then: Select "replace" again
   - ANSWER: "CONFIRM"
5. Verify custom content removed
```

### TEST E: Edge Cases

```
E1: Create empty CLAUDE.md, run /proto-init, report behavior
E2: Create malformed markdown, run /proto-init, report behavior
E3: Create 1000+ line file, run /proto-init, report behavior
E4: Remove write permissions, run /proto-init, report error handling
```

## Phase 5: Report

```
For each test, generate:
{
  "test": "A",
  "prompts_received": [
    {"prompt": "...", "answer": "...", "result": "..."}
  ],
  "validations": [...],
  "status": "PASS/FAIL"
}
```

## Phase 6: Cleanup

```
ASK USER:
  [K] Keep directory for inspection
  [D] Delete directory
```

---

## Prompt Logging Format

Every interaction must be logged:

```
═══════════════════════════════════════
PROMPT: [Exact question/prompt received]
───────────────────────────────────────
ANSWER: [My response]
───────────────────────────────────────
RESULT: [What happened after]
═══════════════════════════════════════
```

---

## Execution Command

From Claude Code:
```
"Run protocol tests using framework at Claude_Protocol/test/"
```
