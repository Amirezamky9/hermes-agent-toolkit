---
name: n8n-workflow-pipeline
description: |-
  FULL PIPELINE orchestrator for building n8n workflows on this instance.
  Load this FIRST on any n8n-build request ONLY WHEN no task deck exists.
  If the user provides a deck-*.yaml path directly, skip pipeline and go
  straight to n8n-builder. Maps the user's request to the right phase
  (intake → planner → reviewer → builder → qa), verifies prerequisites,
  directs the next session. DO NOT build workflows directly — delegate to
  phase skills (n8n-intake, n8n-planner, n8n-reviewer, n8n-builder).
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [n8n, pipeline, workflow-builder, orchestration]
    related_skills:
      - n8n-intake
      - n8n-planner
      - n8n-reviewer
      - n8n-builder
      - n8n-qa
      - n8n-quality-improvement
    references:
      - references/setup.md
      - references/phase-reference.md
---

# n8n Workflow Pipeline — Orchestrator

## Overview

The n8n workflow builder on this instance follows a **5-phase pipeline** with a **cross-phase quality improvement system** running in parallel.
Phase 2.5 (n8n-reviewer) sits between Planner and Builder — it decomposes
the human-optimized ARCHITECTURE.md into machine-optimized YAML task decks
so Builder sessions don't overflow their context window.
Each phase is a separate Hermes skill, run in its own single-skill session.
Never mix phases in one chat.

```
User Request
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  Phase 1: n8n-intake                                 │
│  Ask clarifying questions, search similar workflows, │
│  list credentials, output intake.yaml                │
└──────────────────────┬───────────────────────────────┘
                       │ intake.yaml
                       ▼
┌──────────────────────────────────────────────────────┐
│  Phase 2: n8n-planner                                │
│  Read intake, fetch reference workflows, design      │
│  architecture, write ARCHITECTURE.md + task breakdown│
└──────────────────────┬───────────────────────────────┘
                       │ ARCHITECTURE.md
                       ▼
┌──────────────────────────────────────────────────────┐
│  ▶ Phase 2.5: n8n-reviewer (NEW)                    │
│  Decompose ARCHITECTURE.md into YAML task decks      │
│  (≤150 lines, ≤20 nodes each) for LLM-optimized     │
│  builder sessions. Writes manifest.yaml + deck-*.yaml│
└──────────────────────┬───────────────────────────────┘
                       │ deck-*.yaml + manifest.yaml
                       ▼
┌──────────────────────────────────────────────────────┐
│  Phase 3: n8n-builder (per deck)                     │
│  Build Data Tables + Workflows via MCP SDK,          │
│  set credentials, verify. One deck per session.      │
└──────────────────────┬───────────────────────────────┘
                       │ built workflows
                       ▼
┌──────────────────────────────────────────────────────┐
│  Phase 4: n8n-qa (planned but not yet authored)      │
│  Test, execute, validate all workflows               │
└──────────────────────────────────────────────────────┘
```

## 🚨 CRITICAL RULE — THIS SKILL IS ONLY AN ORCHESTRATOR

> **THIS SKILL DOES NOT BUILD WORKFLOWS.** It only:
> 1. Maps the user's request to the right phase
> 2. Verifies prerequisites are met
> 3. Tells the user which skill to load next
>
> **When the user is ready to build, you MUST delegate to n8n-builder.**
> Do NOT attempt to read workflows, write SDK code, validate, or create
> anything from this skill. Always say: «بریم سراغ اسکیل n8n-builder برای فاز ساخت»

## 🚨 CRITICAL RULE — ALWAYS LOAD THE PHASE SKILL

> **When you determine which phase is needed, you MUST:**
> 1. `skill_view('n8n-builder')` (or the relevant phase skill)
> 2. Follow ALL its rules (Golden Rules, Traps, etc.)
> 3. Do NOT skip reading the skill
>
> **Example:**
> ```
> ✅ «بریم سراغ Phase 3. اسکیل n8n-builder رو لود می‌کنم و deck-01b رو می‌سازم»
>    → skill_view('n8n-builder') → read rules → build
> ```
>
> **Failure to load the phase skill = missing critical rules = building wrong.**
> Never build from pipeline context alone.

## 🚨 CRITICAL ZERO — کاربر deck داره → مستقیم برو Builder (اینجا رو لود نکن)

> **اگه کاربر مستقیم مسیر یه deck-*.yaml داده ("ورکفلو ساز رو لود کن و deck-01-*")، یعنی می‌خواد Phase 3 (Builder) رو استارت بزنه — pipeline رو لود نکن!**
>
> در این حالت:
> 1. نگو «پایپلاین لود شد، بریم ببینیم...»
> 2. فوراً بگو «شما deck آماده دارین — مستقیم می‌رم سراغ Builder»
> 3. `skill_view('n8n-builder')` بزن و ادامه بده
>
> **ملاک تشخیص:** اگه کاربر deck-*.yaml یا manifest.yaml رو در پیامش اشاره کرد، یا از session قبلی مشخصه که deck وجود داره → **از pipeline صرف‌نظر کن و مستقیم برو Builder.**

