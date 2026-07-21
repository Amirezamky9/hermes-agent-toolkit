---
name: architecture-audit
description: >
  Multi-persona architecture and codebase audit. Reviews a project from 6-12 perspectives:
  CEO (product strategy), Product (feature gaps), Engineering Manager (code quality),
  Architect (structure/patterns), Database (schema design), Backend (API/services),
  Frontend (UI/UX/accessibility), Security (OWASP/threats), Performance (queries/caching),
  QA (test coverage), DevOps (Docker/CI/CD), Documentation (accuracy/gaps).
  Produces a prioritized remediation report with a Validation Pass before execution.
  Use when: "audit the project", "review the architecture", "full review",
  "architecture review", "codebase audit", "multi-persona review", "professional team review",
  or when the user asks you to use gstack review methodology.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [audit, review, architecture, security, performance, ux, health]
    related_skills: [project-health-analysis, telegram-miniapp-development]
triggers:
  - "audit the project"
  - "review the architecture"
  - "full review"
  - "architecture review"
  - "codebase audit"
  - "multi-persona review"
  - "use gstack review"
  - "gstack workflow"
---

# Architecture Audit — Multi-Persona Project Review

## Overview

A structured codebase review that examines a project from 6 distinct perspectives,
each with its own checklist, findings format, and severity scale. Produces a single
consolidated report with prioritized remediation items.

## When to Use

- User asks for a full project review or architecture audit
- User asks to use "gstack workflow" or "gstack review methodology"
- Before a major release or MVP checkpoint
- When onboarding to an existing codebase
- When user says "بررسی کن" / "audit" / "review the project"
- When user says "like a professional software team" / "مانند یک تیم حرفه‌ای"

## Methodology

### Modes

**Audit-Only Mode (default):** Review + report + action plan. No code changes.
The user will explicitly ask for implementation later. When in doubt, stay
audit-only. Say "هیچ کدی ننویس" = don't write code.

**Implementation Mode:** User explicitly says "start fixing" / "اجرا کن" / "شروع کن".
Even here, run Validation Pass BEFORE any code change.

### The 12 Personas (Full) or 6 Personas (Quick)

**Full audit (12 personas):** Use when user says "like a professional team",
"تیم حرفه‌ای", or lists specific roles. Covers:

| # | Persona | Focus | Key Questions |
|---|---------|-------|---------------|
| 1 | **CEO** | Strategic assessment, MVP viability | Is the product viable? What's blocking launch? |
| 2 | **Product** | Feature completeness, UX gaps | What's built vs placeholder? What's broken? |
| 3 | **Engineering Manager** | Code quality, patterns, team practices | DRY violations? Inconsistent patterns? Dead code? |
| 4 | **Software Architecture** | System design, separation of concerns | Is the architecture sound? Missing layers? |
| 5 | **Database** | Schema design, constraints, indexes | Missing constraints? N+1? Migration path? |
| 6 | **Backend** | API design, business logic, services | Auth complete? Validation? Error handling? |
| 7 | **Frontend** | UI/UX, components, accessibility, RTL | Broken imports? A11y? RTL correct? |
| 8 | **Security** | Threats, auth, secrets, injection, OWASP | Hardcoded secrets? Auth bypass? CORS? |
| 9 | **Performance** | Queries, bundling, caching, N+1 | Slow endpoints? Missing indexes? |
| 10 | **QA** | Test coverage, test quality, gaps | What's tested? What's missing? |
| 11 | **DevOps** | Docker, CI/CD, deployment, monitoring | Health checks? Secrets in compose? |
| 12 | **Documentation** | Docs accuracy, gaps, consistency | Docs match reality? Missing guides? |

**Quick audit (6 personas):** Use when user says "quick review" or "بررسی سریع".

