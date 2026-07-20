#!/usr/bin/env bash
# research-tiktok.sh — تحقیق از TikTok
# Usage: research-tiktok.sh "query" [limit]
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:-}"
LIMIT="${2:-5}"

if [ -z "$QUERY" ]; then
    echo "Usage: research-tiktok.sh \"query\" [limit]"
    exit 1
fi

# Search TikTok via yt-dlp (ytsearch as proxy)
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
URLS=$(yt-dlp "ytsearch${LIMIT}:${QUERY}" \
    --flat-playlist --print "%(id)s %(title)s %(view_count)s %(duration)s" \
    --playlist-items 1-$LIMIT 2>/dev/null | head -$LIMIT)

if [ -z "$URLS" ]; then
    # Fallback: TikTok search page via Jina
    echo "[TikTok search via web]"
    curl -s "https://r.jina.ai/https://www.tiktok.com/search?q=$ENCODED" \
        -H "Accept: text/plain" --max-time 15 2>/dev/null | head -50
    exit 0
fi

echo "=== TikTok Results: $QUERY ==="
echo "$URLS" | while read -r line; do
    VID_ID=$(echo "$line" | awk '{print $1}')
    TITLE=$(echo "$line" | cut -d' ' -f2-)
    echo "🔗 https://www.tiktok.com/@_/video/$VID_ID"
    echo "   $TITLE"
    echo ""
done

# Get detailed info for first result
FIRST_URL=$(echo "$URLS" | head -1 | awk '{print $1}')
if [ -n "$FIRST_URL" ]; then
    echo "=== ویدیو اول: جزئیات ==="
    yt-dlp --dump-json --skip-download "https://www.tiktok.com/@_/video/$FIRST_URL" 2>/dev/null | \
        python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Title: {d.get(\"title\",\"?\")}')
print(f'Author: {d.get(\"uploader\",\"?\")}')
print(f'Duration: {d.get(\"duration\",\"?\")}s')
print(f'Views: {d.get(\"view_count\",\"?\")}')
print(f'Likes: {d.get(\"like_count\",\"?\")}')
print(f'Comments: {d.get(\"comment_count\",\"?\")}')
print(f'Tags: {d.get(\"tags\",[])}')
" 2>/dev/null
fi