## 🚨 CRITICAL RULE — Pipeline NEVER builds directly

> **This skill must NEVER:**
> - `mcp_n8n_mcp_create_workflow_from_code`
> - `mcp_n8n_mcp_validate_workflow`
> - `mcp_n8n_mcp_update_workflow` (adding nodes)
> - `mcp_n8n_mcp_create_data_table`
> - Any n8n mutation tool
>
> **This skill CAN:**
> - `mcp_n8n_mcp_search_projects` (to find project ID)
> - `mcp_n8n_mcp_search_workflows` (to check existing state)
> - `mcp_n8n_mcp_list_credentials` (to verify prerequisites)
> - `mcp_n8n_mcp_get_sdk_reference` (to know SDK exists)
> - `search_files`, `read_file` (to check if deck files exist)
>
> **Mutation = n8n-builder's job. Discovery = everyone's job.**

## Prerequisites (must be satisfied before any phase)

| Prerequisite | Check | Notes |
|---|---|---|
| **MCP n8n Server** | `hermes mcp list` shows `n8n-mcp` enabled | URL: `https://n8n.mym8m.cloud`, JWT auth |
| **n8n credentials** | At least one api-accessible credential | Load via `list_credentials` mid-pipeline |
| **Hermes CLI in PATH** | `which hermes` finds it | typically `~/.hermes/hermes-agent/hermes` |
| **webhook_wrapper.py** | file exists at `~/.hermes/skills/n8n-builder/webhook_wrapper.py` | shared by intake + planner |

## Which phase to load

Read the user's request and map to the correct starting phase:

| User says… | Load phase skill | Notes |
|---|---|---|
| "ورکفلو ساز رو لود کن" + مسیر deck-*.yaml همراه | **n8n-builder** | ⚡ مستقیم! کاربر deck آماده داره. این اسکیل رو لود نکن! |
| "می‌خوام یه ورک‌فلو بسازم" / "یک ربات تلگرام می‌خوام" | **n8n-intake** | Needs-finding first |
| "این intake.yaml رو ببین" / "نیازمندی‌ها رو گفتم" | **n8n-intake** | They have requirements ready |
| "intake.yaml آماده‌ست" / intake file exists | **n8n-planner** | Jump to architecture |
| "معماری رو نوشتم" / ARCHITECTURE.md exists, >200 lines | **n8n-reviewer** | Decompose first, then build per deck |
| ARCHITECTURE.md small (<200 lines) or "برو ببین چیه" | **n8n-builder** | Jump straight to building |
| "ادامه بده از جایی که موندیم" / "arch.missing" | **n8n-builder** | Resume mode — see builder's Rule 16 |
| "انجام شد deck-01a برو بعدی" / "deck-*.yaml موجوده" | **n8n-builder** | Load builder, read next deck, build |
| "ورک‌فلوهای فعلی رو تست کن" | **n8n-qa** (not yet built) | Manual test for now |
| "نصب کن" / "ستآپ کن" / "راه بنداز" infrastructure | **n8n-workflow-pipeline** (this) | See Setup section |

> **When in doubt, start with n8n-intake.** It asks clarifying questions before committing to anything.

## 🚨 CRITICAL — Builder COMPLETION RULE (ONE deck per session)

After Builder finishes a deck, it **STOPS** and reports:
- What was built
- Which deck is next
- Then WAITS for user to say "برو تسک بعدی"

Builder does NOT auto-proceed to the next deck. This is intentional — each deck is a separate session. If you are the pipeline orchestrator and the user says "deck-01a done, go next", you load Builder for the next deck. Builder itself will build ONE deck, report, and STOP again.

**When the user says "انجام شد deck-NN برو بعدی":**
1. ✅ Load n8n-builder via skill_view
2. ✅ Builder reads the next deck
3. ✅ Builder builds it
4. ✅ Builder reports and STOPS (does NOT proceed to deck after next)
5. ⏳ User says "برو بعدی" again → repeat from step 1

## Pipeline flow rules

