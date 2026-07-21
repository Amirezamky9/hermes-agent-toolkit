# Pattern: Async Job Polling Loop — حلقه بررسی وضعیت Job ناهمگام

> Technique key: `async-polling`
> ارسال درخواست به API ناهمگام → بررسی وضعیت → حلقه تا تکمیل → خروجی

---

## ۱. معرفی

خیلی از APIها (تولید تصویر، پردازش ویدئو، CI/CD، ترجمه حجیم) به صورت **ناهمگام** کار میکنن:
1. درخواست بفرست → یه `task_id` بگیر
2. هر چند ثانیه وضعیت رو چک کن
3. وقتی `status == done` بود، نتیجه رو بگیر

این الگو در n8n با **Wait → Check Status → IF → Loop** پیاده میشه.

---

## ۲. معماری

```
[HTTP Request: Submit Job]  ← POST, task_id برمیگردونه
    ↓
[Set: Store Task Data]      ← task_id رو ذخیره کن
    ↓
[Wait: 15 seconds]          ← ⏳ انتظار
    ↓
[HTTP Request: Check Status] ← GET با task_id
    ↓
[IF: Status == done?]       ← شرط
    ├─ TRUE  → [Output]     ← خروجی نهایی
    └─ FALSE → [Wait]       ← 🔙 لوپ برگشت!
```

---

## ۳. نکات کلیدی SDK

### ذخیره task_id برای استفاده در لوپ
```javascript
const storeTaskData = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Store Task Data',
    parameters: {
      mode: 'manual',
      includeOtherFields: true,
      assignments: {
        assignments: [
          { id: 'task-id', name: 'taskId', value: expr('{{ $json.id }}'), type: 'string' }
        ]
      }
    }
  }
});
```

### URL پویا با task_id
```javascript
const checkStatus = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.4,
  config: {
    name: 'Check Job Status',
    parameters: {
      method: 'GET',
      url: expr('{{ "https://api.example.com/result/" + $("Store Task Data").item.json.taskId }}')
    }
  }
});
```

### شرط بررسی وضعیت
```javascript
const isDone = ifElse({
  version: 2.3,
  config: {
    name: 'Job Done?',
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [{
          leftValue: expr('{{ $json.status }}'),
          operator: { type: 'string', operation: 'equals' },
          rightValue: 'done'
        }],
        combinator: 'and'
      }
    }
  }
});
```

### اتصال لوپ (IF false → Wait)
```javascript
// در SDK مستقیم supported نیست — باید از update_workflow استفاده کنی:
// update_workflow({ operations: [
//   { type: 'addConnection', source: 'Job Done?', sourceIndex: 1, target: 'Wait 15 Seconds', targetIndex: 0 }
// ]})
```

---

## ۴. نمونه‌های واقعی

### تولید تصویر (Stability AI)
```
POST /v2beta/stable-image/generate/async  → { id: "abc123" }
GET  /v2beta/stable-image/generate/result/abc123  → { status: "done", image: "base64..." }
```

### ترجمه حجیم (DeepL)
```
POST /v2/translate  → { job_id: "xyz" }
GET  /v2/job/xyz    → { status: "completed", result: "..." }
```

### پردازش ویدئو (Replicate)
```
POST /v1/predictions  → { id: "abc123", status: "starting" }
GET  /v1/predictions/abc123  → { status: "succeeded", output: "url" }
```

---

## ۵.陷阱‌ها

### 🕳️ task_id از بین میره بعد از Wait
**مشکل:** بعد از Wait node، item context ممکنه تغییر کنه.
**راه‌حل:** حتماً از Set node برای ذخیره task_id استفاده کن، و در Check Status از `$("Store Task Data").item.json.taskId` استفاده کن (نه `$json.id`).

### 🕳️ Wait زیادی کوتاه
**مشکل:** بعضی APIها حداقل ۳۰ ثانیه زمان میبرن.
**راه‌حل:** از ۱۵-۳۰ ثانیه شروع کن. اگه API Rate Limit داره، wait رو بیشتر کن.

### 🕳️ حلقه بی‌نهایت
**مشکل:** اگه API هیچوقت `done` برنگردونه، حلقه بی‌نهایت اجرا میشه.
**راه‌حل:** یه counter اضافه کن (max 10 retries) یا timeout بذار.

### 🕳️ Status متفاوت
**مشکل:** بعضی APIها به جای `done` از `completed`، `succeeded`، یا `200` استفاده میکنن.
**راه‌حل:** داکیومنت API رو چک کن. condition رو مطابق تنظیم کن.

### 🕳️ fullResponse لازمه
**مشکل:** بعضی APIها status رو توی header برمیگردونن، نه body.
**راه‌حل:** `options: { response: { response: { fullResponse: true } } }` رو فعال کن.

---

## ۶. تفاوت با Polling Schedule

| ویژگی | Async Polling Loop | Schedule Polling |
|--------|-------------------|-----------------|
| **زمان اجرا** | یه بار اجرا، تا تکمیل لوپ میزنه | هر X دقیقه یه بار اجرا |
| **نود اصلی** | Wait + IF + Loop | Schedule Trigger + Data Table |
| **مناسب برای** | Jobهای < ۵ دقیقه | Jobهای > ۱ ساعت |
| **Complexity** | ساده‌تر | پیچیده‌تر (نیاز به Data Table) |
| **مثال** | تولید تصویر، ترجمه | گزارش روزانه، sync داده |

---

## ۷. نودهای استفاده شده

| نود | کاربرد |
|-----|--------|
| `httpRequest` (POST) | ارسال درخواست اولیه |
| `set` | ذخیره task_id و اطلاعات |
| `wait` | انتظار قبل از بررسی |
| `httpRequest` (GET) | بررسی وضعیت |
| `if` | شرط تکمیل |
| `code` | فرمت خروجی نهایی |
