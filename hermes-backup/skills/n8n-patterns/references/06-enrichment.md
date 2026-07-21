# Best Practices: Enrichment

> Technique key: `enrichment`
> غنی‌سازی داده — اضافه کردن جزئیات به داده‌های موجود با ادغام اطلاعات از منابع دیگر

---

## ۱. معرفی

Enrichment یعنی **داده‌ات رو تکمیل کنی** با منابع خارجی. مثلاً یه لیست اسم شرکت داری → URL لینکدینش رو پیدا کن، آدرسش رو پیدا کن، ایمیلش رو پیدا کن.

### چه چیزهایی رو می‌شه enriched کرد؟

| داده ورودی | منبع enrichment | خروجی |
|-----------|----------------|-------|
| اسم شرکت | Apollo, Crunchbase, LinkedIn | domain, revenue, employee count, industry |
| LinkedIn URL | RapidAPI, BrightData | name, location, about, connections |
| IP Address | BigDataCloud, ipapi, ipinfo | country, city, ISP, coordinates |
| آدرس | Google Maps API, SerpAPI | coordinates, place ID, phone, rating |
| وبسایت شرکت | ScrapingBee + AI Agent | business model, products, ICP, value prop |
| ایمیل | Mailcheck, ZeroBounce | valid/invalid, disposable, role-based |
| نام شخص | LinkedIn, Apollo | job title, department, company, location |
| cryptocurrency data | Binance API + Airtable | funding fees, position, mark price, liquidation |

---

## ۲. زیرساخت کلی

```
[Source (Google Sheets / Data Table / Webhook / Form)]
    ↓
[Split In Batches: پردازش یکی‌یکی]
    ↓
[HTTP Request / API: دریافت داده از منبع سوم]
    ↓
[Code / Set: تبدیل و نرمال‌سازی]
    ↓
[Merge: ادغام داده اصلی + enriched]
    ↓
[Output: Google Sheets / Data Table / Response / Airtable / Supabase]
```

### تریگرهای رایج

| تریگر | کی |
|-------|-----|
| `scheduleTrigger` | enrichment دوره‌ای (شبانه) |
| `googleSheetsTrigger` | وقتی ردیف جدید به شیت اضافه شد |
| `formTrigger` | کاربر فرم ارسال کرد |
| `webhook` | سیستم خارجی درخواست enrichment داد |
| `manualTrigger` | enrichment دستی |
| `executeWorkflowTrigger` | workflow دیگه صدا زد |

---

## ۳. پترن ۱: Lead Enrichment با Apollo API + AI

**منطق:** اسم شرکت داری → domain, decision maker, department رو پیدا کن.

```
[Google Sheets: خواندن شرکت‌های پردازش‌نشده]
    ↓
[IF: domain وجود داره؟]
    ├── no  → [HTTP: Apollo company search → پیدا کردن domain]
    │         ↓
    │        [Google Sheets: update دامین]
    └── yes → ادامه
    ↓
[HTTP: Apollo organization enrichment]
    ↓
[AI: خلاصه کردن business شرکت (GPT-4o-mini)]
    ↓
[Split In Batches (batch: 1000)]
    ↓
[HTTP: Apollo people search (decision makers)]
    ↓
[Split Out: جداسازی افراد]
    ↓
[AI: تشخیص دپارتمان (از روی job title)]
    ↓
[Split In Batches (batch: 10)]
    ↓
[HTTP: Apollo bulk people enrichment]
    ↓
[Google Sheets: append/update کانتکت‌ها]
```

**نودهای کلیدی:**
- `httpRequest` → Apollo API search + enrichment
- `googleSheets` → خواندن و نوشتن داده
- `openAi` / `lmChat*` → تشخیص دپارتمان و خلاصه‌سازی
- `splitInBatches` → batch کردن API calls
- `splitOut` → جدا کردن people از array
- `merge` → تلفیق داده‌ها
- `filter` → حذف رکوردهای پردازش‌شده

> ⚠️ Apollo API rate limit: از `splitInBatches` با `batchInterval` استفاده کن
> ⚠️ همیشه یه فیلد `enriched` boolean بذار تا دوبار پردازش نشن

---

## ۴. پترن ۲: Company Enrichment با AI Agent + Web Scrape

**منطق:** اسم شرکت + وبسایت داری → AI بره سایت رو بگرده و اطلاعات ساخت‌یافته برگردونه.

