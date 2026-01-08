#!/usr/bin/env python3
"""
Git Push Guard - Enforces workflow guardrails before push.

Checks:
1. Commit messages have per-file comments
2. No bulk/lazy commit messages
3. Root .claude/ files are synced to CP/.claude/
4. CP directory is not directly modified (changes flow from root)
"""

import subprocess
import sys
import os
import re
import json
from pathlib import Path

# Color support
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hook_colors import hook_status
except ImportError:
    def hook_status(*args, **kwargs): pass

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Bulk commit patterns to reject
BULK_PATTERNS = [
    r'^updated?\s*(files?)?$',
    r'^fixed?\s*(stuff|things|bugs?)?$',
    r'^various\s*(updates?|changes?|fixes?)?$',
    r'^bug\s*fix(es)?$',
    r'^wip$',
    r'^work\s*in\s*progress$',
    r'^refactor(ing)?$',
    r'^changes?$',
    r'^updates?$',
    r'^fixes?$',
    r'^misc(ellaneous)?$',
    r'^cleanup$',
    r'^clean\s*up$',
    r'^minor\s*(changes?|updates?|fixes?)?$',
    r'^tweaks?$',
]

# Per-file comment pattern: "- filename: description" or "- folder/file: description"
PER_FILE_PATTERN = r'^-\s+[\w./_-]+:\s+.+'


