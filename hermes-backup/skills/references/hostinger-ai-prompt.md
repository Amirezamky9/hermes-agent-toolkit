# Hostinger AI Assistant — Prompt & Pitfalls

When the user wants to delegate a Traefik setup task to Hostinger's built-in AI assistant (executes commands on the host via terminal), use this prompt template.

## Template

```
I need to add a webhook route to my existing Traefik setup.

My Traefik runs in Docker with network_mode: host. It uses Docker provider only (no file provider). Its docker-compose is at /docker/traefik/docker-compose.yml

I have an HTTP service running on localhost:<PORT> (Hermes Webhook Platform) on the host machine (not in Docker).

I want Traefik to route:
https://<domain>/webhooks/* → http://127.0.0.1:<PORT>

Please:
1. Create a dynamic config file at /docker/traefik/dynamic/webhook.yml with the router and service
2. Add --providers.file=true and --providers.file.directory=... to the Traefik docker-compose command section
3. Mount /docker/traefik/dynamic:/dynamic:ro in the docker-compose volumes section
4. Restart Traefik with docker compose

Make sure it uses the existing letsencrypt certresolver and websecure entrypoint.
```

## ⚠️ HARDENED PITFALL — AI ALWAYS skips steps 2 & 3

**Confirmed across multiple independent attempts:** The Hostinger AI ALWAYS only creates the YAML file (step 1). It ALWAYS forgets:

- Adding `--providers.file=true` / `--providers.file.directory=/dynamic` to the Traefik command args
- Mounting the `/docker/traefik/dynamic` directory into the container's volumes section

**This is not a one-off — it is the AI's consistent pattern. Do NOT try a third time.**

**Symptom:** Requests hit the WebUI (port 8787) instead of the webhook (8644) → `HTTP 302 redirect → login?next=...` instead of `{"status": "accepted"}`.

**Trace logic to confirm:** When the Host header matches a Traefik Docker label rule (hermes-webui), Docker provider wins over file provider if file provider is not active. The 302 is the WebUI responding to an unrecognized POST.

**Fix path:** Abort the Traefik approach at the user's first sign of frustration. Go directly to Cloudflare quick tunnel — it's faster, simpler, and avoids the user having to babysit the AI.

## Recommended: Don't start this path

The Hostinger AI has **never** completed this task correctly. Only enter this path if:

1. The user explicitly says they want permanent DNS-based setup
2. AND you warn them upfront that the AI will likely miss steps
3. AND you're prepared to verify and fix the docker-compose.yml manually after the AI finishes

If at any point the user says "بییخالش", "بیخیال", or shows frustration → **abort Traefik immediately, switch to Cloudflare tunnel** with no apology or explanation.

## Manual sed fix (when you're doing it yourself)

Instead of relying on the AI, run these three commands directly on the host:

```bash
# 1. Add file provider flags after the last Docker provider line
sed -i 's/providers.docker.exposedbydefault=false/providers.docker.exposedbydefault=false\n      - --providers.file=true\n      - --providers.file.directory=\/dynamic/' /docker/traefik/docker-compose.yml

# 2. Add volume mount
sed -i 's|/var/run/docker.sock:/var/run/docker.sock:ro|/var/run/docker.sock:/var/run/docker.sock:ro\n      - /docker/traefik/dynamic:/dynamic:ro|' /docker/traefik/docker-compose.yml

# 3. Restart
docker compose -f /docker/traefik/docker-compose.yml up -d --force-recreate
```

## Alternative: Patch steps alone (if YAML already exists)

If the AI already created the YAML and you just need to enable + mount it, run only the two sed commands above, then restart.

## Verification

After setup:

```bash
curl -s -o /dev/null -w "%{http_code}" https://<domain>/webhooks/test-webhook \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"message":"test"}' | openssl dgst -sha256 -hmac '<SECRET>' | awk '{print $2}')" \
  -d '{"message":"test"}'
```

Expected: `200` / `{"status": "accepted"...}`  
Symptom of missed step: `302` → abort and tunnel.
