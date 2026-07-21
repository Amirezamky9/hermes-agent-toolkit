# Traefik + DNS Setup for Hermes Webhooks — Hostinger VPS

**Server:** `hermes-webui-wvwd.srv1699470.hstgr.cloud` (IP `152.239.112.214`)
**Traefik:** Runs via Docker, `network_mode: host`, ports 80/443, Docker provider only, Let's Encrypt via `ACME_EMAIL` from `.env`.

## Architecture

```
my-domain.com ──→ A record (152.239.112.214) ──→ Traefik (host network)
                                                        │
                ┌───────────────────────────────────────┼──────────────────────────┐
                ▼                                       ▼                          ▼
        webui subdomain                          webhook subdomain          cookie-sync subdomain
         → label on hermes-webui                  → needs config              → needs config
         → port 8787                              → port 8644 (HMAC)          → port 9999 (Bearer)
```

## DNS (Hostinger Panel)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `*` | `152.239.112.214` | Auto |

Wildcard `*` covers ALL subdomains in one record — scalable, no per-subdomain config.

## Problem: Traefik has Docker provider only

Current Traefik uses `--providers.docker=true` with NO file provider. Two services need routes but run outside Docker:

| Service | Port | Runs as | Issue |
|---------|------|---------|-------|
| Hermes Webhook Platform | 8644 | Native `hermes gateway run` | No Docker labels |
| Cookie-sync FastAPI | 9999 | Native `python3 main.py` | No Docker labels |

Both are reachable at `http://127.0.0.1:PORT` because Traefik is on host network.

### Solution: Add file provider to Traefik

```bash
# 1. Create a dyn config file
cat > /docker/traefik/dynamic.yml << 'EOF'
http:
  routers:
    webhook-gateway:
      rule: "Host(`webhook.YOUR_DOMAIN`)"
      entryPoints: ["websecure"]
      tls:
        certResolver: letsencrypt
      service: webhook-gateway
    cookie-sync:
      rule: "Host(`sync.YOUR_DOMAIN`)"
      entryPoints: ["websecure"]
      tls:
        certResolver: letsencrypt
      service: cookie-sync
  services:
    webhook-gateway:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:8644"
    cookie-sync:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:9999"
EOF

# 2. Mount it + add file provider to Traefik's docker-compose.yml
# Add volume:
#   - /docker/traefik/dynamic.yml:/dynamic.yml
# Add command flag:
#   - --providers.file.filename=/dynamic.yml
```

### Alternative: Caddy alongside Traefik

Simpler but adds a second reverse proxy:

```yaml
# In docker-compose.yml as second service
caddy:
  image: caddy:latest
  network_mode: host
  volumes:
    - /docker/caddy/Caddyfile:/etc/caddy/Caddyfile
```

Caddyfile:
```
webhook.YOUR_DOMAIN { reverse_proxy 127.0.0.1:8644 }
sync.YOUR_DOMAIN    { reverse_proxy 127.0.0.1:9999 }
```

## Verify

```bash
curl -v https://webhook.YOUR_DOMAIN/health 2>&1 | grep SSL
curl -v https://sync.YOUR_DOMAIN/health 2>&1 | grep SSL
```

## ⚠️ Pitfalls

- **Port 8000 occupied** by another app — never use for new services.
- **Router names must be unique** within Traefik.
- **File provider path** must be writable by Traefik container (bind mount).
