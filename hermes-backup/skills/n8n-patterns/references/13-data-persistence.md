# Best Practices: Data Persistence

> Technique key: `data_persistence` — Storing, updating, or retrieving records from durable storage
> (Data Tables, Google Sheets, Airtable, databases, object storage, Notion, and more)

---

## ۱. کی از persistence استفاده کنیم؟

| وضعیت | مثال | Storage پیشنهادی |
|-------|------|-----------------|
| ذخیره داخلی سریع | audit trail, پردازش | **Data Table** |
| چند workflow نیاز دارن | تنظیمات shared | **Data Table / Postgres** |
| هم‌تیمی‌ها ببینن/ویرایش کنن | گزارش، dashboard | **Google Sheets** |
| داده ساخت‌یافته با relation | پروژه، تسک، inventory | **Airtable / Postgres** |
| فایل / باینری | آپلود تصویر، PDF | **S3 + Data Table (meta)** |
| History چت / RAG | حافظه AI Agent | **Redis / PGVector / Supabase** |
| API read/write سنگین | real-time | **Redis / DynamoDB** |

---

## ۲. جدول مقایسه Storage Nodes

| نود | Credential | Upsert | Query | Self-host |
|-----|:----------:|:------:|:-----:|:---------:|
| **Data Table** | ❌ | ✅ | filter + orderBy | built-in |
| **Google Sheets** | ✅ OAuth | ✅ appendOrUpdate | read | ❌ |
| **Airtable** | ✅ API Key | ✅ | search/filterByFormula | ❌ |
| **Postgres** | ✅ | ✅ | SQL کامل | ✅ |
| **MySQL** | ✅ | ✅ | SQL کامل | ✅ |
| **Microsoft SQL** | ✅ | ❌ | SQL (executeQuery) | ✅ |
| **Snowflake** | ✅ | ❌ | SQL (executeQuery) | ❌ |
| **Redis** | ✅ host/port | ✅ set | get/keys | ✅ |
| **MongoDB** | ✅ ConnStr | ✅ findOneAndUpdate+upsert | find/aggregate | ✅ |
| **S3 / AWS S3** | ✅ AWS Keys | ❌ overwrite | list/search | S3-compat |
| **Supabase** | ✅ API Key | ❌ | get/getAll | ✅ |
| **Firebase Firestore** | ✅ Service Acct | ✅ upsert | query/get | ❌ |
| **Notion** | ✅ Integration | ❌ | search/get | ❌ |
| **Excel 365** | ✅ Graph | ✅ worksheet upsert | readRows/lookup | ❌ |
| **DynamoDB** | ✅ AWS Keys | ✅ | get/getAll (scan) | ❌ |

---

## ۳. Data Table (پیش‌فرض) — بدون Credential

**Table:** `create`, `list`, `delete`, `update` (name)
**Row:** `insert`, `get` (=getAll با `returnAll: true`), `update`, **`upsert`** ✅, `deleteRows`, `rowExists`, `rowNotExists`

| نکته | توضیح |
|------|-------|
| **`id` خودکار** | تو insert/upsert فیلد `id` رو نفرست |
| **filter** | `matchType: anyCondition/allConditions` — conditionها: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `isEmpty`, `contains`, `startsWith`, ... |
| **upsert = update or insert** | بر اساس filter conditions. اگه match پیدا کنه update می‌کنه، وگرنه insert |
| **محدودیت** | max ۵۰ ردیف پیش‌فرض (`returnAll: true` برای همه). filter محدود — برای query پیچیده از Postgres استفاده کن |

---

## ۴. Google Sheets — نیاز به OAuth

- **Sheet:** `read`, `append`, `update`, **`appendOrUpdate`** (upsert), `create`, `clear`, `delete`
- **Rate limit:** 60 req/user/min. **Degrade >10k rows.** Header row الزامی.
- برای workflow storage از Data Table استفاده کن. Sheets واسه collaboration.

## ۵. Airtable — نیاز به API Key

