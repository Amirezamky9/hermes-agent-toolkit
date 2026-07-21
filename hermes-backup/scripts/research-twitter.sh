#!/usr/bin/env bash
# research-twitter.sh — Twitter research with rate limit protection
# Usage: bash research-twitter.sh "query" [max_results] [delay_seconds]
# Output: compressed tweet data

set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
source ~/.agent-reach/cookies/twitter.env 2>/dev/null
export TWITTER_AUTH_TOKEN TWITTER_CT0

QUERY="${1:?Usage: research-twitter.sh \"query\" [max_results] [delay_seconds]}"
MAX_RESULTS="${2:-5}"
DELAY="${3:-2}"

echo "=== TWEETS ==="
twitter search "$QUERY" -n "$MAX_RESULTS" 2>&1 | \
  python3 -c "
import sys, json, yaml

try:
    data = yaml.safe_load(sys.stdin.read())
    if not data or not data.get('data'):
        print('No results')
        sys.exit(0)
    
    for tweet in data['data'][:$MAX_RESULTS]:
        author = tweet.get('author', {})
        metrics = tweet.get('metrics', {})
        print(f'@{author.get(\"screenName\",\"?\")} ({metrics.get(\"likes\",0)} likes, {metrics.get(\"retweets\",0)} RT)')
        text = tweet.get('text','')[:200]
        print(f'  {text}')
        print()
except Exception as e:
    print(f'Parse error: {e}')
    print(sys.stdin.read()[:500])
" 2>&1

sleep "$DELAY"
