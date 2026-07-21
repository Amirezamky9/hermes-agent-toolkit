#!/usr/bin/env bash
# research-bilibili.sh — تحقیق از Bilibili
# Usage: research-bilibili.sh "query" [limit]
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:-}"
LIMIT="${2:-5}"

if [ -z "$QUERY" ]; then
    echo "Usage: research-bilibili.sh \"query\" [limit]"
    exit 1
fi

echo "=== Bilibili Search: $QUERY ==="

# Search via bili-cli
bili search "$QUERY" --type video -n "$LIMIT" 2>/dev/null | python3 -c "
import yaml,sys
try:
    d = yaml.safe_load(sys.stdin)
    items = d.get('data', [])
    for i, item in enumerate(items, 1):
        print(f'{i}. {item.get(\"title\",\"?\")}')
        print(f'   Author: {item.get(\"author\",\"?\")}')
        print(f'   Views: {item.get(\"play\",\"?\")}')
        print(f'   Duration: {item.get(\"duration\",\"?\")}')
        print(f'   URL: https://www.bilibili.com/video/{item.get(\"bvid\",\"?\")}')
        print()
except:
    print('Parse error')
" 2>/dev/null

echo "=== Bilibili Hot ==="
bili hot -n 3 2>/dev/null | python3 -c "
import yaml,sys
try:
    d = yaml.safe_load(sys.stdin)
    items = d.get('data', {}).get('items', [])
    for i, item in enumerate(items, 1):
        print(f'{i}. {item.get(\"title\",\"?\")}')
        print(f'   Author: {item.get(\"owner\",{}).get(\"name\",\"?\")}')
        print(f'   Duration: {item.get(\"duration\",\"?\")}')
        print(f'   URL: {item.get(\"url\",\"?\")}')
        print()
except:
    print('Parse error')
" 2>/dev/null
