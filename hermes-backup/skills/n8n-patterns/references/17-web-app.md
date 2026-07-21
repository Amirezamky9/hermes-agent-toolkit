# Best Practices: Web App Workflows (SPA served from a webhook)

> Technique key: `web_app` — Serving a single-page application (HTML + JS) from a webhook — dashboards, admin UIs, forms that need custom rendering

## Architecture

Webhook (responseNode) → Code node (build HTML) → respondToWebhook (Content-Type: text/html).

Serve a single-page application from an n8n webhook. The workflow fetches data, then renders a full HTML page with a client-side framework (Alpine.js + Tailwind via CDN is the default stack — no build step needed).

## File-based HTML (REQUIRED for pages > ~50 lines)

Write the HTML to a separate file (e.g., `chunks/dashboard.html`), then in SDK TypeScript code use `readFileSync` + `JSON.stringify` to safely embed in a Code node. This eliminates ALL escaping problems:

1. Write full HTML (CSS, JS, Alpine.js/Tailwind) to `chunks/page.html`
2. In `src/workflow.ts`: `const htmlTemplate = readFileSync(join(__dirname, '../chunks/page.html'), 'utf8');`
3. Use `JSON.stringify(htmlTemplate)` to create a safe JS string literal
4. For data injection, embed a `__DATA_PLACEHOLDER__` token and replace at runtime

**Do not embed large HTML directly in `jsCode`** — neither as template literals nor as arrays of quoted lines. Always use file-based pattern.

## Data Injection Patterns

- **Static page**: embed HTML directly, no placeholder
- **Dynamic data**: `<script id="__data" type="application/json">__DATA_PLACEHOLDER__</script>`. Code replaces `__DATA_PLACEHOLDER__` with base64-encoded JSON. Client: `JSON.parse(atob(document.getElementById('__data').textContent))`
- Do NOT put bare `{{ $json... }}` in HTML string parameter — they won't be evaluated

## Multi-route SPA

Use multiple webhooks in one workflow — one serves HTML, others serve JSON API endpoints. HTML's JS uses `fetch()` to call sibling webhook paths.

## Responding Correctly

Use `respondToWebhook` with `respondWith: "text"`, put HTML in `responseBody` via expression, set `Content-Type: text/html; charset=utf-8`.

## Recommended Nodes
- **Webhook** (n8n-nodes-base.webhook): Multiple for multi-route (GET/POST for different paths)
- **Data Table** (n8n-nodes-base.dataTable): Fetch/update backend data
- **Code** (n8n-nodes-base.code): Build HTML with `runOnceForAllItems` mode
- **Aggregate** (n8n-nodes-base.aggregate): Combine all items into one JSON array
- **respondToWebhook** (n8n-nodes-base.respondToWebhook): Return rendered page

## Common Pitfalls
- Large HTML breaks jsCode — use file-based pattern
- Data injection via n8n expressions in HTML doesn't work — use `__DATA_PLACEHOLDER__`
- Missing Content-Type header shows raw HTML in browser