```
[Google Sheets: خواندن ردیف‌های pending]
    ↓
[Split In Batches]
    ↓
[AI Agent: شرکت X رو تحقیق کن]
    │
    ├── Tool 1: Sub-workflow (ScrapingBee → Markdown)
    │   وبسایت شرکت رو scrape کن و به متن تبدیل کن
    │
    └── Tool 2: SerpAPI (Google Search)
        موردکاوی و اطلاعات تکمیلی
    │
    ↓
[AI: استخراج structured JSON]
    ↓
[Output Parser: enforce schema]
    ↓
[Set: آماده‌سازی برای نوشتن]
    ↓
[Google Sheets: update ردیف]
```

**خروجی AI parser:**
```json
{
  "business_area": "Fintech",
  "products": ["payment gateway", "fraud detection"],
  "value_proposition": "کاهش شارژبک به ۰.۵٪",
  "business_model": "SaaS + per-transaction",
  "target_customers": ["SME", "enterprise"],
  "has_case_studies": true,
  "data_sufficient": true
}
```

**نودها:**
- `agent` + `lmChatOpenAi` → AI Agent اصلی
- `toolWorkflow` → sub-workflow برای scrape
- `outputParserStructured` → JSON schema
- `httpRequest` → ScrapingBee / ScrapingFish
- `markdown` → تبدیل HTML به Markdown
- `googleSheets` → ذخیره

---

## ۵. پترن ۳: LinkedIn Profile Enrichment

**منطق:** LinkedIn URL داری → پروفایل کامل رو بگیر.

```
[Google Sheets: خواندن LinkedIn URLها]
    ↓
[Filter: حذف enriched شده‌ها]
    ↓
[HTTP: RapidAPI / BrightData → LinkedIn profile API]
    ↓
[Wait: polling تا آماده شدن دیتا]
    ↓
[IF: data ready?]
    ├── no  → [Wait loop]
    └── yes → [Code: استخراج فیلدهای مهم]
    ↓
[Merge: با داده اصلی]
    ↓
[Google Sheets: upsert]
```

**داده‌هایی که می‌گیریم:**
- name, headline, location
- about section
- experience (company, title, duration)
- education
- skills
- recent posts

**APIهای موجود:**

| سرویس | نود | محدودیت |
|-------|-----|---------|
| RapidAPI LinkedIn | `httpRequest` | پولی، نیاز به اشتراک |
| BrightData LinkedIn | `httpRequest` | پولی، polling داره |
| Apollo People Search | `httpRequest` | محدودیت رایگان |
| N8N-CUSTOM | `executeWorkflow` | sub-workflow اختصاصی |

---

## ۶. پترن ۴: IP Geolocation Enrichment

**منطق:** IP آدرس داری → موقعیت جغرافیایی و ISP رو پیدا کن.

```
[Webhook / MCP Trigger: دریافت IP]
    ↓
[HTTP: BigDataCloud / ipapi / ipinfo]
    ↓
[Code: استخراج فیلدهای مهم]
    ↓
[Return: JSON غنی‌شده]
```

**APIهای موجود:**

| سرویس | خروجی | رایگان |
|-------|-------|--------|
| BigDataCloud | country, city, coordinates, ISP, hazard report | ✅ محدود |
| ip-api | country, city, ISP, lat/lon | ✅ |
| ipinfo.io | country, city, org, ASN | ✅ محدود |
| abstractapi | country, city, timezone, currency | ❌ |

**کاربردها:**
- نمایش موقعیت کاربر در dashboard
- تشخیص VPN/proxy
- شخصی‌سازی محتوا بر اساس کشور
- Fraud detection

---

## ۷. پترن ۵: Financial Data Enrichment (API + Storage)

**منطق:** داده مالی داری → با API خارجی غنی‌سازی کن و توی Airtable/DataTable ذخیره کن.

```
[Schedule Trigger]
    ↓
[HTTP: Binance API (funding fees)]
    ↓
[HTTP: Binance API (position risk)]
    ↓
[Airtable: دریافت token data]
    ↓
[Aggregate: تلفیق fee + position + token]
    ↓
[Merge: بر اساس symbol]
    ↓
[IF: token ID وجود داره؟]
    ├── no  → [Airtable: ایجاد token جدید]
    └── yes → ادامه
    ↓
[Split Out: یکی‌یکی funding records]
    ↓
[Airtable: insert/update funding statement]
```

