# RSS-Based Web Scraping for Flask News Apps

## Why RSS over HTML scraping
- RSS feeds are structured XML — no fragile CSS selectors
- Most gaming/tech news sites publish RSS feeds
- Less likely to be blocked (RSS is meant for aggregation)
- Parses with `beautifulsoup4` + `lxml` for XML mode

## Pattern

```python
import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 ...'}

def fetch_rss(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, 'xml')  # lxml parser
    except Exception as e:
        print(f"RSS error: {e}")
        return None

def parse_feed(soup, source_name):
    articles = []
    for item in soup.find_all('item')[:10]:
        title = item.find('title').text.strip()
        link = item.find('link').text.strip()
        desc = item.find('description').text.strip()
        
        # Image extraction — try media:content first, then content:encoded
        image = ''
        media = item.find('media:content')
        if media and media.get('url'):
            image = media['url']
        content = item.find('content:encoded')
        if content and not image:
            img = BeautifulSoup(content.text, 'html.parser').find('img')
            if img and img.get('src'):
                image = img['src']
        
        desc_clean = BeautifulSoup(desc, 'html.parser').get_text()[:300]
        articles.append({...})
    return articles
```

## Known working RSS feeds (gaming)
| Site | Feed URL |
|------|----------|
| VG247 | `https://www.vg247.com/feed` |
| PC Gamer | `https://www.pcgamer.com/rss/` |
| Rock Paper Shotgun | `https://www.rockpapershotgun.com/feed` |

## Category auto-detection
Use keyword matching against article title + summary:
```python
CATEGORY_KEYWORDS = {
    'action': ['action', 'shooter', 'combat', 'battle', 'fortnite'],
    'rpg': ['rpg', 'role-playing', 'final fantasy', 'elden ring'],
    'sports': ['sport', 'football', 'fifa', 'racing'],
    # ...
}
```

## Required packages
```
requests==2.32.3
beautifulsoup4==4.12.3
lxml==5.2.2        # XML parser for BS4
```

## Admin integration
Add a `/admin/scrape` POST route that:
1. Calls `scrape_all()`
2. Deduplicates by slug
3. Auto-categorizes
4. Inserts new articles
5. Shows flash message with count
