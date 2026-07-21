# Workflow Pattern Reference — n8n-intake

> **Purpose:** Pre-digested knowledge from n8n MCP best practices.  
> The model using this skill reads this file — it NEVER calls MCP tools directly.  
> Load with: `skill_view(name='n8n-intake', file_path='references/workflow-patterns.md')`

---

## 1. Trigger Types — چجوری شروع میشه؟

| Trigger | مثال | کی استفاده کنیم؟ |
|---------|------|-----------------|
| **Webhook** | یه سیستم خارجی درخواست می‌فرسته | رویدادهای real-time از بیرون |
| **Schedule (Cron)** | هر روز ۹ صبح | کارهای دوره‌ای، گزارش، پایش |
| **Chat Trigger** | پیام توی Telegram یا Slack | ربات‌های مکالمه |
| **Form Trigger** | کاربر فرم پر می‌کنه | ثبت‌نام، نظرسنجی، سفارش |
| **Service Trigger** | سطر جدید توی Sheets | واکنش به تغییرات سرویس‌ها |

---

## 2. معماری‌های رایج — ۷ الگوی پرکاربرد

### الگوی ۱: Chatbot — ربات مکالمه
```
[Telegram Trigger → AI Agent (LLM + Memory) → Telegram Send]
```
**سوالات مناسب:**  
- "از کدوم پیام‌رسان؟ تلگرام، اسلک، واتساپ؟"  
- "چنل یا گروه؟ حتماً chat ID رو می‌دونی؟"  
- "با AI جواب بده یا منوی ثابت؟"  
- "کدوم LLM؟ OpenAI، Gemini، DeepSeek، Grok؟"  
- "نیاز به حافظه داره؟"  
- "فقط چت کنه یا کار دیگه‌ای هم بکنه؟"

**Credential مورد نیاز:** توکن ربات (مثلاً Telegram Bot API Token)

---

### الگوی ۲: Trigger & Route — دسته‌بندی و مسیریابی (Triage)
```
[Webhook → IF/Switch → مسیرهای مختلف]
```
**موارد استفاده:**  
- دسته‌بندی تیکت‌ها (فوری / معمولی / کم‌اهمیت)  
- مسیریابی ایمیل‌ها  
- امتیازدهی لیدها

**گره‌های کلیدی:** Switch, IF, Text Classifier, AI Agent  
**Credential:** بستگی به خروجی داره (Slack, Email, Sheets)

---

### الگوی ۳: ذخیره‌سازی (Data Persistence)
```
[Trigger → پردازش → Data Table / Sheets / Postgres]
```
**گزینه‌ها:**  
- **Data Table** (داخلی n8n) — برای داده‌های کم تا متوسط، بدون نیاز به credential  
- **Google Sheets** — وقتی کاربر می‌خواد ببینه و ویرایش کنه  
- **Postgres / MySQL / MongoDB** — دیتابیس حرفه‌ای  
- **Airtable** — وقتی رابطه بین جدول‌ها مهمه

**Credential مورد نیاز:** کلید API سرویس مربوطه

---

### الگوی ۴: اعلان (Notification)
```
[Trigger → Check Condition → Email / Slack / Telegram / SMS]
```
**کانال‌ها:**  
- Email (SMTP)  
- Slack (Bot Token + chat:write)  
- Telegram (Bot Token + Chat ID)  
- SMS (Twilio)

**Credential مورد نیاز:** بستگی به کانال داره (SMTP, Slack Token, Twilio)

---

### الگوی ۵: استخراج داده (Data Extraction)
```
[ورودی (فایل/PDF/CSV) → Extract From File / AI → خروجی ساختاریافته]
```
**موارد استفاده:** OCR فاکتور، پارس PDF، استخراج از ایمیل  
**Credential:** OpenAI API Key (برای AI Extraction)

---

### الگوی ۶: تولید محتوا (Content Generation)
```
[Trigger → AI Agent → خروجی متن/تصویر/صدا]
```
**Credential:** OpenAI / StabilityAI / ... Key

---

### الگوی ۷: Web App — فرم و داشبورد
```
[Form Trigger → پردازش → خروجی یا ذخیره‌سازی]
```
برای prototype داخلی، بدون نیاز به Front-end خارجی

---

## 3. Credential Types — چه کلیدهایی نیازه؟

