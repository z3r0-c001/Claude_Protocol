# Research Verifier Skill

## Purpose

Verify best practice claims against authoritative sources with scientific rigor. Ensures recommendations are based on official documentation, not assumptions or anecdotes.

## Core Mandates

### 1. Official Sources First

- ALWAYS check official/vendor documentation BEFORE any other source
- Community posts, blogs, Stack Overflow are LAST RESORT
- If using community source, MUST label: "Community opinion, not officially verified"

### 2. Version Alignment

- Identify user's version BEFORE researching
- Match documentation to that specific version
- If version mismatch or docs unavailable:
  - STOP and inform user
  - Present options: older docs, source code analysis, or skip
  - DO NOT proceed without user direction

### 3. Scientific Comparative Analysis

- Anecdotes are NOT evidence
- Benchmarks require: methodology, environment, sample size, date
- Note commercial bias (vendor comparing to competitor)
- Mark unverifiable claims as UNVERIFIED
- Old data (>2 years) should be flagged as potentially outdated

## Source Hierarchy (Mandatory Order)

```
1. Official Documentation (vendor/maintainer)
   └── API references, guides, changelogs

2. Official GitHub/Source Repo
   └── README, CHANGELOG, issue discussions BY MAINTAINERS

3. RFCs / Specifications
   └── For standards (HTTP, OAuth, etc.)

4. Peer-reviewed / Published Research
   └── Academic papers, benchmarks with methodology

5. Community Sources (LAST RESORT, LABEL AS SUCH)
   └── Stack Overflow, blogs, Reddit
   └── MUST be marked as "Community opinion, not verified"
```

## Version Handling Protocol

```
IF user_version is known:
    Search docs for THAT version specifically

IF docs_version > user_version:
    WARN: "Docs are for vX.Y, you're on vX.Z. Behavior may differ."

IF docs_version < user_version:
    WARN: "Your version is newer than available docs."
    ASK: "Should I proceed with older docs, or check release notes?"

IF no docs available:
    STOP
    ASK: "I cannot find official documentation for [X]. Options:
         1. Proceed with source code analysis
         2. Use community resources (less reliable)
         3. Skip this verification"
```

## Activation

### Keywords
- best practice
- should I
- how should
- correct way
- recommended
- standard
- pattern
- convention
- proper way
- official
- according to
- the right way

### Intent Patterns
- "what's the best way to..."
- "which is better..."
- "is this the correct way..."
- "what does the documentation say..."

## Output Formats

### For Best Practice Claims

```
## Verified Best Practice

**Claim:** [What's being verified]
**Source:** [Official doc link]
**Version:** [Docs version] | **Your version:** [User's version]
**Confidence:** Official ✓ | Community ⚠ | Unverified ✗

[Implementation details...]
```

### For Comparisons

```
## Comparison: [A] vs [B]

| Criteria | [A] | [B] | Source |
|----------|-----|-----|--------|
| [Metric] | [Value] | [Value] | [Official doc / Benchmark link] |

### Methodology
- Environment: [describe]
- Test conditions: [describe]
- Sample size: [N]
- Date: [when tested]

### Caveats
- [Any limitations or biases noted]
```

### Confidence Levels

| Level | Meaning | Requirements |
|-------|---------|--------------|
| **Official ✓** | Documented in official guides | Direct link to vendor docs |
| **Community ⚠** | Widely adopted, not officially documented | Must be labeled as such |
| **Unverified ✗** | Cannot find authoritative source | Must inform user |

## Anti-Patterns (DO NOT)

- Claim "best practice" without official source
- Use Stack Overflow as primary source
- Present blog opinions as facts
- Ignore version differences
- Trust benchmarks without methodology
- Proceed when docs unavailable without user consent
- Assume anecdotes or "common knowledge" are accurate
- Skip version verification
- Mix official and community sources without clear labels

## Integration

### Auto-Invoked Agents
- `fact-checker` - Verify factual claims in research

### Triggers Commands
- Activated on keywords above
- Can be manually invoked when verification needed

## Examples

### Good Response

```
## Verified Best Practice

**Claim:** Use `useCallback` for event handlers passed to child components
**Source:** https://react.dev/reference/react/useCallback
**Version:** React 18.2 | **Your version:** React 18.2 ✓
**Confidence:** Official ✓

The React documentation explicitly recommends useCallback when:
1. Passing callbacks to optimized child components
2. The callback is a dependency of useEffect

[Code example from official docs...]
```

### Bad Response (What NOT to do)

```
useCallback is best practice for all event handlers.
Everyone uses it this way.
I saw on a blog that this is the standard approach.
```

### Handling Missing Docs

```
## Documentation Not Found

I cannot find official documentation for `obscure-library` v3.2.

**Options:**
1. Analyze source code on GitHub (maintainer comments only)
2. Check community resources (will be labeled as unverified)
3. Skip verification and proceed with caution

Which approach would you prefer?
```
