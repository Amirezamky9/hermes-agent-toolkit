---
name: telegram-miniapp-development
description: >-
  Build Telegram Mini Apps — architecture decisions, SDK selection, authentication,
  UI frameworks, charting, RTL/Persian support, deployment. Covers the full lifecycle
  from architecture planning through MVP to production. Use when the user asks about
  building, designing, or deploying a Telegram Mini App, or when researching tech
  stacks for Telegram-based web applications.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram, mini-app, webapp, react, architecture, persian]
    related_skills: [web-research, realtime-web-apps, telegram-hybrid-bot]
---

# Telegram Mini App Development

## Overview

Telegram Mini Apps are **web applications rendered in Telegram's WebView**. They are
technically standard web apps (HTML/CSS/JS) served at a URL that Telegram loads in
a WebView component inside the Telegram client. This means any web framework works,
but the Telegram SDK ecosystem heavily favors **React**.

## When to Use

Triggers: "telegram mini app", "mini app", "telegram webapp", "twa", "telegram bot
webapp", "build a mini app", "telegram frontend", "@tma.js", "telegram-ui".

## Architecture Fundamentals

### What a Mini App Actually Is
- A standard web app (static files: .js, .css, .html) served at an HTTPS URL
- Telegram loads this URL in a WebView inside the Telegram client
- The app communicates with Telegram via `@tma.js/sdk` (JS bridge)
- No server-side rendering needed (SSR is wasteful — it's a single-user WebView)
- Mobile-first design is mandatory (WebView on phones)

### Key Telegram Bot API Features for Mini Apps
Source: core.telegram.org/bots/webapps (checked Jul 2026)

| Feature | Bot API Version | Notes |
|---------|----------------|-------|
| ThemeParams (dark/light sync) | 6.1+ | Real-time color theme from Telegram |
| BiometricManager | 7.2+ | Biometric auth in-app |
| CloudStorage | 6.9+ | Key-value storage in Telegram cloud |
| Full-screen mode | 8.0+ | Portrait and landscape |
| Home screen shortcuts | 8.0+ | Add to device homescreen |
| DeviceStorage | 9.0+ | Persistent local storage on device |
| SecureStorage | 9.0+ | Secure local storage for sensitive data |
| Geolocation | 8.0+ | Location access with permission |
| BottomButton / SecondaryButton | 7.10+ | Native bottom bar buttons |
| requestChat | 9.6+ | Request chat access |

### Authentication Pattern
**InitData + JWT (recommended)**
1. Mini App opens → `@tma.js/sdk` provides `initData` (contains user info + HMAC hash)
2. Backend validates `initData` using bot token (HMAC-SHA256) via `@tma.js/init-data-node`
3. Backend issues JWT token → stored in Mini App
4. All subsequent API calls use JWT in Authorization header

**Do NOT build a separate login flow.** Telegram already authenticated the user.

## SDK Ecosystem (as of Jul 2026)

### @tma.js — Official Community SDK
Source: github.com/Telegram-Mini-Apps/tma.js

| Package | Version | Maturity |
|---------|---------|----------|
| `@tma.js/sdk` | 3.3.0 | ✅ Mature |
| `@tma.js/sdk-react` | 3.0.23 | ✅ **Most mature** — highest adoption |
| `@tma.js/sdk-solid` | 3.0.23 | ⚠️ v1.x API |
| `@tma.js/sdk-vue` | 1.0.23 | ⚠️ v1.x API |
| `@tma.js/sdk-svelte` | 1.0.23 | ⚠️ v1.x API |
| `@tma.js/init-data-node` | 2.0.8 | ✅ Server-side validation |

**Recommendation: React.** The SDK ecosystem, community examples, and UI toolkit all
heavily favor React. Vue/Svelte SDKs exist but are v1.x and have less community support.

### @telegram-apps/telegram-ui — Official UI Component Library
- **React-only** (no Vue/Svelte/Solid support)
- Components follow iOS HIG + Android Material Design
- Supports Telegram's native color scheme
- Includes: AppRoot, Placeholder, Button, Cell, Input, List, Tabs, etc.
- Figma files available for design

## Frontend Technology Stack

### Recommended Stack
```
React 18+ / TypeScript / Vite
@tma.js/sdk-react          ~15kB gzip
@telegram-apps/telegram-ui ~20kB gzip
Chart.js + react-chartjs-2  ~66kB gzip (for dashboards)
Framer Motion               ~30kB gzip (for animations)
TailwindCSS                 ~10kB gzip
```
**Total: ~140kB gzipped** — acceptable for WebView.

### Charting Library Comparison (bundle sizes)
Source: bundlephobia.com (checked Jul 2026)

| Library | Min | Gzip | Best For |
|---------|-----|------|----------|
| **Chart.js** | 194kB | **66kB** | **Best balance** — bar, line, pie, doughnut |
| Recharts | 483kB | 117kB | React-native feel, heavier |
| uPlot | ~35kB | ~13kB | Time series only, no pie/doughnut |
| lightweight-charts | 160kB | 50kB | Financial charts only |
| ECharts | 1MB | 325kB | ❌ Too heavy for Mini App |
| @ant-design/charts | 2.1MB | 584kB | ❌ Way too heavy |

**For POS dashboards (completion rates, streaks, trends, progress): Chart.js is ideal.**

### Why NOT Next.js?
- Mini App is a SPA in WebView — no SEO, no SSR benefit
- Vite is lighter and faster to build
- Smaller bundle = faster load in WebView
- Next.js adds unnecessary complexity (routing, API routes, etc.)

## Backend Architecture

### Recommended: FastAPI (Python)
- Async-native, auto-generates Swagger docs
- Pydantic for validation (TypeScript codegen possible)
- Direct integration with Python AI ecosystem
- SQLAlchemy ORM works with both SQLite and PostgreSQL

### Backend ↔ n8n Communication Pattern
```
Backend → n8n: Webhooks (trigger workflows)
n8n → Backend: REST API calls (write results back)
```
Key principle: **Backend is always the Source of Truth.** n8n only does workflow/AI.

## Database Strategy

### SQLite for MVP → PostgreSQL for Scale
- SQLite: zero-config, file-based, perfect for single-user personal app
- PostgreSQL: when scaling to multi-user SaaS or needing advanced FTS
- SQLAlchemy handles both — migration is just changing the connection string
- FTS5 supports Unicode/Farsi text search adequately

## RTL / Persian Language Support

### CSS Patterns for RTL
- TailwindCSS: use `rtl:` modifier (`rtl:text-right`)
- HTML: `<html lang="fa" dir="rtl">`
- Font: IRANYekan from fontiran.com (standard Iranian web font)
- Date handling: use `@persian-tools/persian-date` for Shamsi calendar

### Persian-specific Considerations
- Number display: support both Western (1,2,3) and Persian (۱,۲,۳) numerals
- Form validation messages in Farsi
- RTL layout mirroring for all directional elements

## Deployment

### Docker Compose (no separate SQLite service)
```yaml
services:
  backend:    # FastAPI + uvicorn
  miniapp:    # Built React app served by Caddy
  n8n:        # n8nio/n8n image
  caddy:      # Reverse proxy + auto-HTTPS
# SQLite: just a volume mount on backend, NOT a separate service
```

### Web Server: Caddy (not Nginx)
- Auto-HTTPS with zero config
- Simpler than Nginx for this use case
- Caddyfile is more readable

## Real-Time Communication

### Use SSE, NOT WebSocket
Source: Official Telegram docs + production experience (Jul 2026)

**WebSocket is fragile in Telegram WebView.** The WebView lifecycle (minimize,
resume, background) causes WebSocket connections to drop without proper close
events. Reconnection logic is complex and unreliable across Telegram clients
(Android, iOS, Desktop, Web).

**Server-Sent Events (SSE) is the recommended approach:**
- SSE auto-reconnects natively (EventSource API)
- Simpler than WebSocket (unidirectional: server→client)
- Works reliably across all Telegram clients
- FastAPI: use `sse-starlette` package
- React: use native `EventSource` API or `@microsoft/fetch-event-source`

**Pattern:**
```
Client→Server: REST API calls (any HTTP method)
Server→Client: SSE stream (push updates, notifications, AI responses)
```

**Never use WebSocket for Telegram Mini Apps.** It breaks on app minimize/resume.

### SSE Event Types
For a Personal OS app, typical SSE events:
- `habit_reminder` — time to do a habit
- `task_reminder` — task deadline approaching
- `ai_response` — streaming AI agent response
- `timeline_update` — new event logged
- `daily_reflection` — nightly reflection prompt

## 3-Layer Storage System (Bot API 9.0+)

Telegram provides three storage layers (since April 2025):

| Storage | Scope | Capacity | Use Case |
|---------|-------|----------|----------|
| **CloudStorage** | Synced across devices | 1024 items × 4KB | User preferences, settings |
| **DeviceStorage** | Local, persistent | 5MB per user | Offline cache, app state |
| **SecureStorage** | Local, encrypted | 10 items per user | Tokens, secrets, auth state |

**Usage in Mini App:**
```javascript
// CloudStorage (synced across devices)
Telegram.WebApp.CloudStorage.setItem('theme', 'dark', callback);
Telegram.WebApp.CloudStorage.getItem('theme', callback);

// DeviceStorage (local, 5MB)
Telegram.WebApp.DeviceStorage.setItem('cache', JSON.stringify(data));

// SecureStorage (encrypted, 10 items only)
Telegram.WebApp.SecureStorage.setItem('auth_token', token);
```

**Recommended allocation:**
- SecureStorage: auth token, refresh token (2 of 10 slots)
- CloudStorage: theme preference, language, active workspace (small items)
- DeviceStorage: timeline cache, offline queue, large datasets

## Third-Party Auth Validation (Bot API 8.0+)

If sharing auth data with a third party (e.g., n8n), they can validate Telegram
initData **without your bot token** using Ed25519 signature verification:
- Use Telegram's public keys (test + production)
- Data-check-string format: `bot_id:WebAppData\n<sorted fields>`
- n8n can validate directly — no need to proxy through your backend

**Public keys:**
- Test: `40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec`
- Prod: `e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d`

## Personal Productivity Mini App Pattern

For a personal productivity Mini App with tasks, routines, courses, reminders, and AI planning, avoid copying a single competitor wholesale:

- Use **task-first clarity**: make `Today` the home screen, with the next meaningful action before secondary modules.
- Use a **daily planning ritual**: morning check-in collects capacity/energy; evening reflection closes the loop.
- Use **gentle motivation**, not guilt: a missed task offers reschedule, reduce, skip-with-reason, or reflection. Never frame a broken streak as failure.
- Keep broad capability behind progressive disclosure. Calendar, courses, analytics, settings, and reports must not compete with today’s work on the home screen.
- Prefer lightweight reward feedback (haptic completion, small milestone celebration, visible momentum) over RPG economies, loot, leaderboards, or a persistent gamified shell.

### Adaptive planning

A user can explicitly enter a low-energy/difficult-day mode. The planner should propose a smaller realistic plan, minimum viable versions of routines, and rescheduling of unfinished work. Preserve completed history; only change future proposed/unscheduled occurrences after the user confirms.

### Long-horizon course planning

Let the user provide each course’s total duration or session count plus a deadline. Compute the required pace, create a proposed daily/weekly allocation, and update future allocations plus goal/progress projections when a course is added or progress changes. Do not rewrite completed historical data.

### End-of-day learning loop

Persist task lifecycle timestamps (`created`, `planned`, `interaction/start`, `completed`, `deferred`, `skipped`) and an optional skip/defer reason. The nightly reflection agent uses only that user-scoped data to ask exploratory questions about delay or non-completion, then saves a structured report for weekly analysis. It must phrase patterns as hypotheses for the user to confirm, never as diagnoses or labels such as “lazy.”

### Design implementation checklist

- Mobile Telegram is the primary target; desktop is responsive but secondary.
- Respect Telegram light/dark/custom theme tokens, safe areas, dynamic type, reduced motion, and lower-performance devices.
- Use Telegram MainButton only for the single critical action in a flow; use native Telegram dialogs for destructive/system actions.
- Use haptic feedback for completion and validation, skeletons for loading, and explicit offline/reconnecting plus retry states.
- For RTL Persian interfaces, design icon direction, touch behavior, typography, and Jalali/Gregorian display natively rather than applying RTL as a late CSS override.

## n8n Integration Pattern (Webhook-Only)

When using n8n for AI agent orchestration alongside a Python/FastAPI backend:

**Architecture principle:** All AI agent work happens in n8n. Communication is
webhook-only. n8n manages chat memory/history. FastAPI is the data Source of Truth.

```
FastAPI → n8n: POST webhook (trigger agent workflow with user context)
n8n → FastAPI: POST webhook (return agent result to save in DB)
```

**Why n8n over Python-native AI frameworks (LangGraph, CrewAI) for early phases:**
- Visual workflow builder = faster iteration
- Built-in monitoring/debugging of every agent execution
- Memory management handled by n8n nodes
- No extra Python dependencies needed
- Telegram node built-in for notifications

**When to migrate away from n8n:** When the product matures and performance
or latency becomes critical, integrate agent logic directly into FastAPI.
This is a standard evolution path, not a rewrite.

## Architecture Document Workflow

When designing architecture for a new project:

1. **Read the spec** — understand all requirements
2. **Research tech choices** — parallel subagents for independent questions
3. **Create architecture docs** — one file per concern (frontend, backend, DB, etc.)
4. **Include ALL open questions** — write them INTO the architecture document
   so the user can review and answer before coding begins
5. **Use diagrams** — ASCII art for system architecture, data flow, ER diagrams
5. **Wait for user feedback** — don't start coding until architecture is approved
6. **Cascading updates after feedback** — when the user answers questions or
   provides feedback, update ALL affected architecture files, not just the
   relevant one. Example: user says "no meal logging" → update:
   - `09-DECISIONS.md` (new decision)
   - `07-QUESTIONS.md` (mark as answered)
   - `02-FRONTEND.md` (remove meal-related components)
   - `03-BACKEND.md` (remove meal API endpoints)
   - `04-DATABASE.md` (remove meal fields from models)
   - `05-N8N-AGENTS.md` (remove meal-related agent logic)
   Use a todo list to track which files are updated.
7. **Review external documents** — if the user sends prior design docs, PDFs, or
   references, compare them against the current architecture. Produce a dedicated
   comparison file (e.g. `10-OLD-DESIGN-ANALYSIS.md`) categorizing findings into
   🔴 Must-have, 🟡 Nice-to-have, 🔵 Optional. Update `07-QUESTIONS.md` with any
   new questions the review surfaces.

**Critical: Split large documents.** Architecture docs with full code examples,
diagrams, and detailed specs easily exceed 30KB. The `write_file` tool has a
stream timeout for very large content. Always split into multiple files:
- `01-OVERVIEW.md` — system diagram, principles, tech stack summary
- `02-FRONTEND.md` — pages, components, routing, state
- `03-BACKEND.md` — API, auth, services, n8n integration
- `04-DATABASE.md` — models, relations, indexes, queries
- `05-N8N-AGENTS.md` — workflows, system prompts, memory
- `06-DEPLOYMENT.md` — Docker, env vars, CI/CD
- `07-QUESTIONS.md` — ALL open decisions and questions
- `08-ROADMAP.md` — phased development plan
- `09-DECISIONS.md` — finalized decisions from user answers
- `10-*.md` — additional analysis files (old design comparison, etc.)

### Canonical Roadmap for Cross-Chat Continuity

For a greenfield or long-running Mini App, create `docs/ROADMAP.md` before implementation and treat it as the resume point for every new chat. It should record: current phase, confirmed architecture decisions, open questions, target system diagram, delivery order, and the exact next step. Update it at the end of each material session: mark completed items, move answered questions into decisions, and replace the next-step section. Keep it project-local rather than relying on chat history or agent memory. If legacy design documents conflict, label the roadmap as the current canonical direction until a reviewed decision supersedes it.

When pausing before implementation, also create `docs/NEXT-CHAT-HANDOFF.md`. It must state the approved scope and exclusions, non-negotiable boundaries, exact gstack sequence, remaining decisions, and an exact copy-paste prompt for the next chat. Explicitly say what has **not** started, so a new agent does not prematurely scaffold, initialize Git, install app dependencies, or create workflows.

**Fatigue/headache is a hard workflow stop.** If the user asks to wrap up because of fatigue, stop all decision prompts immediately. Mark the active review `in progress; intentionally paused` rather than complete, preserve the exact pass/step and confirmed visual choices, replace stale resume prompts, write an append-only checkpoint, and verify the saved state from disk. Use [references/fatigue-safe-r0-handoff.md](references/fatigue-safe-r0-handoff.md) for the complete procedure and checkpoint template.

### Configurable n8n AI Boundary

If the user wants AI to remain fully configurable in n8n, make FastAPI and the Mini App model-agnostic. n8n exclusively owns provider/model selection, credentials, system prompts, agent memory, tools, guardrails, fallbacks, cost controls and workflow behavior. FastAPI remains the user-scoped source of truth: it authenticates calls, validates structured proposals, writes approved mutations, and exposes allowlisted internal APIs. Do not put model identifiers, prompt text, or AI credentials into the app backend/frontend.

For user chat sessions, use session-bounded memory. A new user-created session must not receive the previous transcript by default. Prefer compact, purpose-specific summaries and scoped retrieval of current plans/reports through FastAPI over injecting an entire history. Design deletion/export semantics for AI sessions and reflection reports before launch.

### Planner Reality Checks

For course/deadline planning, compare required workload to actual user availability before finalizing a plan. If it cannot fit, expose the conflict and offer increase-time, reduce-concurrent-load, move-deadline, or explicitly-warned intensive-plan options. Never silently create an impossible plan. Preserve completed historical records when changing a future plan.

For low-energy days or multi-day absence, produce a user-confirmed lighter recovery proposal for future work, not an overwhelming backlog. Keep the tone non-punitive.

### HTML Report Delivery

Telegram messages support limited HTML formatting, not a full rendered HTML document. When n8n generates a detailed HTML weekly report, explicitly choose and document the delivery transport: attach the `.html` document, host an authenticated/deep-linked report page, or both. Do not promise that `sendMessage` alone will render a full report.

## Dynamic User-Specific Design (CRITICAL)

**Every multi-user app MUST follow this principle. Nothing is hardcoded.**

Each user has their own unique schedule, habits, tasks, courses, goals, reminders,
and dashboard. The system generates everything dynamically per-user.

```python
# ❌ WRONG — hardcoded
REMINDER_TIME = "08:00"           # All users get reminded at 8
MAX_TASKS = 10                    # All users have 10 tasks
COURSE_DAYS = ["sat", "mon"]      # All users have class on Sat/Mon

# ✅ CORRECT — dynamic
reminder_time = user.settings.morning_checkin_time   # Each user's own time
max_tasks = calculateFromAvailableHours(user.profile) # Based on their availability
course_days = course.schedule.preferred_days          # Each course's own schedule
```

**Data relationships — every entity ties to a user:**
```
users → user_settings (1:1)
users → user_profile (1:1)       # goals, limitations, preferences
users → onboarding_data (1:1)    # courses, tasks, routines from wizard
users → workspaces (1:N)
workspaces → habits (1:N)        # each habit has its OWN schedule
workspaces → tasks (1:N)         # each task has its OWN time_slot
workspaces → courses (1:N)       # each course has its OWN schedule
users → timeline_events (1:N)
users → morning_checkins (1:N)
users → weekly_goals (1:N)
```

**Dynamic reminder generation — per-user, per-habit, per-task:**
```python
# Generate reminders for ONE user based on THEIR schedule
reminders = []
for habit in user.habits:
    if is_scheduled_today(habit, date):
        for time in habit.schedule.times:
            reminders.append(Reminder(time=time, habit=habit))
for task in user.tasks:
    if task.scheduled_time:
        reminders.append(Reminder(time=task.scheduled_time, task=task))
```

**Dashboard is always personalized** — never show aggregate or other users' data.

**AI context is always personal** — system prompt + user profile + user history.

## User Preferences (Persian-speaking, production-focused)

**Core principle: Do NOT over-engineer.** If the user says a category isn't needed
(for a personal app with limited users), DO NOT add it. Redis, CDN, load balancing,
multi-worker, advanced CI/CD — these are overkill for a personal Telegram Mini App.
Always ask: "does this actually matter for N users?" before adding infrastructure.

**Deliver prompts, not fixes.** When the user says "پرامپت بده بدم میمو" (give me a
prompt to give to MiMo), they want a ready-to-paste prompt file — NOT for you to
implement the fix yourself. Prepare the prompt, save it as a `.md` file, and let
the user feed it to their AI coding agent.

**Separate fix files > single mega document.** When creating production fix guides,
write ONE `.md` file per fix category (e.g., `FIX-01-RATE-LIMITING.md`,
`FIX-02-ALEMBIC.md`). Users give these to MiMo Code one at a time. A single
massive file is overwhelming and hard to iterate on.

**Simple file delivery.** When the user asks for a zip/archive:
1. `tar -czf NAME.tar.gz PATH/` in `/workspace/` — done
2. Do NOT try HTTP servers, do NOT copy to `/home/hermeswebui/`, do NOT use MEDIA: for tarballs
3. The file at `/workspace/NAME.tar.gz` is visible in the WebUI file browser

**Tick-mark checklists.** "با تیک بهم نشون بده" = show with ✅/❌ ticks. Users think
in percentages and scores ("46% → 80%"), not prose. Always use tables with status
columns. The number matters more than the explanation.

**Workflow: prepare prompts, user orchestrates MiMo.** The standard flow is:
1. You analyze and prepare mega prompts / fix prompts / review prompts
2. User feeds them to MiMo Code
3. User reports results back to you
4. You interpret results and prepare next prompts
This is NOT a "you do everything" workflow — the user actively participates via MiMo.

## Common Pitfalls

1. **Don't build a separate auth system.** Telegram already authenticated the user.
   Use InitData validation + JWT. See @tma.js/init-data-node.

2. **Don't let n8n access SQLite directly.** n8n should NEVER mount or read the
   SQLite database file. Instead: n8n calls a FastAPI backup endpoint via HTTP
   webhook, and FastAPI handles the export/convert/import logic. This keeps
   n8n stateless, avoids SQL dialect incompatibilities (SQLite dump ≠ PostgreSQL),
   and maintains security (backup endpoint protected by API key).
   ```yaml
   # ❌ WRONG — n8n gets direct file access
   n8n:
     volumes:
       - ./data:/data

   # ✅ CORRECT — n8n only makes HTTP requests
   n8n:
     environment:
       - BACKEND_URL=http://backend:8000
       - BACKUP_API_KEY=${BACKUP_API_KEY}
   ```

2. **Don't use heavy UI libraries.** ECharts, Ant Design, Material UI are too large
   for WebView. Stick to @telegram-apps/telegram-ui + Chart.js.

3. **Don't forget theme sync.** Mini Apps receive Telegram's color theme in real time.
   Use ThemeParams to match dark/light mode. Ignoring this makes the app feel
   "foreign" inside Telegram.

4. **Don't use SSR frameworks.** Next.js, Nuxt.js add unnecessary overhead for a
   WebView SPA. Use Vite.

5. **Don't treat SQLite as a service.** No Docker container needed — it's a file.
   Just mount a volume.

6. **Don't build chat as a text bot.** The Mini App IS the interface. The bot
   backend only handles webhook communication and push notifications.

7. **Validate initData server-side.** Never trust client-side Telegram data without
   HMAC validation using the bot token.

8. **Don't use WebSocket for real-time.** It breaks when the Mini App is minimized
   or backgrounded in Telegram's WebView. Use SSE (Server-Sent Events) instead.
   SSE auto-reconnects and works reliably across all Telegram clients.

9. **Don't write architecture docs as one massive file.** Split into multiple files
   (one per concern) to avoid tool timeouts and improve readability. Always
   include an explicit questions/decisions file.

10. **Don't skip questions in architecture docs.** Include every open decision,
    unknown, and tradeoff. Users review architecture before coding — if questions
    are missing, they surface mid-implementation and cause rework.

11. **Don't try to `read_file` on PDFs.** Raw PDF bytes are unreadable. Use PyPDF2:
    ```python
    from PyPDF2 import PdfReader
    reader = PdfReader(path)
    text = ''.join(page.extract_text() for page in reader.pages)
    ```
    Install with `pip install PyPDF2` if not available. Do NOT attempt `pdftotext`
    (often not installed). If PyPDF2 also fails (scanned/image PDF), use
    `vision_analyze` as a last resort.

12. **When reviewing external design docs, always produce a comparison report.**
    Categorize findings into: 🔴 Must-have (add to current architecture),
    🟡 Nice-to-have (defer to later phase), 🔵 Optional (skip for now).
    Write results to `ARCHITECTURE/10-OLD-DESIGN-ANALYSIS.md` or similar.
    Also update `07-QUESTIONS.md` with any new questions the review surfaces.

13. **When user feedback changes scope, update ALL files.** Architecture files
    are interconnected — a decision in `09-DECISIONS.md` affects frontend
    components, backend endpoints, database models, and n8n workflows. Use a
    todo list to track which files are updated. Missing a file causes
    inconsistencies that surface during implementation.

14. **Don't hardcode user-specific values.** When the user says "don't make it
    hardcoded" or "each user is different", this is a CRITICAL architectural
    signal. Audit every config value, every constant, every default — ask
    "is this the same for all users?" If yes, it belongs in user_settings
    or user_profile. This applies to: reminder times, task limits, course
    schedules, habit frequencies, dashboard data, AI prompts, notification
    messages.

15. **Always validate workspace ownership on write operations.** When creating
    habits, tasks, or courses, always verify that the workspace belongs to
    the current user. Without this check, User A can create data in User B's
    workspace by passing an arbitrary workspace_id. Every create/update/delete
    service method must verify ownership:
    ```python
    workspace = await db.get(Workspace, data.workspace_id)
    if not workspace or workspace.user_id != user_id:
        raise NotFoundError("workspace")
    ```

16. **Don't let AI coding agents hardcode workspace_id.** When feeding mega
    prompts to MiMo/Claude/Codex, explicitly warn: "NEVER hardcode
    workspace_id. Always fetch the user's active workspace first." This is
    the #1 bug AI agents introduce in multi-user apps.

17. **Don't present production readiness as prose.** Users want tick-mark checklists
    with scores, not paragraphs explaining what's missing. Use the 13-category
    production checklist (see references/production-readiness-checklist.md). Present
    results as a table with ✅/❌ and a total percentage. Users think in "how close
    are we?" not "what should we do?". The score (e.g., "46%") is more actionable
    than a list of issues.

18. **Don't over-engineer for personal apps.** When the user says "don't add X if
    it's not needed", respect it. For a personal app with limited users: Redis is
    overkill, CDN is overkill, load balancing is overkill, full CI/CD is overkill.
    Focus on the 6 core categories: Frontend, API, Database, Auth, Security, Logging.
    If you add infrastructure the user didn't ask for, they will be frustrated.
    Ask: "does this actually matter for N users?" before adding anything.

19. **Separate fix files > one mega document.** When creating production fix guides,
    write ONE `.md` file per category (FIX-01-RATE-LIMITING.md, etc.). Users give
    these to their AI coding agent one at a time. A single 300-line file is
    overwhelming and impossible to iterate on. See
    references/production-fix-file-pattern.md for the template.

20. **Onboarding data MUST transition to operational tables.** Wizard-based apps
    collect structured data in onboarding (courses, habits, tasks, routines) but
    often store it as JSON blobs in a single `onboarding_data` table. If there's
    no service method that transforms this JSON into actual `habits`, `tasks`,
    `courses`, and `workspaces` records on onboarding completion, the user's
    setup data is dead — they filled the wizard but nothing works after.
    The onboarding completion endpoint must: (1) create a workspace, (2) parse
    the JSON and create operational records, (3) mark `completed = true`.

21. **Rate limiting config without middleware is security theater.** Defining rate
    limits in a Python dict or YAML file does nothing if no middleware reads that
    config and enforces it. After defining rate limits, verify the middleware is
    actually registered in the FastAPI app (via `app.add_middleware()` or a
    dependency). Common mistake: config file exists, endpoint definitions exist,
    but the middleware that enforces them was never wired.

22. **Alembic migrations are not optional.** Using `Base.metadata.create_all()`
    on startup works for prototyping but means: (a) schema changes require
    dropping and recreating tables (data loss), (b) production deployments
    can't safely evolve the schema, (c) multiple instances may race on schema
    creation. Set up Alembic from day one, even if you only have one migration.
    The first migration should be generated from the existing models, not written
    by hand.

23. **Vite proxy is MANDATORY for full-stack dev.** When frontend (Vite on :5173)
    and backend (FastAPI on :8000) run separately, Vite must proxy `/api/*` to
    the backend. Without it, ALL API calls go to localhost:5173 and return 404.
    This is silent — no console error, just empty/error states on every page.
    ```typescript
    // vite.config.ts
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    ```
    **Symptom:** Dashboard shows "خطا در بارگذاری اطلاعات", Tasks/Habits stuck
    on loading spinner, all pages show error state despite valid auth token.

23b. **Vite cache hides CSS changes.** After significant CSS/style changes, if the
     browser still shows old styles despite Vite HMR reporting updates:
     1. Delete `node_modules/.vite` and restart the dev server
     2. Tell the user to hard-refresh: `Ctrl+Shift+R` (Win/Linux) or `Cmd+Shift+R` (Mac)
     3. Alternatively: F12 → Network tab → check "Disable cache" → refresh
     This is separate from the proxy issue (23) — the CSS file IS being served
     correctly, but the browser caches the old version aggressively.

24. **Backend SQLite needs data/ directory.** FastAPI + aiosqlite crashes on startup
    with `unable to open database file` if the directory doesn't exist. Create it
    before first run: `mkdir -p backend/data`. The DB URL is relative
    (`sqlite+aiosqlite:///./data/pos.db`), so it depends on CWD.

25. **Dev-mode auth bypass for testing.** When `BOT_TOKEN` is empty and `ENV=development`,
    the auth service skips HMAC hash validation. This allows creating test users
    with fake initData for QA testing:
    ```bash
    CURRENT_TIME=$(date +%s)
    USER_DATA=$(python3 -c "import urllib.parse; print(urllib.parse.quote('{\"id\":12345678,\"first_name\":\"Test\"}'))")
    curl -X POST http://localhost:8000/api/v1/auth/validate \
      -H "Content-Type: application/json" \
      -d "{\"init_data\": \"user=${USER_DATA}&auth_date=${CURRENT_TIME}\"}"
    ```
    Returns a valid JWT without Telegram. Only works in dev mode.

26. **Design: use AI mockups, not incremental CSS.** For Telegram Mini Apps, manual
    CSS improvements (adding hover states, color variables, animations) produce
    generic-looking results. Users expect polished, Telegram-native designs.
    Use gstack design tools for AI-generated mockups:
    - `design generate --brief "..." --output mockup.png` — single mockup
    - `design variants --brief "..." --count 3 --output-dir variants/` — multiple options
    - `design evolve --screenshot current.png --brief "make it calmer"` — iterate
    Requires OpenAI API key with image generation permissions
    (`~/.gstack/openai.json` or `OPENAI_API_KEY` env var).
    Without API key: use `design-html` skill to generate production HTML/CSS
    from a text description instead. See references/gstack-design-tools.md
    for the full decision tree.

27. **Don't over-process design.** Users get frustrated with multi-phase design
    consultation workflows ("بابا خیلی ساده این چیه ناموسا"). The 5-phase
    `/design-consultation` skill (context → research → proposal → drill-down →
    preview) is too heavy for users who want quick, visible results. Instead:
    - Skip to concrete proposals fast — present ONE coherent package, not
      separate questions for font, color, layout
    - Show screenshots early — seed test data, take screenshots, let user see
      results before debating theory
    - If user says "ساده" or "اشغال" — they want less process, not more options
    - Prefer `/design-html` (generate and show) over `/design-consultation`
      (talk and plan) when user is visually oriented
    The design skill has its place, but lead with results, not process.

28. **Glassmorphism works for RTL Persian apps.** Concrete CSS patterns that
    produced premium-looking results in Telegram Mini Apps:
    - Floating bottom nav: `position: fixed; bottom: 12px; border-radius: 20px;
      backdrop-filter: blur(20px); background: rgba(255,255,255,0.95)`
    - Glass cards: `background: rgba(255,255,255,0.7); backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.3)`
    - Gradient stat cards: `background: linear-gradient(135deg, #2563EB, #7C3AED)`
    - Mesh background: `background: radial-gradient(at 40% 20%, #2563EB22 0px,
      transparent 50%), radial-gradient(at 80% 0%, #7C3AED22 0px, transparent 50%)`
    - Staggered animations: `animation: slideUp 0.4s ease-out both;
      animation-delay: ${index * 60}ms`
    Use IRANSansX (not Vazirmatn) for modern Persian typography.
    These patterns work well on Telegram WebView's limited rendering engine.

29. **NEVER rewrite globals.css from scratch.** When updating a design system in a
    Tailwind v4 + React project, always preserve ALL existing class definitions
    when adding new ones. Removing legacy utility classes (card-mobile, input-mobile,
    grid-mobile-*, shadow-lg, text-heading-*, animate-*, etc.) that components
    depend on causes white/blank pages with zero JS errors — the most confusing
    failure mode. **Pattern:** Add new premium classes (card-glass, card-gradient,
    bottom-nav, header-gradient, mesh-bg) ALONGSIDE old ones. Use `patch` mode
    to append, never `write_file` to replace. If you must rewrite, diff the old
    and new files and ensure every class referenced by any .tsx component is
    preserved. Verify with: `grep -r "className=" src/ | grep -oP 'class-\w+|[a-z]+-[a-z]+(-[a-z]+)*' | sort -u` and cross-check against CSS definitions.
    
30. **Seed test data before showing design.** Empty-state UI looks bad and
    users can't evaluate design quality. Before showing screenshots for design
    review: create test users via fake Telegram auth (dev mode), seed tasks,
    habits, check-ins. The extra 5 minutes of seeding dramatically improves
    the user's perception of the design. See pitfall 25 for the auth bypass
    pattern.

31. **Don't patch auto-generated gstack skills.** Skills under
    `~/.hermes/skills/gstack/.hermes/skills/` are auto-generated from templates
    (`bun run gen:skill-docs`). Patching them is wasted work — changes get
    overwritten on next gstack update. Add learnings to project-specific skills
    (like this one) or reference files instead.

## Mega Prompts for AI Coding Agents

When delegating implementation to an external AI coding agent (MiMo Code,
Claude Code, Cursor, Codex, etc.), prepare comprehensive mega prompts.

**Structure of a mega prompt:**
```
# [Feature Name] — Mega Prompt for AI Agent

## Task
Clear description of what to build.

## What to Build
- Complete code examples (copy-pasteable)
- File paths (exact, not vague)
- Dependencies and imports

## Testing Requirements
- Unit tests
- Integration tests
- E2E tests (if applicable)

## Checklist
- [ ] Specific acceptance criteria

## Next
Reference to the next mega prompt in sequence.
```

**Key rules for mega prompts:**
1. **Complete code** — don't say "add validation", show the actual function
2. **Exact file paths** — `src/models/user.py` not "the model file"
3. **Testing in every file** — each file includes test examples
4. **n8n placeholders** — mark integration points with `# TODO: n8n integration`
5. **No hardcoded values** — emphasize dynamic user-specific design
6. **Sequential ordering** — each prompt references the next one
7. **English language** — AI agents work best with English instructions

**Pre-implementation docs (write BEFORE mega prompts):**
- `docs/BUG-FIX-GUIDE.md` — If architecture review found issues, list every fix
  with exact code. The AI agent reads this FIRST, fixes bugs, then starts
  implementing. This prevents the agent from building on broken foundations.
- `docs/DYNAMIC-USER-DESIGN.md` — Dedicated doc explaining the per-user
  data model, dynamic reminder generation, and personalized dashboard.
  Reference this in every mega prompt that touches user data.

**Feeding workflow:**
1. Give `MASTER-GUIDE.md` → agent reads project overview
2. Give `BUG-FIX-GUIDE.md` → agent fixes critical issues first
3. Feed mega prompts sequentially (01 → 02 → ... → 09)
4. After each, verify completion before feeding next
5. If agent reports errors, paste error back and ask for fix before continuing

**Folder structure for mega-prompt-driven projects:**
```
PROJECT/
├── frontend/src/{components,pages,hooks,services,stores,utils,types}
├── backend/app/{api,core,models,services,schemas,middleware}
├── docs/mega-prompts/    # Numbered: 01-INFRASTRUCTURE.md, 02-AUTH.md, etc.
├── docs/MASTER-GUIDE.md  # Overview for the AI agent
├── n8n/                   # Placeholder for orchestration
└── docker/                # Deployment config
```

## Post-Implementation Review Workflow

After an AI coding agent implements the project, run a **multi-pass review**:

### Pass Structure

| Pass | Focus | What to check |
|------|-------|---------------|
| **1. Security & Critical** | 🔴 Hardcoded secrets, auth bypass, data leakage, SQL injection, workspace ownership validation |
| **2. Functionality & Integration** | 🔗 Frontend↔Backend type match, API contract alignment, complete user flows, date/RTL handling |
| **3. Code Quality** | ✨ DRY violations, missing tests, N+1 queries, missing ForeignKeys, type safety |
| **4. UX & Production** | 🎨 Loading states, empty states, error messages in local language, tap targets, offline behavior |

**Passes 1-3** are code-focused (give to AI agent or review yourself).
**Pass 4** is user-focused — walk through each flow as a non-technical user.

### Review Prompt Pattern
See [references/multi-pass-review-prompts.md](references/multi-pass-review-prompts.md) for
copy-pasteable review prompts for each pass.

### Iteration
- Run review → get issues → fix → re-run review
- Minimum 2 rounds: find bugs → verify fixes
- Stop when Critical = 0 and Warnings < 10

## File Delivery in WebUI

**Pitfall:** Users in Hermes WebUI cannot see files at arbitrary paths. They can only
see files displayed inline via `MEDIA:/path` (for renderable types) or in the workspace.

**Fix:** Always place deliverable files (zip, tar.gz, docs) in `/workspace/` so they're
visible in the file browser. For code archives:
```bash
cd /workspace && tar -czf PROJECT.tar.gz PROJECT/
```
The file at `/workspace/PROJECT.tar.gz` is visible in the WebUI file browser.

Do NOT try to copy files to `/home/hermeswebui/` — permission denied.

## User Format Preferences (Persian users)

When working with Persian-speaking users, adapt output format:

- **Tick-mark checklists** — Users prefer `✅` / `❌` or checkbox format over prose.
  Example: "با تیک بهم نشون بده" = show with ticks. Always use tables with status
  columns rather than paragraph descriptions.
- **Concise responses** — Users get frustrated with verbose explanations. Lead with
  the answer, then explain only if asked. Tables > paragraphs.
- **File delivery** — Place all deliverables in `/workspace/` (visible in WebUI
  file browser). Do NOT copy to `/home/hermeswebui/` (permission denied). For
  archives: `tar -czf` in `/workspace/`.
- **Persian language** — Responses, error messages, UI text, and documentation
  should be in Persian unless the user explicitly asks for English.

## Iterative Review → Fix Cycle

The standard workflow for AI-coded projects:

```
Architecture docs → Mega prompts → MiMo Code implements
    ↓
Code review (3-pass) → list bugs → MiMo fixes
    ↓
UX review (4-pass) → list UX issues → MiMo fixes
    ↓
Production checklist (13 categories, scored) → identify gaps
    ↓
Repeat until Score ≥ 80%
```

Each cycle produces a review prompt → MiMo fixes → next review prompt.
The user orchestrates this cycle, not the agent. The agent prepares
the prompts and interprets the results.

## References

- [references/telegram-miniapp-tech-stack.md](references/telegram-miniapp-tech-stack.md) —
  Detailed comparison tables and bundle size analysis
- [references/telegram-miniapp-realtime-storage.md](references/telegram-miniapp-realtime-storage.md) —
  SSE patterns, 3-layer storage, third-party auth validation, n8n integration
- [references/ai-coding-agent-mega-prompts.md](references/ai-coding-agent-mega-prompts.md) —
  MiMo Code / AI coding agent mega prompt pattern, dynamic user-specific design
- [references/architecture-review-checklist.md](references/architecture-review-checklist.md) —
  42-bug checklist from real architecture review: auth holes, SQL issues, missing endpoints, backup anti-patterns
- [references/multi-pass-review-prompts.md](references/multi-pass-review-prompts.md) —
  Copy-pasteable review prompts: code review (3-pass) + UX review (4-pass)
- [references/production-readiness-checklist.md](references/production-readiness-checklist.md) —
  13-category scoring checklist for production readiness (121 items)
- [references/production-fix-file-pattern.md](references/production-fix-file-pattern.md) —
  File-per-fix pattern for closing production gaps (individual MD per category)
- [references/gstack-design-tools.md](references/gstack-design-tools.md) —
  Gstack design tool ecosystem: which tools work without OpenAI API key, workflow for Telegram Mini Apps
