# Trap Reference — Build-time Errors & Solutions

> Load this ON EVERY DataTable-related batch, not just on errors.
> If the user says "نجات بده"، "خالیه"، or "پارامتر نداره" → read Traps 28, 30, 37, 39, 41, 44, 46 immediately.
> If cart items vanish on re-add → read Trap 50.
> If /menu returns 404 → read Trap 51.
> If remove from cart does nothing → read Trap 52.
> Call: `skill_view('n8n-builder', file_path='references/trap-reference.md')`

## SDK code traps

### Trap 1-2: TypeScript annotations & function declarations
❌ `function makeNode(name: string) {` or `const foo: Bar = {...}`
✅ No type annotations, no function declarations — everything inline

### Trap 3: `settings` in SDK config ignored
❌ `config: { name: 'X', parameters: {...}, settings: {...} }`
✅ Create first, then `setNodeSettings` via `update_workflow`

## Telegram node traps

### Trap 4: Wrong discriminator

⚠️ **CRITICAL: `resource: "chat"` + `operation: "sendMessage"` = BROKEN.** n8n silently ignores sendMessage when resource is `chat`. The node exists in the canvas but never sends anything.

| Operation | Correct `resource` | Correct `operation` |
|-----------|-------------------|-------------------|
| sendMessage | `message` | `sendMessage` |
| editMessageText | `message` | `editMessageText` |
| answerCallbackQuery | `callback` | `answerQuery` |

**Common mistakes:**
- Setting `resource: "chat"` on a sendMessage node → node created but NEVER sends. `chat` resource is ONLY for: `get`, `administrators`, `member`, `leave`, `setDescription`, `setTitle`.
- Omitting `resource` entirely → validation warning "Missing discriminator", but node may still work at runtime. Still, always set it.
- For `editMessageText`, you also need `messageId` parameter (the message being edited).

**Fix after applying `updateNodeParameters` with `replace: true`:** `replace: true` nukes ALL parameters including `resource` and `operation`. Always re-include them in the replace payload:
```json
{ "type": "updateNodeParameters", "nodeName": "📞 Ask Phone",
  "parameters": { "resource": "message", "operation": "sendMessage",
    "chatId": "={{ $json.chat_id }}", "text": "...", "additionalFields": {} },
  "replace": true }
```

### Trap 5: Auto-credential picks wrong bot
After every create, explicitly set credentials with `setNodeCredential`.
n8n auto-assigns the first matching credential, often the wrong bot token.

**Symptom after `setNodeCredential`:** `get_workflow_details` shows `credentials: {}` in the raw node JSON — **this is normal**. The credential is stored at the workflow level in `autoAssignedCredentials`, not in each node's raw JSON. Don't be misled by empty `credentials: {}` in get_workflow_details output.

**Use `list_credentials` to find the RIGHT credential, then always reference by ID and name:**
```json
{ "type": "setNodeCredential", "nodeName": "📞 Ask Phone",
  "credentialKey": "telegramApi", "credentialId": "78sfmXZgmLK4r8lq",
  "credentialName": "bale_bot_evet_rosteri" }
```

### Trap 7: `inlineKeyboard` expression — DO NOT USE FOR DYNAMIC KEYBOARDS

❌ Using `"inlineKeyboard": "={{ $json.rows }}"` or `"inlineKeyboard": "={{ JSON.parse($json.rows) }}"` on a Telegram node produces a `INVALID_PARAMETER` warning. Although it works at runtime, the Telegram node's expression-based inlineKeyboard is unreliable.

✅ **For dynamic keyboards: use Code node → HTTP Request.** Code node outputs `{ text, inline_keyboard }` (raw Telegram 2D array), HTTP Request calls the API directly. This produces zero warnings and is fully reliable.

✅ **For static keyboards: use Telegram node native `inlineKeyboard: { rows: [...] }`.** Write inline directly in params, NO expression needed, NO Code node needed.

### Trap 8: Auto-credential picks wrong bot
If a downstream Telegram node has its own `inlineKeyboard` config, the Code node's dynamic keyboard is silently ignored. **Fix:** Don't define inlineKeyboard on both nodes.

### Trap 26: Test webhook (webhook-test) mocks Telegram API
Telegram node returns `message_id: 0` in test mode — no real API call is made.
Only production webhook URL actually sends messages. Activate WF to test for real.

### Trap 36: Answer Callback Query often unnecessary
If your bot uses `editMessageText` for every callback, Answer Callback Query is redundant. Editing the message itself acknowledges the button press.

## Switch/If node traps

### Trap 6: Nested switchCase chains must be inline
```typescript
// ✅ Correct — all .onCase() inside the chain
routeByState.onCase(0, routeByType.onCase(0, handler1).onCase(1, handler2))

// ❌ Wrong — disconnected .onCase() calls lose connections
```

### Trap 20: Switch conditions need complete structure
❌ `"conditions": [{ "leftValue": "...", ... }]` — array only → FILTER_MISSING_ERROR
✅ `"conditions": { "combinator": "and", "conditions": [...], "options": { "version": 3 } }`

