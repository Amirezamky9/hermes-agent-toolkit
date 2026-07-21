---
name: local-webapp-qa
description: QA testing for local dev servers — start services, test with browse tool, use vision analysis for screenshots, handle full-stack apps with separate frontend/backend. Use when user wants to QA test a local project that isn't deployed yet.
triggers:
  - test local app
  - qa local
  - test my app locally
  - run qa on localhost
---

## When to invoke

QA testing when the app runs locally (not deployed). Covers starting dev servers, discovering ports, testing with the browse tool, and evaluating screenshots with vision analysis.

## Workflow

### Phase 1: Discover and Start Services

**Check if servers are already running:**
```bash
curl -s http://localhost:5173 > /dev/null && echo "Frontend on :5173" || echo "Frontend not running"
curl -s http://localhost:3000 > /dev/null && echo "Frontend on :3000" || echo "Frontend not running"
curl -s http://localhost:8000 > /dev/null && echo "Backend on :8000" || echo "Backend not running"
```

**Start missing services (background with notify_on_complete):**
- Frontend: `cd frontend && npm run dev` (typically :5173)
- Backend: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` (typically :8000)

**Backend gotcha — create data directories before starting:**
Many Python backends (SQLite, SQLAlchemy) need a `data/` directory. Check config for DATABASE_URL path and `mkdir -p` the parent before starting.

**Wait for readiness:** Use `curl` health checks, not blind `sleep`.

### Phase 2: Navigate and Test

```bash
~/.hermes/skills/gstack/browse/dist/browse goto http://localhost:PORT
~/.hermes/skills/gstack/browse/dist/browse snapshot -i
~/.hermes/skills/gstack/browse/dist/browse screenshot /path/to/screenshot.png
```

**Test each page:**
1. Navigate to page
2. Take screenshot
3. Get snapshot for interactive elements
4. Click buttons, test forms
5. Check console for errors: `$B console --errors`

### Phase 3: Evaluate with Vision Analysis

Use `vision_analyze` on screenshots to get detailed design/UX feedback:
```python
vision_analyze(
    image_url="/path/to/screenshot.png",
    question="Describe the layout, design quality, and any issues. Is the RTL layout working? Are icons visible? Is the visual hierarchy clear?"
)
```

### Phase 4: Test Responsiveness

```bash
# Mobile viewport
$B viewport 375x812
$B screenshot screenshots/mobile.png

# Desktop viewport
$B viewport 1280x720
$B screenshot screenshots/desktop.png
```

### Phase 5: Document Issues

For each issue found:
1. Screenshot evidence
2. Severity (Critical/High/Medium/Low)
3. Category (Visual/Functional/UX/Content/Performance/Accessibility)
4. Repro steps

### Phase 6: Compute Health Score

Use the standard rubric (Console 15%, Links 10%, Visual 10%, Functional 20%, UX 15%, Performance 10%, Content 5%, Accessibility 15%).

## Pitfalls

- **Vite/proxy misconfiguration (CRITICAL):** Frontend dev servers (Vite, CRA, Next.js) do NOT proxy API requests by default. If `API_BASE = '/api/v1'`, the frontend sends requests to `localhost:5173/api/v1/` which returns 404. Every page that calls the API shows a loading spinner or error state. **Fix:** Add proxy to `vite.config.ts` before testing. See [references/vite-proxy-patterns.md](references/vite-proxy-patterns.md) for exact configs.
- **Auth injection for headless browsers:** Browserbase/headless sessions have isolated localStorage. You cannot test authenticated pages by asking the user to refresh. Use the HTML injector pattern — see [references/browser-auth-injection.md](references/browser-auth-injection.md).
- **Backend data directory missing:** SQLite backends fail silently if the parent directory doesn't exist. Always `mkdir -p` the data path before starting.
- **Auth blocking pages:** If the app has auth, you may need to set a token in localStorage via `$B js "localStorage.setItem('key', 'value')"` to bypass login screens. For Telegram Mini Apps in dev mode, the auth endpoint often skips hash validation — create a test user via `curl -X POST /api/v1/auth/validate` with a fake `init_data` containing a recent `auth_date` timestamp.
- **Stale refs:** After navigation, refs change. Always re-run `snapshot -i` before clicking.
- **Console errors from missing API:** 404s from API calls are expected if testing without a real backend. Note them but don't over-weight.
- **Persian/RTL apps:** Check that text direction, font, and layout are correct. Bottom nav order should be RTL (rightmost = home).
- **Frontend depends on backend:** For full-stack apps, always start the backend BEFORE the frontend. The frontend may silently fail on mount if API calls return errors, showing loading spinners or error states instead of real content.
- **Seed test data before visual QA:** Empty states make design review meaningless. Before taking screenshots, seed the database via API calls: create users, complete onboarding, add items, mark some complete. Read the backend schemas first (Pydantic models or route handlers) to learn required fields — guessing at field names wastes time on 422 errors.
- **Vision API rate limits:** `vision_analyze` and `browser_vision` use external models that rate-limit. If you get 429 errors, wait 10-15 seconds between calls. Batch screenshot analysis or space them out. If rate-limited persistently, take all screenshots first, then analyze them sequentially.
- **CSS changes not visible despite HMR updates:** Vite HMR may report CSS updates (`hmr update /src/styles/globals.css`) but the browser still shows old styles. This happens when: (a) Vite cache is stale, (b) browser aggressively caches CSS. **Fix sequence:** (1) Kill Vite, (2) `rm -rf node_modules/.vite`, (3) Restart Vite, (4) User does hard-refresh (`Ctrl+Shift+R`). If the app uses Tailwind v4 (`@import "tailwindcss"`), custom CSS classes defined after the import are NOT purged — the issue is always browser cache, not Tailwind.
- **Browser session isolation (Browserbase/headless):** When using Browserbase or headless browser sessions, the session has its own localStorage, cookies, and auth state — completely separate from the user's real browser. You CANNOT test authenticated flows by telling the user "refresh the page" — their browser has different state. **Workaround for token injection:** Create a temporary HTML file in `public/` that sets localStorage and redirects:
  ```html
  <script>
    localStorage.setItem('pos_token', 'TOKEN_VALUE');
    window.location.href = '/';
  </script>
  ```
  Navigate to `http://localhost:PORT/auth.html` to inject the token into the headless session. Remember to delete the file after testing.
- **browser_vision returns blank screenshots:** Sometimes `browser_vision` captures a white/blank image even when the page has content (race condition with page load, or headless browser rendering issue). **Workaround:** Save the screenshot with `$B screenshot /path/file.png`, then use `vision_analyze(image_url="/path/file.png", question="...")` on the saved file — this reads the file directly and works reliably. Don't trust `browser_vision` analysis when the result says "blank" or "white".
