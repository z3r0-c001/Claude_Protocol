# Skills Reference

Complete reference for all Claude Bootstrap Protocol skills.

## Overview

Skills are specialized instruction sets that enhance Claude's capabilities for specific tasks. They are:
- **Auto-activated** based on keywords and patterns
- **Manually invoked** via the Skill tool
- **Always-on** for critical behaviors (like honesty-guardrail)

## Skill Configuration

Skills are configured in `.claude/skills/skill-rules.json`:

```json
{
  "version": "1.0.0",
  "rules": [
    {
      "skill": "skill-name",
      "triggers": {
        "keywords": ["word1", "word2"],
        "patterns": ["regex pattern"]
      },
      "priority": 1,
      "auto_invoke": true
    }
  ]
}
```

## Core Skills

### quality-control

**Purpose:** Automated quality control for all generated code.

**Location:** `.claude/skills/quality-control/SKILL.md`

**Triggers:**
- Keywords: `verify`, `validate`, `check`, `ensure`, `double-check`
- Patterns: `is this correct`, `fact-check`, `ensure quality`

**Features:**
- Zero-tolerance completeness checks
- Import/package verification
- Syntax validation
- Security scanning

**Quality Gates:**
| Check | Threshold |
|-------|-----------|
| Completeness | No placeholders |
| Correctness | All packages verified |
| Syntax | 100% valid |
| Security | No vulnerabilities |

**Usage:**
```
Triggered automatically when using words like "validate" or "check"
Or manually: /validate
```

---

### workflow

**Purpose:** Standard development workflows for consistent implementations.

**Location:** `.claude/skills/workflow/SKILL.md`

**Triggers:**
- Keywords: `implement`, `build`, `create`, `develop`, `fix`, `refactor`
- Patterns: `add feature`, `fix bug`, `build new`

**Workflows:**

1. **Feature Implementation**
   - Understand → Plan → Implement → Verify → Cleanup

2. **Bug Fix**
   - Reproduce → Investigate → Fix → Verify

3. **Refactoring**
   - Assess → Plan → Refactor → Verify

4. **Code Review**
   - Context → Check → Feedback

**Example:**
```
User: "Implement a dark mode toggle"
→ Skill activates, follows Feature Implementation workflow
```

---

### memorizer

**Purpose:** Manage persistent memory across sessions.

**Location:** `.claude/skills/memorizer/SKILL.md`

**Triggers:**
- Keywords: `remember`, `save`, `store`, `note`, `record`
- Patterns: `don't forget`, `keep track`, `note that`

**Memory Categories:**
| Category | Auto-Save | Purpose |
|----------|-----------|---------|
| `user-preferences` | Yes | Coding style, goals |
| `project-learnings` | Yes | Technical discoveries |
| `corrections` | Yes | Mistakes to avoid |
| `patterns` | Yes | Detected patterns |
| `decisions` | Ask | Architecture choices |

**Auto-Save Behaviors:**
- Saves learnings silently
- Saves corrections silently
- Asks permission for major decisions

**Usage:**
```
User: "Remember that we use PostgreSQL"
→ Skill saves to project-learnings

User: "Note: we decided on JWT for auth"
→ Skill asks permission, saves to decisions
```

---

### honesty-guardrail

**Purpose:** Maintain intellectual honesty in all responses.

**Location:** `.claude/skills/honesty-guardrail/SKILL.md`

**Type:** Always-on (not triggered, always active)

**Behaviors:**

1. **Never Overclaim**
   - Don't say "definitely" without proof
   - Don't claim 100% certainty
   - Acknowledge uncertainty

2. **Admit Ignorance**
   - Say "I don't know" when true
   - Offer to research
   - Don't make up answers

3. **Verify Before Claiming**
   - Check documentation
   - Test assertions
   - Cite sources

4. **Stop When Failing**
   - Don't try random variations
   - Research actual cause
   - Explain what went wrong

**Flagged Phrases:**
- "I'm 100% sure"
- "This will definitely work"
- "There's no way this could fail"