### Trap 27: Switch output shift after condition changes
When updating Switch from N to M conditions, existing connections shift to wrong indices.
**Fix:** Remove connections in ONE batch, then add connections in a SEPARATE batch.

## Set node traps

### Trap 14: `assignments` must be nested object
✅ `"assignments": { "assignments": [{ "id": "a1", "name": "title", "value": "...", "type": "string" }] }`
❌ `"assignments": [{ "name": "title", "value": "...", "type": "string" }]`

### Trap 16: `\n` in JSON payload breaks expression parser
In JSON, `\n` becomes actual newline. n8n expression parser breaks on real newlines.
✅ Use `\\n` in JSON: `"value": "={{ 'line1\\\\nline2' }}"`

### Trap 17: `type: "array"` with expression errors
❌ `{ "type": "array", "value": "={{ JSON.parse(...) }}" }` → syntax error
✅ Use `type: "string"` for expression values that are arrays.

## Code node traps

### Trap 24: Use `jsCode` NOT `sourceCode` in addNode
❌ `"sourceCode": { "javascript": "..." }` → silently ignored by addNode
✅ `"jsCode": "const items = $input.all(); ..."`

### Trap 33: Code v2 `runOnceForAllItems` cannot multi-output
❌ `return [[output0], [output1]]` → runtime error
✅ Single output with flag + If node downstream for routing

## 🎯 DataTable traps — CRITICAL CLUSTER

### Trap 27: DataTable `upsert` with empty `columns.value` = `state: null` → Switch Fallback

**مشکل:** وقتی `upsert` رو درست ست می‌کنی ولی `columns.value` فقط `telegram_id` رو داره (حالت خالی).
upsert ردیف رو می‌سازه ولی بقیه ستون‌ها (مثل `state`) رو `null` ذخیر می‌کنه.
Switch بعدی هیچ conditionی match نمی‌کنه → Fallback می‌خوره. هیچ خطایی هم نمی‌بینی.

**تشخیص تو execution log:**
```
Create Session → { state: null, telegram_id: "123", ... }
Route by State → output 5/5 (Fallback) ← ۰ تا از ۵ تا condition match شدن
```

**رفع:** `columns.value` رو با ALL فیلدهایی که می‌خوای ست بشن پر کن:
```json
"columns": {
  "value": {
    "telegram_id": "={{ $('Extract Input Data').first().json.user_id }}",
    "state": "idle"                    // ← اینو فراموش نکن!
  }
}
```

**یادت باشه:** `replace: true` روی DataTable → می‌تونه `columns.value` رو نابود کنه. همیشه بعد از `replace: true` چک کن.

### Trap 28: DataTable filter needs `keyName`
❌ `"filters": { "conditions": [{ "keyValue": "..." }] }` → 0 results silently
✅ `"filters": { "conditions": [{ "keyName": "id", "keyValue": "..." }] }`

### Trap 28b: DataTable returns `main: [[]]` — table is empty
If `Get Products` succeeds but outputs `main: [[]]` (one empty item per schema column → zero data rows), the filter may be correct but the **table itself is empty**.
**Diagnosis:** Check the table directly with `search_data_tables` → look at the `updatedAt` field or check if any rows exist. A freshly created `products_cache` table has 0 rows. The filter `is_active: isTrue` returns nothing.
**Fix:** Populate the table with sample rows using `add_data_table_rows`.

### Trap 30: `update` with no matching row = silent 0-row update
Use `upsert` (update OR insert) instead of `update` when the row might not exist.

### Trap 37: addNode drops DataTable complex params
`resource`, `operation`, `filters.conditions.*.keyName`, `columns.value`, and `data.keyValue` silently dropped by addNode for DataTable nodes.
**Fix:** addNode with bare minimum (name/type/version/position), then `updateNodeParameters(node_name, full_params, replace: true)`.
**DO NOT use this as excuse to archive the whole WF.**

### Trap 39: DataTable `keyValue` must be string, not boolean
❌ `"keyValue": true` → validator: "expected string, got boolean"
✅ `"keyValue": "true"`

### Trap 41: DataTable `columns.value: {}` — writes nothing
❌ `"columns": { "schema": [...], "value": {} }` → n8n shows empty fields, writes nothing
✅ `"columns": { "schema": [...], "value": { "state": "selecting_weight", ... } }`
The `schema` defines WHICH columns exist. The `value` defines WHAT to write. Both are required.
**Only include columns in schema that have a value. Extra schema columns with no value appear empty on the canvas.**

### Trap 46: DataTable update/upsert needs BOTH `columns.value` AND `data.keyValue`
❌ Setting only `columns.value: { "state": "idle" }` → n8n may show the value in the UI but DataTable skips it at runtime.
✅ Both must be populated with the same pairs:
```json
{
  "columns": {
    "schema": [{ "id": "state", "displayName": "state", "type": "string" }],
    "value": { "state": "idle" }
  },
  "data": {
    "keyValue": [
      { "keyName": "state", "keyValue": "idle" }
    ]
  }
}
```
The two structures are redundant but the n8n UI uses one and the API uses the other. Always set both.

