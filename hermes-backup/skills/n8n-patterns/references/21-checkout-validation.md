# Telegram Checkout — Input Validation Pattern

> اعتبارسنجی ورودی کاربر در چک‌اوت بات‌های تلگرام
> Pattern key: `checkout_validation`

---

## ۱. معماری چک‌اوت Validation

پس از اینکه کاربر متن آزاد تایپ می‌کنه و State Router state مربوط به چک‌اوت رو تشخیص داد، جریان باید به این صورت باشه:

```
🔀 State Router
  │
  ├─ [0] checkout_name     → ✅ IF Name (validation)
  │                            ├─ [true]  → 💾 Save DataTable → 📞 Ask Phone
  │                            └─ [false] → ❌ Invalid Name (تلگرام)
  │
  ├─ [1] checkout_phone    → ✅ IF Phone (validation)
  │                            ├─ [true]  → 💾 Save DataTable → 🏠 Ask Address
  │                            └─ [false] → ❌ Invalid Phone
  │
  ├─ [2] checkout_address  → ✅ IF Address (validation)
  │                            ├─ [true]  → 💾 Save DataTable → 📮 Ask Postal
  │                            └─ [false] → ❌ Invalid Address
  │
  └─ [3] checkout_postal   → ✅ IF Postal (validation)
                               ├─ [true]  → 💾 Save DataTable → 📄 Order Summary
                               └─ [false] → ❌ Invalid Postal
```

> **قانون طلایی:** After DataTable save → Ask next question. نه برعکس (اول بپرس بعد ذخیره کن).

---

## ۲. نودهای مورد نیاز

| نود | نوع | تعداد | کاربرد |
|-----|-----|-------|--------|
| ✅ IF * | `if` | ۴ | validation هر فیلد (true=ادامه، false=خطا) |
| ❌ Invalid * | `telegram` (sendMessage) | ۴ | پیام خطا به کاربر |
| 💾 Save * | `dataTable` (update) | ۴ | ذخیره داده تو سشن |
| 📞 Ask * | `telegram` (sendMessage) | ۴ | سوال مرحله بعدی |

---

## ۳. الگوی **صحیح** If Node برای Validation

### 🚨 NEVER use these approaches:

❌ **Switch expression mode:** `${ $json.message.text.match(/^09\d{9}$/) ? 0 : 1 }` — Switch برای routing هست، validation کار نمی‌کنه چون Fallback output غیرقابل پیش‌بینی می‌شه.

❌ **If node with regexMatch operator:** `operator: { type: "string", operation: "regexMatch" }` روی مقدار `.match(/.../)` — این اپراتور غیرقابل اعتماد.

### ✅ درست: If node + boolean expression

| فیلد | leftValue | operator | rightValue |
|------|-----------|----------|------------|
| نام | `{{ ($json.message.text \|\| '').trim().length > 0 }}` | boolean / equals | `true` |
| شماره | `{{ ($json.message.text \|\| '').match(/^09\d{9}$/) !== null }}` | boolean / equals | `true` |
| آدرس | `{{ ($json.message.text \|\| '').trim().length > 0 }}` | boolean / equals | `true` |
| کد پستی | `{{ ($json.message.text \|\| '').match(/^\d{10}$/) !== null }}` | boolean / equals | `true` |

**پارامتر کامل If node برای شماره تماس:**

```json
{
  "conditions": {
    "combinator": "and",
    "conditions": [
      {
        "leftValue": "={{ ($json.message.text || '').match(/^09\\d{9}$/) !== null }}",
        "operator": {
          "type": "boolean",
          "operation": "equals"
        },
        "rightValue": true
      }
    ],
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict",
      "version": 2
    }
  },
  "options": {
    "ignoreCase": false,
    "looseTypeValidation": false
  }
}
```

**پارامتر کامل If node برای نام/آدرس (غیرخالی):**

```json
{
  "conditions": {
    "combinator": "and",
    "conditions": [
      {
        "leftValue": "={{ ($json.message.text || '').trim().length > 0 }}",
        "operator": {
          "type": "boolean",
          "operation": "equals"
        },
        "rightValue": true
      }
    ],
    "options": {
      "caseSensitive": true,
      "leftValue": "",
      "typeValidation": "strict",
      "version": 2
    }
  },
  "options": {
    "ignoreCase": false,
    "looseTypeValidation": false
  }
}
```

> **توضیح:** leftValue مستقیماً boolean تولید می‌کنه (true/false). operator آن رو با `rightValue: true` مقایسه می‌کنه. اگه true باشه → output 0 (ادامه)، false → output 1 (خطا).

---

## ۴. پیام‌های خطا (Telegram sendMessage)

