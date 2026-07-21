# Best Practices: Monitoring

> Technique key: `monitoring`
> چک کردن دوره‌ای وضعیت سرویس‌ها، workflowها، دیتا و لاگ‌ها + نوتیفیکیشن + مصورسازی

---

## ۱. معرفی

مانیتورینگ توی n8n یعنی **چک کردن دوره‌ای و خودکار** وضعیت چیزها:

| چی رو مانیتور می‌کنیم؟ | چطور؟ |
|----------------------|-------|
| **Workflow health** | n8n API → آخرین execution |
| **API/Site uptime** | HTTP Request → status code |
| **Data Table records** | Data Table → GET با شرط |
| **SSL / Domain expiry** | HTTP Request (check API) |
| **لاگ‌ها و executionها** | n8n execution → getAll |
| **RSS/Release‌ها** | RSS Feed Read |
| **دیتابیس (Postgres و...)** | SQL query |
| **Changelog / security** | GitHub API + AI analysis |

---

## ۲. زیرساخت کلی

```
[Schedule Trigger | Cron | Interval]
    ↓
[Source Check: HTTP / DataTable / n8n API / SQL / RSS]
    ↓
[IF: وضعیت مطلوب؟]
    ├── ✅ yes → [Log: No-Op / DataTable / Sheet]  ← ثبت سالم
    └── ❌ no  → [Alert: Telegram / Slack / Email / SMS / Jira]
                    ↓
                  [Escalation: اگر N بار متوالی خطا → alert متفاوت]
```

### تریگرهای رایج

| تریگر | کی استفاده کنیم |
|-------|----------------|
| `scheduleTrigger` | کرون انعطاف‌پذیر (دقیقه/ساعت/روز) |
| `cron` | کرون fixed (مثلاً هر روز ۸ صبح) |
| `interval` | بازه ثابت (هر ۱۰ دقیقه) |
| `webhook` | مانیتورینگ رویدادمحور (incoming webhook) |
| `manualTrigger` | دیباگ و تست دستی |

### انواع آلرت

| سرویس | موارد استفاده |
|-------|--------------|
| `telegram` | آلرت سریع توی کانال/گروه |
| `slack` | آلرت توی کانال DevOps |
| `gmail` / `emailSend` | آلرت رسمی + summary روزانه |
| `twilio` | SMS برای بحرانی‌ها |
| `jira` / `linear` | ایجاد تیکت برای رفع مشکل |
| `awsSes` / `sendgrid` | میل سرور اختصاصی |
| `custom` HTTP Request | هر API دیگه (ntfy, pushover, ...) |

---

## ۳. پترن ۱: مانیتورینگ Workflow Health

**منطق:** برو ببین کدوم workflowها از برنامه اجرا عقب افتادن.

```
[Schedule Trigger (hourly)]
    ↓
[n8n: workflows → getAll]
    ↓
[Code: فیلتر workflowهای schedule/polling دار]
    ↓
[Split In Batches]
    ↓
[n8n: execution → get (آخرین اجرا)]
    ↓
[Code: محاسبه - آیا از آخرین اجرا بیشتر از تایم انتظار گذشته؟]
    ↓
[IF: stale?]
    ├── no  → [No-Op: همه سالم]
    └── yes → [Stop & Error: آلرت با جزئیات]
```

**نودهای کلیدی:**
- `n8n` → `resource: workflow, operation: getAll` — همه workflowها
- `n8n` → `resource: execution, operation: get` — آخرین اجرا
- `code` → محاسبه `maxAllowedAge` بر اساس interval/cron
- `if` → مقایسه `lastExecutionTime` با `maxAllowedAge`
- `stopAndError` → خطا هندلینگ مرکزی (به Error Trigger می‌خوره)

> 💡 می‌تونی tag بزنی به workflowها: `skip-monitoring`, `daily`, `critical`
> و توی code فقط اونایی که tag `skip-monitoring` ندارن رو بررسی کنی.

---

## ۴. پترن ۲: Health Check سرویس خارجی

**منطق:** یه API/Site رو ping بزن، اگه ۲۰۰ برنگردوند آلرت بده.

