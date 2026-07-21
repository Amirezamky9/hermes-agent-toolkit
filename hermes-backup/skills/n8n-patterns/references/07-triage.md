# Best Practices: Triage

> Technique key: `triage`
> دسته‌بندی و مسیریابی خودکار داده‌ها — کلاسیفای کردن ورودی بر اساس نوع، اولویت، urgency و هدایت به شاخه مناسب

---

## ۱. معرفی

Triage یعنی **ورودی رو بخون، بفهم چیه، بفرست جای درست**.

### کجا کاربرد داره؟

| سناریو | مثال |
|--------|------|
| **پشتیبانی مشتری** | پیام کاربر → "problem" / "question" / "booking" → تیم مربوطه |
| **ایمیل triage** | ایمیل جدید → "spam" / "important" / "notification" / "needs reply" |
| **Ticket handling** | تیکت → severity P1-P5 → مسیر escalation |
| **Deal/CRM routing** | HubSpot deal جدید → stage: won/lost/presentation → اقدام متفاوت |
| **Feedback categorization** | نظرات کاربران → "success story" / "urgent issue" / "feature request" |
| **IT Support triage** | درخواست → "incident" / "service request" / "general" |
| **Signal routing** | سیگنال از Notion → Jira / Sprint / Customer Health |
| **SaaS onboarding** | ثبت‌نام کاربر → "trial" / "paid" / "enterprise" → onboarding path |
| **Telegram bot routing** | پیام → "command" / "callback" / "free text" → state machine |

---

## ۲. زیرساخت کلی

```
[Trigger: Webhook / Gmail / Telegram / Form / Schedule]
    ↓
[Preprocessing: استخراج metadata, normalization]
    ↓
┌────────────────────────────────────────────┐
│           CLASSIFICATION                   │
│                                            │
│  مسیر A: Rule-Based (Switch/IF)            │
│  مسیر B: AI Text Classifier                │
│  مسیر C: AI Agent (multi-step reasoning)   │
│  مسیر D: Combined (rule + AI)              │
└────────────────┬───────────────────────────┘
                 ↓
            [Category + Priority + Confidence]
                 ↓
          [Switch: مسیریابی بر اساس category]
                 ↓
┌────────┬────────┬────────┬────────┬────────┐
│  تیم A  │  تیم B  │  تیم C  │  Default │  Error │
└────┬───┴────┬───┴────┬───┴────┬───┴────┬───┘
     │       │       │       │       │
     ▼       ▼       ▼       ▼       ▼
  [Action] [Action] [Action] [Manual] [Log+Retry]
     │       │       │       │       │
     └───────┴───────┴───────┴───────┘
                 ↓
          [Merge: Logging نهایی]
                 ↓
          [Output: Telegram / Data Table / CRM]
```

---

## ۳. استراتژی‌های Classification

### ۳.۱ Rule-Based (Switch / IF)

**کی استفاده کنیم:** وقتی قوانین دقیق و قابل پیش‌بینی هستن.

```
[ورودی]
    ↓
[Switch: بررسی فیلد خاص]
    ├── value = "bug"       → [Jira: create bug]
    ├── value = "feature"   → [Jira: create story]
    ├── value = "question"  → [AI: پاسخ خودکار]
    └── default             → [Manual Review]
```

**نودها:** `switch` با `options.fallbackOutput: 'extra'`
**مزیت:** سریع، بدون هزینه، predictable
**عیب:** انعطاف‌ناپذیر، متون طبیعی رو نمی‌فهمه

### ۳.۲ AI Text Classifier

**کی استفاده کنیم:** دسته‌بندی متن ساده با برچسب‌های از پیش تعریف‌شده.

```
[ورودی: متن کاربر]
    ↓
[Text Classifier: @n8n/n8n-nodes-langchain.textClassifier]
    │  categories: ["urgent", "question", "feedback"]
    │  model: OpenAI / Gemini
    ↓
[Switch: بر اساس category خروجی]
```

**پارامترها:**
- `model` → مدل انتخابی
- `categories` + `categoryDescriptions` → توضیحات برای هر دسته (به Accuracy کمک می‌کنه)
- `"When No Clear Match"` → `"Output on Extra, 'Other' Branch"` ← **اجباری!**

**مزیت:** ساده، سریع، ارزان (token کم)
**عیب:** متناسب برای classification ساده، نه multi-step reasoning

### ۳.۳ AI Agent (Structured Output)

