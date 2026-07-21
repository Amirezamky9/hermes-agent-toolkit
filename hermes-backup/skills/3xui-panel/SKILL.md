---
name: 3xui-panel
description: 3X-UI panel API — VPN setup, client management, inbound creation, node management
tags: [vpn, 3x-ui, xray, proxy, networking]
---

# 3X-UI Panel API Skill

## Panel Connection

- **Base URL:** `https://wyokeu-app.tr.caasify.in/panel/api`
- **Auth:** Bearer token `REPLACE_WITH_YOUR_TOKEN`
- **Header:** `Authorization: Bearer <token>`

## Panel State (as of 2026-07-19)

| Property | Value |
|---|---|
| Panel Version | 3.5.0 (latest stable, no update) |
| Xray Version | 26.7.11 |
| Server IP | 185.226.93.96 |
| Web Port | 2053 |
| CPU | 32 cores |
| RAM | ~32 GB |
| Disk | ~200 GB |
| Fail2ban | installed & usable |
| Subscriptions | enabled on port 2096 |
| Sub Path | `/sub/` |
| LDAP | disabled |
| Telegram Bot | not configured |
| SMTP | not configured |
| 2FA | disabled |
| Panel GUID | b560a193-c4c2-4701-ab27-5da4834ed4fb |

**Created (2026-07-19):** 2 inbounds (Reality-443 on TCP/443, Hysteria2-8443 on UDP/8443), 1 client (user1@hermes). No nodes, no hosts, no outbound subs.

## Key API Endpoints

### Server
- `GET /server/status` — real-time CPU/mem/disk/xray state
- `GET /server/getConfigJson` — running Xray JSON config
- `POST /server/restartXrayService` — reload Xray config
- `GET /server/fail2banStatus` — IP limit enforcement check
- `GET /server/getXrayVersion` — available Xray versions
- `POST /server/installXray/{version}` — install Xray version
- `GET /server/logs/{count}` — panel logs
- `POST /server/xraylogs/{count}` — Xray logs

### Inbounds (VPN tunnels)
- `GET /inbounds/list` — all inbounds with clients & stats
- `GET /inbounds/list/slim` — lightweight list (no full clients)
- `GET /inbounds/options` — dropdown projection (id, tag, protocol, port)
- `POST /inbounds/add` — create inbound (full payload: protocol, port, settings, streamSettings, sniffing, remark, enable)
- `POST /inbounds/update/{id}` — replace inbound config
- `POST /inbounds/setEnable/{id}` — toggle enable/disable
- `POST /inbounds/del/{id}` — delete inbound
- `POST /inbounds/bulkDel` — delete many
- `GET /inbounds/get/{id}` — single inbound detail
- `GET /inbounds/allLinks` — all client subscription URLs
- `GET /inbounds/{id}/fallbacks` — fallback rules
- `POST /inbounds/{id}/fallbacks` — replace fallback rules

### Clients
- `GET /clients/list` — all clients with traffic & inbound IDs
- `GET /clients/list/paged` — paginated filtered list
- `GET /clients/get/{email}` — single client
- `POST /clients/add` — create client (JSON body: client object + inboundIds array)
- `POST /clients/update/{email}` — replace client
- `POST /clients/del/{email}` — delete client
- `POST /clients/bulkCreate` — create many
- `POST /clients/bulkDel` — delete many
- `POST /clients/bulkEnable` / `bulkDisable` — toggle clients
- `POST /clients/bulkAdjust` — shift expiry/quota
- `POST /clients/bulkAttach` / `bulkDetach` — attach/detach to inbounds
- `POST /clients/resetTraffic/{email}` — zero counters
- `GET /clients/links/{email}` — subscription URLs for one client
- `GET /clients/subLinks/{subId}` — URLs by subscription ID
- `POST /clients/onlines` — currently connected emails
- `GET /clients/traffic/{email}` — traffic counters
- `GET /clients/export` — export all as JSON
- `POST /clients/import` — import from JSON
- `POST /clients/{email}/attach` — attach to more inbounds
- `POST /clients/{email}/detach` — detach from inbounds
- `POST /clients/delDepleted` — delete exhausted clients
- `POST /clients/delOrphans` — delete unattached clients
- `GET /clients/groups` — list groups with counts
- `POST /clients/groups/bulkAdd` — add to group
- `POST /clients/groups/bulkRemove` — remove from group
- `POST /clients/groups/create` — new empty group
- `POST /clients/groups/delete` — delete group
- `POST /clients/groups/rename` — rename group
- `GET /clients/lastOnline` — email→timestamp map