| سرویس | نوع Credential | توضیح |
|-------|---------------|-------|
| **Telegram** | Telegram API | توکن از BotFather |
| **Slack** | Slack API | Bot Token + OAuth |
| **OpenAI** | OpenAI API | API Key |
| **Google Gemini** | Google AI | API Key |
| **DeepSeek** | DeepSeek API | API Key |
| **Grok (xAI)** | xAI API | API Key |
| **Postgres** | Postgres | Host + Port + User + Pass |
| **MySQL** | MySQL | Host + Port + User + Pass |
| **MongoDB** | MongoDB | Connection URI |
| **Google Sheets** | Google Sheets OAuth2 | OAuth via Google Cloud |
| **Airtable** | Airtable API | Personal Access Token |
| **Twilio** | Twilio API | Account SID + Auth Token |
| **SMTP (Email)** | SMTP | Host + Port + User + Pass |
| **HTTP Request** | Header/Basic Auth | API Key توی هدر |

---

## 4. گره‌های کلیدی به تفکیک کاربرد

| دسته | گره‌ها |
|------|--------|
| **AI** | AI Agent, OpenAI Chat Model, Gemini, Grok, DeepSeek, Text Classifier, Information Extractor |
| **Memory** | Simple Memory (Buffer Window), Session Memory |
| **Database** | Data Table, Postgres, MySQL, MongoDB |
| **Spreadsheet** | Google Sheets, Airtable |
| **Communication** | Telegram (trigger+send), Slack, Email, Twilio, WhatsApp, Discord |
| **Logic** | IF, Switch, Filter, Merge |
| **Data** | Set/Edit Fields, Code, Split Out, Aggregate, Summarize, Remove Duplicates, Sort, Limit |
| **File** | Extract From File (PDF/CSV/Excel), HTML Extract |
| **Batch** | Split In Batches (برای دیتای حجیم) |
| **HTTP** | HTTP Request (برای APIهای سفارشی) |

---

## 5. Common Pitfalls — چیزایی که باید موقع نیازمندی بپرسی

1. **Trigger + Chatbot ترکیبی:** اگه کاربر هم Schedule هم Chatbot می‌خواد → باید حافظه مشترک داشته باشن (Memory Node)
2. **ربات حتماً از همون کانال جواب بده:** تلگرام → تلگرام، اسلک → اسلک، مخلوط نکن
3. **n8n Attribution:** ربات‌های تلگرام پیش‌فرض "n8n workflow" رو می‌چسبونن → کاربر می‌تونه غیرفعال کنه
4. **حافظه Session Key:** برای تلگرام از `message.chat.id` استفاده کن، `$json` نباشه
5. **Fallback در Switch:** حتماً مسیر پیش‌فرض بذار (fallbackOutput: 'extra') وگرنه داده گم میشه
6. **Batch دیتای حجیم:** اگه دیتا زیاد (۱۰۰+) می‌خواد → Split In Batches الزامیه
7. **Code Node فرمت:** همیشه `return [{json: {...}}]` برگردونه
8. **Set Node:** "Keep Only Set" تیک نخوره مگر اینکه Intentional باشه (داده رو پاک می‌کنه)
9. **Text Classifier:** حتماً "When No Clear Match" رو به "Other" تنظیم کن

---

## 6. سوالات هوشمندانه بر اساس الگو

وقتی کاربر گفت "می‌خوام..."، بر اساس الگو سوالات خاص بپرس:

| اگه کاربر گفت... | سوالات خاص |
|-----------------|-----------|
| "ربات تلگرام" | توکن داری؟ چت تکی یا گروهی؟ AI می‌خوای یا منوی ثابت؟ |
| "ذخیره اطلاعات" | دیتا چقدره؟ چن تا فیلد؟ نیاز به جستجو داری؟ |
| "ایمیل بزنه" | SMTP داری؟ چند نفر؟ با attachment? |
| "فایل بخونه" | PDF, CSV یا Excel؟ حجمش چقدره؟ |
| "هر روز ساعت X" | cron باشه؟ چه روزایی؟ |
| "API وصل بشه" | REST هست؟ GraphQL؟ کلید API داری؟ |
| "دسته‌بندی کنه" | چند دسته؟ دقیقاً چی رو دسته‌بندی کنه؟ |
| "AI" | کدوم مدل؟ OpenAI, Gemini, Grok, DeepSeek? |
| "شیت" | Google Sheets؟ Airtable؟ |

---

## 7. مثال نگاشت Goal به الگو

| Goal کاربر | Trigger | Pattern | Credentials Needed |
|-----------|---------|---------|-------------------|
| سفارش قهوه با تلگرام | Telegram | Chatbot + Storage | Telegram, OpenAI, Sheets |
| مانیتورینگ سرور | Schedule | Notification | SMTP / Slack |
| استخراج فاکتور از PDF | Webhook | Data Extraction | OpenAI |
| ربات پشتیبانی مشتریان | Telegram | Triage + Chatbot | Telegram, OpenAI, CRM |
| ارسال گزارش روزانه | Schedule | Notification | Email/Slack |
| فرم ثبت‌نام | Form | Data Persistence | Sheets/Data Table |
