# Hermes Cookie Sync Extension

A Chrome Extension (Manifest V3) that captures browser cookies and syncs them to a remote Hermes AI agent backend via webhooks. AI agents can maintain authenticated browser sessions without user re-login.

Based on [CacheCat](https://github.com/chinmay29hub/CacheCat).

---

## How It Works

```
Chrome Browser  -->  Extension Captures Cookies  -->  Webhook POST  -->  Hermes Backend  -->  storage_state.json  -->  Playwright Session (Authenticated)
```

1. User installs extension and configures which domains to sync
2. Extension captures cookies from those domains
3. Cookies are sent via webhook to your Hermes backend
4. Backend saves cookies as Playwright's `storage_state.json`
5. Playwright reads the file and opens an already-authenticated browser session

---

## Features

- **Cookie Capture** — Captures all cookies for user-specified domains (e.g., `google.com`, `notebooklm.google.com`)
- **Manual Sync** — Click "SYNC NOW" to immediately send cookies to your Hermes API
- **Auto-Sync** — Automatically sync when cookies change (via `chrome.cookies.onChanged`)
- **Webhook Integration** — POST requests to your Hermes API with Bearer token auth
- **Persistent Config** — Settings saved in Chrome's `storage.local`, survive restarts
- **Secure** — Cookie values never logged to console; HTTPS + Bearer token for API calls
- **Backend Example** — Complete Python FastAPI server that saves cookies as Playwright format

---

## Installation

### Prerequisites

- Node.js 18+
- Google Chrome 88+

### Build from Source

```bash
git clone https://github.com/your-username/hermes-cookie-sync.git
cd hermes-cookie-sync
npm install
npm run build
```

### Load in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `dist/` folder from this project
5. Extension icon appears in toolbar

### If Build Fails (Windows Rollup Error)

Manually copy files to `dist/`:

```bash
mkdir dist
copy manifest.json dist\
xcopy /E /I icons dist\icons
copy src\background\background.js dist\
copy src\agent\agent.js dist\
copy src\content\content.js dist\
```

---

## Configuration

Click the extension icon, then click **Hermes Sync** in the sidebar.

| Setting | Description | Example |
|---------|-------------|---------|
| **Enable Hermes Sync** | Master toggle | ON |
| **Auto-Sync** | Sync when cookies change | ON |
| **Hermes API URL** | Backend endpoint | `https://my-hermes-server.com/api/browser-sync` |
| **API Key** | Bearer token | `your-secret-api-key` |
| **Sync Domains** | Domains to capture | `google.com`, `notebooklm.google.com` |

---

## Usage

### Manual Sync

1. Open dashboard (click extension icon)
2. Go to **Hermes Sync** tab
3. Click **SYNC NOW**
4. Status shows success/failure

### Auto-Sync

1. Toggle **Auto-Sync on Cookie Changes** ON
2. When cookies change for configured domains, extension syncs after 1s debounce

### Test Connection

1. Enter API URL and Key
2. Click **TEST CONNECTION**
3. See if backend responds (200 = OK)

---

## Webhook Payload

The extension sends this POST request on sync:

```json
{
  "domain": "google.com",
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": ".google.com",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax",
      "expirationDate": 1735689600,
      "session": false,
      "storeId": "0",
      "hostOnly": false
    }
  ],
  "timestamp": "2026-07-02T23:17:00.000Z"
}
```

Headers:
```
Content-Type: application/json
Authorization: Bearer your-api-key
```

---

## Backend Integration

### hermes-browser-sync.config.json

Copy this file to your Hermes project root:

```json
{
  "type": "cachecat-hermes-sync",
  "version": "1.0",
  "endpoints": {
    "sync_url": "https://YOUR-HERMES/api/browser-sync"
  },
  "instructions": "Hermes should read this file and update storage_state.json for Playwright sessions."
}
```

### Python FastAPI Backend

Located in `examples/hermes-backend/`.

```bash
cd examples/hermes-backend
pip install -r requirements.txt
export HERMES_API_KEY="your-secret-api-key"
export STORAGE_STATE_PATH="storage_state.json"
python main.py
```

Server starts at `http://localhost:8000`.

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/browser-sync` | POST | Receives cookies, saves as `storage_state.json` |
| `/api/test-connection` | POST | Connection test |
| `/health` | GET | Health check |

#### storage_state.json Format

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": ".google.com",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax",
      "expires": 1735689600,
      "url": "https://google.com/"
    }
  ],
  "origins": []
}
```

#### Use with Playwright

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(storage_state="storage_state.json")
    page = context.new_page()
    page.goto("https://google.com")  # Already authenticated!
```

---

## Project Structure

```
hermes-cookie-sync/
├── src/
│   ├── background/
│   │   ├── background.js          # Service worker: message routing, tab management, auto-sync
│   │   ├── hermes-sync.js         # Config storage, webhook POST, connection test
│   │   └── cookie-capture.js      # Capture cookies for configured domains
│   │
│   ├── dashboard/
│   │   ├── App.jsx                # Root component, view routing
│   │   ├── dashboard.html         # Dashboard HTML entry
│   │   ├── main.jsx               # React entry point
│   │   ├── index.css              # Tailwind styles
│   │   ├── components/
│   │   │   ├── Layout.jsx         # Layout with sidebar nav
│   │   │   ├── Sidebar.jsx        # Left sidebar
│   │   │   ├── TopBar.jsx         # Top bar
│   │   │   ├── CookieTable.jsx    # Cookie display table
│   │   │   ├── CookieForm.jsx     # Cookie add/edit form
│   │   │   ├── Modal.jsx          # Modal dialog
│   │   │   ├── Toast.jsx          # Toast notifications
│   │   │   └── ...
│   │   ├── contexts/
│   │   │   ├── ThemeContext.jsx    # Dark/light theme
│   │   │   └── AttachContext.jsx  # Tab attachment state
│   │   └── views/
│   │       ├── CookiesView.jsx         # Cookies management
│   │       ├── LocalStorageView.jsx    # Local Storage management
│   │       ├── SessionStorageView.jsx  # Session Storage management
│   │       ├── IndexedDBView.jsx       # IndexedDB management
│   │       ├── CacheStorageView.jsx    # Cache Storage management
│   │       └── HermesSyncView.jsx      # Hermes Sync configuration (NEW)
│   │
│   ├── content/
│   │   └── content.js             # Bridge: page <-> extension communication
│   │
│   └── agent/
│       └── agent.js               # Injected into page for storage access
│
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
│
├── examples/
│   └── hermes-backend/
│       ├── main.py                # FastAPI server
│       ├── requirements.txt       # Python dependencies
│       └── README.md
│
├── hermes-browser-sync.config.json   # Backend integration config
├── manifest.json                     # Chrome Extension manifest
├── package.json                      # Node.js config
├── vite.config.js                    # Build config
├── tailwind.config.js                # Tailwind config
├── postcss.config.js                 # PostCSS config
└── README.md                         # This file
```

---

## File Explanation

### New Files (Hermes Sync)

**`src/background/hermes-sync.js`** — Configuration and webhook module
- `getSyncConfig()` — Load config from Chrome storage
- `setSyncConfig(config)` — Save config to Chrome storage
- `sendWebhookSync()` — Capture cookies and POST to webhook
- `testWebhookConnection()` — Send test payload to backend

**`src/background/cookie-capture.js`** — Cookie capture module
- `captureCookiesForDomains()` — Get all cookies for configured domains
- `formatCookiesForHermes(cookies, domain)` — Format for webhook payload

**`src/dashboard/views/HermesSyncView.jsx`** — React UI component
- Toggle switches for enable/auto-sync
- Input fields for webhook URL and API key
- Domain list with add/remove
- SYNC NOW and TEST CONNECTION buttons
- Status messages

**`hermes-browser-sync.config.json`** — Backend integration config
- Endpoint URL format
- Authentication method
- Payload format example

**`examples/hermes-backend/main.py`** — FastAPI backend
- Receives cookies via POST
- Converts to Playwright format
- Merges with existing cookies
- Saves as `storage_state.json`

**`examples/hermes-backend/requirements.txt`** — Python dependencies
- fastapi, uvicorn, pydantic

### Modified Files (from CacheCat)

**`manifest.json`** — Added `storage` permission for config persistence

**`src/background/background.js`** — Added:
- Hermes sync message handlers (GET_CONFIG, SET_CONFIG, SYNC_NOW, TEST_CONNECTION)
- `chrome.cookies.onChanged` listener for auto-sync
- 1-second debounce for rapid cookie changes

**`src/dashboard/App.jsx`** — Added `hermes: <HermesSyncView />` to views

**`src/dashboard/components/Layout.jsx`** — Added Hermes Sync to sidebar nav

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Chrome Browser                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Website Tab  <-->  Content Script  <-->  Dashboard     │
│                                       (React UI)        │
│                                          │              │
│                                          v              │
│                                   Service Worker        │
│                                   ┌─────────────┐      │
│                                   │ hermes-sync  │      │
│                                   │ cookie-capture│      │
│                                   └──────┬──────┘      │
│                                          │              │
└──────────────────────────────────────────┼──────────────┘
                                           │
                                    Webhook POST
                                    (Bearer Token)
                                           │
                                           v
┌─────────────────────────────────────────────────────────┐
│                 Hermes Backend (FastAPI)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  POST /api/browser-sync                                 │
│       │                                                 │
│       v                                                 │
│  Receive Cookies  -->  Convert to Playwright  -->  Save │
│                                          │              │
│                                          v              │
│                              storage_state.json         │
│                                                         │
└─────────────────────────────────────────────────────────┘
                                           │
                                    File Read
                                           │
                                           v
┌─────────────────────────────────────────────────────────┐
│                  Playwright Session                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  browser.new_context(storage_state="storage_state.json")│
│       │                                                 │
│       v                                                 │
│  Authenticated Browser (no login needed)                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Security

- Cookie values are **never** logged to console
- All API requests use **Bearer token** authentication
- Use **HTTPS** for production webhook URLs
- Settings stored in Chrome's encrypted `storage.local`
- Extension only accesses cookies for **explicitly configured domains**

---

## Development

```bash
npm run dev       # Watch mode (auto-rebuild)
npm run build     # Production build
npm run lint      # Check code quality
npm run format    # Format with Prettier
```

### Debugging

- **Dashboard:** Right-click tab -> Inspect
- **Background:** `chrome://extensions/` -> Find extension -> Click "service worker"
- **Content Script:** DevTools on target website -> Console

---

## License

MIT

---

## Credits

Based on [CacheCat](https://github.com/chinmay29hub/CacheCat) by [Chinmay Sonawane](https://github.com/chinmay29hub).
