# YouTube Bot Detection — Bypass Guide (2025-2026)

## The Problem

YouTube aggressively blocks cloud/datacenter IPs with "Sign in to confirm you're not a bot". This affects:
- yt-dlp (all player_client options)
- youtube-transcript-api
- YouTube innertube API (all client types: WEB, ANDROID, IOS, TV)
- Invidious/Piped instances (most are down or blocked)
- Jina Reader (partial — gets title/chapters but not transcript)

## Solution 1: PO Token (Recommended for automation)

PO Token (Proof-of-Origin) proves you're not a bot. Two modes:

### Mode A: Plugin only
```bash
pip install bgutil-ytdlp-pot-provider
yt-dlp --js-runtimes node --remote-components ejs:github \
  --extractor-args "youtube:player_client=web,android_vr,tv_downgraded" URL
```

### Mode B: Dedicated server (better for production)
```bash
cd /tmp && git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server && npm ci && npx tsc
node build/main.js &
export YT_DLP_POT_PROVIDER_URL="http://127.0.0.1:4416"
yt-dlp --extractor-args "youtube:player_client=web,android_vr,tv_downgraded" URL
```

**Pitfall:** Running the server WITHOUT setting `YT_DLP_POT_PROVIDER_URL` — server runs fine but yt-dlp doesn't know it exists.

## Solution 2: Residential SOCKS5 Proxy

Residential IPs are not blocked by YouTube.

```bash
# curl test
curl -x socks5://user:pass@proxy:port https://httpbin.org/ip

# yt-dlp
yt-dlp --proxy "socks5://user:pass@proxy:port" URL

# Python (with PySocks)
pip install pysocks
```

### PySocks IPv6 pitfall
YouTube resolves to IPv6 (AAAA records). PySocks doesn't support IPv6. Force IPv4:
```python
import socket
_original_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo
```

## Solution 3: Cloudflare WARP Proxy

Routes through Cloudflare IPs (not blocked by YouTube). Needs root or userspace WireGuard.

```bash
# Install wgcf
curl -fsSL -o /usr/local/bin/wgcf https://github.com/ViRb3/wgcf/releases/download/v2.2.22/wgcf_2.2.22_linux_amd64
chmod +x /usr/local/bin/wgcf

# Register + generate config
wgcf register --accept-tos
wgcf generate

# Add SOCKS5 section to wgcf-profile.conf
echo -e "\n[Socks5]\nBindAddress = 127.0.0.1:1080" >> wgcf-profile.conf

# Start with wireproxy (userspace, no root needed)
wireproxy -c wgcf-profile.conf &
yt-dlp --proxy socks5://127.0.0.1:1080 URL
```

**Pitfall:** wireproxy binary may not be available. Alternative: gost (GO Simple Tunnel) with WireGuard config, or Docker WARP images.

## Solution 4: Client Rotation (May not fix IP blocking)

Only works if the issue is client-specific, not IP-level:
```bash
yt-dlp --extractor-args "youtube:player_client=tv_downgraded,web_embedded,android_vr" URL
```

Client status (March 2026):
| Client | Status | Token Needed |
|--------|--------|--------------|
| web | ❌ SABR only (360p) | PO Token |
| android_vr | ✅ Full DASH | None |
| tv_downgraded | ✅ Full DASH | None |
| web_creator | ✅ Full DASH | None |
| mweb | ✅ Full DASH | None |
| web_embedded | ✅ Full DASH | None |

## Solution 5: Browser Cookies (Last Resort)

```bash
yt-dlp --cookies-from-browser chrome URL
# Or export cookies.txt with browser extension
yt-dlp --cookies cookies.txt URL
```

**Pitfall:** Cookies expire and need periodic re-export. Not suitable for automation.

## YouTube Transcript Extraction (no yt-dlp needed)

If you only need the transcript (not the video):

### youtube-transcript-api
```python
from youtube_transcript_api import YouTubeTranscriptApi
ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id)
```
**Pitfall:** Also blocked on cloud IPs. Needs proxy or residential IP.

### Innertube API (with proxy)
```python
# POST to https://www.youtube.com/youtubei/v1/player
# Parse captionTracks from response
# Fetch caption URL
```

## Reference
- Repo: `CRtheHILLS/yt-dlp-rescue` — comprehensive guide, battle-tested
- Updated: March 2026
