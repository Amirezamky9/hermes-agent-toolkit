# Clean IP (ایپی تمیز) Setup Guide for Iran

## Concept
In Iran, direct VPN server IPs get blocked by DPI quickly. "Clean IP" means routing traffic through Cloudflare's edge network, which has IPs that are not blocked.

## Approach 1: VLESS + WebSocket + TLS behind Cloudflare

### Requirements
- Domain name (any cheap domain works)
- Cloudflare account (free tier)
- Server with 3x-ui panel

### Steps
1. Add domain to Cloudflare, point DNS to server IP, enable proxy (orange cloud)
2. On server: install SSL cert via 3x-ui panel script (`x-ui` → Cloudflare SSL)
3. Create VLESS + WS + TLS inbound on 3x-ui:
   - Port: 443 (or custom)
   - Network: ws
   - Security: tls
   - Path: /ws (or custom)
4. Client connects via Cloudflare edge IP → Cloudflare proxies to origin

### Why it works
- Client sees Cloudflare IP, not your server IP
- Cloudflare IPs are "clean" — not flagged by DPI
- Traffic looks like normal HTTPS to Cloudflare

## Approach 2: Nahan (نهان) — Cloudflare Worker

A Cloudflare Worker that acts as a VLESS/Trojan reverse proxy.

### Setup
1. Create Cloudflare D1 database
2. Deploy Worker with Nahan code
3. Configure clean IPs in the dashboard
4. Auto-generates subscription links with clean IPs

### Features
- Multi-user profiles
- Clean IP multiplexer (auto-generates configs for multiple clean IPs)
- NAT64 support
- QR code generation

## Approach 3: Clean IP Scanner

Tools to find working Cloudflare edge IPs in Iran:
- `CF-Scan-TolidMelli` — Scans Cloudflare IP ranges, tests TLS connection, measures speed
- Output: list of clean IPs that work in Iran

## Key Points
- Clean IP configs are SLOWER than direct Reality (extra hop through Cloudflare)
- But much MORE RELIABLE in Iran (harder to block)
- Best practice: Offer both Reality (fast) and Clean IP (reliable) to users
- Panel operators (Sanaei/سنایی style) typically set up multi-location nodes with clean IPs
- **Always check hosting architecture FIRST** — don't assume the server has direct IP access

## Approach 4: Managed Panel Hosting (Caasify/Istio)

Some hosting providers (e.g., Caasify) run3x-ui behind Kubernetes/Istio Envoy proxy. Only port 443 is exposed, and it routes to the panel's internal port (2053).

### Architecture
```
Client → Envoy(:443) → Panel(:2053) → Xray(internal)
```

### Key Findings
- Domain resolves to Envoy IP (e.g., .252), panel reports different real IP (e.g., .96)
- `server: istio-envoy` in response headers confirms Kubernetes/Istio
- Panel has own WebSocket endpoint at `/ws` (returns 401 = needs auth)
- Panel v3.5.0+ proxies WebSocket-based Xray traffic through its own port
- **Reality does NOT work** (needs raw TCP passthrough that Envoy doesn't provide)
- **VLESS + WS + TLS DOES work** (panel proxies the WS upgrade internally)

### Working Configuration
1. Create VLESS + WS inbound (no TLS cert needed — Envoy handles TLS termination)
2. Client connects with `security: tls` to domain on port 443
3. Envoy terminates TLS, forwards to panel, panel routes to Xray

### Client Link Format
```
vless://UUID@DOMAIN:443?encryption=none&type=ws&host=DOMAIN&path=%2Fvless-ws&security=tls&sni=DOMAIN#VLESS-WS
```

### Why Panel Can't Use Reality
Reality requires the raw TCP connection to reach Xray directly. Envoy intercepts all port 443 traffic and proxies HTTP/WS to the panel. The panel's Go server can detect and proxy WebSocket upgrades, but it cannot proxy raw Reality handshakes — those are opaque to the HTTP reverse proxy.

## References
- Nahan: https://github.com/itsyebekhe/nahan
- CF-Scan: https://github.com/xpersian/CF-Scan-TolidMelli
- Stealth Proxy VPS Setup: https://github.com/RezaXAfrasyabi/stealth-proxy-vps-setup
