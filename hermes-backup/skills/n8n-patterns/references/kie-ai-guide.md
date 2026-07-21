# KIE.AI — راهنمای استفاده در n8n

> به‌صرفه‌ترین گزینه برای تولید تصویر و ویدئو در n8n
> جایگزین DALL-E, Gemini Vision, Runway, HeyGen, Leonardo
> (برگرفته از ۳ ورک‌فلو واقعی در دیتابیس)

## Credential در n8n

Credential type: **Header Auth**
- Header Name: `Authorization`
- Header Value: `Bearer <API_KEY>`

## مدل‌ها

KIE.AI کلی مدل داره — توی پنلش لیست کامل رو ببین. نمونه‌هایی که توی ورک‌فلوهای n8n دیدیم: `kling-2.6`, `wan-2.6`

## پترن Polling (مشترک در همه ورک‌فلوها)

```
POST /v1/{text2video|image2video} → task_id
    ↓
loop:
  Wait 5s
  GET /v1/status/{task_id}
  Switch state:
    success   → extract video_url → download
    fail      → stop/retry
    generating/queuing/waiting → loop
```

## پارامترهای پیشنهادی

| پارامتر | مثال |
|---------|-------|
| `model` | `kling-2.6` |
| `prompt` | توضیح دقیق |
| `image_url` | برای image-to-video |
| `duration` | `5` (ثانیه) |
| `aspect_ratio` | `16:9`, `9:16`, `1:1` |
| `resolution` | `720p`, `1080p` |
| `sound` | `true`/`false` |

## نکات

- نود اختصاصی نداره — `httpRequest` با Header Auth
- همیشه polling loop بذار (Wait + Switch + maxTries)
- `continueOnFail: true` برای HTTP Request در polling
- resolution پایین (720p) برای کاهش هزینه و سرعت بیشتر
