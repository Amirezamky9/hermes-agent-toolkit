# Iranian Job Sites — Scraping Reference

## Site Profiles

### Divar.ir (دیوار)
Iran's largest classifieds platform.
- **Structure**: City → Category → Listings
- **URL pattern**: `https://divar.ir/s/{city}/list/{category}`
  - Shahroud accounting: `/s/shahrud/list/jobs-accountant`
  - All Shahroud jobs: `/s/shahrud/list/jobs`
  - Iranian-wide jobs: `/s/iran/list/jobs`
- **Content Delivery**: SSR with HTML + React hydration. Post card titles are in `<h2 class="kt-post-card__title">`, prices in `<span class="kt-post-card__description">`. Data-token attributes link to individual posts.
- **API**: POST to `https://api.divar.ir/v8/web-search/{city}/{category}` with body `{"json_schema":{}}` and header `x-api-key: anonymous`. But requires up-to-date app version.
- **Job categories** (via URL slug): `jobs-accountant`, `jobs`, `finance-legal-jobs`
- **Rate limits**: modest; 10-15 req/min with browser UA works.

### Sheypoor.com (شیپور)
- **URL pattern**: `https://www.sheypoor.com/s/{city}/{category}`
  - Shahroud jobs: `/s/shahrud/jobs`
  - Shahroud accounting: `/s/shahrud/accounting-finance`
  - Sales: `/s/shahrud/sales-expert`
- **Content**: Mostly SSR, but some items loaded via JS.
- **Category slugs**: `accounting-finance`, `sales-expert`, `chef-cooking`, `nurse`, `office-clerk-secretary`, `driver`, `technician`, `managerial-positions`, `other-jobs`

### Jobinja.ir (جابینجا)
- **URL**: `https://jobinja.ir/jobs?filters%5Bkeywords%5D%5B%5D={term}`
- **Content**: Fully JS-rendered (React). Hard to scrape directly.
- **Workaround**: Use DuckDuckGo HTML search to find jobinja listings, or add `&sort=best` to keyword searches.
- **API**: `/api/jobs` endpoint returns `{"message": "messages.api_not_found"}` — no public API.

### e-estekhdam.com (ای استخدام)
- **URL**: `https://www.e-estekhdam.com/search/{term}`
- **Status**: Cloudflare-protected, blocks most scrapers.
- **Workaround**: DuckDuckGo may show cached snippets.

### Jooiakar.com
- **URL**: `https://www.jooiakar.com/search/job/shahrood`
- **Status**: JS-rendered, not easily scrapable.

## Recommended Search Strategy (Iranian Jobs)

1. **Start with DuckDuckGo HTML search**: `https://html.duckduckgo.com/html/?q=site:divar.ir+شاهرود+حسابدار+پاره+وقت`
   - Returns result titles + snippets + redirect links
   - Snippets often contain key details (pay, hours, dates)

2. **Direct scrape Divar** for city+category pages
   - Use `curl` with proper Persian headers
   - Extract from `<h2.kt-post-card__title>` and `<span.kt-post-card__description>`

3. **Sheypoor** for category overview
   - Get category links from the jobs page, then drill into each

4. **Report format**: Markdown table with Title, Pay, Category, and direct link.

## Persian Language Notes
- Header: `Accept-Language: fa-IR,fa;q=0.9,en;q=0.8`
- Character class: `[\u0600-\u06FB]` covers standard Persian/Arabic
- Persian digits are U+06F0–U+06F9 (۰-۹), not ASCII 0-9
- Unicode normalize Persian text: use `unicodedata.normalize('NFKC', text)` to fold different forms of ی and ک