**نودهای کلیدی:**
- `crypto` → HMAC signature برای API احراز هویت
- `airtable` → ذخیره و بازیابی داده
- `aggregate` → تلفیف چند source
- `merge` → join روی symbol

---

## ۸. پترن ۶: Multi-Source AI Enrichment (RAG)

**منطق:** کاربر یه سوال می‌پرسه → چند تا source مختلف رو بگرد و با AI جواب بده.

```
[Webhook: دریافت query کاربر]
    ↓
[GPT-4: پارس کردن query به پارامترهای ساخت‌یافته]
    ↓
┌────────────── Parallel ──────────────┐
│  [Gmail: جستجوی ایمیل‌ها]            │
│  [Google Calendar: جستجوی رویدادها]  │
│  [Google Photos: جستجوی عکس‌ها]      │
└────────────────┬─────────────────────┘
                 ↓
          [Merge: تلفیق نتایج]
                 ↓
          [Code: فیلتر و رتبه‌بندی]
                 ↓
          [Claude: تولید پاسخ conversational]
                 ↓
          [Webhook Response: JSON]
```

**این چجوری enrichment حساب میشه؟** چون داری داده‌های خام (raw query) رو با **ادغام چند منبع مختلف** غنی‌سازی می‌کنی تا یه پاسخ کامل بدی.

---

## ۹. پترن ۷: Google Maps Place Enrichment

**منطق:** URL جستجوی Google Maps داری → اطلاعات کامل placeها رو استخراج کن.

```
[Google Sheets: خواندن URLهای جستجو]
    ↓
[Code: استخراج keyword + coordinates از URL]
    ↓
[HTTP: SerpAPI Google Maps API]
    ↓
[Code: پردازش pagination]
    ↓
[IF: صفحه بعدی هست؟]
    ├── yes → [ادامه pagination loop]
    └── no  → ادامه
    ↓
[Merge + Split Out: تلفیق همه نتایج]
    ↓
[Filter: حذف تکراری‌ها]
    ↓
[Google Sheets: upsert]
    ↓
[Google Sheets: update status=success]
```

**داده‌های استخراجی:**
- name, phone, website
- rating, reviews count
- address, coordinates
- place_id, types
- opening hours

---

## ۱۰. پترن ۸: Social Media Profile Extraction

**منطق:** وبسایت شرکت داری → لینک‌های شبکه‌های اجتماعیش رو پیدا کن.

```
[Supabase: خواندن شرکت‌ها]
    ↓
[AI Agent: کاوش وبسایت برای لینک‌های اجتماعی]
    │
    ├── Tool 1: Sub-workflow (get text content)
    │   صفحه HTML → Markdown → متن
    │
    └── Tool 2: Sub-workflow (get all URLs)
        استخراج همه hrefها → فیلتر → normalize
    │
    ↓
[Output Parser: JSON ساخت‌یافته]
    ↓
[Code: پردازش و validate]
    ↓
[Supabase: insert داده‌های غنی‌شده]
```

**خروجی:**
```json
{
  "platforms": [
    {"name": "linkedin", "url": "https://linkedin.com/company/..."},
    {"name": "twitter", "url": "https://twitter.com/..."},
    {"name": "instagram", "url": "https://instagram.com/..."}
  ]
}
```

---

## ۱۱. پترن ۹: Enrichment Pipeline با Webhook (برای Sub-workflow)

**منطق:** یه workflow دیگه enrichment رو صدا می‌زنه و نتیجه رو می‌گیره.

```
┌─ Caller Workflow ─┐
│  داده اصلی دارم    │
│  نیاز به enrich   │
└────────┬──────────┘
         │ executeWorkflow
         ▼
┌─ Enrichment Sub-workflow ─┐
│  [Execute Workflow Trigger] │
│  ↓                         │
│  [IF: LinkedIn URL داره؟]  │
│   ├── yes → [Sub-workflow: extract LinkedIn data] │
│   └── no  → [Sub-workflow: find LinkedIn URL]    │
│  ↓                         │
│  [IF: enrichment موفق؟]     │
│   ├── yes → [Sub-workflow: calc ICP score]       │
│   └── no  → [Default values]                     │
│  ↓                         │
│  [Merge: همه داده‌ها]      │
│  ↓                         │
│  [Return: JSON غنی‌شده]    │
└───────────────────────────┘
```

