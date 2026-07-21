# مستندات Hermes Toolkit (فارسی)

این مخزن سه بخش اصلی دارد:

1. **همگام‌سازی کوکی** — افزونه Chrome مبتنی بر CacheCat روی سیستم کاربر + بک‌اند Hermes
2. **ابزارهای تلگرام** — ابزار جستجو/دانلود/مانیتور با Telethon
3. **ابزارهای ریسرچ** — اسکریپت‌ها و skillهای Agent-Reach برای 16+ پلتفرم

## از کجا شروع کنم؟

- [راهنمای نصب](installation.md)
- [نمای کلی Cookie Sync](../cookie-sync/README.md)
- [کلاینت Cookie Sync](../cookie-sync/client/README.fa.md)
- [بک‌اند Cookie Sync](../cookie-sync/backend/README.fa.md)
- [ابزارهای تلگرام](../telegram-toolkit/README.md)
- [ابزارهای ریسرچ](../research/README.md)

## ساختار فایل‌ها

- `cookie-sync/client/` — افزونه‌ای که کاربر در Chrome نصب می‌کند
- `cookie-sync/backend/` — بک‌اندی که کوکی‌ها را به `storage_state.json` تبدیل می‌کند
- `cookie-sync/hermes-browser-sync.config.json` — فایل راهنمای اتصال برای Hermes
- `telegram-toolkit/` — CLI تلگرام، بات‌ها و دانلود موسیقی
- `research/` — اسکریپت‌های تحقیق روی پلتفرم‌ها
- `skills/` — skillها و رفرنس‌های Hermes

## قوانین امنیتی

- کوکی واقعی، توکن، `.env` و فایل session را هرگز commit نکن
- بک‌اند را پشت HTTPS یا tunnel نگه دار
- در مثال‌ها فقط placeholder استفاده کن

## نصب روی Hermes جدید

1. [راهنمای نصب](installation.md) را بخوان
2. skillها را از `skills/` نصب کن
3. اسکریپت‌ها را از `research/scripts/` کپی کن
4. افزونه را از `cookie-sync/client/` build کن
5. بک‌اند را از `cookie-sync/backend/` اجرا کن
6. دامنه‌ها و API key را تنظیم کن
7. با `agent-reach doctor --json` تست کن

## عیب‌یابی

- اگر افزونه به بک‌اند نرسید، از Cloudflare Tunnel یا یک HTTPS proxy استفاده کن.
- اگر لاگین تلگرام شکست خورد، `telegram-toolkit/telegram.session` را حذف کن و دوباره لاگین کن.
- اگر یک backend ریسرچ نبود، `agent-reach doctor --json` را اجرا کن و channelهای لازم را نصب کن.