```
[Schedule Trigger (every 10 min)]
    ↓
[Google Sheets: خواندن لیست URLها]
    ↓
[Split In Batches (batch: 1)]
    ↓
[Set: ثبت timestamp شروع]
    ↓
[HTTP Request: GET با timeout=3s]
    ↓
[IF: status code = 200?]
    ├── ✅ yes → [Set: status=OK]
    │            ↓
    │          [Google Sheets: append به Check Log]
    └── ❌ no  → [Set: status=ERROR]
                 ↓
               [Google Sheets: append به Check Log]
                 ↓
               [GPT-4o-mini: تولید پیام آلرت]
                 ↓
               [Gmail: ارسال ایمیل آلرت]
                 ↓
               [Google Sheets: update alert_sent=true]
```

**نودهای کلیدی:**
- `httpRequest` → `method: GET, timeout: 3000, options: {json: true}`
- `if` → چک کردن `statusCode = 200`
- `splitInBatches` → پردازش یکی‌یکی URLها
- `gmail` / `telegram` / `slack` → نوتیفیکیشن
- `googleSheets` → خواندن لیست + ذخیره لاگ

### پارامترهای مهم HTTP Request برای health check

| پارامتر | مقدار | چرا |
|---------|-------|-----|
| `method` | `GET` | ساده‌ترین |
| `timeout` | `5000` (5s) | timeout سریع اگه سایت پایین‌است |
| `retryOnFail` | `true` | یک بار دیگه امتحان کنه |
| `maxTries` | `2` | بیش از ۲ بار تکرار نکن |
| `options.allowUnauthorizedCerts` | `false` | SSL رو جدی بگیر |

---

## ۵. پترن ۳: مانیتورینگ Data Table

**منطق:** جدول رو چک کن ببین کدوم recordها نیاز به پیگیری دارن.

```
[Schedule Trigger (daily)]
    ↓
[Data Table: row → get (با returnAll و filter)]
    ↓
[IF: رکورد نیازمند آلرت وجود داره؟]
    ├── yes → [Telegram/Slack: ارسال لیست]
    │         ↓
    │        [Data Table: update → mark notified]
    └── no  → [No-Op: همه چی عادی]
```

**موارد استفاده:**
- سفارش‌های پرداخت‌نشده (pending orders)
- کاربران ثبت‌نام‌کرده ولی فعال‌نشده
- sessionهای منقضی‌شده
- خطاهای ثبت‌شده که resolution ندارن
- رکوردهای قدیمی‌تر از N روز

**نودها:**
- `dataTable` → `resource: row, operation: get, returnAll: true`
- `if` → بررسی وجود رکورد
- `telegram` / `slack` → نوتیفیکیشن
- `dataTable` → `operation: update` (مارک کردن به عنوان رسیدگی‌شده)

### مثال: چک کردن خطاهای unresolved

```
[Schedule Trigger (every 6h)]
    ↓
[Data Table: row → get | filter: resolved=false]
    ↓
[IF: count > 0?]
    ├── yes → [Set: پیام خلاصه]
    │         ↓
    │        [Telegram: "⚠️ 5 خطا نیاز به بررسی داره"]
    └── no  → [No-Op]
```

---

## ۶. پترن ۴: SSL / Domain Expiry

**منطق:** تاریخ انقضای SSL رو چک کن، اگه نزدیک بود آلرت بده.

```
[Schedule Trigger (daily at 8 AM)]
    ↓
[Google Sheets: خواندن لیست domainها]
    ↓
[Filter: حذف domainهای غیرفعال]
    ↓
[Split In Batches]
    ↓
[HTTP Request: SSL checker API (ssldecks.com/json)]
    ↓
[Code: محاسبه days remaining + وضعیت (Expired/Critical/Warning/Healthy)]
    ↓
[IF: نیاز به آلرت داره؟]
    ├── ✅ yes → [Jira: ایجاد تیکت]
    │            ↓
    │           [Slack: ارسال هشدار]
    │            ↓
    │           [Gmail: ایمیل به تیم]
    └── ❌ no  → [Google Sheets: لاگ سالم]
                 ↓
               [Code: Aggregate گزارش روزانه]
                 ↓
               [Slack: ارسال digest dayانه]
```

**وضعیت‌بندی:**

| روز باقی‌مونده | وضعیت | اقدام |
|---------------|-------|--------|
| < 0 | Expired | 🔴 آلرت فوری |
| 0-7 | Critical | 🔴 تیکت + آلرت |
| 8-30 | Warning | 🟡 آلرت (بدون تیکت) |
| > 30 | Healthy | 🟢 لاگ سالم |
| Unknown | Unknown | ⚪ احتمالاً خطا |

---

## ۷. پترن ۵: Execution Log Dashboard

**منطق:** از همه workflowها آمار بگیر و یه داشبورد HTML/JSON بده.

