---
description: Initialize Claude Bootstrap Protocol. Comprehensive setup for any project, any skill level.
---

$ARGUMENTS

# PROTOCOL INITIALIZATION - COMPLETE SETUP

You are initializing the Claude Bootstrap Protocol. This is a **comprehensive process** that ensures everything is properly configured. Walk through EVERY step - do not skip anything.

---

## PHASE 1: ENVIRONMENT CHECK
**Purpose**: Ensure the protocol can run

### 1.1 Verify Protocol Files
```bash
echo "Checking protocol installation..."
ls -la .claude/settings.json .claude/agents/laziness-destroyer.md .claude/scripts/validate-all.sh 2>/dev/null && echo "✓ Protocol files present" || echo "✗ Protocol files MISSING"
```

**If files are missing**: Stop and inform the user:
```
Protocol files not found. Please copy the protocol to your project first:

cp -r /path/to/claude-protocol/.claude ./
cp -r /path/to/claude-protocol/.claude-plugin ./
cp /path/to/claude-protocol/.mcp.json ./
```

### 1.2 Check Git Repository
```bash
git rev-parse --git-dir > /dev/null 2>&1 && echo "✓ Git repository" || echo "⚠ Not a git repo"
```

### 1.3 Check Directory Structure
```bash
echo "Project root contents:"
ls -la
echo ""
echo "Directory structure:"
find . -maxdepth 2 -type d | grep -v node_modules | grep -v __pycache__ | grep -v .git | head -20
```

---

## PHASE 2: PROJECT DISCOVERY
**Purpose**: Understand what this project is

### 2.1 Project Type Detection
```bash
echo "=== PROJECT TYPE DETECTION ==="

# Check for project manifests
[ -f "package.json" ] && echo "✓ Node.js project (package.json)" && cat package.json | head -20
[ -f "pyproject.toml" ] && echo "✓ Python project (pyproject.toml)" && cat pyproject.toml | head -20
[ -f "requirements.txt" ] && echo "✓ Python project (requirements.txt)"
[ -f "Cargo.toml" ] && echo "✓ Rust project (Cargo.toml)" && cat Cargo.toml | head -15
[ -f "go.mod" ] && echo "✓ Go project (go.mod)" && cat go.mod | head -10
[ -f "pom.xml" ] && echo "✓ Java/Maven project"
[ -f "build.gradle" ] && echo "✓ Java/Gradle project"
[ -f "Gemfile" ] && echo "✓ Ruby project"
[ -f "composer.json" ] && echo "✓ PHP project"
[ -f "Package.swift" ] && echo "✓ Swift project"
[ -f "Makefile" ] && echo "✓ Makefile present"
[ -f "Dockerfile" ] && echo "✓ Docker configuration"
[ -f "docker-compose.yml" ] && echo "✓ Docker Compose"
```

### 2.2 Language Detection
```bash
echo ""
echo "=== LANGUAGE DETECTION ==="
echo "File types found:"
find . -type f -name "*.py" | head -1 | xargs -I{} echo "  ✓ Python (.py)"
find . -type f -name "*.ts" | head -1 | xargs -I{} echo "  ✓ TypeScript (.ts)"
find . -type f -name "*.tsx" | head -1 | xargs -I{} echo "  ✓ TypeScript React (.tsx)"
find . -type f -name "*.js" | head -1 | xargs -I{} echo "  ✓ JavaScript (.js)"
find . -type f -name "*.jsx" | head -1 | xargs -I{} echo "  ✓ React (.jsx)"
find . -type f -name "*.go" | head -1 | xargs -I{} echo "  ✓ Go (.go)"
find . -type f -name "*.rs" | head -1 | xargs -I{} echo "  ✓ Rust (.rs)"
find . -type f -name "*.java" | head -1 | xargs -I{} echo "  ✓ Java (.java)"
find . -type f -name "*.rb" | head -1 | xargs -I{} echo "  ✓ Ruby (.rb)"
find . -type f -name "*.php" | head -1 | xargs -I{} echo "  ✓ PHP (.php)"
find . -type f -name "*.swift" | head -1 | xargs -I{} echo "  ✓ Swift (.swift)"
find . -type f -name "*.cs" | head -1 | xargs -I{} echo "  ✓ C# (.cs)"
find . -type f -name "*.cpp" -o -name "*.cc" | head -1 | xargs -I{} echo "  ✓ C++ (.cpp/.cc)"
find . -type f -name "*.c" | head -1 | xargs -I{} echo "  ✓ C (.c)"
```

