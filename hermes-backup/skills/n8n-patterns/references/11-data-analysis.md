# Best Practices: Data Analysis

> Technique key: `data_analysis` — Examining data to find patterns, trends, anomalies, or insights
>
> MCP documentation: not available (built from general n8n knowledge + real node definitions)

---

## ۱. نودهای اصلی

| نود | ورژن | قابلیت‌ها | نکته |
|-----|------|-----------|------|
| **Summarize** | 1.1 | sum, count, countUnique, average, max, min, append, concatenate + split by field | بدون Code اکثر تحلیل‌ها رو می‌کشه |
| **Filter** | 2.3 | شرط‌های ترکیبی (and/or) روی فیلدها با type validation | جایگزین IF برای فیلتر ساده |
| **Item Lists** | 3.1 | sort, limit, removeDuplicates, concatenateItems, splitOutItems, **summarize** (pivot) | ۶ تا operation تو یه نود |
| **Code** | 2 | JS/Python sandbox (بدون network) | **آخرین راهکار** — native nodes همیشه اول |
| **IF** | 2.3 | true/false routing با expression | برای threshold checks |
| **Switch** | 3.4 | multi-way routing با rules یا expression | برای دسته‌بندی مقادیر |
| **Data Table** | 1.1 | get با filter, orderBy, returnAll; rowExists; upsert | ذخیره + query تاریخی |
| **Aggregate** | 1 | تبدیل N آیتم به ۱ آیتم با array | برعکس Split Out |
| **Convert To File** | 1.1 | csv, xls, xlsx, html, json, ods | خروجی گزارش |
| **Sum** | — | تابع expression تو Set/Code | برای جمع ساده نیازی به Summarize نیست |

---

## ۲. زیرساخت کلی تحلیل داده

```
[Trigger: Schedule / Webhook / DataTable / Form / HTTP]
    ↓
[Filter: پالایش اولیه — حذف null, outlier, ناقص‌ها]
    ↓
[Summarize / Item Lists: محاسبات آماری — avg, sum, count, sort]
    ↓
[IF / Code: بررسی threshold — anomaly detection]
    ↓
[Branch: دو مسیر]
    ├── نرمال → [DataTable: ذخیره] → پایان
    └── آنومالی → [Notification: تلگرام/ایمیل/اسلک] + [DataTable: ذخیره با تگ anomaly]
```

---

## ۳. پترن ۱: Summarize Pure (بدون Code)

**سناریو:** آمار فروش روزانه — مجموع، میانگین، بیشترین، کمترین

```
[Schedule Trigger: هر روز ۸ صبح]
    ↓
[DataTable: get از جدول سفارشات روز قبل]
    ↓
[Summarize: مجموع قیمت + میانگین + count]
    │  aggregation: sum    → field: amount
    │  aggregation: average → field: amount
    │  aggregation: count
    ↓
[Set: فرمت کردن خروجی]
    │  summary_text: "فروش دیروز: {{ $json.sum_amount }} تومان
    │                 میانگین: {{ $json.average_amount }}
    │                 تعداد: {{ $json.count }}"
    ↓
[Telegram / Email: ارسال گزارش]
```

**نکته:** `fieldsToSummarize` می‌تونه چندتا aggregation همزمان داشته باشه. `fieldsToSplitBy` هم می‌تونه گروه‌بندی کنه (مثلاً group by `category`).

---

## ۴. پترن ۲: Group By + Multiple Aggregation

**سناریو:** تفکیک فروش به تفکیک دسته‌بندی — مجموع و تعداد هر دسته

```
[DataTable: get همه رکوردها]
    ↓
[Summarize: group by + چندتا aggregation]
    │  fieldsToSplitBy: "category"
    │  aggregation: sum    → field: amount
    │  aggregation: count
    │  aggregation: average → field: amount
    ↓
[Sort: بر اساس sum_amount نزولی]
    ↓
[Convert To File: xlsx — خروجی Excel]
```

