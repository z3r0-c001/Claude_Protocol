---
name: quality-control
description: "Automated verification of information accuracy. Use for fact checking, claim verification, source evaluation, and honesty assessment. Triggered by PostToolUse and Stop hooks."
---

# Quality Control Skill

This skill provides systematic verification of information accuracy and intellectual honesty.

## When to Use

- After completing research tasks
- Before presenting factual claims
- When synthesizing multiple sources
- During response finalization

## Verification Process

### Step 1: Claim Extraction

Identify all verifiable claims in the content:
1. Factual assertions (dates, numbers, events)
2. Technical claims (API behaviors, language features)
3. Statistical claims (percentages, measurements)
4. Attribution claims (who said/did what)

### Step 2: Source Verification

For each claim:
1. Identify the source tier (1-3)
2. Check source authority
3. Verify claim against source
4. Note any discrepancies

### Step 3: Confidence Assessment

Assign confidence levels:
- **HIGH**: Multiple Tier 1 sources confirm
- **MEDIUM**: Single Tier 1 or multiple Tier 2 sources
- **LOW**: Only Tier 3 sources or single Tier 2
- **UNVERIFIED**: No authoritative source found

### Step 4: Honesty Check

Verify response demonstrates:
- Appropriate uncertainty language
- Accurate source representation
- Complete task status
- No overconfident claims

## Integration Points

### PostToolUse Hook (WebSearch/WebFetch)

```json
{
  "action": "analyze_sources",
  "check": ["authority", "recency", "bias", "relevance"],
  "flag_if": ["low_authority", "outdated", "single_source"]
}
```

### Stop Hook

```json
{
  "action": "final_verification",
  "check": ["claims_verified", "uncertainty_appropriate", "task_complete"],
  "block_if": ["unverified_critical_claims", "hidden_uncertainty"]
}
```

## Agents Used

- `fact-checker`: Verifies individual claims
- `research-analyzer`: Synthesizes multiple sources
- `honesty-evaluator`: Checks epistemic honesty

## Output Format

```json
{
  "verification_status": "PASS|WARN|FAIL",
  "claims_checked": 5,
  "verified": 4,
  "unverified": 1,
  "confidence": "HIGH",
  "honesty_score": 0.95,
  "issues": [],
  "recommendations": []
}
```

## Files

- `verification-checklist.md`: Manual verification steps
- `source-tiers.md`: Source authority rankings
