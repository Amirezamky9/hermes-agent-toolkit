# VLESS + WebSocket + TLS — Managed Hosting Config

For panels behind Envoy/Istio/Cloudflare where direct Reality doesn't work.

## Step 1: Create Inbound via Panel API

```bash
curl -s -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "remark": "VLESS-WS",
    "protocol": "vless",
    "port": 443,
    "settings": {
      "clients": [{
        "email": "user@example.com",
        "id": "CLIENT_UUID",
        "flow": "",
        "limitIp": 0,
        "totalGB": 0,
        "expiryTime": 0,
        "enable": true,
        "subId": "ws-sub"
      }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": {
        "path": "/vless-ws",
        "headers": {
          "Host": "YOUR_DOMAIN"
        }
      }
    },
    "sniffing": {
      "enabled": true,
      "destOverride": ["http", "tls", "quic"]
    },
    "enable": true
  }' "https://PANEL/panel/api/inbounds/add"
```

## Step 2: Restart Xray

```bash
curl -s -X POST -H "Authorization: Bearer TOKEN" \
  "https://PANEL/panel/api/server/restartXrayService"
```

## Step 3: Client Link (NO manual construction needed — panel auto-link works for WS)

```
vless://CLIENT_UUID@DOMAIN:443?encryption=none&type=ws&host=DOMAIN&path=%2Fvless-ws&security=tls&sni=DOMAIN#VLESS-WS
```

## Client v2rayNG Settings

| Field | Value |
|---|---|
| address | YOUR_DOMAIN |
| port | 443 |
| encryption | none |
| flow | (empty) |
| network | ws |
| security | tls |
| sni | YOUR_DOMAIN |
| path | /vless-ws |
| host | YOUR_DOMAIN |
| fingerprint | chrome |
| allowInsecure | 0 |

## Key Differences from Reality

| | Reality | WS+TLS |
|---|---|---|
| flow | xtls-rprx-vision | (empty) |
| security | reality | tls |
| pbk | required | not needed |
| fp | required | optional |
| sni | cover site (microsoft.com) | own domain |
| Needs raw TCP | Yes | No |
| Works behind proxy | No | Yes |

## Common Mistakes

1. **Setting flow to xtls-rprx-vision** — WS doesn't use XTLS. Leave flow empty.
2. **Using security=reality** — WS must use security=tls with a valid cert.
3. **Missing Host header** — Some proxies need the Host header to route correctly.
4. **Forgetting to restart Xray** — Changes don't take effect until restart.
