# Caddy Setup on Hostinger VPS — Step by Step

## Context

This server has **no Docker**, no Traefik, no nginx. Ports 80/443 are free.
Caddy is the simplest reverse-proxy that auto-provisions SSL via LetsEncrypt.

## Installation

```bash
# Caddy is NOT in apt repo by default — use official method
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

## Config → `/etc/caddy/Caddyfile`

```caddy
sync.YOUR_DOMAIN {
    reverse_proxy localhost:9999
}
```

Replace `YOUR_DOMAIN` with the actual domain. Reload:

```bash
sudo systemctl reload caddy
```

## DNS Setup (Hostinger hPanel)

Before Caddy will get a cert, DNS must resolve:

1. Login to **hPanel** → **Domains** → your-domain → **DNS Zone Editor**
2. Add an **A record**:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `sync` | `152.239.112.214` | 14400 (default) |

3. Wait ~5 minutes for DNS propagation

Alternatively, a **wildcard A record** (`*` → `152.239.112.214`) catches all subdomains in one shot.

## Verify

```bash
# Check Caddy is running
systemctl status caddy

# Check the cert was provisioned
curl -v https://sync.YOUR_DOMAIN/health 2>&1 | grep "SSL certificate verify"

# Test the actual endpoint
curl -s -X POST https://sync.YOUR_DOMAIN/api/browser-sync \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"test.com","cookies":[{"name":"test","value":"val"}]}'
```

## Also available: Hostinger's own AI/panel

The user mentioned Hostinger has an AI assistant in their panel. You can prompt it:
> "Add these labels to the existing service that has port 8787. Do NOT create a new service — the container is already on the traefik network."

This only applies if they're using Hostinger's Docker hosting with built-in Traefik. If they have a plain VPS, ignore this and use Caddy above.

## Pitfalls

- **Server has NO `ps`/`pgrep`/`socat`** — use `/proc` inspection or `systemctl` directly
- **Container user is non-root** but has `sudo` for Caddy commands
- **Port 8000 is occupied** by an unknown app — never use it
- **Caddy needs port 80 + 443** free. If something else is on those ports, Caddy won't start
- **First HTTPS request is slow** (~5s) while LetsEncrypt provisions the initial cert
