# Changelog

**Current Version:** 1.1.6
**Date:** 2026-01-06

> This file is overwritten with each release. For historical changes, see git history.

---

## v1.1.6 - Research Verifier Skill

Added new skill for verifying best practice claims against authoritative sources with scientific rigor.

### New Skill: research-verifier

| File | Description |
|------|-------------|
| `.claude/skills/research-verifier/SKILL.md` | Complete skill implementation |

### Core Mandates

1. **Official Sources First**
   - ALWAYS check vendor/official docs BEFORE any other source
   - Community posts, blogs, Stack Overflow are LAST RESORT
   - Must label community sources as "not officially verified"

2. **Version Alignment**
   - Match documentation to user's specific version
   - STOP and prompt user if version mismatch or docs unavailable
   - Never proceed without user direction when docs missing

3. **Scientific Comparative Analysis**
   - Anecdotes are NOT evidence
   - Benchmarks require: methodology, environment, sample size, date
   - Note commercial bias in vendor comparisons
   - Mark unverifiable claims as UNVERIFIED

### Source Hierarchy (Mandatory Order)

```
1. Official Documentation (vendor/maintainer)
2. Official GitHub/Source Repo (maintainer comments)
3. RFCs / Specifications
4. Peer-reviewed research / Published benchmarks
5. Community sources (LAST - always labeled)
```

### Trigger Keywords

`best practice`, `should I`, `correct way`, `recommended`, `standard`, `pattern`, `convention`, `proper way`, `official`

### Documentation Updates

| File | Change |
|------|--------|
| CLAUDE.md | Added research-verifier to auto-activated skills table |
| CLAUDE.md | Version 1.1.5 → 1.1.6 |
| protocol-manifest.json | Version 1.1.5 → 1.1.6 |

---

## v1.1.5 - Documentation Accuracy Audit

Fixed discrepancies between documented claims and actual codebase implementation.

### Critical Fixes

| Issue | Fix |
|-------|-----|
| "80+ specialized agents" | Changed to "21 specialized agents" |
| `/verify` command | Removed - doesn't exist |
| `/coverage` command | Changed to `/test --coverage` |

---

## v1.1.4 - Existing CLAUDE.md Preservation

Added B0 section to proto-init for analyzing and preserving existing CLAUDE.md files.
