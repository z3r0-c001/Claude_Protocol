---
name: design-system
description: "Establish, document, and enforce consistent design tokens, component patterns, and styling conventions across the codebase."
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Task
---

# Design System Skill

## Overview

Create and maintain design system consistency. This skill helps establish design tokens, document component patterns, and enforce styling conventions to ensure a unified UI across the application.

## When This Skill Activates

- Setting up a new project's styling foundation
- Creating or updating design tokens
- Establishing component library patterns
- Auditing UI consistency
- Migrating to a design system

## Core Components

### 1. Design Tokens

Design tokens are the atomic values that define your visual language.

#### Color Tokens
```typescript
// tokens/colors.ts
export const colors = {
  // Brand
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },

  // Semantic
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',

  // Neutral
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    500: '#6b7280',
    900: '#111827',
  },

  // Surfaces
  background: 'var(--color-gray-50)',
  foreground: 'var(--color-gray-900)',
  muted: 'var(--color-gray-100)',
  border: 'var(--color-gray-200)',
} as const
```

#### Spacing Tokens
```typescript
// tokens/spacing.ts
export const spacing = {
  px: '1px',
  0: '0',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  2: '0.5rem',      // 8px
  3: '0.75rem',     // 12px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  8: '2rem',        // 32px
  10: '2.5rem',     // 40px
  12: '3rem',       // 48px
  16: '4rem',       // 64px
} as const
```

#### Typography Tokens
```typescript
// tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },

  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],
    sm: ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem', { lineHeight: '1.5rem' }],
    lg: ['1.125rem', { lineHeight: '1.75rem' }],
    xl: ['1.25rem', { lineHeight: '1.75rem' }],
    '2xl': ['1.5rem', { lineHeight: '2rem' }],
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
  },

  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
} as const
```

#### Animation Tokens
```typescript
// tokens/animation.ts
export const animation = {
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },

  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
} as const
```

### 2. Component Patterns

#### Base Component Interface
```typescript
// types/component.ts
export interface ComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface VariantProps<T extends string> {
  variant?: T
}

export interface SizeProps<T extends string = 'sm' | 'md' | 'lg'> {
  size?: T
}
```

#### Variant Pattern
```typescript
// lib/variants.ts
import { cva, type VariantProps } from 'class-variance-authority'

export const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
        ghost: 'hover:bg-gray-100 hover:text-gray-900',
        destructive: 'bg-error text-white hover:bg-red-600',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)
```

### 3. CSS Custom Properties

```css
/* styles/tokens.css */
:root {
  /* Colors */
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;

  /* Semantic */
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* Spacing */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Animation */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);

  /* Focus */
  --ring-color: var(--color-primary-500);
  --ring-offset: 2px;
}

/* Dark mode */
[data-theme="dark"] {
  --color-background: #111827;
  --color-foreground: #f9fafb;
  --color-muted: #1f2937;
  --color-border: #374151;
}
```

### 4. Consistency Enforcement

#### Token Validation Hook
```bash
#!/bin/bash
# hooks/validate-design-tokens.sh

# Check for magic color values
if grep -rE "#[0-9a-fA-F]{3,6}" --include="*.tsx" --include="*.css" \
   | grep -v "tokens" | grep -v "tailwind.config"; then
  echo "ERROR: Found hardcoded color values. Use design tokens instead."
  exit 1
fi

# Check for magic pixel values
if grep -rE "[0-9]+px" --include="*.tsx" --include="*.css" \
   | grep -v "tokens" | grep -v "@media"; then
  echo "WARNING: Found hardcoded pixel values. Consider using spacing tokens."
fi
```

#### Component Audit Checklist
```markdown
## Component Audit: [Component Name]

### Token Usage
- [ ] Uses color tokens (no hex values)
- [ ] Uses spacing tokens (no px values)
- [ ] Uses typography tokens (no font-size px)
- [ ] Uses radius tokens
- [ ] Uses shadow tokens
- [ ] Uses animation tokens

### Pattern Compliance
- [ ] Follows variant pattern
- [ ] Follows size pattern
- [ ] Has TypeScript interface
- [ ] Uses forwardRef
- [ ] Supports className override
- [ ] Uses cn() for class merging

### Accessibility
- [ ] Has focus-visible styles
- [ ] Color contrast compliant
- [ ] Touch target size compliant
- [ ] Semantic HTML used
```

## File Structure

```
src/
├── design-system/
│   ├── tokens/
│   │   ├── colors.ts
│   │   ├── spacing.ts
│   │   ├── typography.ts
│   │   ├── animation.ts
│   │   └── index.ts
│   ├── primitives/
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Card/
│   │   └── index.ts
│   ├── patterns/
│   │   ├── FormField/
│   │   ├── PageHeader/
│   │   └── index.ts
│   ├── styles/
│   │   ├── tokens.css
│   │   ├── reset.css
│   │   └── utilities.css
│   └── index.ts
```

## Quick Commands

### Initialize Design System
```bash
# Create token files
mkdir -p src/design-system/tokens
touch src/design-system/tokens/{colors,spacing,typography,animation,index}.ts

# Create CSS tokens
mkdir -p src/design-system/styles
touch src/design-system/styles/{tokens,reset,utilities}.css
```

### Audit Token Usage
```bash
# Find hardcoded colors
grep -rE "#[0-9a-fA-F]{3,6}" --include="*.tsx" --include="*.css" | wc -l

# Find hardcoded pixels
grep -rE "[0-9]+px" --include="*.tsx" --include="*.css" | wc -l
```

## Integration Points

| Tool/Agent | Purpose |
|------------|---------|
| `frontend-designer` | Applies design system to new components |
| `reviewer` | Validates token usage in PRs |
| ESLint plugin | Automated token enforcement |
| Storybook | Token documentation |

## Anti-Patterns

1. **One-off Values**
   - Never create values for single use
   - Extend token scale instead

2. **Token Explosion**
   - Keep token sets minimal
   - Avoid excessive variants

3. **Inconsistent Naming**
   - Follow naming convention strictly
   - Use semantic names over descriptive

4. **Missing Documentation**
   - Document all tokens
   - Include usage examples

## Success Criteria

- [ ] All tokens defined and documented
- [ ] CSS custom properties exported
- [ ] TypeScript types generated
- [ ] No magic values in codebase
- [ ] Audit script passes
- [ ] Design system documented
