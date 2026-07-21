---
name: local-webapp-access-diagnose
description: Use when a user reports they cannot access a local web app they "built", "set up", or "deployed" (404, blank page, login fails, admin panel won't load, /admin/ won't open). Diagnoses run-state vs code bugs by checking process/port FIRST before reading source.
---

# Local Web App Access Diagnosis

**Most "can't access" reports are "app never started" — not code bugs. Verify run state BEFORE reading source.**

## When to use

Trigger on any of:
- "I built it but can't login"
- "admin panel won't load"
- "404 on localhost"
- "site is blank"
- "I deployed but it doesn't work"
- any local web app access failure

## Step 1: Is it actually running? (CHECK THIS FIRST)

```bash
# Process check
ps aux | grep -iE "python|node|ruby|go|java|flask|gunicorn|uvicorn" | grep -v grep

# Port check (common dev ports)
ss -tlnp 2>/dev/null | grep -E ":(3000|4000|5000|5001|8000|8080|8888)\b"

# If docker was expected
which docker && docker ps -a
```

**No process + no listening port = app is NOT running. Start it. Do not read code yet.**

## Step 2: Identify the runtime

Look for the entry points in this order:
- `docker-compose.yml` / `Dockerfile` → containerized
- `package.json` → Node (read `"scripts"`)
- `requirements.txt` / `pyproject.toml` / `Pipfile` → Python
- `Gemfile` → Ruby
- `go.mod` → Go
- `README.md` → usually has the run command

## Step 3: Standard startup sequences

**Python (no docker):**
```bash
cd /path/to/project
python3 -m venv .venv 2>/dev/null || true
.venv/bin/pip install -q -r requirements.txt
[ -f seed.py ] && .venv/bin/python seed.py   # one-time: creates DB + admin user
.venv/bin/python run.py                       # foreground, or background=true in tool call
```

**Node:**
```bash
cd /path/to/project
npm install
npm start   # or `npm run dev`, check package.json scripts
```

**Docker:**
```bash
which docker || echo "DOCKER NOT INSTALLED — use bare-metal startup instead"
docker compose up --build
```

## Step 4: Verify before declaring victory

```bash
curl -s -o /dev/null -w "homepage: %{http_code}\n" http://localhost:PORT/
curl -s -o /dev/null -w "login:    %{http_code}\n" http://localhost:PORT/auth/login
curl -s -o /dev/null -w "admin:    %{http_code}\n" http://localhost:PORT/admin/
```

- `200` = working
- `302` = redirect (expected for protected pages when unauthenticated)
- `404` = route doesn't exist (route bug, not run-state)
- `500` = server error (check logs)

## Step 5: For login flow specifically (CSRF)

Many Flask/Django apps require a CSRF token. curl-testing login:

```bash
# 1. Fetch login page, grab CSRF token
curl -s -c cookies.txt http://localhost:PORT/auth/login -o /tmp/login.html
CSRF=$(grep -oP 'name="csrf_token"[^>]*value="\K[^"]+' /tmp/login.html | head -1)

# 2. Submit login with cookies + token
curl -s -b cookies.txt -c cookies.txt -L \
  -X POST http://localhost:PORT/auth/login \
  -d "username=admin&password=admin123&csrf_token=$CSRF" \
  -o /tmp/after.html -w "%{http_code}\n"

# 3. Try protected page with same cookies
curl -s -b cookies.txt http://localhost:PORT/admin/ -w "%{http_code}\n"
```

## Step 7: Frontend-backend proxy (Vite/React/Next.js)

**Symptom:** Frontend loads but all API calls return 404. Backend is running on a different port.

**Root cause:** Vite/React dev server doesn't proxy `/api/*` requests to the backend by default.

**Diagnosis:**
```bash
# Check if backend is running
curl -s http://localhost:8000/api/v1/health  # or whatever the backend port is

# Check if frontend is making requests to the wrong origin
# In browser console, look for: Failed to load resource: the server responded with a status of 404
```

**Fix (Vite):** Add proxy to `vite.config.ts`:
```ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // backend port
        changeOrigin: true,
      },
    },
  },
})
```

**Fix (Next.js):** Add `rewrites` to `next.config.js`:
```js
module.exports = {
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' },
    ]
  },
}
```