- **Row:** `create`, **`upsert`** ✅ (نیاز به unique field), `update`, `get`, `search` (filterByFormula), `deleteRecord`
- **Base:** `getMany`, `getSchema`
- **Rate limit:** 5 req/sec. upsert نیاز به unique field بعنوان identifier.

## ۶. Postgres / MySQL / MS SQL / Snowflake — نیاز به Credential

| Operation | Postgres | MySQL | MS SQL | Snowflake |
|-----------|:--------:|:-----:|:------:|:---------:|
| select / insert / update | ✅ | ✅ | via query | via query |
| **upsert** | ✅ | ✅ | ❌ | ❌ |
| `executeQuery` | ✅ | ✅ | ✅ | ✅ |

- برای upsert در MS SQL/Snowflake: `IF EXISTS ... UPDATE ELSE INSERT`
- SQL injection: n8n parameterize می‌کنه ولی ایمن باش

## ۷. Redis — نیاز به host/port

**Operations:** `set`, `get`, `delete`, `incr`, `push`, `pop`, `llen`, `keys`, `publish`, `info`
**کاربرد:** cache, counter, rate limiter, pub/sub, chat memory (subnode)
> **Durable نیست** — داده evict میشه. TTL دستی بذار.

## ۸. AWS S3 / S3-Compat — نیاز به AWS Keys

**Bucket:** `create`, `delete`, `getAll`, `search`
**File:** `upload`, `download`, `delete`, `copy`, `getAll`
**Folder:** `create`, `delete`, `getAll`

> **تله:** S3 فایل رو replace می‌کنه اگه اسم یکسان باشه. timestamp بذار توی fileName: `uploads/{{ $now.toFormat('yyyy/MM') }}/{{ $json.fileName }}`

## ۹. MongoDB — نیاز به connection string

**Operations:** `insert`, `update`, `findOneAndUpdate` (=upsert با `upsert: true`), `findOneAndReplace`, `find` (JSON filter), `aggregate`, `delete`, search index
> برای RAG: `vectorStoreMongoDBAtlas`

## ۱۰. Supabase / Firebase

| سرویس | Operations | Upsert |
|-------|-----------|:------:|
| **Supabase** | create, get, getAll, update, delete | ❌ |
| **Firebase Firestore** | create, **upsert** ✅, get, getAll, query, delete | ✅ |
| **Firebase Realtime** | create, get, update, push, delete | ❌ |

## ۱۱. Notion — نیاز به Integration Token

**Resources:** `databasePage` (create/get/getAll/update), `page` (create/archive/search), `block` (append/getAll), `database` (get/getAll/search), `user`
> Rate limit: 3 req/sec. upsert نداره — با search قبلش چک کن.

## ۱۲. Microsoft Excel 365 — نیاز به Graph

- **Workbook:** addWorksheet, deleteWorkbook, getAll
- **Worksheet:** append, **`upsert`** ✅, clear, readRows, update, getAll
- **Table:** append, addTable, getRows, getColumns, lookup

## ۱۳. AWS DynamoDB — نیاز به AWS Keys

- **Item:** **`upsert`** ✅, get (full key), getAll (scan), delete
> `getAll` = scan روی کل جدول — گرون. upsert atomic و سریع.

---

## ۱۴. پترن‌های واقعی

### ۱۴.۱. Form → Immediate Store
```
[Form Trigger] → [Data Table: insert] → [IF: success?]
  ├─ true → [Telegram: نوتیفیکیشن]
  └─ false → [Data Table: insert error_log]
  ↓ [Webhook Response: 200]
```

### ۱۴.۲. Upsert (بدون Duplicate)
```
[Webhook: دیتا] → [Data Table: upsert (match on orderId)]
  → [IF: inserted/updated] → [Telegram: سفارش جدید / آپدیت شد]
```
> معادل‌ها: Sheets=appendOrUpdate, Airtable=upsert+unique, Postgres=upsert+conflict, Redis=set, Firebase=upsert

