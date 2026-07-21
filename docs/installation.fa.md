# راهنمای نصب Hermes Toolkit

این راهنما نصب کامل پکیج را برای یک Hermes تازه توضیح می‌دهد.

## چه چیزهایی نصب می‌شود؟

- **کلاینت Cookie Sync**: افزونه CacheCat روی سیستم کاربر
- **بک‌اند Cookie Sync**: FastAPI webhook روی سمت Hermes
- **Telegram Toolkit**: جستجو، دانلود، مانیتور و بات‌ها
- **Research Tools**: اسکریپت‌ها و skillهای Agent-Reach
- **Hermes Skills**: `agent-reach`، `deep-research`، `research-manager`، `web-research`، `deep-research-optimized`، `telegram-music-bot`

---

## 0) پیش‌نیازها

### روی سیستم Hermes
- Python 3.10+
- Node.js 18+
- Git
- `pipx` پیشنهاد می‌شود
- `gh` برای GitHub
- `mcporter` برای Exa

### روی سیستم کاربر
- Google Chrome 88+
- امکان نصب افزونه Chrome
- یک پروفایل مرورگر که داخلش لاگین شده باشد (برای تست cookie sync)

---

## 1) کلون مخزن

```bash
git clone https://github.com/Amirezamky9/hermes-agent-toolkit.git
cd hermes-agent-toolkit
```

---

## 2) نصب وابستگی‌های پایتون

```bash
pip install -r requirements.txt
```

اگر محیط جدا می‌خواهی:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) نصب skillها روی Hermes

```bash
cp -r skills/* ~/.hermes/skills/
chmod -R u+rwX ~/.hermes/skills
```

اسکریپت‌ها:

```bash
cp research/scripts/*.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.sh
```

### skillهای موجود
- `agent-reach`
- `deep-research`
- `research-manager`
- `web-research`
- `deep-research-optimized`
- `telegram-music-bot`

---

## 4) تنظیم Agent-Reach

اگر Agent-Reach نصب نیست:

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
agent-reach doctor --json
```

### Agent-Reach چه چیزهایی می‌دهد؟
- Web search با Jina / Exa
- Twitter/X، Reddit، YouTube، GitHub
- Bilibili، Telegram، RSS، V2EX
- Facebook، Instagram، LinkedIn، XiaoHongShu
- Xueqiu و Grok

### backendهای مهم
- `yt-dlp`
- `gh`
- `twitter-cli`
- `rdt-cli`
- `bili-cli`
- `mcporter`
- `telethon`

اگر یک backend در حالت `warn` یا `off` بود، همان را طبق `agent-reach doctor --json` نصب کن.

---

## 5) نصب Telegram Toolkit

مسیر:

```text
telegram-toolkit/
```

### تنظیم اولیه

```bash
cd telegram-toolkit
cp config.yaml.example config.yaml
```

داخل `config.yaml` مقدارهای زیر را بگذار:
- `api_id`
- `api_hash`

### گرفتن API تلگرام
1. برو به https://my.telegram.org/apps
2. یک app بساز
3. `api_id` و `api_hash` را بردار
4. در `telegram-toolkit/config.yaml` قرار بده

### لاگین اول

```bash
python3 cli.py info @telegram
```

شماره تلفن و کد تایید را وارد کن.

### تست سریع

```bash
python3 cli.py search "query" --channel @channel
python3 cli.py download @channel --limit 10
python3 cli.py export @channel --format json
python3 cli.py monitor @channel
```

### بات موسیقی

```bash
python3 music_bot.py search "Hello Adele"
python3 music_bot.py full "Hello Adele" --output /tmp/
```

---

## 6) نصب کلاینت Cookie Sync

کلاینت در این مسیر است:

```text
cookie-sync/client/
```

### build

```bash
cd cookie-sync/client
npm install
npm run build
```

خروجی build:

```text
cookie-sync/client/dist/
```

### نصب در Chrome

1. برو به `chrome://extensions/`
2. **Developer mode** را روشن کن
3. **Load unpacked** را بزن
4. پوشه `cookie-sync/client/dist/` را انتخاب کن
5. آیکون افزونه را می‌بینی

### تنظیم دامنه‌ها
در داشبورد افزونه:
1. تب **Hermes Sync** را باز کن
2. **Enable Hermes Sync** را روشن کن
3. دامنه‌های موردنظر را اضافه کن
   - `google.com`
   - `notebooklm.google.com`
   - `x.com`
4. ذخیره کن

### وظیفه کلاینت
- کوکی‌های دامنه‌های انتخاب‌شده را می‌گیرد
- به بک‌اند می‌فرستد
- هم sync دستی دارد هم auto-sync
- هیچ‌وقت مقدار کوکی را در console لاگ نمی‌کند

---

## 7) نصب بک‌اند Hermes

مسیر بک‌اند:

```text
cookie-sync/backend/
```

### فایل env

```bash
cd cookie-sync/backend
cp .env.example .env
```

مقادیر زیر را تنظیم کن:
- `HERMES_API_KEY`
- `STORAGE_STATE_PATH`
- `BACKEND_HOST`
- `BACKEND_PORT`

