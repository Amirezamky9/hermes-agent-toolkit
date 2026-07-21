# افزونه Cookie Sync (فارسی)

این افزونه روی **سیستم کاربر** نصب می‌شود و کوکی‌های دامنه‌های انتخاب‌شده را به بک‌اند Hermes می‌فرستد.

## این بخش دقیقاً چه می‌کند؟

- Cookieهای سایت‌های مشخص‌شده را می‌خواند
- از طریق webhook به بک‌اند می‌فرستد
- با `storage_state.json` کار می‌کند
- برای سینک sessionهای authenticated در Hermes استفاده می‌شود

## ساختار

- `manifest.json` — تنظیمات Chrome Extension
- `src/background/` — منطق sync و cookie capture
- `src/dashboard/` — رابط تنظیمات و Hermes Sync tab
- `dist/` — خروجی build برای نصب در Chrome

## پیش‌نیازها

- Chrome 88+
- Node.js 18+
- npm

## Build

```bash
cd cookie-sync/client
npm install
npm run build
```

خروجی در `cookie-sync/client/dist/` ساخته می‌شود.

## نصب در Chrome

1. `chrome://extensions/` را باز کن
2. **Developer mode** را روشن کن
3. **Load unpacked** را بزن
4. پوشه `cookie-sync/client/dist/` را انتخاب کن
5. افزونه بالا می‌آید

## تنظیم Hermes Sync

داخل داشبورد افزونه:

1. تب **Hermes Sync** را باز کن
2. **Enable Hermes Sync** را روشن کن
3. آدرس بک‌اند Hermes را وارد کن
   - مثال: `http://localhost:8000/api/browser-sync`
   - یا URL تونل Cloudflare
4. API Key را وارد کن
5. دامنه‌ها را اضافه کن
   - `google.com`
   - `notebooklm.google.com`
   - `x.com`
6. **Save** را بزن

## Sync دستی

1. دامنه‌ها را تنظیم کن
2. **SYNC NOW** را بزن
3. افزونه کوکی‌ها را به بک‌اند می‌فرستد

## Auto-sync

اگر **Auto-Sync** روشن باشد، با تغییر cookie در دامنه‌های تنظیم‌شده، افزونه خودش sync می‌کند.

## نکته‌های مهم

- هیچ‌وقت مقدار کوکی را در console چاپ نکن
- فقط دامنه‌های لازم را اضافه کن
- از پروفایل مرورگر مخصوص Hermes استفاده کن

## خطاهای رایج

### build fail شد
- مطمئن شو Node.js 18+ نصب است
- `npm install` را دوباره اجرا کن

### backend در دسترس نیست
- آدرس backend را چک کن
- اگر از بیرون شبکه به آن دسترسی نیست، Cloudflare Tunnel بگذار

### کوکی sync نشد
- دامنه‌ها را دقیق وارد کن
- مطمئن شو روی همان سایت login شده‌ای

## منابع

- [CacheCat](https://github.com/chinmay29hub/CacheCat)
- [Backend README](../backend/README.fa.md)
- [English docs](../../docs/README.en.md)
