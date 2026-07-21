# AGENTS.md — Research Topic

## Auto-Load Protocol
When the user sends a message in the Research topic, ALWAYS load these skills in order:

1. **research-manager** — Top-level orchestrator (ALWAYS FIRST)
2. **deep-research** — Execution engine for complex research
3. **web-research** — Multi-source data gathering
4. **agent-reach** — Platform-specific content fetching

## Quick Reference

### Cookie-Sync Webhook
- **Server**: localhost:9999
- **Tunnel URL**: `https://arctic-eating-replica-producing.trycloudflare.com`
- **API Key**: `7jJt8VW7OvdbhgMiJ5bVy9BWZOtJHMBBC1p82zIatmQ`
- **Cron Job**: `cookie-sync-watchdog`
- **Skill**: `cookie-sync-webhook`

### Active Channels (9/15)
| Platform | Backend | Status |
|----------|---------|--------|
| GitHub | gh CLI | ✅ `@Amirezamky9` |
| Twitter/X | twitter-cli | ✅ `@amirezamk912` |
| Reddit | rdt-cli | ✅ `u/amirmky912` |
| YouTube | yt-dlp | ✅ |
| Bilibili | bili-cli | ✅ |
| V2EX | Public API | ✅ |
| RSS | feedparser | ✅ |
| Exa Search | mcporter | ✅ |
| Web | Jina Reader | ✅ |

### Environment Files
- Twitter env: `~/.agent-reach/cookies/twitter.env`
- Tunnel URL: `~/.hermes/scripts/cookie-sync-url.txt`
- API Key: `~/.hermes/scripts/cookie-sync-apikey.txt`

### Startup Script
```bash
bash ~/.hermes/scripts/research-startup.sh
```

### Health Check
```bash
agent-reach doctor --json
gh auth status
twitter whoami
rdt whoami
```

## Research Workflow
1. **Load skills** (research-manager → deep-research → web-research → agent-reach)
2. **Check health** (agent-reach doctor --json)
3. **Classify complexity** (Low/Medium/High)
4. **Select mode** (Quick/Standard/Deep/Code Audit/etc.)
5. **Execute** (direct tools or delegate to subagents)
6. **Synthesize** (merge, deduplicate, finalize)

## Important Notes
- Gateway restart: User will sync CacheCat manually
- GitHub: Auth restored, account `Amirezamky9`
- Twitter: Env vars in `~/.agent-reach/cookies/twitter.env`
- Reddit: Logged in as `u/amirmky912`
- Cookie-sync: FastAPI server on port 9999, cloudflared tunnel active
