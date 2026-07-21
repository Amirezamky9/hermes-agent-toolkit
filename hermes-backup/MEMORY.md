Telegram gateway: user 943724562, DM topics, keepalive daemon. Server: hermes-webui-wvwd.srv1699470.hstgr.cloud, 152.239.112.214, mym8m.cloud, Traefik, n8n, supabase. .venv read-only, python3 3.12.13, Node.js v24.18.0 via nvm.
§
Agent-Reach v1.5.0: 8 channels (web, YouTube, V2EX, RSS, Exa, Bilibili, Twitter, Reddit). Delegation: groq/llama-3.3-70b + deepseek-v4-flash, max 4. crawl4ai, ffmpeg.
§
Hermes skills stack: research-manager (top orchestrator) → deep-research v2 → web-research. All in ~/.hermes/skills/research/
§
Security: never show tokens/secrets — read from files, pipe to commands. Prefers stdlib http.server over FastAPI. User runs credential commands himself.
§
Webhook platform on 8644 (HMAC). Cookie-sync FastAPI on 9999 (Bearer, CacheCat only). Tunnel watchdog every 12h → Telegram.
§
User (Amirezamky9, Persian, lazy-senior dev) wants direct, simple, raw answers — not architecture discussions. On operational tasks, give the result, not the process. Gets frustrated with over-explaining.
§
Topic 465358 (Amir): always load research-manager skill on research requests.
§
Build workflow: user wants step-by-step progress updates during multi-phase builds. Default direct build for ≤10 files, subagent for larger. Simple multiplayer web apps: Node.js + ws + single HTML, no frameworks. Port 3000 safe.