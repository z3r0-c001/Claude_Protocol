# Changelog v1.1.1

## Summary

Fix protocol documentation inconsistencies, standardize hook output format, and add missing manifest entries. Adds mandatory /git pre-push checklist skill.

## Changes

### docs/TROUBLESHOOTING.md
- Line 21: Changed Node.js version requirement from `v20.0.0` to `v18.0.0` for consistency with INSTALLATION.md

### docs/INSTALLATION.md
- Line 179: Updated command count from `(14 total)` to `(24 total)` to match actual .claude/commands/ contents
- Line 183: Updated hook count from `(13 total)` to `(20 total)` to match actual .claude/hooks/ contents
- Line 188: Updated skill count from `(6 total)` to `(15 total)` to match actual .claude/skills/ directories
- Lines 196-200: Removed non-existent scripts (validate-all.sh, session-init.sh, protocol-init.sh, audit.sh), replaced with actual file (install-to-scope.sh)

### protocol-manifest.json
- Line 9: Changed repository URL from `https://github.com/user/Claude_Protocol` to `https://github.com/z3r0-c001/Claude_Protocol`
- Line 11: Changed raw_base URL from `https://raw.githubusercontent.com/user/Claude_Protocol/main` to `https://raw.githubusercontent.com/z3r0-c001/Claude_Protocol/main`
- Line 3: Updated protocol version from `1.0.0` to `1.1.1`
- Line 19: Added AGENT_PROTOCOL description: "Master agent protocol defining standards for all specialized agents."
- Line 153: Added dev-guidelines description: "Development guidelines and coding standards for consistent, maintainable code."
- Line 159: Added doc-processor description: "Process large documentation files into searchable chunks and summaries."
- Line 165: Added project-bootstrap description: "Bootstrap new projects with discovery, analysis, and initial configuration."
- Line 177: Added memorizer description: "Persistent memory management for storing and recalling information across sessions."
- Line 195: Added workflow description: "Development workflow automation for features, fixes, commits, and releases."
- Line 219: Added honesty-guardrail description: "Always-active honesty protocol ensuring accurate claims and uncertainty acknowledgment."
- Line 225: Added quality-control description: "Comprehensive quality validation suite including syntax, lint, completeness, and correctness checks."
- Line 341: Added manage-tools description: "Manage tool permissions and auto-approved tool configurations."
- Line 391: Added post-write-validate.sh description: "Validates written files for syntax errors and completeness after write operations."
- Line 397: Added context-detector.sh description: "Detects file context and suggests appropriate agents based on file type and content."
- Line 403: Added research-quality-check.sh description: "Validates research quality from web fetches and searches for completeness."
- Line 409: Added stop-verify.sh description: "Final verification before stopping to ensure all quality checks pass."
- Line 415: Added file-edit-tracker.sh description: "Tracks file edits for session state and change monitoring."
- Line 421: Added run-hook.sh description: "Utility wrapper for running hooks with proper environment setup."
- Line 427: Added research-validator.sh description: "Validates research output from subagents for accuracy and completeness."
- Line 433: Added hook-logger.sh description: "Logs hook executions for debugging and monitoring."
- Line 439: Added laziness-check.sh description: "Detects placeholder code, TODOs, and incomplete implementations in Stop hook."
- Line 445: Added pre-write-check.sh description: "Blocks writes to protected directories and validates paths before file operations."
- Line 451: Added honesty-check.sh description: "Validates responses for overclaiming and ensures uncertainty is acknowledged."
- Line 457: Added agent-handoff-validator.py description: "Validates agent handoffs to ensure proper context transfer between agents."
- Line 463: Added doc-size-detector.py description: "Detects large documentation files and suggests doc-ingest for processing."
- Line 469: Added context-loader.py description: "Loads project context and checks for protocol updates on startup."
- Line 475: Added pretool-laziness-check.py description: "Blocks Write/Edit with placeholder code, TODOs, or delegation phrases."
- Line 481: Added skill-activation-prompt.py description: "Suggests relevant skills based on user prompt keywords and patterns."
- Line 487: Added dangerous-command-check.py description: "Blocks dangerous bash commands like rm -rf /, chmod 777, and piped curls."
- Line 493: Added pretool-hallucination-check.py description: "Verifies imported packages exist on PyPI/npm before allowing writes."
- Lines 495-500: Added commit-message-validator.sh entry with checksum sha256:bd1e3f831ba5423078f49abd2726829dd5379bc2095a3f72fb9835d679a4fb4b
- Line 485: Updated dangerous-command-check.py checksum from sha256:feb88c2e... to sha256:ee8efcca... after code modification

### .claude/hooks/dangerous-command-check.py
- Lines 12-23: Added output_json() function for consistent JSON output format matching pretool-laziness-check.py and pretool-hallucination-check.py
- Lines 69-71: Changed error handling from `print(msg, file=sys.stderr); sys.exit(1)` to `output_json("continue"); sys.exit(0)`
- Lines 76-78, 81-83: Changed early exits from `sys.exit(0)` to `output_json("continue"); sys.exit(0)`
- Lines 97-98: Changed block output from `print(msg, file=sys.stderr); sys.exit(2)` to `output_json("block", block_message=msg); sys.exit(0)`
- Lines 100-101: Changed success exit from `sys.exit(0)` to `output_json("continue"); sys.exit(0)`
- Lines 104-110: Added try/except wrapper with fallback JSON output for robustness

### .claude/commands/git.md (NEW FILE)
- Created mandatory /git pre-push checklist skill
- Enforces: location verification (must be in CP), commit message specificity, version bump check, changelog check, tag verification
- Defines version numbering rules (PATCH/MINOR/MAJOR)
- Specifies changelog format requirements
- Non-negotiable checklist that must pass before any push

### CLAUDE.md
- Line 9: Updated version from `1.1.0` to `1.1.1`

## Issue References

Fixes issues identified in protocol analysis:
- HIGH #1: Node version inconsistency between INSTALLATION.md and TROUBLESHOOTING.md
- HIGH #2: Missing scripts referenced in INSTALLATION.md
- HIGH #3: Hook output format inconsistency in dangerous-command-check.py
- MEDIUM #4: Incorrect repository URL in protocol-manifest.json
- MEDIUM #5: Outdated component counts in INSTALLATION.md
- LOW #6: Truncated/empty descriptions in protocol-manifest.json
