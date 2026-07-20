# Cookie Sync — Detailed Guide

## Overview

Cookie Sync allows automatic synchronization of browser cookies to server tools.

## Components

### CacheCat Extension

Chrome extension that:
- Reads cookies from current website
- Sends them to webhook server
- Supports all storage types (cookies, localStorage, etc.)

### Webhook Server

Python server that:
- Receives cookies from extension
- Saves to local files
- Updates tool-specific credentials
- Handles multiple domains

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Amirezamky9/hermes-toolkit.git
cd hermes-toolkit
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Generate Token

```bash
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Your token: $COOKIE_SYNC_TOKEN"
```

### Step 4: Start Server

```bash
python3 cookie-sync/webhook.py
```

### Step 5: Install Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable Developer mode
4. Click "Load unpacked"
5. Select `cookie-sync/cachecat-extension/`

### Step 6: Configure Extension

1. Click CacheCat icon
2. Enter URL: `http://localhost:9999`
3. Enter your token
4. Save

## Usage

### Sync Twitter Cookies

1. Go to twitter.com (make sure you're logged in)
2. Click CacheCat icon
3. Click "Sync"
4. Server saves cookies

### Sync Reddit Cookies

1. Go to reddit.com (make sure you're logged in)
2. Click CacheCat icon
3. Click "Sync"
4. Server saves cookies

## Supported Platforms

| Platform | Cookies | Auto-Update |
|----------|---------|-------------|
| Twitter/X | auth_token, ct0 | ✅ |
| Reddit | reddit_session | ✅ |
| YouTube | SID, HSID, SSID | ✅ |
| Xueqiu | xq_a_token | ✅ |

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :9999

# Kill existing process
kill -9 $(lsof -t -i:9999)

# Try again
python3 cookie-sync/webhook.py
```

### Extension can't connect

1. Check server is running: `curl http://localhost:9999/health`
2. Check token is correct
3. Check firewall settings
4. Try different port

### Cookies not updating

1. Check server logs
2. Verify cookie format
3. Check tool-specific paths

## Credits

Based on [CacheCat](https://github.com/chinmay29hub/CacheCat) by chinmay29hub.
