# Telegram Router Reference for n8n

> معماری مسیریابی و session management برای بات‌های تلگرام
> برای توسعه‌دهنده n8n — نه راهنمای راه‌اندازی

---

## ۱. ۴ نود

| نود | نوع | کاربرد |
|-----|-----|--------|
| `telegramTrigger` | Trigger | دریافت پیام، کامند، voice، photo، callback |
| `telegram` | Action | ارسال پیام، عکس، فایل، rich message، keyboard |
| `telegramTool` | Tool | برای AI Agent |
| `telegramHitlTool` | Tool | Human-in-the-Loop |

### Credential

```
Credentials → New → Telegram API
  Access Token: 7234567890:AAHdqTcvCH1vGWJxfSeofS
```

---

## ۲. خروجی Trigger (simplify: false)

| پارامتر | توضیح |
|---------|-------|
| `triggerOn` | چه نوع updateهایی دریافت کنه — message, callback_query, etc. |
| `simplifyOutput` | خروجی رو ساده‌سازی کنه یا raw JSON بده |
| `expression` | شرط اضافی برای فیلتر کردن (اختیاری) |

### خروجی Trigger:

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 42,
    "from": { "id": 12345, "is_bot": false, "first_name": "Ali" },
    "chat": { "id": -1001234567890, "type": "supergroup", "title": "My Group" },
    "text": "سلام",
    "date": 1700000000
  }
}
```

> CDP: اگه `simplify: false` باشه، callback_query و channel_post هم توی update میان

### فیلدهای مهم خروجی:

```
متن پیام:     {{ $json.message.text }}
چت آیدی:     {{ $json.message.chat.id }}
یوزر آیدی:   {{ $json.message.from.id }}
اسم کاربر:   {{ $json.message.from.first_name }}
یوزرنیم:     {{ $json.message.from.username }}
فایل صوتی:   {{ $json.message.voice.file_id }}
فایل تصویری: {{ $json.message.photo[-1].file_id }}
دکمه فشده:   {{ $json.callback_query.data }}
```

---

## ۳. Action — پارامترهای کلیدی

### sendMessage

| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `chatId` | ✅ | آیدی چت (`-100...` برای supergroup) |
| `text` | ✅ | متن پیام |
| `replyMarkup` | خیر | inlineKeyboard / forceReply |
| `additionalFields.parse_mode` | خیر | `HTML` (ترجیح) یا `MarkdownV2` |
| `additionalFields.reply_to_message_id` | خیر | ریپلای به پیام |
| `additionalFields.message_thread_id` | خیر | ارسال به topic خاص |
| `additionalFields.disable_notification` | خیر | بی‌صدا ارسال کنه |
| `additionalFields.appendAttribution` | خیر | **پیش‌فرض: true** — عبارت "This message was sent automatically with n8n" رو اضافه میکنه. برای بات‌های حرفه‌ای `false` بذار |

### sendPhoto / sendDocument

```
photo/document: { "__rl": true, "mode": "binary"|"url", "value": binaryRef|URL }
caption: string
```

### sendMediaGroup (آلبوم)

```
media: { "media": [{ "type": "photo"|"video", "media": {...}, "caption": "" }] }
```

### sendRichMessage (اگه n8n >= 1.0)

```
richMessage: {
  blocks: [
    { type: "header"|"text"|"list"|"footer", text: "" },
    { type: "list", elements: [{ type: "listItem", content: "" }] }
  ]
}
```

### sendAndWait

بعد از ارسال، output دوم trigger-like هست با `message.text` حاوی پاسخ کاربر.

### answerCallbackQuery

بعد از callback **الزامی** — وگرنه UI قفل می‌شه:

```
callbackQueryId: {{ $json.callback_query.id }}
```

---

## ۴. Inline Keyboard

```typescript
replyMarkup: "inlineKeyboard",
inlineKeyboard: {
  rows: [{ row: { buttons: [
    { text: "✅ تایید", additionalFields: { callback_data: "approve" } },
    { text: "🌐 سایت", additionalFields: { url: "https://..." } },
    { text: "📱 اشتراک", additionalFields: { request_contact: true } }
  ]}}]
}
```

> محدودیت: ۸ دکمه/ردیف، ۱۰۰ دکمه/کیبورد، callback_data حداکثر ۶۴ بایت

---

## ۵. استفاده از Tool / HITL در AI Agent

```typescript
// telegramTool — خود Agent تصمیم می‌گیره کی بفرسته
{ name: "telegramTool", operation: "sendMessage", chatId: "-1001234567890" }

// telegramHitlTool — منتظر تأیید انسانی می‌مونه
{ name: "telegramHitlTool", operation: "sendMessage" }
```

---

## ⭐ معماری اصلی: مسیریاب هوشمند (۴ مسیر پایه)

> مبنای هر بات تلگرامی — جدا کردن مسیرها از همون ابتدا برای سرعت و مقیاس‌پذیری

### تشخیص مسیر با Switch (بدون کد)

```
[Telegram Trigger]
    ↓
[Switch: تشخیص نوع update]
    ┌──────────────────────────────────────────────────────┐
    │ Routing Rules (expression mode):                     │
    │                                                      │
    │  callback → {{ $json.callback_query !== undefined }} │
    │  file     → {{ $json.message.photo                  │
    │               || $json.message.document              │
    │               || $json.message.voice                 │
    │               || $json.message.audio                 │
    │               || $json.message.video                 │
    │               || $json.message.animation !== undefined }} │
    │  command  → {{ $json.message.text                    │
    │               && $json.message.text.startsWith('/') }}    │
    │  text     → {{ $json.message.text                    │
    │               && !$json.message.text.startsWith('/') }}   │
    │  unknown  → (fallback)                               │
    └──────────────────────────────────────────────────────┘
    │
    ├── callback ──→ [مسیر Callback]
    ├── file     ──→ [مسیر File/Media]
    ├── command  ──→ [مسیر Commands]
    ├── text     ──→ [مسیر Free Text + Session Check]
    └── unknown  ──→ [NoOp / Nothing]