**After fix:** Restart the frontend dev server.

**Backend SQLite directory:** If backend crashes with `unable to open database file`, the data directory may not exist:
```bash
mkdir -p data  # or wherever DATABASE_URL points
```

## Common pitfalls

- **"I built it" ≠ "I ran it".** Persian "بیلد کردم" often means "set it up / extracted the code". Verify actual run state — never trust the verb.
- **docker not installed.** `docker compose up` fails silently if docker is missing. Always `which docker` first.
- **DB not seeded.** Many apps (Flask + SQLAlchemy especially) need a one-time `seed.py` to create admin users. Check the project root.
- **Long-running apps need background.** Start with `background=true` and capture `session_id` — don't block the main thread.
- **Default credentials live in `seed.py`.** Check it before asking the user for credentials.
- **Read CSRF token from the form, not from memory.** CSRF tokens are session-bound.
- **Don't trust "I built it" → "the app should be up".** This is the #1 false assumption.
- **Windows venv differs from Linux.** On Windows: `python -m venv .venv`, then `.venv\Scripts\activate`, then `pip install -r requirements.txt`, then `python seed.py`, then `python run.py`. If user reports `ModuleNotFoundError: No module named 'flask'`, they skipped pip install or used wrong python.
- **`seed.py` not run = login always fails.** "نام کاربری یا رمز اشتباه است" with correct credentials = DB was never seeded. Fix: `python seed.py` then restart the server.
- **After code changes, restart the server.** Hot-reload is not guaranteed. Kill and restart the process.
- **Content scraping: always sanitize HTML.** When scraping RSS/HTML feeds, don't store raw HTML as article content. Use `bleach` or a custom `clean_html()` that whitelists safe tags (`p`, `a`, `strong`, `em`, `img`, `ul`, `ol`, `li`). Link external sources with `target="_blank" rel="noopener"`.
- **Raw HTML tags visible in browser = template escape issue.** If user sees `<p>text</p><a href="...">link</a>` rendered as text, the template uses `{{ var | e }}` (double-escape). Fix: sanitize content on input, then use `{{ var | safe }}` in template. **NEVER** change `| e` to `| safe` without first verifying the content is sanitized — that opens XSS. See `references/flask-html-rendering.md`.

## Step 6: HTML rendering issues (Flask/Jinja2)

**Symptom:** User sees raw HTML tags like `<p>`, `<a href>` as text in the browser instead of rendered content.

**Root cause:** Template uses `{{ variable | e }}` (escape) on content that should be rendered as HTML.

**Fix path (order matters — don't skip step 1):**
1. **Verify content is sanitized.** Check the code that creates/stores the HTML (scraper, form handler, seed script). If it's scraped from RSS or user-generated, it MUST go through a sanitizer before storage. If you skip this and just swap `| e` → `| safe`, you've opened an XSS vector.
2. **Change `| e` → `| safe`** in the template.
3. **Clear stale DB entries** if they were stored before the sanitizer was added. Re-scrape or re-seed.

**Lightweight sanitizer (no bleach dependency):**
```python
from bs4 import BeautifulSoup
ALLOWED_TAGS = {'p', 'a', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'img'}

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        tag.attrs.clear()
        if tag.name == 'a' and attrs.get('href'):
            tag['href'] = attrs['href']
            tag['target'] = '_blank'
            tag['rel'] = 'noopener'
        elif tag.name == 'img':
            src = attrs.get('src') or attrs.get('data-src')
            if src:
                tag['src'] = src
                tag['alt'] = attrs.get('alt', '')
    return str(soup)
```

**Why `| e` breaks things:** Jinja2 auto-escapes `{{ var }}` by default (safe). Adding `| e` double-escapes HTML entities. Using `| safe` disables escaping entirely. The correct pattern is: **sanitize on input → `| safe` on output**. See `references/flask-html-rendering.md` for the full decision matrix.

## Verification: when you think it's fixed

Always do at least one of:
- `curl` the homepage and login page, confirm 200/302
- Test the actual login flow with cookies + CSRF
- Tell the user the exact URL + credentials to try in their browser

Don't say "fixed" until you've exercised the code path.
