---
description: Verify factual claims, research quality, and honesty of content
---
$ARGUMENTS

Run comprehensive verification on the specified content:

1. **Fact Check**: Invoke the `fact-checker` agent to verify all factual claims
   - Extract verifiable claims
   - Search authoritative sources
   - Report VERIFIED/CONTESTED/UNVERIFIED/FALSE for each

2. **Research Analysis**: Invoke the `research-analyzer` agent to evaluate sources
   - Assess source quality and authority
   - Identify patterns and contradictions
   - Note gaps in coverage
   - Provide confidence levels

3. **Honesty Evaluation**: Invoke the `honesty-evaluator` agent to check:
   - Epistemic honesty (claims match evidence)
   - Source honesty (accurate representation)
   - Task honesty (completion status accurate)
   - Appropriate uncertainty language

**Output a combined verification report:**

```
## Verification Report

### Factual Accuracy
- Claims checked: X
- Verified: Y
- Contested: Z
- Unverified: W

### Source Quality
- Sources analyzed: X
- Tier 1 (authoritative): Y
- Tier 2 (reliable): Z
- Tier 3 (use caution): W

### Honesty Evaluation
- Epistemic score: X/10
- Source score: Y/10
- Task score: Z/10
- Red flags: [list]

### Overall Confidence: HIGH/MEDIUM/LOW

### Recommendations
- [actionable recommendations]
```

If $ARGUMENTS is empty, verify the previous response in this conversation.