```

### توضیح правила:

| مسیر | Expression |
|------|-----------|
| `callback` | `{{ $json.callback_query !== undefined }}` |
| `file` | `{{ $json.message.photo \|\| $json.message.document \|\| $json.message.voice \|\| $json.message.audio \|\| $json.message.video \|\| $json.message.animation !== undefined }}` |
| `command` | `{{ $json.message.text && $json.message.text.startsWith('/') }}` |
| `text` | `{{ $json.message.text && !$json.message.text.startsWith('/') }}` |

> **ترتیب outputs مهمه:** Switch اولین rule که true باشه رو می‌گیره. اول callback رو بذار، بعد file، بعد command، بعد text.

### نکته: استخراج fileId و fileType

هنوز برای مسیر file نیاز به یه Code node داری (چون Switch فقط route می‌کنه، transform نمی‌کنه):

```
[Switch: route → file]
    ↓
[Code: استخراج fileId و fileType از message]
    const msg = $input.first().json.message;
    let fileType = 'photo';
    if (msg.document) fileType = 'document';
    else if (msg.voice) fileType = 'voice';
    else if (msg.audio) fileType = 'audio';
    else if (msg.video) fileType = 'video';

    return [{
      json: {
        fileType,
        fileId: (msg.photo?.[msg.photo.length-1]?.file_id)
                || msg.document?.file_id || msg.voice?.file_id
                || msg.audio?.file_id || msg.video?.file_id,
        caption: msg.caption || '',
        mimeType: msg.document?.mime_type,
      }
    }];
```

(اگر `fileId` در خروجی تریگر موجود است و نیازی به استخراج نیست، می‌توان از `$json.message.voice.file_id` مستقیماً استفاده کرد — بخش فایل همین توضیح را ببینید.)

### نمودار مسیریابی:

```
                 Telegram Trigger
                       │
                       ▼
             ┌─── Switch: Route Rules ────┐
             │                            │
     ┌───────┴────────┬──────────┬─────────┴───────┬─────────┐
     ▼              ▼          ▼                   ▼         ▼
  callback       file      command             text      unknown
     │             │          │                   │         │
     ▼             ▼          ▼                   ▼         ▼
  answerQuery   Code:      Switch:           Session      NoOp
  + process    extract    /start,/help,       Check
               fileId     /settings,...    ┌──┴──┐
                                          new   existing
                                           │      │
                                           ▼      ▼
                                        Welcome  AI/Logic
                                        + set     + process
                                        session
```

---

## ۶. مسیر ۱: Callback Query

**ورودی:** Switch output → callback

```
[Switch: route → callback]
    ↓
[Switch: callback_query.data]
    ├── "approve" → [پردازش] → [Telegram: editMessageText / sendMessage]
    ├── "reject"  → [پردازش] → [Telegram: editMessageText / sendMessage]
    ├── "page_2"   → [دیتا بعدی] → [Telegram: editMessageText با دکمه‌های جدید]
    └── default    → [Telegram: sendMessage "دستور نامعتبر"]
```

> **نیازی به `answerCallbackQuery` نیست.** پردازش زیر ۱ ثانیه ست — کاربر دکمه رو می‌زنه، مستقیم editMessageText می‌گیره. اگه پردازش طولانی‌تر بود (چند ثانیه)، اون وقت تنها جایی که بهش نیازه.

---

## ۷. مسیر ۲: File / Media

**ورودی:** `$json.route === 'file'`

```
[Switch: route]
    file:
    ↓
[Telegram: getFile]
    fileId: {{ $json.fileId }}
    ↓
[HTTP: GET file از Telegram]
    url: https://api.telegram.org/file/bot<TOKEN>/{{ $json.result.file_path }}
    responseFormat: file
    ↓
[Switch: fileType]
    ├── voice   → [Whisper / OpenAI TTS: تبدیل به متن]
    ├── photo  → [Vision AI / OCR: استخراج محتوا]
    ├── document → [Extract From File: استخراج متن]
    ├── video  → [دانلود مستقیم / تبدیل]
    └── audio  → [ذخیره / پردازش]
    ↓
[Telegram: sendMessage — نتیجه]
```

از ورک‌فلو واقعی `a95128f7` (۳۷ نود):

```
[Switch: route]
    file:
    ↓
[IF: voice?]
    ├── yes → [HTTP: download from Telegram]
    │          ↓
    │         [OpenAI: Whisper transcription]
    │          ↓
    │         [Merge: متن تبدیل‌شده با بقیه دیتا]
    └── no → [ادامه مستقیم]
    ↓
[ادامه پردازش معمول...]
```

---

## ۸. مسیر ۳: Commands (/...)

**ورودی:** `$json.route === 'command'`

```
[Switch: route]
    command:
    ↓
[Switch: command]
    ├── "/start"   → [Telegram: خوش‌آمدگویی + توضیحات]
    │                  ↓
    │                [PostgreSQL / DataTable: ایجاد session جدید]
    │                  status: "welcome"
    │
    ├── "/help"    → [Telegram: ارسال متن راهنما]
    │
    ├── "/settings" → [Telegram: دکمه‌های تنظیمات]
    │
    ├── "/status"  → [DataTable: آمار] → [Telegram: گزارش]
    │
    ├── "/end"     → [PostgreSQL: بستن session]
    │                  status: "closed"
    │                  ↓
    │                [Telegram: "جلسه پایان یافت"]
    │
    └── unknown    → [Telegram: "دستور نامعتبر. /help"]
```

> کامندهای مختص هر بات رو توی array توی Code node تعریف کن:
> `const COMMANDS = ['start', 'help', 'settings', 'status', 'end'];`

از ورک‌فلو واقعی (`35cc9b6e` — 52 نود):

```
[Switch: command]
    ├── "/start"        → [PostgreSQL: CREATE session + خوشامد]
    ├── "/billing"      → [PostgreSQL: UPDATE department=billing] → [Telegram: "شما به بخش صورتحساب متصل شدید"]
    ├── "/ReturnPolicy" → [PostgreSQL: UPDATE department=returns] → [Telegram: "شما به بخش مرجوعی متصل شدید"]
    ├── "/TechSupport"  → [PostgreSQL: UPDATE department=tech] → [Telegram: "شما به بخش پشتیبانی فنی متصل شدید"]
    ├── "/end"          → [PostgreSQL: UPDATE status=inactive] → [Telegram: "جلسه پایان یافت"]
    └── default         → [Telegram: sendMessage "دستور نامعتبر. از /start برای راهنما استفاده کنید"]
```

---

## ۹. مسیر ۴: Free Text + Session Management ⭐

**مهم‌ترین مسیر — اینجاست که Session میاد توی کار**

### ۹.۱ چک Session

```
[Switch: route]
    text:
    ↓
