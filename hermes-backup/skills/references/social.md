# Social — Multi-backend social platforms

Always run `agent-reach doctor --json` first to check active_backend per platform.

---

## XiaoHongShu (小红书)

| Backend | When | Command |
|---------|------|---------|
| OpenCLI | desktop (Chrome) | `opencli xiaohongshu search "query" -f yaml` |
| xiaohongshu-mcp | server / headless | `mcporter call 'xiaohongshu.get_login_qrcode()'` then scan QR |
| xhs-cli | legacy (2026-03 EOL) | `xhs login` → `xhs search "query"` |

## Twitter / X

| Backend | When | Command |
|---------|------|---------|
| twitter-cli | ✅ installed, needs cookie | `twitter search "query" -n 10` |
| OpenCLI | desktop fallback | `opencli twitter search "query" -f yaml` |
| bird | legacy fallback | `bird search "query"` |
| **Exa (mcporter)** | **fallback when search broken** | `mcporter call 'exa.web_search_exa(query: "site:twitter.com QUERY", numResults: 10)'` |

### ⚠️ twitter-cli: ClientTransaction bug (FIXED with patch)
If `twitter search` fails with `ClientTransaction: 'NoneType'` warning + 404:

**Root cause**: `_ensure_client_transaction()` fetches x.com without cookies → gets logged-out page → regex fails to find `ondemand.s` reference.

**Fix** (1-line patch to `twitter_cli/client.py`):
```python
# In _ensure_client_transaction(), after ct_headers = _gen_ct_headers():
ct_headers["Cookie"] = self._cookie_string or "auth_token=%s; ct0=%s" % (self._auth_token, self._ct0)
```

**Or use the automated patch script**:
```bash
bash ~/.hermes/skills/agent-reach/scripts/apply-twitter-patch.sh
```

Full patch location: `~/.local/share/pipx/venvs/twitter-cli/lib/python3.12/site-packages/twitter_cli/client.py` (line ~1073)

**After patching**, clear cache and test:
```bash
rm -f ~/.cache/twitter-cli/ct_cache.json
twitter search "test" -n 3
```

**Note**: This patch is on the pipx venv file. If twitter-cli is upgraded via `pipx upgrade twitter-cli`, the patch will be overwritten and must be re-applied. Consider saving the patch to `~/.agent-reach/patches/twitter-client-cookies.patch` for easy re-application.

**Workaround (no patch)**: Use Exa via mcporter for Twitter content search:
```bash
mcporter call 'exa.web_search_exa(query: "site:twitter.com QUERY", numResults: 10)'
```