**کی استفاده کنیم:** classification پیچیده + استخراج اطلاعات اضافی.

```
[ورودی: پیام کاربر]
    ↓
[AI Agent: تحلیل + دسته‌بندی + استخراج]
    │  prompt: "You are a triage agent..."
    │  temperature: 0.1
    │  few-shot examples
    ↓
[Output Parser: enforce JSON schema]
    ↓
[Switch: بر اساس category]
```

**Structured Output Schema:**
```json
{
  "category": "INTERESTED | NOT_INTERESTED | QUESTION",
  "confidence": 0.95,
  "reasoning": "کاربر درباره قیمت پرسیده",
  "extracted_data": {
    "product": "اشتراک حرفه‌ای",
    "urgency": "high"
  }
}
```

**نودها:** `agent` + `lmChat*` + `outputParserStructured`
**مزیت:** انعطاف‌پذیر، multi-step reasoning، استخراج داده
**عیب:** هزینه token بالاتر، latency بیشتر

### ۳.۴ Combined (Rule + AI)

**کی استفاده کنیم:** بهترین حالت — AI حرف آخر رو بزنه، ولی قوانین ساده رو سریع Filter کنه.

```
[ورودی]
    ↓
[IF: keywordهای واضح (مثل "urgent", "refund")]
    ├── yes → [Route مستقیم (بدون AI)]
    └── no  → [AI Agent: classification دقیق]
    │          ↓
    │        [Output Parser: category + confidence]
    │          ↓
    │        [IF: confidence > 0.8?]
    │           ├── yes → [Route خودکار]
    │           └── no  → [Manual Review]
```

---

## ۴. پترن ۱: Customer Support Triage (AI Agent + Switch)

**منطق:** پیام کاربر رو بگیر، دسته‌بندی کن، به Agent تخصصی بفرست.

```
[Webhook: دریافت پیام کاربر]
    ↓
[AI Agent (Routing Agent): دسته‌بندی intent]
    │  categories: ["order_status", "support_ticket",
    │               "product_recommendation", "general"]
    ↓
[Output Parser: JSON با category]
    ↓
[Switch: بر اساس intent]
    ├── order_status
    │   └── [Order Agent: جستجوی سفارش در Supabase]
    │
    ├── support_ticket
    │   └── [Ticket Agent: ایجاد تیکت + ایمیل تأیید]
    │
    ├── product_recommendation
    │   └── [Recommendation Agent: جستجوی محصولات مشابه]
    │
    └── general
        └── [General Agent: پاسخ دوستانه]
    ↓
[Merge: تلفیق همه پاسخ‌ها]
    ↓
[Respond To Webhook: JSON]
```

**نودهای کلیدی:**
- `agent` + `lmChat*` + `outputParserStructured` → Routing Agent
- `switch` → مسیریابی بر اساس category
- `supabaseTool` / `dataTableTool` → جستجوی داده
- `memoryBufferWindow` → حفظ context مکالمه
- `respondToWebhook` → پاسخ نهایی

---

## ۵. پترن ۲: Email Triage (Gmail + AI Classification)

**منطق:** ایمیل جدید رو تحلیل کن، دسته‌بندی کن، draft پاسخ بده.

```
[Gmail Trigger: ایمیل جدید]
    ↓
[Set: آماده‌سازی metadata]
    ↓
[Sentiment Analysis (AI): دسته‌بندی]
    │  categories:
    │  - spam → [Gmail: بایگانی]
    │  - important → [AI: چک کن واقعاً مهمه؟]
    │  - promotion → [AI: مهمه یا نه؟]
    │  - notification → [AI: مهمه یا نه؟]
    │  - personal
    │  - call_request
    │  - needs_reply
    ↓
[AI Agent: Draft Reply (برای personal/call/needs_reply)]
    │  tools: GmailTool, Google CalendarTool
    │  output: structured JSON reply
    ↓
[Gmail: create draft]
    ↓
[Telegram: "✅ Draft برای ایمیل X ساخته شد"]
```

**نودهای کلیدی:**
- `gmailTrigger` → تریگر ایمیل جدید
- `sentimentAnalysis` / `agent` → تحلیل محتوا
- `gmailTool` → ایمیل‌ها + draft
- `googleCalendarTool` → সময় و تاریخ
- `telegram` → نوتیفیکیشن draft

---

## ۶. پترن ۳: SaaS Onboarding + Triage (Multi-Branch)