[PostgreSQL / DataTable: get session کاربر]
    ┌─────────────────────────────┐
    │ SELECT * FROM sessions      │
    │ WHERE user_id = {{ $json.from.id }}  │
    │   AND status != 'closed'    │
    │ ORDER BY updated_at DESC    │
    │ LIMIT 1                     │
    └─────────────────────────────┘
    ↓
[IF: session exists?]
    ├── yes → [ادامه با session قبلی]
    └── no  → [Telegram: خوشامد] → [PostgreSQL: CREATE new session]
```

### ۹.۲ State Machine Session

هر session یه `state` داره که مشخص می‌کنه کاربر تو چه مرحله‌ایه:

| State | معنی | چه پیامی قبوله |
|-------|------|---------------|
| `welcome` | تازه اومده | دستور /start یا انتخاب دپارتمان |
| `awaiting_input` | منتظر ورودی | متن آزاد |
| `awaiting_confirm` | توی تأیید | بله/خیر (callback) |
| `processing` | در حال پردازش | هیچی (بی‌صدا) |
| `closed` | جلسه بسته | فقط /start |

### ۹.۳ مثال کامل Session + Routing

از ورک‌فلو واقعی (`35cc9b6e`):

```
[Telegram Trigger]
    ↓
[Code: Route Detector — مشخص کن route چیه]
    ↓
[Switch: route]
    │
    ├── callback →
    │   [Telegram: answerCallbackQuery]
    │   [Switch: data] → پردازش
    │
    ├── command →
    │   [Switch: command]
    │   ├── /start → [PostgreSQL: INSERT OR UPDATE session]
    │   │            │  user_id={{ from.id }}, status='welcome'
    │   │            [Telegram: "سلام! لطفاً دپارتمان خود را انتخاب کنید:" + inlineKeyboard]
    │   ├── /billing / /ReturnPolicy / /TechSupport →
    │   │            [PostgreSQL: UPDATE session SET department=X, state='awaiting_input']
    │   │            [Telegram: "متصل شدید. سوال خود را بپرسید"]
    │   └── /end →  [PostgreSQL: UPDATE session SET status='closed']
    │                [Telegram: "جلسه پایان یافت"]
    │
    └── text →
        [PostgreSQL: get session by user_id]
        [IF: state是什么؟]
        ├── 'awaiting_input' →
        │     [AI Agent: پردازش سوال با context دپارتمان]
        │     [Telegram: sendMessage]
        │     [PostgreSQL: log message]
        ├── 'awaiting_confirm' →
        │     [IF: text === 'بله'?]
        │     │  ├── yes → [PostgreSQL: UPDATE state='awaiting_input']
        │     │  └── no  → [Telegram: "درخواست لغو شد"] + [PostgreSQL: UPDATE state='awaiting_input']
        │     └── default → [Telegram: "لطفاً بله یا خیر پاسخ دهید"]
        └── 'welcome' →
              [Telegram: "ابتدا دپارتمان را انتخاب کنید: /billing /ReturnPolicy /TechSupport"]
```

---

## ۱۰. Session Storage Options

| Storage | مزیت | عیب |
|---------|------|-----|
| **DataTable** | بدون وابستگی خارجی | query محدود |
| **PostgreSQL** | query قدرتمند + join | نیاز به DB |
| **Redis** | سریع، TTL | داده موقته |
| **Memory Buffer** (AI Agent) | فقط برای chatbot | session محدود |

### نمونه DataTable:

```sql
-- ساختار جدول sessions:
user_id:    number (PK)
chat_id:    number
department: string (billing/tech/returns)
state:      string (welcome/awaiting_input/awaiting_confirm/processing/closed)
context:    string (آخرین context برای AI)
created_at: datetime
updated_at: datetime
```

---

## ۱۱. پترن ۶: Message Debouncing (Anti-Spam)

از ورک‌فلو واقعی (`a02b4296` — 24 نود):

```
[Telegram Trigger]
    ↓
[PostgreSQL: چک session فعال]
    │  SELECT * FROM sessions WHERE status IN ('LISTENING','AGGREGATING')
    ↓
[IF: session exists?]
    ├── no  → [PostgreSQL: INSERT session با status='LISTENING', wait_until=now+60s]
    │          ↓
    │         [Wait: 60 ثانیه — جمع‌آوری پیام‌های بعدی]
    │          ↓
    │         [PostgreSQL: GET همه پیام‌های این تایم‌ویندو]
    │          ↓
    │         [AI Agent: پاسخ جامع به همه پیام‌ها]
    │          ↓
    │         [Telegram: sendMessage]
    │          ↓
    │         [PostgreSQL: UPDATE status='COMPLETED']
    │
    └── yes → [PostgreSQL: APPEND message + UPDATE status='AGGREGATING']
               [پایان — منتظر تایم‌اوت]
```

> کاربر ۴ تا پیام پشت سر هم می‌فرسته → همه جمع میشن → یه پاسخ جامع می‌گیره.
> به جای AI agent ۴ بار صدا زدن، ۱ بار.

### format

با `parse_mode: HTML`:
```
<b>بولد</b>  <i>ایتالیک</i>  <code>کد</code>  <pre>کدبلاک</pre>
<a href="url">لینک</a>  <s>خط خورده</s>  برای 4096+ کاراکتر split بزن
```

---

## ۱۲. چک‌اوت: نمایش پیام تأیید پرداخت

### ❌ اشتباه رایج: `$json` در editMessageText

```typescript
// ❌ نادرست — $json فقط دیتای نود قبلی رو داره
text: "={{ '✅ سفارش شما با کد ' + $json.order_code + ' ثبت شد.' +
        '💰 مبلغ: ' + Number($json.total).toLocaleString('fa-IR') + ' تومان' +
        '💳 شماره کارت: ' + $json.card_number }}"
```

`💳 Show Payment Confirm` که از `editMessageText` استفاده می‌کنه، نود قبلیش `💳 Get Card Number` هست با خروجی `{value: "6037-..."}` — پس `$json` فقط `value` رو داره. `order_code`، `total`، `card_number` همه `undefined` → خروجی `کد undefined` و `مبلغ ناعدد`.

**رفع:** همیشه با `$('NodeName').first().json.fieldName` رفرنس بده:

```typescript
// ✅ درست
text: "={{ '✅ سفارش شما با کد ' + $('📦 Build Order Data').first().json.order_code +
        ' ثبت شد.\n💰 مبلغ: ' + Number($('📦 Build Order Data').first().json.total).toLocaleString('fa-IR') + ' تومان' +
        '\n💳 شماره کارت: ' + $('💳 Get Card Number').first().json.value }}"
