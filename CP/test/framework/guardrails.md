# Test Reporting Guardrails

## Core Directive

**NO FABRICATED RESULTS. NO SKIPPED PROMPTS. NO HARDCODED ANSWERS.**

---

## Anti-Hallucination Rules

### 0. Actually Run The Tests

- If a test requires running `/proto-init`, RUN IT
- If a prompt appears, ANSWER IT and LOG IT
- If you can't run something, say so - don't fake results

### 1. Evidence-Based Only

Every claim requires:
- Command that was run (visible)
- Raw output (visible)
- Interpretation (labeled)

**CORRECT:**
```bash
$ test -f CLAUDE.md && echo "EXISTS" || echo "NOT_FOUND"
EXISTS

✓ CLAUDE.md exists
```

**WRONG:**
```
✓ CLAUDE.md exists   # No evidence
```

### 2. Verification Commands

| Claim | Required Command |
|-------|------------------|
| File exists | `test -f <file> && echo EXISTS` |
| Content preserved | `grep "<string>" <file>` |
| Count | `ls <path> \| wc -l` |
| JSON valid | `jq empty <file>` |
| Version | `grep "version" <file>` |
| Executable | `ls -la <file>` |

### 3. Failure-First

- Default status: UNKNOWN
- Only PASS after command succeeds
- If unexpected output: FAIL immediately
- Never assume success

### 4. No Interpretation of Ambiguity

| Scenario | Action |
|----------|--------|
| No output | "No output returned" - investigate |
| Partial match | Show what matched/didn't |
| Unexpected | Show raw, don't interpret |
| Timeout | FAIL, not PASS |

### 5. Mandatory Diff for Preservation

```bash
# Before
cat CLAUDE.md > /tmp/before.md

# After
cat CLAUDE.md > /tmp/after.md

# Verify
grep -F "exact string" CLAUDE.md
```

### 6. Counter-Verification

```bash
# Primary
grep "My Custom Section" CLAUDE.md

# Counter
grep -c "My Custom Section" CLAUDE.md  # Should be 1
```

### 7. No Metrics Without Source

| Metric | Source Required |
|--------|-----------------|
| Duration | `time` or timestamp diff |
| File count | `find ... \| wc -l` output |
| Line count | `wc -l` output |

### 8. Uncertainty Markers

```
⚠ UNCERTAIN: Output format unexpected.
  Raw output: [show it]
  Please confirm: PASS or FAIL?
```

### 9. Honesty Checklist

Before any claim:
- Did I run a command? If no → don't report
- Can I show output? If no → don't claim
- Would user get same result? If unsure → UNCERTAIN
- Am I inferring? If yes → say "I believe" not "It is"

---

## Anti-Boasting Rules

### 1. Banned Language

| Don't Say | Say Instead |
|-----------|-------------|
| Flawlessly | Completed without errors |
| Perfectly | As expected |
| Impressive | [remove] |
| Excellent | [remove] |
| Robust | Passed [N] tests |
| Battle-tested | Tested |
| Production-ready | Passed these tests |
| Amazing/Great/Awesome | Never use |

### 2. Scope Limitations Required

Every summary must state what was NOT tested.

### 3. No Extrapolation

| Don't Say | Say Instead |
|-----------|-------------|
| This proves it works | These tests passed |
| Users can rely on this | These scenarios passed |
| The feature is solid | Feature worked in this test |
| 100% reliable | 9/9 passed this run |

### 4. Mandatory Caveats

After any success:
- Single machine, controlled environment
- Specific inputs designed for tests
- Does not guarantee user's environment
- Single run, not repeated

### 5. Numbers Without Adjectives

| Don't Say | Say Instead |
|-----------|-------------|
| Blazing fast 47s | 47 seconds |
| Only 3 minutes | Duration: 3 minutes |
| Massive 122 files | 122 files |

### 6. No Self-Congratulation

**Banned:**
- "I successfully..."
- "I was able to..."
- "I've proven..."

**Use:**
- "The test completed..."
- "Output shows..."
- "Results indicate..."

### 7. Comparison Prohibition

Never compare to:
- Other tools
- Previous versions without data
- Hypothetical alternatives
- Industry standards without citation

### 8. Final Check

Before delivering report:
- [ ] Adjective audit - remove superlatives
- [ ] Scope stated - what wasn't tested
- [ ] No extrapolation beyond data
- [ ] No self-praise
- [ ] User told to verify themselves
