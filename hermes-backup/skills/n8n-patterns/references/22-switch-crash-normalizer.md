# Switch Node Crash & Code Node Normalizer Pattern

## مشکل

Switch node v3.4 (expression mode) با خطای داخلی کرش می‌کنه وقتی expression به جای عدد، `undefined` برگردونه:

```
NodeOperationError: Cannot read properties of undefined (reading 'push')
  at SwitchV3.node.ts:492
```

### چه وقتی اتفاق میفته

وقتی expression به فیلدی رفرنس بده که وجود نداره — مثلاً `$('⚡ Admin Entry').first().json.callback_query.data` وقتی ورودی `/admin` text message باشه:

```
Core Skeleton:
  /admin (text) → Execute Admin → Sub-workflow
    → Admin Entry output: { message: { text: "/admin", ... } }  ← callback_query نداره!
    → Admin Router: $('⚡ Admin Entry').first().json.callback_query.data
                   = undefined
                   → Switch crashes!
```

### تشخیص

```
execution → error → node: "🔀 Admin Router" (switch typeVersion 3.4)
message: "Cannot read properties of undefined (reading 'push')"
input data: { "value": "943724562" }  ← output نود PostgreSQL بعد از Gate
```

Switch internal code سعی می‌کنه نتیجه expression رو به `results[outputIndex]` push کنه — اگه expression `undefined` برگردونه، `results` خودش undefined میشه.

## رفع: Code node normalizer

به جای تلاش برای expression پیچیده با optional chaining، یه **Code node** قبل از Switch بذار که داده رو normalize کنه:

```
⚡ Admin Entry → 👤 Get Settings → 🔐 Admin Gate → ⚡ Normalize Input → 🔀 Admin Router
```

### ⚡ Normalize Input (Code node v2)

```javascript
var e = $('⚡ Admin Entry').first().json;
var d = (e.callback_query && e.callback_query.data) || (e.message && e.message.text) || '';
return [{ json: { ...e, route: d } }];
```

این همه فیلدهای اصلی Telegram رو حفظ می‌کنه و فقط `route` رو اضافه می‌کنه.

### 🔀 Admin Router (Switch — ساده و امن)

```
{{ $json.route == 'admin_dashboard' || $json.route == '/admin' ? 0 : $json.route == 'admin_orders' ? 1 : $json.route.startsWith('admin_order_confirm_') ? 2 : ... }}
```

Switch دیگه مستقیماً به `callback_query.data` رفرنس نمی‌ده — فقط `$json.route` رو می‌خونه.

### چرا بهتر از expression پیچیده؟

| روش | عیب |
|-----|-----|
| Optional chaining طولانی در Switch expression | `const/let` ساپورت نمیشه → تکرار بیش از حد → باگ احتمالی |
| Code node normalizer | یه بار بنویس، Switch ساده و امن بشه |

### قانون

> Switch node با بیش از ۵-۶ output + dual input (text + callback) → همیشه Code node normalizer بذار قبلش.

## نکته: setNodeParameter نمی‌تونه Switch output رو آپدیت کنه

اگه Switch node از قبل expression mode با ۱۶ output داره و می‌خوای expressionش رو عوض کنی:

- `setNodeParameter(path: "parameters/output")` → nested `parameters.parameters.output` می‌سازه ❌
- `updateNodeParameters` با parameters کامل → گاهی با "Expected object, received string" خطا میده ❌
- **راه‌حل:** Switch رو **حذف و دوباره بساز** (`removeNode` + `addNode` + `addConnection` × N) ✅

```
removeNode("🔀 Admin Router")
→ addNode({ name: "🔀 Admin Router", parameters: { mode: "expression", output: "NEW_EXPR" } })
→ addConnection("⚡ Normalize Input", "🔀 Admin Router")
→ addConnection("🔀 Admin Router", "📊 Dashboard Stats")  // × 11 output connections
```

### متوقف کننده‌های updateNodeParameters روی Switch

سه باگ شناخته‌شده جلوی بروزرسانی expression روی Switch می‌گیرن — اگه هر کدوم رو دیدی، **مستقیم برو removeNode + addNode**:

1. **`setNodeParameter(path: "parameters/output")`** → nested `parameters.parameters.output` می‌سازه ❌
2. **`updateNodeParameters` با عبارت طولانی** → `"Expected object, received string"` (JSON serialization fail) ❌
3. **عبارت حاوی `const/let`** → n8n expression parser ساپورت نمی‌کنه ❌

### قانون