```

### قانون سرانگشتی `$json`:

| موقعیت | `$json` کار می‌کنه؟ | جایگزین |
|--------|-------------------|---------|
| نود قبلی مستقیم (۱ قدم فاصله) | ✅ بله | `$json.field` |
| ۲+ قدم فاصله (چند نود قبل) | ❌ نه → `undefined` | `$('Node').first().json.field` |
| نود قبلی یه شاخه موازی | ❌ نه | `$('Node').first().json.field` |

---

## ۱۳. Cascade Effect: ارور `$json` → callback_data `undefined` → NaN در دیتابیس

### زنجیره فاجعه

این یه زنجیره‌ست که از یه `$json` اشتباه شروع می‌شه و به ارور دیتابیس ختم می‌شه:

```
📩 Forward Receipt to Admin (caption از $json → undefined)
  ↓ (پیام با caption=undefined و callback_data=admin_ap_undefined)
کاربر روی دکمه کلیک می‌کنه ← callback_data="admin_ap_undefined"
  ↓
🔍 Fetch Order for Approve: parseInt($json.callback_query.data.split('_').pop())
  → parseInt("undefined") = NaN
  ↓
PostgreSQL: WHERE id = NaN → "invalid input syntax for type integer: NaN"
```

**رفع سطح اول:** caption و callback_data از `$('Node').first().json.field` درست بشن تا پیام درست بره.  
**رفع سطح دوم:** callback data extraction نباید به `.pop()` (آخرین تیکه) متکی باشه چون اگه `undefined` توی بقیه callback_data باشه، NaN می‌گیره.

### الگوی درست استخراج order_id از callback_data

```typescript
// ❌ ناپایدار — به آخرین segment بعد از _ متکیه
parseInt($json.callback_query.data.split('_').pop())

// ✅ پایدارتر — prefix رو حذف می‌کنه
parseInt($json.callback_query.data.replace('admin_ap_', ''))
parseInt($json.callback_query.data.replace('admin_rj_', ''))
```

> `.replace()` هم کامل نیست. اگه یه `undefined` توی callback_data باشه (نشت از یه فیلد upstream)، `"admin_rj_undefined".replace('admin_rj_','')` = `"undefined"` و `parseInt("undefined")` = `NaN`.

**✅ مقاوم‌ترین روش:** با رجکس فقط عدد رو بگیر، اگه نبود ۰ برگردون:

```typescript
// ✅ مقاوم در برابر هر گونه undefined در callback_data
(callback_query.data.match(/\d+/) || ['0'])[0]
// → "admin_rj_14".match(/\d+/) = ["14"] → 14
// → "admin_rj_undefined".match(/\d+/) = ["0"] → 0 (NaN نمی‌ده)
```

از این الگو توی `queryReplacement` نودهای Postgres استفاده کن:

```typescript
queryReplacement: "={{ (($json.callback_query.data.match(/\\d+/) || ['0'])[0]) }}">
```

### چه موقع از کدوم استفاده کنیم؟

| روش | مناسب | ریسک |
|-----|-------|------|
| `.split('_').pop()` | callback_data قطعاً فقط عدد داره | اگه `undefined` نشت کنه → NaN |
| `.replace('prefix_', '')` | callback_data prefix مشخص داره | اگه خود `undefined` توی دیتا باشه → NaN |
| `.match(/\d+/)` | همیشه | هیچی — ۰ fallback داره |

---

## ۱۴. پترن: فوروارد فیش به ادمین (sendPhoto با کپشن داینامیک)

### معماری

```
🔍 Get Pending Order (subquery: items_summary)
  ↓
🔍 Get Admin for Photo (SELECT value FROM settings WHERE key = 'admin_telegram_id')
  ↓
📝 Build Receipt Caption (Set node: order_code, shipping_name, total, items_text)
  ↓
📦 Set Status: Awaiting Approval (UPDATE orders SET status='awaiting_approval')
  ↓
📩 Forward Receipt to Admin (sendPhoto + caption)
```

### نکات کلیدی

**۱. chatId:** از `🔍 Get Admin for Photo` میاد — توی settings دیتابیس ذخیره شده.

**۲. caption:** از `📝 Build Receipt Caption` رفرنس بگیر — **نه** از `$json`:
```
$('📝 Build Receipt Caption').first().json.order_code
$('📝 Build Receipt Caption').first().json.shipping_name
$('📝 Build Receipt Caption').first().json.items_text
```

**۳. callback_data دکمه‌ها:** همون رفرنس رو برای order_id استفاده کن:
```
callback_data: {{ 'admin_ap_' + $('📝 Build Receipt Caption').first().json.order_id }}
```

**۴. چرا `📝 Build Receipt Caption`؟** چون همه فیلدهای مورد نیاز رو یه جا داره: order_code، shipping_name، total، items_text — و همچنین order_id که واسه callback_data لازمه.

### چه کسی پیام رو می‌بینه؟ (chatId رو اشتباه نگیر)

| نود | chatId = ? | نکته |
|-----|-----------|------|
| `💳 Show Payment Confirm` | `$('📱 Telegram Trigger').first().json.callback_query.message.chat.id` | کاربری که چک‌اوت کرده |
| `📩 Forward Receipt to Admin` | `$('🔍 Get Admin for Photo').first().json.value` | ادمین (از settings) |

---

## ۱۵. Fork-Join Antipattern: دوتایی اجرا شدن نودها

### مشکل
وقتی دو شاخه موازی به یه نود Join بشن (هر دو output به یه نود وصل شن)، اون نود **به تعداد ورودی‌هاش اجرا می‌شه**:

```
🔍 Get Pending Order
  ├── 🔍 Get Admin ──────→ 📝 Build Receipt Caption ←── اجرا #1
  └── 🔍 Get Items ──→ 📊 Aggregate ──→ 📝 Build Receipt Caption ←── اجرا #2
