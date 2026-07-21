# Best Practices: Human in the Loop (HITL)

> Technique key: `human_in_the_loop` — Pausing workflow for human decision/input before resuming

---

## ۱. معماری کلی

```
[Trigger] → [Data/Process] → [Send Message + Wait]
                                ↓ انسان تصمیم می‌گیره
                              [Receive Response]
                                ↓
                              [IF: approve/reject?]
                                ├─ approve → ادامه workflow
                                └─ reject / timeout → fallback
```

**سه راه اصلی HITL در n8n:**
1. **sendAndWait** — بومی‌ترین راه. خود نود منتظر جواب می‌مونه
2. **Wait + Webhook** — برای Approval پیچیده (مثلاً ایمیل با لینک)
3. **Form Trigger** — فرم اختصاصی

---

## ۲. sendAndWait — ساده‌ترین راه

پشتیبانی‌شده در نودهای زیر:

| نود | operation | خروجی |
|-----|-----------|-------|
| **Telegram** | `message.sendAndWait` | پاسخ کاربر به‌عنوان message بعدی |
| **Slack** | `message.sendAndWait` | پاسخ کاربر |
| **Discord** | `message.sendAndWait` | پاسخ کاربر |
| **Email (SMTP)** | `sendAndWait` | کلیک روی Approve/Reject لینک |
| **Gmail** | `message.sendAndWait` | کلیک روی لینک |
| **Outlook** | `message.sendAndWait` | کلیک روی لینک |
| **Teams** | `chatMessage.sendAndWait` | پاسخ کاربر |
| **Google Chat** | `message.sendAndWait` | پاسخ کاربر |

### Flow ساده با sendAndWait
```
[Telegram Trigger]
  → [Process: generate summary]
  → [Telegram: sendAndWait "آیا این رو تأیید می‌کنی؟"]
  → (wait for response)
  → [IF: response === "بله"]
    ├─ true → [ادامه workflow]
    └─ false → [Telegram: sendMessage "لغو شد"]
```

> **نکته:** `sendAndWait` execution رو pause می‌کنه تا کاربر جواب بده. مدت انتظار با `wait` node زمان‌بندی میشه.

---

## ۳. Telegram HITL — کامل‌ترین راه

عملیات‌های مفید برای HITL:

| Operation | توضیح |
|-----------|-------|
| `sendMessage` | ارسال پیام با دکمه شیشه‌ای (inline keyboard) |
| `sendAndWait` | ارسال + منتظر جواب مستقیم |
| `sendRichMessage` | پیام با headings, tables + دکمه |
| `editMessageText` | ویرایش پیام بعد از تصمیم |
| `deleteMessage` | حذف پیام بعد از تصمیم |
| `sendChatAction` | typing indicator در حین انتظار |

### Telegram Batch Approval
```
[Process: ۵ آیتم نیاز به تأیید]
  → [Loop: for each item]
    → [Telegram: sendAndWait "آیتم #N رو تأیید می‌کنی؟"]
    → [Data Table: insert decision (itemId, response)]
  → [Loop done]
  → [Telegram: sendMessage "همه تصمیم‌ها ثبت شد"]
```

---

## ۴. Email HITL — ایمیل با لینک Approve/Reject

emailSend/Gmail/Outlook با `sendAndWait` یک ایمیل با دکمه‌های Approve/Reject می‌فرسته. کاربر کلیک می‌کنه → n8n ادامه می‌ده.

```
[Schedule: گزارش روزانه]
  → [Set: prepare report]
  → [Email: sendAndWait "آیا گزارش رو ارسال کنم؟" + approve/reject links]
  → (wait for click)
  → [IF: approve?]
    ├─ true → [Email: send report to manager]
    └─ false → [Data Table: log "skip"]
```

**نکته:** لینک‌های approve/reject خودکار توسط n8n ساخته می‌شن. نیاز به webhook URL در SMTP credential داری.

---

## ۵. Form Trigger — فرم اختصاصی

برای review پیچیده (چندتا فیلد, انتخاب, توضیح):

```
[Form Trigger: فرم review]
  → [Data Table: get مورد نیاز به تأیید]
  → [Form: نمایش آیتم + دکمه‌های submit]
  → (کاربر فرم رو پر می‌کنه)
  → [Form Trigger (response): دریافت جواب]
  → ادامه workflow
```

**پارامترهای Form Trigger:**
- `formTitle`, `formDescription`, `formFields`: تعریف فیلدها
- `responseMode`: پاسخ رو به workflow برگردونه
- `options`: تایم‌اوت, پیام success

> **مقایسه:** Form برای مواردی مناسبه که کاربر نیاز به پر کردن چند فیلد داره. sendAndWait برای یک تصمیم ساده.

---

## ۶. Wait + Webhook — HITL دستی

وقتی sendAndWait کافی نیست:

```
[Trigger: درخواست]
  → [Send: نوتیفیکیشن به کاربر (لینک approve/reject)]
  → [Wait: Reschedule - تا timeout یا دریافت webhook]
    │
    └── همزمان:
        [Webhook: دریافت جواب]
        → [Data Table: store decision]
  → (resume at Wait با جواب)
  → [IF: approve?]
```

---

## ۷. Timeout Handling

| روش | توضیح |
|-----|-------|
| **Wait node** | `resumeMode: "afterTimeInterval"` — تایم‌اوت مستقیم |
| **SendAndWait timeout** | خود نود timeout داره. بعد از timeout execution resume میشه |
| **Telegram + Wait** | `Wait: ۲۴ ساعت` → اگه جوابی نیومد، fallback |

