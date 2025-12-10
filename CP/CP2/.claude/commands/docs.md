---
description: Generate project documentation from code. Usage: /docs [--api] [--readme] [--all]
---

$ARGUMENTS

# DOCS - Generate Documentation

Generate comprehensive documentation from the codebase.

## Process

### Step 1: Analyze Codebase

```bash
# Find all source files
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" \) \
    | grep -v node_modules | grep -v __pycache__ | grep -v .git

# Extract structure
tree -I 'node_modules|__pycache__|.git|dist|build' -L 3
```

### Step 2: Extract Documentation

For each source file, extract:
- Module/file docstrings
- Class/function signatures
- Docstrings and comments
- Type annotations
- Exported functions/classes

### Step 3: Generate Documentation

Based on arguments:

#### README (default or --readme)
Generate/update README.md with:
```markdown
# Project Name

Brief description from package.json/pyproject.toml/Cargo.toml

## Installation

[Auto-detected install commands]

## Usage

[Main entry points and examples]

## API Reference

[Key functions/classes]

## Configuration

[Environment variables, config files]

## Development

### Prerequisites
- [Detected dependencies]

### Setup
```bash
[Setup commands]
```

### Testing
```bash
[Test commands]
```

## License

[From LICENSE file]
```

#### API Documentation (--api)
Generate docs/API.md with:
```markdown
# API Reference

## Module: src/module

### Functions

#### `functionName(param1: Type, param2: Type): ReturnType`

Description from docstring.

**Parameters:**
- `param1` (Type): Description
- `param2` (Type): Description

**Returns:** ReturnType - Description

**Example:**
```python
result = functionName("value", 42)
```

### Classes

#### `ClassName`

Description from docstring.

**Constructor:**
```python
ClassName(param1: Type)
```

**Methods:**
- `method1()`: Description
- `method2(arg)`: Description
```

#### Full Documentation (--all)
Generate:
- README.md
- docs/API.md
- docs/ARCHITECTURE.md
- docs/CONTRIBUTING.md
- CHANGELOG.md (if git history exists)

## Output Location

```
docs/
├── API.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── examples/
    └── basic-usage.md
README.md
CHANGELOG.md
```

## Output Format

```markdown
## Documentation Generated

### Files Created/Updated
| File | Status | Lines |
|------|--------|-------|
| README.md | Updated | 150 |
| docs/API.md | Created | 420 |

### Coverage
- Documented functions: 45/52 (87%)
- Documented classes: 12/12 (100%)
- Missing docstrings: 7 items

### Suggestions
- Add docstring to `src/utils.py:calculate_total`
- Add examples to `src/api.py:fetch_data`
```

## Save State

```bash
bash .claude/scripts/save-memory.sh project-learnings "docs-generated" "$(date): README, API docs"
```
