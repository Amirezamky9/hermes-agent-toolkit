---
name: realtime-web-apps
description: Build simple real-time web applications (chat, multiplayer games, collaborative tools) with minimal dependencies. Node.js + ws + single HTML file. No frameworks, no build tools. Covers WebSocket server, room management, mobile-first UI, RTL/Farsi support.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-development, websocket, multiplayer, games, realtime]
    related_skills: [plan]
---

# Real-Time Web Apps

Build simple multiplayer/real-time web apps with **minimal dependencies** and **zero build tools**.

## When to Use

- User wants a multiplayer game, chat, collaborative tool, or any real-time web app
- Mobile-first requirement (phone browser)
- Quick prototype / MVP, not enterprise-scale
- User prefers simple and raw approach

## Tech Stack

```
Server:  Node.js + ws (WebSocket) — ONE dependency
Client:  Single index.html (HTML + CSS + JS embedded)
No:      Express, Socket.IO, React, Vue, build tools, bundlers
```

**Why `ws` over Socket.IO:** `ws` is lighter (no polling fallback, no client library), sufficient for simple apps. Use Socket.IO only when you need auto-reconnect, rooms, or broadcast primitives out of the box.

**ponytail:** Upgrade to Socket.IO if reconnection logic gets complex (>50 lines). Upgrade to a framework if the project exceeds ~1000 lines of client JS.

## File Structure (4 files)

```
project/
├── server.js          # HTTP server (static files) + WebSocket server
├── game-logic.js      # Business logic / state machine (separated from server)
├── index.html         # Single-page client (HTML + CSS + JS)
└── package.json       # Just "ws" dependency
```

**Rule:** Keep business logic in a separate file from the server. Server handles connections + routing only.

## Server Pattern

> **Template:** `templates/server-template.js` — copy-paste starter with static file serving, room management, and broadcast. Modify for your game.

```javascript
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');

// HTTP server serves static files (index.html for /)
const server = http.createServer((req, res) => { /* static file serving */ });
const wss = new WebSocket.Server({ server });

// Room management
const rooms = new Map(); // roomId -> state
const playerWs = new Map(); // playerId -> { ws, roomId }

wss.on('connection', (ws) => {
  ws.on('message', (raw) => {
    const msg = JSON.parse(raw);
    handleMessage(ws, msg);
  });
  ws.on('close', () => handleDisconnect(ws));
});

server.listen(PORT);
```

## Key Patterns

### Room Management
- 4-char alphanumeric room codes (exclude I/O/0/1 to avoid confusion)
- Host creates, others join with code
- In-memory rooms (no DB needed for prototypes)

### State Synchronization
- Server is source of truth — never trust client state
- Send personalized state to each player (hide hidden info)
- Broadcast after every state change

### Mobile UI
- Use `100dvh` (dynamic viewport height) for mobile browsers
- RTL support: html dir=rtl lang=fa
- Touch targets: minimum 44px
- Dark theme default (easier on battery, looks modern)

### Real-time Timers
- Server-side timeouts for game phases (challenge windows, turn timers)
- Client receives countdown, not server time
- Clear intervals/overlays when phase changes

### Reconnection
- Store roomId + playerId in localStorage
- On reconnect: send join with same name -> server detects existing player
- On disconnect: mark player disconnected, skip their turn if needed

## Deployment (No Root Access)

When user has no root/SSH access to modify Traefik or nginx, use **cloudflared quick tunnel**:

```bash
# 1. Start server in background
cd /workspace/project && node server.js &

# 2. Start cloudflare tunnel
cloudflared tunnel --url http://localhost:3000 --protocol http2 2>&1 &

# 3. Get the URL from output (look for trycloudflare.com)
# URL appears in: "Your quick Tunnel has been created! Visit it at: https://xxx.trycloudflare.com"
```

**Verify:** `curl -s -o /dev/null -w "%{http_code}" https://<tunnel-url>` should return `200`.

**WebSocket test:** Quick tunnels support WebSocket natively — no extra config needed.