### نصب وابستگی‌های بک‌اند

```bash
pip install -r requirements.txt
```

### اجرا

```bash
python main.py
```

مقادیر پیش‌فرض:
- `http://localhost:8000`
- `POST /api/browser-sync`
- `POST /api/test-connection`
- `GET /health`

---

## 8) اتصال کلاینت به بک‌اند

در تنظیمات Hermes Sync افزونه:

- **API URL**: `http://localhost:8000/api/browser-sync`
- **API Key**: همان مقدار `HERMES_API_KEY`

تست:
1. **TEST CONNECTION**
2. **SYNC NOW**
3. بررسی ساخت/آپدیت `storage_state.json`

---

## 9) Cloudflare / دسترسی از راه دور

اگر بک‌اند مستقیم از سیستم کاربر قابل دسترسی نیست:

### گزینه A — Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

بعد در افزونه، API URL را روی URL تونل بگذار:

```text
https://your-tunnel.trycloudflare.com/api/browser-sync
```

### گزینه B — reverse proxy HTTPS
از nginx / Caddy یا هر proxy امن استفاده کن.

### نکته مهم
- اگر ممکن است، HTTPS استفاده کن
- API key هنوز لازم است
- بک‌اند را بدون auth منتشر نکن

---

## 10) تنظیم Hermes

### فایل تنظیم Hermes

این فایل را در root پروژه Hermes بگذار:

```text
cookie-sync/hermes-browser-sync.config.json
```

### کاربرد
- آدرس webhook را مستند می‌کند
- فرمت payload را مشخص می‌کند
- به Hermes می‌گوید `storage_state.json` کجاست

### استفاده معمول در Hermes

```python
context = browser.new_context(storage_state="storage_state.json")
```

اگر Hermes مسیر دیگری دارد، هم در بک‌اند و هم در config همان را تنظیم کن.

---

## 11) چک‌لیست نهایی

### سمت کاربر
- [ ] Chrome نصب است
- [ ] افزونه build شده
- [ ] `dist/` در Chrome load شده
- [ ] دامنه‌ها اضافه شده‌اند
- [ ] Hermes Sync روشن است
- [ ] API URL تنظیم شده
- [ ] API key تنظیم شده

### سمت بک‌اند Hermes
- [ ] وابستگی‌های پایتون نصب شده
- [ ] `.env` ساخته شده
- [ ] بک‌اند اجرا می‌شود
- [ ] `/health` جواب می‌دهد
- [ ] `POST /api/test-connection` کار می‌کند
- [ ] `POST /api/browser-sync` کوکی می‌گیرد

### سمت Hermes agent
- [ ] `agent-reach doctor --json` سالم است
- [ ] skillها به `~/.hermes/skills/` کپی شده‌اند
- [ ] اسکریپت‌ها به `~/.hermes/scripts/` کپی شده‌اند
- [ ] Telegram toolkit تنظیم شده

---

## 12) تست و صحت‌سنجی

### build کلاینت

```bash
cd cookie-sync/client
npm run build
ls dist/
```

### بک‌اند

```bash
cd cookie-sync/backend
python main.py
curl http://localhost:8000/health
```

### Cookie Sync
1. یک دامنه اضافه کن
2. **TEST CONNECTION**
3. **SYNC NOW**
4. بررسی `storage_state.json`

### Hermes

```bash
agent-reach doctor --json
python3 telegram-toolkit/cli.py info @telegram
./research/scripts/research-web.sh "hello world"
```

---

## 13) عیب‌یابی

### build افزونه شکست خورد
- Node.js 18+ را چک کن
- `npm install` را دوباره اجرا کن
- اگر build ابزار خاصی خطا داد، از خروجی `dist/` استفاده کن

### بک‌اند در دسترس نیست
- بررسی کن process بالا باشد
- پورت درست باشد
- اگر پشت NAT هستی، از Cloudflare Tunnel استفاده کن

### کوکی‌ها sync نمی‌شوند
- دامنه‌ها را چک کن
- مطمئن شو سایت واقعاً با دامنه‌های تنظیم‌شده یکی است
- دسترسی افزونه به سایت را چک کن

### Authorization fail می‌شود
- API key داخل افزونه و بک‌اند باید یکی باشد
- مطمئن شو `.env` خوانده می‌شود

### Hermes از storage_state استفاده نمی‌کند
- مسیر `storage_state.json` را در Hermes و بک‌اند یکسان کن
- مطمئن شو Playwright storage state می‌خواند

---

## 14) فایل‌هایی که نباید commit شوند

هرگز این‌ها را commit نکن:
- کوکی واقعی
- `.env`
- `storage_state.json`
- session فایل‌ها
- API key
- token
- config شخصی

فقط از نمونه‌های `.env.example` و config template استفاده کن.

---

## 15) تشکر و منابع

- [Agent-Reach](https://github.com/Panniantong/Agent-Reach)
- [CacheCat](https://github.com/chinmay29hub/CacheCat)
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Exa](https://exa.ai)
- [Jina Reader](https://github.com/jina-ai/reader)
