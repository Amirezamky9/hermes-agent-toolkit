# Testing n8n Workflows with Pin Data

> **Reference for**: How to test workflows incrementally using `test_workflow` + `prepare_test_pin_data`.
> **When to use**: When the user asks to "test the workflow" or "pin data and verify it works".

---

## Overview

n8n workflows can be tested without triggering real external services by using **pin data**. This allows the Builder to verify each session's logic before moving to the next session.

### Key Tools

| Tool | Purpose |
|------|---------|
| `prepare_test_pin_data(workflowId)` | Returns JSON schemas for nodes that need pin data |
| `test_workflow(workflowId, pinData, triggerNodeName)` | Runs the workflow with pinned data |
| `get_execution(executionId, includeData=true)` | Retrieves execution results |

---

## Step-by-Step Testing Pattern

### 1. Prepare Pin Data Schema

```json
prepare_test_pin_data(workflowId: "iVVXVC6IdZu0SP9S")
```

Returns:
- `nodeSchemasToGenerate`: Nodes with schema (can auto-generate)
- `nodesWithoutSchema`: Nodes that need manual pin data (Telegram nodes, Postgres, Data Table, etc.)
- `nodesSkipped`: Logic nodes (Switch, If, Code, Set) that execute normally

### 2. Build Pin Data Object

For each node in `nodesWithoutSchema`, provide realistic test data.

#### ⚠️ Critical: Trigger Type Determines Pin Data Shape

The pin data structure for the trigger node depends on the trigger type used:

| Trigger Type | Pin Data Shape | Real Execution Shape |
|---|---|---|
| `telegramTrigger` | `{"message": {...}}` or `{"callback_query": {...}}` | Same — Telegram API sends direct |
| `webhook` (simple HTTP) | `{"body": {"message": {...}}}` | `{"headers":{...}, "body": {"message": {...}}, "params":{}, "query":{}, "webhookUrl":"...", "executionMode":"..."}` |
| `webhook` (callback_query) | `{"body": {"callback_query": {...}}}` | `{"headers":{...}, "body": {"callback_query": {...}}, ...}` |

**Since this project uses `webhook` (not `telegramTrigger`), the real structure has a `body` wrapper.** Pin data must mirror this.

**Webhook Trigger (message)** — ✅ Correct for this project:
```json
{"json": {
  "body": {
    "message": {
      "chat": {"id": 66881162, "first_name": "کاربر", "type": "private"},
      "from": {"id": 66881162, "first_name": "کاربر", "is_bot": false},
      "message_id": 136,
      "text": "/start",
      "date": 1782755903,
      "entities": [{"offset": 0, "length": 6, "type": "bot_command"}]
    }
  },
  "executionMode": "test",
  "headers": {
    "content-type": "application/json",
    "host": "n8n.mym8m.cloud"
  },
  "webhookUrl": "https://n8n.mym8m.cloud/webhook-test/uuid"
}}
```

**Webhook Trigger (callback_query)** — ✅ Correct:
```json
{"json": {
  "body": {
    "callback_query": {
      "id": "12345",
      "from": {"id": 66881162, "first_name": "کاربر", "is_bot": false},
      "message": {"message_id": 136, "chat": {"id": 66881162}},
      "data": "view_products"
    }
  },
  ...headers etc...
}}
```

**Telegram Trigger (message)** — ❌ Wrong for Webhook, only correct for old TelegramTrigger:
```json
{"json": {"message": {"chat": {"id": 123}, "text": "/start"}}}
```
With Webhook, this would land at `$json.message` but real data is at `$json.body.message`.

#### Other Nodes

**Telegram (sendMessage/editMessageText/answerCallbackQuery)** — no real data needed:
```json
{"json": {}}
```

**PostgreSQL (SELECT)** — simulated return data:
```json
{"json": {"telegram_id": "66881162", "first_name": "کاربر"}}
```

**PostgreSQL (INSERT/UPDATE)** — no real data needed:
```json
{"json": {}}
```

**Data Table (get — single item)**:
```json
{"json": {}}  // empty if no session, or {"state": "idle", "cart_json": "[]"} if session exists
```

**Data Table (read — returnAll)**:
```json
{"json": {"name": "قهوه ۱۰۰٪ عربیکا", "price_250g": 150000, ...}}
```
Note: `returnAll: true` returns multiple items. If you pin it with only 1 item, downstream `$items().map()` will only see 1. For realistic tests, provide at least 2-3 items.

### 3. Run Test

```json
test_workflow(
  workflowId: "iVVXVC6IdZu0SP9S",
  pinData: { "Webhook": [{"json": {...}}], "Telegram Node": [{"json": {}}], ... },
  triggerNodeName: "Webhook"
)
```

### 4. Check Results

```json
get_execution(
  workflowId: "iVVXVC6IdZu0SP9S",
  executionId: "5601",
  includeData: true,
  truncateData: 5
)
```