### Nodes
- `GET /nodes/list` — all remote nodes
- `POST /nodes/add` — register node (URL, apiToken, remark)
- `POST /nodes/update/{id}` — update node
- `POST /nodes/del/{id}` — delete node
- `POST /nodes/setEnable/{id}` — pause/resume sync
- `POST /nodes/test` — probe without saving
- `POST /nodes/probe/{id}` — probe existing node
- `POST /nodes/inbounds` — list remote inbounds for import
- `GET /nodes/history/{id}/{metric}/{bucket}` — node metric history

### Hosts
- `GET /hosts/list` — all hosts grouped by inbound
- `POST /hosts/add` — create host group
- `POST /hosts/update/{groupId}` — replace host group
- `POST /hosts/del/{groupId}` — delete host group
- `POST /hosts/setEnable/{groupId}` — toggle
- `GET /hosts/tags` — distinct tags
- `GET /hosts/byInbound/{inboundId}` — hosts for one inbound

### Settings
- `POST /setting/all` — full settings blob
- `POST /setting/update` — persist all settings
- `POST /setting/updateUser` — change admin credentials
- `POST /setting/restartPanel` — restart panel process
- `GET /setting/apiTokens` — list tokens
- `POST /setting/apiTokens/create` — mint new token
- `POST /setting/apiTokens/delete/{id}` — delete token
- `POST /setting/apiTokens/setEnabled/{id}` — toggle token
- `POST /setting/defaultSettings` — computed defaults for host
- `POST /setting/testSmtp` — test SMTP
- `POST /setting/testTgBot` — test Telegram bot

### Xray
- `POST /xray/update` — save Xray config template
- `POST /xray/testOutbound` — test one outbound
- `POST /xray/testOutbounds` — test batch (max 50)
- `GET /xray/getOutboundsTraffic` — outbound traffic stats
- `POST /xray/routeTest` — routing simulation
- `POST /xray/warp/{action}` — Cloudflare WARP
- `POST /xray/nord/{action}` — NordVPN
- `GET /xray/outbound-subs` — outbound subscriptions
- `POST /xray/outbound-subs` — create outbound sub
- `POST /xray/resetOutboundsTraffic` — reset outbound counters

## Common Inbound Payloads

