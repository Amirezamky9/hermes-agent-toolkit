# Products Cache Data Table Pattern

> Pattern for caching shop products in an n8n Data Table with dynamic inline keyboards via HTTP Request.

## Schema

| Column | Type | Notes |
|--------|------|-------|
| `name` | string | Product display name |
| `category` | string | Internal key (e.g. `arabica`, `robusta`, `blend50`) |
| `category_display` | string | Persian display name (e.g. `عربیکا ۱۰۰٪`). **Must be stored in DB, not hardcoded.** |
| `price_250` | number | Price for 250g. 0 = not available |
| `price_500` | number | Price for 500g |
| `price_750` | number | Price for 750g |
| `price_1000` | number | Price for 1kg |
| `stock_250` | number | Stock for 250g |
| `stock_500` | number | Stock for 500g |
| `stock_750` | number | Stock for 750g |
| `stock_1000` | number | Stock for 1kg |
| `is_active` | boolean | `true`: visible. `false`: hidden (no physical delete) |

## Key principles

1. **`category_display` in DB, not in code** — admin changes category names without touching the workflow
2. **Price 0 = weight not available** — Code checks `Number(price) > 0` before rendering
3. **Callback prefixes**: `menu_` (category list), `product_` (product detail), `cart_add_` (add to cart with weight)
4. **Main Menu builds dynamically**: scans all products for unique categories, builds 2-per-row keyboard from `category_display`
5. **Category view**: filters products by category via `input.first().json.rows`

## Callback routing

| Prefix | Router output | Action |
|--------|---------------|--------|
| `menu_main` | Callback[0] | Show main menu (edits current message) |
| `menu_{category}` | Callback[1] | Show products in category |
| `product_{id}` | Callback[2] | Show product detail + weight selector |
| `cart_add_{id}_{weight}` | Callback[3] | Add to cart |
| `cart_view` | Callback[4] | View cart |
| `cart_remove_{idx}` | Callback[5] | Remove from cart |

## HTTP Request vs Telegram node

- **Main Menu**: HTTP Request (`editMessageText`) — dynamic categories from DB
- **Category list**: HTTP Request (`editMessageText`) — dynamic products/weights from DB
- **Weight selector**: HTTP Request (`editMessageText`) — dynamic available weights
- **/menu command**: HTTP Request (`sendMessage`) — sends **new** message (not edit)
- **/start welcome**: Telegram node (`sendMessage`) — static content, no dynamic keys needed

All HTTP Request nodes use `$credentials('bale_bot_evet_rosteri').accessToken` embedded in the URL — no credential assignment needed.