```

نتیجه: `📝 Build Receipt Caption` دو بار اجرا میشه → `📦 Set Status` و `📩 Forward` و بقیه downstream هم دو بار.

### تشخیص
توی execution log ببین اگه یه نود دو بار با `executionIndex` مختلف ظاهر شده ولی source از نودهای مختلف داره → fork-join داری.

### رفع (دو راه)

**۱. حذف مسیر اضافه (ترجیحی):**
اگه دیتای یک شاخه کافیه (مثلاً `🔍 Get Pending Order` خودش `items_summary` داره)، کانکشن شاخه دوم رو از `📝 Build Receipt Caption` قطع کن.

**۲. Merge کردن دیتا قبل از join:**
اگه به دیتای هر دو شاخه نیاز داری، اول با Merge/Set هر دو رو ترکیب کن، بعد بده به نود بعدی.

---

## ۱۵. Draft ≠ Active: Publish رو فراموش نکن

### مشکل
وقتی `update_workflow` پارامترهای یه نود رو تغییر میده، تغییرات فقط توی **draft** ورک‌فلو اعمال می‌شه. اگه workflow **active** باشه (منتشرشده)، production/webhook executions از **active version** استفاده می‌کنن — نه draft.

### تشخیص
توی `get_workflow_details` این دو فیلد رو مقایسه کن:
```json
{
  "versionId": "5de596aa-9c3d-438e-be80-4a2e8358382e",       // draft (آخرین ویرایش)
  "activeVersionId": "0c598bdc-c4f2-453b-a6ab-f83e3112a072"  // active (منتشرشده)
}
```
اگه فرق دارن → تولید از نسخه قدیمی استفاده می‌کنه.

### رفع
بعد از هر `update_workflow` که فیکس می‌زنی، فوراً publish کن:
```bash
mcp_n8n_mcp_publish_workflow(workflowId="...")
```

### قانون
**بعد از هر `setNodeParameter` که مشکل لاگیک رو فیکس می‌کنه → publish کن.** تغییرات credential-independent publish امن هستن.

---

## ۱۶. editMessageText روی پیام عکس: "there is no text in the message to edit"

### مشکل

پیام‌های عکس/فیلم/voice در تلگرام `text` ندارن — فقط `caption` دارن. API `editMessageText` نمی‌تونه روی پیام عکس کار کنه:

```
Bad Request: there is no text in the message to edit (HTTP 400)
```

این اتفاق می‌افته وقتی کاربر روی inline keyboardِ **زیر یه عکس** کلیک می‌کنه (مثلاً دکمه تأیید/رد زیر فیش واریزی) و نود downstream با `editMessageText` سعی می‌کنه محتواش رو عوض کنه.

### رفع

از `sendMessage` به جای `editMessageText` استفاده کن — یه پیام جدید می‌فرسته به جای ادیت پیام عکس:

| Operation | کاربرد | محدودیت |
|-----------|--------|---------|
| `editMessageText` | ادیت پیام متنی | ❌ روی عکس/voice کار نمی‌کنه |
| `sendMessage` | ارسال پیام جدید | ✅ همیشه کار می‌کنه |

### نودهایی که معمولاً روی callback پیام عکس اجرا می‌شن

این نودها معمولاً توی مسیر callback_admin هستن و باید `sendMessage` باشن، **نه** `editMessageText`:

```
📝 Confirm Approve Prompt    (بعد از کلیک روی ✅ تأیید زیر عکس فیش)
📝 Ask Reject Comment         (بعد از کلیک روی ❌ رد زیر عکس فیش)
```

### تشخیص

توی execution log:
```
"description": "Bad Request: there is no text in the message to edit",
"node": { "name": "📝 Confirm Approve Prompt", "operation": "editMessageText" },
"message": "400 - Bad Request: there is no text in the message to edit"
```

اگر `message` توی trigger `photo` داره و نود error دار روی `editMessageText` ست → عوضش کن به `sendMessage`.

---

## ۱۷. ExpressionExtensionError: $() در inlineKeyboard additionalFields

### مشکل

وقتی عبارت expression شامل `$('NodeName').first().json.field` داخل `additionalFields.callback_data` در `inlineKeyboard` باشه، n8n expression parser ممکنه `ExpressionExtensionError: invalid syntax` بده — حتی اگه syntax ظاهراً درست باشه.

```
Error: ExpressionExtensionError: invalid syntax
  at extendSyntax (expression-extension.ts:609)
  context: { parameter: "inlineKeyboard" }
```

### نمونه خطا (از execution واقعی — coffee bot)

```typescript
// ❌ خطادار — expression پیچیده داخل additionalFields.callback_data
inlineKeyboard: {
  rows: [{ row: { buttons: [
    { text: "بله، تأیید",
      additionalFields: {
        callback_data: "={{ 'admin_ap_yes_' + $('🔍 Fetch Order for Approve').first().json.id }"
      }}
  ]}}]
}
```

### رفع

**گزینه ۱ (ترجیحی):** مقدار callback_data رو از یه Set node قبلی بیار:

```
[🔍 Fetch Order for Approve] → [📝 Build Confirm Buttons (Set node)]
  → callback_data_ap: "admin_ap_yes_{{ $json.id }}"
  → callback_data_rj: "admin_rj_yes_{{ $json.id }}"
→ [📝 Confirm Approve Prompt (Telegram)]
  → additionalFields.callback_data: "={{ $('📝 Build Confirm Buttons').first().json.callback_data_ap }}"
```

**گزینه ۲:** از `$json` ساده استفاده کن اگه نود قبلی مستقیماً فیلدها رو داره:

```typescript
callback_data: "={{ 'admin_ap_yes_' + $json.id }}"
```

### قانون
> عبارت‌های پیچیده با `$('...')` رو **هرگز** داخل `additionalFields` توی inlineKeyboard قرار نده.
> اول با یه Set/Code node مقدار نهایی رو بساز، بعد توی Telegram node فقط رفرنس بده.

---

## ۱۸. Sub-workflow `$json` Replacement: Execute Workflow Trigger

### مشکل

در ساب‌ورک‌فلوها با `Execute Workflow Trigger` (inputSource: passthrough)، داده اصلی Telegram از ورک‌فلوی والد وارد میشه. ولی **اولین نود پردازشی** (مثلاً PostgreSQL) `$json` رو با خروجی خودش جایگزین می‌کنه:

```
⚡ Execute Workflow Trigger  →  $json = {callback_query: {from: {id: 123}, ...}}
  ↓
