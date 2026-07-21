# Deck Self-Review Checklist — Structural Validation

> **When to load:** AFTER all decks are written, BEFORE reporting to the user.
> **Purpose:** Catch structural bugs that pass YAML validation but break Builder.

## Must-Run Checks

### 1. Cross-Reference Audit

For every `deck-*.yaml`:

- [ ] Every node name in `connections[].source` and `connections[].target` exists in that deck's `nodes[].name` list.
  - **Exception:** cross-deck targets referenced ONLY in `switch_outputs` and `builder_notes`, NEVER in `connections[]`.
- [ ] Every `switch_outputs[].outputs[].target` either exists in `nodes[]` or is tagged as a cross-deck target in a note.
- [ ] No `connections[]` entry references a node from another deck — those go in `switch_outputs` only.

### 2. Node Existence Check

- [ ] No `type: "n8n-nodes-base.noOp"`, `noop`, `no-op`, or `noOperation` — these do not exist in n8n.
- [ ] Every node `type` is a real n8n node type (check with `search_nodes` if unsure).
- [ ] Every Code node's `jsCode` is inspected — no placeholder text like `// placeholder`, `// TODO`, `// FIXME`, `// actual query`, or `pass through`.
  - **Fix:** Replace Code placeholders with real nodes (postgres, httpRequest, dataTable, etc.).

### 3. Telegram-Specific Checks

- [ ] All `chatId` expressions using `$json.callback_query.from.id` are actually meant to be `$json.callback_query.message.chat.id`.
  - **Rule:** `from.id` = user ID, `message.chat.id` = chat ID. Never use `from.id` as chatId.
- [ ] `simplifyOutput` on `telegramTrigger` is `false` for raw JSON access.
- [ ] `operation: "editMessageText"` has both `chatId` and `messageId` populated.
- [ ] `operation: "sendMessage"` does NOT have `messageId` (it's a new message).

### 4. Sequence/Auto-Increment Check

- [ ] If the architecture generates order codes with a counter pattern (e.g. `CB-2407-0001`):
  - [ ] A `seeds` section in `manifest.yaml` defines initial `order_counter` value.
  - [ ] A node reads the counter before order creation.
  - [ ] A node increments the counter after order creation.
  - [ ] The `order_code` is assembled in a Code node, not split across nodes.

### 5. DataTable Session Lookup Check

- [ ] `operation: "get"` on DataTable has `alwaysOutputData: true`.
- [ ] An IF node after the lookup checks `{{ $json.empty }}` or `{{ $json.rows.length == 0 }}` to handle new vs returning users.
- [ ] The "new user" branch leads to session creation (upsert).

### 6. Error Handling Coverage

- [ ] Every Telegram node (sendMessage, editMessageText) has `onError: "continueRegularOutput"`.
- [ ] Every Postgres node has at least `onError: "continueRegularOutput"` (or `"continueErrorOutput"` for critical operations).
- [ ] Stock update queries are conditional: `UPDATE ... SET stock = stock - qty WHERE stock >= qty`.

## When to Reject a Deck

Reject and rewrite if ANY of these are true:

- A `connections[]` entry references a node name not in `nodes[]` (cross-deck target in connections = always wrong).
- A Code node has placeholder code (`// placeholder`, empty function body, `return [{ json: data }]` passthrough).
- An admin-router Switch is described in `switch_outputs` but has no corresponding node in `nodes[]`.
- The deck uses `noOp` or equivalent.

## Example Review Flow

```
Check #1: Cross-Reference 💀
  connections[].source → exists in nodes[]?  ✅
  connections[].target → exists in nodes[]?  ❌ "🔙 back to orders"
  → Fix: either add the node or change the target

Check #2: code placeholder 💀
  node "🔍 Fetch User Orders" → jsCode contains "// placeholder"
  → Fix: replace with real postgres node

Check #3: chat_id 💀
  node "🛒 Add to Cart" → chat_id: cb.from?.id
  → Fix: change to cb.message.chat.id

Check #4: sequence counter 💀
  order_code_prefix used but no counter read/increment
  → Fix: add Get Order Counter + Increment Counter nodes
```
