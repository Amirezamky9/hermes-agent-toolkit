# Pattern: Form Input — فرم‌های ورودی کاربر

> Technique key: `form_input`
> جمع‌آوری داده از کاربران از طریق فرم‌های تحت وب

---

## ۱. معرفی

فرم‌های n8n برای سناریوهایی که کاربر باید داده رو از طریق **فرم تحت وب** وارد کنه — ثبت‌نام، نظرسنجی، سفارش، درخواست پشتیبانی.

**موارد استفاده:**
- فرم ثبت سفارش ساده
- فرم چندمرحله‌ای (ثبت‌نام → آدرس → تأیید)
- فرم پشتیبانی
- فرم نظرسنجی

---

## ۲. معماری پایه

### فرم ساده (تک مرحله):
```
[Form Trigger]
    ↓
[Storage Data: ذخیره raw داده]
    ↓
[Process: پردازش (در صورت نیاز)]
    ↓
[Notification / Response]
```

### فرم چندمرحله‌ای:
```
[Form Trigger (مرحله ۱)]
    ↓
[Form (مرحله ۲)]
    ↓
[Form (مرحله ۳)]
    ↓
[Merge / Set: جمع‌آوری همه مراحل]
    ↓
[Storage: ذخیره raw داده]
    ↓
[Process / Notification]
```

---

## ۳. Form Trigger — شروع فرم

> نود: `n8n-nodes-base.formTrigger` (v2.6)

### پارامترهای اصلی:

| پارامتر | توضیح |
|---------|-------|
| `formTitle` | عنوان فرم (اجباری) |
| `formDescription` | توضیحات زیر عنوان (HTML مجاز) |
| `formFields` | فیلدهای فرم |

### تنظیمات (options):

| تنظیم | توضیح | پیش‌فرض |
|-------|-------|---------|
| `appendAttribution` | نمایش "Form automated with n8n" | true ❌ **غیرفعال کن!** |
| `buttonLabel` | متن دکمه ارسال | Submit |
| `path` | آخرین بخش URL فرم | — |
| `respondWithOptions` | پیام بعد از ارسال یا redirect | text |
| `customCss` | استایل سفارشی CSS | — |
| `ignoreBots` | نادیده گرفتن ربات‌ها | false |
| `useWorkflowTimezone` | استفاده از timezone workflow | false |
| `ipWhitelist` | محدودیت IP | — |
| `authentication` | basicAuth / n8nUserAuth / none | none |

### انواع فیلدها:

| `fieldType` | توضیح |
|-----------|-------|
| `text` | متن ساده |
| `number` | عدد |
| `email` | ایمیل با validation خودکار |
| `textarea` | متن بلند |
| `password` | رمز عبور (ماسک شده) |
| `dropdown` | منوی انتخاب (با fieldOptions) |
| `radio` | دکمه رادیویی |
| `checkbox` | چک‌باکس (مفرد یا چندتایی) |
| `date` | انتخاب تاریخ (فرمت YYYY-MM-DD) |
| `file` | آپلود فایل |
| `hiddenField` | فیلد مخفی (برای tracking) |
| `html` | HTML دلخواه (نه script, style, input) |

### نکات مهم:
- **Test URL** فقط برای توسعه — از Production URL برای انتشار استفاده کن
- **هیچ type به اسم `time` وجود نداره** — برای زمان از `text` با placeholder استفاده کن
- فیلد `file` از `acceptFileTypes` برای محدود کردن فرمت فایل پشتیبانی می‌کنه
- `hiddenField` برای پاس دادن داده‌های tracking (مثل source, campaign) مفیده

---

## ۴. Form Node — مراحل بعدی

> نود: `n8n-nodes-base.form` 

برای فرم‌های چندمرحله‌ای، بعد از Form Trigger از `Form` node استفاده کن.

### نحوه کار:
```
Form Trigger (مرحله ۱: نام و ایمیل)
  → Form (مرحله ۲: آدرس)
  → Form (مرحله ۳: تأیید نهایی)
  → Merge/Set: ترکیب داده‌های همه مراحل
  → Storage: ذخیره raw data
```

### نکات:
- هر Form یک صفحه/مرحله‌ست
- فیلدهای داینامیک: با Code node تولید کن و به Form بده
- بین مراحل می‌تونی با IF/Switch مسیریابی کنی

---

## ۵. ذخیره‌سازی — قانون طلایی

> **🔴 CRITICAL: همیشه raw داده رو ذخیره کن!**