| نود | chatId | text | resource |
|-----|--------|------|----------|
| ❌ Invalid Name | `={{ $json.chat_id }}` | ❌ نام و نام خانوادگی نامعتبر است. لطفاً نام خود را وارد کنید. | `message` |
| ❌ Invalid Phone | `={{ $json.chat_id }}` | ❌ فرمت شماره تماس نامعتبر است. لطفاً یک شماره ۱۱ رقمی با پیش‌شماره ۰۹ وارد کنید. | `message` |
| ❌ Invalid Address | `={{ $json.chat_id }}` | ❌ آدرس نامعتبر است. لطفاً آدرس خود را به درستی وارد کنید. | `message` |
| ❌ Invalid Postal | `={{ $json.chat_id }}` | ❌ کد پستی نامعتبر است. لطفاً یک کد پستی ۱۰ رقمی وارد کنید. | `message` |

> **resource discriminator:** برای `sendMessage` باید `"resource": "message"` باشه — اگه `"chat"` باشه خطا میده.

---

## ۵. Session Logging (`last_sent_at`)

برای رهگیری اینکه آخرین پیام کی به کاربر ارسال شده، یه ستون `last_sent_at` (string, ISO timestamp) به Data Table session اضافه کن و در همه Save nodeها مقدار `="{{ $now.toISO() }}"` بذار.

**نودهایی که نیاز به `last_sent_at` دارن:**
- Init Session (upsert اولیه)
- Set Checkout State (شروع چک‌اوت)
- Save Name → Phone
- Save Phone → Address
- Save Address → Postal
- Save Postal → Summary
- Set state: awaiting_payment

**⚠️ `setNodeParameter` برای nested path کار نمی‌کنه!**
از `setNodeParameter` با `path: "/parameters/columns/value/last_sent_at"` استفاده نکن — یه لایه اضافه `parameters.parameters` می‌سازه که n8n نادیده می‌گیره. همیشه از `updateNodeParameters` + `replace: true` استفاده کن.

---

## ۶. Telegram Node `resource` Discriminator

تمام نودهای Telegram که `sendMessage` یا `editMessageText` انجام می‌دن نیاز به discriminator دارن:

| عملیات | resource | operation |
|--------|----------|-----------|
| sendMessage | `message` | `sendMessage` |
| editMessageText | `message` | `editMessageText` |
| answerCallbackQuery | `callback` | `answerQuery` |

اگه missing باشه، UI node رو با warning باز می‌کنه ولی runtime ممکنه کار کنه. بهتره همیشه ست کنی.

---

## ۷. دستور `updateWorkflow` برای ساخت IF Validation

```json
// Add IF node for phone validation
{
  "type": "addNode",
  "node": {
    "name": "✅ IF Phone",
    "type": "n8n-nodes-base.if",
    "typeVersion": 2.3,
    "position": [224, 1264],
    "parameters": {
      "conditions": {
        "combinator": "and",
        "conditions": [{
          "leftValue": "={{ ($json.message.text || '').match(/^09\\d{9}$/) !== null }}",
          "operator": { "type": "boolean", "operation": "equals" },
          "rightValue": true
        }],
        "options": { "version": 2, "caseSensitive": true, "leftValue": "", "typeValidation": "strict" }
      },
      "options": { "ignoreCase": false, "looseTypeValidation": false }
    }
  }
}

// Re-wire: remove old connections first, add new ones
[
  { "type": "removeConnection", "source": "🔀 State Router", "sourceIndex": 1, "target": "💾 Save Phone → Address" },
  { "type": "addConnection", "source": "🔀 State Router", "sourceIndex": 1, "target": "✅ IF Phone" },
  { "type": "addConnection", "source": "✅ IF Phone", "sourceIndex": 0, "target": "💾 Save Phone → Address" },
  { "type": "addConnection", "source": "✅ IF Phone", "sourceIndex": 1, "target": "❌ Invalid Phone" }
]
```

> **ترتیب عملیات مهمه:** اول removeConnection، بعد addConnection. removeConnection برای ارتباطی که وجود نداره باعث FAIL کل batch میشه.

---

## ۸. Troubleshooting

| مشکل | علت | راه‌حل |
|------|-----|--------|
| If node خروجی ۱ (false) میده با اینکه ورودی درسته | regexMatch operator خرابه | به boolean expression تغییر بده |
| Switch خروجی fallback میده | Switch برای validation مناسب نیست | به If node تغییر بده |
| save node run میشه ولی ask node اجرا نمیشه | save node به چیزی وصل نیست | چک کن save node خروجی به ask داره |
| کاربر خطا می‌بینه و state رو می‌بازه | If بعد از State Router نیست | State Router باید مستقیم به If وصل باشه |
| Telegram node "Invalid value for resource" | resource="chat" برای sendMessage غلطه | به "message" تغییر بده |