**منطق:** ثبت‌نام کاربر جدید → تحلیل plan → مسیر onboarding + billing + analytics.

```
[Form Trigger: ثبت‌نام کاربر]
    ↓
[Data Table: ذخیره کاربر جدید]
    ↓
[AI Business Logic Orchestrator: تحلیل کاربر]
    │  - plan type? trial / pro / enterprise
    │  - send welcome email
    │  - assign onboarding path
    ↓
[Data Table: update analytics]
    ↓
[Gmail: ارسال ایمیل خوش‌آمدگویی]
                   
[Webhook: دریافت تیکت پشتیبانی]
    ↓
[AI Support Triage Agent: تحلیل تیکت]
    │  - issue type
    │  - priority (high/low)
    │  - auto-generate response
    ↓
[IF: priority = high?]
    ├── yes → [Gmail: ایمیل فوری به ادمین]
    └── no  → [Gmail: پاسخ خودکار به کاربر]
    ↓
[Data Table: ذخیره تیکت]

[Webhook: رویداد billing]
    ↓
[IF: event type?]
    ├── payment_success → [Gmail: تأیید پرداخت]
    │                     [Data Table: update status=pending]
    └── payment_failed  → [Gmail: اطلاع قطع سرویس]
                          [Data Table: update status=suspended]

[Schedule Trigger (daily): analytics]
    ↓
[Data Table: getAll → Aggregate]
    ├── total users, active, churn rate, revenue
    ↓
[HTTP: ارسال به dashboard API]
```

---

## ۷. پترن ۴: HubSpot Deal Stage Routing

**منطق:** deal جدید در HubSpot → بر اساس stage و value → اقدام متفاوت.

```
[HubSpot Trigger: deal جدید]
    ↓
[HubSpot: get deal (جزئیات کامل)]
    ↓
[Switch: بر اساس deal stage]
    ├── closed_won
    │   └── [Slack: "🎉 فلان معامله بسته شد!"]
    │
    ├── presentation_scheduled
    │   └── [Google Slides: ایجاد presentation]
    │
    └── closed_lost
        └── [Airtable: append به lost deals]
    ↓
(موازی)
    ↓
[IF: value > 500 AND type = newbusiness AND stage not lost/won?]
    ├── yes → [HubSpot: create ticket priority=high]
    └── no  → [HubSpot: create ticket priority=medium]
```

**نودها:** `hubspotTrigger`, `hubspot`, `switch`, `slack`, `googleSlides`, `airtable`, `if`

---

## ۸. پترن ۵: Notion Signal Routing (5-Way Switch)

**منطق:** سیگنال از Notion با وضعیت "Routing" → بر اساس "Route Destination" به مقصد مناسب بفرست.

```
[Notion Trigger: وقتی status = "Routing"]
    ↓
[Code: استخراج همه فیلدها → JSON یکپارچه]
    ↓
[Switch (5-way): بر اساس Route Destination]
    │
    ├── "Jira Bug"
    │   └── [HTTP: POST به Jira API (bug fields + priority)]
    │
    ├── "Jira Feature"
    │   └── [HTTP: POST به Jira API (story + context)]
    │
    ├── "RICE+ Backlog"
    │   └── [Notion: create page در RICE database]
    │
    ├── "Customer Health"
    │   └── [Notion: create page در health tracker]
    │
    └── "Sprint Backlog"
        └── [Notion: create page در sprint database]
    ↓
(همه شاخه‌ها converge)
    ↓
[Notion: update signal → status = "Routed" + reference link]
    ↓
[Slack: reply در thread اصلی + تأیید]
```

**نودهای کلیدی:**
- `notion` → trigger + read + create + update
- `switch` → 5-way routing
- `code` → flatten کردن داده
- `httpRequest` → Jira API
- `slack` → reply در thread

---

## ۹. پترن ۶: IT Support Triage (یکپارچه با ServiceNow)

**منطق:** پیام کاربر → دسته‌بندی (Incident/Request/Other) → اقدام.

```
[Chat Trigger: دریافت پیام]
    ↓
[Text Classifier: دسته‌بندی]
    │  - Incident
    │  - Request
    │  - Everything Else
    ↓
[Switch: بر اساس category]
    ├── Incident
    │   └── [ServiceNow: create incident (short desc=پیام)]
    │
    ├── Request
    │   └── [HTTP: POST به ServiceNow (catalog request)]
    │
    └── Everything Else
        └── [AI Agent: پاسخ هوشمند (web search + memory)]
    ↓
[Summary Chain: خلاصه‌سازی outcome]
    ↓
[Chat Response]
```