👤 Get Admin Settings (PostgreSQL)  →  $json = {value: "123456789"}  ← داده Telegram از بین رفت!
  ↓
🔀 Admin Router  →  $json.callback_query.data = undefined  ← خطا!
  ↓
📝 Show Dashboard  →  $json.message.chat.id = undefined  ← ارور Telegram API!
```

**تفاوت با مشکل تک‌ورک‌فلویی (بخش ۱۲):** در تک‌ورک‌فلو، فقط نودهای ۲+ قدم فاصله مشکل دارن. در ساب‌ورک‌فلو، **همه نودهای بعد از اولین نود پردازشی** خراب میشن — حتی نود مجاور.

### رفع

**همه نودها** باید به جای `$json` از `$('⚡ Execute Workflow Trigger').first().json` استفاده کنن:

```typescript
// ❌ خطا — $json بعد از PostgreSQL فقط {value: "..."} داره
$json.callback_query.data
$json.message.chat.id

// ✅ درست — رفرنس مستقیم به trigger
$('⚡ Execute Workflow Trigger').first().json.callback_query.data
$('⚡ Execute Workflow Trigger').first().json.callback_query.message.chat.id
$('⚡ Execute Workflow Trigger').first().json.callback_query.message.message_id
```

### نودهایی که باید فیکس بشن

| نود | پارامتر | قبل | بعد |
|-----|---------|------|-----|
| Switch/Router | `output` expression | `$json.callback_query.data` | `$('⚡ Execute Workflow Trigger').first().json.callback_query.data` |
| Telegram (editMessage) | `chatId` | `$json.message.chat.id` | `$('⚡ Execute Workflow Trigger').first().json.callback_query.message.chat.id` |
| Telegram (editMessage) | `messageId` | `$json.message.message_id` | `$('⚡ Execute Workflow Trigger').first().json.callback_query.message.message_id` |
| PostgreSQL (queryReplacement) | `options.queryReplacement` | `$json.callback_query.data` | `$('⚡ Execute Workflow Trigger').first().json.callback_query.data` |
| IF node | `leftValue` | `$json.callback_query.from.id` | `String($('⚡ Execute Workflow Trigger').first().json.callback_query.from.id)` |

### نکته type casting

در IF node با `typeValidation: "strict"`، باید `String()` دور عدد بذاری چون PostgreSQL value رو string برمیگردونه:

```typescript
// ❌ عدد ≠ string در strict mode
leftValue: $json.callback_query.from.id  // number
rightValue: $('👤 Get Settings').first().json.value  // string "123456789"

// ✅ هر دو string
leftValue: String($('⚡ Execute Workflow Trigger').first().json.callback_query.from.id)
rightValue: $('👤 Get Settings').first().json.value
```

### نکته: نام نود Trigger در رفرنس

عبارت `$('⚡ Execute Workflow Trigger')` فقط یه مثاله — **نام واقعی نود** رو باید استفاده کنی. توی coffee bot نامش `⚡ Admin Entry` بود. همیشه با `get_workflow_details` نام دقیق نود trigger رو پیدا کن.

---

## ۱۹. Sub-workflow همزمان: message + callback_query

### مشکل

ساب‌ورک‌فلویی که هم با `/admin` (text command) و هم با callback_query (دکمه) فراخوانی میشه، باید **هر دو نوع ورودی** رو handling کنه:

```
Core Skeleton:
  /admin (text) → Command Router [output 5] → ⚙️ Execute Admin → Sub-workflow
  callback: admin_dashboard → Callback Router [output 10] → ⚙️ Execute Admin → Sub-workflow
```

### رفع

**۱. Gate node:** هر دو `message.from.id` و `callback_query.from.id` رو چک کن:

```typescript
// ✅ optional chaining برای هر دو نوع ورودی
String($('⚡ Admin Entry').first().json.message?.from?.id || $('⚡ Admin Entry').first().json.callback_query?.from?.id)
```

**۲. Router node:** `message.text` و `callback_query.data` رو با هم route کن:

```typescript
// ✅ هر دو source رو ببین
($('⚡ Admin Entry').first().json.message?.text || $('⚡ Admin Entry').first().json.callback_query?.data || '') == 'admin_dashboard'
|| ($('⚡ Admin Entry').first().json.message?.text || '') == '/admin'
```

**۳. Telegram nodes:** `chat.id` و `message_id` از هر دو مسیر بیان:

```typescript
chatId: $('⚡ Admin Entry').first().json.message?.chat?.id || $('⚡ Admin Entry').first().json.callback_query?.message?.chat?.id
messageId: $('⚡ Admin Entry').first().json.message?.message_id || $('⚡ Admin Entry').first().json.callback_query?.message?.message_id
```

### قانون

> ساب‌ورک‌فلویی که هم با text command و هم با callback فراخوانی میشه → **همه expression ها** باید optional chaining با `||` داشته باشن. یه بار بنویس، برای هر دو کار کنه.

---

## ۲۰. Workflow Backup قبل از Edit

### روش

همیشه قبل از ویرایش ورک‌فلو، version history رو بگیر:

```
1. get_workflow_history(workflowId) → لیست versionها
2. get_workflow_version(workflowId, versionId) → snapshot کامل
3. update_workflow → تغییرات
4. publish_workflow → فعال‌سازی
```

اگه اشتباه زدی، `restore_workflow_version` برگردون.

### checkpoint chain

هر `update_workflow` یه versionId جدید برمیگردونه. زنجیره رو دنبال کن:
```
b71767c2 → 0a79a107 → 7a845b08 (هر کدوم یه checkpoint)
```

---

## ۲۱. MCP `update_workflow` Tool Quirks

### setNodeParameter creates nested parameters

`setNodeParameter` with `path: "parameters/output"` incorrectly nests `parameters.parameters.output` instead of replacing `parameters.output`. This causes the Switch node to read the OLD expression.

```
// ❌ Wrong — setNodeParameter creates nesting
"parameters": {
  "output": "={{ OLD_expression }}",        // ← Switch reads this
  "parameters": {
    "output": "={{ NEW_expression }}"        // ← buried, ignored
  }
}