### ۱۴.۳. Lookup → Enrich
```
[Webhook: سفارش با customerEmail]
  → [Data Table: get customers (email=...)]
  → [IF: exists?]
    ├─ true → [Set: enrich] → [Data Table: insert orders]
    └─ false → [Data Table: insert unknown_orders] + [Slack: notify]
```

### ۱۴.۴. Batch Store (حجم بالا)
```
[Schedule]
  → [HTTP: ۱۰۰۰ رکورد]
  → [Split In Batches: batchSize=10]
    → (main) [Postgres: insert batch] → back to Split
    → (done) [Telegram: "۱۰۰۰ رکورد ذخیره شد"]
```

### ۱۴.۵. Schedule → Aggregate → Store
```
[Schedule: روزانه ۸ صبح]
  → [Data Table: get سفارشات دیروز]
  → [Summarize: group by category, sum(amount), count]
  → [Data Table: insert daily_sales_summary]
  → [Convert To File: csv] → [Gmail: report]
```

### ۱۴.۶. S3 Upload + Meta
```
[Webhook: binary + meta]
  → [S3: upload (bucket, fileName با timestamp)]
  → [Data Table: insert meta (fileUrl, size, mime, userId)]
  → [Webhook Response: { fileUrl, id }]
```

### ۱۴.۷. State Machine (Read → Modify → Update)
```
[Webhook: taskId + newStatus]
  → [Airtable: get task]
  → [IF: pending→processing OR processing→done?]
    ├─ valid → [Airtable: update status + timestamp]
    └─ invalid → [400: Invalid transition]
```

### ۱۴.۸. Archive / Cleanup
```
[Schedule: نیمه‌شب]
  → [Data Table: get رکوردهای >90 روز]
  → [Data Table: deleteRows (همان filter)]
  → [Data Table: insert archive_log (count, date)]
  → [S3: upload CSV backup]
```

---

## ۱۵. انتخاب درست Storage

```
بدون credential → Data Table
با credential:
  ├─ جدول ساده     → Google Sheets / Airtable
  ├─ SQL relation  → Postgres / MySQL
  ├─ Document/JSON → MongoDB / Firebase
  ├─ Key-Value     → Redis / DynamoDB
  ├─ File/Binary   → S3
  ├─ Collaboration → Notion / Google Sheets
  └─ Vector/RAG    → PGVector / Redis Vector / Supabase
```

---

## ۱۶. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **Duplicate record** | `upsert` استفاده کن |
| 2 | **Data Table: insert با `id` دستی** | Row ID خودکار. `id` رو نفرست |
| 3 | **Data Table: فراموشی `returnAll`** | پیش‌فرض ۵۰ تا. `returnAll: true` بذار |
| 4 | **Google Sheets Rate Limit** | Data Table واسه volume بالا |
| 5 | **Google Sheets degrade >10k** | archive کن |
| 6 | **S3: overwrite فایل** | timestamp بذار توی fileName |
| 7 | **MongoDB upsert دستی** | `findOneAndUpdate` با `upsert: true` |
| 8 | **Airtable upsert بدون unique field** | unique field بعنوان identifier |
| 9 | **Redis: durable نیست** | واسه cache، نه storage اصلی |
| 10 | **DynamoDB `getAll` = scan** | از query با key condition استفاده کن |
| 11 | **Notion Rate Limit (3 req/sec)** | bulk بفرست با delay |
| 12 | **تغییر schema بعد از create** | Data Table تغییر ستون نداره — خوب design کن |
| 13 | **validation قبل از ذخیره** | حتماً required fields رو چک کن |
| 14 | **نوتیفیکیشن قبل از ذخیره موفق** | notification رو بعد از insert موفق بذار |
| 15 | **Firebase `create` روی سند موجود** | از `upsert` Firestore استفاده کن |

---

> **اصل طلایی:** Data Table پیش‌فرضه. تا وقتی دلیل مشخصی نداری، از Data Table استفاده کن. فقط وقتی credential/relation/file/collaboration نیاز داری برو سراغ بقیه.