**مزایا:**
- workflowهای مختلف می‌تونن یه enrichment sub-workflow مشترک صدا بزنن
- تغییرات enrichment فقط توی یه جا اعمال می‌شه
- می‌تونی rate limiting مرکزی داشته باشی

---

## ۱۲. پترن ۱۰: Funding / News Data Enrichment (Crunchbase)

**منطق:** هر روز برو ببین چه شرکت‌هایی funding گرفتن و توی شیت ذخیره کن.

```
[Schedule Trigger (daily 8 AM)]
    ↓
[HTTP: Crunchbase API (funding rounds)]
    │  params: location, industry, date range
    ↓
[Code: استخراج فیلدها + format investor list]
    ↓
[HTTP: Company info API (enrichment)]
    │  website, linkedin, employee count, country
    ↓
[Code: استخراج فیلدهای اضافی]
    ↓
[Merge: داده‌های اصلی + enriched]
    ↓
[Google Sheets: append/update]
```

**کاربردها:**
- لیست startupهای فعال در حوزه خاص
- رصد رقبا
- شناسایی روندهای سرمایه‌گذاری
- sales prospecting

---

## ۱۳. نودهای پرکاربرد در Enrichment

| نود | نقش |
|-----|------|
| `httpRequest` | API calls اصلی (Apollo, Crunchbase, RapidAPI, BrightData, SerpAPI, ...) |
| `code` | تبدیل داده، extract فیلدها، format کردن |
| `set` | آماده‌سازی فیلدها برای نوشتن |
| `merge` | ادغام داده اصلی + enriched |
| `filter` | حذف رکوردهای پردازش‌شده |
| `if` / `switch` | مسیریابی بر اساس وجود/عدم وجود داده |
| `splitInBatches` | batch کردن API calls (rate limit) |
| `splitOut` | جدا کردن آیتم‌های array |
| `aggregate` | جمع‌آوری نتایج برای bulk write |
| `googleSheets` | منبع ورودی/خروجی |
| `airtable` / `supabase` / `postgres` | storage جایگزین |
| `dataTable` | storage داخلی n8n |
| `wait` | polling برای APIهای ناهمزمان (BrightData) |
| `executeWorkflowTrigger` | sub-workflow enrichment |
| `agent` + `lmChat*` | AI enrichment با web research |
| `outputParserStructured` | JSON schema از AI |
| `toolWorkflow` | scrape + extract در AI Agent |
| `removeDuplicates` | حذف رکوردهای تکراری |
| `itemLists` | عملیات list (sort, limit, paginate) |

---

## ۱۴. جدول APIهای enrichment

| API/Source | چه چیزی میده | rate limit | هزینه | احراز هویت |
|-----------|--------------|------------|-------|-----------|
| **Apollo** | company, people, enrichment | 100/day free | 💰 | API Key |
| **Crunchbase** | funding rounds, investors | 200/day free | 💰 | API Key |
| **BrightData** | LinkedIn profiles | بر اساس plan | 💰💰💰 | API Key |
| **RapidAPI LinkedIn** | LinkedIn profile data | بر اساس plan | 💰 | RapidAPI Key |
| **SerpAPI** | Google Maps, Google Search | 100/month free | 💰 | API Key |
| **BigDataCloud** | IP geolocation | محدود رایگان | 🆓 | API Key |
| **ip-api** | IP geolocation | ~45/min | 🆓 | — |
| **ScrapingBee** | web scraping | 1000 credits | 💰 | API Key |
| **ScrapingFish** | web scraping | 1000 credits | 💰 | API Key |
| **OpenAI / Anthropic** | AI analysis, enrichment | حسب plan | 💰💰 | API Key |
| **Binance** | crypto price, funding fees | 1200/weight/min | 🆓 | API Key + Secret |
| **Mailcheck** | email validation | 100/day free | 💰 | API Key |

---

## ۱۵. تله‌ها و نکات

### 🕳️ API Rate Limit
**مشکل:** API بعد از N تا درخواست ۴۲۹ میده
**راه‌حل:**
- `splitInBatches` + `batchInterval` (مثلاً ۱۰۰ms بین هر batch)
- صف بندی با Wait node
- رزرو API keyهای چندگانه

