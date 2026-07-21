# Best Practices: Data Extraction

> Technique key: `data_extraction`
> استخراج داده‌های ساخت‌یافته از ورودی‌های مختلف — فایل، HTML، API، OCR، AI

---

## ۱. منابع داده

| منبع | نود اصلی | روش |
|------|---------|------|
| **PDF** | `extractFromFile` (operation: pdf) | متن مستقیم |
| **Excel (xls/xlsx)** | `extractFromFile` (operation: xls/xlsx) | تبدیل به JSON |
| **CSV** | `extractFromFile` (operation: csv) | تبدیل به JSON |
| **HTML صفحه** | `htmlExtract` / `webpageContentExtractor` | CSS selector |
| **JSON** | `extractFromFile` (operation: fromJson) | پارس مستقیم |
| **XML / ICS / ODS / RTF** | `extractFromFile` | operation مخصوص |
| **تصویر اسکن‌شده** | Tesseract / AWS Textract / Mindee | OCR |
| **Invoice/Receipt** | `mindee` (invoice/receipt) | AI ساخت‌یافته |
| **Text unstructured** | `informationExtractor` + LLM | AI extraction |
| **API (JSON array)** | HTTP → `splitOut` → پردازش | جداسازی آیتم‌ها |
| **وبسایت (reader mode)** | `webpageContentExtractor` | محتوای خالص |

---

## ۲. زیرساخت کلی

```
[Trigger: Webhook / Gmail / Schedule / Local File / Form]
    ↓
[IF/Switch: تشخیص نوع فایل (MIME type / extension)]
    ↓
[Extract From File / OCR / AI / HTML Extract]
    ↓
[Split Out: اگر خروجی array بود، جدا کن]
    ↓
[Validate: Code / IF — خالی نباشه، schema درست باشه]
    ↓
[Output: DataTable / Google Sheets / Postgres / CSV File]
```

---

## ۳. پترن ۱: File Type Routing + Extraction

ورک‌فلوهای واقعی (`5a09b609`, `ce5fa685`):

```
[Webhook / Local File Trigger]
    ↓
[Switch: MIME type]
    ├── application/pdf    → [Extract From File: pdf]
    ├── image/*            → [Tesseract OCR / Gemini Vision]
    ├── text/csv           → [Extract From File: csv]
    ├── application/vnd.*excel → [Extract From File: xls/xlsx]
    └── default            → [Error / Manual Review]
    ↓
[AI: استخراج ساخت‌یافته (Gemini / GPT-4)]
    ↓
[Code: Validate + Clean]
    ↓
[Google Sheets / Postgres: ذخیره]
```

---

## ۴. پترن ۲: Web Scraping با Information Extractor

ورک‌فلو واقعی (`f8fd8869`):

```
[Manual / Schedule]
    ↓
[HTTP Request: GET HTML صفحه]
    ↓
[Information Extractor: استخراج با schema]
    │  مدل: OpenAI Chat Model
    │  schema: { title, price, availability, url, image }
    ↓
[Split Out: جداسازی آیتم‌ها]
    ↓
[Google Sheets: append ردیف‌ها]
```

> برای استخراج ساده‌تر: `htmlExtract` با CSS selector (مثل `div.book h3 a`)
> برای استخراج خوانا: `webpageContentExtractor` (تبدیل صفحه به متن خالص)

---

## ۵. پترن ۳: CSV → Sort → Email

ورک‌فلو واقعی (`a8294862`):

```
[Google Sheets Trigger: ردیف جدید با URL]
    ↓
[HTTP: GET صفحه / Dumpling AI scrape]
    ↓
[HTML > Split Out: جداسازی آیتم‌ها]
    ↓
[HTML > Extract: title + price]
    ↓
[Sort: بر اساس price]
    ↓
[Convert To File: csv]
    ↓
[Gmail: ارسال فایل]
```

---

## ۶. پترن ۴: API → Split Out → Aggregate

ورک‌فلوهای واقعی (`8ab4856f`, `7ef5a3a0`):

```
[HTTP: GET از API (Trustpilot / Monday.com / هر API)]
    ↓
[Code: parse JSON embedded در HTML]
    ↓
[Split Out: هر آیتم جدا]
    ↓
[Set: format کردن فیلدها]
    ↓
[Aggregate / Google Sheets: ذخیره]
```

> قانون: **همیشه** بعد از HTTP که JSON array می‌گیره، `Split Out` بزن.
> بعدش می‌تونی `itemLists` (sort/limit/summarize) یا `aggregate` بزنی.

---

## ۷. پترن ۵: AI Extraction + Validation + Storage

ورک‌فلوهای واقعی (`0c9a12ef`, `84647459`):

```
[Local File Trigger: فایل جدید]
    ↓
[PDF Vector / Extract: استخراج متن]
    ↓
[GPT-4 / Claude: استخراج ساخت‌یافته]
    │  خروجی: { doc_type, date, parties, amounts, terms }
    ↓
[Code: Validate]
    │  - چک کردن doc_type
    │  - پارس کردن تاریخ‌ها
    │  - پاک کردن مقادیر مالی
    │  - validation ایمیل
    ↓
[Switch: doc_type]
    ├── invoice → [Postgres: insert به invoices]
    └── other   → [Postgres: insert به documents]
    ↓
[Convert To File: csv (گزارش روزانه)]
```

---

## ۸. نودهای کامل

| نود | عملیات‌ها | نکته |
|-----|-----------|------|
| `extractFromFile` | pdf, csv, xls, xlsx, json, xml, text, html, rtf, ods, ics, binaryToProperty | **قبلش type رو چک کن** |
| `htmlExtract` | CSS selector | `selector: "div.item h3 a"` |
| `html` | extractHtmlContent | محتوای متنی HTML |
| `webpageContentExtractor` | reader mode | هدر/فوتر رو حذف می‌کنه |
| `informationExtractor` | AI extraction با schema | نیاز به LLM داره |
| `splitOut` | array → items جدا | بعد از HTTP حتماً |
| `aggregate` | items → array | برعکس splitOut |
| `itemLists` | sort, limit, removeDuplicates, concatenateItems, summarize, splitOutItems | جایگزین چند نود |
| `summarize` | sum, count, max, min, avg, ... | روی numbers |
| `convertToFile` | csv, xls, xlsx, html, json, rtf, ods, iCal | خروجی فایل |
| `awsTextract` | analyzeExpense | OCR پیشرفته |
| `mindee` | invoice.predict, receipt.predict | invoice/receipt |
| `code` / `function` | custom validation | همیشه بذار |

---

## ۹. تله‌ها

| تله | راه‌حل |
|-----|--------|
| **File Type اشتباه** | `extractFromFile` با operation اشتباه → خالی یا خطا. همیشه Switch بذار روی MIME type |
| **JSON Array در HTTP** | اگه Split Out نزنی، فقط یه آیتم می‌گیری |
| **Binary Data Loss** | Set/Code بدون "Include Other Input Fields" → binary می‌پره |
| **استخراج خالی از PDF** | PDF اسکن‌شده → fallback به OCR |
| **AI Output بی‌کیفیت** | `outputParserStructured` بذار + validation |
| **Duplicate Processing** | Gmail Trigger "Mark as Read" + dedup |
| **Memory با فایل بزرگ** | batch processing + filesystem mode |
