# Web — Jina Reader + RSS

## Backend: Jina Reader (web pages)

### Read any web page as clean markdown
```bash
curl -s "https://r.jina.ai/https://example.com/article"
```

### Search via Jina
```bash
curl -s "https://r.jina.ai/search?q=YOUR+QUERY" -H "Accept: text/plain"
```

### Custom headers (set user-agent, accept-language, etc.)
```bash
curl -s "https://r.jina.ai/URL" -H "Accept-Language: zh-CN,zh;q=0.9"
```

## Backend: feedparser (RSS/Atom)

### Read any RSS feed
```bash
python3 -c "
import feedparser, json
feed = feedparser.parse('https://hnrss.org/frontpage')
entries = [{ 'title': e.title, 'link': e.link, 'published': e.get('published', ''), 'summary': e.get('summary', '')[:200] } for e in feed.entries[:5]]
print(json.dumps(entries, indent=2, default=str))
"
```

### Single-entry check by URL
```bash
python3 -c "
import feedparser
feed = feedparser.parse('URL')
for e in feed.entries[:3]:
    print(f'{e.title}\n  {e.link}\n')
"
```

## Pitfalls
- Jina may fail on pages behind Cloudflare / aggressive bot protection
- Some sites block Jina's IP range — fall back to direct curl with proper UA
- RSS feeds with authentication required won't work without credentials
