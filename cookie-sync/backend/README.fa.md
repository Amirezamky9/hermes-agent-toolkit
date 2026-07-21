# بک‌اند Hermes Cookie Sync (فارسی)

این بک‌اند روی **سمت Hermes** اجرا می‌شود و کوکی‌هایی را که افزونه از سیستم کاربر می‌فرستد دریافت می‌کند.

## وظیفه

- دریافت cookie payload از افزونه
- ذخیره آن به فرمت Playwright `storage_state.json`
- merge کردن cookieهای جدید با state قبلی
- فراهم کردن `/health` و `test-connection`

## فایل‌ها

- `main.py` — برنامه FastAPI
- `requirements.txt` — dependencyها
- `.env.example` — template تنظیمات

## نصب

```bash
cd cookie-sync/backend
cp .env.example .env
pip install -r requirements.txt
python main.py
```

## متغیرهای محیطی

- `HERMES_API_KEY` — کلید مشترک بین افزونه و بک‌اند
- `STORAGE_STATE_PATH` — مسیر ذخیره Playwright state
- `BACKEND_HOST` — host اجرا
- `BACKEND_PORT` — port اجرا

## API

### `POST /api/browser-sync`
کوکی‌ها را از افزونه می‌گیرد و در storage state می‌نویسد.

### `POST /api/test-connection`
برای تست اتصال.

### `GET /health`
بررسی سلامت سرویس.

## Cloudflare / دسترسی بیرونی

اگر بک‌اند مستقیم از سیستم کاربر قابل دسترسی نیست، آن را پشت Cloudflare Tunnel یا HTTPS proxy بگذار.

مثال:

```bash
cloudflared tunnel --url http://localhost:8000
```

بعد URL تونل را در افزونه وارد کن.

## امنیت

- API key را محرمانه نگه دار
- بک‌اند را بدون auth عمومی نکن
- `storage_state.json` را commit نکن

## استفاده در Hermes

در پروژه Hermes، Playwright را با فایل ذخیره‌شده باز کن:

```python
context = browser.new_context(storage_state="storage_state.json")
```

## منابع

- [CacheCat](https://github.com/chinmay29hub/CacheCat)
- [Client README](../client/README.fa.md)
- [English docs](../../docs/README.en.md)