- **Check upstream**: [public-clis/twitter-cli#69](https://github.com/public-clis/twitter-cli/issues/69)
- See [references/tool-diagnostics.md](references/tool-diagnostics.md) for full diagnostic workflow

### Cookie setup (headless/server)

Cookies are stored in `~/.agent-reach/config.yaml`. twitter-cli reads from env vars, so export them:

```bash
# Add to ~/.bashrc (permanent)
grep -q "TWITTER_AUTH_TOKEN" ~/.bashrc 2>/dev/null || cat >> ~/.bashrc << 'EOF'
export TWITTER_AUTH_TOKEN="$(grep twitter_auth_token ~/.agent-reach/config.yaml | cut -d' ' -f2)"
export TWITTER_CT0="$(grep twitter_ct0 ~/.agent-reach/config.yaml | cut -d' ' -f2)"
EOF
source ~/.bashrc
twitter whoami  # verify
```

**Pitfall**: `agent-reach configure twitter-cookies` stores values in config.yaml but does NOT export env vars. twitter-cli needs `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` as env vars. On headless servers, always add exports to `~/.bashrc`.

### Cookie setup (desktop)

`agent-reach configure twitter-cookies "header-string"` (cookie from Cookie-Editor Chrome extension). Or: `agent-reach configure --from-browser chrome` to auto-extract.

## Bilibili

| Backend | When | Command |
|---------|------|---------|
| bili-cli | ✅ installed, zero-config | `bili search "query" --type video -n 5` |
| OpenCLI | subtitles | `opencli bilibili subtitle BVxxx` |
| B站搜索 API | pure curl fallback | `curl -s "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY"` |

bili-cli commands:
```bash
bili search "AI" --type video -n 10
bili info BV1xx411c7mD               # video details
bili hot                              # trending
bili rank --type weekly               # weekly ranking
bili audio BV1xx411c7mD               # audio only
```

## V2EX

| Backend | Command |
|---------|---------|
| Public API | `curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"` |
| Node topics | `curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python" -H "User-Agent: agent-reach/1.0"` |
| Topic detail | `curl -s "https://www.v2ex.com/api/topics/show.json?id=123456" -H "User-Agent: agent-reach/1.0"` |
| Replies | `curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=123456" -H "User-Agent: agent-reach/1.0"` |
| User info | `curl -s "https://www.v2ex.com/api/members/show.json?username=user" -H "User-Agent: agent-reach/1.0"` |

## Reddit

| Backend | When | Command |
|---------|------|---------|
| OpenCLI | desktop (Chrome) | `opencli reddit search "query" -f yaml` |
| rdt-cli | server / headless | `rdt search "query" --limit 10` |

**No zero-config path.** Anonymous .json API blocked, official API needs approval.
Configure: `rdt login` (auto browser cookie extraction) or paste cookie header string.

## Facebook

| Backend | When | Command |
|---------|------|---------|
| OpenCLI | desktop only | `opencli facebook search "query" -f yaml` |
| OpenCLI | groups | `opencli facebook groups -f yaml` |
| OpenCLI | profile | `opencli facebook profile zuck -f yaml` |

Needs Chrome extension + browser login session. Not available on headless servers.

## Instagram

| Backend | When | Command |
|---------|------|---------|
| OpenCLI | desktop only | `opencli instagram search "query" -f yaml` (user search, not full-text) |
| OpenCLI | user posts | `opencli instagram user nasa -f yaml` |
| OpenCLI | explore | `opencli instagram explore -f yaml` |
| Embed page scrape | headless/server, no login | see [Instagram embed fallback](#instagram-embed-fallback) below |

OpenCLI only for search/profile. Note: search is user search, not post keyword search.

### Instagram embed fallback (no login, headless)

When OpenCLI is unavailable (server), you can scrape post/reel metadata from Instagram's **public embed page** (no login required). Instagram embeds post data as JSON in the page source.

**Approach:** fetch the embed page via a proxy that bypasses Instagram's anti-bot gate, then extract `contextJSON` from the embedded JS.

```bash
# 1. Fetch embed page via proxy
PROXY_URL="https://api.allorigins.win/get"  # may be unreliable; try alternatives
SHORTCODE="DaNzbz9SjoW"

curl -sL "$PROXY_URL?url=https://www.instagram.com/reel/$SHORTCODE/embed/" \
  -H "User-Agent: Mozilla/5.0" --max-time 20 -o /tmp/ig_embed.html

# 2. Extract contextJSON (gql_data contains caption, owner, video_url, stats)
python3 -c "
import re, json

with open('/tmp/ig_embed.html') as f:
    html = f.read()

# The JSON lives in a JS call: contextJSON='{...}'
m = re.search(r'contextJSON.*?\'(.*?)\'', html, re.DOTALL)
if m:
    # Unescape
    raw = m.group(1).replace('\\u00253D', '=').replace('\\u00252B', '+').replace('\\/','/')
    data = json.loads(raw)
    media = data.get('gql_data', {}).get('shortcode_media', {})

    caption = ''
    edges = media.get('edge_media_to_caption', {}).get('edges', [])
    if edges:
        caption = edges[0].get('node', {}).get('text', '')

    owner = media.get('owner', {})
    print(json.dumps({
        'id': media.get('id'),
        'shortcode': media.get('shortcode'),
        'is_video': media.get('is_video'),
        'video_duration': media.get('video_duration'),
        'video_view_count': media.get('video_view_count'),
        'caption': caption,
        'owner_username': owner.get('username'),
        'owner_followers': owner.get('edge_followed_by', {}).get('count'),
        'like_count': media.get('edge_liked_by', {}).get('count'),
        'comment_count': media.get('edge_media_to_comment', {}).get('count'),
        'video_url': media.get('video_url'),
        'music_artist': media.get('clips_music_attribution_info', {}).get('artist_name'),
        'music_song': media.get('clips_music_attribution_info', {}).get('song_name'),
    }, indent=2, ensure_ascii=False))
"
```

**Pitfalls:**
- **allorigins.win is unreliable** — rate-limited, frequently times out (20s+), and returns errors. If it fails, try alternatives like `https://r.jina.ai/https://www.instagram.com/reel/SHORTCODE/embed/` (Jina Reader) or a different proxy.
- Instagram uses aggressive anti-bot measures. A plain `curl` directly to the embed page usually returns a wall of CSS/JS (no content). You **must** go through a proxy that spoofs a real browser.
- This technique is **read-only**. You can't post, like, or comment.
- The embed page only works for **public** posts. Private accounts always require login.
- Both `/reel/SHORTCODE/` and `/p/SHORTCODE/` embed pages work the same way.
- `contextJSON` uses unicode escapes (`\u00253D` for `=`, etc.) — decode them before parsing.