### DataTable Quick Fix Flowchart

```
DataTable node has empty params on canvas?
├── YES → check `columns.value`
│   ├── `{}`? → Trap 41. Add key-value pairs matching the schema.
│   └── Has values? → check `data.keyValue`
│       ├── Missing? → Trap 46. Add both fields.
│       └── Has values? → check for `keyName` in filters (Trap 28).
├── Still empty after fixing all? → addNode dropped them (Trap 37).
│   Re-run `updateNodeParameters(node, full_params, replace: true)`.
│
DataTable update does nothing at runtime?
├── Row might not exist → Trap 30. Change `operation` to `upsert`.
├── Row exists but no match → Trap 28. Check `filters.conditions[n].keyName`.
│
DataTable shows "expected string, got boolean"?
└── Trap 39. Wrap booleans in strings: `"keyValue": "true"`.
```

## HTTP Request traps

### Trap 29: Body parameters need `name` field
❌ `{ "value": "={{ ... }}" }` → 400 Bad Request
✅ `{ "name": "chat_id", "value": "={{ ... }}" }`

### Trap 45: HTTP Request node cannot use `telegramApi` credential
❌ `setNodeCredential` with `credentialKey: "telegramApi"` on an HTTP Request node → error
✅ No credential needed — the bot token is embedded in the URL expression: `={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText'}}`. The `$credentials()` function resolves it at runtime.

## Update workflow traps

### Trap 38: create_workflow_from_code silently truncates >20 nodes
No error message. Always check nodeCount with `get_workflow_details` after every create.

### Trap 19: `setNodeParameter` nesting bug — affects ANY deep path, not just Code nodes

> **وقتی از `setNodeParameter` با `path` تودرتو استفاده می‌کنی (مثلاً `/parameters/jsCode` یا `/parameters/columns/value/last_sent_at`)، یه لایه اضافه `parameters.parameters.*` توی ساختار نود ایجاد می‌شه که n8n اون رو نادیده می‌گیره.**

Affects Code nodes, DataTable nodes, **Set nodes**, and any node with nested parameter paths.

```json
// ❌ غلط — nested layer created silently
{ "type": "setNodeParameter", "nodeName": "🏷️ Category Menu",
  "path": "/parameters/jsCode", "value": "..." }
{ "type": "setNodeParameter", "nodeName": "🆕 Init Session",
  "path": "/parameters/columns/value/last_sent_at", "value": "={{ $now.toISO() }}" }
{ "type": "setNodeParameter", "nodeName": "📦 Build Order Data",
  "path": "/parameters/assignments/assignments", "value": [...] }  // ← parameters.parameters.assignments خراب!

// ✅ درست — updateNodeParameters with replace: true overwrites the whole object
{ "type": "updateNodeParameters", "nodeName": "🏷️ Category Menu",
  "parameters": { "jsCode": "...", "language": "javaScript", "mode": "runOnceForAllItems" },
  "replace": true }
{ "type": "updateNodeParameters", "nodeName": "🆕 Init Session",
  "parameters": { "operation": "upsert", "columns": { "value": { "last_sent_at": "={{ $now.toISO() }}", ... } } },
  "replace": true }
{ "type": "updateNodeParameters", "nodeName": "📦 Build Order Data",
  "parameters": { "mode": "manual", "includeOtherFields": true,
    "assignments": { "assignments": [{ "id": "a1", "name": "order_code", ... }] } },
  "replace": true }
```

**Fix:** For ANY nested parameter (Code jsCode, DataTable columns.value, **Set assignments**, deep config), always use `updateNodeParameters` + `replace: true`. Never `setNodeParameter` on paths deeper than 1 level.

**Symptom of Set node nesting bug:** The node JSON shows BOTH `parameters.assignments.assignments` (the real one) AND `parameters.parameters.assignments.assignments` (the nested garbage). The nested one overrides — the assignments you set with `setNodeParameter` appear in the canvas but never actually execute. **Fix:** `updateNodeParameters` with `replace: true` and the COMPLETE payload including `mode: "manual"`, `includeOtherFields`, and `assignments` — this nukes the nested layer.

**Always include `mode: "manual"` in replace payload for Set nodes.** Without it, the node loses its mode and may not execute assignments.

### Trap 40: `setNodeParameter` field name is `path` NOT `paramPath`
❌ `{ "paramPath": "/parameters/resource", ... }` → cryptic "Invalid operations: operation 0.path: Required"
✅ The field is called `path`: `{ "path": "/parameters/resource", "value": "row" }`

### Trap 41: `setNodeParameter` with `path: "/"` rejected
❌ `{ "path": "/", ... }` → "must contain at least 2 characters"
✅ Use `updateNodeParameters` with `replace: true` instead.

### Trap 42: Code nodes lose position in addNode
If you omit `position` in an addNode call for a Code node, it defaults to `[0, 0]` silently.
✅ Always include `"position": [x, y]` on every addNode, including Code nodes.