```
[Manual Trigger / Webhook]
    ↓
[n8n: workflow → getAll]
    ↓
[Code: استخراج node types, tags, webhooks]
    ↓
[Set: خلاصه هر workflow]
    ↓
[Aggregate: آمار کلی (تعداد نودها, tagها, webhookها)]
    ↓
[Merge: تلفیق همه آمارها]
    ↓
[XML: تبدیل JSON به XML]
    ↓
[HTML: XSLT transform → داشبورد بصری]
```

**آمارهای قابل استخراج:**

| معیار | توضیح |
|-------|--------|
| تعداد کل workflowها | active + inactive |
| تعداد کل نودها | تفکیک‌شده بر type |
| popular node types | کدوم نودها بیشتر استفاده شدن |
| tag distribution | workflowها بر اساس tag |
| webhook endpoints | همه endpointهای فعال |
| فعال/غیرفعال | درصد workflowهای active |
| trigger types | schedule, webhook, manual, etc. |

> 💡 برای dashboard ساده‌تر از `quickChart` استفاده کن به جای XML+HTML
> برای dashboard حرفه‌ای از `grafana` node استفاده کن

---

## ۸. پترن ۶: مانیتورینگ Changelog / Release

**منطق:** GitHub API یا RSS رو چک کن ببین release جدید اومده.

```
[Schedule Trigger (daily)]
    ↓
[GitHub API: releases → getAll]
    ↓
[Code: مقایسه با آخرین نسخه ذخیره‌شده]
    ↓
[IF: release جدید؟]
    ├── yes → [AI: تحلیل changelog (breaking? urgent?)]
    │         ↓
    │        [IF: urgency=critical]
    │         ├── critical → [Alert فوری: Telegram + Slack]
    │         └── normal   → [Batch: ذخیره برای digest روزانه]
    │         ↓
    │        [PostgreSQL: ذخیره تاریخچه releaseها]
    │         ↓
    │        [Set: بروزرسانی آخرین نسخه]
    └── no  → [No-Op]
```

**موارد استفاده:**
- مانیتورینگ نسخه‌های n8n
- مانیتورینگ سرویس‌های self-hosted (Immich, Traefik, ...)
- مانیتورینگ امنیتی (CVE, security patches)
- خبرهای RSS (ردیت، وبلاگ‌ها)

**نودهای ویژه:**
- `rssFeedRead` → برای RSS/Atom feed
- `httpRequest` → برای GitHub API
- `code` → مقایسه version با semver
- `lmChatAnthropic` / `openAi` → تحلیل changelog با AI
- `postgres` / `dataTable` → ذخیره تاریخچه

---

## ۹. پترن ۷: Threshold Alert از دیتابیس

**منطق:** دیتابیس رو query بزن، اگه مقداری از حد گذشت آلرت بده (و جلوگیری از آلرت تکراری).

```
[Cron Trigger]
    ↓
[PostgreSQL: SELECT * FROM sensors WHERE value > 70 AND notified=false]
    ↓
[IF: رکورد وجود داره؟]
    ├── yes → [Twilio: SMS آلرت]
    │         ↓
    │        [Set: notified=true]
    │         ↓
    │        [PostgreSQL: UPDATE sensors SET notified=true]
    └── no  → [No-Op]
```

**تکنیک جلوگیری از آلرت تکراری:**
1. یه فیلد `notified` (boolean) یا `last_alerted_at` (timestamp) توی جدول بذار
2. query فقط رکوردهای `notified=false` رو بزن
3. بعد از آلرت، مقدار رو `true` کن یا timestamp بذار
4. یه cron جداگانه می‌تونه بعد از رفع مشکل، `notified` رو ریست کنه

---

## ۱۰. پترن ۸: مانیتورینگ Event-driven (Webhook)

**منطق:** به جای polling، بذار سرویس خودش بهت خبر بده (webhook incoming).

```
[Webhook Trigger]
    ↓
[IF: type = error یا type = threshold_exceeded؟]
    ├── yes → [Telegram: آلرت فوری]
    │         ↓
    │        [Data Table: insert به error_logs]
    └── no  → [No-Op: فقط لاگ]
```

**کی استفاده کنیم:**
- سرویس‌هایی که webhook support دارن (GitHub, GitLab, Stripe, etc.)
- مانیتورینگ‌هایی که تأخیر ۱-۲ ثانیه‌ای براشون acceptable نیست
- وقتی polling خیلی heavy هست

