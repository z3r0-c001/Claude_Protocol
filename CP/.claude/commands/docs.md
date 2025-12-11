---
description: Generate project documentation from code. Usage: /docs [--api] [--readme] [--all]
---

# Documentation Generator

Generate documentation from the codebase.

## Usage

- `/docs` - Generate overview documentation
- `/docs --api` - Generate API documentation
- `/docs --readme` - Update README.md
- `/docs --all` - Generate all documentation

## Process

### Overview Documentation
1. Scan project structure
2. Identify main components
3. Generate architecture overview
4. Document key patterns

### API Documentation
1. Find public interfaces
2. Extract JSDoc/docstrings
3. Generate API reference
4. Include examples

### README Generation
1. Read project configuration
2. Extract description
3. Add setup instructions
4. Include usage examples

## Output Location

Documentation is generated in:
- `docs/` directory
- Or specified output path

## Quality Checks

Generated docs must:
- Be accurate to current code
- Include working examples
- Have no placeholder content

---

Analyze the codebase and generate appropriate documentation.