### Trap 44: `updateNodeParameters` with `replace: true` nukes sibling keys — Telegram sendMessage stops working

❌ Running `updateNodeParameters` with `replace: true` on a Telegram node while providing only `chatId`, `text`, `inlineKeyboard` — `resource` and `operation` are silently destroyed. The node appears on the canvas but **never sends anything** — no error, no warning.

✅ Always include `resource`, `operation`, `additionalFields` etc. in the replace payload. `replace: true` does NOT merge — it COMPLETELY OVERWRITES the parameters object.

**Safe minimal replace payload for a sendMessage node:**
```json
{
  "resource": "message",
  "operation": "sendMessage",
  "chatId": "={{ $json.chat_id }}",
  "text": "Hello",
  "additionalFields": {}
}
```

**Safe minimal replace payload for an editMessageText node:**
```json
{
  "resource": "message",
  "operation": "editMessageText",
  "chatId": "={{ $json.callback_query.message.chat.id }}",
  "messageId": "={{ $json.callback_query.message.message_id }}",
  "text": "Updated",
  "additionalFields": {}
}
```

**Common symptoms of nuked params:**
- Node shows `resource: chat` or no resource at all after update → Telegram ignores it
- Node shows no `operation` field → node does nothing
- `editMessageText` node missing `messageId` → API returns 400

### Trap 47: `setNodeParameter` often fails on nested Switch/If options
❌ `{ "type": "setNodeParameter", "path": "/parameters/conditions/options/typeValidation", "value": false }` → the update succeeds (0 warnings) but the parameter is NOT actually changed at runtime.
✅ Use `updateNodeParameters` with `replace: true` and the full condition config including `"typeValidation": false` stripped from options. The `replace: true` approach forces the server to re-parse the entire parameters object.

### Trap 48: Postgres returns numbers for integer columns — IF/Switch condition type mismatch
When Postgres returns `{ "id": 3 }` (number), an IF node with `{{ $json.id }}` + `notEmpty` + `typeValidation: strict` errors with `Wrong type: '3' is a number but was expecting a string`.
**Fix:** Set `typeValidation: false` on both IF and Switch nodes. For Switch, do it per-condition in the options. For IF, set `conditions.options.typeValidation: false` — but use `replace: true` since `setNodeParameter` may not stick (Trap 47).

### Trap 49: `Session Found?` must NOT connect directly to Route by State
❌ `Session Found?` output 0 → both `Route by State` AND `Normalize Session` → Route by State executes BEFORE Normalize with `state: null`.
✅ `Session Found?` output 0 → ONLY `Normalize Session` → `Route by State`.
✅ `Create Session` → ONLY `Normalize Session` (NOT `Route by State`).
This ensures ALL session data passes through normalization before any state-dependent routing.

## Session JSON (cart) traps

### Trap 50: JSON cart overwritten instead of append-or-increment

**مشکل:** کد `const cart = [newItem]` همیشه سبد خرید قبلی رو نادیده می‌گیره و از صفر می‌سازه — هر بار که کاربر محصول جدید اضافه می‌کنه، محصول قبلی از بین می‌ره.

**علت ریشه:** Code node `💾 Save Cart` مستقیماً به `🛒 Add to Cart` وصل بود ولی `cart_json` موجود رو از سشن نمی‌خوند.

**الگوی درست (Read-Modify-Write):**
```
🛒 Add to Cart → 🔍 Fetch Session (از DataTable) → 💾 Save Cart (append/increment) → 💾 Update Session Cart (ذخیره تو DataTable)
```

**⚠️ CRITICAL — DataTable nodes DO NOT passthrough custom fields:**
وقتی یه DataTable رو بین دو Code node می‌ذاری، DataTable فقط ستون‌های خودش رو برمی‌گردونه. فیلدهای custom مثل `cartItem`, `chat_id`, `user_id` که توسط Code node قبلی ساخته شدن **نابود می‌شن**. ورودی `💾 Save Cart` فقط `{ user_id, chat_id, state, cart_json, ... }` رو داره — دیگه `cartItem` نداره!

**کد درست Save Cart (append-or-increment + cross-node ref):**
```javascript
const data = $input.first().json;

// ⚠️ DataTable dropped cartItem — read it from the upstream Code node directly
const addToCartOutput = $('🛒 Add to Cart').first().json;
const newItem = addToCartOutput.cartItem;

if (!newItem) return [{ json: data }];

// Read existing cart from session (fetched from upstream DataTable)
let cart = [];
if (data.cart_json) {
  try { cart = JSON.parse(data.cart_json); } catch(e) { cart = []; }
}

// Same product+weight → increment qty, else push new
const existingIdx = cart.findIndex(i => i.product_id === newItem.product_id && i.weight === newItem.weight);
if (existingIdx >= 0) {
  cart[existingIdx].qty += newItem.qty;
} else {
  cart.push(newItem);
}
return [{ json: { cart_json: JSON.stringify(cart), user_id, chat_id, action: 'add' } }];
```

