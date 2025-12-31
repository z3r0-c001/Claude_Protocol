---
name: frontend-design
description: "Complete frontend design workflow: research, design, implement, and validate UI components with consistency enforcement."
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - Task
---

# Frontend Design Skill

## Overview

A comprehensive workflow for creating consistent, accessible, and maintainable frontend code. Combines research, design specification, implementation guidance, and validation.

## When This Skill Activates

- User mentions: UI, frontend, component, design, layout, responsive, accessibility, CSS, styling
- Working with: .tsx, .jsx, .vue, .svelte, .css, .scss files
- Creating: buttons, forms, modals, cards, navigation, pages

## Workflow Stages

### Stage 1: Discovery (Always First)

Before writing any UI code:

1. **Search Existing Components**
   - Find existing components in codebase
   - Find existing styles
   - Check for design tokens

2. **Identify Design System**
   - Check for Tailwind (tailwind.config.js)
   - Check for CSS variables (:root)
   - Check for styled-components/emotion
   - Check for component library (package.json)

3. **Document Existing Patterns**
   - Styling Approach: Tailwind, CSS Modules, Styled Components, etc.
   - Component Library: Custom, Radix UI, Shadcn/ui, MUI, etc.
   - Design Tokens: Colors, Spacing, Typography locations

### Stage 2: Research (When Needed)

Invoke ui-researcher agent when:
- No existing patterns found
- Need to evaluate new libraries
- Complex accessibility requirements
- Performance-critical components

### Stage 3: Design Specification

Before coding, create component spec:

- Purpose: What problem does this solve?
- Variants: Primary, Secondary, Ghost, etc.
- States: Default, Hover, Active, Focus, Disabled, Loading, Error
- Props: Type definitions with defaults
- Accessibility: Role, keyboard navigation, ARIA attributes

### Stage 4: Implementation

Follow consistent structure:
- Use TypeScript interfaces
- Use forwardRef for DOM access
- Use design tokens (no magic values)
- Include all states
- Ensure keyboard accessibility

### Stage 5: Validation

Run these checks:

1. **Accessibility Audit**
   - All interactive elements focusable
   - Focus order logical
   - Color contrast >= 4.5:1
   - Touch targets >= 44x44px
   - Labels for all inputs
   - Alt text for images

2. **Responsive Check**
   - Works at 320px width
   - Works at 768px width
   - Works at 1024px width
   - No horizontal scroll

3. **Consistency Check**
   - Uses design tokens (no magic values)
   - Follows naming convention
   - Matches existing patterns
   - Props interface documented

## Quick Reference: Common Patterns

### Colors (Use Tokens)
- Good: Use CSS variables or Tailwind classes
- Bad: Hardcoded hex values

### Spacing (Use Scale)
- Good: Use spacing variables or utility classes
- Bad: Hardcoded pixel values

### Typography (Use Scale)
- Good: Use text size tokens
- Bad: Hardcoded font sizes

### Focus States (Always Include)
- Required for accessibility
- Visible focus ring on keyboard navigation

## Integration Points

| Agent | When to Invoke |
|-------|----------------|
| ui-researcher | Need library recommendations |
| frontend-designer | Complex component architecture |
| brainstormer | Requirements unclear |
| tester | After implementation |
| reviewer | Before PR |

## Anti-Patterns to Avoid

1. **Magic Values** - Always use design tokens
2. **Missing States** - Always handle hover, focus, active, disabled
3. **Accessibility Skipping** - Never remove focus outlines without replacement
4. **Inconsistent Naming** - Follow existing conventions
5. **Inline Styles** - Avoid except for dynamic values

## Success Criteria

- Discovery phase completed
- Component spec created
- Uses design tokens
- All states implemented
- Keyboard accessible
- Screen reader accessible
- Responsive across breakpoints
- Props fully typed
- Follows existing patterns