```
[Telegram: sendAndWait "تصمیم بگیر"]
  → [Wait: ۲۴ ساعت / timeout]
  → [IF: response?]
    ├─ yes → پردازش
    └─ no/timeout → [Telegram: "تایم‌اوت — به‌طور پیش‌فرض رد شد"]
                    [Data Table: log timeout]
```

> **همیشه تایم‌اوت بذار.** یکشنبه‌ها کسی جواب نمی‌ده.

---

## ۸. پترن‌ها

### ۸.۱. تک Approval
```
[Webhook: درخواست]
  → [Telegram: sendAndWait "آیا {$json.taskName} تأیید می‌شه؟"]
  → [IF: response === "بله"]
    ├─ → [ادامه workflow]
    └─ → [لغو + لاگ]
```

### ۸.۲. Batch Approval (چندتایی)
```
[Schedule: هر روز ۸ صبح]
  → [Data Table: get pending items]
  → [Loop: for each]
    → [Telegram: sendAndWait "آیتم #$index: $item.name؟"]
    → [Data Table: update status]
  → [Telegram: sendMessage "همه تصمیم‌ها گرفته شد"]
```

### ۸.۳. Two-Phase Approval
```
[Webhook: درخواست]
  → [Email: sendAndWait "مدیر ۱: تأیید می‌کنی؟"]
  → (جواب مدیر ۱)
  → [IF: approve?]
    ├─ true → [Email: sendAndWait "مدیر ۲: تأیید می‌کنی؟"]
    │        → (جواب مدیر ۲)
    │        → [ادامه workflow]
    └─ false → [لغو]
```

### ۸.۴. Human Review + Comment
```
[Form Trigger: review form]
  → [Form: نمایش آیتم + textarea for comment + دکمه approve/reject]
  → (پر شدن فرم)
  → [IF: approve + comment?]
    ├─ → [ادامه workflow + ثبت comment]
    └─ → [لغو + ثبت comment]
```

### ۸.۵. Escalation (خودکار بعد از تایم‌اوت)
```
[Telegram: sendAndWait "تصمیم کن" — به user A]
  → Wait: 4 hours
  → [IF: response?]
    ├─ yes → continue
    └─ timeout → [Telegram: sendAndWait "تصمیم کن" — به user B (escalate)]
                → Wait: 4 hours
                → [IF: response?]
                  ├─ yes → continue
                  └─ timeout → [Telegram: "تسک auto-approved"]
```

### ۸.۶. Slack + Multi-User Voting
```
[Slack: sendAndWait "آیا این تغییر رو deploy کنیم؟"]
  → (multiple users می‌تونن رأی بدن)
  → Wait: 2 hours
  → [Summarize: count votes]
  → [IF: approve > reject?]
    ├─ true → deploy
    └─ false → cancel
```

---

## ۹. Decision Logging

همیشه بعد از HITL لاگ بذار:

```
[Data Table: insert decision_log]
  │  decisionId (auto)
  │  workflowName, itemId
  │  decider: "{{ $json.from }}"
  │  decision: approve/reject/timeout
  │  comment: "..."
  │  decidedAt: $now.toISO()
  │  responseTime: $now.diff($startTime)
```

---

## ۱۰. مقایسه روش‌های HITL

| روش | Credential | UX | مناسب برای |
|-----|:----------:|:--:|-----------|
| **sendAndWait (Telegram/Slack)** | Bot Token | دکمه / جواب متنی | تصمیم سریع — بهترین گزینه |
| **sendAndWait (Email)** | SMTP | لینک در ایمیل | رسمی + attachment |
| **Form Trigger** | ❌ | فرم کامل | review با چند فیلد |
| **Wait + Webhook** | وابسته | حداکثر انعطاف | سناریوهای خاص |
| **Slack reaction** | Bot Token | Emoji react | رأی‌گیری ساده |

---

## ۱۰. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **بدون تایم‌اوت** | همیشه Wait یا timeout بذار. یکی نیاد جواب بده چی؟ |
| 2 | **Telegram chat ID اشتباه** | از trigger بگیر: `$json.message.chat.id` |
| 3 | **ایمیل بدون webhook برای sendAndWait** | SMTP credential باید webhook URL داشته باشه |
| 4 | **کاربر جواب نمی‌ده** | escalation یا auto-fallback |
| 5 | **چندتا جواب از یک کاربر** | idempotency key بذار (messageId) |
| 6 | **عدم لاگ تصمیم** | همیشه log بذار. قابل audit باشه |
| 7 | **Form تایم‌اوت نداره** | خودت Wait قبل از Form بذار |
| 8 | **Slack: Bot به DM دسترسی نداره** | Bot رو اول به کانال invite کن |
| 9 | **Discord sendAndWait فقط یه جواب** | بعد از جواب, پیام رو ویرایش/حذف کن |
| 10 | **تصمیم اشتباه منجر به داده فاسد** | undo capability یا confirmation دوم |

---

## خلاصه

```
تصمیم سریع (دکمه) → Telegram sendAndWait
رسمی + attachment → Email sendAndWait
چند فیلد / متن طولانی → Form Trigger
Voting تیمی        → Slack sendAndWait
Two-phase approval → زنجیره sendAndWait
تایم‌اوت           → Wait node + escalation
همیشه: log بذار + timeout + auto-fallback
```