| # | Persona | Focus |
|---|---------|-------|
| 1 | **CEO / Product** | Strategy + features combined |
| 2 | **Architect** | Structure + database combined |
| 3 | **CSO / Security** | Security + auth |
| 4 | **Performance** | Queries + caching |
| 5 | **UX / Design** | Frontend + accessibility |
| 6 | **Code Health** | Tests + docs + DevOps combined |

### Execution Order

Run personas in this order. Each builds on findings from the previous:

```
Full:   CEO → Product → Eng Manager → Architect → Database → Backend →
        Frontend → Security → Performance → QA → DevOps → Documentation

Quick:  CEO → Architect → CSO → Performance → UX → Code Health
```

**CEO first** because product viability gates everything. If the product direction
is wrong, architecture fixes don't matter.

**Security before Performance** because security issues are higher priority.

**Documentation last** because it benefits from context gathered by all other personas.

### Severity Scale

| Level | Symbol | Meaning |
|-------|--------|---------|
| Critical | 🔴 | Blocks MVP / security hole / data loss risk |
| Significant | 🟡 | Causes incorrect behavior / tech debt accumulating |
| Minor | 🟢 | Code quality / consistency / future-proofing |

## Execution Steps

### Step 0: Project Discovery

Before running any persona, discover the project:

1. **File structure** — `search_files` with target=files, get full tree
2. **Config files** — Read package.json, requirements.txt, docker-compose.yml, .env
3. **Entry points** — Read main.py / App.tsx / index.ts
4. **Models/schema** — Read all database models or type definitions
5. **Docs** — Read README, architecture docs, any existing bug reports

Use `delegate_task` for parallel file reads when the project is large (>50 files).

### Step 1: CEO / Product Review

**Read the product through the CEO's eyes.**

Checklist:
- [ ] Product goal is clear and stated in docs/code
- [ ] MVP scope is defined (what's in, what's deferred)
- [ ] Core user flow is complete (end-to-end, not just CRUD)
- [ ] Business model or monetization is considered (even if "none yet")
- [ ] n8n/AI integration (if planned) has real code, not just placeholders
- [ ] Phase roadmap exists and is realistic

Output format:
```markdown
## CEO / Product Review
### Status: [DONE / DONE_WITH_CONCERNS / BLOCKED]
### Key Finding: [one sentence]
### Issues:
| # | Issue | Severity |
```

### Step 2: Architect Review

**Check structural integrity.**

Checklist:
- [ ] Models layer complete (all entities from docs exist in code)
- [ ] Service layer separates business logic from routing
- [ ] Onboarding → operational data flow exists (critical for wizard-based apps)
- [ ] Config from environment (not hardcoded)
- [ ] Migrations system in place (Alembic, Prisma, etc.)
- [ ] No circular imports or dependency cycles
- [ ] API contract matches between frontend types and backend schemas
- [ ] Repository/query layer exists (or services are clean enough without it)

**Common architectural gaps to check:**
- Missing models that docs reference
- Onboarding data never transitions to operational tables
- Settings/config scattered across multiple tables without single source of truth
- Migrations missing (create_all on startup = data loss risk)

Output format:
```markdown
## Architect Review
### Status: [DONE / DONE_WITH_CONCERNS / BLOCKED]
### Key Finding: [one sentence]
### Issues:
| # | Issue | File(s) | Severity |
```

### Step 3: CSO / Security Review

**Run STRIDE threat model + OWASP Top 10 check.**

Checklist:
- [ ] No hardcoded secrets in docker-compose, config files, or source
- [ ] SECRET_KEY / JWT signing key is mandatory (no empty default)
- [ ] Webhook endpoints have signature verification
- [ ] Rate limiting middleware is wired (not just config)
- [ ] CORS is not `["*"]` in production
- [ ] Auth bypass not possible (empty token = rejection, not skip)
- [ ] SQL injection vectors checked (f-string table names, raw queries)
- [ ] HTTPS enforced (not just port 80)
- [ ] Admin endpoints have proper authorization
- [ ] No credentials in git history

