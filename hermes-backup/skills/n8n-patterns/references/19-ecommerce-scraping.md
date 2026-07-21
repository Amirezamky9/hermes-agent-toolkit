# E-Commerce Scraping — Two-Pass Product + Price Scraper

## Pattern Overview

A two-pass scraping strategy for e-commerce sites:

1. **Pass 1** — Scrape a category/shop listing page to collect all product links
2. **Pass 2** — Visit each product page individually to extract name, price, seller data

Suitable for sites like Torob, Digikala, and other Persian e-commerce platforms.

## Node Sequence

```
ManualTrigger / ScheduleTrigger
  → HTTP Request (GET category page)
    → WebpageContentExtractor (parse HTML → JSON)
      → HTML Extract (a[href] → array of links)
        → Split Out (array → individual items)
          → Filter (relative paths, no external URLs)
            → Loop Over Items (batches of 1)
              → HTTP Request (GET product page)
                → HTML Extract (selectors per product)
                  → Set (structure output)
                    → Wait (rate-limit delay)
```

## Key Techniques

### Link Filtering

Filter node with AND conditions:

| Condition | Operator | Purpose |
|-----------|----------|---------|
| `$json.link` | `not empty` | Skip nulls |
| `$json.link` | `not contains "https"` | Keep relative paths only |
| `$json.link` | `not contains "shop"` | Skip non-product paths |

### Rate-Limit Throttle

Use `Wait` node in the loop body (default 1-2 s). For conservative builds: 2-3 s.

### Price Structure Parsing

JavaScript expression inside `Set` node to parse raw HTML price blocks:

```javascript
$json.price.map(item => {
  const s = String(item);
  const parts = s.split('\n');
  const price = (parts[0] || '').trim();
  const match = s.match(/\[(.*?)\]/);
  const link = match ? match[1].trim() : '';
  return [link, price];
});
```

## Common Pitfalls

- **Persian/Arabic numerals** — prices come as `۱۲۳,۴۵۶` not `123,456`. Add a digit conversion node after the Set to map `۰-۹` → `0-9` before numeric processing.
- **CSS selector fragility** — sites change class names. If `.price-credit` breaks, inspect the live HTML and update selectors.
- **No pagination** — this pattern scrapes page 1 only. For multi-page, add a pagination loop (track `?page=N` query param).
- **Blocking** — too many requests without delay = 403/429. Always include `Wait`.
- **Community node required** — `WebpageContentExtractor` must be installed via n8n Settings → Community Nodes → Install `n8n-nodes-webpage-content-extractor`.

## When to Use

- Price monitoring / competitor analysis
- Product catalog backups
- Building a local price comparison dataset
- Data enrichment for existing product databases

## Sample Output Shape

```json
{
  "name": "Product Title",
  "top5price": [
    ["/seller/link/1", "۱,۲۳۴,۰۰۰"],
    ["/seller/link/2", "۱,۱۰۰,۰۰۰"]
  ]
}
```
