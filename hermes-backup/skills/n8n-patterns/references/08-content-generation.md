# Best Practices: Content Generation

> Technique key: `content_generation`
> تولید خودکار محتوا — متن، تصویر، ویدئو، پست شبکه‌های اجتماعی، خبرنامه، blog

---

## ۱. معرفی

**اصل مهم:** برای **متن** از LLM (GPT-4o-mini, Claude Haiku) استفاده کن. برای **تصویر و ویدئو** از **KIE.AI** استفاده کن (API ارزان، تنوع مدل). مدل‌های گرون (DALL-E, Gemini Vision, Runway, HeyGen) برای تولید روزمره به‌صرفه نیستن.

---

## ۲. KIE.AI — راهنمای کامل (از ۳ ورک‌فلو واقعی)

> نود اختصاصی نداره — همه با `httpRequest` انجام می‌دن.

**Credential:** Header Auth با `Authorization: Bearer YOUR_API_KEY`

### مدل‌ها:
> KIE.AI کلی مدل داره — **توی وبسایتش** لیست کامل مدل‌ها (ویدئو، تصویر، صدا) رو می‌تونی ببینی. مدل‌ها مرتب آپدیت می‌شن.
> 
> اونایی که توی ورک‌فلوهای n8n دیدیم: `kling-2.6`, `wan-2.6` + مدل‌های دیگه (برو توی panel kie.ai چک کن).

### پترن کلی Polling (مشترک در هر ۳ ورک‌فلو):

```
[Manual Trigger / Schedule]
    ↓
[Set: پارامترها (prompt, image_url, duration, aspect_ratio, model)]
    ↓
[HTTP POST: https://api.kie.ai/v1/{text2video|image2video}]
    ↓
[Wait: 5 ثانیه]
    ↓
[HTTP GET: polling status task]
    ↓
[Switch: بر اساس state]
    ├── "success"   → [Code: استخراج video_url] → [HTTP: دانلود ویدئو]
    ├── "fail"      → [Stop: خطا]
    ├── "generating" → [Wait loop]
    ├── "queuing"   → [Wait loop]
    └── "waiting"   → [Wait loop]
```

### پارامترهای درخواست:
| پارامتر | مثال |
|---------|-------|
| `model` | `kling-2.6` یا `wan-2.6` |
| `prompt` | "A cat walking on a sunny beach" |
| `image_url` | https://... (برای image-to-video) |
| `duration` | `5` (ثانیه) |
| `aspect_ratio` | `16:9` یا `9:16` یا `1:1` |
| `resolution` | `720p` یا `1080p` |

---

## ۳. زیرساخت کلی

```
[Trigger: Schedule / Webhook / Telegram / RSS / Manual]
    ↓
[Text Generation: LLM (GPT-4o-mini / Claude Haiku)]
    ↓
[Image/Video: KIE.AI API → httpRequest]
    ↓
[Processing: Output Parser / Markdown / Edit Image]
    ↓
[Publishing: WordPress / Facebook / Telegram / Instagram]
```

---

## ۴. پترن ۱: Social Media Post (Telegram → AI + Multi-Platform)

```
[Telegram Trigger]
    ↓
[Switch: type]
    ├── text   → [LLM: caption مخصوص هر پلتفرم]
    ├── voice  → [Whisper: متن] → [LLM: caption]
    ├── photo  → [دانلود] → [LLM: تحلیل + caption]
    └── video  → [دانلود] → [LLM: تحلیل + caption]
    ↓
[Output Parser: JSON array]
    ↓
[Upload Post به Facebook / Instagram / Twitter / LinkedIn]
    ↓
[Telegram: تأیید انتشار]
```

---

## ۵. پترن ۲: AI Blog + Featured Image (KIE.AI)

```
[Schedule Trigger (weekly)]
    ↓
[LLM: تحقیق + تولید مقاله]
    ↓
[KIE.AI: تولید تصویر شاخص از موضوع]
    ↓
[WordPress: انتشار post]
```

---

## ۶. پترن ۳: News Digest روزانه

```
[RSS / Schedule Trigger]
    ↓
[RSS Feed Read: چند منبع]
    ↓
[LLM: خلاصه ۴۰۰ کلمه‌ای]
    ↓
[KIE.AI: تصویر شاخص]
    ↓
[Telegram / Newsletter]
```

---

## ۷. پترن ۴: AI Video از Prompt (KIE.AI)

> برگرفته از ورک‌فلوهای واقعی 54168686, 4a8aefaf, b551634b

```
[Schedule / Manual Trigger]
    ↓
[Set: prompt + model + duration + aspect_ratio]
    │  model options: "kling-2.6", "wan-2.6"
    ↓
[HTTP POST: KIE.AI (ایجاد task)]
    ↓
┌── Polling Loop ─────────────┐
│  [Wait: 5s]                 │
│  [HTTP GET: status/{taskId}] │
│  [Switch: state]             │
│   ├── success → خروج        │
│   ├── fail → خطا             │
│   └── generating → لوپ      │
└─────────────────────────────┘
    ↓
[Code: استخراج video_url]
    ↓
[HTTP: دانلود ویدئو]
    ↓
[Telegram: ارسال ویدئو]
```

---

## ۸. نودهای پیشنهادی

| نود | کار |
|-----|-----|
| `httpRequest` | KIE.AI + APIهای خارجی |
| `openAi` | متن، Whisper، TTS |
| `lmChatOpenAi` (gpt-4o-mini) | متن روزمره |
| `lmChatAnthropic` (haiku) | متن سریع |
| `switch` | مسیریابی state polling |
| `wait` | فاصله polling |
| `code` | استخراج result |
| `wordpress` / `webflow` | انتشار blog |
| `facebookGraphApi` | اینستاگرام/فیسبوک |
| `telegram` / `slack` | نوتیفیکیشن |

---

## ۹. تله‌ها

| تله | راه‌حل |
|-----|--------|
| **Polling بی‌نهایت** | maxTries بذار (مثلاً ۲۰ بار) |
| **API Key در Expression** | از credential استفاده کن |
| **ویدئو دانلود نشد** | `continueOnFail` + fallback |
| **حجم ویدئو زیاد** | resolution پایین (720p) |
| **AI Output ناقص** | OutputParserStructured |
