# Search — Exa AI search via mcporter

## Prerequisites

- Exa API key obtained
- `mcporter` installed (`npm install -g mcporter`) — needed for `mcporter call` commands, but NOT needed to save the config

## Setup: adding Exa as an mcporter MCP server

### ⚠️ Pitfall: Config file does NOT require mcporter installed (2026-07-19)

The config file `~/.mcporter/mcporter.json` is just JSON — **create it directly** when the user gives you an API key. Do NOT jump to installing Node.js + mcporter first. User explicitly corrected: "inside agent-reach check exactly where it's saved, just change that, I don't think anything needs to be installed."

**Correct sequence:**
1. Write `~/.mcporter/mcporter.json` with the API key
2. Test with direct curl: `curl -s "https://api.exa.ai/search" -H "Content-Type: application/json" -H "x-api-key: KEY" -d '{"query":"test","numResults":1}'`
3. Only install mcporter later if user wants `agent-reach doctor` to show Exa as `ok`

**Wrong sequence:** suggest installing Node.js + mcporter before saving the config.

### Free tier (no API key — simplest path)
```bash
mcporter config add exa https://mcp.exa.ai/mcp
mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'  # verify
```
**Pitfall**: `mcporter config add` writes to workspace-local `config/mcporter.json` by default. On servers, prefer `~/.mcporter/mcporter.json` for persistence.

### With API key (higher rate limits)

`mcporter config add` does **not** support `--header` from the CLI. Write the config JSON directly:

**`~/.mcporter/mcporter.json` (global):**
```json
{
  "mcpServers": {
    "exa": {
      "baseUrl": "https://mcp.exa.ai/mcp",
      "headers": {
        "x-api-key": "YOUR_EXA_API_KEY"
      }
    }
  }
}
```

### Verify the config
```bash
mcporter config list                # shows configured servers
cat ~/.mcporter/mcporter.json       # confirm headers block is present
```

### ⚠️ Pitfall: Config placement
**Never put mcporter.json in workspace** (`/workspace/config/mcporter.json`) — workspace can be wiped at any time. Always use `~/.mcporter/mcporter.json` (global, persists across workspace changes).

### Quick smoke test
```bash
mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'
```

Expected output includes a `Title` and `URL`. A 401 means the API key header is missing.

## Backend: Exa via mcporter

### Web search
```bash
mcporter call 'exa.web_search_exa(query: "latest LLM agent frameworks 2026", numResults: 5)'
```

### Automatic embeddings search
```bash
mcporter call 'exa.find_similar_links_exa(url: "https://example.com", numResults: 5)'
```

### Direct HTTP (without mcporter, for standalone testing / verifying the API key alone)
```bash
python3 -c "
import urllib.request, json
body = json.dumps({'query': 'test', 'numResults': 1}).encode()
req = urllib.request.Request(
    'https://api.exa.ai/search',
    data=body,
    headers={'Content-Type': 'application/json', 'x-api-key': 'YOUR_KEY'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=15) as resp:
    print(json.dumps(json.loads(resp.read()), indent=2))
"
```

## Fallback chain (when primary search is blocked/down)

1. **Exa via mcporter** (primary — semantic search, best quality)
2. **Jina Search** — `curl -s "https://r.jina.ai/search?q=QUERY" -H "Accept: text/plain"` (needs API key for search endpoint)
3. **Yahoo HTML search** — works when DuckDuckGo/Google block bots:
   ```bash
   curl -sL --compressed "https://search.yahoo.com/search?p=QUERY" \
     -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" | \
     python3 -c "
   import sys, re, html
   data = sys.stdin.read()
   titles = re.findall(r'<h3[^>]*>(.*?)</h3>', data, re.DOTALL)
   for t in titles[:10]:
       clean = re.sub(r'<[^>]+>', '', t).strip()
       if clean: print(f'{html.unescape(clean)}')"
   ```
4. **DuckDuckGo HTML** — works from servers with proper User-Agent (e.g. `Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0`). May rate-limit after rapid queries; retry once after 2s. More reliable than Google from headless environments. Extraction:
   ```bash
   curl -sL "https://html.duckduckgo.com/html/?q=QUERY" \
     -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0" | \
     python3 -c "
   import sys, re, html as h
   data = sys.stdin.read()
   results = re.findall(r'class=\"result__a\"[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>.*?class=\"result__snippet\"[^>]*>(.*?)</span>', data, re.DOTALL)
   for url, title, snippet in results[:10]:
       title = re.sub(r'<[^>]+>', '', title).strip()
       snippet = re.sub(r'<[^>]+>', '', snippet).strip()
       print(f'TITLE: {h.unescape(title)}')
       print(f'URL: {url}')
       print(f'SNIPPET: {h.unescape(snippet)[:200]}')
       print('---')"
   ```
5. **Google** — often returns CAPTCHAs from server IPs; unreliable

**Pitfall**: DuckDuckGo and Google frequently block server-side requests with
bot detection. Yahoo Search is the most reliable HTML search fallback from
headless/server environments. However, DuckDuckGo HTML with proper User-Agent
header works reliably for moderate query volumes.
