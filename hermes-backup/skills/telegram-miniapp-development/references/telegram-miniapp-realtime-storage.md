# Telegram Mini App — Real-Time, Storage & Integration Reference

## SSE Implementation with FastAPI

### Server-Side (FastAPI + sse-starlette)

```python
# core/events.py
import asyncio
import json
from typing import Dict, Set
from fastapi.responses import StreamingResponse

class SSEManager:
    def __init__(self):
        self.connections: Dict[int, Set[asyncio.Queue]] = {}

    async def connect(self, user_id: int):
        queue = asyncio.Queue()
        if user_id not in self.connections:
            self.connections[user_id] = set()
        self.connections[user_id].add(queue)

        async def event_generator():
            try:
                while True:
                    data = await queue.get()
                    yield f"data: {json.dumps(data)}\n\n"
            except asyncio.CancelledError:
                self.connections[user_id].discard(queue)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )

    async def send(self, user_id: int, data: dict):
        if user_id in self.connections:
            for queue in self.connections[user_id]:
                await queue.put(data)

sse_manager = SSEManager()
```

### SSE Endpoint

```python
# api/v1/sse/events.py
from fastapi import APIRouter, Depends
from app.core.events import sse_manager
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/sse")
async def sse_stream(user: User = Depends(get_current_user)):
    return await sse_manager.connect(user.id)
```

### Client-Side (React)

```typescript
// hooks/useSSE.ts
import { useEffect, useCallback, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';

interface SSEEvent {
  type: string;
  data: any;
}

export function useSSE(onEvent: (event: SSEEvent) => void) {
  const token = useAuthStore(s => s.token);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!token) return;

    const connect = () => {
      const es = new EventSource(
        `${import.meta.env.VITE_API_URL}/api/v1/sse?token=${token}`
      );

      es.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onEvent(data);
      };

      es.onerror = () => {
        // EventSource auto-reconnects (this is why we use SSE, not WS)
        es.close();
        setTimeout(connect, 3000); // Manual reconnect after 3s
      };

      eventSourceRef.current = es;
    };

    connect();

    return () => {
      eventSourceRef.current?.close();
    };
  }, [token, onEvent]);
}

// Usage in component:
// useSSE((event) => {
//   if (event.type === 'ai_response') updateChat(event.data);
//   if (event.type === 'habit_reminder') showNotification(event.data);
// });
```

### CORS Configuration for SSE

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Caddy Config for SSE

```
# SSE needs no buffering — flush_interval -1 disables buffering
handle /api/v1/sse/* {
    reverse_proxy backend:8000 {
        flush_interval -1
    }
}
```

## 3-Layer Storage — Implementation Examples

### CloudStorage (synced, 1024 items × 4KB)

```typescript
// Store user preferences (synced across devices)
const storeTheme = (theme: string) => {
  Telegram.WebApp.CloudStorage.setItem('theme', theme, (err, success) => {
    if (success) console.log('Theme saved and synced');
  });
};

const loadTheme = () => {
  Telegram.WebApp.CloudStorage.getItem('theme', (err, value) => {
    if (value) applyTheme(value);
  });
};
```

### DeviceStorage (local, 5MB — for offline cache)

```typescript
// Cache timeline data for offline access
const cacheTimeline = async (date: string, events: Event[]) => {
  try {
    await Telegram.WebApp.DeviceStorage.setItem(
      `timeline_${date}`,
      JSON.stringify(events)
    );
  } catch (e) {
    console.warn('DeviceStorage full or unavailable');
  }
};

const getCachedTimeline = async (date: string): Promise<Event[] | null> => {
  try {
    const data = await Telegram.WebApp.DeviceStorage.getItem(`timeline_${date}`);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
};
```

### SecureStorage (encrypted, 10 items — for sensitive data only)

```typescript
// Store auth token securely (max 10 items!)
const storeAuthToken = (token: string) => {
  Telegram.WebApp.SecureStorage.setItem('auth_token', token);
};

const getAuthToken = (): Promise<string | null> => {
  return new Promise((resolve) => {
    Telegram.WebApp.SecureStorage.getItem('auth_token', (err, value) => {
      resolve(value || null);
    });
  });
};
```

**Slot allocation (10 max):**
1. `auth_token` — JWT access token
2. `refresh_token` — JWT refresh token
3-10. Reserved for future use (biometric keys, etc.)

## Third-Party Auth Validation (Ed25519)

### For n8n Workflows

n8n can validate Telegram initData directly without your bot token:

```javascript
// n8n Code Node
const crypto = require('crypto');

function validateInitData(initData, botId, publicKey) {
  const parsed = Object.fromEntries(new URLSearchParams(initData));
  const hash = parsed.hash;
  delete parsed.hash;

  const dataCheckString = Object.keys(parsed)
    .sort()
    .map(k => `${k}=${parsed[k]}`)
    .join('\n');

  const secretKey = `bot${botId}:WebAppData\n${dataCheckString}`;

  // Ed25519 verification using Telegram's public key
  const verifier = crypto.createVerify('SHA256');
  verifier.update(secretKey);
  return verifier.verify(publicKey, hash, 'base64');
}
```

**Telegram's Ed25519 Public Keys:**
- Test environment: `40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec`
- Production: `e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d`

## n8n Webhook-Only Integration Pattern

### Architecture Diagram

```
┌──────────────┐    webhook POST     ┌──────────────┐
│   FastAPI    │ ──────────────────▶ │     n8n      │
│              │                     │              │
│  Source of   │ ◀────────────────── │  AI Brain +  │
│  Truth       │    webhook POST     │  Memory      │
└──────────────┘   (results back)    └──────────────┘
```

### Webhook Payload Schema

```json
// FastAPI → n8n (trigger)
{
  "user_id": 12345,
  "message": "برنامه امروزم چیه?",
  "context": {
    "workspace": "Personal",
    "current_date": "2026-07-17",
    "habits_count": 5,
    "pending_tasks": 3
  }
}

// n8n → FastAPI (result)
{
  "agent_type": "chat",
  "user_id": 12345,
  "response": "امروز ۳ تسک داری...",
  "metadata": {
    "model": "gpt-4o",
    "tokens_used": 250,
    "memory_updated": true
  }
}
```

### n8n Memory Structure

```
Per-user memory in n8n:
├── chat_history: [{role, content, timestamp}] (max 50 messages)
├── context: {workspace, goals, preferences}
└── state: {setup_completed, last_interaction, mood}
```

## WebView Lifecycle Events

```javascript
// Track app lifecycle for SSE reconnection
Telegram.WebApp.onEvent('activated', () => {
  // App came to foreground — reconnect SSE
  reconnectSSE();
});

Telegram.WebApp.onEvent('deactivated', () => {
  // App went to background — optionally disconnect SSE
  // (or let it stay connected for push)
});

// Check if app is currently active
const isActive = Telegram.WebApp.isActive;
```

## Performance Tips

1. Call `Telegram.WebApp.ready()` ASAP in your entry point
2. Use CSS variables (`var(--tg-theme-*)`) for theming — not hardcoded colors
3. Respect `safeAreaInset` for notch/navigation bar overlap
4. On Android, check `userAgent` for hardware class → reduce animations on low-end
5. `sendData()` has a 4096 byte limit — use API for larger payloads
6. Lazy load heavy components (charts, calendar) — don't include in initial bundle
