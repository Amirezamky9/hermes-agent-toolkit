# Video — YouTube, Bilibili, Xiaoyuzhou

## Backend: yt-dlp (YouTube)

### Get video info (JSON)
```bash
yt-dlp --dump-json "URL" | python3 -m json.tool
```

### Download subtitles only
```bash
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"
```

### Download auto-generated captions
```bash
yt-dlp --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
```

### List available formats
```bash
yt-dlp -F "URL"
```

### Download audio only
```bash
yt-dlp -f bestaudio --extract-audio --audio-format mp3 -o "/tmp/%(title)s.%(ext)s" "URL"
```

### Search YouTube
```bash
yt-dlp "ytsearch10:AI agents tutorial" --dump-json | python3 -c "import json,sys; [print(json.dumps({k:v for k,v in json.loads(l).items() if k in ('title','id','webpage_url','duration','view_count','channel')}, indent=2)) for l in sys.stdin]"
```

## Backend: bili-cli (Bilibili)

### Search
```bash
bili search "AI agent" --type video -n 10
```

### Video info
```bash
bili info BV1xx411c7mD
```

### Trending
```bash
bili hot
bili rank --type weekly
bili rank --type monthly
```

### Audio only
```bash
bili audio BV1xx411c7mD
```

## Backend: OpenCLI (Bilibili subtitles)
```bash
opencli bilibili subtitle BV1xx411c7mD -f yaml
```

## Backend: Xiaoyuzhou (podcast transcription)

### Prerequisites
- ffmpeg (system package)
- Groq API key: `agent-reach configure groq-key gsk_xxxxx`

### Transcribe
```bash
bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh https://www.xiaoyuzhoufm.com/episode/xxxxx
```

## Bot Detection (2025+) — YouTube blocks cloud/datacenter IPs

YouTube aggressively blocks cloud IPs (AWS, GCP, Azure, etc.) with "Sign in to confirm you're not a bot". This affects yt-dlp, youtube-transcript-api, and all API-based approaches. **This is the #1 issue when working from servers.**

See [references/youtube-bot-detection.md](references/youtube-bot-detection.md) for full solutions.

### Quick diagnosis
If yt-dlp gives `Sign in to confirm you're not a bot`, your IP is blocked. Client rotation alone usually doesn't fix it on datacenter IPs.

### Solution hierarchy (try in order)

**1. PO Token (best for automation)**
```bash
pip install bgutil-ytdlp-pot-provider
# Start PO Token server
cd /tmp && git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server && npm ci && npx tsc
node build/main.js &
export YT_DLP_POT_PROVIDER_URL="http://127.0.0.1:4416"
# Now yt-dlp uses PO tokens automatically
yt-dlp --extractor-args "youtube:player_client=web,android_vr,tv_downgraded" URL
```

**2. Residential SOCKS5 proxy (if PO token doesn't work)**
```bash
# Format: socks5://user:pass@ip:port
yt-dlp --proxy "socks5://user:pass@proxy:port" --extractor-args "youtube:player_client=web,android_vr,tv_downgraded" URL
```

**3. User's cookies (last resort)**
```bash
yt-dlp --cookies-from-browser chrome URL
# Or manual cookies.txt file
yt-dlp --cookies cookies.txt URL
```

### PySocks IPv6 pitfall
When using PySocks with SOCKS5 proxy for YouTube, force IPv4 or you get `PySocks doesn't support IPv6`:
```python
_original_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo
```

### Reference repo
`CRtheHILLS/yt-dlp-rescue` — battle-tested guide with 5-layer defense (client rotation + PO Token + WARP proxy + cache management + retry/backoff). Updated March 2026.

## Pitfalls
- **YouTube bot detection on cloud IPs (2025+)** — yt-dlp, transcript APIs, and innertube all blocked. See section above.
- **NEVER use yt-dlp for Bilibili** — B站's CDN has blocked yt-dlp since 2026-06 (HTTP 412). Use bili-cli.
- bili-cli upstream stopped updates 2026-03; still works for search/info/audio
- yt-dlp YouTube search may return fewer results on server IPs
- Podcast transcription: free Groq Whisper limit ~7200s/hour
