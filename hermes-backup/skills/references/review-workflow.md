# Review Workflow — Step-by-Step Process (Generic)

## When to Use This Reference

Load this when you're in Phase A (Read & Analyze Architecture) and need
to systematically extract all information from ARCHITECTURE.md for ANY
type of n8n project — Telegram bot, webhook, schedule, AI agent, or
data pipeline.

## Step-by-Step Extraction

### 1. Identify Project Type & Trigger

Before extracting details, identify the architecture's trigger type.
This determines how you extract routing, state, and data flow.

- **Trigger → Identify trigger type** → webhook / telegram / cron / form / manual
- **Pattern** → chatbot / pipeline / monitoring / notification / admin panel / AI agent
- **Statefulness** → stateless (pipeline) or stateful (chatbot, multi-step form)

### 2. Extract Workflow Map

Scan the doc for:
- `## N. WF0X` headings → workflow list
- Mermaid `flowchart` blocks → connection map
- `flowchart TD` with subgraphs → Data Table ↔ Postgres relationships
- Tables with columns like "نود", "مرحله", "اکشن" → node lists

**Output:** `manifest.yaml` → `project` and workflow summary.

### 3. Extract Credentials

Find sections like `Credential Mapping` or tables mentioning `Credential`.

**Output:** `manifest.yaml` → `credentials`.

Check: Are these real credential names in n8n or placeholders?

### 4. Extract Data Tables

Find:
- `Data Table Schema` sections or tables
- Column definitions with types
- PK and FK notes
- TTL or cleanup notes

**Output:** `manifest.yaml` → `data_tables`.

### 5. Extract Database Schemas

If PostgreSQL/MySQL/SQLite schemas exist, find `جدول:` blocks or
`CREATE TABLE` definitions with field types.

**Output:** `manifest.yaml` → `postgres_schemas` (or appropriate DB name).

### 6. Extract State Machine (Stateful Architectures Only)

Skip this step for stateless architectures (pipelines, scheduled tasks,
simple webhooks, data transformations).

For stateful architectures (chatbots, multi-step forms, admin panels with
state tracking), find:
- `Session States` or `ماشین حالت` tables
- `state` field definitions with valid inputs
- Navigation transitions

**Output:** `manifest.yaml` → `state_machine`.

### 7. Extract Callback/Command Conventions (Chatbots Only)

Skip this for non-chatbot architectures.

For bots with callback buttons or commands, find:
- `Callback Data` or `نام‌گذاری` tables
- Command definitions (/start, /menu, etc.)
- Navigation patterns

**Output:** `manifest.yaml` → `callback_conventions`.

### 8. Extract Message/Notification Flow

For messaging platforms (Telegram, Slack, etc.):
- Which interactions use editMessageText vs sendMessage?
- Platform-specific behavior (answerCallbackQuery etc.)

**Output:** `manifest.yaml` → `message_editing` (if applicable).

### 9. Extract Error Handling

Find `Error Handling` or `مدیریت خطا` sections:
- Retry patterns
- Fallback notifications
- Listener-level vs per-node error handling

**Output:** `manifest.yaml` → `error_handling`.

### 10. Validate Completeness

Checklist before writing decks:

- [ ] All credential names resolved (no "مشخص نشده" / "TBD" / "placeholder")
- [ ] For Telegram bots: answerCallbackQuery pattern identified
- [ ] For chatbots: state machine has all states documented
- [ ] For pipelines: input data format documented
- [ ] For webhooks: HTTP method + response format documented
- [ ] For AI agents: model + tools + memory documented
- [ ] All Data Table columns extracted
- [ ] All PostgreSQL tables and columns extracted
- [ ] For stateful: every state has a handler, every input type has a route
- [ ] Error handling covers: API failures, empty data, timeouts
- [ ] Node count per deck ≤ 20
- [ ] Line count per deck ≤ 1,500

## Architecture-Type Table Extraction

### Telegram Bot Architecture Tables

Tables typically have columns:
| # | مرحله | نود (نوع n8n) | Credential | جزئیات و پارامترها |

Extract to:
```yaml
- name: "Handler Name"                    # from "مرحله"
  type: "n8n-nodes-base.telegram"         # from "نوع n8n"
  typeVersion: 1.2                        # from search_nodes
  parameters:                             # from "جزئیات"
    resource: "message"
    operation: "sendMessage"
    chatId: "={{ $json.chat_id }}"
    text: "Message text"
  credentials: telegramApi                # key from manifest
  position: [1320, 500]
  notes: "Send welcome message"
```

### Webhook Architecture Tables

| # | Step | Node Type | Credential | Details |
Extract node type + HTTP method + payload mapping.

### Data Pipeline Tables

| # | Step | Node | Source | Destination | Transform |
Extract source query, transform logic, destination mapping.

## Manifest → Deck Reference Resolution

When a deck needs a value from manifest:

```yaml
# WRONG — embedded credential
credentials:
  telegramApi:
    name: "my_bot"
    id: "..."

# RIGHT — key reference
credentials: telegramApi  # resolved from manifest.yaml
```

Builder loads `manifest.yaml` first, then the deck. They merge the references.

## How to Set Node Positions

Use a consistent grid pattern:

```yaml
# Trigger column:      x = 200
# Extraction column:   x = 480
# Router column:       x = 760
# Handler column:      x = 1040
# Sub-handler column:  x = 1320
# Output column:       x = 1600

# Y-spacing: 300px per row
# Branch offset: +360px per branch
```

Adjust spacing for denser workflows if needed. Builder can reposition.

## When to Archive vs Update Decks

- If Planner edits the ARCHITECTURE.md, re-run the reviewer to regenerate
  only the affected decks (check `depends_on` + git diff)
- If Builder reports an issue with a deck, edit that deck's YAML (not the
  architecture) and mark it as `version: 2`
- Archived decks live in `{{dir}}/archived/` so Builder can reference them

## Architecture-Type Edge Cases

### Telegram Bot
1. **Empty callback data** — user presses an unregistered button
2. **Old message edit** — editMessageText on deleted message → fallback to sendMessage
3. **Concurrent messages** — user sends text while processing a callback
4. **Blocked user** — user blocked the bot → Telegram API returns 403
5. **Rate limiting** — too many requests → 429 retry

### Webhook
1. **Missing payload** — webhook called with empty body
2. **Invalid signature** — HMAC/auth check fails
3. **Timeout** — downstream service takes >30s
4. **Duplicate webhook** — same event delivered twice (idempotency)

### Scheduled Task
1. **Empty source** — DB/API returns no data
2. **Source unavailable** — downstream service down
3. **Partial failure** — some rows succeed, some fail (error row handling)

### AI Agent
1. **Tool failure** — one of the agent's tools throws an error
2. **Context overflow** — agent input exceeds model token limit
3. **Slow response** — model takes >30s to respond
4. **Hallucinated output** — agent returns non-existent data

### Data Pipeline
1. **Schema mismatch** — source schema changed but destination expects old format
2. **Duplicate records** — same row processed twice (idempotency key)
3. **Large dataset** — batch size exceeds SplitInBatches limits

Edge cases go in:
- `nodes[].notes` — one-liner about the handling
- `test_hints.cases[]` — a pin-data entry that triggers the edge case
- Connections — an error output connected to an error handler