### VLESS + Reality
> **Verified working template:** `templates/vless-reality-deploy.md` — step-by-step with exact curl commands and share link construction (panel's auto-link is incomplete, must build manually).
```json
{
  "remark": "VLESS-Reality",
  "protocol": "vless",
  "port": 443,
  "settings": {
    "clients": [
      {
        "email": "user@example.com",
        "id": "<auto-generated-uuid>",
        "flow": "xtls-rprx-vision"
      }
    ]
  },
  "streamSettings": {
    "network": "tcp",
    "security": "reality",
    "realitySettings": {
      "show": false,
      "dest": "www.google.com:443",
      "xver": 0,
      "serverNames": ["www.google.com"],
      "privateKey": "<server-private-key>",
      "shortIds": ["<random-hex>"],
      "maxTimeDiff": 0
    }
  },
  "sniffing": {
    "enabled": true,
    "destOverride": ["http", "tls", "quic"]
  },
  "enable": true
}
```

### VLESS + TLS + WebSocket
> **Managed hosting template:** `templates/vless-ws-managed-hosting.md` — for panels behind Envoy/Istio/Cloudflare where Reality doesn't work.
```json
{
  "remark": "VLESS-WS-TLS",
  "protocol": "vless",
  "port": 443,
  "settings": {
    "clients": [
      {
        "email": "user@example.com",
        "id": "<uuid>"
      }
    ]
  },
  "streamSettings": {
    "network": "ws",
    "security": "tls",
    "tlsSettings": {
      "certificates": [
        {
          "certificateFile": "/path/to/cert.pem",
          "keyFile": "/path/to/key.pem"
        }
      ]
    },
    "wsSettings": {
      "path": "/ws-path"
    }
  },
  "sniffing": {
    "enabled": true,
    "destOverride": ["http", "tls", "quic"]
  },
  "enable": true
}
```

### VMess + WebSocket
```json
{
  "remark": "VMess-WS",
  "protocol": "vmess",
  "port": 8080,
  "settings": {
    "clients": [
      {
        "email": "user@example.com",
        "id": "<uuid>"
      }
    ]
  },
  "streamSettings": {
    "network": "ws",
    "wsSettings": {
      "path": "/vmess-ws"
    }
  },
  "sniffing": {
    "enabled": true,
    "destOverride": ["http", "tls", "quic"]
  },
  "enable": true
}
```

### Trojan + TLS
```json
{
  "remark": "Trojan-TLS",
  "protocol": "trojan",
  "port": 443,
  "settings": {
    "clients": [
      {
        "email": "user@example.com",
        "password": "<password>"
      }
    ]
  },
  "streamSettings": {
    "network": "tcp",
    "security": "tls",
    "tlsSettings": {
      "certificates": [
        {
          "certificateFile": "/path/to/cert.pem",
          "keyFile": "/path/to/key.pem"
        }
      ]
    }
  },
  "sniffing": {
    "enabled": true,
    "destOverride": ["http", "tls", "quic"]
  },
  "enable": true
}
```

### Shadowsocks 2022
```json
{
  "remark": "SS-2022",
  "protocol": "shadowsocks",
  "port": 8388,
  "settings": {
    "method": "2022-blake3-aes-128-gcm",
    "password": "<server-key-in-base64>",
    "clients": [
      {
        "email": "user@example.com",
        "password": "<client-key-in-base64>"
      }
    ]
  },
  "enable": true
}
```

### Hysteria2
```json
{
  "remark": "HY2",
  "protocol": "hysteria",
  "port": 443,
  "settings": {
    "version": 2,
    "auth": "password",
    "authStr": "<password>",
    "upMbps": 100,
    "downMbps": 100
  },
  "streamSettings": {
    "network": "udp"
  },
  "enable": true
}
```
> ⚠️ `version: 2` in settings is MANDATORY — Xray rejects Hysteria without it. The panel does not add it automatically.

## Client Add Payload
```json
{
  "client": {
    "email": "user@example.com",
    "id": "<uuid-for-vless/vmess>",
    "flow": "xtls-rprx-vision",
    "limitIp": 0,
    "totalGB": 0,
    "expiryTime": 0,
    "enable": true,
    "tgId": "",
    "subId": ""
  },
  "inboundIds": [1]
}
```

## Protocols Supported
- **vless** — requires UUID, optional flow (xtls-rprx-vision)
- **vmess** — requires UUID
- **trojan** — requires password
- **shadowsocks** — requires method + password (server key) + client password
- **hysteria** — requires auth/authStr + speed limits
- **socks, http, mixed, wireguard, dokodemo, tunnel** — no URL form (not for VPN)

## Stream/Security Options
- **network:** tcp, ws, grpc, h2, quic, httpupgrade, splithttp, xhttp
- **security:** none, tls, reality, wss (for websocket over TLS)
- **tlsSettings:** certificates (file/inline), serverName, alpn, fingerprint, allowInsecure
- **realitySettings:** dest, serverNames, privateKey, shortIds, publicKey, spiderX

## Research Findings: Best Config for Iran (July 2026)

### Protocol Comparison (real benchmarks from Iran, May 2026)

| Protocol | Iran Mobile Speed | Iran Fixed Speed | DPI Resistance | Detection Risk |
|---|---|---|---|---|
| **VLESS + Reality + XTLS-Vision** | 43 Mbps | near line rate | **Highest** | **Very Low (99.1% success)** |
| **Hysteria2 (QUIC + Salamander)** | **61 Mbps** | near line rate | High | Low (97.3% success) |
| **Trojan (TLS)** | 11 Mbps | near line rate | Medium | **High (2-7 day survival)** |
| **VMess + WS + TLS + CDN** | varies | varies | High (behind CDN) | Low |
| **VLESS + WS + TLS + CDN** | varies | varies | High (behind CDN) | Low |

### Recommendation for Iran: 3-tier approach

1. **PRIMARY: VLESS + Reality + XTLS-Vision on port 443** — Best DPI resistance (99.1% success rate on MCI, Irancell, Rightel, Shatel, Asiatech). Looks like real HTTPS to microsoft.com. GFW detects Reality by analyzing heavy traffic patterns on a single IP — keep user count low (5-7 per server).

2. **SECONDARY: Hysteria2 on UDP port 443** — Fastest on lossy mobile networks (61 vs 43 Mbps on Irancell). Good fallback when Reality is rate-limited. Some ISPs throttle UDP — client should auto-switch.

3. **BACKUP: VLESS + WS + TLS behind Cloudflare CDN** — IP hidden behind Cloudflare, very hard to block. Slower but reliable fallback.

### Clean IP (ایپی تمیز) — Cloudflare CDN for Iran
> User correction: "برو پنل ثنایی رو نگاه کن، داری اشتباه کانفیگ می‌کنی، تحقیق کن ایپی تمیز چوری میزنن"

In Iran, direct IP connections get blocked quickly. The standard approach used by Sanaei (سنایی) panel operators is **Clean IP via Cloudflare CDN**:

1. **Domain + Cloudflare DNS** — Point a domain to the server, enable Cloudflare proxy (orange cloud)
2. **SSL Certificate** — Use Let's Encrypt or Cloudflare's SSL
3. **VLESS + WS + TLS behind Cloudflare** — Traffic goes through Cloudflare edge IPs (which are clean/not blocked)
4. **Clean IP Scanner** — Tools like `CF-Scan` find working Cloudflare edge IPs in Iran
5. **Nahan (نهان)** — Cloudflare Worker-based tool that auto-generates clean IP configs with VLESS/Trojan

**Why this works better than direct Reality for some users:**
- Real server IP is completely hidden behind Cloudflare
- Cloudflare edge IPs are "clean" (not flagged by DPI)
- Harder to block — would need to block all of Cloudflare
- Multi-location configs possible (different Cloudflare edge IPs per region)

**Architecture:** Client → Cloudflare Edge (clean IP) → Origin Server (your VPS)

> Full clean IP setup guide: `references/clean-ip-setup.md`

### Reality Blocking in Iran (July 2026 status)
- Reality is the ONLY protocol that has survived sustained in Iran
- GFW (MCI) can detect Reality by monitoring heavy traffic on a single IP
- Recommendation: share server with max 5-7 users, keep traffic moderate
- New aggressive blocking waves target servers with >200 users
- Fresh IPs work better than old ones
- Port 443 is mandatory for Reality

### Best Reality Targets for Iran
- `www.microsoft.com:443` (most reliable)
- `www.cloudflare.com:443`
- `www.apple.com:443`
- `dl.google.com:443`
- Must NOT be blocked in the target network
- SNI must match dest exactly

### Fragment Settings (for CDN/WS fallback)
```json
"fragment": {
  "packets": "tlshello",
  "length": "100-200",
  "interval": "10-20"
}
```
- Note: Iran's DPI has adapted to classic TCP fragmentation in 2026
- Newer SNI-spoofing tools may be needed if fragment is detected

### Key Pitfalls for Iran
- Trojan SNI is visible to DPI → blocked in 2-7 days
- Reality detected when >20 users share one IP with heavy traffic
- Hysteria2 fails when ISPs block/throttle UDP
- CDN WS is slowest but most reliable fallback
- Clock sync is critical for Reality (NTP within 30 seconds)
- Always use `fp=chrome` fingerprint for Reality
- `flow: xtls-rprx-vision` mandatory for best performance
- XTLS-Vision enables Splice on Linux → zero-copy transfer

> Full research data with benchmarks and detection methods: `references/iran-dpi-bypass.md`
> Hysteria2 creation debugging notes: `references/hysteria2-pitfalls.md`

## Pitfalls

### API Gotchas
- **OpenAPI JSON has control chars** — `json.loads()` fails without `re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', content)` first.
- **GET vs POST confusion** — `/server/getNewX25519Cert` and `/server/getNewUUID` are **GET**, not POST. The spec is correct; always check `method` in the OpenAPI before assuming POST for "action" endpoints.
- **`port` must be integer** — `"port": "443"` fails with `cannot unmarshal string into Go struct field .alias.port of type int`. Always use `"port": 443`.
- **Hysteria2 without TLS** — works with `security: "none"` and no cert. Client link needs `insecure=1`. If TLS is desired, provide cert paths in `tlsSettings`.

### Share Link Construction (CRITICAL)
- **Panel's `/clients/links/{email}` may omit `pbk` and `fp`** for Reality inbounds. The generated URI is incomplete — clients will fail to connect.
- **Always construct VLESS Reality links manually** with all required params:
  ```
  vless://UUID@HOST:443?flow=xtls-rprx-vision&security=reality&pbk=PUBLIC_KEY&fp=chrome&sni=SNI&sid=SHORT_ID&spx=%2F&type=tcp#NAME
  ```
- Required fields: `flow`, `security`, `pbk`, `fp`, `sni`, `sid`, `spx`, `type`
- Missing any of these → client handshake fails silently or with cryptic error

### Hysteria2 Creation (multiple gotchas)
- **`"version": 2` is mandatory in settings** — without it, Xray fails with `version != 2`. The panel does NOT add this automatically.
- **`streamSettings.network: "udp"` required** — despite the error `unknown transport protocol: udp` appearing when `version: 2` is missing, the correct working config needs BOTH `"version": 2` in settings AND `"streamSettings": { "network": "udp" }`. The error is misleading — it's not about the network value, it's about missing version.
- **Port must be integer** — `"port": "8443"` (string) fails. Use `"port": 8443`.
- **Working Hysteria2 payload:**
  ```json
  {
    "remark": "Hysteria2-8443",
    "protocol": "hysteria",
    "port": 8443,
    "settings": {
      "version": 2,
      "auth": "password",
      "authStr": "<password>",
      "upMbps": 100,
      "downMbps": 100
    },
    "streamSettings": { "network": "udp" },
    "enable": true
  }
  ```
- **Hysteria2 share link:** `hy2://PASSWORD@HOST:PORT?insecure=1&type=udp#NAME`
- **Client must be attached** after inbound creation via `POST /clients/{email}/attach` with `{"inboundIds": [INBOUND_ID]}`

### Crash-Loop Cascade (CRITICAL)
- **A broken inbound crashes ALL of Xray.** If any single inbound config is invalid (e.g., Hysteria2 with missing `version: 2`), Xray enters a crash-loop (`exit status 23`). This kills EVERY inbound — including working ones like Reality.
- **Symptoms:** `XRAY: Failed to start` repeated every 2 seconds in panel logs. All ports go dark. No traffic flows. Client connects but gets no data.
- **Fix:** Immediately delete the broken inbound via `POST /inbounds/del/{id}`, then `POST /server/restartXrayService`. Reality starts working again within seconds.
- **Prevention:** Always add inbounds ONE AT A TIME. After each creation, verify `GET /server/status` shows `state: running`. If it shows `error`, the last inbound you added is the problem.
- **Panel log cache:** Deleted inbounds' error logs persist in the panel log buffer. Seeing old `in-8443-udp` errors does NOT mean the inbound still exists — check `GET /inbounds/list` to confirm.

### Stale Xray Config Tag Collision (CRITICAL)
- **Deleting an inbound via API removes it from the panel DB but may NOT clean the Xray config template.** The old inbound (with its tag like `in-443-tcp`) persists in the running Xray config. When a new inbound is created with the same auto-generated tag, Xray crashes with: `existing tag found: in-443-tcp`.
- **Symptoms:** Panel says inbound is deleted, but `GET /server/getConfigJson` still shows the old inbound. New inbound creation succeeds via API but Xray fails to start. Error loop every 2 seconds.
- **Fix (nuclear clean):**
  1. Delete all inbounds via API
  2. Fetch the Xray template: `GET /server/getConfigJson`
  3. Remove ALL non-API inbounds from the JSON (keep only `tag: api`)
  4. Update the template: `POST /xray/update` with the cleaned JSON
  5. Restart: `POST /server/restartXrayService`
  6. Verify clean config with `GET /server/getConfigJson` — should show only `api` inbound
  7. NOW create the new inbound
- **Prevention:** After deleting an inbound, always verify with `GET /server/getConfigJson` that the tag is gone before creating a new one with the same tag. The `GET /inbounds/list` endpoint only shows the panel DB, NOT the actual Xray config.

### ICMP Ping Doesn't Work Through VPN
- Users often test VPN by pinging. **ICMP (ping) does not traverse V2Ray/Xray tunnels.** Only TCP and UDP traffic goes through.
- This is NOT a bug. If the app connects without error and the VPN icon appears, the tunnel is working.
- Correct test: open a web browser and visit a site, or use an app that requires internet.

### NAT/Proxy Detection (CRITICAL — check BEFORE creating any inbound)
- **If the server is behind NAT/proxy/load balancer, Reality AND WebSocket will fail silently.** The client connects, no error, but zero traffic flows. This is the most common cause of "config is correct but nothing works."
- **Diagnostic (run FIRST, before creating any inbound):**
  1. Resolve the panel domain: `curl https://dns.google/resolve?name=DOMAIN&type=A` → get resolved IP
  2. Get server's public IP: `GET /server/status` → `publicIP.ipv4`
  3. **If these IPs differ → server is behind proxy. Reality will NOT work.**
  4. Test direct TCP to the real IP: `curl https://REAL_IP:443 --connect-timeout 5`
  5. If it times out → ports are not exposed. Only protocols that traverse the proxy work.
  6. **Check response headers:** `curl -sk -I https://DOMAIN/` — look for `server: istio-envoy` (Kubernetes/Istio), `server: cloudflare` (CF proxy), or other reverse proxy signatures.
  7. **WebSocket path test:** `curl -sk -o /dev/null -w "%{http_code}" -H "Upgrade: websocket" -H "Connection: Upgrade" https://DOMAIN/ws` — if returns 401 (not 404), the panel HAS a WebSocket endpoint and Envoy IS forwarding WS connections to the panel.
- **When behind proxy, the panel v3.5.0+ proxies Xray WS traffic through its own port:**
  - Envoy/Istio routes external:443 → panel:2053
  - Panel's Go server detects VLESS/VMess WS traffic and forwards to Xray internally
  - **Result: VLESS + WS + TLS works! Reality does NOT work.** (Reality needs raw TCP passthrough)
  - **This is by design** — managed hosting providers (Caasify etc.) use this architecture intentionally
- **Working solution for managed hosting (Caasify/Istio):**
  1. Create VLESS + WS inbound (no TLS in streamSettings — the Envoy proxy handles TLS termination)
  2. **WS PATH MUST be one that the reverse proxy actually forwards.** Test which paths work: `curl -sk -o /dev/null -w "%{http_code}" https://DOMAIN/<path>`. Only paths returning 200/301/401 are forwarded. Paths returning 404 are NOT forwarded by Envoy.
  3. In Caasify/Istio: only `/` (200), `/panel` (301), `/ws` (401) are forwarded. Custom paths like `/vless-ws` return 404.
  4. **Solution: use root path `/` as the WS path.** The panel's Go server detects VLESS traffic on `/` and forwards it to Xray internally.
  5. Client connects with `security: tls` (TLS to Envoy), then WS upgrade inside
  6. Link format: `vless://UUID@DOMAIN:443?encryption=none&type=ws&host=DOMAIN&path=%2F&security=tls&sni=DOMAIN#NAME`
  7. Client v2rayNG settings: security=tls, network=ws, sni=DOMAIN, path=/, host=DOMAIN, flow=empty
  8. **Critical:** flow must be EMPTY (no xtls-rprx-vision) for WS mode — XTLS only works with Reality/TCP
  9. **Critical:** security must be `tls` (not `reality`) — Envoy handles TLS, Reality needs raw TCP passthrough which Envoy doesn't support
- **When NOT behind proxy (direct VPS):**
  - Reality is the best protocol (highest DPI resistance, 99.1% success in Iran)
  - VLESS + Reality + XTLS-Vision on port 443
- **Caasify-specific findings:** Domain resolves to `.252` (Envoy) but panel reports `.96` (real IP). Port 443 on real IP is closed from outside. `server: istio-envoy` header confirms Kubernetes/Istio. Panel WS at `/ws` returns 401 (panel's own WS for live updates). **Envoy only forwards 3 paths:** `/` (200), `/panel` (301), `/ws` (401) — all others return 404. Reality doesn't work because Envoy terminates TLS and only forwards to panel:2053, not Xray:443. **Important correction:** do not assume VLESS+WS+TLS works just because the panel exists. In this managed-hosting layout, panel-generated WS links may point to an internal port (e.g. 2083) that is not externally reachable, and `/` returning 200 is just the panel HTML, not a WS upgrade. If `curl -H 'Upgrade: websocket' ... /` returns 200 instead of 101, the WS path is not actually proxied to Xray. In that case you need a provider-exposed port or a different host/setup; the panel alone is insufficient.

### General
- `settings`, `streamSettings`, `sniffing` can be JSON objects (preferred) or JSON-encoded strings (legacy)
- `POST /inbounds/add` needs full payload, not partial
- UUID is generated server-side via `GET /server/getNewUUID` if omitted
- Xray restart is automatic after inbound/client changes
- `fail2ban` is required for per-client IP limits
- Subscription URL format: `https://<panel-host>/sub/<subId>`
- Panel web runs on port 2053 (not 80/443)
- **Same port conflict** — Cannot bind two inbounds to the same port (e.g., both Reality TCP 443 and Hysteria2 UDP 443 need different port numbers unless the protocol区分 is sufficient). Use distinct ports: Reality on TCP 443, Hysteria2 on UDP 8443.
- **Self-connection test fails** — Testing port 443 from the same server (`curl https://185.226.93.96:443`) often times out. This is normal — many servers block self-connections. The port can still be reachable from external clients.

### User Preferences
- User is Iranian, prefers Farsi responses
- User refers to 3x-ui as "پنل سنایی" (Sanaei panel) — the developer is MHSanaei
- User wants practical results, not lengthy explanations — if it works, say "اوکی شد" and move on
- "ایپی تمیز" (clean IP) = Cloudflare CDN approach to hide real server IP
- **Don't assume the hosting is broken.** When something doesn't work, investigate the architecture FIRST. The user said "بیخودی ک پنل نمی‌زارن حتما ی راهی داره" — managed panels ARE designed to work, find how. Check reverse proxy config, response headers (`server: istio-envoy`), which paths are forwarded, etc. before concluding it's impossible.
- **Don't repeat the same approach.** If creating/deleting inbounds isn't working, stop and analyze WHY before trying again. The user got frustrated with repeated config churn without progress.