**STRIDE quick check:**
- **S**poofing — Can someone pretend to be another user?
- **T**ampering — Can someone modify data they shouldn't?
- **R**epudiation — Can actions be traced back to users?
- **I**nfo disclosure — Can sensitive data leak?
- **D**oS — Can the service be overwhelmed?
- **E**levation — Can a user gain admin privileges?

Output format:
```markdown
## CSO / Security Review
### Status: [DONE / DONE_WITH_CONCERNS / BLOCKED]
### STRIDE Summary: [S:_, T:_, R:_, I:_, D:_, E:_]
### Issues:
| # | Issue | File | Severity |
```

### Step 4: Performance Review

**Find the slow paths.**

Checklist:
- [ ] N+1 query patterns (per-item queries in loops)
- [ ] Missing database indexes on frequently queried columns
- [ ] create_all or equivalent on every startup (should be migrations)
- [ ] Frontend bundle size appropriate for platform (WebView < 200kB gzip)
- [ ] No unnecessary re-renders or state updates
- [ ] Pagination on list endpoints
- [ ] Caching where appropriate (but not premature)

**N+1 detection pattern:**
```python
# ❌ N+1: loop with query inside
for item in items:
    result = await db.execute(select(...).where(... == item.id))

# ✅ Batch: single query with IN clause
result = await db.execute(select(...).where(... .in_([i.id for i in items])))
```

Output format:
```markdown
## Performance Review
### Status: [DONE / DONE_WITH_CONCERNS / BLOCKED]
### Key Finding: [one sentence]
### Issues:
| # | Issue | File:Line | Impact |
```

### Step 5: UX / Design Review

**Walk through every user flow as a non-technical user.**

Checklist:
- [ ] Loading states on all pages (not just one)
- [ ] Error states with retry option on all pages
- [ ] Empty states with call-to-action (not blank screens)
- [ ] Destructive actions have confirmation dialogs
- [ ] No dead-end screens (Chat placeholder, empty pages)
- [ ] RTL layout correct (if applicable)
- [ ] Bottom nav doesn't overlap scrollable content
- [ ] Offline behavior considered (crash vs graceful degradation)

Output format:
```markdown
## UX / Design Review
### Status: [DONE / DONE_WITH_CONCERNS / BLOCKED]
### Issues:
| # | Issue | User Impact | Severity |
```

### Step 6: Code Health Review

**Run available tools and compute scores.**

If tools are available (tsc, pytest, eslint, etc.), run them and score:
- Type safety (tsc errors)
- Test coverage (tests exist, passing)
- Lint cleanliness (warnings/errors)
- Dead code detection
- Dependency health

If tools are NOT available (no node_modules, no venv), do a manual check:
- Are test files present?
- Are type definitions complete?
- Are there unused imports/files?

Output format:
```markdown
## Code Health
### Composite Score: X/10
### Breakdown:
| Category | Score | Status | Notes |
```

### Step 7: Consolidated Report

Merge all persona findings into one report:

```markdown
# Architecture Audit Report

> **Date:** YYYY-MM-DD
> **Project:** [name]
> **Methodology:** GSTACK Multi-Persona Review

## Executive Summary
[2-3 sentences: overall health, top 3 issues, verdict]

## Findings by Persona

### CEO: [status]
[Issues table]

### Architect: [status]
[Issues table]

### CSO: [status]
[Issues table]

### Performance: [status]
[Issues table]

### UX: [status]
[Issues table]

### Code Health: [score]
[Issues table]

## Remediation Priority

### Immediate (Week 1) — Blocking for MVP
| # | Fix | Persona | Time Est |
|---|-----|---------|----------|

### Important (Week 2) — Required for Quality
| # | Fix | Persona | Time Est |
|---|-----|---------|----------|

### Improvements (Week 3+)
| # | Fix | Persona | Time Est |
|---|-----|---------|----------|

## GSTACK REVIEW REPORT
| Persona | Status | Key Finding |
|---------|--------|-------------|
| CEO | [status] | [finding] |
| Architect | [status] | [finding] |
| CSO | [status] | [finding] |
| Performance | [status] | [finding] |
| UX | [status] | [finding] |
| Health | [status] | [finding] |

**VERDICT:** [one paragraph]
**NO UNRESOLVED DECISIONS**
```

