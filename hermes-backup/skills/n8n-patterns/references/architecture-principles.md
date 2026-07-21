# n8n Architecture Principles

> اصول معماری n8n — برای استفاده Planner و Reviewer
> Compiled from real session experience and user corrections.

## 0. Pattern Authoring Style
- **No e-commerce/sales examples** unless explicitly requested.
- **One canonical reference per domain.** Three files covering the same topic ≈ 1 file, not 3. If a better source exists (MCP best practices, enriched docs), delete the hand-rolled duplicate and redirect all references. Don't keep N files that say roughly the same thing — they drift apart and confuse both the agent and the author.
- **Direct, concrete content.** Node names, exact parameters, wiring examples.
- **Include what doesn't exist** (e.g. "n8n has no Exa node — use HTTP Request").
- **Every pattern has a Pitfalls section.**
- **When a Code Node has sandbox limits, say so visibly** (🚫 No Network).
- **Developer references: NO setup content.** No BotFather, no API key tutorials.
- **Do NOT assume/autocorrect user terms.** If user writes "kie.ai", search for "kie.ai" — not "krea.ai".

## 1. Telegram Routing: Type-First (NOT State-First)

```
📱 Telegram Trigger
          │
          ▼
┌──────────────────────────────────────┐
│  Switch: Route by message type       │
│  (expression mode — NO Code node)    │
├──────────────────────────────────────┤
│ callback → callback_query exists     │
│ file     → photo/document/voice/...  │
│ command  → text starts with "/"      │
│ text     → text exists, no "/"       │
│ unknown  → fallback                  │
└────────┬─────────────────────────────┘
         │
         ▼
    [process per route]
```

- **Session state is checked ONLY on the `text` route.** Commands and callbacks always work regardless of state.
- **Four routes are not optional** — every Telegram bot needs all four.
- **answerCallbackQuery is NOT needed** — `editMessageText` resolves Telegram's loading indicator.

### Switch Expression Rules
- Output 0: `callback` — `{{ $json.callback_query !== undefined }}`
- Output 1: `file` — `{{ $json.message.photo || $json.message.document || ... !== undefined }}`
- Output 2: `command` — `{{ $json.message.text && $json.message.text.startsWith('/') }}`
- Output 3: `text` — `{{ $json.message.text && !$json.message.text.startsWith('/') }}`
- Output 4: `unknown` — fallback (NoOp)

## 2. message_id is Innate
Every Telegram message carries its own `message_id`:
- Messages: `$json.message.message_id`
- Callbacks: `$json.callback_query.message.message_id`
Do NOT store message_id in session state.

## 3. Telegram Message Rules
| Scenario | Action | Reason |
|----------|--------|--------|
| /start | sendMessage | Always new message |
| Button press (callback) | editMessageText | Keep UI clean |
| /menu, /cart (command) | editMessageText | Like a button |
| User types free text | sendMessage | Natural conversation |

## 4. DataTable: Always Use Upsert
After EVERY DataTable addNode via MCP:
- Immediately call `updateNodeParameters` with `replace: true`
- Include ALL routing-dependent fields in `columns.value`
- Use **upsert** (not update) for session-state rows

## 5. Execute Sub-Workflow vs HTTP Request
- **Execute Sub-Workflow** for calling other workflows — NOT HTTP Request + Webhook
- `waitForSubWorkflow: true` — parent waits and handles messaging
- `waitForSubWorkflow: false` — child is responsible for its own messaging

## 6. No-Code First
| Action | ✅ Right Node | ❌ Wrong Node |
|--------|-------------|-------------|
| Read/Write Data Table | `dataTable` | `code` |
| Routing by condition | `switch` | `code` |
| Boolean if/else | `if` | `code` |
| Simple transform | `set` | `code` |
| AI / LLM | `agent` + `lmChat*` | `code` |
| HTTP Request | `httpRequest` | `code` |

**Only use `code` when:** no native node exists, or operation is too specific for Set/Expression.

