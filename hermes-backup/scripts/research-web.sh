#!/usr/bin/env bash
# research-web.sh — Fast web research via Exa + Jina (compressed output)
# Usage: bash research-web.sh "query" [max_results]
# Output: compressed text, minimal tokens

set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:?Usage: research-web.sh \"query\" [max_results]}"
MAX_RESULTS="${2:-3}"

# Step 1: Exa semantic search (compressed)
echo "=== SEARCH ==="
mcporter call "exa.web_search_exa(query: \"$QUERY\", numResults: $MAX_RESULTS)" 2>&1 | \
  grep -E "^(Title|URL|Published|Highlights):" | head -30

echo ""
echo "=== TOP PAGES ==="
# Step 2: Read top 2 results via Jina (compressed to first 500 chars each)
URLS=$(mcporter call "exa.web_search_exa(query: \"$QUERY\", numResults: 2)" 2>&1 | \
  grep "^URL:" | sed 's/^URL: //' | head -2)

i=0
for url in $URLS; do
  i=$((i+1))
  echo "--- Page $i: $url ---"
  curl -s "https://r.jina.ai/$url" -H "Accept: text/plain" --max-time 15 2>/dev/null | \
    head -c 2000
  echo ""
  echo "..."
done
