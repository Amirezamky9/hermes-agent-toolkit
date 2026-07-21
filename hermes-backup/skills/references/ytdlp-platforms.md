# yt-dlp Platform Test Results (2026-07-20)

Tested on: Linux server, yt-dlp 2026.07.04, no browser, cloud IP.

## Test Methodology

For each platform: `yt-dlp --dump-json --skip-download URL` then check:
- Info extraction (title, duration, views)
- Subtitle availability
- Format count
- Video download
- Audio extraction

## Results by Platform

### ✅ Fully Working

#### YouTube
- **Info**: ✅ Full metadata (title, duration, views, likes, description)
- **Formats**: 37 (mp4, webm, m3u8; 360p to 4K)
- **Subtitles**: ✅ English + auto-generated (multiple languages)
- **Download**: ✅ Video + audio (separate or merged with ffmpeg)
- **Config required**: `~/.config/yt-dlp/config` must contain:
  ```
  --js-runtimes node
  --cookies ~/.agent-reach/cookies/youtube-cookies.txt
  --remote-components ejs:github
  ```
- **Pitfall**: Without `--remote-components ejs:github`, only storyboard thumbnails are returned (YouTube 2025+ JS challenge)

#### TikTok
- **Info**: ✅ Title, duration, views, author
- **Formats**: 10 (h264_540p, bytevc1_540p/720p)
- **Subtitles**: ❌ None available
- **Download**: ✅ Video (mp4, combined audio+video)
- **Audio-only**: ⚠️ Not available as separate format
- **Pitfall**: "Requested format is not available" when using `-f bestaudio` — TikTok only serves combined formats

### ⚠️ Needs Authentication/Cookies

#### Instagram
- **Error**: "No CSRF token set by Instagram API"
- **Fix**: `--cookies-from-browser chrome` or manual cookie export
- **Note**: Public reels may work with cookies, private content requires login

#### Douyin (TikTok China)
- **Error**: "Fresh cookies (not necessarily logged in) are needed"
- **Fix**: Export cookies from browser

#### Reddit
- **Error**: "HTTP Error 403: Blocked" + "impersonation not available"
- **Fix**: Install `curl_cffi` for `--impersonate` flag
- **Alternative**: Use `rdt-cli` instead (works with cookie-sync cookies)

### ❌ Not Working (use alternative tool)

#### Bilibili
- **Error**: "HTTP Error 412: Precondition Failed"
- **Alternative**: `bili-cli` (search, hot, audio, feed, favorites)
- **bili-cli commands**: `search`, `hot`, `feed`, `audio`, `like`, `coin`, `favorites`, `following`, `history`

#### Twitter/X
- **Error**: "No video could be found in this tweet" (for text tweets)
- **Note**: yt-dlp can download VIDEO from tweets, but not extract text/metadata
- **Alternative**: `twitter-cli` for search, user info, text content

#### Vimeo
- **Error**: "Failed to fetch macos OAuth token: 401" + "impersonation not available"
- **Fix**: Install `curl_cffi` for `--impersonate`

#### SoundCloud
- **Error**: 404 (depends on URL validity)
- **Note**: Works with valid track/playlist URLs

#### Bandcamp
- **Note**: Works with valid album/track URLs

#### Bluesky
- **Error**: "HTTP Error 400: Bad Request"
- **Note**: Extractor exists but may need valid post IDs

#### LinkedIn
- **Error**: 404 (requires login)
- **Alternative**: `linkedin-scraper-mcp` or Jina Reader

#### Pinterest
- **Error**: "Unsupported URL"
- **Note**: Only video pins may work

#### Tumblr
- **Error**: "Unsupported URL"
- **Note**: Generic extractor fallback fails

#### Snapchat
- **Error**: Unsupported
- **Note**: Requires app

### 📺 News/Media (URL-dependent)

#### CNN, BBC, Al Jazeera
- **Status**: Extractors exist but depend on valid video URLs
- **Note**: Need actual video page URLs, not article URLs

## Rate Limits Observed

| Platform | Delay Between Calls | Max Consecutive |
|----------|-------------------|-----------------|
| YouTube | 2s | No strict limit |
| TikTok | 2s | No strict limit |
| Exa Search | 1s | No strict limit |
| Jina Reader | 0s | No strict limit |
| Twitter (twitter-cli) | 2s | 5 before break |
| Reddit (rdt-cli) | 1s | No strict limit |

## Token Optimization

Using `research-youtube.sh` instead of raw `yt-dlp --dump-json`:
- Raw output: ~50,000 tokens per video
- Compressed: ~200 tokens (title, duration, views, subtitles)
- Savings: 99%

## Recommendations

1. **YouTube**: Primary tool, works great with proper config
2. **TikTok**: Good for video download, no subtitle support
3. **Bilibili**: Use `bili-cli` instead of yt-dlp
4. **Twitter**: Use `twitter-cli` for text, yt-dlp only for video download
5. **Reddit**: Use `rdt-cli` instead of yt-dlp
6. **Instagram**: Need cookies export from browser
7. **Everything else**: Check if extractor exists, test with valid URL