**نودها:** `chatTrigger`, `textClassifier`, `switch`, `serviceNow`, `httpRequest`, `agent` + `toolSerpApi`, `memoryBufferWindow`, `chainSummarization`

---

## ۱۰. پترن ۷: Feedback Triage (Discord + AI)

**منطق:** بازخورد کاربر → AI دسته‌بندی کنه → به Discord channel مناسب بفرسته.

```
[Webhook: دریافت بازخورد کاربر]
    ↓
[OpenAI GPT-4: تحلیل و دسته‌بندی]
    │  prompt: classify as "success-story" / "urgent-issue" / "ticket"
    │  output: { category, original_feedback, instruction }
    ↓
[Switch: بر اساس category]
    ├── success-story → [Discord: #user-success]
    ├── urgent-issue → [Discord: #it-urgent]
    └── ticket       → [Discord: #helpdesk]
         default     → [No-Op]
```

---

## ۱۱. پترن ۸: Lead Scoring (AI + Rules)

**منطق:** لید جدید → AI امتیاز بده + Switch مسیریابی کن.

```
[Webhook / Form: لید جدید]
    ↓
[AI Agent: تحلیل لید]
    │  - company size, industry, job title, intent signals
    │  - output: { score: 0-100, segment: "hot"/"warm"/"cold" }
    ↓
[Switch: بر اساس segment]
    ├── hot   → [Slack: به تیم فروش]
    │           [HubSpot: create deal priority=high]
    │
    ├── warm  → [HubSpot: create lead]
    │           [Email: drip campaign]
    │
    └── cold  → [Data Table: nurture queue]
```

---

## ۱۲. نودهای پرکاربرد در Triage

| نود | نقش |
|-----|------|
| `switch` | **مهم‌ترین نود** — مسیریابی چندشاخه |
| `if` | دودویی (true/false) |
| `code` | pre-processing پیچیده |
| `set` | آماده‌سازی فیلدها برای switch |
| `merge` | تلفیق شاخه‌ها بعد از routing |
| `textClassifier` | AI classification ساده |
| `agent` + `lmChat*` | AI classification پیشرفته |
| `outputParserStructured` | enforce JSON schema |
| `sentimentAnalysis` | تحلیل احساسات ایمیل / متن |
| `chainSummarization` | خلاصه outcome |
| `memoryBufferWindow` | حفظ context در Agentهای تخصصی |
| `filter` | حذف آیتم‌های پردازش‌نشده |
| `splitInBatches` | batch processing |

---

## ۱۳. مقایسه روش‌های Classification

| روش | سرعت | هزینه | دقت | انعطاف | کی استفاده کنیم |
|-----|------|-------|-----|--------|---------------|
| **Rule-Based** | 🚀 بالا | 🆓 رایگان | 🟢 قابل قبول | 🔴 کم | فیلدهای مشخص، keywordهای واضح |
| **Text Classifier** | ⚡ متوسط | 💰 کم | 🟡 متوسط | 🟡 متوسط | دسته‌بندی متن با برچسب ثابت |
| **AI Agent** | 🐢 کند | 💰💰💰 | 🟢 بالا | 🟢 بالا | extraction + classification همزمان |
| **Combined** | 🚀+🐢 | 💰+🆓 | 🟢 عالی | 🟢 خوب | بهترین حالت — rule filter + AI depth |

---

## ۱۴. تله‌ها و نکات

### 🕳️ No Default Path در Switch
**مشکل:** Switch بدون fallback — آیتم‌های unmatched **بی‌صدا حذف میشن**.
**راه‌حل:** همیشه `options.fallbackOutput: 'extra'` رو تنظیم کن.
```
switch → options: { fallbackOutput: 'extra' }
```

### 🕳️ Overlapping Conditions
**مشکل:** دو شرط روی یه آیتم match می‌کنن.
**راه‌حل:** Switch با مقادیر distinct (نه چند IF موازی که هر دو می‌تونن true باشن).
از **مختص‌ترین** به **عام‌ترین** مرتب کن.

### 🕳️ Text Classifier بدون "Other"
**مشکل:** آیتم‌هایی که با هیچ category match نمی‌شن حذف میشن.
**راه‌حل:** حتماً "When No Clear Match" = "Output on Extra, 'Other' Branch"

