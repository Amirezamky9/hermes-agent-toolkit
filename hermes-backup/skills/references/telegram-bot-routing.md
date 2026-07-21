# Telegram Bot Routing Architecture (n8n)

## Three-Layer Routing Pattern (v2 — Type-First)

The core routing architecture for n8n Telegram bots uses:

```
Telegram Trigger
      ↓
[Core Router: 4 Routes (Type-First)]
      ↓        ↓         ↓           ↓
  COMMANDS  CALLBACKS  FREE_TEXT  SESSION MGMT
      ↓        ↓         ↓           ↓
  [Process] [Process]  [State Check]  [Save]
                          ↓
                    [idle → AI/Fallback]
                    [checkout_address → Address]
                    [searching_order → Tracking]
```

### Layer 1: Core Router — Detect Input Type (Type-First)

**Pattern: detect input TYPE first, then check session STATE only for free text.**
COMMANDS and CALLBACKS always work regardless of state.

| Output | Rule | Route |
|--------|------|-------|
| 0 | COMMANDS — `message.text` matches `^/` | /start, /menu, /cart, /orders |
| 1 | CALLBACKS — `callback_query` exists | Button clicks |
| 2 | FREE TEXT — `message.text` exists, not starting with / | Free text (state-restricted) |
| Fallback | none | Log + default response |

**⚠️ Output order matters:** COMMANDS first (regex `^/`), CALLBACKS second, FREE TEXT third.

**❌ Do NOT add Answer Callback Query node.** After editMessageText, Telegram removes loading state automatically. Connect Telegram Trigger directly to Switch.

### Layer 2: Session State Check (FREE TEXT only)

After FREE TEXT is detected, check session state:

| Output | State | Handler |
|--------|-------|---------|
| 0 | idle | AI Agent / Default fallback |
| 1 | selecting_weight | ❌ "Use buttons, not text" |
| 2 | checkout_address | Save as address |
| 3 | searching_order | Search tracking code |
| Fallback | unknown | "I didn't understand" |

### Layer 3: Route Callback — Callback Data Routing

| Output | Pattern | Handler |
|--------|---------|---------|
| 0 | equals "view_products" | Show products |
| 1 | startsWith "view_product_" | Product detail |
| 2 | equals "back_to_menu" | Back to menu |
| 3+ | etc. | ... |
| Fallback | none matched | Unknown callback |

## 🎯 Key Changes from v1

| Topic | ❌ Old (v1) | ✅ New (v2) |
|-------|------------|------------|
| **Routing order** | State-First → Type-Second | **Type-First** → State only for FREE TEXT |
| **message_id** | Stored in DataTable | Use `$json.callback_query.message.message_id` directly |
| **Answer Callback Query** | Separate node | **Not needed** — editMessageText is sufficient |
| **User blocked?** | /start couldn't reach COMMANDS due to state check | /start always works (Type-First) |

### Layer 3: Route Callback — Callback Data Routing

Routes based on `$json.callback_data` from button presses.

| Output | Condition | Example Data | Handler |
|--------|-----------|-------------|---------|
| 0 | equals "view_products" | `view_products` | → Get Products |
| 1 | startsWith "view_product_" | `view_product_1` | → Get Product Detail |
| 2 | equals "back_to_menu" | `back_to_menu` | → Edit Back to Menu |
| 3 | equals "view_cart" | `view_cart` | → Check Cart Empty |
| 4 | equals "view_orders" | `view_orders` | → View Orders |
| 5 | equals "support" | `support` | → Support |
| 6 | equals "checkout" | `checkout` | → Validate Cart |
| 7 | equals "clear_cart" | `clear_cart` | → Clear Cart |
| 8 | startsWith "weight_" | `weight_1_250` | → **Weight Handler (safety net)** |
| Fallback | none matched | others | → Other Callbacks handler |

**Key rule**: Conditions use `equals` for exact match and `startsWith` for pattern matches (e.g., `view_product_*`). All outputs should be defined in order with the fallback as the last.

## Callback Data Naming Convention

Consistent naming prevents routing conflicts:

```
view_products       → مشاهده لیست محصولات
view_product_{id}   → جزئیات یک محصول (id = DataTable row ID)
weight_{id}_{grams} → انتخاب وزن (grams = 250, 500, 1000)
back_to_menu        → بازگشت به منوی اصلی
view_cart           → مشاهده سبد خرید
view_orders         → پیگیری سفارش‌ها
support             → پشتیبانی
```

### Data Parsing from callback_data

```javascript
// Extract product_id and grams from "weight_1_250"
const parts = $json.callback_data.split('_');  // ["weight", "1", "250"]
const product_id = parts[1];                     // "1"
const grams = parseInt(parts[2]);                // 250
```

## Inline Keyboard Button Structure

```json
{
  "replyMarkup": "inlineKeyboard",
  "inlineKeyboard": {
    "rows": [
      {
        "row": {
          "buttons": [
            {
              "text": "🛍 مشاهده محصولات",
              "additionalFields": {
                "callback_data": "view_products"
              }
            }
          ]
        }
      },
      {
        "row": {
          "buttons": [
            {
              "text": "🛒 سبد خرید",
              "additionalFields": {
                "callback_data": "view_cart"
              }
            },
            {
              "text": "📦 پیگیری سفارش",
              "additionalFields": {
                "callback_data": "view_orders"
              }
            }
          ]
        }
      }
    ]
  }
}
```

