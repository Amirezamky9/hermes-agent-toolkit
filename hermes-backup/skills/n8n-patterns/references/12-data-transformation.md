# Best Practices: Data Transformation

> Technique key: `data_transformation` — Cleaning, formatting, or restructuring data (including summarization)
>
> مبنا: MCP best-practices docs + type definitions واقعی نودها + تجربه عملی

---

## فهرست

1. [اصول کلی](#۱-اصول-کلی)
2. [Expressions — توابع JS درون {{ }}](#۲-expressions--توابع-js-درون--)
3. [نود Edit Fields (Set)](#۳-نود-edit-fields-set)
4. [نود Filter](#۴-نود-filter)
5. [نود IF / Switch](#۵-نود-if--switch)
6. [نود Merge](#۶-نود-merge)
7. [نود Item Lists](#۷-نود-item-lists)
8. [نود Remove Duplicates](#۸-نود-remove-duplicates)
9. [نود Split Out / Aggregate](#۹-نود-split-out--aggregate)
10. [نود Date & Time](#۱۰-نود-date--time)
11. [نود HTML](#۱۱-نود-html)
12. [نود Spreadsheet File](#۱۲-نود-spreadsheet-file)
13. [نود Code](#۱۳-نود-code)
14. [نود Split In Batches (Loop)](#۱۴-نود-split-in-batches-loop)
15. [نود AI Transform](#۱۵-نود-ai-transform)
16. [نود Sort / Limit](#۱۶-نود-sort--limit)
17. [پترن‌های ترکیبی](#۱۷-پترنهای-ترکیبی)
18. [تله‌ها](#۱۸-تلهها)

---

## ۱. اصول کلی

- **Input → Transform → Output**: همیشه این پترن رو رعایت کن
- **Filter early**: دیتا رو تا جایی که می‌شه زود reduce کن
- **از Set و Code برای تبدیل استفاده کن**، ولی Code رو آخرین راهکار بذار
- **همیشه نوع داده (type) رو چک کن** — string/number/boolean درست ست نشه، بقیه نودها fail می‌کنن
- **از expressions برای transformations ساده استفاده کن** — نیازی به Code نیست

---

## ۲. Expressions — توابع JS درون `{{ }}`

> 📎 **مرجع کامل expressions در فایل جدا:** [`XX-n8n-expressions.md`](XX-n8n-expressions.md)
> — شامل همه متغیرها (`$json`, `$now`, `$('Node')`, ...)، توابع String/Number/Array/DateTime،
> پترن‌های کاربردی، دسترسی بین نودی، و ۱۰ تله.

Expressions یا همون **`expr('...')`** جانشین اصلی Code node هستند. توی فیلدهای اکثر نودها می‌تونی مستقیم expression بزنی — بدون نیاز به نوشتن کد.

```
مثال:    expr('Hello {{ $json.name }}, today is {{ $now.toFormat("yyyy-MM-dd") }}')
مثال:    expr('{{ $json.count > 0 ? "active" : "empty" }}')
مثال:    expr('{{ $("Trigger").item.json.body.email }}')
```

**قوانین طلایی Expressions:**
- `$json` فقط به **نود قبلی** اشاره می‌کنه — بعد از Set/Merge عوض می‌شه
- `$('NodeName').item.json.field` برای دسترسی به **نودهای دیگر**
- `$()` و `$json` و `$now` فقط **داخل `{{ }}`** معنی دارن
- برای fallback: `$json.name || 'Unknown'` یا `$json.price ?? 0`

> برو سراغ [`XX-n8n-expressions.md`](XX-n8n-expressions.md) برای مرجع کامل.

---

## ۳. نود Edit Fields (Set)

### ۳.۱. دو Mode

#### Manual Mapping (mode: manual)
تبدیل فیلد به فیلد یکی‌یکی. هر assignment یک `type` داره:

| Type | توضیح | مثال مقدار |
|------|-------|-----------|
| `string` | رشته یا expression | `expr('Hello {{ $json.name }}')` |
| `number` | عدد یا expression | `expr('{{ Number($json.price) * 1.09 }}')` |
| `boolean` | true/false | `expr('{{ $json.count > 0 }}')` |
| `array` | آرایه | `expr('{{ [1, 2, 3] }}')` |
| `object` | object (نه array) | `expr('{{ { key: "value" } }}')` |
| `binary` | دیتای باینری از نود قبلی | `$('Node').item.binary.data` |

**نکته:** `includeOtherFields` (همون Keep Only Set سابق):
- **false** (پیش‌فرض) = فقط فیلدهایی که توی assignment تعریف کردی می‌مونه. بقیه می‌پره — **DATA LOSS**
- **true** = فیلدهای ورودی + فیلدهای جدید. می‌تونی با `include=selected` یا `include=except` فیلترش کنی

#### JSON/Raw Mode (mode: raw)
یه JSON می‌دی که دقیقاً همون shape رو می‌سازه. دستت بازتره:

```json
{
  "fullName": "{{ $json.firstName }} {{ $json.lastName }}",
  "total": "{{ Number($json.price) * Number($json.qty) }}",
  "createdAt": "{{ $now.toISO() }}"
}
```

### ۳.۲. Optionهای مهم

| option | پیش‌فرض | اثر |
|--------|---------|-----|
| `includeBinary` | true | دیتای باینری رو همراه کنه؟ |
| `stripBinary` | true | حذف binary از خروجی (فقط وقتی includeOtherFields=true) |
| `ignoreConversionErrors` | false | خطاهای type conversion رو نادیده بگیره |
| `dotNotation` | true | `a.b` → `{a: {b: value}}`. false → `{"a.b": value}` |

### ۳.۳. پترن: Duplicate Item برای تست

Set می‌تونه آیتم رو تکرار کنه (برای تست bulk):
- `duplicateItem: true`
- `duplicateCount: 5` → ۶ تا آیتم می‌ده (۱ اصلی + ۵ تا کپی)

### ۳.۴. نکات Set

- **برای تبدیل نوع داده** (`string → number`): expression بزن `Number($json.price)`
- **برای fallback**: `expr('{{ $json.name || "Unknown" }}')`
- **برای شرط**: `expr('{{ $json.count > 0 ? "active" : "inactive" }}')`
- **dotNotation=false** به دردمون می‌خوره وقتی اسم فیلد نقطه داره (مثلاً `user.name` واقعیه نه nested)
- **تست با fallback**: موقع تست Set بذار `expr('{{ $json.name || "Jane Doe" }}')` که اگه فیلد نباشه، کرش نکنه

---

## ۴. نود Filter

فیلتر کردن آیتم‌ها بر اساس شرط. filter می‌کنه نه route — آیتم‌های不符合 رو حذف می‌کنه.

### پارامترها

```javascript
{
  combinator: 'and' | 'or',
  conditions: [{
    leftValue: expr('{{ $json.field }}'),
    operator: {
      type: 'string' | 'number' | 'dateTime' | 'boolean' | 'array' | 'object',
      operation: 'equals' | 'notEquals' | 'contains' | 'startsWith' | 'endsWith' |
                 'larger' | 'smaller' | 'isEmpty' | 'isNotEmpty' | ...
    },
    rightValue: 'value'
  }],
  options: {
    caseSensitive: true,
    leftValue: '',
    typeValidation: 'strict' | 'loose',
    version: 2
  }
}
```

### نکات

| نکته | توضیح |
|------|-------|
| **جایگزین IF واسه filter** | اگه فقط می‌خوای آیتم‌های غیر符合 رو حذف کنی (نه routing)، از **Filter** استفاده کن نه IF |
| **`looseTypeValidation`** | مقادیر رو cast می‌کنه. مثلاً `"false"` به `false` تبدیل می‌شه |
| **زود filter کن** | هر چی زودتر filter بزنی، نودهای بعدی volume کمتری پردازش می‌کنن |

---

## ۵. نود IF / Switch

- **IF**: دو خروجی (true/false) — برای binary routing
- **Switch**: N خروجی — برای multi-way routing
  - `mode: rules` — شرط بذار برای هر خروجی
  - `mode: expression` — expression بنویس که شماره خروجی رو برگردونه

> **نکته انتقادی:** IF دو خروجی `onTrue` و `onFalse` داره. اگه یه خروجی رو وصل نکنی، آیتم‌هاش **بی‌صدا حذف** می‌شن. همیشه هر دو مسیر رو چک کن.

---

## ۶. نود Merge

### ۶.۱. پنج Mode

| Mode | زمانی استفاده کن | مثال |
|------|-----------------|------|
| **Append** | دو branch رو پشت سر هم بچسبون | برچ ۱: [{a},{b}] برچ ۲: [{c}] → [{a},{b},{c}] |
| **Combine (by Key)** | دو branch رو با یه کلید مشترک JOIN کن (مثل SQL JOIN) | برچ ۱: [{id:1, x}] برچ ۲: [{id:1, y}] → [{id:1, x, y}] |
| **Combine (by Position)** | بر اساس ایندکس جفت کن | برچ ۱: [{a},{b}] برچ ۲: [{c}] → [{a,c}, {b, undefined}] |
| **SQL Query** | ۲+ ورودی، join/aggregation پیشرفته | `SELECT * FROM input1 LEFT JOIN input2 ON input1.id = input2.id` |
| **Choose Branch** | فقط یه branch رو نگه دار | از بین ۲ ورودی یکی رو انتخاب کن |

### ۶.۲. Merge by Key — جزئیات

```javascript
mode: 'combine'
// داخل combine mode دو زیرحالت:
// 1) combineByFields — JOIN بر اساس فیلد
// 2) combineByPosition — JOIN بر اساس ترتیب
```

برای `combineByFields`:
- `fieldsToMatch.input1.fieldName` / `fieldsToMatch.input2.fieldName` — فیلد کلید
- `outputType` — `both` (merge), `input1Only`, `input2Only`

### ۶.۳. Merge by SQL

برای ۲+ ورودی یا عملیات پیچیده:
```sql
SELECT 
  i1.name,
  i1.total,
  i2.category,
  i2.region
FROM input1 AS i1
LEFT JOIN input2 AS i2 ON i1.id = i2.id
```

### ۶.۴. نکات Merge

| نکته | توضیح |
|------|-------|
| **همیشه اسم فیلدها رو normalize کن** | قبل از Merge، با Set اسم فیلدها رو یکسان کن |
| **Merge منتظر همه branchها می‌مونه** | تا هر دو branch نرسن، اجرا نمی‌شه |
| **Mode اشتباه بی‌صدا آیتم حذف می‌کنه** | `combineByPosition` وقتی تعداد آیتم‌ها不等 باشه، مازاد رو undefined می‌کنه |
| **Append با executeOnce** | بعد از append، نود بعدی N بار execute می‌شه. اگه می‌خوای یه بار اجرا بشه، `executeOnce` بذار |

---

## ۷. نود Item Lists

یه نود با ۶ تا operation که جای چند نود مجزا رو می‌گیره:

| Operation | کاربرد | معادل نود مجزا |
|-----------|--------|----------------|
| **concatenateItems** | فیلدهای چند آیتم رو توی یه لیست ترکیب کن | Aggregate |
| **limit** | تعداد آیتم‌ها رو محدود کن | Limit |
| **removeDuplicates** | آیتم‌های تکراری رو حذف کن | Remove Duplicates |
| **sort** | مرتب‌سازی بر اساس فیلد | Sort |
| **splitOutItems** | آرایه داخل آیتم رو به آیتم‌های جدا تبدیل کن | Split Out |
| **summarize** | Pivot Table — aggregation گروهی | Summarize |

### ۷.۱. concatenateItems

```javascript
operation: 'concatenateItems',
options: {
  concatenate: {
    fields: ['fieldName'],    // فیلدی که می‌خوایم مقادیرش توی array جمع بشه
    delimiter: ',',            // جداکننده
    includeEmpty: false
  }
}
// خروجی: یه آیتم با array توش
```

### ۷.۲. sort

```javascript
operation: 'sort',
sort: {
  sortFields: {
    values: [{
      fieldName: 'price',
      sortOrder: 'Descending' | 'Ascending'
    }]
  },
  options: {
    disableDotNotation: false
  }
}
```

### ۷.۳. summarize (Pivot)

مثل Summarize ولی توی Item Lists:
```javascript
operation: 'summarize',
summarize: {
  groupBy: 'category',
  values: {
    aggregation: 'sum',
    field: 'amount'
  }
}
```

> **کی از Item Lists (summarize) استفاده کنم و کی از Summarize مجزا؟**
> - از **Item Lists** وقتی بعدش sort/limit هم نیاز داری
> - از **Summarize** وقتی فقط aggregation ساده می‌خوای (خواناتره)

---

## ۸. نود Remove Duplicates

### ۸.۱. سه Operation

| Operation | کاربرد |
|-----------|--------|
| `removeDuplicateInputItems` | از بین آیتم‌های ورودی، تکراری‌ها رو حذف کن (بر اساس فیلد/فیلدها) |
| `removeItemsSeenInPreviousExecutions` | آیتم‌هایی که تو executionهای قبلی دیده شدن رو حذف کن — **بین executionها dedup می‌کنه** |
| `clearDeduplicationHistory` | حافظه dedup رو پاک کن — بعدش دوباره از اول dedup می‌کنه |

### ۸.۲. مثال‌ها

```javascript
// Operation: removeDuplicateInputItems
// Scope: duplicatesInField — مقایسه بر اساس فیلد مشخص
// scopeToCheck: 'allFields' | 'selectedField'
// fieldName: 'email'  ← فقط وقتی scopeToCheck=selectedField
```

```javascript
// Operation: removeItemsSeenInPreviousExecutions
// Scope: 'workflow' | 'node'
// Key to Deduplicate On: 'email' ← فیلد کلید
// Storage Key: 'uniqueEmails' ← کلید ذخیره در حافظه
```

---

## ۹. نود Split Out / Aggregate

| نود | جهت | توضیح |
|-----|-----|-------|
| **Split Out** | ۱ آیتم با آرایه → N آیتم | `{items: ["a","b"]}` → ۲ آیتم `{item: "a"}` و `{item: "b"}` |
| **Aggregate** | N آیتم → ۱ آیتم با آرایه | برعکس Split Out |

### نکات

- **بعد از HTTP Request اگه خروجی array باشه، حتماً Split Out بزن** — وگرنه فقط یه آیتم می‌گیری
- **Aggregate فیلد مشخصی رو جمع می‌کنه** — `aggregate.target` اسم فیلدی که می‌خوایم array بشه
- **برای merge چند branch از Merge استفاده کن** نه Aggregate. Aggregate فقط یه branch رو جمع می‌کنه

---

## ۱۰. نود Date & Time

### ۱۰.۱. هفت Operation

| Operation | توضیح | پارامترهای کلیدی |
|-----------|-------|------------------|
| `getCurrentDate` | زمان فعلی | `includeTime`, `outputFieldName` |
| `formatDate` | فرمت تاریخ | `date`, `format: yyyy/MM/dd | custom`, `customFormat` |
| `addToDate` | اضافه کردن زمان | `magnitude`, `timeUnit`, `duration` |
| `subtractFromDate` | کم کردن زمان | مثل addToDate |
| `getTimeBetweenDates` | تفاوت دو تاریخ | `startDate`, `endDate`, `units: ["day"]` |
| `extractDate` |提取 بخشی از تاریخ | `part: month | year | day | week | hour | minute | second` |
| `roundDate` | رند کردن | `mode: roundDown | roundUp`, `toNearest: month | week | day...` |

### ۱۰.۲. Custom Format Tokens

برای `customFormat`، از **Luxon tokens** استفاده کن:

| Token | خروجی |
|-------|-------|
| `yyyy` | 2026 |
| `MM` | 07 |
| `dd` | 09 |
| `HH` | 18 (24h) |
| `mm` | 30 |
| `ss` | 00 |
| `yyyy-MM-dd` | 2026-07-09 |
| `yyyy/MM/dd HH:mm` | 2026/07/09 18:30 |
| `MMMM dd, yyyy` | July 09, 2026 |

### ۱۰.۳. جایگزین Expression

به جای Date & Time node، می‌تونی مستقیم تو Set بنویسی:

```javascript
expr('{{ $now.toISO() }}')                    // زمان فعلی ISO
expr('{{ $now.toFormat("yyyy-MM-dd") }}')     // فرمت دلخواه
expr('{{ $now.plus({days: 7}).toISO() }}')    // ۷ روز بعد
expr('{{ $today.toISODate() }}')              // فقط تاریخ امروز
```

> **کی از Date & Time node استفاده کنم؟** وقتی نیاز به تنظیمات timezone، format از پیش‌تعریف‌شده، یا عملیات خاص (extract/round) داری. برای تبدیل ساده، expression داخل Set کافیه.

---

## ۱۱. نود HTML

### ۱۱.۱. سه Operation

| Operation | توضیح | پارامترها |
|-----------|-------|-----------|
| `generateHtmlTemplate` | رندر HTML template با expression | `html` (string با expression) |
| `extractHtmlContent` | استخراج داده از HTML با CSS selector | `sourceData: json | binary`, `extractionValues` |
| `convertToHtmlTable` | تبدیل JSON به جدول HTML | `options: caption, tableAttributes, ...` |

### ۱۱.۲. مثال‌ها

```html
<!-- generateHtmlTemplate -->
<html>
<body>
  <h1>Order Report</h1>
  <p>Date: {{ $now.toFormat("yyyy-MM-dd") }}</p>
  <ul>
  {{ $input.all().map(i => `<li>${i.json.name}: $${i.json.total}</li>`).join('') }}
  </ul>
</body>
</html>
```

```javascript
// extractHtmlContent
extractionValues: {
  values: [{
    key: 'title',
    cssSelector: 'h1.product-title',
    returnValue: 'text', // text | html | attribute | value
    returnArray: false
  }, {
    key: 'links',
    cssSelector: 'a',
    returnValue: 'attribute',
    attribute: 'href',
    returnArray: true
  }]
}
```

---

## ۱۲. نود Spreadsheet File

- **`fromFile`**: فایل CSV/XLS/XLSX/ODS رو می‌خونه و به JSON تبدیل می‌کنه
- **`toFile`**: JSON رو می‌نویسه به فایل spreadsheet

### پارامترهای مهم fromFile

| پارامتر | توضیح |
|---------|-------|
| `fileFormat` | `csv`, `xls`, `xlsx`, `ods` |
| `options.range` | محدوده سلول‌ها (مثلاً `A1:C10`) |
| `options.sheetName` | اسم شیت (فقط xlsx) |
| `options.headerRow` | true = ردیف اول رو header در نظر بگیر |
| `options.includeEmptyCells` | false = سلول‌های خالی رو حذف کن |

> **تفاوت با `extractFromFile`:** `spreadsheetFile` دیتای spreadsheet (ردیف/ستون) رو مدیریت می‌کنه با optionهای ویژه (range, sheet, header). `extractFromFile` فایل رو به JSON ساده تبدیل می‌کنه. برای CSV/XLS/XLSX، `spreadsheetFile.toFile` معمولاً بهتر از `convertToFile` هست چون فرمت‌بندی بهتری داره.

---

## ۱۳. نود Code

### ۱۳.۱. دو Mode

| Mode | زبان‌ها | توضیح |
|------|---------|-------|
| `runOnceForEachItem` | JavaScript, Python | به تعداد ورودی‌ها اجرا می‌شه. `$input.item` داری |
| `runOnceForAllItems` | JavaScript, Python | یه بار اجرا می‌شه با همه آیتم‌ها. `$input.all()` داری |

### ۱۳.۲. JavaScript patterns

```javascript
// Run Once for Each Item
return {
  name: $json.name.toUpperCase(),
  total: Number($json.price) * Number($json.qty),
  date: $now.toISO()
};

// Run Once for All Items
const items = $input.all();
const result = items.map(item => ({
  ...item.json,
  total: Number(item.json.price) * Number(item.json.qty),
  category: item.json.amount > 100 ? 'high' : 'low'
}));
// برای aggregation:
const total = items.reduce((s, i) => s + Number(i.json.amount), 0);
result.push({ summary: { total, count: items.length } });
return result;
```

### ۱۳.۳. Python patterns

```python
# Run Once for Each Item
item = _input  # دیکشنری current item
return {
    'name': item['json']['name'].upper(),
    'total': float(item['json']['price']) * float(item['json']['qty'])
}

# Run Once for All Items  
items = _input.all()
result = []
for item in items:
    result.append({
        **item['json'],
        'total': float(item['json']['price']) * float(item['json']['qty'])
    })
return result
```

### ۱۳.۴. نکات حیاتی Code

| نکته | توضیح |
|------|-------|
| **خروجی حتماً `return items` یا `[{json: {...}}]`** | هر چیز دیگه‌ای باعث خطا می‌شه |
| **Sandbox: بدون network** | `fetch()`, `axios`, `requests` **کار نمی‌کنن** |
| **از Code به عنوان آخرین راهکار استفاده کن** | Set, Summarize, Item Lists, Filter خیلی سریعترن |
| **برای API از HTTP Request استفاده کن** | بعدش می‌تونی با Code پردازشش کنی |
| **Code سنگین روی ۱۰۰۰۰+ آیتم timeout می‌ده** | Split In Batches بزن |
| **Luxon داخل Code در دسترسه** | `$now`, `$today`, `DateTime` |
| **`$jmespath` واسه query JSON** | `$jmespath.query($json.data, 'items[?price > `10`]')` |

---

## ۱۴. نود Split In Batches (Loop)

برای پردازش حجم زیاد دیتا در batchهای کوچک:

```
[Trigger] → [Split In Batches: batchSize=10]
    ↓ main (هر batch)
  [HTTP / AI / پردازش سنگین]
    ↓
  ← back به Split In Batches (nextBatch) ←
    ↓ done
  [ادامه workflow بعد از all batches]
```

### نکات

| نکته | توضیح |
|------|-------|
| **خروجی `nextBatch` داره و `done`** | `nextBatch` برمی‌گرده به خودش (for next batch). `done` بعد از آخرین batch فعال می‌شه |
| **روی ورودی خالی خطا نمی‌ده** | `no-ops on empty input` — نیازی به IF gate نیست |
| **`batchSize`** | تعداد آیتم در هر batch. برای API calls بذار ۵-۱۰. برای پردازش سبک ۵۰-۱۰۰ |
| **`options.reset`** | اگر true، هر execution از اول شروع می‌کنه (نادیده گرفتن وضعیت قبلی) |

---

## ۱۵. نود AI Transform

نود جدید `aiTransform` — دیتا رو با توضیح به زبان ساده تغییر بده:

```
ورودی: JSON از یک API
AI Transform: "استخراج فقط فیلدهای name و email. فیلد name رو به حروف بزرگ تبدیل کن."
خروجی: JSON پالایش‌شده
```

> جایگزین جالب Set + Code برای transformationهای غیرقطعی یا وقتی schema رو دقیقاً نمی‌دونی. فقط برای پردازش‌های سبک — گرونه برای volume بالا.

---

## ۱۶. نود Sort / Limit

| نود | توضیح |
|-----|-------|
| **Sort** | مرتب‌سازی بر اساس یک یا چند فیلد (Ascending/Descending) |
| **Limit** | نگه‌داشتن فقط N آیتم اول |

> هر دو رو می‌تونی با **Item Lists** (operation: sort / limit) هم انجام بدی. اگه sort + limit + چیز دیگه‌ای می‌خوای، یه دونه Item Lists کافیه.

---

## ۱۷. پترن‌های ترکیبی

### پترن ۱: Webhook → Validate → Clean → Save

```
[Webhook: دریافت فرم ثبت‌نام]
    ↓
[Filter: email خالی نباشه]
    ↓
[Set: normalize کردن — trim, lowercase, type conversion]
    │  name: expr('{{ $json.name.trim() }}')
    │  email: expr('{{ $json.email.toLowerCase().trim() }}')
    │  age: expr('{{ Number($json.age) }}')
    │  registeredAt: expr('{{ $now.toISO() }}')
    ↓
[IF: age > 0 و age < 120]
    ├── true → [DataTable: ذخیره]
    └── false → [Webhook Response: error message]
```

### پترن ۲: CSV → Parse → Transform → Excel

```
[Local File Trigger: فایل CSV جدید]
    ↓
[Spreadsheet File: fromFile — خواندن CSV]
    ↓
[Set: تبدیل نوع داده — string → number]
    │  amount: expr('{{ Number($json.amount) }}')
    │  date: expr('{{ $json.date }}')  // string به string
    ↓
[Item Lists: sort بر اساس amount DESC]
    ↓
[Item Lists: limit به ۱۰ تا]
    ↓
[Set: اضافه کردن فیلد rank]
    │  rank: expr('{{ $itemIndex + 1 }}')
    ↓
[HTML: convertToHtmlTable — خروجی HTML]
```

### پترن ۳: Merge دو API + Transformation

```
[HTTP: API مشتریان → [{id, name, email}]]
    ↓ (branch A)
[HTTP: API سفارشات → [{customerId, total, date}]]
    ↓ (branch B)
[Merge: combineByFields — id = customerId]
    ↓
[Set: محاسبه مجموع خرید هر مشتری]
    │  totalSpent: expr('{{ $json.total }}')  // بعد از Merge
    │  segment: expr('{{ $json.total > 1000 ? "VIP" : "Regular" }}')
    ↓
[DataTable: ذخیره]
```

### پترن ۴: Loop با Split In Batches برای پردازش AI

```
[DataTable: get ۱۰۰۰ رکورد]
    ↓
[Split In Batches: batchSize=10]
    ↓ (main)
  [AI Agent: تحلیل دسته‌ای آیتم‌ها]
    ↓
  [Set: ذخیره نتیجه در فیلد analysis]
    ↓
  → back to Split In Batches (nextBatch)
    ↓ (done)
[DataTable: upsert all results]
```

### پترن ۵: Dedup بین executionها

```
[Schedule: هر روز ۸ صبح]
    ↓
[HTTP: GET از API جدیدترین رکوردها]
    ↓
[Remove Duplicates: removeItemsSeenInPreviousExecutions]
    │  scopeToCheck: 'selectedField'
    │  fieldName: 'id'
    │  storageKey: 'seenIds'
    ↓
[DataTable: upsert فقط رکوردهای جدید]
```

### پترن ۶: Date Range Filter + Pivot

```
[DataTable: get همه سفارشات]
    ↓
[Filter: date >= $now.minus({days: 30})]
    ↓
[Date & Time: extractDate — part: month]
    │  field: $json.date
    ↓
[Summarize: group by month + sum amount + count]
    ↓
[Sort: بر اساس month ASC]
    ↓
[Convert To File: xlsx]
```

---

## ۱۸. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **Set: includeOtherFields=false → data loss** | همیشه بعد از Set خروجی رو inspect کن. اگه همه فیلدها رو می‌خوای، `includeOtherFields=true` بذار |
| 2 | **Set: dotNotation=true → `a.b` به `{a: {b: value}}` تبدیل می‌شه** | اگه اسم فیلد واقعاً نقطه داره، `dotNotation=false` کن |
| 3 | **Expression خارج از `{{ }}`** | `$()` و `$json` و `$now` فقط داخل `{{ }}` کار می‌کنن |
| 4 | **`$json` بعد از Set یا Merge تغییر می‌کنه** | برای فیلدهای نودهای قبلی از `$('NodeName').item.json.field` استفاده کن |
| 5 | **Merge mode اشتباه** | mode رو بر اساس shape دیتا انتخاب کن — `append` واسه concatenation، `combineByFields` واسه JOIN |
| 6 | **Code: return format اشتباه** | همیشه `return items` یا `return [{json: {...}}]`. هیچ وقت `return $json` نکن |
| 7 | **Code: Network calls** | Sandbox هیچ network accessی نداره. از HTTP Request استفاده کن |
| 8 | **Split Out فراموش شده** | بعد از HTTP که JSON array می‌ده، Split Out رو فراموش نکن — وگرنه فقط ۱ آیتم می‌گیری |
| 9 | **Aggregate به‌جای Merge** | Aggregate فقط یه branch رو handle می‌کنه. برای چند branch از Merge استفاده کن |
| 10 | **Split In Batches بدون `nextBatch`** | loop بی‌نهایت. همیشه خروجی `nextBatch` رو به Split In Batches وصل کن |
| 11 | **بعد از Split In Batches executeOnce** | نود بعد از `nextBatch` واسه هر batch اجرا می‌شه. اگه می‌خوای یه بار execute بشه، `executeOnce` بذار بعد `done` |
| 12 | **IF با یه خروجی باز** | IF دو خروجی داره. اگه یه‌طرف رو وصل نکنی، آیتم‌هاش بی‌صدا حذف می‌شن |
| 13 | **`removeItemsSeenInPreviousExecutions` حافظه داره** | تا `clearDeduplicationHistory` نزنی، آیتم‌هایی که قبلاً دیده شده بودن برای همیشه حذف می‌شن |
| 14 | **`$input.first()` به‌جای `$('Node').item.json`** | تو multi-item workflow `first()` فقط آیتم ۰ رو می‌ده |
| 15 | **Expression با `$json` تو AI Agent subnode** | `$json` تو agent subnodeها بی‌اعتباره. از `nodeJson()` استفاده کن |
| 16 | **Type mismatch: string به‌جای number** | Set type درست رو انتخاب کن. واسه تبدیل دستی: `expr('{{ Number($json.price) }}')` |
| 17 | **فراموشی timezone** | `$now` بر اساس timezone instance هست. اگه timezone خاصی می‌خوای، تو Date & Time Node `options.timezone` رو ست کن |
| 18 | **CSV با هدرهای متفاوت** | از `spreadsheetFile` با `options.headerRow: true` استفاده کن. نذار schema ثابت داشته باشه |
| 19 | **MCP: Set assignments به‌صورت bare array خرابش می‌کنه** | وقتی از `update_workflow` Set v3.4 رو ویرایش می‌کنی، assignments باید `{assignments: [...]}` باشه نه `[...]`. آرایه لخت باعث corrupt شدن نود و "node not found" می‌شه. راه‌حل: `addNode` + `addConnection` برای بازسازی. جزئیات بیشتر: `references/27-mcp-editing-pitfalls.md` |

---

## خلاصه سریع

```
تبدیل ساده فیلد       → Set (expression)
نرمالایز کردن          → Set (trim, lowerCase, Number)
فیلتر                  → Filter
Routing                → IF / Switch
Merge دو stream        → Merge (byKey / append / SQL)
Sort + Limit           → Item Lists (sort + limit)
Dedup بین execution    → Remove Duplicates (removeItemsSeenInPreviousExecutions)
Pivot table            → Item Lists (summarize) / Summarize
Array → items          → Split Out
Items → array          → Aggregate
Date manipulation      → Date & Time / expression در Set
HTML extraction        → HTML (extractHtmlContent)
HTML generation        → HTML (generateHtmlTemplate)
CSV/Excel              → Spreadsheet File
Bulk processing        → Split In Batches
AI Transform           → AI Transform / Code + LLM
Code (آخرین راهکار)    → Code (runOnceForEachItem / runOnceForAllItems)
```

> **اصل طلایی:** تا جایی که می‌شه از **native nodes** استفاده کن. هر expressionای که تو Set/Filter/Summarize قابل پیاده‌سازی باشه، نباید بره تو Code. Code رو فقط برای الگوریتم‌هایی بزن که با نودهای آماده نشه.