**نکته ۱:** `data.cart_json` از خروجی `🔍 Fetch Session` میاد که از DataTable با `operation: get` سشن رو گرفته. همیشه قبل از modify یه Read بزن.

**نکته ۲ (`action` field):** به جای اینکه `cartItem` رو توی خروجی Save Cart بذاری (که بعد DataTable Update گم می‌شه و Route Confirmation خراب می‌کنه)، یه فیلد `action: 'add'` بذار. Route Confirmation با `$json.action == 'add' ? 0 : 1` Route می‌کنه — این فیلد از DataTable عبور می‌کنه چون توی `cart_json` نیست و DataTable اون رو تغییر نمیده.

**قانون:** بعد از هر DataTable در مسیر، اگه به فیلدهای ساخته‌شده توسط Code node قبلی نیاز داری، از `$('PreviousCodeNode').first().json` استفاده کن. به `data.*` تکیه نکن چون DataTable فقط ستون‌های خودش رو پاس میده.

### Trap 50b: Route Confirmation switch — use `action` field not `cartItem`

**مشکل:** Route Confirmation با `$json.cartItem ? 0 : 1` درست Route نمی‌کرد چون DataTable (`💾 Update Session Cart`) `cartItem` رو ذخیره نمی‌کنه و توی خروجی گمش می‌کنه.

**رفع:** Route Confirmation expression:
```
={{ $json.action == 'add' ? 0 : 1 }}
```
و توی Code node‌ها `action: 'add'` (برای افزودن) یا `action: 'remove'` (برای حذف) ست کن.

**مسیر نهایی Cart:**
```
افزودن: 🛒 Add to Cart → 🔍 Fetch Session for Add → 💾 Save Cart →
  ├─→ 💾 Update Session Cart (ذخیره در DataTable)
  └─→ 🔀 Route Confirmation[0] → ✅ Cart Confirmation (پیام موفقیت)

حذف: 🔍 Fetch Session for Remove → 🗑️ Remove Item →
  ├─→ 💾 Update Session Cart (ذخیره در DataTable)
  └─→ ✅ Cart Updated (پیام موفقیت)
```

### Trap 51: HTTP Request URL typo — `sendMessage` vs `editMessageText`

**مشکل:** وقتی آدرس HTTP Request برای sendMessage رو اشتباه بنویسی (مثلاً `SendeMessageText` یا آخرش `editMessageText` بذاری)، API 404 برمی‌گردونه و کاربر پیام خطا نمی‌بینه.

**علت ریشه:** کپی کردن URL از یه نود editMessageText و یادآوری نکردن که آخرش رو عوض کنی.

**قوانین:**
| URL suffix | When |
|------------|------|
| `/sendMessage` | برای کامندها (/menu, /start) — کاربر متن تایپ کرده، پیام جدید بفرست |
| `/editMessageText` | برای کالبک‌ها (دکمه فشرده) — پیام موجود رو ویرایش کن |

**رفع:** قبل از write هر HTTP Request برای Telegram API، چک کن:
1. آیا برای کامنده یا کالبک؟
2. آخر URL با عملگر درست مطابقت داره؟
3. `chat_id` از منبع درست گرفته شده؟ (کامند → `message.chat.id`، کالبک → `callback_query.message.chat.id`)

### Trap 52: Remove-item Code node referencing a node from another path

**مشکل:** `🗑️ Remove Item` از `$('🔍 Session Lookup')` استفاده می‌کرد ولی `🔍 Session Lookup` فقط توی مسیر TEXT هست و توی CALLBACK وجود نداره → `$input.first()` پاس داده نمی‌شه و `cart_json` خالی میاد.

**علت ریشه:** فرض کردن یه نود DataTable توی یه مسیر دیگه (TEXT) برای همه مسیرها (از جمله CALLBACK) در دسترسه.

**الگوی درست — هر مسیر سشن خودش رو بخونه:**
```
CALLBACK path:
  🔀 Callback Router[5] (cart_remove_) → 🔍 Fetch Session for Remove → 🗑️ Remove Item → 💾 Update Session Cart

TEXT path:
  🔀 Core Router[3] → 🔍 Session Lookup → 🔀 State Router → ...
```

**قانون:** هیچوقت با `$('SomeNodeInAnotherBranch')` به نودی که توی مسیر جاری وجود نداره رفرنس نده. برای هر مسیر، DataTable سشن رو جداگانه بخون.

## Routing traps

### Trap 31: Add `weight_` prefix fallback to Route Callback
When user presses a weight button but session state hasn't updated yet, Route Callback needs a `startsWith weight_` condition.

### Trap 34: Answer Callback Query drops all input data
After `answerQuery`, only `{ok: true, result: true}` remains. All `$json.*` from upstream become undefined.
✅ Reference upstream data with `$('Extract Input Data').first().json.*` instead.

### Trap 54: If node `regexMatch` operator is unreliable