Look at `resultData.runData` to see:
- Which nodes executed
- What data passed through each node (`data.main[0][i].json`)
- Where execution stopped (`lastNodeExecuted`)
- Any errors (check `executionStatus: "error"` and the `error` field)

### 5. Fix and Retry

If a node fails or produces wrong output:
1. Use `update_workflow` with atomic operations to fix the issue
2. Re-run `test_workflow` to verify the fix
3. Repeat until all paths pass

---

## Common Test Scenarios for WF01 (Telegram Coffee Bot)

### Scenario A: `/start` command (new user)
- **Trigger**: Webhook with `body.message.text = "/start"`
- **Expected path**: Webhook → Extract Input Data → Answer Callback Query → Get Session → Session Manager → Route by State (idle → output 0) → Route by Type (/start → output 0) → Check User → [User Found? → Register User or skip] → Format Welcome → Send Welcome → Save Welcome mid
- **Session Manager pin data**: `chat_id="66881162", user_id="66881162", text="/start", state="idle", input_source="command"`

### Scenario B: `/menu` command
- **Trigger**: Webhook with `body.message.text = "/menu"`
- **Expected path**: Route by Type (/menu → output 2) → Get Products (reads from products_cache) → Format Product Keyboard → Send Products
- **Get Products**: Do NOT pin this node — let it read from the real DataTable. If you must pin, provide ALL 5 products as separate items.

### Scenario C: `view_product_1` button
- **Trigger**: Webhook with `body.callback_query.data = "view_product_1"`
- **Expected path**: Route by State (idle) → Route by Type (callback) → Route Callback (view_product_) → Get Product Detail → Format Product Detail → Show Product Detail → Set Selecting Weight

### Scenario D: `weight_1_500` button
- **Trigger**: Webhook with `body.callback_query.data = "weight_1_500"`, Session must have `state=selecting_weight`
- **Expected path**: Route by State (selecting_weight → output 1) → Weight Handler → Check Input Type → Extract Weight Data → Check Stock → Stock Available → [Build Cart → Save Cart → Cart Success Message] or [Stock Error]

### Scenario E: `/cart` command (empty)
- **Trigger**: `body.message.text = "/cart"`, `state=idle`
- **Expected path**: Route by Type (/cart → output 3) → Check Cart Empty (empty → output 0) → Show Empty Cart

### Scenario F: `/cart` command (with items)
- **Trigger**: `body.message.text = "/cart"`, `state=idle`, `cart_json` has items
- **Expected path**: Route by Type (/cart → output 3) → Check Cart Empty (NOT empty → output 1) → Format Cart Items → Show Cart Items → Validate Cart → Request Address → Set Checkout State

### Scenario G: Checkout address input
- **Trigger**: `body.message.text = "تهران، خیابان ولیعصر"`, `state=checkout_address`
- **Expected path**: Route by State (checkout_address → output 2) → Check Address Input → Check Address Length → Save Address → Show Order Summary

---

## Important Notes

1. **pinData format**: Must be a JSON object (not string). Keys are node names, values are arrays of items wrapped in `{"json": {...}}`.

2. **Logic nodes don't need pin**: Switch, If, Code, Set, Filter, Merge nodes execute normally with data from upstream.

3. **Only pin external service nodes**: Telegram Trigger/Webhook, Telegram, PostgreSQL, Data Table, HTTP Request, and nodes with credentials.

4. **Test incrementally**: Test one path first, fix bugs, then test the next path.

5. **Use realistic data**: Match the actual data shape that the real service would return. For Webhook triggers, ALWAYS wrap in `body`.

6. **Don't pin logic nodes you want to test**: If you want to test the Session Manager's output, DON'T pin it. If you must pin it (e.g. it depends on a credential node), include ALL fields the downstream logic relies on.

---

## Pitfall: pinData Type

The `test_workflow` tool expects `pinData` as a **JSON object** (dict), not a JSON string. If you get `invalid_type: expected object, received string`, make sure you're passing a proper object, not `json.dumps()` output.

---

## Pitfall: Webhook body wrapper mismatch

The most common testing mistake: providing Telegram Trigger-shaped pin data (`{"message": {...}}`) for a Webhook-based workflow that expects `{"body": {"message": {...}}}`.

**How to detect this in execution logs:**
- Extract Input Data (Code node) returns ALL EMPTY fields (`chat_id: ""`, `text: ""`)
- Every downstream node gets empty data
- Route by Type falls through to Fallback

**Root cause:** The Code node checks `item.message` but the data is at `item.body.message`.

**Fix in test:** Change pin data from `{"message": {...}}` to `{"body": {"message": {...}}}`.

**Fix in workflow (permanent):** Make Extract Input Data support both structures:
```javascript
const body = item.body || item;
const msg = body.message || body;
const cbq = body.callback_query;
```

---

## Pitfall: Session Manager pin data (missing callback_data)

When you pin Session Manager (a Code node), you MUST provide ALL fields it would normally produce, including `callback_data`:

```json
"Session Manager": [{"json": {
  "chat_id": "66881162",
  "user_id": "66881162",
  "text": "",
  "callback_data": "weight_1_250",
  "message_id": "150",
  "input_source": "callback",
  "state": "selecting_weight",
  "cart_json": "[]",
  ...
}}]
```

If `callback_data` is missing, the Weight Handler won't receive it because Session Manager's code (`$('Extract Input Data').first().json.callback_data`) is never executed when pinned.

---

## Pitfall: Route by State exact state names

Switch nodes check for exact string matches. Before building pin data:
1. Check the Switch node's conditions directly (via `get_workflow_details`)
2. Use the exact state name from the condition — e.g. `"selecting_weight"` not `"weight_selecting"`
3. Wrong state names cause the fallback output to fire instead of the intended branch

---

## Pitfall: Set node expression `\\n` in pin test (and all JSON-sourced expressions)

Set node expressions sent via JSON (including through `test_workflow`'s pin data) need `\n` as `\\n` in the JSON string. This gets stored correctly by n8n. If you use single `\n`, the expression evaluates to a syntax error.

This is NOT a pin-data-specific issue — it affects any time you write Set node expression values through JSON (API, update_workflow, create_workflow_from_code).

---

## Debugging checklist when a test fails:

1. ✅ Check `get_execution(..., includeData=True)` → look at `lastNodeExecuted` and each node's `runData`
2. ✅ First check **Extract Input Data** output — does it have `chat_id`, `text`, `input_source`? If empty → trigger pin data has wrong structure (Webhook body wrapper mismatch)
3. ✅ Check **Answer Callback Query** — did it error? `callback_query_id: cannot be blank` → set `onError: continueRegularOutput`
4. ✅ Check **Session Manager** output — does it have all needed fields? (state, callback_data, cart_json, chat_id)
5. ✅ Check **Route by State** — which output index fired? (index N = Nth condition in Switch)
6. ✅ Check **Route by Type** / **Weight Handler** — does the condition match the actual value?
7. ✅ Check **Set node expressions** — are `\\n` correctly escaped? Is `type: "array"` used with expression?
8. ✅ Check **Code node references** — if pinned, does pin data include what `$('OtherNode')` would serve?
9. ✅ Check **telegram node warnings** — `Invalid resource` on Telegram node means missing or wrong `resource` discriminator (expected `chat`, `callback`, or `file`)
10. ✅ Check **expressions referencing old trigger name** — `$('Telegram Trigger')` in any expression when the node is named `Webhook`

---

## Concrete Test Traces (from WF01 - Coffee Bot)

### Test 5601: `/start` command (new user) — PASSED ✅
```
Webhook (body.message.text=/start) → Extract Input Data (chat_id=66881162, text=/start, input_source=command)
→ Answer Callback Query (onError:continueRegularOutput → clean pass) → Get Session (empty)
→ Session Manager (state=idle, chat_id=66881162) → Route by State (idle → output 0)
→ Route by Type (/start → output 0) → Check User → User Found? (output 1, new user)
→ Register User → Format Welcome → Send Welcome → Save Welcome mid ✅
```

### Test 5608: `/menu` command — PASSED ✅
```
Webhook (body.message.text=/menu) → ... → Route by State (idle → output 0)
→ Route by Type (/menu → output 2) → Get Products (reads 5 products from products_cache)
→ Format Product Keyboard → Send Products ✅
```
**Output text:**
```
📦 محصولات ما:

1. ☕ قهوه ۱۰۰٪ عربیکا
2. ☕ قهوه ۵۰٪ عربیکا ۵۰٪ روبستا
3. ☕ قهوه ۷۰٪ عربیکا ۳۰٪ روبستا
4. ☕ قهوه ۱۰۰٪ روبستا
5. ☕ اسپیشیالیتی (لاین ویژه)

روی نام محصول کلیک کنید 👇
```

### Test 5595: Weight selection with stock — PASSED ✅
```
Webhook (callback_query.data=weight_1_250) → ... → Route by State (selecting_weight → output 1)
→ Weight Handler (starts with "weight_" → output 0) → Extract Weight Data (product_id=1, grams=250)
→ Check Stock (stock_250g=50 >= 1) → Stock Available (true → output 0)
→ Build Cart → Save Cart → Cart Success Message ✅
```

### Test 5596: Weight selection no stock — PASSED ✅
```
... → Check Stock (stock_100000g not found) → Stock Available (false → output 1) → Stock Error ✅
```

### Test 5591: `/cart` with items — PASSED ✅
```
... → Route by Type (/cart → output 3) → Check Cart Empty (has items → output 1)
→ Format Cart Items → Show Cart Items → Validate Cart → Request Address → Set Checkout State ✅
```
**Format Cart Items output:** `{"text":"سبد خرید شما:\nCoffee Arabica | 1x250g = 150000\n\nجمع کل: 150000","cart_total":150000}`
