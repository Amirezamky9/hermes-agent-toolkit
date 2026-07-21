# Flask/Jinja2 HTML Rendering Reference

## The Problem

Flask templates display content in three ways:
1. **Escaped** (`{{ var | e }}`) — HTML tags shown as literal text
2. **Auto-escaped** (`{{ var }}`) — Jinja2 default, escapes `<>&"'`
3. **Raw** (`{{ var | safe }}`) — renders HTML as-is, no escaping

## Decision Matrix

| Scenario | Template filter | Content must be | Risk |
|----------|----------------|-----------------|------|
| User-generated text (comments, bios) | `{{ var }}` (default) | Any | Low — auto-escape handles it |
| CMS/admin-entered HTML (rich text editor) | `{{ var \| safe }}` | Sanitized server-side | Medium — XSS if sanitizer missing |
| Scraped RSS/HTML content | `{{ var \| safe }}` | Sanitized on ingestion | Medium — RSS can contain anything |
| Third-party embeds (YouTube, tweets) | `{{ var \| safe }}` | Sanitized server-side | High — iframe/script injection |

## Common Mistakes

### 1. `| e` on content meant to be HTML
```html
<!-- WRONG: shows <p>tags</p> as text -->
{{ article.content | e }}

<!-- RIGHT: renders paragraphs and links -->
{{ article.content | safe }}
```
**Fix:** Sanitize content on input, then use `| safe`.

### 2. `| safe` without sanitization
```html
<!-- DANGEROUS: renders anything including <script> -->
{{ user_comment | safe }}
```
**Fix:** Never use `| safe` on unsanitized user input. Sanitize first:
```python
from bs4 import BeautifulSoup
ALLOWED_TAGS = {'p', 'a', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'img'}

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED_TAGS:
            tag.unwrap()
    # clean attributes, add target="_blank" to links, etc.
    return str(soup)
```

### 3. Auto-escape doesn't cover all contexts
```html
<!-- SAFE: quotes are escaped -->
<a href="{{ url }}">link</a>

<!-- DANGEROUS: javascript: URLs pass through -->
<a href="{{ user_url }}">link</a>
```
**Fix:** Validate URLs server-side — reject `javascript:`, `data:`, `vbscript:`.

## Sanitization Libraries

| Library | Size | Notes |
|---------|------|-------|
| `bleach` | 200KB | Full-featured, W3C allowlists, maintained |
| Custom `clean_html()` | 0 deps | Lightweight, whitelists specific tags |
| `markupsafe.Markup` | bundled | Only marks as safe, doesn't sanitize |

**Recommendation:** For scraping projects, custom `clean_html()` with BeautifulSoup is sufficient. For user-generated content, use `bleach` with `bleach.ALLOWED_TAGS`.

## Flask-Specific Gotchas

- **`Markup()` in Python** = same as `| safe` in template. Don't use on unsanitized content.
- **`{% autoescape false %}`** disables escaping for a block. Avoid unless content is pre-sanitized.
- **`| e` is redundant** when Jinja2 auto-escaping is on (default). It double-escapes `&` → `&amp;amp;`.
- **Template inheritance:** If `base.html` uses `| safe`, all child templates inherit the risk. Check the base template first.