// ✅ Correct — use updateNodeParameters to replace entire params object
updateNodeParameters(nodeName, parameters: { mode, numberOutputs, output: "NEW" })
```

### Expressions cannot use `const` declarations

n8n Switch node expressions do NOT support `const`/`let` declarations. Use inline ternaries:

```
// ❌ Crashes — "Cannot read properties of undefined (reading 'push')"
{{ const src = $('Node').first().json; const d = src.callback_query?.data || src.message?.text || ''; ... }}

// ✅ Inline — repetitive but works
{{ ($('Node').first().json.callback_query && $('Node').first().json.callback_query.data) || ($('Node').first().json.message && $('Node').first().json.message.text) || '' }}
```

> **Shorter alternative:** Add a Code node upstream that normalizes `d = cb.data || msg.text || ''` into `$json.admin_action`, then the Switch just reads `$json.admin_action`.

### Workflow locked while editor is open

`update_workflow` returns `"Cannot modify workflow while it is being edited by a user in the editor."` — the workflow tab must be closed in n8n UI before MCP edits.

### updateNodeParameters missing `type` field

The `type: "updateNodeParameters"` field is REQUIRED in each operation object. Omitting it causes `"Required"` validation error — but confusingly, the error points to `operations[N].type` being `undefined`.

### Batch operations fail silently on expression length

Large Switch expressions (16 outputs) sometimes cause `"Expected object, received string"` when batched. Fix: update one node at a time.

---

## ۲۲. Admin Panel Routing: Switch `rules` Mode با ۱۵+ خروجی

### الگو

یه پنل ادمین تلگرامی که دکمه‌های مختلف callback_data دارن و هر کدوم مسیر جداگانه‌ای داره:

```
⚡ Admin Entry (Execute Workflow Trigger)
  ↓
👤 Get Admin Settings (Postgres: admin_telegram_id)
  ↓
🔐 Admin Gate (IF: from.id == admin_id?)
  ├── true  → ⚡ Normalize Input (Set: mode=raw, jsonOutput extract route)
  │             ↓
  │           🔀 Admin Router (Switch: rules mode, 15 outputs)
  │             ├── output 0:  admin_dashboard       → 📊 Dashboard Stats → ...
  │             ├── output 1:  admin_orders          → 📞 Fetch Pending → ...
  │             ├── output 2:  admin_order_confirm_* → ✅ Extract ID → ...
  │             ├── output 3:  admin_order_reject_*  → ❌ Extract ID → ...
  │             ├── output 4:  admin_order_ship_*    → 🚚 Extract ID → ...
  │             ├── output 5:  admin_order_detail_*  → 📋 Fetch Detail → ...
  │             ├── output 6:  admin_back_orders     → 📞 Fetch Pending
  │             ├── output 7:  admin_ap_yes_*        → ✅ Approve Receipt → ...
  │             ├── output 8:  admin_rj_yes_*        → ❌ Reject Receipt → ...
  │             ├── output 9:  admin_ap_*            → 🔍 Fetch for Approve → ...
  │             ├── output 10: admin_rj_*            → 🔍 Fetch for Reject → ...
  │             ├── output 11: admin_cancel          → ❌ Cancel
  │             ├── output 12: admin_products        → 📦 Products List → ...
  │             ├── output 13: admin_users           → 👤 Users List → ...
  │             ├── output 14: admin_broadcast       → 📢 Count Users → ...
  │             └── fallback:  menu_main             → 🔙 Back to Menu
  └── false → ⛔ Access Denied
```

### Switch rules mode — ساختار دقیق

```jsonc
{
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "rules",
    "numberOutputs": 16,
    "options": { "fallbackOutput": "extra" },
    "rules": {
      "values": [
        {
          "conditions": {
            "combinator": "and",
            "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
            "conditions": [
              { "id": "r0", "leftValue": "={{ $json.route }}", "operator": { "operation": "equals", "type": "string" }, "rightValue": "admin_dashboard" }
            ]
          }
        },
        {
          "conditions": {
            "combinator": "and",
            "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
            "conditions": [
              { "id": "r1", "leftValue": "={{ $json.route }}", "operator": { "operation": "startsWith", "type": "string" }, "rightValue": "admin_order_confirm_" }
            ]
          }
        }
        // ... more rules, one per output
      ]
    }
  }
}
```

### Normalize Input — Set node (mode: raw)

```jsonc
{
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "raw",
    "duplicateItem": false,
    "jsonOutput": "={{ { route: ($('⚡ Admin Entry').first().json.callback_query && $('⚡ Admin Entry').first().json.callback_query.data) || ($('⚡ Admin Entry').first().json.message && $('⚡ Admin Entry').first().json.message.text) || '' } }}",
    "includeOtherFields": false,
    "options": {}
  }
}
```

### تست با Pin Data

برای تست یه مسیر خاص، callback_data مورد نظر رو pin کن:

```
test_workflow(
  workflowId = "...",
  triggerNodeName = "⚡ Admin Entry",
  pinData = {
    "⚡ Admin Entry": [{
      "json": {
        "callback_query": {
          "data": "admin_products",  // ← مسیر مورد نظر
          "from": { "id": 943724562, "first_name": "Amir" },
          "message": { "chat": { "id": 943724562 } },
          "id": "test_callback_001"
        }
      }
    }],
    "👤 Get Admin Settings": [{ "json": { "value": "943724562" } }]
  }
)
```

> **نکته:** `Get Admin Settings` رو هم pin کن تا PostgreSQL واقعی صدا زده نشه.

### قانون

> Switch با `expression` mode توی test همه outputs رو فعال می‌کنه (طبیعیه).
> Switch با `rules` mode فقط output مatching رو فعال می‌کنه — **ولی rules mode از طریق MCP نامعتبر ذخیره میشه** (rules.rules به جای rules.values).
>
> **الگوی قطعی از طریق MCP:** Code node عددی + Switch expression mode.

### ✅ الگوی قطعی: Code node + numeric index

```javascript
// 🔢 Route Index (Code node v2) — بعد از Normalize Input
const route = $json.route || '';
let idx = 16; // fallback = Back to Menu
if (route === 'admin_dashboard') idx = 0;
else if (route === 'admin_orders') idx = 1;
else if (route.startsWith('admin_order_confirm_')) idx = 2;
else if (route.startsWith('admin_order_reject_')) idx = 3;
else if (route.startsWith('admin_order_ship_')) idx = 4;
else if (route.startsWith('admin_order_detail_')) idx = 5;
else if (route === 'admin_back_orders') idx = 6;
else if (route.startsWith('admin_ap_yes_')) idx = 7;
else if (route.startsWith('admin_rj_yes_')) idx = 8;
else if (route.startsWith('admin_ap_')) idx = 9;
else if (route.startsWith('admin_rj_')) idx = 10;
else if (route === 'admin_cancel') idx = 11;
else if (route === 'admin_products') idx = 12;
else if (route === 'admin_users') idx = 13;
else if (route === 'admin_broadcast') idx = 14;
else if (route === 'admin_track_save') idx = 15;
return [{ json: { ...$json, routeIndex: idx } }];
```

```jsonc
// 🔀 Admin Router — Switch expression mode
{
  "mode": "expression",
  "numberOutputs": 17,
  "options": { "fallbackOutput": "extra" },
  "output": "={{ $json.routeIndex }}"
}
```

### `/admin` text → internal route mapping

```javascript
// ⚡ Normalize Input (Code node v2) — sub-workflow context
const e = $('⚡ Admin Entry').first().json;
const route = e.callback_query
  ? e.callback_query.data
  : (e.message && e.message.text === '/admin' ? 'admin_dashboard'
  : e.message ? e.message.text : '');
