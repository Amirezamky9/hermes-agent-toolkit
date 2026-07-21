# Installation Guide

Complete install guide for a fresh Hermes instance.

## What you install

- **Cookie Sync Client**: CacheCat-based Chrome extension on the user’s computer
- **Cookie Sync Backend**: FastAPI webhook server on the Hermes side
- **Telegram Toolkit**: Telegram automation, search, download, monitor
- **Research Tools**: Agent-Reach-based scripts and skills
- **Hermes Skills**: `agent-reach`, `deep-research`, `research-manager`, `web-research`, `deep-research-optimized`, `telegram-music-bot`

---

## 0) Prerequisites

### On the Hermes machine
- Python 3.10+
- Node.js 18+
- Git
- `pipx` recommended
- `gh` CLI for GitHub operations
- `mcporter` for Exa search integration

### On the user’s computer
- Google Chrome 88+
- Chrome extension installation access
- If testing cookie sync locally, a browser profile with the desired logins

---

## 1) Clone the repository

```bash
git clone https://github.com/Amirezamky9/hermes-agent-toolkit.git
cd hermes-agent-toolkit
```

---

## 2) Install Python dependencies

```bash
pip install -r requirements.txt
```

If you prefer isolated installs:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) Install Hermes skills

Copy the skills into Hermes:

```bash
cp -r skills/* ~/.hermes/skills/
chmod -R u+rwX ~/.hermes/skills
```

Copy the scripts into Hermes:

```bash
cp research/scripts/*.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.sh
```

### Skills included
- `agent-reach` — mother project router for 16 platforms
- `deep-research` — delegation-based deep research
- `research-manager` — research orchestration
- `web-research` — web research workflow
- `deep-research-optimized` — token-efficient deep research
- `telegram-music-bot` — music bot automation

---

## 4) Configure Agent-Reach

Install Agent-Reach if it is not already present on the Hermes machine:

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
agent-reach doctor --json
```

### What Agent-Reach provides
- Web search via Jina / Exa
- Twitter/X, Reddit, YouTube, GitHub
- Bilibili, Telegram, RSS, V2EX
- Facebook, Instagram, LinkedIn, XiaoHongShu
- Xueqiu, Grok

### Required installs for common backends
- `yt-dlp`
- `gh`
- `twitter-cli`
- `rdt-cli`
- `bili-cli`
- `mcporter`
- `telethon`

If a backend is `warn` or `off`, follow `agent-reach doctor --json` and install the missing backend.

---

## 5) Install the Telegram Toolkit

The Telegram toolkit lives in:

```text
telegram-toolkit/
```

### Setup

```bash
cd telegram-toolkit
cp config.yaml.example config.yaml
```

Edit `config.yaml` and set:
- `api_id`
- `api_hash`

### Get Telegram API keys
1. Go to https://my.telegram.org/apps
2. Create an app
3. Copy `api_id` and `api_hash`
4. Put them in `telegram-toolkit/config.yaml`

### First login

```bash
python3 cli.py info @telegram
```

Enter the phone number and verification code when prompted.

### Test commands

```bash
python3 cli.py search "query" --channel @channel
python3 cli.py download @channel --limit 10
python3 cli.py export @channel --format json
python3 cli.py monitor @channel
```

### Music bot

```bash
python3 music_bot.py search "Hello Adele"
python3 music_bot.py full "Hello Adele" --output /tmp/
```

---

## 6) Install the Cookie Sync Client Extension

The client extension is located in:

```text
cookie-sync/client/
```

### Build the extension

```bash
cd cookie-sync/client
npm install
npm run build
```

The build output is in:

```text
cookie-sync/client/dist/
```

### Load it into Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `cookie-sync/client/dist/`
5. The extension icon appears in the toolbar

### Configure the sync domains
In the extension dashboard:
1. Open **Hermes Sync** tab
2. Enable **Hermes Sync**
3. Add domains to sync
   - Example: `google.com`
   - Example: `notebooklm.google.com`
   - Example: `x.com`
4. Save

### What the client does
- Captures cookies for the selected domains
- Sends them to the backend as JSON
- Supports manual sync and cookie-change auto-sync
- Never logs cookie values to the console

---

## 7) Install the Hermes Backend

The backend lives in:

```text
cookie-sync/backend/
```

### Create env file

```bash
cd cookie-sync/backend
cp .env.example .env
```

Set:
- `HERMES_API_KEY`
- `STORAGE_STATE_PATH`
- `BACKEND_HOST`
- `BACKEND_PORT`

### Install backend dependencies

```bash
pip install -r requirements.txt
```

### Run backend

```bash
python main.py
```

Backend defaults to:
- `http://localhost:8000`
- `POST /api/browser-sync`
- `POST /api/test-connection`
- `GET /health`

