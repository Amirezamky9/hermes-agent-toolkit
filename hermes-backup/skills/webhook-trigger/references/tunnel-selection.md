# Tunnel Selection Cheat Sheet

## Quick Decision
```
Need real-time from browser?
├── NO (webhooks, APIs, forms) → cloudflared tunnel --url
├── YES + no constraints → localtunnel --port (but splash page)
└── YES + must work everywhere → HTTP Polling + cloudflared
```

## cloudflared Quick Tunnel
```bash
cloudflared tunnel --url http://localhost:<PORT>
# URL: https://<random>.trycloudflare.com
# ⚠️ WebSocket FAILS from browsers (HTTP/2 issue)
# ✅ Works for HTTP-only (webhooks, REST APIs, static sites)
# ✅ Node.js/Python WS clients DO connect (server-side only)
```

## localtunnel
```bash
npx --yes localtunnel --port <PORT>
# URL: https://<name>.loca.lt
# ✅ WebSocket works from browsers
# ⚠️ "Click to Continue" splash on first visit (sometimes blocks entirely)
# ⚠️ Less reliable uptime than cloudflared
```

## HTTP Polling Pattern (Most Reliable)
When WebSocket isn't available, convert real-time to polling:

### Server (Node.js)
```javascript
const http = require('http');
const state = {}; // in-memory game state

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', c => body += c);
  req.on('end', () => {
    const data = JSON.parse(body);
    // Handle action
    if (req.url === '/api/action') { /* process action */ }
    // Poll for state
    if (req.url === '/api/poll') {
      res.writeHead(200, {'Content-Type':'application/json'});
      res.end(JSON.stringify({ state: getState(data.roomId, data.playerId) }));
    }
  });
});
```

### Client
```javascript
async function poll() {
  const r = await fetch('/api/poll', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({roomId, playerId})
  });
  const {state} = await r.json();
  render(state);
  setTimeout(poll, 1500);
}
poll();
```

### Tradeoffs
| Aspect | WebSocket | HTTP Polling |
|--------|-----------|-------------|
| Latency | ~0ms | ~1500ms (poll interval) |
| Works through CF tunnel | ❌ | ✅ |
| Works through proxies | Sometimes | ✅ Always |
| Bandwidth | Low (push) | Medium (periodic pull) |
| Complexity | Higher | Lower |
| Turn-based games | Overkill | Perfect fit |