**مشکل:** If node با `operator: { type: "string", operation: "regexMatch" }` گاهی درست کار می‌کنه، گاهی نه. مخصوصاً با اکسپرشن‌هایی که خودشون regex دارند مثل `{{ $json.message.text.match(/^09\d{9}$/) }}`.

**تشخیص:** If node خروجی false میده با اینکه ورودی درسته. هیچ خطایی توی execution log نیست.

**رفع:** همیشه از **boolean expression** استفاده کن:
```
leftValue: ={{ ($json.message.text || '').match(/^09\\d{9}$/) !== null }}
operator: { type: "boolean", operation: "equals" }
rightValue: true
```

leftValue خودش مستقیم true/false برمی‌گردونه، و If با boolean operator ساده مقایسه می‌کنه. این همیشه کار می‌کنه.

### Trap 55: Switch expression mode برای validation مناسب نیست

**مشکل:** Switch با `mode: "expression"` و خروجی `={{ $json.message.text.match(/^09\\d{9}$/) ? 0 : 1 }}` در عمل خروجی اشتباه میده و به fallback می‌خوره.

**علت:** Switch برای **routing** طراحی شده، نه validation. Fallback output رو در صورت عدم تطابق برمی‌گردونه که قابل پیش‌بینی نیست.

**رفع:** برای validation از **If node** با boolean expression استفاده کن. If دقیقاً دو خروجی داره: 0=true (ادامه) و 1=false (خطا).

| Scenario | Node | Why |
|----------|------|-----|
| Type detection (callback vs command vs text) | Switch | Route کردن، نه validation |
| State routing (checkout_name vs checkout_phone) | Switch | Route کردن |
| Input validation (phone format, postal length) | If | Boolean decision tree |

**مشکل:** وقتی با `addNode` یه Postgres با `operation: "executeQuery"` می‌سازی و `"columns": { "mappingMode": "defineBelow", "value": {...} }` توش باقی می‌مونه (مثلاً چون از template insert کپی شده)، n8n خطا میده: `Field "parameters.columns": This field is only allowed when operation=insert/update/upsert`.

**علت ریشه:** templateهای insert/upsert از ساختار `columns` استفاده می‌کنن ولی executeQuery نباید داشته باشهش.

**رفع:** بعد از addNode با `updateNodeParameters(nodeName, { operation: "executeQuery", query: "...", options: {...} }, true)` ستون‌ها رو پاک کن. `replace: true` کل parameters رو بازنویسی می‌کنه و `columns` دیگه وجود نداره.

**پیشگیری:** توی addNode برای executeQuery فقط این سه فیلد رو بذار: `operation`, `query`, `options`. هرگز `columns` نذار.

## Trap 56: `updateNodeParameters` batch with Unicode/Persian expressions fails

**مشکل:** وقتی ۲+ `updateNodeParameters` با expressions فارسی طولانی (حاوی Unicode مثل `\\\\n`, `\\n`, `\\'`) توی یه batch send می‌کنی، MCP خطا میده: `"Expected object, received string"`. خطا vague هست و معلوم نیست problem چیه.

**علت ریشه:** MCP serialization با Unicode strings طولانی در batch mode مشکل داره. هر operation بعد از اولین مورد corrupt میشه.

**تشخیص:**
- Response میگه `"Expected object, received string"` ولی payload تو JSON درسته
- با یه single operation همون payload کار می‌کنه
- خطا فقط با Persian/Unicode strings طولانی رخ میده، با ASCII کوتاه نه

**رفع:** هر `updateNodeParameters` با expressions Unicode رو **جداگانه** توی یه call خودش بفرست. batch فقط برای `addNode` + `addConnection` + `removeNode` + `removeConnection` استفاده کن.

```json
// ❌ غلط — با ۲+ updateNodeParameters فارسی تو یه batch
{ "operations": [
  { "type": "updateNodeParameters", "nodeName": "📄 Show Order Detail", "parameters": { "text": "... Persian with \\\\n ..." } },
  { "type": "updateNodeParameters", "nodeName": "📝 Confirm Approve Prompt", "parameters": { "text": "... Persian with \\\\n ..." } }
]}

// ✅ درست — هر کدوم تو یه call جدا
// Call 1:
{ "operations": [{ "type": "updateNodeParameters", "nodeName": "📄 Show Order Detail", "parameters": { "text": "..." } }] }
// Call 2:
{ "operations": [{ "type": "updateNodeParameters", "nodeName": "📝 Confirm Approve Prompt", "parameters": { "text": "..." } }] }
```

**Limitation confirmed on:** Provider `custom/opencode200k`, n8n version N/A (MCP layer).

## Trap 57: DataTable `addNode` with credential rejected

**مشکل:** وقتی `addNode` برای DataTable با `credentials: { telegramApi: {...} }` می‌فرستی، خطا می‌گیری: `"node type 'n8n-nodes-base.dataTable' does not accept credential 'telegramApi'"`.

**علت ریشه:** DataTable نود credential نمی‌خواد — مستقیماً به MCP server خودش وصل میشه. برخلاف Telegram/Postgres که credential لازم دارن.

