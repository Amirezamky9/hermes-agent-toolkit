---
name: telegram-hybrid-bot
description: "Telegram bot hybrid architecture design."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Telegram, Bot, Serverless, n8n, Hybrid, Automation]
---

# Telegram Hybrid Bot Architecture

A decision framework and blueprint for building Telegram bots using the new
**Telegram Serverless** platform (core.telegram.org/bots/serverless) in
combination with a backend (n8n or Python). Purely serverless bots are
covered, but the skill's core value is the **hybrid pattern**: it tells you
exactly where the serverless boundary lies and when you *must* add a backend.

**What it does NOT cover:** legacy Managed Bots, polling-based bots, or
non-Telegram messaging platforms.

**Dependency stance:** standard Node.js tools (`npx`, `npm`) for the
serverless side; any HTTP-capable backend for the bridge side (n8n, Python
FastAPI, Flask, Express, etc.). No exotic dependencies.

## When to Use

- User asks: "build a Telegram bot without a server" (pure serverless)
- User asks: "combine Telegram Serverless with n8n or a Python backend" (hybrid)
- User asks: "what is the maximum I can do with pure Telegram Serverless?"
- User asks: "can Telegram Serverless handle AI, file uploads, or Postgres?"
- User asks: "design a hybrid Telegram bot — light ops serverless, heavy ops backend"
- User wants a decision tree comparing serverless vs. hybrid vs. full-backend
- Discussing limitations: file download, npm packages, cron, foreign keys
- User asks: "I don't see Serverless in BotFather — what do I do?"
- User asks: "monitor when Serverless becomes available for my bot"
- User wants a watch script to catch the rollout before anyone else

## Prerequisites

- **Node.js 18+** installed locally.
- A Telegram bot registered via `@BotFather`.
- `@BotFather` → your bot → **Serverless** toggled **on**.
- CLI access token from `@BotFather` → your bot → Serverless → CLI Access.
- (Optional) An n8n instance or Python backend with a public webhook URL.

## How to Run

1. Consult the **decision matrix** below to pick the bot tier.
2. Scaffold the project: `npx tgcloud init` (or `npm create @tgcloud/bot`).
3. Implement `handlers/`, `lib/`, and `schema.js`.
4. If hybrid: add `lib/bridge.js` for the backend link.
5. Deploy: `npx tgcloud push` + `npx tgcloud migrate`.

## Pure Serverless Tier (Max Capability)

This tier answers: "what can I build with **zero** servers?" — the complete
no-backend path. Details in `references/pure-serverless-bot-design.md`.

**What you CAN do without any backend:**
- SQLite-backed notes, todos, bookmarks (4-table schema pattern)
- Inline keyboards with pagination, filtering, category drill-down
- Inline Mode search across user data from any chat
- AI chat via `sdk/fetch` (Gemini, Groq — free) using the proxy pattern
- Multi-language, personal stats, user preferences
- Smart classifier: short text → save note, long/question → AI reply

**Boundary — stop here and go hybrid if:**
- User must upload/download files
- Bot must send scheduled reminders (cron)
- Data must live in Postgres/MongoDB/external DB
- Code needs npm packages at runtime

## Quick Reference: Decision Matrix

| Capability needed | Tier | Backend? |
|---|---|---|
| Text replies, inline keyboards, SQLite | **Serverless-only** | No |
| AI calls (OpenAI, Claude via HTTP) | **Serverless + Backend** | Yes (proxy) |
| File download / upload | **Hybrid** | Yes |
| Postgres / MongoDB | **Hybrid** | Yes |
| Scheduled tasks (cron) | **Hybrid** | Yes (n8n scheduler) |
| Multi-service orchestration | **Hybrid** | Yes (n8n) |
| npm packages at runtime | **Hybrid** (fetch calls) | Yes |
| Binary / streaming responses | **Hybrid** | Yes |

## Procedure

### 1. Classify the bot's requirements

Review these hard boundaries from the official docs. If *any* box is checked,
you **cannot** stay pure-serverless:

- [ ] **File I/O** — bot must download user files or upload new ones
- [ ] **npm packages** — handler code needs a non-trivial JS library
- [ ] **Foreign key / relational DB** — must enforce referential integrity
- [ ] **Binary HTTP** — must send or receive non-text payloads
- [ ] **Scheduled tasks** — cron, reminders, periodic digests
- [ ] **Persistent connection** — WebSocket, SSE as client
- [ ] **Custom webhook URL** — need to point Telegram webhook elsewhere

If ≥1 box is checked → **Hybrid tier**.

### 2. Check Serverless availability in BotFather

Open @BotFather → `/mybots` → select your bot. Look for:

- **Serverless** (English)
- **سرورلس** / **بدون سرور** (Persian Telegram)
- **Cloud Code** / **Code Runner** (alternative labels)
- Under sub-menu: `Bot Settings → Features → Serverless`
- Under sub-menu: `Bot Settings → Developer Mode → Serverless`

**If visible:** tap → Turn On → CLI Access → save the `app<id>:<secret>` token.

**If NOT visible (gradual rollout):**
  - Try updating Telegram to latest version.
  - The `@tgcloud` npm packages still work for local development,
    but you cannot deploy (`tgcloud push`) without a linked bot.
  - You CAN scaffold and edit the project; just can't go live yet.
  - Re-check BotFather periodically — the feature may appear later.
  - The CLI supports `TGCLOUD_TOKEN` env var for CI setups (skips the
    interactive BotFather-flow), but you still need a valid token from
    BotFather once to generate it.

### 3. Scaffold the serverless project

```bash
# Create project (CLI installed as devDependency)
npm create @tgcloud/bot my-bot
cd my-bot

# Link with BotFather CLI token
npx tgcloud login
```

### 3. Wire the bridge (hybrid only)

Create `lib/bridge.js`:

```js
import { fetch } from 'sdk';

const BACKEND_URL = process.env.BACKEND_URL;
const SHARED_SECRET = process.env.BRIDGE_SECRET;

export async function forward(payload) {
  try {
    const res = await fetch(BACKEND_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Bridge-Secret': SHARED_SECRET,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      console.error('Bridge error:', res.status);
      return { reply: 'Service unavailable. Try later.' };
    }
    return await res.json();
  } catch (err) {
    console.error('Bridge fetch failed:', err);
    return { reply: 'Service unavailable. Try later.' };
  }
}
```

### 4. Implement the classifier (`lib/classifier.js`)

Routes each message to cache, local logic, or the bridge:

```js
const LOCAL_PATTERNS = [
  /^\/start$/, /^\/help$/, /^\/settings/, /^(hi|hello|hey|سلام)$/i,
];

export function classify(text) {
  for (const p of LOCAL_PATTERNS) if (p.test(text)) return 'local';
  return 'bridge';  // everything else → backend
}
```

### 5. Deploy

```bash
npx tgcloud status          # review changes
npx tgcloud push            # deploy modules atomically
npx tgcloud migrate         # apply database schema changes
```

### 6. Set up the backend (n8n / Python)

**n8n:** Create a workflow with a **Webhook trigger** (path like
`/telegram-bridge`), process with any n8n node, and **Respond to Webhook**
with JSON `{ "reply": "…", "context": … }`.

**Python (FastAPI):**

```python
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

BACKEND_KEY = "my-shared-secret"

@app.post("/telegram-bridge")
async def bridge(req: Request):
    if req.headers.get("x-bridge-secret") != BACKEND_KEY:
        return {"error": "unauthorized"}, 403
    body = await req.json()
    # ... process with your Python logic (AI, DB, etc.)
    return {"reply": "Processed by Python backend."}
```

## Pitfalls

- **Serverless may not appear in BotFather (gradual rollout).** The feature
  appears to be in staged rollout. Many bots do not show the Serverless menu
  item at all. If missing: try updating Telegram, look under different names
  (Persian: "سرورلس", "بدون سرور"; English: "Cloud Code", "Code Runner"),
  check sub-menus (`Bot Settings → Features → Serverless`), or wait. The
  `@tgcloud` npm packages ARE available regardless — you can scaffold and
  edit the project locally, just can't deploy without a linked bot. Re-check
  BotFather periodically.