1. **One phase per session.** Each phase skill warns at the top of SKILL.md: SINGLE-SKILL SESSION.
2. **Output of one phase = input of next.** Intake writes `intake.yaml`. Planner reads it and writes `ARCHITECTURE.md`. Reviewer reads ARCHITECTURE.md and writes `deck-*.yaml` + `manifest.yaml`. Builder reads a deck + manifest and writes workflows.
3. **No phase skips unless the user explicitly says so.** "از اول می‌خوام" doesn't skip Phase B (search) in intake.
4. **Resume mode (Builder Rule 16):** If ARCHITECTURE.md is missing mid-build, use `session_search` + live n8n tools to reconstruct state.
5. **مهم: بعد از مشخص کردن فاز، حتماً اسکیل مربوطه رو با skill_view لود کن!** بدون لود اسکیل، قوانین طلایی و تله‌ها دیده نمی‌شن.

## Cross-Phase Quality Improvement Loop

Running alongside the pipeline is a **closed-loop quality improvement system**:

```
🌙 2AM Nightly Worker (READ-ONLY):
   Reads session-logs, feedback, manual-fixes
   Deep session_search for missed errors
   Per-action traceability log → reports/

☀️ Judge (Hermes in morning):
   Reads worker report → presents to user
   User decides on patches, no auto-mutations

📝 Session Log Protocol:
   After each phase session:
     User fills: user_manual_fixes, user_feedback, user_suggestions
     Agent fills: judge_model_mistakes, judge_observations, judge_stats
```

See `skill_view('n8n-quality-improvement')` for full documentation. The nightly cron is active at `0 2 * * *` (job: `n8n-deep-nightly`).

| Item | Value |
|---|---|
| n8n URL | `https://n8n.mym8m.cloud` |
| MCP Server | `n8n-mcp` (enabled, JWT Bearer auth via config.yaml) |
| Hermes version | v0.18.0 |
| Node.js | v22.15.0 (system) + nvm v0.40.1 |
| mimo CLI | v0.1.5 at `~/.local/node/bin/mimo` |
| Available credentials | telegramApi (bale_bot_evet_rosteri, @natentestbot), openAiApi, groqApi, postgres, gmailOAuth2, googleCalendarOAuth2Api, trelloApi, httpBearerAuth |

## Skill file map

```
~/.hermes/skills/
├── n8n-intake/              SKILL.md + 11 reference files (patterns, templates, tool-usage)
├── n8n-planner/             SKILL.md + 4 reference files (architecture, modules, telegram-bot)
├── n8n-reviwer/             SKILL.md + 2 reference files (task-deck-schema, review-workflow)
├── n8n-builder/             SKILL.md + references/ + webhook_wrapper.py
│   └── references/          agents.md, trap-reference.md, update-workflow.md,\n│                            error-analysis-loop.md, testing-with-pin-data.md,\n│                            node-sdk-patterns.md, expression-syntax.md,\n│                            inline-keyboard.md, workflow-debugging-checklist.md,\n│                            same-trigger-parallel-branches.md, bale-telegram-api.md
├── n8n-patterns/            کاتالوگ پترن‌های دامنه (Planner/Reviewer فقط)
│   └── references/          chatbot.md, scraping-node-schemas.md, kie-ai-guide.md, ...
├── n8n/                     umbrella skills
│   ├── n8n-workflow-pipeline/    ← THIS SKILL
│   ├── n8n-quality-improvement/  کارگر شبانه و گزارش
│   └── n8n-workflow-analyzer/    تحلیلگر JSON ورک‌فلو
└── n8n-qa/                  (not yet created)
```

> **درباره `n8n-patterns`:** این اسکیل یک کاتالوگ مرجع برای **Reviewer** است تا هنگام نوشتن deck پارامترهای دقیق نودها را از رفرنس‌هایش دریافت کند (`skill_view('n8n-patterns', file_path='references/20-telegram.md')`). Planner هم می‌تواند ایندکس را ببیند. Builder از n8n-patterns استفاده نمی‌کند — رفرنس‌های SDK خودش (`references/*`) کافی است. همه فایل‌های پترن در `n8n-patterns/references/` قرار دارند، نه در `/workspace/n8n-best-practices-mcp/`.

## Reference files

- `skill_view('n8n-workflow-pipeline', file_path='references/setup.md')` — full install/verification steps
- `skill_view('n8n-workflow-pipeline', file_path='references/phase-reference.md')` — phase details

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `hermes: command not found` | PATH not set | `export PATH="$HOME/.hermes/hermes-agent:$PATH"` (persist in .bashrc) |
| MCP tools respond empty | Server down or auth expired | Check config.yaml for JWT token. Re-add via `hermes mcp add` |
| `webhook_wrapper.py` not found | Builder skill not installed | Run the skill-install procedure below |
| `mimo: command not found` | Node global bin not in PATH | `export PATH="/home/hermeswebui/.local/node/bin:$PATH"` |
| `Bad Request: callback_query_id` | AnswerCallbackQuery without continueOnError | Set `onError: continueRegularOutput` on the node |
