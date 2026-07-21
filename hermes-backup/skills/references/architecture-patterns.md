# Architecture Patterns — n8n-planner (v3.0)

> Load with: `skill_view(name='n8n-planner', file_path='references/architecture-patterns.md')`

---

## 1. Hub-and-Spoke (Orchestrator Core)

**الگوی اصلی** — مناسب ورک‌فلوهای چند-ماژول.

```
                    ┌──────────────┐
                    │   Entry      │
                    │   Point      │
                    │  (Trigger)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Orchestrator  │
                    │    Core       │
                    │  (Switch)     │
                    └──┬───┬───┬───┘
                       │   │   │
              ┌────────┘   │   └────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ Module 1 │ │ Module 2 │ │ Module N │
       └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │   Response   │
                    │    Output    │
                    └──────────────┘
```

**کاربرد:** ورک‌فلوهایی که چندین مسیر مجزا دارن (ربات تلگرام با بخش‌های مختلف، داشبورد مدیریت).

**مزایا:**
- مقیاس‌پذیری — ماژول‌ها مستقل هستن
- قابلیت تست مجزا
- افزودن ماژول جدید بدون شکستن بقیه

---

## 2. Pipeline (Linear Chain)

**الگوی خطی** — مناسب ورک‌فلوهای تک‌منظوره با مراحل متوالی.

```
[Trigger] → [Node 1] → [Node 2] → [Node 3] → [Output]
```

**کاربرد:** پردازش فایل (PDF استخراج → خلاصه‌سازی → ذخیره)، ایمیل اتوماسیون ساده.

---

## 3. Fan-Out / Broadcast

**الگوی پخش همزمان** — یک ورودی به چندین خروجی موازی.

```
                ┌──────────────┐
                │   Trigger    │
                └──────┬───────┘
                       │
                ┌──────▼───────┐
                │    Split     │
                └──┬───┬───┬───┘
                   │   │   │
       ┌───────────┘   │   └───────────┐
       ▼               ▼               ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Post to  │   │ Post to  │   │ Save to  │
│ Telegram │   │ Twitter  │   │ Database │
└──────────┘   └──────────┘   └──────────┘
```

**کاربرد:** تولید محتوا و انتشار در چند پلتفرم.

---

## 4. Aggregator / Collector

**الگوی تجمیع** — چند ورودی به یک خروجی واحد.

```
┌──────────┐
│ Source 1 ├──┐
└──────────┘  │   ┌──────────────┐
              ├──►│  Merge/      │
┌──────────┐  │   │  Aggregate   │──►[Output]
│ Source 2 ├──┘   └──────────────┘
└──────────┘
```

**کاربرد:** جمع‌آوری داده از چند API، گزارش‌گیری تلفیقی.

---

## 5. Error Handler Pattern

برای هر ماژول مهم، یک مسیر خطا در نظر بگیر:

```
[Switch] ── success ──► [Main Logic] ──► [Success Output]
         │
         └── error ──► [Error Handler] ──► [Notify Admin]
```

بهترین روش:
- نودها: `set onError: "continueErrorOutput"` برای ادامه مسیر خطا
- یک نود Notify که به تلگرام/ایمیل ادمین گزارش خطا بده

---

## 6. Session Memory Pattern

برای ربات‌های چت با حافظه مکالمه:

```
[Telegram Trigger]
       │
       ▼
[Chat Memory] ◄──── نگهداری تاریخچه
       │
       ▼
[AI Agent] ◄──── context از حافظه
       │
       ▼
[Memory Saver] ────► ذخیره پاسخ جدید
       │
       ▼
[Send Message]
```

---

## 7. Data Persistence Patterns

| Storage Type | بهترین ابزار n8n | کاربرد |
|-------------|------------------|--------|
| Data Table | `Data Table` node | داده‌های ساختاریافته ساده |
| PostgreSQL | `Postgres` node | داده‌های پیچیده با رابطه |
| Google Sheets | `Google Sheets` node | داده‌های قابل اشتراک |

---

## 8. Credential Mapping

هر نودی که به API خارجی وصل میشه، یک credential نیاز داره:

| Credential Type | Nodes Using It |
|----------------|----------------|
| `telegramApi` | Telegram Trigger, Send Message |
| `httpHeaderAuth` | HTTP Request (kie.ai, etc.) |
| `openRouterApi` | OpenAI / LangChain nodes |
| `postgres` | Postgres nodes |
| `gmailOAuth2` | Email send, Read |
| `slackApi` | Slack nodes |

---

## انتخاب معماری مناسب

| اگه کاربر می‌خواد... | الگو |
|---------------------|------|
| ربات چت چندمنظوره | **Hub-and-Spoke** |
| یه کار ساده (API بزنه و ذخیره کنه) | **Pipeline** |
| محتوا رو چند جا منتشر کنه | **Fan-Out** |
| از چند منبع داده جمع کنه | **Aggregator** |
| ترکیبی از چند الگو | **Hub-and-Spoke** (انعطاف‌پذیرترین) |

---

## 📝 Full YAML Plan Example

> This is a reference example showing ALL required sections of the output YAML.

