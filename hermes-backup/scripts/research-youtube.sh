#!/usr/bin/env bash
# research-youtube.sh — YouTube video research (compressed output)
# Usage: bash research-youtube.sh "URL_or_query" [max_results]
# Output: video metadata + subtitle preview

set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:?Usage: research-youtube.sh \"URL_or_query\" [max_results]}"
MAX_RESULTS="${2:-3}"

# If it's a URL, get info directly
if echo "$QUERY" | grep -qE "(youtube\.com|youtu\.be)"; then
  echo "=== VIDEO INFO ==="
  yt-dlp --dump-json --skip-download "$QUERY" 2>/dev/null | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'Title: {d[\"title\"]}')
print(f'Channel: {d.get(\"channel\",\"?\")}')
print(f'Duration: {d.get(\"duration_string\",\"?\")}')
print(f'Views: {d.get(\"view_count\",0):,}')
print(f'Likes: {d.get(\"like_count\",0):,}')
print(f'Description: {d.get(\"description\",\"\")[:500]}')
subs = list(d.get('subtitles',{}).keys())[:5]
auto = list(d.get('automatic_captions',{}).keys())[:5]
print(f'Subtitles: {subs}')
print(f'Auto-captions: {auto}')
"
  
  # Try to get English subtitles
  echo ""
  echo "=== SUBTITLES (English) ==="
  yt-dlp --write-sub --write-auto-sub --sub-lang en --skip-download \
    --sub-format vtt -o "/tmp/yt-subs-%(id)s" "$QUERY" 2>/dev/null
  SUBFILE=$(find /tmp -name "yt-subs-*.en.vtt" -newer /tmp 2>/dev/null | head -1)
  if [ -n "$SUBFILE" ]; then
    head -c 3000 "$SUBFILE" | grep -v "^$" | tail -c 2000
  else
    echo "No subtitles available"
  fi
else
  # Search YouTube
  echo "=== SEARCH ==="
  yt-dlp "ytsearch${MAX_RESULTS}:${QUERY}" --dump-json --skip-download 2>/dev/null | \
    python3 -c "
import json, sys
for line in sys.stdin:
    try:
        d = json.loads(line)
        print(f'Title: {d[\"title\"]}')
        print(f'URL: https://youtube.com/watch?v={d[\"id\"]}')
        print(f'Duration: {d.get(\"duration_string\",\"?\")} | Views: {d.get(\"view_count\",0):,}')
        print()
    except:
        pass
"
fi