### 2.3 Framework Detection
```bash
echo ""
echo "=== FRAMEWORK DETECTION ==="

# JavaScript/TypeScript frameworks
[ -f "package.json" ] && {
    grep -q '"react"' package.json && echo "  ✓ React"
    grep -q '"next"' package.json && echo "  ✓ Next.js"
    grep -q '"vue"' package.json && echo "  ✓ Vue.js"
    grep -q '"nuxt"' package.json && echo "  ✓ Nuxt"
    grep -q '"angular"' package.json && echo "  ✓ Angular"
    grep -q '"svelte"' package.json && echo "  ✓ Svelte"
    grep -q '"express"' package.json && echo "  ✓ Express.js"
    grep -q '"fastify"' package.json && echo "  ✓ Fastify"
    grep -q '"nestjs"' package.json && echo "  ✓ NestJS"
    grep -q '"electron"' package.json && echo "  ✓ Electron"
}

# Python frameworks
[ -f "requirements.txt" ] && {
    grep -qi "django" requirements.txt && echo "  ✓ Django"
    grep -qi "flask" requirements.txt && echo "  ✓ Flask"
    grep -qi "fastapi" requirements.txt && echo "  ✓ FastAPI"
    grep -qi "pytorch\|torch" requirements.txt && echo "  ✓ PyTorch"
    grep -qi "tensorflow" requirements.txt && echo "  ✓ TensorFlow"
    grep -qi "pandas" requirements.txt && echo "  ✓ Pandas"
    grep -qi "numpy" requirements.txt && echo "  ✓ NumPy"
}

[ -f "pyproject.toml" ] && {
    grep -qi "django" pyproject.toml && echo "  ✓ Django"
    grep -qi "flask" pyproject.toml && echo "  ✓ Flask"
    grep -qi "fastapi" pyproject.toml && echo "  ✓ FastAPI"
}
```

### 2.4 Tooling Detection
```bash
echo ""
echo "=== TOOLING DETECTION ==="

# Testing
[ -f "jest.config.js" ] || [ -f "jest.config.ts" ] && echo "  ✓ Jest (testing)"
[ -f "vitest.config.js" ] || [ -f "vitest.config.ts" ] && echo "  ✓ Vitest (testing)"
[ -f "pytest.ini" ] || [ -f "conftest.py" ] && echo "  ✓ Pytest (testing)"
[ -f "phpunit.xml" ] && echo "  ✓ PHPUnit (testing)"

# Linting
[ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ] && echo "  ✓ ESLint"
[ -f ".prettierrc" ] || [ -f "prettier.config.js" ] && echo "  ✓ Prettier"
[ -f "ruff.toml" ] || [ -f ".ruff.toml" ] && echo "  ✓ Ruff (Python)"
[ -f ".flake8" ] && echo "  ✓ Flake8 (Python)"
[ -f "mypy.ini" ] || grep -q "mypy" pyproject.toml 2>/dev/null && echo "  ✓ MyPy (Python types)"
[ -f "tsconfig.json" ] && echo "  ✓ TypeScript"
[ -f "biome.json" ] && echo "  ✓ Biome"

# Build tools
[ -f "webpack.config.js" ] && echo "  ✓ Webpack"
[ -f "vite.config.js" ] || [ -f "vite.config.ts" ] && echo "  ✓ Vite"
[ -f "rollup.config.js" ] && echo "  ✓ Rollup"
[ -f "esbuild.config.js" ] && echo "  ✓ esbuild"

# CI/CD
[ -d ".github/workflows" ] && echo "  ✓ GitHub Actions"
[ -f ".gitlab-ci.yml" ] && echo "  ✓ GitLab CI"
[ -f "Jenkinsfile" ] && echo "  ✓ Jenkins"
[ -f ".circleci/config.yml" ] && echo "  ✓ CircleCI"
```

### 2.5 Existing Documentation Check
```bash
echo ""
echo "=== EXISTING DOCUMENTATION ==="
[ -f "README.md" ] && echo "  ✓ README.md" && head -30 README.md
[ -f "CONTRIBUTING.md" ] && echo "  ✓ CONTRIBUTING.md"
[ -f "CHANGELOG.md" ] && echo "  ✓ CHANGELOG.md"
[ -d "docs" ] && echo "  ✓ docs/ directory"
[ -f "CLAUDE.md" ] && echo "  ⚠ CLAUDE.md already exists - will update"
```

---

## PHASE 3: COMMAND DETECTION
**Purpose**: Find build, test, lint, and run commands

### 3.1 Package.json Scripts (if Node.js)
```bash
[ -f "package.json" ] && {
    echo "=== AVAILABLE NPM SCRIPTS ==="
    grep -A 30 '"scripts"' package.json | head -35
}
```

### 3.2 Makefile Targets (if present)
```bash
[ -f "Makefile" ] && {
    echo "=== MAKEFILE TARGETS ==="
    grep -E "^[a-zA-Z_-]+:" Makefile | head -20
}
```

### 3.3 Python Commands
```bash
[ -f "pyproject.toml" ] && {
    echo "=== PYTHON PROJECT SCRIPTS ==="
    grep -A 10 '\[project.scripts\]' pyproject.toml 2>/dev/null
    grep -A 10 '\[tool.poetry.scripts\]' pyproject.toml 2>/dev/null
}
```

