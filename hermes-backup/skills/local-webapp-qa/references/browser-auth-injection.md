# Browser Auth Injection Patterns

When testing authenticated web apps with headless browsers (Browserbase, Playwright, Puppeteer), the browser session has isolated localStorage/cookies. You cannot share auth state with the user's real browser.

## Pattern 1: Temporary HTML Token Injector

Create a file in the frontend's `public/` directory:

```html
<!DOCTYPE html>
<html>
<body>
<script>
  // Replace TOKEN_VALUE with actual JWT
  localStorage.setItem('auth_token', 'TOKEN_VALUE');
  window.location.href = '/';
</script>
<p>Setting auth token...</p>
</body>
</html>
```

Navigate to `http://localhost:PORT/inject-auth.html` — the browser sets the token and redirects to the app.

**Cleanup:** Delete the file after testing (it's a security risk if left in production).

## Pattern 2: Get Token from Backend API

For Telegram Mini Apps in dev mode (no HMAC validation):

```bash
# Create user and get token
CURRENT_TIME=$(date +%s)
USER_DATA=$(python3 -c "import urllib.parse; print(urllib.parse.quote('{\"id\":12345678,\"first_name\":\"Test\"}'))")
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/validate \
  -H "Content-Type: application/json" \
  -d "{\"init_data\": \"user=${USER_DATA}&auth_date=${CURRENT_TIME}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "$TOKEN"
```

Then inject via Pattern 1 or via browser JS console (if available).

## Pattern 3: Direct API Testing (No UI)

Skip the browser entirely for API-focused testing:

```bash
TOKEN="your-jwt-here"
curl -s http://localhost:8000/api/v1/dashboard \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Useful when you only need to verify backend logic, not visual design.

## Gotchas

- Browserbase sessions are completely isolated — no shared state with user's browser
- `browser_console` with `expression` parameter may be blocked by security policy
- After injecting token, the app may need a full page reload (not just navigation) to pick up the new auth state
- Onboarding completion is per-user — if backend already completed onboarding for this user, the frontend onboarding flow will fail with 403
