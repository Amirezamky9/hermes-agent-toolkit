# grok-chat — چت با Grok از ترمینال

ابزاری برای ارسال پیام به Grok (xAI) از طریق Playwright — مستقیماً از ترمینال، اسکریپت‌ها، یا Hermes.

## پیش‌نیازها

- Node.js 18+
- Playwright با Chromium (از طریق gstack یا جداگانه نصب شده)
- کوکی‌های معتبر x.com (`auth_token` + `ct0`)

## شروع سریع

```bash
# پیام ساده
node grok-chat.js "پایتخت فرانسه کجاست؟"

# خروجی JSON (برای اسکریپت‌ها)
node grok-chat.js --json "محاسبات کوانتومی رو در ۳ نکته توضیح بده"

# حالت Deep
node grok-chat.js --mode deep "یک شعر درباره هوش مصنوعی بنویس"

# ذخیره اسکرین‌شات
node grok-chat.js --screenshot /tmp/grok.png "سلام دنیا"

# تنظیم زمان انتظار (میلی‌ثانیه)
node grok-chat.js --timeout 30000 "یک مقاله طولانی درباره تغییرات آب‌وهوا بنویس"
```

## گزینه‌ها

| پرچم | توضیحات | پیش‌فرض |
|------|---------|--------|
| `--mode <fast\|deep>` | حالت فکر کردن Grok | `fast` |
| `--json` | خروجی به صورت JSON | false |
| `--screenshot <مسیر>` | ذخیره اسکرین‌شات | — |
| `--timeout <ms>` | حداکثر زمان انتظار پاسخ | 20000 |
| `--help`, `-h` | نمایش راهنما | — |

## کوکی‌ها

اسکریپت کوکی‌ها را از این منابع بارگذاری میکند (به ترتیب اولویت):

1. **متغیرهای محیطی**: `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`
2. **agent-reach**: `~/.agent-reach/cookies/twitter.env`
3. **agent-reach**: `~/.agent-reach/cookies/x_com.json`

برای دریافت کوکی‌های جدید، از افزونه [Cookie Sync](../../cookie-sync/) استفاده کنید.

## نصب Playwright

اگر قبلاً نصب نشده:

```bash
# از gstack (از قبل موجود)
PLAYWRIGHT_BROWSERS_PATH=~/.cache/ms-playwright node grok-chat.js "سلام"

# یا نصب جداگانه
npm i -g playwright
npx playwright install chromium
```

اگر خطا داد (کتابخونه‌های سیستمی کم هست):

```bash
# Debian/Ubuntu
apt-get install -y libglib2.0-0t64 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libcups2t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 libxfixes3 libgbm1 \
  libcairo2 libasound2 libnspr4 libx11-6 libxcb1 libxcomposite1 libxdamage1 \
  libxrandr2 libxext6 libpango-1.0-0 libpangocairo-1.0-0
```

## خروجی JSON

```json
{
  "success": true,
  "message": "پایتخت فرانسه کجاست؟",
  "response": "پاریس",
  "mode": "fast",
  "timestamp": "2026-07-23T11:00:53.922Z"
}
```

## محدودیت‌ها

- تاریخچه مکالمه ندارد (هر فراخوانی یک نشست جدید است)
- به ساختار DOM توییتر وابسته است — ممکن است با تغییرات توییتر خراب شود
- نیاز به مرورگر headless (~100MB Chromium)
- انتظار پاسخ بر اساس polling است، نه streaming

## نحوه کار

1. Chromium headless را از طریق Playwright اجرا میکند
2. کوکی‌های auth x.com را تنظیم میکند
3. به `x.com/i/grok` میرود
4. پیام را در textarea چت تایپ میکند
5. Enter را فشار میدهد تا ارسال شود
6. متن صفحه را تا تثبیت پاسخ poll میکند (۶ ثانیه بدون تغییر)
7. متن پاسخ را استخراج و تمیز میکند
8. مرورگر را میبندد

## لایسنس

MIT