> ⚠️ همیشه یه Schedule-based fallback هم بذار — اگه webhook نیومد، cron جاش پر کنه.

---

## ۱۱. پترن ۹: Escalation (آلرت پله‌ای)

**منطق:** اگه یه خطا N بار متوالی تکرار شد، آلرت رو escalated کن.

```
[Schedule Trigger]
    ↓
[Source Check]
    ↓
[IF: error?]
    ├── yes → [Data Table: insert/update error_counter +1]
    │         ↓
    │        [IF: count >= 3?]
    │         ├── no  → [Telegram: آلرت معمولی]
    │         └── yes → [Slack @channel + SMS: آلرت بحرانی]
    │                    ↓
    │                   [Jira: تیکت P1]
    └── no  → [Data Table: reset error_counter = 0]
```

**سطوح escalation:**

| تعداد خطاهای متوالی | اقدام |
|--------------------|--------|
| ۱ | فقط لاگ |
| ۲ | Telegram آلرت ساده |
| ۳+ | Slack @channel / SMS / Jira تیکت |
| N/A (رفع شد) | ریست کردن کانتر |

---

## ۱۲. مصورسازی (Visualization)

### QuickChart

نود `quickChart` برای ساختن نمودار از آمارها:

```
[Data Table: getAll execution logs]
    ↓
[Code: آماده‌سازی داده (labels + datasets)]
    ↓
[QuickChart: chartType=line|bar|pie]
    ↓
[Telegram/Slack: ارسال عکس نمودار]
```

**نوع چارت‌های QuickChart:**

| نوع | کاربرد |
|-----|--------|
| `line` | trend success rate در طول زمان |
| `bar` | مقایسه تعداد خطاها بین workflowها |
| `pie` | توزیع statusها (success/error/waiting) |
| `doughnut` | نسبت workflowهای active/inactive |
| `polarArea` | توزیع node types استفاده‌شده |

### Google Sheets + Chart

می‌تونی لاگ‌ها رو توی Google Sheets بزاری و از chart داخلی خودش استفاده کنی.

### Grafana

n8n نود `grafana` داره که می‌تونه dashboard بسازه:
- `resource: dashboard, operation: create` → ساخت dashboard جدید
- `operation: update` → آپدیت dashboard موجود

> 💡 ترکیب مرسوم: Data Table + QuickChart + Telegram = dashboard جیبی

---

## ۱۳. نودهای پرکاربرد در Monitoring

| نود | نقش | نحوه استفاده |
|-----|------|-------------|
| `scheduleTrigger` | تریگر کرون | `rule: { interval: "every 10m" }` |
| `cron` | تریگر fixed | `expression: "0 8 * * *"` |
| `n8n` | workflow/execution API | `resource: execution/audit` |
| `httpRequest` | health check | `method: GET, url: "..."` |
| `dataTable` | ذخیره و بازیابی لاگ | `resource: row, operation: get/upsert` |
| `code` | محاسبات | محاسبه staleness, days remaining |
| `if` / `switch` | مسیریابی وضعیت | شرط‌های ۲۰۰/خطا/وقت‌گذشتن |
| `splitInBatches` | پردازش لیست URLها | `batchSize: 1, options: { requestInterval: 100 }` |
| `stopAndError` | خطا برای Error Trigger | پیام خطا با جزئیات |
| `quickChart` | نمودار | `chartType: bar/line/pie` |
| `telegram` / `slack` / `gmail` | نوتیفیکیشن | متفاوت بر اساس urgency |
| `set` | قالب‌بندی پیام | آماده‌سازی متن آلرت |
| `noOp` | مسیر سالم | فقط لاگ بزن و تموم کن |
| `googleSheets` | ذخیره لاگ قابل اشتراک | ساده و همه‌گیر |

---

## ۱۴. تله‌ها و نکات

### 🕳️ آلرت تکراری
**مشکل:** هر بار که workflow اجرا میشه، آلرت می‌فرسته
**راه‌حل:** فیلد `notified` یا `last_alerted_at` توی Data Table بذار و بعد از آلرت مقدارش رو set کن.

### 🕳️ Timeout نامناسب
**مشکل:** health check تا ۳۰ ثانیه منتظر می‌مونه
**راه‌حل:** `timeout` رو بذار `5000` (۵ ثانیه). اگه سایت ۵ ثانیه جواب نداد یعنی مشکل داره.

