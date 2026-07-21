# Best Practices: Notification Workflows

> Technique key: `notification` — Sending alerts or updates via email, chat, SMS when events occur

---

## ۱. زیرساخت کلی

```
[Trigger] → [Data/Condition] → [IF: threshold?]
  ├─ true → [Set: format message]
  │         → [Email] [Slack] [Telegram] [Discord] ... (parallel)
  └─ false → [Log: "no alert needed"]
```

**قانون طلایی:** یه شرط → چند notification به صورت **موازی**. نه اینکه workflow رو کپی کنی.

---

## ۲. نودهای Notification

| پلتفرم | نود | Credential | بهترین برای |
|--------|-----|:----------:|-------------|
| **Telegram** | `telegram` (message.sendMessage) | Bot Token (BotFather) | پیام فوری شخصی/گروهی — پشتیبانی از rich message, document, photo, video, sendAndWait |
| **Slack** | `slack` (message.post) | Bot Token + chat:write | تیم — markdown, channel ID (با C شروع می‌شه), فایل آپلود, sendAndWait |
| **Discord** | `discord` (message.send) | Bot Token | جامعه گیمر/Dev — embed, react, sendAndWait |
| **Email** | `emailSend` (send) | SMTP | گزارش رسمی با attachment, HTML |
| **Twilio** | `twilio` (sms.send) | Account SID + Auth Token | SMS/WhatsApp — بحرانی, مختصر |
| **Teams** | `microsoftTeams` (channelMessage.create / chatMessage.create) | Microsoft Graph | سازمانی — channel/chat/task |
| **Mattermost** | `mattermost` (message.post) | Token | Self-hosted تیم |
| **Pushover** | `pushover` (message.push) | App Token | نوتیفیکیشن موبایل ساده |
| **Gotify** | `gotify` (message.create) | App Token | Self-hosted push |
| **HTTP Request** | `httpRequest` | وابسته به API | Webhook به سرویس‌های بی‌نود (custom) |

---

## ۳. Telegram — Message Operations

| Operation | توضیح |
|-----------|-------|
| `sendMessage` | متن ساده + parse_mode (Markdown/HTML) |
| `sendRichMessage` | متن با headings, lists, tables, media — **پیشنهادی** |
| `sendDocument` | فایل (PDF, CSV, ...) |
| `sendPhoto` / `sendVideo` / `sendAudio` / `sendAnimation` | مدیا |
| `sendMessageDraft` / `sendRichMessageDraft` | استریم partial message در حین تولید |
| **`sendAndWait`** | پیام بده و منتظر جواب کاربر بمون (Human-in-the-loop) |
| `editMessageText` | ویرایش پیام قبلی |
| `deleteMessage` | حذف پیام |
| `pinChatMessage` | پین کردن |

**نکات:**
- Chat ID رو از `telegramTrigger` می‌گیری: `{{ $json.message.chat.id }}`
- `parse_mode: Markdown` برای **bold**, `_italic_`, `` `code` ``
- `sendAndWait` = منتظر جواب کاربر می‌مونه (مفید برای HITL)

---

## ۴. Slack — Message Operations

| Resource | Operation | توضیح |
|----------|-----------|-------|
| **message** | `post` | ارسال به کانال |
| | `sendAndWait` | ارسال + منتظر جواب |
| | `update` | ویرایش |
| | `delete` | حذف |
| | `search` | جستجو |
| | `schedule` | ارسال زمان‌بندی شده |
| **file** | `upload` | آپلود فایل |
| **reaction** | `add` / `get` / `remove` | Emoji reaction |
| **channel** | `create`, `archive`, `invite`, `history`, `members`, ... | مدیریت کانال |

**نکات:**
- Channel ID با `C` شروع می‌شه، نه اسم کانال
- Bot باید قبلاً به کانال invite شده باشه
- Markdown داخل Slack: `*bold*`, `_italic_`, `` `code` ``, `>quote`

---

## ۵. Discord — Message Operations

| Resource | Operation | توضیح |
|----------|-----------|-------|
| **message** | `send` | ارسال متن + embeds |
| | `sendAndWait` | منتظر جواب |
| | `sendLegacy` | از طریق webhook (قدیمی) |
| | `get` / `getAll` | واکشی |
| | `deleteMessage` | حذف |
| | `react` | Emoji reaction |
| **channel** | `create`, `get`, `getAll`, `update`, `deleteChannel` | مدیریت کانال |
| **member** | `getAll`, `roleAdd`, `roleRemove` | مدیریت اعضا |

**نکات:** از Embed برای پیام‌های غنی استفاده کن — `{ title, description, color, fields, footer }`

---

## ۶. Email — Send Email

| Operation | توضیح |
|-----------|-------|
| `send` | ارسال ایمیل (HTML یا plain text) |
| `sendAndWait` | ارسال + منتظر جواب کاربر |

**پارامترها:** `fromEmail`, `toEmail`, `subject`, `text` / `html`, `attachments` (binary)
**نکات:** SMTP credentials لازمه. برای Gmail از App Password استفاده کن.

---

## ۷. Twilio — SMS / WhatsApp

| Operation | توضیح |
|-----------|-------|
| `sms.send` | ارسال SMS/MMS/WhatsApp |
| `call.make` | تماس تلفنی |