```yaml
# n8n-wfb-coffee-bot-plan.yaml
status: "success"
phase: "2-plan"
agent: "n8n-planner"
version: "5.0.0"

summary: |
  معماری Hub-and-Spoke برای ربات تلگرام مدیریت سفارش قهوه.
  ۱۲ ماژول مجزا که توسط Core Router به هم متصل شدن.

workflow_name: "ربات مدیریت سفارش قهوه تلگرام"
architecture_pattern: "Hub-and-Spoke (Orchestrator Core + 11 Modules)"

design_decisions:
  - decision: "Hub-and-Spoke انتخاب شد چون تعداد ماژول‌ها زیاده و نیاز به مسیریابی مجزا دارن"
  - decision: "Switch به جای IF استفاده شد چون مقیاس‌پذیرتر و خواناتر هست"
  - decision: "Authorization Gate جدا شد تا بتونیم ازش برای همه ماژول‌ها استفاده کنیم"
  - decision: "Cache برای منوی محصولات استفاده میشه چون دیتاش تغییر چندانی نداره"

data_flow:
  entry: "Telegram Trigger (Webhook)"
  router: "Switch (Core Router)"
  flow_description: |
    کاربر پیام میده → Core Router تشخیص میده کدوم ماژول →
    Authorization بررسی میکنه → ماژول اجرا میشه → خروجی به کاربر

    مسیرهای اصلی:
    - /start → Welcome Module
    - سفارش جدید → Auth Gate → Cart → Order → Payment
    - پشتیبانی → AI Support
    - ادمین → Admin Panel
    - کانال → Content Broadcast (Cron Job مجزا)

modules:
  - name: "Core Router"
    responsibility: "تشخیص intent کاربر و مسیریابی"
    type: "Switch (چند شاخه)"
    input: "متن کامل پیام کاربر"
    output: "مسیریابی به ماژول مناسب"
    nodes: 2
    notes: "از Switch با Rule بر اساس محتوای پیام استفاده کن"

  - name: "User Management"
    responsibility: "ثبت‌نام، پروفایل، تنظیمات"
    type: "CRUD"
    input: "userId, action"
    output: "داده‌های کاربر"
    data_table: "users"
    nodes: 5

  - name: "Authorization Gate"
    responsibility: "بررسی دسترسی کاربر"
    type: "اعتبارسنجی ترکیبی"
    input: "userId"
    output: "مجاز / غیرمجاز"
    nodes: 3
    credentials: ["telegramApi"]

  - name: "Order Management"
    responsibility: "ثبت و پیگیری سفارش"
    type: "تراکنشی"
    input: "userId, productId, quantity"
    output: "orderId, status"
    data_table: "orders"
    nodes: 6
    depends_on: ["User Management", "Product Catalog", "Notification"]

nodes:
  - name: "Core Router"
    type: "n8n-nodes-base.switch"
    source: "new"
    module: "Core"
    purpose: "مسیریابی پیام‌های کاربر به ماژول‌ها"
    config_notes: |
      mode: 'rules'
      rules: [
        { name: 'start', regex: '/start', output: 0 },
        { name: 'order', regex: 'سفارش|خرید', output: 1 },
        { name: 'support', regex: 'پشتیبانی|help', output: 2 },
        { name: 'admin', regex: '/admin', output: 3 }
      ]
    connections: ["Telegram Trigger"]

  - name: "Check Group Membership"
    type: "n8n-nodes-base.telegram"
    source: "new"
    module: "Authorization Gate"
    purpose: "بررسی عضویت کاربر در گروه"
    config_notes: |
      resource: 'chatMember'
      operation: 'get'
      chatId: '{{ $json.chatId }}'
    credentials: "telegramApi"
    connections: ["Core Router"]

connections:
  - from: "Telegram Trigger"    to: "Core Router"
  - from: "Core Router"         to: "Welcome Module"
  - from: "Core Router"         to: "Check Group Membership"
  - from: "Check Group Membership"  to: "Switch Access"

credentials_needed:
  - name: "Telegram Bot Token"
    type: "telegramApi"
    purpose: "ارسال و دریافت پیام تلگرام"
    used_by: ["Telegram Trigger", "Check Group Membership"]
  - name: "PostgreSQL"
    type: "postgres"
    purpose: "ذخیره کاربران و سفارشات"
    used_by: ["User Management DB", "Order DB"]

error_handling:
  - module: "Order Management"
    on_error: "continueErrorOutput"
    fallback: "ذخیره در dead-letter queue، notify admin"
  - module: "Payment Gateway"
    on_error: "stopWorkflow"
    retry: 3
    retry_delay: 5000

caching:
  - target: "Product Catalog"
    strategy: "Data Table cache با 5-min TTL"
    reason: "محصولات هر چند ساعت تغییر می‌کنن"

estimated_nodes: 38
estimated_complexity: "high"
estimated_modules: 12
estimated_builder_sessions: 3

test_plan:
  pinned: |
    {
      "message": { "text": "/start", "chat": { "id": 12345 } }
    }
  module_tests:
    - module: "Core Router"
      steps: [
        "/start → خوش‌آمدگویی",
        "'خرید قهوه' → فروشگاه",
        "'پشتیبانی' → AI"
      ]

open_questions: []
needs_human: false
```
