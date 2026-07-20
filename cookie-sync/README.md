# Cookie Sync

Sync browser cookies to server tools automatically.

## How It Works

1. Install CacheCat Chrome extension
2. Start webhook server
3. Click "Sync" on any website
4. Cookies are sent to server
5. Server updates tool credentials

## Setup

### 1. Install Extension

See [CacheCat Repository](https://github.com/chinmay29hub/CacheCat)

### 2. Start Server

```bash
# Generate token
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start
python3 webhook.py
```

### 3. Configure Extension

- Webhook URL: `http://localhost:9999`
- Token: Your generated token

## Supported Tools

| Tool | Cookie Format | Auto-Update |
|------|---------------|-------------|
| Twitter/X | auth_token, ct0 | ✅ |
| Reddit | reddit_session | ✅ |
| YouTube | SID, HSID, etc. | ✅ |
| Xueqiu | xq_a_token | ✅ |

## API

### POST /
Receive cookies from extension.

**Request:**
```json
{
  "domain": "twitter.com",
  "cookies": [{"name": "auth_token", "value": "..."}]
}
```

**Response:**
```json
{
  "success": true,
  "domain": "twitter.com",
  "count": 2
}
```

### GET /health
Health check.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-07-20T23:00:00"
}
```

## Credits

Based on [CacheCat](https://github.com/chinmay29hub/CacheCat) by chinmay29hub.
