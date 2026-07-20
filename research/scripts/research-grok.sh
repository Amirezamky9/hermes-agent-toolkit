#!/usr/bin/env bash
# research-grok.sh — تحقیق از طریق xAI API / Grok
# Usage: research-grok.sh "query" [model]
# نیاز به XAI_API_KEY در محیط یا ~/.agent-reach/cookies/xai.env
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:-}"
MODEL="${2:-grok-4}"

if [ -z "$QUERY" ]; then
    echo "Usage: research-grok.sh \"query\" [model]"
    echo "Models: grok-4, grok-4-mini, grok-3"
    exit 1
fi

# Load API key
if [ -f ~/.agent-reach/cookies/xai.env ]; then
    source ~/.agent-reach/cookies/xai.env
fi

if [ -z "${XAI_API_KEY:-}" ]; then
    echo "❌ XAI_API_KEY تنظیم نشده"
    echo "   از console.x.ai API key بگیر"
    echo "   و در ~/.agent-reach/cookies/xai.env ذخیره کن:"
    echo '   XAI_API_KEY=xai-...'
    
    # Fallback: search Grok public tweets
    echo ""
    echo "=== جستجوی پاسخ‌های عمومی Grok ==="
    twitter search "from:grok $QUERY" -n 3 2>/dev/null || echo "twitter-cli در دسترس نیست"
    exit 0
fi

echo "=== Grok Research: $QUERY (model: $MODEL) ==="

RESPONSE=$(curl -s "https://api.x.ai/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $XAI_API_KEY" \
    -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
            {\"role\": \"system\", \"content\": \"You are a research assistant. Be concise and factual. Max 500 words.\"},
            {\"role\": \"user\", \"content\": \"$QUERY\"}
        ],
        \"max_tokens\": 1000,
        \"temperature\": 0.3
    }" --max-time 30 2>/dev/null)

echo "$RESPONSE" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    if 'choices' in d:
        msg = d['choices'][0]['message']['content']
        print(msg)
        usage = d.get('usage',{})
        print(f'\n--- Tokens: {usage.get(\"total_tokens\",\"?\")} ---')
    elif 'error' in d:
        print(f'Error: {d[\"error\"].get(\"message\",d[\"error\"])}')
    else:
        print(json.dumps(d, indent=2)[:500])
except:
    print(sys.stdin.read()[:500])
" 2>/dev/null
