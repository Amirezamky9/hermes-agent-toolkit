# SPA API Reverse Engineering via JS Bundle Analysis

## When to Use
When a website is a Single Page Application (SPA) with no public API docs, and you need to discover its backend API endpoints, authentication methods, and data flows.

## Technique

### Step 1: Identify SPA Framework
```bash
curl -sL "https://example.com/" | grep -oP 'src="[^"]*\.js[^"]*"'
```
Look for:
- `__NEXT_DATA__` → Next.js
- `__NUXT__` → Nuxt.js
- Webpack chunk patterns → Vue/React with Webpack
- Vite module patterns → Vite-based SPA

### Step 2: Download JS Bundles
```bash
# Download all JS bundles from the page
curl -sL "https://example.com/" | grep -oP 'src="(//[^"]*\.js[^"]*)"' | sed 's/src="//;s/"//' | while read js; do
  [[ "$js" == //* ]] && js="https:$js"
  curl -sL "$js" -o "/tmp/bundle_$(basename "$js")" 2>/dev/null
done
```

### Step 3: Extract API Endpoints
```bash
# Find all API paths
grep -ohP '"/api[^"]*"' /tmp/bundle_*.js | sort -u

# Find fetch/axios patterns
grep -oP '(fetch|axios|request|post|get)\s*\(\s*[`"'"'"'][^`"'"'"']*[`"'"'"']' /tmp/bundle_*.js | sort -u

# Find full URL patterns
grep -ohP 'https?://[a-zA-Z0-9._/-]+/api[a-zA-Z0-9._/-]*' /tmp/bundle_*.js | sort -u
```

### Step 4: Search for Feature Keywords
```bash
# Search for specific feature-related terms
grep -ohP '(image|generat|task|job|submit|async|poll|create|upload|download)[a-zA-Z0-9_/]{0,60}' /tmp/bundle_*.js | sort | uniq -c | sort -rn | head -20
```

### Step 5: Check i18n/Translation Files
Translation files often reveal feature names and API endpoints:
```bash
grep -oP '"[^"]*api[^"]*"' /tmp/bundle_*.js | sort -u
# Chinese apps: search for 图片(图像), 生成(生成), 绘画(创作)
grep -P '[\x{4e00}-\x{9fff}]' /tmp/bundle_*.js | head -20
```

### Step 6: Test Discovered Endpoints
```bash
# Test with curl
curl -s -X POST "https://example.com/api/v1/task-polling" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Pitfalls

1. **SPA HTML is empty** — The initial HTML response only contains `<div id="app"></div>` and script tags. Content is rendered by JS. You MUST download and analyze the JS bundles.

2. **Swagger/OpenAPI endpoints return SPA HTML** — Many SPAs serve their index.html for any route (including `/swagger.json`, `/openapi.json`, `/api-docs`). A 200 status doesn't mean the endpoint exists — check if the response is actual JSON or just the SPA shell.

3. **Task-polling ≠ Image generation** — The presence of a `task-polling` endpoint doesn't necessarily mean image generation. It could be for feedback cases, order status, or any async operation. Check the context in the JS code.

4. **Translation files reveal features** — i18n JSON embedded in JS bundles often contains feature names, UI labels, and API-related strings that reveal functionality not visible in the main code.

5. **Multiple domains** — SPAs often split across domains: `example.com` (frontend), `api.example.com` (backend), `cdn.example.com` (assets). Check all domains for API endpoints.

## Real-World Example: LongCat.ai Research

**Discovery process:**
1. `longcat.ai` → SPA with Vue.js, served empty HTML
2. Downloaded main JS bundle (621KB) → found `fetch('/api/v1/login-info')` and `fetch('/api/v1/wx-config')`
3. Found platform at `longcat.chat/platform/` → another SPA
4. Downloaded platform JS bundles → found 40+ API endpoints including:
   - `/api/lc-platform/v1/model/list` → only LongCat-2.0
   - `/api/lc-platform/v1/task-polling` → POST required, needs session login
   - `/api/pay/commercial/...` → payment endpoints
5. API endpoint `https://api.longcat.chat/openai/v1/chat/completions` → OpenAI-compatible chat only
6. Model list returned only `LongCat-2.0` (text LLM, 1M context, 131K output)
7. **Conclusion:** No image generation API found despite user's claim

**Key learning:** When a user insists a service has a capability you can't find, do exhaustive research (all JS bundles, all domains, i18n files, API testing) before concluding. But also trust your evidence — if thorough research shows no evidence, say so honestly.