**Critical details:**
- `replyMarkup` MUST be `"inlineKeyboard"` (not `"inline_keyboard"`)
- `rows` is an array of `{ "row": { "buttons": [...] } }` objects
- Each button is `{ "text": "...", "additionalFields": { "callback_data": "..." } }`
- The Telegram node MUST have `resource: "message"` + `operation: "sendMessage"` for the inline keyboard to render
- Without `resource: "message"` discriminator, the `inlineKeyboard` parameter is ignored and no buttons appear

## Updating Telegram Node Discriminators (Fix for Missing Buttons)

When inline keyboards don't appear, the most common cause is missing `resource` + `operation` discriminators on Telegram nodes.

**Fix via update_workflow:**

```json
{
  "type": "updateNodeParameters",
  "nodeName": "Send Welcome",
  "parameters": {
    "resource": "message",
    "operation": "sendMessage",
    "chatId": "={{ $('Extract Input Data').first().json.chat_id }}",
    "text": "={{ $json.text }}",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": { "rows": [...] },
    "additionalFields": { "parse_mode": "HTML", "appendAttribution": false }
  },
  "replace": true
}
```

## Fixing Misrouted Switch Connections

When a Switch node's outputs are connected to wrong downstream nodes (common after adding/removing conditions):

**Step 1**: Remove the bad connection first, then add the correct one.

```json
// Batch 1: Fix output connections
[
  { "type": "removeConnection",
    "source": "Route Callback", "sourceIndex": 1,
    "target": "Edit Back to Menu" },
  { "type": "addConnection",
    "source": "Route Callback", "sourceIndex": 1,
    "target": "Get Product Detail" },
  { "type": "addConnection",
    "source": "Route Callback", "sourceIndex": 2,
    "target": "Edit Back to Menu" }
]
```

**Step 2**: Verify with `get_workflow_details` or run a test with pin data.

**Common pitfalls:**
- `removeConnection` for a non-existent connection FAILS the entire atomic batch. Remove connections separately from adds.
- Switch output indices correspond to condition order in `rules.values[]`. Adding a new condition shifts all subsequent indices.
- After updating conditions via `updateNodeParameters`, previously connected outputs may become `null` (disconnected) — reconnect them explicitly.
- The `addConnection` call MUST use `sourceIndex` matching the new condition index.

## Testing callback_query with Pin Data

Structure pin data to simulate a real button press:

```json
"Wehbok": [{"json": {
  "body": {
    "callback_query": {
      "data": "view_product_1",
      "from": { "id": 66881162, "is_bot": false, "first_name": "کاربر" },
      "id": "abc123",
      "message": {
        "chat": { "id": 66881162, "type": "private", "first_name": "کاربر" },
        "date": 1782755903,
        "message_id": 136,
        "text": "☕ متن پیام قبلی..."
      }
    },
    "update_id": 144
  },
  "executionMode": "test"
}}]
```

Key fields:
- `body.callback_query.data` → what the button sends (`view_product_1`, `weight_1_250`, etc.)
- `body.callback_query.message.chat.id` → chat_id (NOT at `callback_query.chat.id`)
- `body.callback_query.id` → callback_query_id for Answer Callback Query
- `body.callback_query.message.message_id` → message_id for editMessageText

## Session Persistence: DataTable `update` vs `upsert`

**⚠️ تله بحرانی:** نودهایی که سشن رو ذخیره می‌کنن (`Set Selecting Weight`, `Save Cart`, `Save Welcome mid`, `Save Address`) از `operation: "update"` استفاده می‌کنن. ولی اگه کاربر سشن نداشته باشه (کاربر جدید، جدول دیتابیس جدید)، `update` روی ردیف وجود نداره ۰ ردیف برمی‌گردونه — **بدون خطا و هشدار** — و downstream هرگز اجرا نمی‌شه.

**رفع:** همه رو به `operation: "upsert"` با `resource: "row"` تغییر بده:
```json
{
  "resource": "row",
  "operation": "upsert",
  "dataTableId": {"__rl": true, "mode": "id", "value": "TABLE_ID"},
  "matchType": "allConditions",
  "filters": {"conditions": [{"keyName": "telegram_id", "keyValue": "={{ chat_id }}"}]},
  "columns": {
    "mappingMode": "defineBelow",
    "value": {
      "state": "selecting_weight",
      "selected_product_id": "={{ $('Format Product Detail').first().json.product_id }}",
      "updated_at": "={{ $now.toISO() }}"
    },
    "schema": [...]
  },
  "options": {}
}
```

> DataTable operation `upsert` = update if exists, insert if not. `resource: "row"` discriminator الزامیه.

```
/user sends /start
  → Webhook → Extract Input Data → Register User (if new)
  → Format Welcome → Send Welcome (with 4 inline buttons)
  → user clicks 🛍 مشاهده محصولات
  → Webhook (callback_query: view_products)
  → Route by State (idle → 0)
  → Route by Type (callback → 1)
  → Route Callback (view_products → 0)
  → Get Products → Format Product Keyboard → Send Products
  → user clicks product "قهوه ۱۰۰٪ عربیکا"
  → Webhook (callback_query: view_product_1)
  → Route by State (idle → 0)
  → Route by Type (callback → 1)
  → Route Callback (view_product_* → 1)
  → Get Product Detail → Format Product Detail → Show Product Detail (weight buttons)
  → Set Selecting Weight (state = selecting_weight)
  → user clicks 🟢 ۲۵۰ گرم
  → Webhook (callback_query: weight_1_250)
  → Route by State (selecting_weight → 1)
  → Weight Handler (startsWith weight_ → 0)
  → Extract Weight Data → Check Stock → Stock Available → Build Cart → Save Cart → Cart Success Message
```
