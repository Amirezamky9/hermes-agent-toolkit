# Module Templates — n8n-planner (v4.0)

> Load with: `skill_view(name='n8n-planner', file_path='references/module-templates.md')`

این رفرنس شامل تمپلت‌های ماژول‌های رایج هست. از این‌ها **الگو بگیر** ولی همیشه بر اساس نیاز خاص کاربر شخصی‌سازی کن.

---

## 1. Telegram Bot — Complete Module Map

### Common Telegram Bot Architecture

```
                         ┌─────────────────────────┐
                         │   Telegram Webhook      │
                         │       (Trigger)         │
                         └───────────┬─────────────┘
                                     │
                         ┌───────────▼─────────────┐
                         │     Core Router         │
                         │  (Switch — Intent       │
                         │   Classification)       │
                         └───┬───┬───┬───┬───┬────┘
                             │   │   │   │   │
              ┌──────────────┘   │   │   │   └──────────────┐
              ▼                  ▼   ▼   ▼                  ▼
       ┌────────────┐   ┌────────────┐   ┌────────────┐
       │ Module 1   │   │ Module 2   │   │ Module N   │
       │ (Welcome)  │   │ (Shop)     │   │ (Support)  │
       └──────┬─────┘   └──────┬─────┘   └──────┬─────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Data Persistence  │
                    │  (Data Table / DB)  │
                    └─────────────────────┘
```

### ماژول‌های استاندارد ربات تلگرام

**Core Router** — ضروری برای همه ربات‌ها
```
Type: Switch
Input: پیام کامل کاربر (text, callbackQuery, command)
Logic:
  - اگر پیام با "/" شروع شد → دستور (command routing)
  - اگر callbackQuery بود → دکمه (button routing)
  - اگر متن معمولی بود → intent detection با regex یا AI
Output: Integer (شماره شاخه Switch)
```

**Welcome & Onboarding**
```
Trigger: /start یا عضو جدید
Steps:
  1. Check if user exists in DB → خوش‌آمد یا ثبت‌نام مجدد؟
  2. If new → ذخیره userId, username, joinDate
  3. ارسال پیام خوش‌آمدگویی با دکمه‌های اصلی
  4. آیا کاربر رو به گروه دعوت کنه؟
Storage: Data Table "users"
```

**User Management**
```
Actions: 
  - update_profile: ویرایش نام/شماره/آدرس
  - view_profile: نمایش اطلاعات کاربر
  - delete_account: حذف حساب
  - set_preferences: تنظیمات اعلان‌ها
Storage: Data Table "users"
Relations: orders, messages
```

**Authorization Gate**
```
Purpose: بررسی دسترسی کاربر قبل از سرویس‌دهی
Methods:
  1. Check group membership (Telegram API getChatMember)
  2. Check user level in DB (admin / premium / free)
  3. Check rate limit (X requests per minute)
Output: دو مسیر — allow / deny
```

**Product Catalog**
```
نوع: نمایش محصولات
Steps:
  1. Fetch products from storage (با cache)
  2. Format as Inline Keyboard (دسته‌بندی شده)
  3. Handle callback: next page / product details / add to cart
Storage: Data Table "products"
          Data Table "categories"
Cache: بله (محصولات کمتغییر)
Nodes: Telegram + Data Table (read) + IF (pagination)
```

**Shopping Cart**
```
Steps:
  1. Add: userId + productId → cart.items[]
  2. View: نمایش محتویات سبد
  3. Edit: تغییر تعداد / حذف آیتم
  4. Checkout: انتقال به Order
Storage: Data Table "carts" (موقت)
         یا Session/Context (برای سبد ساده)
```

**Order Management**
```
Steps:
  1. Validate: موجودی کافی هست؟
  2. Create: orderId = generate(), save order
  3. Update: کاهش موجودی محصول
  4. Clear Cart: حذف سبد خرید فعلی
  5. Notify: ارسال پیام به ادمین (سفارش جدید!)
  6. Confirm: ارسال رسید به کاربر
Storage: Data Table "orders" (اصلی)
          Data Table "order_items"
Relations: users, products, payments
Error: continueErrorOutput, ذخیره در dead-letter queue
```

**AI Chat Support**
```
Trigger: درخواست پشتیبانی
Steps:
  1. Load chat history from Memory
  2. AI Agent with system message (راهنمای فروشگاه)
  3. If AI can't answer → escalate to admin
  4. Save conversation to Memory
Nodes: 
  - Telegram Trigger (چندمنظوره)
  - Chat Memory (Window Buffer Memory یا Postgres Chat Memory)
  - AI Agent (OpenRouter / LangChain)
  - Send Message
Credentials: openRouterApi
```

**Content Broadcast (Cron)**
```
Trigger: Schedule Trigger (مثلاً هر روز ۱۰ صبح)
Steps:
  1. Fetch content from data source
  2. Generate image (kie.ai / DALL-E)
  3. Format with inline buttons
  4. Send to channel or broadcast to users
Storage: Data Table "publications" (تاریخچه)
Credentials: kie-api, telegramApi
```

**Admin Dashboard**
```
Trigger: /admin (با بررسی سطح دسترسی)
Sections:
  - user_list: لیست کاربران با pagination
  - order_stats: آمار سفارشات (امروز / هفته / ماه)
  - broadcast: ارسال پیام همگانی
  - settings: تغییر تنظیمات ربات
Access: فقط کاربران با role=admin
```