### ⚠️ User Preference (2026-07-19)
**از نود کد کمتر استفاده کن. اگر استفاده کردی اصلاح کن و از ست یا منطق نودهای دیگه استفاده کن یا از expression استفاده کن.**
کاربر صراحتاً خواسته Code node ها به حداقل برسن. جایگزین‌ها:
- **Set node** (mode: manual) برای extract/transform ساده
- **Expression** در پارامترهای نودهای دیگه
- **IF node** برای شرط‌های ساده
- **Switch node** برای routing

فقط Code node بذار وقتی واقعاً هیچ جایگزینی وجود نداره (مثل loop روی array یا JSON parse پیچیده).

## 7. Session State Machine
Only for `text` route — commands/callbacks bypass state:
- `welcome` → await department/role selection
- `awaiting_input` → free text → AI Agent
- `awaiting_confirm` — yes/no only
- `processing` — silent, no new input
- `closed` — only /start reactivates

## 8. Storage: Two-Tier
- Data Table (cache, fast) + PostgreSQL (source of truth)
- Products for user ← `products_cache` (Data Table)
- Active orders ← `orders_cache` (Data Table)
- User sessions ← `user_sessions` (Data Table)
- PostgreSQL for: final orders, users, products (admin)

### ⚠️ User Correction (2026-07-19)
**ماشین حالت کاربر (state machine) همیشه در Data Table ذخیره می‌شود، نه PostgreSQL.**
وقتی معماری یا storage location state رو توضیح میدی، هرگز PostgreSQL رو به عنوان محل نگهداری state machine پیشنهاد نکن.

## 9. Error Handling Levels
1. **Node Retry** — per-node retryOnFail
2. **Workflow Error Handler** — Error Trigger + separate error workflow
3. **Inline Try-Catch** — IF + Split In Batches + Data Table

## 10. Cost-Effective AI
- **Text**: Cheap LLMs (GPT-4o-mini, Claude Haiku, Groq)
- **Image/Video**: KIE.AI via httpRequest (not DALL-E/Gemini/Runway)
- **Voice**: OpenAI TTS (built-in node) for occasional use

## 11. Guardrails Layer
Place a Guardrails node between Trigger and AI Agent to filter:
- Jailbreak attempts (threshold: 0.7)
- NSFW content (threshold: 0.7)
- PII leakage
- API secret keys (entropy detection)

## 12. Git Security Before Public Publish

**Patch/replace on a sensitive string in a file is NOT enough** to protect a public repo — the old string remains in earlier git commits. Anyone cloning the repo sees the full history.

### Pre-Publication Checklist (run BEFORE `git push`)

1. **Scan all workflow JSON files** for IP addresses, credential IDs, webhook IDs, bearer tokens, hostnames:
   ```bash
   grep -nE '\b[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b' workflow.json
   grep -nE '(credentialId|webhookId|apiKey|token|secret|bearer)' workflow.json
   ```

2. **Replace live IPs / endpoints** with placeholders (e.g. `YOUR_MCP_SERVER:3000/mcp`) before the first commit.

3. **If sensitive data was already pushed**, do NOT just patch and commit — the old commit still leaks:
   - Option A: `git filter-repo` to rewrite history (best for collaborative repos)
   - Option B: **Force push with fresh history** (best for solo repos):
     ```bash
     rm -rf .git
     git init && git branch -m main
     git add -A && git commit -m "Initial commit"
     git remote add origin <url>
     git push --force origin main
     ```
   - Verify after push: `gh api repos/<user>/<repo>/commits --jq '.[].sha'` — should show only 1 commit.

4. **READMEs also leak** — any URL/IP/hostname in `README.md` or `README.fa.md` is public forever once pushed.

5. **workflow.json may contain `instanceId`** — not a secret per se but a fingerprint.

### What's Safe to Leave
- Placeholder credential references (n8n auto-creates new ones on import)
- `webhookId` strings (random UUIDs, no auth value without the bot token)
- `templateCredsSetupCompleted: true` (metadata flag)

### What MUST Be Stripped
- **IP addresses** → `YOUR_IP` or `YOUR_SERVER`
- **Domain names of private servers** → `YOUR_DOMAIN`
- **API keys, bearer tokens, passwords** — strip any hardcoded secrets before export
