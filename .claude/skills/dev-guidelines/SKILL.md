---
name: dev-guidelines
description: >
  Core development guidelines and patterns for this project.
  Use when: implementing features, writing code, refactoring, debugging.
  Trigger keywords: implement, create, build, code, refactor, component, module.
allowed-tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Bash
---

# Development Guidelines

## Overview

This skill provides core development patterns and conventions for the project.
All code contributions should follow these guidelines for consistency and maintainability.

## When to Use This Skill

- Implementing new features
- Writing new code files
- Refactoring existing code
- Debugging issues
- Code review preparation

## Core Principles

1. **Consistency** - Follow established patterns in the codebase
2. **Clarity** - Write readable, self-documenting code
3. **Simplicity** - Prefer simple solutions over clever ones
4. **Testability** - Write code that can be tested
5. **Error Handling** - Handle errors explicitly, don't swallow them

## Code Organization

### File Structure
```
src/
├── components/     # Reusable components
├── services/       # Business logic
├── utils/          # Utility functions
├── types/          # Type definitions
└── config/         # Configuration
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase | `getUserById` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Types/Interfaces | PascalCase | `UserProfile` |

## Patterns

### Error Handling
```typescript
// DO: Explicit error handling
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  logger.error('Operation failed', { error });
  return { success: false, error: error.message };
}

// DON'T: Silent failures
try {
  await riskyOperation();
} catch (e) {
  // swallowed - NEVER DO THIS
}
```

### Function Design
```typescript
// DO: Single responsibility, clear inputs/outputs
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// DON'T: Multiple responsibilities
function processOrder(order) {
  // validates, calculates, saves, emails... too much
}
```

## Anti-Patterns (DO NOT)

- Don't use `any` type without justification
- Don't leave console.log in production code
- Don't hardcode configuration values
- Don't ignore error returns
- Don't write functions over 50 lines without good reason
- Don't nest callbacks more than 2 levels deep
- Don't swallow exceptions silently

## Testing Requirements

- New features require tests
- Bug fixes require regression tests
- Test files live next to source: `foo.ts` → `foo.test.ts`
- Aim for meaningful coverage, not 100%

## Code Quality Checklist

Before submitting code, verify:
- [ ] No placeholder code (// ..., TODO, etc.)
- [ ] All error cases handled
- [ ] Types are explicit (no implicit any)
- [ ] Functions have clear purpose
- [ ] No commented-out code
- [ ] Tests pass

## Resources

For detailed information on specific topics, see:
- `resources/error-handling.md` - Detailed error handling patterns
- `resources/testing.md` - Testing guidelines and examples
- `resources/api-patterns.md` - API design patterns

## Customization

**IMPORTANT**: This is a template skill. Customize it for your project:

1. Update file structure to match your project
2. Add language-specific patterns
3. Add framework-specific conventions
4. Update commands for your build system
5. Add project-specific anti-patterns to avoid