def run_cmd(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def get_project_root():
    """Get the project root directory."""
    output, _ = run_cmd("git rev-parse --show-toplevel")
    return Path(output) if output else None


def get_baseline_commit():
    """Get baseline commit hash from config file."""
    root = get_project_root()
    if not root:
        return None

    baseline_file = root / '.claude' / '.git-guard-baseline'
    if baseline_file.exists():
        return baseline_file.read_text().strip()
    return None


def get_unpushed_commits():
    """Get list of commits to check (after baseline or since upstream)."""
    baseline = get_baseline_commit()

    if baseline:
        # Only check commits after the baseline
        output, code = run_cmd(f"git log {baseline}..HEAD --format='%H|%s' 2>/dev/null")
        if code == 0:
            # Baseline exists - return only commits after it (may be empty)
            commits = []
            if output.strip():
                for line in output.strip().split('\n'):
                    if '|' in line:
                        hash_val, subject = line.split('|', 1)
                        commits.append({'hash': hash_val, 'subject': subject})
            return commits  # Return even if empty - baseline is authoritative

    # Try upstream comparison
    output, code = run_cmd("git log @{u}..HEAD --format='%H|%s' 2>/dev/null")
    if code == 0 and output.strip():
        commits = []
        for line in output.strip().split('\n'):
            if '|' in line:
                hash_val, subject = line.split('|', 1)
                commits.append({'hash': hash_val, 'subject': subject})
        return commits

    # No baseline and no upstream - only check last 3 commits
    output, _ = run_cmd("git log -3 --format='%H|%s'")
    commits = []
    for line in output.strip().split('\n'):
        if '|' in line:
            hash_val, subject = line.split('|', 1)
            commits.append({'hash': hash_val, 'subject': subject})
    return commits


def get_commit_body(commit_hash):
    """Get full commit message body."""
    output, _ = run_cmd(f"git log -1 --format='%b' {commit_hash}")
    return output


def check_bulk_pattern(subject):
    """Check if commit subject matches bulk/lazy patterns."""
    subject_lower = subject.lower().strip()
    for pattern in BULK_PATTERNS:
        if re.match(pattern, subject_lower, re.IGNORECASE):
            return True, pattern
    return False, None


def check_per_file_comments(body):
    """Check if commit body has per-file comments."""
    lines = body.strip().split('\n')
    per_file_lines = [l for l in lines if re.match(PER_FILE_PATTERN, l.strip())]
    return len(per_file_lines) > 0, per_file_lines


def get_changed_files_in_commit(commit_hash):
    """Get list of files changed in a commit."""
    output, _ = run_cmd(f"git diff-tree --no-commit-id --name-only -r {commit_hash}")
    return [f for f in output.strip().split('\n') if f]


def check_cp_sync(root):
    """Check if .claude/ files are synced to CP/.claude/"""
    claude_dir = root / '.claude'
    cp_claude_dir = root / 'CP' / '.claude'

    if not cp_claude_dir.exists():
        return True, []  # CP doesn't exist, skip check

    unsynced = []

    # Get files that differ
    output, code = run_cmd(
        f"diff -rq '{claude_dir}' '{cp_claude_dir}' "
        f"--exclude='*.pyc' --exclude='__pycache__' --exclude='.git' "
        f"--exclude='*.log' --exclude='memory.json' 2>/dev/null"
    )

    if output:
        for line in output.split('\n'):
            if line.strip():
                unsynced.append(line)

    return len(unsynced) == 0, unsynced


def check_direct_cp_edits(commits, root):
    """Check if any commits directly modified CP/ without corresponding root changes."""
    warnings = []

    for commit in commits:
        files = get_changed_files_in_commit(commit['hash'])
        cp_files = [f for f in files if f.startswith('CP/')]
        root_files = [f for f in files if f.startswith('.claude/') and not f.startswith('CP/')]

        # If CP files changed but no corresponding root files, warn
        for cp_file in cp_files:
            # Expected root equivalent
            expected_root = cp_file.replace('CP/', '', 1)
            if expected_root.startswith('.claude/') and expected_root not in root_files:
                warnings.append(f"  {commit['hash'][:8]}: {cp_file} modified without {expected_root}")

    return len(warnings) == 0, warnings


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_pass(text):
    print(f"  {GREEN}✓{RESET} {text}")


def print_fail(text):
    print(f"  {RED}✗{RESET} {text}")


def print_warn(text):
    print(f"  {YELLOW}⚠{RESET} {text}")


def main():
    hook_status("git-push-guard", "RUNNING", "Checking commits")
    print_header("Git Push Guard")

    root = get_project_root()
    if not root:
        hook_status("git-push-guard", "ERROR", "No project root")
        print_fail("Could not determine project root")
        return 1

    commits = get_unpushed_commits()
    if not commits:
        hook_status("git-push-guard", "OK", "No commits to check")
        print_pass("No unpushed commits to check")
        return 0

    print(f"  Checking {len(commits)} unpushed commit(s)...\n")

    errors = []
    warnings = []

    # Check each commit
    for commit in commits:
        commit_hash = commit['hash'][:8]
        subject = commit['subject']
        body = get_commit_body(commit['hash'])

        # Check 1: Bulk pattern
        is_bulk, pattern = check_bulk_pattern(subject)
        if is_bulk:
            errors.append(f"Bulk commit detected [{commit_hash}]: '{subject}'")

        # Check 2: Per-file comments
        has_per_file, file_comments = check_per_file_comments(body)
        if not has_per_file:
            errors.append(f"Missing per-file comments [{commit_hash}]: '{subject}'")

    # Check 3: CP sync
    synced, unsynced = check_cp_sync(root)
    if not synced:
        for item in unsynced[:5]:  # Limit output
            warnings.append(f"Sync needed: {item}")

    # Check 4: Direct CP edits
    no_direct, direct_edits = check_direct_cp_edits(commits, root)
    if not no_direct:
        for edit in direct_edits:
            warnings.append(f"Direct CP edit: {edit}")

    # Print results
    print(f"{BOLD}Results:{RESET}\n")

    if not errors and not warnings:
        hook_status("git-push-guard", "OK", "All checks passed")
        print_pass("All checks passed")
        return 0

    for error in errors:
        print_fail(error)

    for warning in warnings:
        print_warn(warning)

    if errors:
        hook_status("git-push-guard", "BLOCK", f"{len(errors)} errors")
        print(f"\n{RED}{BOLD}PUSH BLOCKED{RESET}")
        print(f"\nFix commit messages to include per-file comments:")
        print(f"  - filename.ext: Description of what changed")
        print(f"\nAvoid bulk comments like: 'Updated files', 'Fixed stuff', 'WIP'")
        return 1

    if warnings:
        hook_status("git-push-guard", "WARN", f"{len(warnings)} warnings")
        print(f"\n{YELLOW}{BOLD}WARNINGS - Push allowed but review recommended{RESET}")
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
