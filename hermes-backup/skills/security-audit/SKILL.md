---
name: security-audit
description: Web application security auditing — methodology, checklists, and framework-specific vulnerability patterns. Covers Flask, Django, Express, and generic web apps. Use when asked to audit code for security, check for vulnerabilities, or review a prior audit's fixes.
tags:
  - security
  - audit
  - vulnerability
  - flask
  - owasp
triggers:
  - security audit
  - check for vulnerabilities
  - review audit fixes
  - security review
  - OWASP
---

# Security Audit — Web Application

## Methodology

### Phase 1: Verify Previous Findings (if re-audit)

Before scanning for new issues, check if prior findings were fixed:

1. Read the previous audit report (look for `REPORT.md` in sibling directories like `cycle1-*`, `cycle2-*`, etc.)
2. For each CRITICAL/HIGH finding, trace the exact code path to verify the fix
3. Report status: FIXED ✅ / STILL OPEN ❌ / PARTIALLY FIXED ⚠️
4. Check if fixes introduced regressions (e.g., `| safe` → `| e` breaks HTML rendering)

**Pitfall:** Don't just grep for the old pattern. Read the surrounding code — a fix might look correct in isolation but fail in context (e.g., SECRET_KEY from env but with a hardcoded fallback that's the same as the old key).

### Phase 2: Read Everything First

Before writing any findings, read ALL source files:
- Every `.py` / `.js` / `.ts` route handler and model
- Every template (check for XSS, template injection)
- Configuration files (`__init__.py`, `config.py`, `.env.example`)
- `requirements.txt` / `package.json` (dependency audit)
- Any seed/migration scripts (often contain hardcoded creds)

### Phase 3: Targeted Scans

Run these grep searches across all templates and source files:

```
# XSS patterns
grep -rn '| *safe' templates/          # Unescaped HTML output
grep -rn '| *e }}' templates/          # Escaped output (verify it's on the right vars)

# CSRF coverage
grep -rn 'csrf_token' templates/       # Count tokens vs form count
grep -rn '<form' templates/            # Every POST form needs a CSRF token

# Secrets
grep -rn 'SECRET_KEY\|secret\|password\|api_key\|token' *.py  # Hardcoded secrets

# Auth patterns
grep -rn 'login_required\|auth_required' *.py  # Verify all sensitive routes are protected
grep -rn 'is_admin\|admin_required' *.py        # Verify admin routes have guards

# Input handling
grep -rn 'request\.form\|request\.args\|request\.json' *.py  # All user input points
grep -rn 'redirect(' *.py               # Check for open redirects
```

### Phase 4: Framework-Specific Deep Dive

Load `references/flask-checklist.md` (or the relevant framework checklist) and work through it systematically.

### Phase 5: Report

Structure the report as:
1. Previous Issue Status (FIXED / STILL OPEN with evidence)
2. New Issues Found (sorted by severity: CRITICAL → HIGH → MEDIUM → LOW)
3. Each finding: file:line, description, exploit scenario, fix recommendation
4. Summary table
5. Priority fix order

## Severity Guide

| Severity | Criteria |
|----------|----------|
| CRITICAL | Direct exploit path, data breach, auth bypass |
| HIGH | Exploitable with moderate effort, affects multiple users |
| MEDIUM | Requires specific conditions, limited impact |
| LOW | Defense-in-depth, hardening, best practice |

## Output Format

Write the report to `<project>/cycle<N>-security/REPORT.md`. Use markdown tables for the summary. Include line numbers for every finding. For previous-issue tracking, use a status column with emoji (✅/❌/⚠️).

## Anti-Patterns to Avoid

- **Don't report theoretical risks without exploit paths.** "Could be exploited if..." needs a concrete step-by-step scenario.
- **Don't mix infrastructure and app security.** If both are needed, note which section covers what.
- **Don't forget the `next` parameter.** Open redirects via login redirect parameters are the #1 missed finding in Flask/Django audits.
- **Don't trust Jinja2 auto-escaping blindly.** It protects text context but not all attribute contexts. `img src`, `href`, and `style` attributes need extra scrutiny.
- **Don't skip seed/migration scripts.** They often contain hardcoded passwords that end up in production.