> اگه Switch node با expression پیچیده خراب شد → حذف و بازسازی سریع‌تر و مطمئن‌تره. وقتت رو تلف expression fix نکن.

---

## مشکل ۳: expression حاوی single quote → MCP serialization failure

عبارت Switch expression اگه single quote داشته باشه (مثل `$json.route==='admin_dashboard'`)، MCP tool کل operations array رو string میفرسته:

```
❌ "Expected object, received string" at path operations[0]
```

این مشکل از "large operations" (#8 در 27-mcp-editing-pitfalls.md) جداست — حتی یه operation هم خراب میشه.

### رفع: Code node + numeric index pattern

**الگوی قطعی برای routing از طریق MCP:**

```
⚡ Normalize Input → 🔢 Route Index (Code) → 🔀 Admin Router (Switch expression)
```

**🔢 Route Index (Code node v2):**
```javascript
const route = $json.route || '';
let idx = 16; // fallback
if (route === 'admin_dashboard') idx = 0;
else if (route === 'admin_orders') idx = 1;
else if (route.startsWith('admin_order_confirm_')) idx = 2;
else if (route.startsWith('admin_order_reject_')) idx = 3;
// ... ادامه conditions
return [{ json: { ...$json, routeIndex: idx } }];
```

**🔀 Admin Router (Switch expression mode):**
```jsonc
{
  "mode": "expression",
  "numberOutputs": 17,
  "options": { "fallbackOutput": "extra" },
  "output": "={{ $json.routeIndex }}"
}
```

### چرا این بهترین الگو هست

| مشکل | Code node + expression | Switch inline |
|------|----------------------|---------------|
| single quote serialization | ✅ JS syntax در Code node کار میکنه | ❌ MCP خراب میکنه |
| rules.key mismatch | ✅ اصلاً rules استفاده نمیکنه | ⚠️ rules.rules vs rules.values |
| undefined crash | ✅ fallback مقدار داره | ❌ expression undefined → کرش |
| MCP batch size | ✅ expression کوتاه و ساده | ❌ expression طولانی serialization fail |
| test mode | ✅ کار میکنه | ✅ expression mode کار میکنه |

### قانون

> Switch routing از طریق MCP → همیشه Code node عددی حساب کنه + Switch expression mode با `{{ $json.routeIndex }}`.

---

## مشکل ۴: Set node `$json` context در sub-workflow

در sub-workflow، `$json` در Set node `jsonOutput` به INPUT نود قبلی اشاره میکنه (مثلاً `{"value": "943724562"}` از PostgreSQL Gate)، نه به داده اصلی Telegram:

```
❌ $json.message.text  → undefined (چون $json فقط "value" داره)
✅ $('⚡ Admin Entry').first().json.message.text  → "/admin"
```

**ولی** `$('⚡ Admin Entry').first().json` حاوی single quote هست → MCP serialization fail!

**رفع:** از Code node استفاده کن (نه Set node):
```javascript
const e = $('⚡ Admin Entry').first().json;
const route = e.callback_query ? e.callback_query.data
  : (e.message && e.message.text === '/admin' ? 'admin_dashboard'
  : e.message ? e.message.text : '');
return [{ json: { ...$json, route } }];
```

---

## مشکل ۲: addConnection بدون sourceIndex — همه نودها روی output 0

وقتی Switch node دارای چند output هست و با `addConnection` وصلش میکنی، اگه `sourceIndex` مشخص نکنی، **همه نودها روی output 0 وصل میشن**:

```
// ❌ اشتباه — همه روی output 0
addConnection("🔀 Router", "📊 Dashboard")    // → output 0
addConnection("🔀 Router", "📦 Products")     // → output 0
addConnection("🔀 Router", "👤 Users")        // → output 0

// نتیجه: هر سه نود همزمان اجرا میشن!
```

### عیب

وقتی `/admin` (text message) ارسال میشه:
- Switch output 0 → Dashboard ✅
- ولی output 0 همچنین → Extract Order ID ← کرش! چون `callback_query.data` وجود نداره

### رفع

```jsonc
// ✅ درست — هر نود روی output خودش
{"type": "addConnection", "source": "🔀 Router", "sourceIndex": 0, "target": "📊 Dashboard"},
{"type": "addConnection", "source": "🔀 Router", "sourceIndex": 1, "target": "📦 Products"},
{"type": "addConnection", "source": "🔀 Router", "sourceIndex": 2, "target": "👤 Users"},
```

### قانون

> Switch node → همیشه `sourceIndex` مشخص کن. بدون اون، همه اتصالات روی output 0 میرن.
