# n8n Expressions — توابع و متغیرهای درون `{{ }}`

> مجموعه کامل متغیرها، توابع، و پترن‌های Expression در n8n. این فایل مرجع تمام transformations با expression هست — بدون نیاز به Code node.

---

## فهرست

1. [متغیرهای در دسترس](#۱-متغیرهای-در-دسترس)
2. [روش استفاده](#۲-روش-استفاده)
3. [String Operations](#۳-string-operations)
4. [Number Operations](#۴-number-operations)
5. [Boolean / Ternary](#۵-boolean--ternary)
6. [Array Operations](#۶-array-operations)
7. [Luxon DateTime (تاریخ و زمان)](#۷-luxon-datetime-تاریخ-و-زمان)
8. [دسترسی به نودهای دیگر](#۸-دسترسی-به-نودهای-دیگر)
9. [JSON و Object](#۹-json-و-object)
10. [پترن‌های کاربردی](#۱۰-پترنهای-کاربردی)
11. [تله‌ها](#۱۱-تلهها)

---

## ۱. متغیرهای در دسترس

| متغیر | معنی | مثال |
|-------|------|------|
| `$json` | دیتای آیتم جاری از **نود قبلی** | `$json.name`, `$json.price` |
| `$('NodeName')` | دسترسی به خروجی نود مشخص (جفت شده با آیتم جاری) | `$('Fetch').item.json.price` |
| `$input.first()` | اولین آیتم از نود قبلی | |
| `$input.all()` | همه آیتم‌های نود قبلی | `$input.all().map(i => i.json.name)` |
| `$input.item` | آیتم جاری (فقط تو Code runOnceForEachItem) | |
| `$binary` | دیتای باینری آیتم جاری | |
| `$now` | زمان فعلی — **Luxon DateTime** | `$now.toISO()`, `$now.toFormat('yyyy-MM-dd')` |
| `$today` | شروع امروز — **Luxon DateTime** | `$today.plus(7, 'days')` |
| `$itemIndex` | ایندکس آیتم جاری (0-based) | |
| `$runIndex` | شماره اجرای جاری | |
| `$execution.id` | ID یکتای execution | |
| `$execution.mode` | `'test'` یا `'production'` | |
| `$workflow.id` | ID ورک‌فلو | |
| `$workflow.name` | نام ورک‌فلو | |

---

## ۲. روش استفاده

همه expressionها داخل `{{ }}` نوشته می‌شن و با `expr()` در SDK یا مستقیم در UI مقداردهی می‌شن:

```
درست:    Hello {{ $json.name }}, welcome!
درست:    Report for {{ $now.toFormat("MMMM d, yyyy") }} — {{ $json.title }}
درست:    {{ $json.firstName }} {{ $json.lastName }}
درست:    Total: {{ $json.items.length }} items, updated {{ $now.toISO() }}
درست:    Status: {{ $json.count > 0 ? "active" : "empty" }}
```

**نکته مهم:** `$()` و `$json` و `$now` فقط **داخل** `{{ }}` معنی دارن. بیرونش کار نمی‌کنن.

---

## ۳. String Operations

```javascript
$json.name.toUpperCase()                        // حروف بزرگ
$json.name.toLowerCase()                        // حروف کوچک
$json.title.trim()                              // حذف فضای خالی اطراف
$json.email.includes('@')                       // چک کردن包含
$json.phone.replace(/[^0-9]/g, '')              // حذف غیرعددی
$json.fullName.split(' ')[0]                    //提取 اسم اول
$json.code.substring(0, 5)                      // ۵ کاراکتر اول
$json.text.slice(0, 100)                        // ۱۰۰ کاراکتر اول
$json.url.startsWith('https://')                // شروع با
$json.file.endsWith('.pdf')                     // پایان با
$json.name || 'Unknown'                         // fallback اگر null/undefined
$json.name ?? 'Unknown'                         // fallback فقط undefined
$json.tags.join(', ')                           // آرایه به رشته
```

---

## ۴. Number Operations

```javascript
Number($json.price)                                    // تبدیل string به number
Number($json.price).toFixed(2)                         // دو رقم اعشار
Math.round($json.rate * 100) / 100                     // رند به ۲ رقم اعشار
Math.ceil($json.value)                                 // گرد به بالا
Math.floor($json.value)                                // گرد به پایین
Math.abs($json.diff)                                   // قدر مطلق
Math.max($json.value, 0)                               // حداقل ۰ (clamp پایین)
Math.min($json.value, 100)                             // حداکثر ۱۰۰ (clamp بالا)
$json.price * $json.qty                                // ضرب
($json.total / $json.count).toFixed(2)                 // میانگین
$json.price ?? 0                                       // اگر null باشه ۰ بذار
```

---

## ۵. Boolean / Ternary

```javascript
$json.count > 0 ? 'active' : 'empty'                   // شرط دو حالته
$json.role === 'admin' ? 'full' : $json.role === 'editor' ? 'edit' : 'view'  // چند حالته
$json.name || 'Unknown'                                 // fallback
$json.price ?? 0                                        // nullish coalescing
!$json.email                                            // negate
$json.completed === true ? '✅' : '❌'                  // boolean به icon
Boolean($json.count)                                    // تبدیل به boolean
```

---

## ۶. Array Operations

```javascript
$json.items.length                                     // تعداد آیتم‌ها
$json.items.join(', ')                                 // به رشته
$json.items.slice(0, 5)                                // ۵ تای اول
$json.items.filter(i => i.active)                      // فیلتر
$json.items.map(i => i.name)                           // فقط اسم‌ها
$json.items.find(i => i.id === targetId)               // پیدا کردن اولین
$json.items.every(i => i.completed)                    // همه تکمیل شدن؟
$json.items.some(i => i.error)                         // حداقل یکی error داره؟
$json.items.includes(targetValue)                      // شامل مقدار X هست؟
```

> توابع Array (`map`, `filter`, `find`, ...) معمولاً تو **HTML template** یا **Set (mode: raw)** بیشتر کاربرد دارن. برای Sort/Limit از **Item Lists** استفاده کن نه expression.

---

## ۷. Luxon DateTime (تاریخ و زمان)

### توابع پرکاربرد

```javascript
$now.toISO()                                            // 2026-07-09T18:30:00.000Z
$now.toISODate()                                        // 2026-07-09
$now.toISO({suppressMilliseconds: true})                // suppress میلی‌ثانیه
$now.toRFC2822()                                        // Thu, 09 Jul 2026 18:30:00 +0000
$now.toFormat('yyyy-MM-dd')                             // 2026-07-09
$now.toFormat('yyyy/MM/dd HH:mm:ss')                    // 2026/07/09 18:30:00
$now.toMillis()                                         // timestamp (ms)
$now.toSeconds()                                        // timestamp (s)
```

### جمع و تفریق

```javascript
$now.plus({ days: 7 })                                  // ۷ روز بعد
$now.plus({ hours: 2, minutes: 30 })                    // ۲:۳۰ بعد
$now.minus({ months: 1 })                               // ۱ ماه قبل
$now.minus({ years: 1, months: 6 })                     // ۱.۵ سال قبل
$today.plus(1, 'days')                                  // فردا
```

### شروع و پایان بازه

```javascript
$now.startOf('month')                                   // اول ماه جاری
$now.endOf('month')                                     // آخر ماه جاری
$now.startOf('week')                                    // اول هفته
$now.endOf('week')                                      // آخر هفته
$now.startOf('year')                                    // اول سال
$now.endOf('day')                                       // ۲۳:۵۹:۵۹ امروز
```

### تفاوت بین دو تاریخ

```javascript
$now.diff($today, 'days').toObject()                    // { days: 5.3 }
$now.diff($today, 'hours').toObject()                   // { hours: 127 }
$now.diff($('Start Date').item.json.date, 'days').values // تفاوت بر حسب روز
$now.diff($json.createdAt, 'hours').hours               // فقط مقدار عددی
```

### استخراج بخشی از تاریخ

```javascript
$now.year                                               // 2026
$now.month                                              // 7 (1-based)
$now.day                                                // 9
$now.hour                                               // 18 (24h)
$now.minute                                             // 30
$now.second                                             // 0
$now.weekday                                            // 4 (Mon=1, Sun=7)
$now.weekNumber                                         // 28
$now.daysInMonth                                        // 31
$now.quarter                                            // 3
```

### فرمت‌های پرکاربرد (Luxon Tokens)

| Token | خروجی | توضیح |
|-------|-------|-------|
| `yyyy` | 2026 | سال ۴ رقمی |
| `yy` | 26 | سال ۲ رقمی |
| `MMMM` | July | نام ماه کامل |
| `MMM` | Jul | نام ماه مختصر |
| `MM` | 07 | ماه ۲ رقمی |
| `dd` | 09 | روز ۲ رقمی |
| `HH` | 18 | ساعت ۲۴ ساعتی |
| `hh` | 06 | ساعت ۱۲ ساعتی |
| `mm` | 30 | دقیقه |
| `ss` | 00 | ثانیه |
| `a` | AM/PM | |
| `yyyy-MM-dd` | 2026-07-09 | |
| `yyyy/MM/dd HH:mm` | 2026/07/09 18:30 | |
| `MMMM dd, yyyy` | July 09, 2026 | |

---

## ۸. دسترسی به نودهای دیگر

### روش درست (داخل `{{ }}`)

```javascript
// دسترسی به فیلد از نود مشخص — جفت شده با آیتم جاری
$('Fetch API').item.json.price
$('Form Trigger').item.json.body.email

// همه آیتم‌های یه نود — برای ساخت option, summary, concat
$('Source').all().map(i => ({ option: i.json.name }))
$('Fetch Projects').all().map(i => ({ option: i.json.name }))

// مقدار از اولین آیتم یه نود
$('Config Node').first().json.apiKey
```

### نکات حیاتی دسترسی بین نودی

| نکته | توضیح | مثال |
|------|-------|------|
| **`$json` فقط نود قبلی رو می‌ده** | اگه بینش Set/Merge بوده، `$json` دیگه فیلدهای قدیمی رو نداره | `$('Fetch').item.json.price` |
| **`.first()` نگیر مگر واقعاً اولین رو بخوای** | تو multi-item همه آیتم‌ها از همون کپی می‌گیرن | |
| **AI Agent subnodeها** | `$json` تو agent subnodeها (memory, model, retriever, tools) بی‌اعتباره | `nodeJson(telegramTrigger, 'message.chat.id')` |
| **Multi-branch fan-in** | بعد از IF/Switch/Merge، `$json` فقط ورودی همون branch رو داره | `$('User Lookup').item.json.id` |
| **بعد از Set با Keep Only** | Set با `includeOtherFields=false` همه فیلدها رو حذف می‌کنه | از `$('Before Set').item.json` استفاده کن |

### روش غلط

```javascript
// غلط — $() بیرون {{ }}
expr('{{ ' + JSON.stringify($('Source').all().map(i => i.json.name)) + ' }}')
// درست:
expr('{{ $("Source").all().map(i => ({ option: i.json.name })) }}')

// غلط — .first() تو multi-item
$('Node').first().json.field  // ← این همیشه آیتم ۰ رو میده
// درست:
$('Node').item.json.field     // ← آیتم جفت شده با آیتم جاری
```

---

## ۹. JSON و Object

```javascript
// String → JSON
JSON.parse($json.rawData)

// JSON → String
JSON.stringify($json.data)

// ساختن object
{ key: 'value', count: $json.items.length }

// دسترسی با bracket notation (برای اسم فیلد داینامیک)
$json[$json.fieldName]

// Spread operator (فقط تو Raw Mode Set یا HTML template)
{ ...$json.data, extraField: 'value' }
```

---

## ۱۰. پترن‌های کاربردی

### ۱۰.۱. Fallbackهای امن

```javascript
$json.name || 'Unknown'              // اگر null/undefined/empty → Unknown
$json.price ?? 0                     // فقط اگر null/undefined → ۰
$json.email || 'no-email@unknown.com'
Number($json.age) || 0               // اگر NaN شد → ۰
```

### ۱۰.۲. تبدیل و نرمالایز

```javascript
// ایمیل به حروف کوچک
$json.email.toLowerCase().trim()

// حذف همه کاراکترهای غیرعددی از تلفن
$json.phone.replace(/[^0-9]/g, '')

// قیمت با دو رقم اعشار
Number($json.price).toFixed(2)

// نام کامل از firstName + lastName
$json.firstName + ' ' + $json.lastName
```

### ۱۰.۳. شرط‌های چندلایه

```javascript
// دسته‌بندی قیمت
$json.amount > 1000 ? 'high' : $json.amount > 100 ? 'medium' : 'low'

// وضعیت سفارش
$json.status === 'completed' ? '✅'
  : $json.status === 'pending' ? '⏳'
  : $json.status === 'cancelled' ? '❌'
  : '❓'

// چک کردن وجود فیلد
$json.email && $json.email.includes('@') ? 'valid' : 'invalid'
```

### ۱۰.۴. ترکیب تاریخ و متن

```javascript
// گزارش با تاریخ
'Report for ' + $now.toFormat('yyyy-MM-dd')

// لاگ خطا
'Error at ' + $now.toISO() + ': ' + $json.error

// مدت زمان گذشته
Math.floor($now.diff($json.createdAt, 'hours').hours) + ' hours ago'
```

### ۱۰.۵. دسترسی به Config/Environment

```javascript
// API URL از یک نود Config
$('Config').first().json.apiUrl

// تنظیمات از Form Trigger
$('Form Trigger').item.json.body.timezone

// Threshold از یک نود Set قبلی
$('Thresholds').item.json.maxPrice
```

---

## ۱۱. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **`$json` بعد از Set/Merge عوض می‌شه** | برای فیلدهای قبلی از `$('Node').item.json.field` استفاده کن |
| 2 | **`$()` بیرون `{{ }}`** | فقط داخل `{{ }}` معنی داره |
| 3 | **`.first()` تو multi-item** | همه آیتم‌ها از مقدار آیتم ۰ کپی می‌گیرن. از `.item.json` استفاده کن |
| 4 | **Null/undefined بدون fallback** | expression پشت سر هم fail می‌کنه. همیشه `||` یا `??` بذار |
| 5 | **Number با کاما (locale issue)** | `Number("۱٬۰۰۰")` → NaN. اول replace کن: `Number($json.str.replace(/,/g, ''))` |
| 6 | **`$json` تو AI Agent subnode** | بی‌اعتباره. حتماً از `nodeJson(trigger, 'path')` استفاده کن |
| 7 | **Type در Set فراموش شده** | مثلاً عدد رو به‌عنوان string ذخیره می‌کنه. همیشه `type: number` رو چک کن |
| 8 | **NaN بدون بررسی** | `Number($json.price) || 0` — اگر NaN بشه، ۰ برمی‌گردونه |
| 9 | **`$now` vs `$today`** | `$now` شامل زمان هست. `$today` شروع روزه (midnight) |
| 10 | **Regex-intensive expression** | expression سنگین می‌تونه performance رو بزنه. واسه پردازش پیچیده از Code استفاده کن |

---

## خلاصه

```javascript
// پرکاربردترین‌ها
$json.field                          // مقدار فیلد
Number($json.field)                  // تبدیل به عدد
$json.field || 'default'             // fallback
$now.toFormat('yyyy-MM-dd')          // تاریخ امروز
$now.plus({days: 7}).toISODate()    // ۷ روز بعد
$json.name.toLowerCase().trim()      // نرمالایز
$('Node').item.json.field            // دسترسی به نود دیگه
$json.count > 0 ? 'yes' : 'no'       // شرط
```