**نکات:** شماره به فرمت بین‌المللی: `+1234567890`. پیام مختصر. برای WhatsApp از `messagingServiceSid` مخصوص WhatsApp استفاده کن.

---

## ۸. HTTP Request — برای سرویس‌های بی‌نود

وقتی نود مخصوص不存在ه (یا سرویس خودت APIs):

```
[Set: body آماده کن]
  ↓
[HTTP Request: POST به webhook/service]
  │  URL: "https://hooks.example.com/alert"
  │  Method: POST
  │  Body: { "text": "{{ $json.message }}", "severity": "critical" }
```

**مثال‌ها:**
- Microsoft Teams webhook (connector)
- Discord webhook (sendLegacy)
- سرویس‌های custom notification
- Zapier / Make webhooks

---

## ۹. پترن‌ها

### ۹.۱. Threshold Alert (ساده)
```
[Schedule: هر ۱۵ دقیقه]
  → [Data Table: get error count > 5]
  → [IF: items.length > 0?]
    ├─ true → [Set: format message]
    │         → [Telegram: sendMessage] + [Slack: post]
    └─ false → end
```

### ۹.۲. Multi-Channel با Severity
```
[Webhook: آلرت]
  → [Switch: severity]
    ├─ critical → [Telegram] + [Twilio: SMS] + [Email: به مدیر]
    ├─ warning  → [Slack: #alerts-warning] + [Telegram]
    └─ info     → [Slack: #general]
```

### ۹.۳. Aggregated Report (جمع‌آوری و ارسال)
```
[Schedule: روزانه ۸ صبح]
  → [Data Table: get رکوردهای دیروز]
  → [Summarize: count, sum by category]
  → [Set: ساخت متن گزارش]
  → [Email: send with HTML table + attachment CSV]
  → [Slack: post خلاصه]
```

### ۹.۴. Notification + Logging
```
[Trigger]
  → [IF: condition]
    ├─ true → [Data Table: insert notification_log (status="sent")]
    │         → [Telegram: send]
    │         → [Data Table: update log (status="delivered")]
    └─ false → [Data Table: insert notification_log (status="skipped")]
```

### ۹.۵. Human-in-the-Loop با sendAndWait
```
[Telegram: sendAndWait "آیا این تسک تأیید می‌شه؟"]
  → [IF: پاسخ === "بله"]
    ├─ true → [ادامه workflow]
    └─ false → [Telegram: sendMessage "لغو شد"]
```

### ۹.۶. File Upload + Notification
```
[Webhook: فایل CSV جدید]
  → [Slack: file.upload (گزارش)]
  → [Telegram: sendDocument (فایل)]
  → [Email: send با attachment]
```

---

## ۱۰. Message Formatting

| پلتفرم | فرمت | مثال |
|--------|------|------|
| **Telegram** | Markdown / HTML | `*bold*` یا `<b>bold</b>` |
| **Slack** | Markdown-like | `*bold*`, `>quote`, `` `code` `` |
| **Discord** | Embed JSON | `{ title, description, color: 0xFF0000, fields: [...] }` |
| **Email** | HTML | `<h1>Alert</h1><p>{{ $json.message }}</p>` |
| **SMS** | Plain text | `Alert: Server down` |

**نکته:** مقدار color در Discord به صورت hex decimal: `0xFF0000` = قرمز

---

## ۱۱. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **Slack: اسم کانال به‌جای ID** | از Channel ID استفاده کن (با C شروع می‌شه). از `slack.channel.getAll` بگیر |
| 2 | **ارسال پیام خالی** | `IF: items.length > 0` قبل از notification |
| 3 | **نبودن Bot در کانال (Slack/Discord)** | اول Bot رو به کانال invite کن |
| 4 | **Telegram Chat ID اشتباه** | از trigger بگیری: `$json.message.chat.id` |
| 5 | **Rate limit تلگرام (30 msg/sec)** | برای bulk از Split In Batches + delay استفاده کن |
| 6 | **Slack rate limit (1 msg/sec per channel)** | aggregated report بفرست، نه تکی |
| 7 | **Twilio: شماره نادرست** | فرمت بین‌المللی + شماره verified |
| 8 | **Email: ارسال به SMTP بدون auth** | App Password برای Gmail، SMTP credentials کامل |
| 9 | **HTML ایمیل در SMS** | SMS فقط plain text. از IF جدا کن |
| 10 | **نوتیفیکیشن تکراری** | log بذار + deduplication با removeItemsSeenInPreviousExecutions |
| 11 | **Discord Embed فرمت اشتباه** | color رو به صورت decimal بده، نه hex string |
| 12 | **Continue On Fail فراموش شده** | برای resilience تو notificationها `continueOnFail: true` بذار |

---

## خلاصه

```
فوری شخصی/گروهی   → Telegram (sendMessage / sendRichMessage / sendAndWait)
تیم               → Slack (post / file.upload)
جامعه             → Discord (send / embed)
رسمی + attachment → Email (send + HTML)
بحرانی (SMS)      → Twilio (sms.send)
سازمانی           → Microsoft Teams
Self-hosted team  → Mattermost
Push موبایل       → Pushover / Gotify
Custom API        → HTTP Request
```

> **اصل:** یه trigger → یه شرط → همه notificationها موازی. هیچوقت workflow رو کپی نکن.