---

## PHASE 4: INTERACTIVE QUESTIONNAIRE
**Purpose**: Fill in gaps and understand unique requirements

Now ask the user these questions. **Adapt based on what was detected** - skip questions you already have answers to.

### 4.1 Basic Project Info
Ask ONLY if not detected:
```
1. What is this project called?
   [Detected: {name from package.json/pyproject.toml} - press Enter to confirm or type new name]

2. Briefly describe what this project does (1-2 sentences):
   [This helps Claude understand context for all future interactions]
```

### 4.2 Commands
Ask ONLY if not detected or ambiguous:
```
3. How do you BUILD this project?
   [Detected: npm run build / make build / none]
   
4. How do you TEST this project?
   [Detected: npm test / pytest / none]
   
5. How do you LINT this project?
   [Detected: npm run lint / ruff check . / none]
   
6. How do you RUN this project (for development)?
   [Detected: npm run dev / python main.py / none]
```

### 4.3 Project-Specific Requirements
Always ask these:
```
7. Are there any CRITICAL files or directories Claude should NEVER modify?
   (e.g., production configs, generated files, vendor code)
   [Default: none]

8. Are there any project-specific PATTERNS or CONVENTIONS Claude should follow?
   (e.g., "always use functional components", "never use ORM, write raw SQL")
   [Default: follow existing patterns in codebase]

9. What testing approach does this project use?
   [ ] Unit tests only
   [ ] Unit + Integration tests
   [ ] Unit + Integration + E2E tests
   [ ] TDD (Test-Driven Development)
   [ ] No tests yet (Claude will help set them up)

10. What's the PRIMARY GOAL for using Claude on this project?
    [ ] New feature development
    [ ] Bug fixing and maintenance
    [ ] Refactoring and cleanup
    [ ] Learning the codebase
    [ ] Documentation
    [ ] All of the above
```

### 4.4 Team Context (if applicable)
```
11. Is this a solo project or team project?
    [ ] Solo - just me
    [ ] Team - multiple developers
    
12. (If team) Any specific code review requirements or PR processes?
    [Default: standard PR with review]
```

### 4.5 Skill Level Calibration
```
13. What's your experience level with THIS project's tech stack?
    [ ] Beginner - explain things in detail
    [ ] Intermediate - standard explanations
    [ ] Expert - be concise, skip basics
    
    (This helps Claude calibrate explanations appropriately)
```

---

## PHASE 5: SYNTHESIS
**Purpose**: Compile everything learned into protocol state

After gathering all information, update the protocol state with comprehensive data about the project.

Save to `.claude/memory/protocol-state.json` with:
- Project name, description, type
- All detected languages and frameworks
- All commands (build, test, lint, dev, deploy)
- Tooling configuration
- User preferences and skill level
- Protected paths and conventions
- Team context

---

## PHASE 6: GENERATE CLAUDE.md
**Purpose**: Create the project context file

Using ALL gathered information, generate a comprehensive CLAUDE.md at the project root with:

1. **Project Overview** - Name, description, purpose
2. **Quick Reference** - Command table
3. **Project Structure** - Key directories explained
4. **Tech Stack** - Languages, frameworks, tools
5. **Conventions** - Code style, patterns to follow
6. **Protected Paths** - What NOT to modify
7. **Development Workflow** - How to develop, test, deploy
8. **For Claude** - Specific instructions for AI assistance

---

## PHASE 7: FINALIZE SETUP
**Purpose**: Complete initialization and verify everything works

### 7.1 Install Git Hooks
```bash
bash .claude/scripts/install-git-hooks.sh
```

### 7.2 Run Validation
```bash
bash .claude/scripts/validate-all.sh
```

### 7.3 Save User Preferences to Memory
```bash
bash .claude/scripts/save-memory.sh user-preferences "skill-level" "[LEVEL]"
bash .claude/scripts/save-memory.sh user-preferences "verbosity" "[based on level]"
bash .claude/scripts/save-memory.sh user-preferences "primary-goal" "[GOAL]"
```

---

## PHASE 8: COMPLETION REPORT

Output a clear, formatted summary showing:
- Project name and type
- Detected languages and frameworks
- Configured commands
- Files created
- Validation status
- Quick start guide with example commands

End with: "Ready to code! What would you like to work on?"

---

## CRITICAL RULES

1. **Walk through EVERY phase** - Do not skip steps
2. **Show your work** - Run the detection commands and show output
3. **Ask when uncertain** - Better to ask than assume wrong
4. **Adapt to skill level** - Verbose for beginners, concise for experts
5. **Save everything** - All discoveries go to memory
6. **Validate before completing** - Ensure setup actually works
7. **No placeholders** - Generate complete, real content
8. **Handle both new and existing projects** - Adapt the flow accordingly