---

## 2. Webhook / API — Module Map

### معماری استاندارد Webhook

```
[HTTP Request (Trigger)]
       │
       ▼
[Auth Layer] → 401 Unauthorized
       │
       ▼
[Request Validator] → 400 Bad Request
       │
       ▼
[Rate Limiter] → 429 Too Many Requests
       │
       ▼
[Core Router] → Endpoint Detection
       │
       ├── POST /order → [Order Handler]
       ├── GET /products → [Catalog (Cache)]
       └── POST /support → [AI Support]
       │
       ▼
[Response Formatter] → Unified JSON Response
       │
       ▼
[HTTP Response] (200 / 201)
```

**ماژول‌های استاندارد:**

**Auth Layer**
```
Type: Code Node یا HTTP Request
Methods:
  - API Key در Header
  - JWT Token (verify signature)
  - Basic Auth
Output: Two branches — pass / fail
Notes: تنظیم onError برای return 401
```

**Rate Limiter**
```
Type: Data Table + Code Node
Logic:
  1. Increment counter در Data Table (key = IP or userId)
  2. If counter > limit → return 429
  3. Reset counter هر دقیقه (با TTL یا Cron)
Storage: Data Table "rate_limits" با TTL
```

**Cache Layer**
```
Purpose: کش کردن پاسخ‌های پرتکرار
Implementation Options:
  - Data Table (کش ساده با TTL دستی)
  - Redis node (کش پیشرفته با TTL خودکار)
  - Context/State (کش درون ورک‌فلو)
Use: همیشه قبل از پردازش اصلی چک کن
```

---

## 3. Cron / Scheduled Job — Module Map

### معماری استاندارد Cron

```
[Schedule Trigger]
       │
       ▼
[Data Fetcher] (API / RSS / DB)
       │
       ▼
[Transformer/Processor] (Code / AI)
       │
       ▼
[Format Converter]
       │
       ▼
[Publisher] (Telegram / Email / API)
       │
       ▼
[History Logger] (Data Table)
       │
   [Error → Notifier]
```

**ماژول‌های استاندارد Cron:**

**Schedule Trigger**
```
Options:
  - Every N minutes (mqtt / interval)
  - Cron expression (0 9 * * * = هر روز ۹ صبح)
  - Specific time (ISO date for one-shot)
```

**Data Fetcher**
```
Methods:
  - HTTP Request (API call with pagination)
  - RSS Feed (XML/JSON parser)
  - Database Query
Error: retry 3 times, then skip cycle
```

**AI Processor**
```
Purpose: خلاصه‌سازی / ترجمه / تولید محتوا
Input: داده خام از فچر
Output: محتوای پردازش شده
Nodes: AI Agent or HTTP Request (OpenRouter API)
```

---

## 4. Cross-Module Patterns

### Error Handler Pattern (قابل استفاده در همه ماژول‌ها)
```
[Main Logic] 
       │
   onError → [Error Handler Node]
                │
                ├── Notify Admin (Telegram)
                ├── Log to Data Table "error_logs"
                └── Send fallback to user

Node Settings (برای همه نودهای بحرانی):
  onError: continueErrorOutput
  retryOnFail: true
  maxTries: 3
  waitBetweenTries: 2000
```

### Cache-Aside Pattern
```
[Request]
       │
       ▼
[Check Cache] ── hit ──► [Return Cached]
       │
      miss
       ▼
[Fetch Live Data] ──► [Update Cache] ──► [Return]
       │
       ▼
[Refresh Cache] (بک‌گراند با کرون مجزا)
```

### Saga Pattern (برای تراکنش‌های چند-ماژولی)
```
Module A: Create Order
    ↓ ok
Module B: Deduct Stock
    ↓ fail
Module C: (rollback) → Notify Admin
    ↓
Compensating: اگر B failed → A را rollback کن (حذف سفارش)
```

---

## 5. Module Count Guidelines

| Complexity | مثال | ماژول‌ها | نودها |
|-----------|------|---------|-------|
| ساده | ارسال پیام تکی، فوروارد دیتا | 2-4 | 4-8 |
| متوسط | ربات تلگرام با ۲-۳ بخش | 5-8 | 12-25 |
| پیچیده | ربات فروشگاهی کامل | 10-15 | 30-50 |
| خیلی پیچیده | سیستم مدیریت سازمانی | 15-25 | 50-100+ |

> **قانون سرانگشتی:** اگه کاربر "چندین بخش" یا "چند نوع کاربر" یا "چند کانال خروجی" داره → حداقل ۸ ماژول.

---

## 6. Data Flow Notations

برای نمایش جریان داده بین ماژول‌ها از این نمادها استفاده کن:

```
[A] ──► [B]          : A به B یک‌طرفه
[A] ◄──► [B]         : دوطرفه (request-response)
[A] ──X──► [B]       : خطا در A → B
[A] ──► [B] ──► [C]  : زنجیره

[Trigger]
    │
    ├── route1 ──► [Module A]
    │
    └── route2 ──► [Module B] ──► [Module C]
```

برای **ماژول‌های ترکیبی** (Composite Modules) که از چند ماژول فرعی تشکیل شدن:

```
[Authorization Gate] ── ترکیبی از:
    ├── [Group Check] + [Level Check] + [Rate Limit]
    │
    └── خروجی: منفرد (pass/fail با دلیل)
```
