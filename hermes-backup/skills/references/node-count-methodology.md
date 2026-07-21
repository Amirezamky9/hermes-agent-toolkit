# Node Count Methodology — Module-Level Breakdown (Generic)

## Why This Exists

Planners consistently underestimate node counts by 40-100%. A table row in ARCHITECTURE.md that says "افزودن آیتم جدید" (1 action) is actually a 4-stage state machine with ~22 real n8n nodes. This reference gives you a standard multiplier per pattern.

## Standard Node Per Module Counts

### Base units (always count these)

| Element | Nodes | Notes |
|---------|-------|-------|
| Trigger (telegram/webhook/schedule/form) | 1 | |
| telegram sendMessage | 1 | |
| telegram editMessageText | 1 | Same node type, different resource/operation |
| telegram answerCallbackQuery | 1 | |
| Slack/Email/SMS/notification send | 1 | Per platform node |
| dataTable (read/search) | 1 | |
| dataTable (create/insert) | 1 | |
| dataTable (update) | 1 | |
| dataTable (delete) | 1 | |
| postgres (SELECT) | 1 | |
| postgres (INSERT) | 1 | |
| postgres (UPDATE) | 1 | |
| postgres (DELETE) | 1 | |
| IF (simple 2-branch) | 1 | |
| Switch (N-branch) | 1 | Covers all branches in 1 node |
| Set (transform) | 1 | |
| Code | 1 | |
| ExecuteWorkflow | 1 | |
| SplitInBatches | 1 | Loop construct |
| HTTP Request / API Call | 1 | |
| Schedule Trigger | 1 | |
| AI Agent | 1 | |
| AI Language Model | 1 | |
| AI Memory | 1 | |
| AI Tool | 1 | Per tool |
| Webhook/Trigger | 1 | |

### Pattern multipliers

| Architecture Description | Real Node Count | Breakdown |
|------------------------|----------------|-----------|
| "Session Manager" | 2-3 | dataTable.search + IF (exists?) + dataTable.create |
| "Form input handler" (1 stage) | 3-5 | IF (input type?) + validation + dataTable.update + telegram |
| "Multi-stage handler" (N states) | 5-7 per stage | IF (input type?) + IF (valid?) + dataTable.update (state + data) + telegram (prompt) + optional sub-stages |
| _4-stage state machine (total)_ | _20-28_ | _Each stage × 4 + one Switch router_ |
| **Broadcast/Bulk notification (loop)** | 5-7 | query audience + SplitInBatches + IF (send?) + sendMessage + result log |
| Reports module (N reports) | 2N + 1 | Switch (select report) + N×(query + format) + output telegram |
| AI Agent without tools | 3-5 | Agent + Model + Memory |
| AI Agent with tools | 4 + (2×tools) | Agent + Model + Memory + (tool config + tool node per tool) |
| **CRUD module** (Create + Read + Update + Delete) | 15-25 | ~4-7 nodes per operation including UI, validation, storage |
| **Edit message with retry** | 2 per edit path | IF (edit failed?) + sendMessage fallback |

## Workflow-level estimate to assign session count

| Node Count | Builder Sessions | Session Duration |
|-----------|----------------:|:----------------:|
| ≤20 | 1 | 45-90 min |
| 21-40 | 2 | 90-180 min total |
| 41-60 | 3 | 3-4 hrs total |
| 61-80 | 4 | 4-6 hrs total |
| 81+ | 5+ | Split into modules, each module 1 session |

## The Admin Panel Amplifier (Worst Offender)

**Empirical finding:** Administrative panels are the #1 source of node-count estimation failure. A planner that estimates "35-40 nodes" for an admin panel actually produces ~85-95 nodes (2.5x ratio). This is because:

| Factor | Why It Amplifies |
|--------|-----------------|
| **CRUD operations** | Each CRUD action (Create/Read/Update/Delete) is listed as 1 line in architecture but needs 4-7 nodes with IF branching, communication, and DB queries |
| **Multi-stage state machines** | "Add item" (4 stages) = ~22 nodes, not "1 action" |
| **Dashboard with N menu items** | A dashboard with 7 menu items needs a 7-branch Switch + each branch needs its own routing logic |
| **Broadcast with loop** | SplitInBatches is always forgotten. It adds 3-5 nodes minimum |
| **Reports section** | N reports = N×2 nodes (SELECT + Telegram) but often listed as 1 row |
| **Missing edges** | Toggle items, sync buttons, cancel handlers, back buttons — these are never in the architecture tables |

**Rule of thumb:** When the architecture describes an "Admin Panel" or "CRM" or "پنل مدیریت", multiply the planner's estimate by **2.5x** before writing any decks. If the result exceeds 80 nodes, split into 3-4 decks.

## AI Agent Amplifier

AI Agents look simple in architecture ("AI Agent with 3 tools" = 1 line) but:

| Component | Nodes |
|-----------|-------|
| Agent | 1 |
| Language Model (OpenRouter/OpenAI) | 1 |
| Memory (Postgres/Session/Window) | 1 |
| Tool 1: DataTable search | 1 (DataTable node) + 1 (Tool definition in SDK) |
| Tool 2: DataTable update | 1 (DataTable node) + 1 (Tool definition in SDK) |
| Tool 3: Postgres query | 1 (Postgres node) + 1 (Tool definition in SDK) |
| **Total** | **~10** (not "1") |

Add guardrails (IF + HTTP) or output parsing (Code), and it's 12-14 nodes.

## User Validation Pattern

When your node count analysis reveals a module where `actual / planner_estimate > 1.5x`, **surface this to the user** before writing decks. The user's intuition about complexity is often sharper than the planner's. Ask:

> "این ماژول طبق تخمین من ~X نود داره درحالی که پلنر ~Y گفته. اگه درست باشه، باید به Z تا دک بشکنیم. تأیید می‌کنی؟"

This serves two purposes: (a) catches planner errors the user already suspects, (b) builds user trust that the reviewer is thorough.

## Common undercount hotspots

These are the most frequently underestimated modules across ALL n8n architecture types:

1. **Multi-state flows** (add item, edit item with field selection, checkout) — each additional state adds 5-7 nodes
2. **Broadcast/loop** — `SplitInBatches` + inner loop nodes are always forgotten
3. **Conditional validation** — a single "check condition" in architecture becomes IF + Set + error message = 3 nodes
4. **Edit/retry fallback** (e.g., editMessageText fallback to sendMessage) — the architecture says "edit retry" as 1 line but it's an IF + telegram node = 2 extra nodes on every edit path
5. **Data table session manager** — every session read needs a create-if-not-exists branch (2-3 nodes, not 1)
6. **Admin/CRM panels** — consistently 2.5-3x the planner estimate
7. **Error handling paths** — graceful error handling doubles some branches (error output → fallback handler → notification)