### Step 8: Validation Pass (MANDATORY before any fix)

**Before executing ANY fix from the audit, prove each issue exists.**

This is not optional. The user asked for it, and it prevents false positives
from wasting time or breaking working code.

For EACH task in the remediation plan:

1. **Prove the issue exists** — Show the exact file and line number.
   Read the file, quote the code, explain why it's wrong.

2. **Explain root cause** — Why does this problem happen? Is it a typo,
   a missing import, a logic error, an architectural gap?

3. **Determine scope** — Is this:
   - **Dev-only:** Only affects development environment (e.g., debug logging)
   - **Production:** Affects live users (e.g., auth bypass, data loss)
   - **Both:** Affects all environments

4. **Flag false positives** — If there's ANY chance the issue doesn't exist
   or is actually intentional, flag it:
   ```
   ⚠️ False Positive Risk: [explanation]
   Confidence: [X]%
   ```

5. **Set confidence threshold** — Minimum 95% to proceed automatically.
   Below 95% → add to "Phase Review" list for human confirmation.

**Validation Output Format:**
```markdown
### T0.1: [Issue Title]

**File:** `path/to/file.ext`
**Line:** 42
**Code:**
\`\`\`python
# actual problematic code here
\`\`\`

**Why it's wrong:** [explanation]
**Environment:** Production / Development / Both
**False Positive:** ❌ No / ⚠️ Yes — [reason]
**Confidence:** [X]%

**Decision:** ✅ Proceed / ⚠️ Phase Review / ❌ Skip (false positive)
```

**After validation, rewrite the execution plan:**
- Remove confirmed false positives
- Move low-confidence items to a separate review list
- Reorder by validated priority
- Update time estimates based on actual complexity found

### Step 9: Master Action Plan (Post-Validation)

After validation, produce a structured execution plan:

```markdown
## Master Action Plan

### Phase [N]: [Name] ([Timeframe])
> Goal: [one sentence]

| Task | Files | Difficulty | Risk | Dependencies | Parallel |
|------|-------|------------|------|--------------|----------|
| T1.1 | `file.py` | ⭐ Easy | 🔴 High | None | ✅ |
| T1.2 | `file.py` | ⭐⭐ Medium | 🟡 Medium | T1.1 | ❌ |

**Files to change:** N
**Estimated time:** X days
**Overall risk:** Low / Medium / High
```

**Dependency Graph:**
- List which tasks block others
- Show parallel execution opportunities
- Identify critical path

**Recommended Timeline:**
```markdown
### Week 1: Phase 0-1
- Days 1-2: Emergency fixes
- Days 3-5: Security hardening

### Week 2: Phase 2-3
- Days 6-8: Architecture fixes
- Days 9-10: Performance optimization
```

## Post-Audit: gstack Workflow

After the audit + validation + action plan are complete, follow the
`gstack-workflow` skill for implementation. The core loop:

1. **Git flow:** `git checkout develop && git checkout -b fix/phase-N-name`
2. **Implement Phase N:** Execute validated tasks only
3. **Commit:** Descriptive message with task references
4. **`/review`:** Pre-landing diff review before merge
5. **`/ship`:** Merge to develop, clean up feature branch
6. **`/qa`:** Test and verify
7. **`/learn`:** Log what we learned
8. **Repeat** for each phase

**Never skip `/review` before merge.** The review catches:
- SQL injection, broken imports, missing error handling
- Files changed that weren't intended
- Scope creep (fixes that grew beyond their phase)