**Recommended Alternatives:**
- "Based on my analysis..."
- "This should work because..."
- "I'm confident, but let me verify..."

---

### dev-guidelines

**Purpose:** Development best practices and patterns.

**Location:** `.claude/skills/dev-guidelines/SKILL.md`

**Triggers:**
- Keywords: `best practice`, `convention`, `pattern`, `guideline`
- Patterns: `should I`, `correct way`, `recommended approach`

**Guidelines:**

1. **Read Before Write**
   - Always read existing code first
   - Understand patterns before modifying
   - Never guess at file contents

2. **Default to Action**
   - Implement, don't just suggest
   - Complete all work
   - No placeholders

3. **Minimal Changes**
   - Only change what's requested
   - Don't over-engineer
   - Preserve existing patterns

4. **Error Handling**
   - Handle all error cases
   - No silent failures
   - Meaningful error messages

---

### project-bootstrap

**Purpose:** Project discovery and initialization.

**Location:** `.claude/skills/project-bootstrap/SKILL.md`

**Triggers:**
- Keywords: `init`, `initialize`, `bootstrap`, `setup`
- Patterns: `new project`, `setup project`

**Discovery Process:**

1. **Detect Project Type**
   - Check for package.json, requirements.txt, Cargo.toml
   - Identify primary language
   - Find frameworks

2. **Find Commands**
   - Build commands
   - Test commands
   - Lint commands

3. **Map Structure**
   - Source directories
   - Test directories
   - Config files

4. **Generate CLAUDE.md**
   - Project-specific instructions
   - Build commands
   - Code patterns

---

## Skill Auto-Activation

### How It Works

1. User submits prompt
2. `skill-activation-prompt.py` runs (UserPromptSubmit hook)
3. Keywords/patterns matched against skill-rules.json
4. Matching skills suggested or auto-invoked

### Priority

When multiple skills match, priority determines order:
- Priority 1 = Highest (invoked first)
- Lower priority = invoked after

### Configuration

```json
{
  "rules": [
    {
      "skill": "quality-control",
      "triggers": {
        "keywords": ["validate"],
        "patterns": ["check.*quality"]
      },
      "priority": 1,
      "auto_invoke": true
    }
  ]
}
```

---

## Creating Custom Skills

### 1. Create Skill Directory

```bash
mkdir -p .claude/skills/my-skill
```

### 2. Create SKILL.md

```markdown
---
name: my-skill
description: >
  What this skill does.
  When it should be used.
allowed-tools:
  - Read
  - Write
  - Bash
---

# My Skill

## Overview
Description of the skill's purpose.

## When to Use
- Trigger condition 1
- Trigger condition 2

## Process
1. Step 1
2. Step 2
3. Step 3

## Best Practices
### DO
- Good practice 1
- Good practice 2

### DON'T
- Anti-pattern 1
- Anti-pattern 2
```

### 3. Add to skill-rules.json

```json
{
  "skill": "my-skill",
  "triggers": {
    "keywords": ["my-keyword", "another-keyword"],
    "patterns": ["do.*my-thing"]
  },
  "priority": 2,
  "auto_invoke": true
}
```

### 4. Test

```
User: "Do my-thing for the project"
→ Should activate my-skill
```

---

## Skill Reference Table

| Skill | Purpose | Triggers | Auto-Invoke |
|-------|---------|----------|-------------|
| quality-control | Quality gates | validate, check | Yes |
| workflow | Dev workflows | implement, fix | Yes |
| memorizer | Memory mgmt | remember, save | Yes |
| honesty-guardrail | Honest responses | Always on | Always |
| dev-guidelines | Best practices | best practice | Yes |
| project-bootstrap | Initialization | init, setup | Yes |

---

## Best Practices

### DO
- Keep skills focused on one purpose
- Provide clear trigger keywords
- Include examples in SKILL.md
- Test auto-activation

### DON'T
- Create overlapping triggers
- Make skills too broad
- Forget to add to skill-rules.json
- Use complex regex patterns
