---
description: Remember something for future sessions. Usage: /remember <category> <what to remember>
---

$ARGUMENTS

# MEMORIZE

You are being asked to remember something. Parse the input and save to memory.

## Categories

Determine the appropriate category:
- **user-preferences** - How the user likes to work, communicate, code style (auto-save)
- **project-learnings** - Technical discoveries, gotchas, what works (auto-save)
- **decisions** - Architectural choices, trade-offs, why we chose X over Y (ask permission)
- **corrections** - Things that were wrong, mistakes to not repeat (auto-save)
- **patterns** - Recurring patterns in code, workflows, or conventions (auto-save)

## Process

1. Parse the user's input to extract:
   - Category (infer if not explicit)
   - Key (short identifier)
   - Value (what to remember)
   - Reason (why this is important)

2. Save using MCP memory tool:
```
Use the mcp__memory__memory_write tool with:
- category: <inferred category>
- key: <short identifier>
- value: <what to remember>
- reason: <why this is important>
```

**Note**: For "decisions" category, the MCP tool will return a permission request. Confirm with user before proceeding with `confirm: true`.

3. Confirm what was saved

## Fallback (CLI usage)

If MCP tools unavailable:
```bash
bash .claude/scripts/save-memory.sh "<category>" "<key>" "<value>" "<reason>"
```

## Examples

Input: "remember I prefer TypeScript over JavaScript"
→ Category: user-preferences
→ Key: language_preference
→ Value: Prefers TypeScript over JavaScript
→ Reason: User stated preference
→ Action: Auto-save (no permission needed)

Input: "remember that the API requires X-Auth-Token header"
→ Category: project-learnings
→ Key: api_auth_header
→ Value: API requires X-Auth-Token header (not Authorization)
→ Reason: Discovered during integration
→ Action: Auto-save (no permission needed)

Input: "we decided to use PostgreSQL for ACID compliance"
→ Category: decisions
→ Key: database_choice
→ Value: PostgreSQL
→ Reason: Need ACID compliance for financial transactions
→ Action: Ask permission first (major decision)

Input: "don't use v1 API endpoints again"
→ Category: corrections
→ Key: api_version
→ Value: Do not use v1 API endpoints
→ Reason: Deprecated, causes errors
→ Action: Auto-save (no permission needed)

## Confirmation

After saving, confirm:
```
Memorized: [key]
  Category: [category]
  Value: [value]

I won't forget this.
```
