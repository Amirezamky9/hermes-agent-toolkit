---
name: n8n-quality-improvement
description: >
  Cross-phase quality improvement system for n8n workflow building.
  Judge + Worker architecture: Worker (nightly cron) analyzes session logs,
  feedback, and manual fixes — READ ONLY, with per-action traceability.
  Judge (Hermes) reads the report, presents findings, suggests patches.
  User decides what to act on. Covers session-logging protocol, feedback
  collection, nightly pipeline, and the closed-loop improvement cycle.
version: 1.0.0
author: "Designed with Amirreza Mokhtari"
license: MIT
metadata:
  hermes:
    tags: [n8n, quality, improvement, continuous, feedback, nightly]
    related_skills: [n8n-intake, n8n-planner, n8n-reviewer, n8n-builder]
---

# n8n-quality-improvement — Closed-Loop Quality System

## Architecture: Judge + Worker

```
🌙 2 AM — Worker (nightly cron, READ-ONLY)
  • reads session-logs, feedback, manual-fixes
  • deep session_search for missed errors
  • generates per-action traceability log (step-by-step)
  • saves report — NEVER modifies files

☀️ Morning — Judge (Hermes)
  • reads worker report
  • presents findings to user
  • suggests trap-reference / SKILL patches
  • user decides what to act on
```

## Core Principles

1. **Worker is READ-ONLY.** It scans, reads, analyzes, reports. Never writes to session-logs, feedback, bugs, or any user file. The only write is the JSON action-log in `reports/`.
2. **Per-action traceability.** Every tool call the worker makes is logged with: tool name, query, status, result_count, duration_ms, error detail, timestamp. No blind "processed" — you can see exactly what happened.
3. **Two-contributor session log.** After each session, BOTH user and agent fill a session-log:
   - User writes: `user_manual_fixes`, `user_feedback`, `user_suggestions`, `user_missed`
   - Judge writes: `judge_model_mistakes`, `judge_observations`, `judge_stats`
4. **User decides.** Judge presents findings and suggestions. User decides whether to patch trap-reference, update a SKILL, or ignore. Judge never modifies production files without the user saying so.

## Directory Layout

```
/workspace/n8n-wfb/
├── session-logs/       ← One YAML per session (TEMPLATE.yaml has the schema)
├── feedback/           ← Real-time feedback during sessions
├── bugs/
│   ├── manual-fixes.yaml    ← Bugs fixed manually in n8n UI
│   └── platform-bugs.md     ← n8n platform bugs
├── reports/            ← Nightly worker action logs (auto-generated)
└── scripts/
    ├── nightly_worker.py    ← v1 simple
    └── deep_nightly_worker.py  ← v2 with deep scanning + per-action log (ACTIVE)
```

## Nightly Worker Script (`deep_nightly_worker.py`)

Located at `~/.hermes/scripts/deep_nightly_worker.py`.

What it does each night:
1. **file_scan** — check for today's session-logs and feedback files
2. **read manual-fixes.yaml** — check for manually-fixed bugs
3. **system check** — verify cron job status
4. **(future) deep session_search** — query past 24h for "error|bug|fix|mistake|trap"

Output: `/workspace/n8n-wfb/reports/YYYY-MM-DD_actions.json` with full per-action traceability.

**The worker is READ-ONLY.** It scans, reads, analyzes, reports. Never writes to session-logs, feedback, bugs, or any user file. The only write is the JSON action-log in `reports/`.

## Important: Worker Does NOT Write to Trap-Reference

The worker's output feeds the Judge (Hermes), who reviews the report and presents findings to the user. **Judge does not modify files either** — user decides what to patch. This is by design:

```
Worker (nightly) → Judge reviews → User decides → (optional) Skill/trap patch
```

No automated patching. No silent file modifications.

## Session Log Protocol

After every n8n-phase session, the user and judge fill `session-logs/YYYY-MM-DD_session-log.yaml`:

```yaml
session:
  id: ""
  date: "YYYY-MM-DD"
  phase: "intake | planner | reviewer | builder"
  topic: "..."

# User fills these:
user_manual_fixes:
  - symptom: "what went wrong"
    manual_fix: "how I fixed it in n8n UI"
    root_cause: "why it broke"
    n8n_ui_fix: true

user_feedback:
  - topic: "subject"
    detail: "the feedback"
    type: "correction | improvement | best_practice"

user_suggestions:
  - "new idea or capability"

user_missed:
  - "something I felt you misunderstood"

# Judge fills these:
judge_model_mistakes:
  - detail: "what the model did wrong"
    model: "opencode200k"
    in_trap_ref: false

judge_observations:
  - detail: "thing I noticed"
    priority: low | medium | high

judge_stats:
  successful_nodes: N
  failed_attempts: N
  tokens_used: N
```

## Cron Job

```bash
Schedule: 0 2 * * *  (every night at 2 AM)
Job name: n8n-deep-nightly
Script: deep_nightly_worker.py
Delivery: origin (this Telegram chat)
```

## Morning Report Format (Judge → User)

```
📊 **گزارش شبانه 2026-07-10**
━━━━━━━━━━━━━━━━━━━
📂 فایل‌های امروز: [list]
📊 Summary: N success, M errors, K empty
🔍 Findings: [what the worker found]

Suggestions:
- [patch trap-reference?]
- [update SKILL?]
- [investigate X?]
```

## When to Load This Skill

✅ Load BEFORE any nightly cron maintenance, quality review, or improvement session
❌ Never load alongside phase skills (intake/planner/reviewer/builder) — this is a cross-cutting QI system

## Related Skills & Overlap

- `n8n-builder` `references/error-analysis-loop.md` — builder-specific subset of this skill. This umbrella supersedes it for cross-phase quality work.

## Pitfalls

1. **Don't modify user files.** The worker reads and analyzes only. The judge suggests and presents. Only the user decides to patch.
2. **Don't skip the session log.** Without the log, the worker has nothing to analyze. 2 minutes of logging per session saves hours of debugging later.
3. **Don't async-fix trap-refs.** If the judge sees a pattern, present it to the user. Let them decide. The judge who also patches is not a judge.
4. **Don't over-automate.** The value is in the feedback loop, not in full automation. Each phase has a human gate.