---

## 8) Connect client to backend

In the extension Hermes Sync settings:

- **API URL**: `http://localhost:8000/api/browser-sync`
- **API Key**: the same value as `HERMES_API_KEY`

Then test:
1. Click **TEST CONNECTION** in the extension
2. Click **SYNC NOW**
3. Confirm the backend writes `storage_state.json`

---

## 9) Cloudflare fallback / remote access

If your backend is not reachable from the user’s computer:

### Option A — Cloudflare Tunnel
Expose the backend with a tunnel and use that public HTTPS URL in the extension.

Example:
```bash
cloudflared tunnel --url http://localhost:8000
```

Then set the extension API URL to the tunnel URL, for example:
```text
https://your-tunnel.trycloudflare.com/api/browser-sync
```

### Option B — Any HTTPS reverse proxy
Use nginx / Caddy / any HTTPS front door and point the extension there.

### Important
- The extension should use HTTPS when possible
- The API key is still required
- Do not expose the backend without auth

---

## 10) Hermes configuration

### Hermes-side config file
Copy:

```text
cookie-sync/hermes-browser-sync.config.json
```

Into the Hermes project root that will use the synced browser state.

### What it does
- Documents the webhook endpoint
- Documents the payload format
- Tells Hermes where to read the synced Playwright storage state

### Typical Hermes usage
In the Hermes automation project, point Playwright to the synced file:

```python
context = browser.new_context(storage_state="storage_state.json")
```

If Hermes uses a different path, update `STORAGE_STATE_PATH` in the backend and the Hermes config file together.

---

## 11) Full installation checklist

### Client machine
- [ ] Chrome installed
- [ ] Extension built
- [ ] `dist/` loaded in Chrome
- [ ] Domains added
- [ ] Hermes Sync enabled
- [ ] API URL set
- [ ] API key set

### Hermes backend
- [ ] Python deps installed
- [ ] `.env` created
- [ ] Backend started
- [ ] `/health` returns OK
- [ ] `POST /api/test-connection` works
- [ ] `POST /api/browser-sync` receives cookies

### Hermes agent
- [ ] `agent-reach doctor --json` is healthy
- [ ] Skills copied into `~/.hermes/skills/`
- [ ] Research scripts copied into `~/.hermes/scripts/`
- [ ] Telegram toolkit configured

---

## 12) Verification steps

### Verify extension build
```bash
cd cookie-sync/client
npm run build
ls dist/
```

### Verify backend
```bash
cd cookie-sync/backend
python main.py
curl http://localhost:8000/health
```

### Verify cookie sync
1. Configure a domain
2. Click **TEST CONNECTION**
3. Click **SYNC NOW**
4. Confirm `storage_state.json` was created or updated

### Verify Hermes install
```bash
agent-reach doctor --json
python3 telegram-toolkit/cli.py info @telegram
./research/scripts/research-web.sh "hello world"
```

---

## 13) Troubleshooting

### Extension build fails
- Make sure Node.js 18+ is installed
- Re-run `npm install`
- If the build tool fails, use `dist/` only if it already exists and is valid

### Backend unreachable
- Check the process is running
- Check the port number
- Use Cloudflare Tunnel if the backend is behind NAT/firewall

### No cookies synced
- Check selected domains
- Confirm the site domain matches the sync list
- Confirm the extension has permission to the site

### Authorization fails
- Make sure the API key in the extension matches the backend env
- Make sure the backend is reading the `.env`

### Cookies not useful in Hermes
- Ensure the Hermes project points to the same `storage_state.json`
- Ensure Hermes is using Playwright storage state, not a different auth mechanism

---

## 14) Files you should not commit

Do **not** commit:
- real cookies
- `.env`
- `storage_state.json`
- browser session files
- API keys
- tokens
- user-specific config

Use the provided `.env.example` and config templates only.

---

## 15) Credits

- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) — mother project
- [CacheCat](https://github.com/chinmay29hub/CacheCat) — browser extension base
- [Telethon](https://github.com/LonamiWebs/Telethon) — Telegram automation
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — media extraction
- [Exa](https://exa.ai) — web search
- [Jina Reader](https://github.com/jina-ai/reader) — article reading
