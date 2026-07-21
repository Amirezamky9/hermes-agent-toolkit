---
name: vercel-react-best-practices
description: >-
  React and Next.js performance optimization guidelines from Vercel Engineering.
  Contains 70+ rules across 8 categories. Use when writing, reviewing, or refactoring
  React/Next.js code to ensure optimal performance patterns.
version: 1.0.0
author: Vercel Engineering
license: MIT
metadata:
  hermes:
    tags: [frontend, react, nextjs, performance, optimization, vercel, web-app, spa, ui]
    related_skills: [realtime-web-apps]
    category: software-development
---

# Vercel React Best Practices

Comprehensive performance optimization guide for React and Next.js applications, maintained by Vercel. Contains 70 rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | JavaScript Optimization | MEDIUM | `js-` |
| 6 | Rerender Prevention | MEDIUM | `rerender-` |
| 7 | Rendering Optimization | MEDIUM | `rendering-` |
| 8 | Advanced Patterns | LOWER | `advanced-` |

## Rule Reference

All 72 rule files are in the `rules/` subdirectory. Load individual rules with `skill_view(name='vercel-react-best-practices', file_path='rules/<rule-name>.md')`.

Key rules:

### Critical: Eliminating Waterfalls
- `async-parallel.md` — Run async operations in parallel when independent
- `async-defer-await.md` — Defer non-critical awaits to avoid blocking renders
- `async-suspense-boundaries.md` — Use Suspense boundaries for streaming

### Critical: Bundle Size
- `bundle-dynamic-imports.md` — Dynamic imports for code splitting
- `bundle-barrel-imports.md` — Avoid barrel imports (re-exports)
- `bundle-conditional.md` — Conditional loading for large dependencies

### High: Server-Side
- `server-parallel-fetching.md` — Parallel data fetching in Server Components
- `server-cache-react.md` — Use React cache() for deduplication
- `server-auth-actions.md` — Server Actions with proper auth checks

### Medium-High: Client-Side
- `client-swr-dedup.md` — SWR/React Query deduplication
- `client-localstorage-schema.md` — Versioned localStorage schemas

### Medium: Rerender Prevention
- `rerender-memo.md` — React.memo usage guidelines
- `rerender-derived-state.md` — Derived state without useEffect
- `rerender-use-deferred-value.md` — useDeferredValue for expensive renders

## Usage

This skill is automatically loaded by the FRONTEND_DEV agent when `skill_discoverer.py` matches its tags (`frontend`, `react`, `web-app`, `spa`) with the agent role keywords.

For complete details, see the `rules/` directory.
