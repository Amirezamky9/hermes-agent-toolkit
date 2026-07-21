#!/usr/bin/env bash
# research-reddit.sh — Reddit research (compressed output)
# Usage: bash research-reddit.sh "query" [subreddit] [max_results]

set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:?Usage: research-reddit.sh \"query\" [subreddit] [max_results]}"
SUBREDDIT="${2:-}"
MAX_RESULTS="${3:-5}"

echo "=== REDDIT ==="
if [ -n "$SUBREDDIT" ]; then
  rdt search "$QUERY" --subreddit "$SUBREDDIT" --sort relevance --limit "$MAX_RESULTS" 2>&1 | \
    head -c 3000
else
  rdt search "$QUERY" --limit "$MAX_RESULTS" 2>&1 | \
    head -c 3000
fi
