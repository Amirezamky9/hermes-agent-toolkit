# Grok (xAI) API Reference

## Endpoints Discovered

### xAI Official API (recommended)
- **Base URL**: `https://api.x.ai/v1`
- **Auth**: `Authorization: Bearer $XAI_API_KEY`
- **Chat**: `POST /v1/chat/completions` (OpenAI-compatible)
- **Responses**: `POST /v1/responses` (simpler single-turn)
- **Models**: `grok-4`, `grok-4-mini`, `grok-4.5`

### grok.com Internal API (requires cookies + challenge solving)
- **Chat**: `POST https://grok.com/rest/app-chat/x`
- **Auth**: `sso` + `sso-rw` cookies + `x-statsig-id` header
- **Models**: `auto`, `fast`, `expert`, `heavy`, `grok-43`
- **Blocked**: Cloudflare managed challenge blocks all datacenter IPs

### grok-web-api (Rust, self-hosted wrapper)
- **GitHub**: https://github.com/imjustprism/grok-web-api
- **OpenAI-compatible**: `POST /v1/chat/completions`
- **Native**: `POST /v1/chat`, `GET /v1/conversations`, `GET /v1/models`
- **Requires**: Rust 1.85+, nasm, clang, grok.com cookies

## Cloudflare Protection

grok.com uses Cloudflare's "managed challenge" which:
1. Detects datacenter IPs (non-residential)
2. Serves JavaScript challenge requiring browser execution
3. Even solving the checkbox challenge fails — Cloudflare fingerprints the environment
4. Returns 403 for all terminal/curl requests regardless of valid cookies

**Tested and confirmed failing:**
- curl with cookies → 403
- curl_cffi with chrome120/124/safari17_0/edge101 impersonation → 403
- Browserbase browser (no stealth) → Cloudflare challenge page
- Browserbase with checkbox click → "Verifying..." → back to checkbox

**Only works from:** Residential IPs with real browser sessions.

## Cookie-sync Coverage

Cookie-sync captures grok.com cookies including `sso` and `sso-rw`, but these are useless for API access because Cloudflare blocks before authentication is checked.

**Cookies captured by cookie-sync:**
| Cookie | Purpose | Useful? |
|--------|---------|---------|
| `sso` | Auth JWT (critical) | ❌ Cloudflare blocks first |
| `sso-rw` | Auth JWT (read-write) | ❌ Cloudflare blocks first |
| `grok_device_id` | Device identifier | ❌ |
| `x-challenge` | Anti-bot token | ❌ |
| `x-signature` | Anti-bot token | ❌ |
| `__cf_bm` | Cloudflare bot mgmt | ❌ |

**Pitfall:** Cookie delivery ≠ API access for Cloudflare-protected sites.
The user may send cookies via cookie-sync and expect grok.com to work —
explain that Cloudflare blocks datacenter IPs regardless of valid cookies.

## xAI API Code Examples

### Python (OpenAI SDK compatible)
```python
from openai import OpenAI
client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)
response = client.chat.completions.create(
    model="grok-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Shell (streaming)
```bash
curl -N https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{"model":"grok-4","stream":true,"messages":[{"role":"user","content":"hello"}]}'
```
