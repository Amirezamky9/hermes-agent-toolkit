# VLESS + Reality + XTLS-Vision — Verified Working Config

Deployed and tested on 3x-ui v3.5.0 / Xray v26.7.11, July 2026.

## Step 1: Generate Keys

```bash
# x25519 keypair via panel API (GET, not POST)
curl -s -H "Authorization: Bearer TOKEN" \
  "https://PANEL/panel/api/server/getNewX25519Cert"
# → {"success":true,"obj":{"privateKey":"...","publicKey":"..."}}

# UUID for client
curl -s -H "Authorization: Bearer TOKEN" \
  "https://PANEL/panel/api/server/getNewUUID"
# → {"success":true,"obj":{"uuid":"..."}}

# Short ID
openssl rand -hex 8
```

## Step 2: Create Inbound via Panel API

```bash
curl -s -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "remark": "Reality-443",
    "protocol": "vless",
    "port": 443,
    "settings": {
      "clients": [{
        "email": "user@example.com",
        "id": "CLIENT_UUID",
        "flow": "xtls-rprx-vision",
        "limitIp": 0,
        "totalGB": 0,
        "expiryTime": 0,
        "enable": true,
        "subId": "reality-sub"
      }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "www.microsoft.com:443",
        "xver": 0,
        "serverNames": ["www.microsoft.com", "microsoft.com"],
        "privateKey": "PRIVATE_KEY",
        "shortIds": ["SHORT_ID", ""],
        "maxTimeDiff": 0
      }
    },
    "sniffing": {
      "enabled": true,
      "destOverride": ["http", "tls", "quic"]
    },
    "enable": true
  }' "https://PANEL/panel/api/inbounds/add"
```

## Step 3: Construct Share Link (MANUAL — panel's auto-link is incomplete)

```
vless://CLIENT_UUID@PANEL_HOST:443?flow=xtls-rprx-vision&security=reality&pbk=PUBLIC_KEY&fp=chrome&sni=www.microsoft.com&sid=SHORT_ID&spx=%2F&type=tcp#Reality-443
```

⚠️ The panel's `/clients/links/{email}` endpoint omits `pbk` and `fp` fields.
Always construct the link manually with ALL fields. Missing any → client fails silently.

## Required Link Parameters

| Param | Value | Notes |
|---|---|---|
| `flow` | `xtls-rprx-vision` | Mandatory for XTLS |
| `security` | `reality` | |
| `pbk` | Server public key | From `/server/getNewX25519Cert` |
| `fp` | `chrome` | Fingerprint, must match realitySettings |
| `sni` | `www.microsoft.com` | Must match dest serverNames |
| `sid` | Short ID hex | From `openssl rand -hex 8` |
| `spx` | `%2F` | SpiderX path, `/` encoded |
| `type` | `tcp` | Transport |

## Verified Dest Sites for Iran

- `www.microsoft.com:443` ← most reliable
- `www.cloudflare.com:443`
- `www.apple.com:443`
- `dl.google.com:443`