### 🕳️ API Key Hardcoded
**مشکل:** API key توی expression نوشته و امن نیست
**راه‌حل:** از credentialهای n8n استفاده کن (نه متن باز)

### 🕳️ Polling نامحدود
**مشکل:** BrightData یا APIهای ناهمزمان رو تا بی‌نهایت poll می‌کنی
**راه‌حل:**
- `maxTries` بذار (مثلاً ۱۰ بار)
- `wait` با timeout معقول
- اگه داده نیومد → fallback یا لاگ خطا

### 🕳️ داده تکراری
**مشکل:** هربار که workflow اجرا میشه دوباره enrich می‌کنه
**راه‌حل:**
- فیلد `enriched_at` یا `enriched` بذار
- `filter` بزن فقط رکوردهای enriched=false
- `googleSheets` با `upsert` (appendOrUpdate)

### 🕳️ AI Hallucination
**مشکل:** AI اطلاعات اشتباه از وبسایت استخراج می‌کنه
**راه‌حل:**
- `outputParserStructured` با schema محدود
- `data_sufficient` و `confidence` فیلد
- validation با `code` node

### 🕳️ Sub-workflow خطا
**مشکل:** sub-workflow enrichment fail میشه و داده اصلی از دست می‌ره
**راه‌حل:**
- `continueOnFail: true` روی executeWorkflow
- `errorWorkflow` جدا برای enrichment
- fallback: اگر enrichment fail شد → داده اصلی رو بدون enrichment ذخیره کن

### 🕳️ حجم داده بالا
**مشکل:** ۱۰۰۰۰ شرکت داری و enrichment slow
**راه‌حل:**
- processing رو شبانه بذار (cron)
- batch size مناسب (۱۰-۵۰)
- فقط enrichment priority بالا (مثلاً شرکت‌های active)

---

## ۱۶. معماری‌های نمونه

### معماری A: Enrichment Pipeline کامل (توصیه‌شده)

```
[Source: Google Sheets / Data Table]
    ↓
[Filter: فقط enriched=false]
    ↓
[Split In Batches (batch: 50)]
    ↓
┌─────────────────────────────────────────┐
│  Step 1: Basic Enrichment              │
│  HTTP (Apollo company search)          │
│  → domain, revenue, industry           │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Step 2: LinkedIn Enrichment           │
│  HTTP (BrightData / RapidAPI)          │
│  → people, titles, locations           │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Step 3: AI Analysis                   │
│  Agent + toolWorkflow (scrape website) │
│  → business model, products, ICP       │
└────────────────┬────────────────────────┘
                 ↓
[Merge: تلفیق داده اصلی + همه enrichments]
    ↓
[Output: Google Sheets / Data Table / Airtable]
```

### معماری B: Enrichment سبک (API-only, بدون AI)

```
[Google Sheets Trigger: ردیف جدید]
    ↓
[HTTP: Apollo company enrich]
    ↓
[IF: success?]
    ├── yes → [Google Sheets: update]
    └── no  → [No-Op: بعداً Retry]
```

### معماری C: AI Enrichment (برای داده‌های کیفی)

```
[Webhook: درخواست enrichment]
    ↓
[Agent: تحقیق شرکت]
    ├── scrape website (toolWorkflow)
    └── google search (SerpAPI)
    ↓
[Output Parser: structured JSON]
    ↓
[Set: format خروجی]
    ↓
[Respond To Webhook: JSON]
```

### معماری D: Bulk Enrichment شبانه

```
[Schedule Trigger (daily 2 AM)]
    ↓
[Data Table: getAll enriched=false]
    ↓
[Split In Batches (batch: 20, interval: 500ms)]
    ↓
[HTTP: API enrichment]
    ↓
[IF: success?]
    ├── yes → [Data Table: upsert enriched_data + enriched_at]
    └── no  → [Data Table: update attempts + error_reason]
    ↓
[Telegram: گزارش روزانه] — "از ۲۰۰ شرکت، ۱۸۵ تا enrich شدن، ۱۵ تا fail"
```

---

> 💡 **اصل مهم:** enrichment هزینه داره (API calls + AI tokens). همیشه:
> 1. فقط داده‌های نیازمند enrich رو پردازش کن (enriched=false)
> 2. priority بذار (داده‌های important اول)
> 3. rate limit رو رعایت کن
> 4. fallback داشته باش (اگه API fail شد → داده خام رو ذخیره کن)