- **Managed Bots CANNOT provide a Serverless CLI token.** Managed Bots (Bot
  API 9.6) give a Bot API token only. Serverless needs a separate CLI token
  (`app<id>:<secret>`) that requires manual activation in BotFather. There is
  no API method to enable Serverless or retrieve its token programmatically.
  See `references/managed-bots-vs-serverless.md` for the full comparison.
- **`npx tgcloud login` requires an interactive terminal.** It will fail with
  "requires an interactive terminal" when run via Hermes' `terminal` tool.
  For non-interactive environments, use `TGCLOUD_TOKEN` environment variable
  (set it to the `app<id>:<secret>` value obtained from BotFather on a device
  that CAN do interactive login once). The token resolution order is: (1)
  `TGCLOUD_TOKEN` env var, (2) `.tgcloud/credentials`.
- **`npm create @tgcloud/bot` scaffolds in the calling CWD.** When run via
  `terminal` tool, the project lands in the terminal's current working
  directory — often `/tmp/` or the session root. Always `cd` to the intended
  parent directory first, then scaffold with `.` or a relative folder name.
  The scaffold prints the full path; verify with
  `find / -name "<project-name>" -type d`. The project folder may be owned
  by `hermeswebui` and not accessible from `/workspace/` context.
- **The service is extremely new (July 12–14, 2026).** `@tgcloud/cli` first
  published 0.1.0 on July 12, now at 0.1.2 (July 13). As of mid-July 2026
  there is **zero public discussion** — no Reddit posts, no HN threads, no
  GitHub repos, no tweets. This is not a bug; the rollout is intentionally
  quiet. Users who see it in BotFather are early; those who don't are the
  majority. Re-check BotFather weekly.
- **Monitor Serverless availability via a daily watch cron job.** Since the
  service rolls out with no announcement, set up a `no_agent=True` cron job
  that checks npm version bumps and whether public discussion has appeared.
  A ready-to-use script is at `scripts/check-serverless-status.sh` in this
  skill — it checks npm packages, official docs hash, Reddit, GitHub, and HN
  in one run. Output is silent when nothing changed. Create it with:
  `skill_manage action=write_file name=telegram-hybrid-bot
  file_path=scripts/check-serverless-status.sh file_content=...`
  then `cronjob action=create schedule="0 10 * * *"
  script=telegram-hybrid-bot/check.sh no_agent=true`.
- **No foreign keys.** The SQLite runtime runs with `PRAGMA foreign_keys = OFF`.
  Model relationships with plain columns and enforce integrity in application
  code.
- **Token mismatch.** The Serverless CLI token (`app<id>:<secret>`) is
  *different* from your bot's API token. Get it from BotFather → Serverless →
  CLI Access.
- **No npm at runtime.** All packages must be resolved at deploy time via the
  SDK. If you need lodash, `node-fetch`, etc., implement that logic on the
  backend side.
- **32 MB response cap.** `sdk/fetch` responses are limited to 32 MB.
  Streaming with `res.body` helps but does NOT raise the limit.
- **Deploying never migrates.** `npx tgcloud push` does NOT touch the
  database. Run `npx tgcloud migrate` separately after a schema change.
- **Execution time limit.** The platform has an unadvertised timeout — if a
  handler takes too long it may be killed. Keep handlers fast; ship heavy
  work to the backend.

## Verification

Send a message to the deployed bot. It should reply instantly (serverless
path). Then test bridging by sending a command that triggers the `bridge`
classifier; check your backend received the POST and returned a reply
visible in the Telegram chat.

## References

- Official docs: https://core.telegram.org/bots/serverless
- Pure serverless bot design (full blueprints, schema, handler map):
  `references/pure-serverless-bot-design.md`
- Managed Bots vs Serverless (explains why Managed Bots tokens cannot
  activate Serverless): `references/managed-bots-vs-serverless.md`
- Monitoring rollout & cron watch setup:
  `references/monitoring-rollout.md`
- Monitoring shell script (no_agent cron):
  `scripts/check-serverless-status.sh`
- `@tgcloud` npm packages: `@tgcloud/cli`, `create @tgcloud/bot`
- BotFather: https://t.me/BotFather
- Bot API: https://core.telegram.org/bots/api
