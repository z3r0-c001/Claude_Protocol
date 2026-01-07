---
description: Create a pull request with all checks. Usage: /pr [title]
---

# Pull Request Command

Create a pull request with proper description and checks.

## Process

1. **Pre-PR Checks**
   - Ensure branch is not main/master
   - Check for uncommitted changes
   - Verify remote is up to date

2. **Analyze Changes**
   - Get all commits since branch diverged
   - Summarize changes made
   - Identify affected areas

3. **Generate PR Description**
   ```markdown
   ## Summary
   <bullet points of changes>

   ## Test Plan
   <how to test the changes>

   ## Checklist
   - [ ] Tests pass
   - [ ] No placeholder code
   - [ ] Documentation updated

   🤖 Generated with Claude Code
   ```

4. **Create PR**
   - Use gh cli to create PR
   - Apply labels if appropriate
   - Request reviewers if configured

5. **Report**
   - Show PR URL
   - List any warnings

---

Analyze the changes and create a well-documented pull request.