**رفع:** DataTable رو بدون `credentials` field بساز:
```json
// ❌ غلط
{ "type": "addNode", "node": { "name": "🏁 Set state: idle",
  "type": "n8n-nodes-base.dataTable", "typeVersion": 1.1,
  "credentials": { "telegramApi": { "id": "...", "name": "..." } },  // ← rejected
  "parameters": { ... }, "position": [0, 0] }}

// ✅ درست
{ "type": "addNode", "node": { "name": "🏁 Set state: idle",
  "type": "n8n-nodes-base.dataTable", "typeVersion": 1.1,
  "parameters": { ... }, "position": [0, 0] }}  // ← no credentials
```

**همین قانون برای DataTable `updateNodeParameters` با `replace: true`:** credential رو توی replace payload نذار — فقط parameters رو بفرست.

## Postgres traps

### Trap 58: `replace: true` on Postgres executeQuery nukes credentials

**مشکل:** وقتی `updateNodeParameters` با `replace: true` روی یه Postgres executeQuery نود می‌زنی، credential نود detached میشه. دفعه بعد خطا میده: `"relation ... does not exist"` چون اصلاً به دیتابیس وصل نشده.

**تشخیص:** `get_workflow_details` → `credentials: {}` برای اون نود (خالی).

**رفع:** بعد از هر `replace: true` روی Postgres، credential رو برگردون:
```json
{ "type": "setNodeCredential", "nodeName": "🔍 Get Pending Order",
  "credentialKey": "postgres", "credentialId": "3pjdkIFwE1sGBCvJ",
  "credentialName": "locall main db" }
```

**پیشگیری:** برای تغییرات کوچیک کوئری از `setNodeParameter(path="/parameters/query")` استفاده کن. فقط برای بازنویسی چند پارامتر از `replace: true` استفاده کن.

### Trap 59: Unicode chars in `string_agg` cause phantom "relation does not exist"

**مشکل:** کرکترهای Unicode مثل `'×'` و `'\\n'` داخل `string_agg` باعث خطای `"relation ... does not exist"` با اینکه جدول وجود داره.

**علت:** n8n Postgres v2 driver Unicode sequences رو موقع پارس query replacement خراب میکنه.

**رفع:** `string_agg` طولانی رو به یه نود Postgres جدا بشکن + `📊 Aggregate` نود (mode: `aggregateAllItemData`):
```
🔍 Get Pending Order (ساده)
  → 🔍 Get Items for Pending Order (فقط SELECT از order_items)
    → 📊 Aggregate Items (چند ردیف → یکی)
      → 📝 Build Caption
```

بعد از Aggregate از `$json.product_name_arr`, `$json.weight_arr` (آرایه) استفاده کن.

**expression نمونه:**
```
={{ (() => { const a = $('📊 Aggregate Items').first().json; 
  if (!a.product_name_arr) return '---'; 
  return a.product_name_arr.map((n,i) => '☕ ' + n + ' (' + a.weight_arr[i] + 'g)').join('\\n'); })() }}
```

### Trap 60: Postgres multi-row before Telegram = duplicate sends

**رفع:** همیشه `📊 Aggregate` بین Postgres چند-ردیفی و Telegram بذار.

## Wiring & Topology traps

### Trap 61: Postgres v2 vs v2.6 — different credential namespace, same visible credential name

**مشکل:** یه ورک‌فلو بعضی نودهای Postgres رو `typeVersion: 2` و بعضی رو `typeVersion: 2.6` داره. هر دو از credential با اسم یکسان استفاده می‌کنن (مثلاً `"locall main db"`) ولی **v2 به یک کانکشن متفاوت از v2.6 بایند میشه**. نودهای v2 خطا می‌دن: `relation "... does not exist"` با اینکه نود v2.6 روی **همون دیتابیس و همون جدول** جواب میده.

**علت ریشه:** `typeVersion` در Postgres به عنوان credential namespace عمل می‌کنه. موقع آپدیت از v2→2.6، credential reference با name حفظ میشه ولی resolved شدنش از pool متفاوتی می‌گذره. اگه بایندینگ به دیتابیس متفاوتی resolved بشه، v2 صادقانه می‌گه جدول وجود نداره.

**تشخیص توی execution log:**
```
🔍 Get Pending Order (v2): "relation \"orders\" does not exist"
📋 Insert Order Items (v2.6): success — same credential name, same query target
```

**رفع:** همه نودهای Postgres توی یه ورک‌فلو رو به یه `typeVersion`統一 منتقل کن. بعد از migrate، با `get_workflow_details` چک کن credential همه نودها ست شده. اگه خالی بود با `setNodeCredential` برگردون.

### Trap 62: Converging parallel branches cause duplicate node execution

**مشکل:** دو نود (`N1`, `N2`) هر دو به یه نود downstream واحد (`Target`) وصل شدن. `Target` تو expressionsش به `$('N2').first().json` رفرنس میده. وقتی `Target` اول از `N1` دیتا می‌گیره (قبل از اینکه `N2` اجرا بشه)، `N2` "hasn't been executed" → ارور. بعد `N2` هم به `Target` می‌ده → `Target` **دوبار** اجرا میشه.