**⚠️ Pitfall: cloudflared ERR_CONNECTION_REFUSED**
First tunnel attempt sometimes fails with `ERR_CONNECTION_REFUSED` in browser. Fix: kill the tunnel, restart with `--protocol http2` flag. The default QUIC protocol can be flaky.

```bash
# Kill old tunnel
pkill cloudflared
# Restart with http2
cloudflared tunnel --url http://localhost:3000 --protocol http2
```

**⚠️ Caveat:** Quick tunnel URLs are temporary. If the process restarts, the URL changes. For permanent URLs, user needs root access for Traefik/Caddy or a Cloudflare account with named tunnels.

## Alternative: CDN-Framework Single-Page App

For **non-real-time** applications (e-commerce dashboards, admin panels, landing pages), the same single-file approach works with React CDN instead of vanilla JS:

```html
<!-- Single HTML file — no build step, no Node.js -->
<!DOCTYPE html>
<html>
<head>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const { useState, useEffect, createContext, useContext } = React;
    // Full React SPA here — components, routing (state-based), API calls
  </script>
</body>
</html>
```

**Key differences from real-time pattern:**
- Uses React (via CDN) instead of vanilla JS — better for complex UIs with 10+ components
- Tailwind CSS via CDN instead of hand-written CSS — faster to iterate
- Babel standalone for JSX transpilation (client-side, no build step)
- Mock data fallback: if the API is unavailable, show hardcoded product data

**When to choose this over vanilla JS:**
- Project has 5+ distinct pages/views
- Complex state management needed (auth, cart, products)
- Team familiar with React ecosystem

**When to choose vanilla JS instead:**
- Real-time features (WebSocket, multiplayer)
- Performance-critical (Babel transpilation adds ~300ms to first render)
- Tiny app (< 5 components)

### API Auth Pitfall: python-jose `sub` must be string

When building the backend API with FastAPI + python-jose:

```python
# CORRECT
token = create_access_token(data={"sub": str(user.id)})  # str() is MANDATORY!
```

```python
# WRONG — this fails with "Subject must be a string"
token = create_access_token(data={"sub": user.id})  # integer! python-jose rejects it
```

python-jose strictly validates the JWT `sub` claim as a string. Pass an integer and every authenticated endpoint returns 401. This is a common footgun with any FastAPI + python-jose auth setup.

## Research → Plan → Build Workflow

For game/app builds that need research first:

1. **Research** (subagents): Use `delegate_task` for parallel research — one subagent for rules/domain knowledge, one for existing implementations on GitHub
2. **Plan** (plan skill): Write implementation plan to `.hermes/plans/`, then build
3. **Build incrementally**: Give user status updates after each major file. User said "مرحله به مرحله منو در جریان بزار" (keep me informed step by step)
4. **Test before deploy**: Run `node -e "require('./game-logic')"` to verify modules, `timeout 3 node server.js` to verify startup
5. **Deploy**: cloudflared quick tunnel

## Pitfalls

1. **Dont use Socket.IO just because.** `ws` is lighter and sufficient for simple apps.
2. **Dont trust client state.** Always validate actions server-side.
3. **Dont forget `100dvh`.** Mobile browsers show/hide address bars, making `100vh` unreliable.
4. **Dont send full state to all players.** Each player should only see their own hidden info.
5. **Dont skip server-side timeouts.** Clients can disconnect mid-phase; the server must advance game state.
6. **Port conflicts.** Check port 8000 is occupied on users server. Use 3000 for development.
7. **cloudflared quick tunnel flaky on first try.** Use `--protocol http2` flag. See Deployment section.
8. **Dont block on subagent results.** Dispatch research subagents, continue building the plan in parallel. Results arrive as new messages.

## Reference

See `.hermes/plans/2026-07-05_coup-web-game.md` for a complete example: server.js (300 lines), game-logic.js (500 lines), index.html (600 lines). Full working game at `/workspace/coup-game/`.