### 🕳️ False Positive
**مشکل:** سرویس کلاً down نیست، فقط یه لحظه latency داشته
**راه‌حل:** 
- تعداد خطاهای متوالی رو بشمار (escalation pattern)
- `retryOnFail: true` بذار
- threshold رو ببر بالا (مثلاً ۳ بار خطا = آلرت)

### 🕳️ حجم لاگ زیاد
**مشکل:** Data Table پر میشه و کند میشه
**راه‌حل:**
- یه cron شبانه برای پاک کردن رکوردهای قدیمی (> ۳۰ روز)
- فقط errorها رو نگه دار، successها رو پاک کن
- از `returnAll: false` و `limit` استفاده کن

### 🕳️ Schedule Trigger بی‌کیفیت
**مشکل:** یه workflow هر ۵ دقیقه یه API رو ping می‌کنه — بی‌فایده و پرهزینه
**راه‌حل:** 
- مانیتورینگ uptime: هر ۱۰-۱۵ دقیقه کافیه
- مانیتورینگ SSL: روزانه
- مانیتورینگ Data Table: هر ۶ ساعت
- execution health: ساعتی

### 🕳️ Webhook منفرد
**مشکل:** فقط به webhook تکیه کردی و سرویس webhook نفرستاد
**راه‌حل:** همیشه یه Schedule-based backup بذار: "آخرین webhook کی رسید؟ اگه > N ساعت گذشته، cron اجرا کن."

### 🕳️ n8n API Rate Limit
**مشکل:** تعداد executionها زیاده و n8n API throttling می‌کنه
**راه‌حل:**
- از `splitInBatches` با `batchInterval` استفاده کن
- فقط workflowهای مهم رو مانیتور کن (tag: critical)
- از `requestOptions.batching` توی node n8n استفاده کن

---

## ۱۵. معماری‌های نمونه

### معماری A: مانیتورینگ جامع (توصیه‌شده)

```
[Schedule Trigger (hourly)]
    ↓
┌─────────────────────────────────────┐
│  Workflow ۱: Execution Health       │
│  ───────────────────────────────── │
│  n8n → Get All Workflows           │
│  Filter (has schedule/poll trigger) │
│  n8n → Get Last Execution          │
│  Code → Calc Staleness             │
│  IF → Stale?                       │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Workflow ۲: Data Table Check       │
│  ───────────────────────────────── │
│  DataTable → Get unresolved errors  │
│  IF → count > 0?                   │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Workflow ۳: External Health Check  │
│  ───────────────────────────────── │
│  Google Sheets → Read URLs          │
│  Split In Batches                   │
│  HTTP Request → GET + timeout       │
│  IF → status = 200?                 │
└────────────────┬────────────────────┘
                 ↓
           [Merge: تلفیق همه آلرت‌ها]
                 ↓
           [IF: آلرتی هست؟]
            ├── yes → [Telegram: خلاصه ساعتی]
            └── no  → [Data Table: log healthy]
```

### معماری B: Simple Health Check (۵ دقیقه‌ای)

```
[Interval Trigger (every 5m)]
    ↓
[HTTP Request: GET https://api.example.com/health]
    ↓
[IF: status = 200?]
    ├── yes → [No-Op]
    └── no  → [Telegram: "🚨 api.example.com DOWN!"]
```

### معماری C: Daily Report + Chart

```
[Schedule Trigger (daily at 8 AM)]
    ↓
[n8n: execution → getAll (آخرین ۲۴ ساعت)]
    ↓
[Code: محاسبه success/fail rate]
    ↓
[Set: آماده‌سازی داده برای chart]
    ↓
[QuickChart: line chart (success rate در زمان)]
    ↓
[Telegram: ارسال گزارش + نمودار]
```

---

## ۱۶. مقایسه Storage برای لاگ‌ها

| Storage | مزایا | معایب | کی استفاده کنیم |
|---------|-------|-------|---------------|
| **Data Table** | built-in, ساده, upsert داره | query محدود | لاگ داخلی n8n |
| **Google Sheets** | قابل اشتراک, dashboard داره | کند, rate limit | تیم‌های غیرفنی |
| **PostgreSQL** | query قدرتمند, retention | نیاز به credential | مانیتورینگ جدی |
| **File (SpreadsheetFile)** | آفلاین, portable | manual | بکاپ دستی |

---

> 💡 **اصل مهم:** مانیتورینگ باید **کمترین نویز** رو داشته باشه. اگه هر ساعت ۱۰ آلرت می‌گیری، کسی دیگه بهش توجه نمی‌کنه. escalation رو جدی بگیر و thresholdها رو درست تنظیم کن.