**Symptom توی execution log:**
```
📝 Build Receipt Caption[0]: start → error "Node '📊 Aggregate Items' hasn't been executed"
📝 Build Receipt Caption[1]: start → success (نسخه دوم بعد از اجرای Aggregate)
📦 Set Status: Awaiting Approval[0]: success
📦 Set Status: Awaiting Approval[1]: success  (← دوبار!)
```
همه چیز پایین‌دست **۲ بار** اجرا میشه — دوتا پیام به ادمین، دوتا DB update.

**Topology کلاسیک که باعث این میشه:**
```
🔍 Get Pending Order
  ├── 🔍 Get Admin ──────→ 📝 Build Receipt Caption
  └── 🔍 Get Items ──→ 📊 Aggregate ──→ 📝 Build Receipt Caption
```
`📝 Build Receipt Caption` دو تا incoming connection داره → دو execution slot می‌گیره → توی slot اول `$('📊 Aggregate Items')` هنوز اجرا نشده.

**تشخیص:** چک کن نود Set/Telegram/Postgres بیشتر از یه incoming connection داره یا نه. اگه آره، هر کدوم از نودهای upstream یه run مستقل ایجاد می‌کنه.

**گزینه‌های رفع (یکی رو انتخاب کن):**
1. **حذف connection اضافی** — اگه `Target` از یه مسیر دیتای کامل رو داره، connection دوم رو قطع کن (مثلاً `📊 Aggregate → 📝 Build Receipt Caption → حذف شد).
2. **استفاده از subquery مستقیم** — اگه نودی مثل `🔍 Get Pending Order` می‌تونه توی یه کوئری `string_agg` همه items رو فرمت کنه و به `items_summary` بده، مسیر Aggregate بی‌نیاز میشه و می‌شه قطعش کرد.
3. **Merge نود** — اگه واقعاً به دیتای هر دو مسیر نیاز داری، یه Merge نود بذار تا صبر کنه هر دو برسن بعد بره جلو.
4. **$if + fallback** — توی expression از `$if($('📊 Aggregate Items').isExecuted, ..., $('🔍 Get Pending Order').first().json.items_summary)` استفاده کن.

**پیشگیری:** موقع wiring مسیرهای موازی، قبل از اتصال به یه نود مشترک چک کن چندتا source داره. اگه >1 تا بود تصمیم بگیر: به Merge نیاز داره یا یه مسیر می‌تونه همه چی رو حمل کنه.

---

## Summary: quick fix table

| Symptom | Likely trap | Quick fix |
|---------|-------------|-----------|
| If node regexMatch condition always false | Trap 54 (regexMatch unreliable) | Use boolean expression: `{{ ($json.message.text || '').match(/.../) !== null }}` with `boolean/equals` + `rightValue: true` |
| Switch validation falls to fallback | Trap 55 (Switch not for validation) | Replace Switch with If node using boolean expression |
| SDK validation fail | Trap 1-2 (annotations/function decl) | Remove types, inline everything |
| Node created but empty params | Trap 24 (sourceCode) or Trap 37 (addNode) | Use `jsCode` not `sourceCode`; updateNodeParameters for DataTable |
| credentials not set | Trap 5 (auto-assign wrong) | Explicit `setNodeCredential` |
| Telegram not sending | Trap 26 (test mode) | Activate WF for production webhook |
| Connection wrong after update | Trap 27 (Switch shift) | Separate remove/add batches |
| DataTable 0 results | Trap 28 (no keyName) or Trap 30 (update not upsert) | Add keyName; use upsert |
| DataTable fields empty on canvas | Trap 41 (columns.value: {}) + Trap 46 (no data.keyValue) | Populate both, match schema to values |
| DataTable boolean warning | Trap 39 | String wrap: `"true"` |
| Add to cart overwrites previous items | Trap 50 (no read-before-write) | Insert Fetch Session between Add and Save; use append-or-increment code |
| /menu command gets 404 / editMessageText error | Trap 51 (wrong URL suffix) | Use `/sendMessage` for commands, `/editMessageText` for callbacks |
| Remove from cart shows empty/does nothing | Trap 52 (cross-branch node ref) | Add dedicated Fetch Session for Remove on the callback path |
| Postgres executeQuery has `INVALID_PARAMETER` warning about columns | Trap 53 (columns set on executeQuery) | `updateNodeParameters(node, {operation, query, options}, true)` without `columns` |
| Validator "expected object, got string" | Trap 7 (inlineKeyboard) | False positive — ignore |
| WF has fewer nodes than expected | Trap 38 (silent truncation) | Check nodeCount; addNode remaining |
| Telegram node lost resource/operation | Trap 44 (replace: true nuke) | Re-add resource/operation in replace payload |
| setNodeParameter on deep path silently ignored | Trap 19 (nesting bug) | Use `updateNodeParameters` + `replace: true` instead |