| نکته | توضیح |
|------|-------|
| **Set و Merge کافی نیستن** | فقط حافظه موقت — باید یه Storage Node اضافه کنی |
| **زمان ذخیره** | بلافاصله بعد از آخرین مرحله |
| **چی ذخیره کنیم** | raw داده، نه خلاصه یا ویرایش شده |
| **Data Table** | گزینه پیشنهادی برای ذخیره‌سازی داخلی |
| **Google Sheets** | برای بررسی دستی و اشتراک‌گذاری |
| **PostgreSQL** | برای ذخیره دائمی و گزارش‌گیری |

### معماری ذخیره‌سازی:

```
[مراحل فرم] → [Merge/Set] → [Storage Node] → [ادامه پردازش]
                              ↓
                        Data Table / Google Sheets / PostgreSQL
```

---

## ۶. فرم چندمرحله‌ای — جریان کامل

### مرحله به مرحله:

۱. **Form Trigger** — صفحه اول: نام، ایمیل
۲. **IF/Switch** — اگه کاربر "شرکت" رو انتخاب کرد → برو مرحله اطلاعات شرکت، وگرنه برو مرحله اطلاعات شخصی
۳. **Form** — صفحه دوم بر اساس انتخاب کاربر
۴. **Merge / Set** — جمع‌آوری داده‌های مرحله ۱ و ۲
۵. **IF: Validation** — اعتبارسنجی داده
۶. **Loop** — اگه invalid → برگشت به Form با خطا
۷. **Storage** — ذخیره raw داده
۸. **End Page** — نمایش پیام تأیید

### Input Validation (بین مراحل):

```
[مرحله ۱] → [IF: ایمیل معتبر؟]
    ├── yes → [مرحله بعد]
    └── no → [برگشت به مرحله ۱ با خطا]
```

---

## ۷. Dynamic Form Fields

برای فیلدهای داینامیک (مثل dropdown از API):

```
[Code Node: تولید فیلدهای JSON]
    ↓
[Form Node: دریافت JSON]
    ↓
[ادامه]
```

### ساختار JSON فیلد:
```json
{
  "fieldName": "product_id",
  "fieldLabel": "انتخاب محصول",
  "fieldType": "dropdown",
  "fieldOptions": {
    "values": [
      { "option": "قهوه خط یک" },
      { "option": "قهوه خط دو" }
    ]
  },
  "requiredField": true
}
```

---

## ۸. Form Ending — پایان فرم

بعد از آخرین مرحله، کاربر باید یه پیام تأیید ببینه:

| حالت | توضیح |
|------|-------|
| **text** | "اطلاعات شما ثبت شد!" |
| **redirect** | انتقال به URL دلخواه |

> با `respondWithOptions` توی Form Trigger تنظیم می‌شه.

---

## ۹. نودهای معرفی شده

| نود | کاربرد |
|-----|--------|
| `formTrigger` | شروع فرم (صفحه اول) |
| `form` | صفحات بعدی فرم |
| `dataTable` | ذخیره raw داده (پیشنهادی) |
| `googleSheets` | ذخیره برای بررسی دستی |
| `postgres` / `mySql` | ذخیره دائمی |
| `set` | جمع‌آوری داده بین مراحل |
| `merge` | ترکیب داده چند مرحله |
| `if` / `switch` | مسیریابی شرطی بین مراحل |
| `code` | تولید فیلد داینامیک یا validation سفارشی |

---

## ۱۰. خطاهای رایج

### 🕳️ Missing Raw Form Response Storage
هر فرم باید storage node داشته باشه. Set و Merge کافی نیستن.

### 🕳️ Data Loss در Multi-Step
همه مراحل رو قبل از ذخیره با Set/Merge ترکیب کن.

### 🕳️ Wrong Field Names
اسم فیلدها باید با ستون‌های destination یکی باشه.

### 🕳️ فرم آزمایشی
از **Production URL** برای انتشار استفاده کن، نه Test URL.

### 🕳️ n8n Attribution
`appendAttribution: false` رو فراموش نکن — وگرنه "Form automated with n8n" پایین فرم نمایش داده می‌شه.

---

## ۱۱. موارد استفاده در پروژه فروشگاهی

| سناریو | Form Type | ذخیره‌سازی |
|--------|-----------|-----------|
| ثبت سفارش جدید | Multi-step (سفارش → آدرس → تأیید) | Data Table + PostgreSQL |
| درخواست پشتیبانی | Simple (موضوع + متن) | Data Table |
| ثبت‌نام در کانال | Simple (نام + موبایل) | Data Table |
| نظرسنجی | Multi-step با IF/Switch | Data Table |
| آپلود مدارک | Simple با File field | Data Table + Binary |

---