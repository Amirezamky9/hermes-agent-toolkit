# Minimal WebSocket Server Template

Copy this and modify for your game/app.

```javascript
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

// HTTP server for static files
const server = http.createServer((req, res) => {
  let filePath = req.url === '/' ? '/index.html' : req.url.split('?')[0];
  const fullPath = path.join(__dirname, filePath);
  const ext = path.extname(fullPath);
  const mimeTypes = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
  };
  fs.readFile(fullPath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not Found'); return; }
    res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
    res.end(data);
  });
});

const wss = new WebSocket.Server({ server });
const rooms = new Map();
const clientMap = new Map(); // clientId -> { ws, roomId }

function generateId(len = 4) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let id = '';
  for (let i = 0; i < len; i++) id += chars[Math.floor(Math.random() * chars.length)];
  return id;
}

function broadcast(roomId) {
  // Send personalized state to each player in room
  for (const [clientId, info] of clientMap) {
    if (info.roomId === roomId && info.ws.readyState === WebSocket.OPEN) {
      info.ws.send(JSON.stringify({ type: 'state', /* ... */ }));
    }
  }
}

wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    try {
      const msg = JSON.parse(raw);
      // Handle: create, join, action, chat, etc.
    } catch (e) {
      ws.send(JSON.stringify({ type: 'error', message: 'Invalid message' }));
    }
  });
  ws.on('close', () => {
    // Handle disconnect: mark player disconnected, skip turn if needed
  });
});

server.listen(PORT, () => console.log(`Server on port ${PORT}`));
```

## Key Rules
- Server is source of truth — never trust client
- Send personalized state (hide hidden info per player)
- Broadcast after every state change
- Handle disconnect gracefully (mark disconnected, skip turn)
- Use `100dvh` in CSS for mobile viewport
- Touch targets minimum 44px