### 🕳️ AI Agent دمای بالا
**مشکل:** classification غیرقابل پیش‌بینی (هر بار یه جور)
**راه‌حل:** `temperature: 0.1` یا حتی `0` برای triage.

### 🕳️ AI بدون few-shot
**مشکل:** AI دسته‌بندی رو درست نمی‌فهمه.
**راه‌حل:** همیشه توی prompt چند نمونه input + output مثال بزن.

### 🕳️ Confidence نادیده گرفته شده
**مشکل:** AI با confidence پایین (< 0.6) رو route می‌کنی.
**راه‌حل:** یه IF بذار بعد از AI: اگه `confidence < 0.7` → manual review.

### 🕳️ Context از دست رفته در Agentهای تخصصی
**مشکل:** بعد از Routing Agent, Agent تخصصی نمی‌دونه قبلاً چی شده.
**راه‌حل:**
- `memoryBufferWindow` رو به Agent تخصصی وصل کن
- context رو به‌عنوان tool input پاس بده

### 🕳️ Gmail Trigger تکراری
**مشکل:** هر بار که workflow اجرا میشه، ایمیل‌های قبلی رو دوباره پردازش می‌کنه.
**راه‌حل:** از فیلتر Gmail Trigger استفاده کن (`query: is:unread`) + بعد از پردازش مارک read کن.

---

## ۱۵. معماری‌های نمونه

### معماری A: Triage Pipeline جامع (توصیه‌شده)

```
[Trigger: Webhook / Gmail / Chat]
    ↓
[Preprocessing: extract sender, timestamp, content]
    ↓
[Rule Filter: keywordهای واضح]
    ├── refund → [Route: تیم مالی]
    ├── urgent → [Route: priority queue]
    └── others → [AI Classification]
    │              ↓
    │            [AI Agent: category + confidence + reasoning]
    │              ↓
    │            [IF: confidence > 0.8?]
    │               ├── yes → [Switch: route by category]
    │               └── no  → [Slack: manual review queue]
    ↓
[Merge: همه شاخه‌ها ← لاگ نهایی]
    ↓
[Data Table: ذخیره triage log (ورودی, category, confidence, action, timestamp)]
```

### معماری B: Simple Rule-Based

```
[Trigger: Webhook]
    ↓
[Switch: بررسی فیلد type]
    ├── "order" → [Order Service]
    ├── "ticket" → [Ticket Service]
    ├── "feedback" → [Feedback Service]
    └── default → [Manual Review]
```

### معماری C: AI-Only Triage

```
[Trigger: Chat Message]
    ↓
[AI Agent: "classify and respond"]
    │  tools: knowledge base, CRM lookup
    │  output: { category, reply, confidence }
    ↓
[IF: confidence > 0.8?]
    ├── yes → [Respond to user]
    └── no  → [Slack: "نیاز به بررسی انسانی"]
```

### معماری D: Event-Driven Triage (HubSpot)

```
[HubSpot Trigger: deal/contact/ticket event]
    ↓
[HubSpot: get details]
    ↓
[Switch: بر اساس event type]
    ├── deal.created → [Lead Scoring + Assignment]
    ├── ticket.created → [Severity Assessment + Team Assignment]
    ├── deal.stage.changed → [Stage-based Action (Slack/Jira/Sheets)]
    └── contact.updated → [Enrichment Pipeline]
```

---

## ۱۶. Checklist طراحی Triage

| کار | توضیح |
|-----|--------|
| ✅ دسته‌ها رو clear و mutually exclusive تعریف کن | "urgent" و "important" همپوشانی دارن |
| ✅ fallback/default path بذار | Switch با `fallbackOutput: 'extra'` |
| ✅ confidence threshold بذار | AI < 0.7 → manual review |
| ✅ logging نهایی داشته باش | همه triageها توی Data Table ذخیره بشن |
| ✅ metadata کافی بذار | timestamp, category, confidence, action |
| ✅ escalation path تعریف کن | بعد N بار خطا → انسان |
| ✅ typeValidation=false روی Switch | اگه مقادیر عددی/Boolean از DB میاد |
| ✅ temperature پایین برای AI | 0.1 حداکثر |

---

> 💡 **اصل طلایی Triage:** همه چیز به یه جایی باید برسه. هیچ ورودی‌ای نباید بی‌صدا حذف بشه. حتی "این رو نمی‌فهمم" هم باید توی log بنویسی.