**معادل Code (اگه کلاً ۱۰۰۰ خط باشه):**
```javascript
// Run Once for All Items
const groups = {};
for (const item of $input.all()) {
  const cat = item.json.category || 'unknown';
  if (!groups[cat]) groups[cat] = { sum: 0, count: 0, amounts: [] };
  groups[cat].sum += Number(item.json.amount) || 0;
  groups[cat].count++;
  groups[cat].amounts.push(Number(item.json.amount) || 0);
}
return Object.entries(groups).map(([category, g]) => ({
  category,
  sum: g.sum,
  avg: g.sum / g.count,
  count: g.count,
}));
```

---

## ۵. پترن ۳: Anomaly Detection + Alerting

**سناریو:** مانیتورینگ خطاهای API — اگه error rate > 5% بزن تلگرام

```
[Schedule Trigger: هر ۱۵ دقیقه]
    ↓
[DataTable: get خطاهای ۱ ساعت اخیر]
    │  filter: { createdAt > $now - 3600 }
    ↓
[DataTable: get کل درخواست‌های ۱ ساعت اخیر]
    ↓
[Code: محاسبه error rate]
    │  (خطاها / کل) * 100
    ↓
[Filter: error_rate > 5]
    ↓
[Switch: روی مقدار anomaly_type]
    ├── critical → [Telegram: آلرت فوری] + [DataTable: insert با severity=critical]
    └── warning  → [DataTable: insert با severity=warning]
```

**نوع anomaly که می‌تونی detect کنی:**

| نوع | منطق | مثال |
|-----|------|------|
| **Threshold** | value > max OR value < min | دما > ۴۰ |
| **Z-Score** | (value - mean) / stddev > 3 | ترافیک غیرعادی |
| **Rate Change** | (current - previous) / previous > 0.2 | افزایش ۲۰٪ |
| **Missing Data** | count امروز < count دیروز | لاگ قطع شده |
| **Duplicate** | removeDuplicates روی ID | رکورد تکراری |

---

## ۶. پترن ۴: Moving Average / Trend Analysis

**سناریو:** روند ۷ روز اخیر فروش با میانگین متحرک

```
[Schedule: هر روز]
    ↓
[DataTable: get ۳۰ روز اخیر — orderBy createdAt ASC]
    ↓
[Code: Run Once for All Items — محاسبه moving average]
    │  const items = $input.all();
    │  const window = 7;
    │  return items.map((item, i) => {
    │    const slice = items.slice(Math.max(0, i - window + 1), i + 1);
    │    const avg = slice.reduce((s, x) => s + Number(x.json.amount), 0) / slice.length;
    │    return { ...item.json, moving_avg_7: avg };
    │  });
    ↓
[Summarize: max, min, last_value]
    ↓
[IF: روند نزولی ۳ روز پشت سر هم؟]
    ├── true → [Telegram: هشدار]
    └── false → [DataTable: ذخیره روند]
```

---

## ۷. پترن ۵: Webhook Data → Validation → Aggregate → Report

**سناریو:** دریافت داده از فرم/API، validate، aggregate و ارسال گزارش

```
[Webhook / Form Trigger: دریافت response]
    ↓
[Code: validation]
    │  if (!$json.email || !$json.amount) throw new Error('missing fields');
    │  if (isNaN($json.amount)) throw new Error('invalid amount');
    │  return $json;
    ↓
[DataTable: upsert — ذخیره]
    ↓
[Summarize: آمار لحظه‌ای]
    │  aggregation: count
    │  aggregation: sum → field: amount
    ↓
[Set: فرمت خروجی]
    │  report: "تعداد کل: {{ $json.count }} | مجموع: {{ $json.sum_amount }}"
    ↓
[Webhook Response: برگردوندن به سرویس caller]
```

---

## ۸. پترن ۶: Real-time Threshold Alert (بدون ذخیره‌سازی)

**سناریو:** وب‌هوک لحظه‌ای سنسور — اگه از حد گذشت فوری اطلاع بده

```
[Webhook: سنسور دما]
    ↓
[IF: temperature > 40]
    ├── true → [Telegram: 🔥 هشدار دمای بالا]
    │            ↓
    │          [HTTP: خاموش کردن سنسور / API]
    └── false → [ پایان — نیازی به ذخیره نیست]
```

این ساده‌ترین پترن analysis هست — حتی به Summarize هم نیاز نداره.

---