return [{ json: { ...$json, route } }];
```

### چرا این الگو بهتره؟

| مشکل | Code node + expression | Switch rules mode |
|------|----------------------|-------------------|
| MCP single-quote serialization | ✅ JS syntax در Code node | ❌ rules.values ذخیره نمیشه |
| undefined crash | ✅ fallback مقدار داره | ❌ expression undefined → کرش |
| MCP batch limits | ✅ expression کوتاه | ❌ 16 rules → serialization fail |
| test mode | ✅ کار میکنه | ✅ کار میکنه (اگه ذخیره درست باشه) |
| `/admin` text mapping | ✅ در Code node ساده | ⚠️ نیاز به rule جداگانه |

### قانون

> MCP → Switch routing → همیشه Code node عددی + Switch `expression: "={{ $json.routeIndex }}"`.

---

## تله‌های کلیدی

| # | تله | راه‌حل |
|---|-----|--------|
| ۱ | chat_id اشتباه | supergroup با `-100` شروع می‌شه، private مثبت |
| ۲ | callback بدون answer | UI قفل می‌شه. همیشه اول answerQuery، بعد پردازش |
| ۳ | sendAndWait تایم‌اوت | بعد ۲۴h منقضی میشه. timeout=3600 بذار |
| ۴ | media group order | ترتیب media در array مهمه. درست بچین |
| ۵ | گفتگو همزمان | با دو ID یکسان برخورد نشه — session-based state machine |
| ۶ | `$json` برای دیتای چند قدم قبل | `undefined` میشه. از `$('Node').first().json` استفاده کن |
| ۷ | Fork-Join دوتایی | نود downstream دو بار اجرا میشه. مسیر اضافه رو حذف کن |
| ۸ | فیکس بدون Publish | فقط draft رو عوض می‌کنه. publish کن تا بره روی production |
| ۹ | editMessageText روی پیام عکس | عکس `text` نداره → ارور ۴۰۰. از `sendMessage` استفاده کن |
| ۱۰ | callback_data نشت `undefined` | `split('_').pop()` → NaN. از `.match(/\\d+/)` با fallback ۰ استفاده کن |
| ۱۱ | ExpressionExtensionError در inlineKeyboard | `$('...')` پیچیده داخل additionalFields → syntax error. اول با Set node بساز |
| ۱۲ | Sub-workflow `$json` replacement | اولین نود پردازشی (PostgreSQL/Set) `$json` رو replace می‌کنه → همه downstream خراب. از `$('⚡ Execute Workflow Trigger').first().json` استفاده کن |
| ۱۳ | IF strict mode: number ≠ string | `from.id` (number) ≠ settings `value` (string). با `String()` دور عدد بپیچون |
| ۱۴ | Sub-workflow با text + callback | Sub-workflow همزمان با `/admin` و callback فراخوانی میشه → همه expression ها optional chaining با `||` لازم دارن |
| ۱۵ | نام trigger نود در رفرنس | `$('⚡ Execute Workflow Trigger')` مثاله — نام واقعی نود رو از get_workflow_details بگیر |
| ۱۶ | setNodeParameter nested params | `path: "parameters/output"` nested `parameters.parameters.output` می‌سازه. از `updateNodeParameters` استفاده کن |
| ۱۷ | const/let در Switch expression | n8n expression parser ساپورت نمی‌کنه → از inline ternaries استفاده کن |
| ۱۸ | Workflow edit-lock | اگه تب ورک‌فلو در n8n UI باز باشه → `update_workflow` خطا میده. ببندش |
| ۱۹ | Switch node push crash | expression undefined برگردونه → "Cannot read properties of undefined (reading 'push')". Code node normalizer بذار قبلش (ref: 22-switch-crash-normalizer.md) |
| ۲۰ | Switch update via MCP | `updateNodeParameters`/`setNodeParameter` نمی‌تونه Switch expression رو عوض کنه → removeNode + addNode + rewire |
| ۲۱ | Set mode:raw + assignments | `mode: "raw"` با `assignments` → default values برمیگردونه (my_field_1). از `jsonOutput` استفاده کن |
| ۲۲ | Switch expression mode routing | expression mode توی test همه outputs رو فعال می‌کنه. از `rules` mode با conditions استفاده کن |
| ۲۳ | MCP large operations array | >5 operations در یه array → serialization failure. یکی یکی بفرست |
| ۲۴ | Admin sub-workflow dual input | `/admin` (text) + callback → همه expression ها optional chaining لازم دارن |
| ۲۵ | MCP single-quote serialization | expression حاوی `===` (single quote) → operations stringified. از Code node استفاده کن |
| ۲۶ | Switch rules.values vs rules.rules | MCP `addNode` ممکنه `rules.rules` ذخیره کنه → Switch rules رو نادیده میگیره. از Code node + expression استفاده کن |
| ۲۷ | Set node `$json` in sub-workflow | `$json` بعد از PostgreSQL/Gate فقط خروجی اون نود رو داره. از `$('⚡ Admin Entry').first().json` استفاده کن |
| ۲۸ | `/admin` → `admin_dashboard` mapping | `/admin` text باید به `admin_dashboard` تبدیل بشه وگرنه هیچ rule مچ نمیشه |