**Phase 0 rule:** Only verified (≥95% confidence), single-file fixes
that unblock other work. If a "small" fix needs multi-file changes
across frontend + backend, it belongs in Phase 2+.

## Pitfalls

- **Don't skip Step 0 (discovery).** Jumping into persona reviews without reading
  the full codebase leads to surface-level findings. Read models, configs, entry
  points, and docs first. Use `delegate_task` for parallel reads on large projects.

- **Use gstack skills, don't improvise.** gstack is installed at
  `~/.hermes/skills/gstack/`. After the audit, follow `gstack-workflow`
  skill for the execution loop (branch → build → review → ship → qa → learn).
  Never create custom Phase 0/1/2/3 plans when gstack skills handle the
  workflow. The preamble scripts reference `$HOME/.hermes/skills/gstack/bin/`.
  Load gstack skills via `read_file` on their SKILL.md paths.

- **Don't report the same finding in multiple personas.** If a hardcoded secret
  appears in docker-compose AND in config.py, report it under CSO only. Cross-
  reference in other personas with "(see CSO #N)" instead of duplicating.

- **Time estimates are for AI-assisted work.** When estimating fix effort, assume
  AI coding agent assistance. "2-3 hours" means the AI agent can do it in that
  time with human review. Without AI, multiply by 3-5x.

- **Persian-speaking users want scores and ticks, not prose.** Present findings
  as tables with ✅/❌/severity columns. The score (e.g., "46%") is more
  actionable than a paragraph. Use Persian for report text if the user's
  conversation is in Persian.

- **Stop at first rung that holds.** Don't over-analyze areas that are already
  solid. If auth is well-implemented, note it briefly and move on. Spend time
  where findings have the highest impact.

- **`read_file` redacts secret-like content.** The `read_file` tool
  automatically redacts strings that look like secrets — e.g.,
  `` `Bearer ${token}` `` appears as `` `*** ${token}` `` in output.
  This causes FALSE POSITIVES during audit: you'll report "bearer token
  is garbled" when the actual file is correct. **Always verify with
  `terminal` + `sed -n` or `cat -A`** before reporting a finding as
  Critical. The hex-byte check pattern:
  ```bash
  sed -n 'LINEp' path/to/file | cat -A
  ```
  This shows raw content without redaction. If `read_file` and `terminal`
  disagree, trust `terminal`.

- **NEVER skip Validation Pass.** The user asked for it explicitly, and it
  prevents wasted effort on false positives. A subagent's audit finding is
  a HYPOTHESIS until you prove it with file:line evidence. Common false
  positives: "X is missing" when X is in a different file, "Y is broken"
  when Y works differently than expected, "Z is unused" when Z is used
  dynamically, and **`read_file` redaction artifacts** (see pitfall above).
  Read the actual code before fixing.

- **Phase 0 ≠ "fix everything small."** Phase 0 should ONLY contain fixes
  that are (a) verified with ≥95% confidence, (b) require ≤1 file change
  each, and (c) unblock other work. If a "small" fix actually needs backend
  + frontend + schema changes, it belongs in a later phase.

- **Audit-only is the default.** Unless the user explicitly says "fix it" /
  "اجرا کن" / "start implementing", produce the report and action plan
  only. Don't start writing code. The user will tell you when to begin.

## References

- [references/gstack-adaptation.md](references/gstack-adaptation.md) —
  How to apply gstack review skills when CLI isn't available in Hermes WebUI
- [references/full-12-persona-checklist.md](references/full-12-persona-checklist.md) —
  Detailed checklist for each of the 12 personas in a full audit
- [references/validation-pass-example.md](references/validation-pass-example.md) —
  Worked example of Validation Pass with false positive detection
- [references/session-pos-miniapp-audit.md](references/session-pos-miniapp-audit.md) —
  Real session: POS_MINIAPP 12-role audit, read_file redaction false positive,
  gstack workflow execution, delegation pattern (3 parallel subagents)