## ۹. پترن ۷: Pivot Table با Item Lists (Summarize operation)

Item Lists با operation=summarize می‌تونه pivot table درست کنه:

```
[DataTable / HTTP: دیتای فروش]
    ↓
[Item Lists: operation=summarize — Pivot]
    │  groupBy: "region"
    │  values:
    │    - aggregation: sum → field: revenue
    │    - aggregation: count
    │    - aggregation: average → field: revenue
    ↓
[Item Lists: operation=sort — بر اساس sum_revenue DESC]
    ↓
[Convert To File: csv]
```

**مقایسه Summarize vs Item Lists (operation=summarize):**

| ویژگی | Summarize | Item Lists (summarize) |
|-------|-----------|----------------------|
| aggregation | sum, avg, count, max, min, append, concatenate | مثل Summarize + pivot style |
| split by field | ✅ | ✅ |
| output format | separateItems / singleItem | like Summarize |
| sort بعدی | نیاز به نود جدا | ✅ تو همون نود نیست |
| version | 1.1 | 3.1 |

> قانون: اگه **فقط** summarize می‌خوای و بعدش sort/limit هم داری، از **Item Lists** استفاده کن (چند operation تو یه نود). اگه فقط aggregation ساده می‌خوای، **Summarize** خواناتره.

---

## ۱۰. نودهای کمکی

| نود | کاربرد در تحلیل |
|-----|----------------|
| **Set** | فرمت‌دهی خروجی، اضافه کردن فیلدهای محاسباتی ساده |
| **Code** | الگوریتم‌های پیچیده (moving average, z-score, regression) |
| **Filter** | حذف outlier, null, ناقص پیش از تحلیل |
| **Merge** | ترکیب دیتا از دو مسیر مختلف (مثلاً خطاها + کل) |
| **Item Lists** (operation: removeDuplicates) | حذف رکورد تکراری قبل از count |
| **Item Lists** (operation: limit) | فقط Top N |
| **DateTime** | تبدیل بازه زمانی، فیلتر تاریخ |
| **Convert To File** | خروجی Excel/CSV/HTML گزارش |
| **DataTable** | ذخیره historical data + query با filter/orderBy |

---

## ۱۱. تله‌ها

| تله | راه‌حل |
|-----|--------|
| **Summarize روی فیلد null/undefined** | `skipEmptySplitFields: true` + `continueIfFieldNotFound: true` |
| **Type mismatch در Filter** | `looseTypeValidation: true` یا Cast با Set قبلش |
| **Code Sandbox بدون network** | برای API از HTTP Request استفاده کن، نه Code |
| **Code سنگین روی ۱۰۰۰۰+ آیتم** | timeout می‌خوری. بکن تکه‌تکه با Filter و Loop |
| **DataTable query بدون filter** | کل دیتا برمی‌گردونه. همیشه `limit` یا `filter` بذار |
| **Group by روی فیلد با تنوع بالا** | خروجی غیرقابل استفاده. اول دسته‌بندی کن با Switch/Code |
| **فراموشی sorting قبل از moving average** | ترتیب data مهمه. همیشه `orderBy createdAt` بذار |
| **تغییر فرمت اعداد موقع Convert To File** | locale رو چک کن. بعضی فرمت‌ها `,` و `.` رو برعکس interpret می‌کنن |
| **دو بار execution همزمان** | برای DataTable analysis از Schedule با overlap prevention استفاده کن |
| **Anomaly false positive** | همیشه یه hysteresis بذار (۲ بار پشت سر هم قبل از آلرت) |

---

## ۱۲. Summary

```
Simple stats     → Summarize
Group by + stats → Summarize (fieldsToSplitBy)
Sort + Limit     → Item Lists (sort, limit)
Pivot table      → Item Lists (summarize)
Complex logic    → Code (آخرین راهکار)
Alerting         → IF + Notification
Historical       → DataTable + Summarize
Trend            → Code (moving average)
Report output    → Convert To File / Google Sheets / Telegram
```

> **اصل:** تا جایی که می‌شه از native nodes (Summarize, Filter, Item Lists) استفاده کن. Code رو فقط برای الگوریتم‌هایی بزن که با نودهای آماده نشه (moving average, z-score, regression, ...).
