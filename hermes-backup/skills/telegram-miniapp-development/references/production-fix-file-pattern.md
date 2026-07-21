# Production Fix File Pattern

When the user wants to close production gaps, create ONE `.md` file per fix.
Each file is self-contained and given to the AI coding agent separately.

## File Naming Convention

```
FIX-01-RATE-LIMITING.md
FIX-02-ALEMBIC.md
FIX-03-GIT.md
FIX-04-ENV-TEMPLATE.md
FIX-05-SECURITY-HEADERS.md
FIX-06-LOGGING.md
FIX-07-CICD.md
FIX-08-ERROR-MONITORING.md
FIX-09-ACCESSIBILITY.md
FIX-10-DOCKER-PRODUCTION.md
```

## File Template

```markdown
# 📋 Fix #N: [Category Name]

> **مشکل:** [One-line description of the gap]
> **راه‌حل:** [One-line description of the fix]

---

## چی باید انجام بشه

### ۱. [Step 1]
[Exact code/commands]

### ۲. [Step 2]
[Exact code/commands]

---

## فایل‌های تغییر یافته

| فایل | تغییر |
|------|--------|
| `path/to/file.py` | What changed |

---

## ⚠️ نکته مهم
[Any warnings or gotchas]
```

## What to Include

1. **Problem statement** — in Persian, one line
2. **Solution** — step-by-step with EXACT code (copy-pasteable)
3. **Files changed** — table of every file touched
4. **Notes/warnings** — gotchas the agent should know

## What NOT to Include

- Long explanations — the code IS the explanation
- Architecture decisions — those are in the architecture docs
- Multiple alternatives — pick the simplest one

## Delivery

After creating all fix files:
```bash
cd /workspace && tar -czf FIXES.tar.gz PROJECT/FIX-*.md
```

Give the user the archive and a README with execution order.

## Execution Order

Always include a `FIXES-README.md` with:
1. Numbered list of fixes in execution order
2. Dependencies (which fix must come before which)
3. Time estimates per fix
4. Overall score improvement projection
