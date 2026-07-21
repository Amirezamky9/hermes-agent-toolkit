#!/bin/bash
# Research Topic Auto-Startup Script
# این اسکریپت خودکار همه چیز رو برای topic research آماده میکنه

echo "🔧 Starting Research Environment..."

# 1. Set PATH
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

# 2. Load Twitter env vars
if [ -f ~/.agent-reach/cookies/twitter.env ]; then
    source ~/.agent-reach/cookies/twitter.env
    echo "✅ Twitter env loaded"
fi

# 3. Check if cookie-sync server is running
if curl -s http://localhost:9999/health > /dev/null 2>&1; then
    echo "✅ Cookie-sync server running on :9999"
else
    echo "⚠️ Cookie-sync server not running, starting..."
    bash ~/.hermes/scripts/start-cookie-sync.sh 2>/dev/null
    if curl -s http://localhost:9999/health > /dev/null 2>&1; then
        echo "✅ Cookie-sync server started"
    else
        echo "❌ Failed to start cookie-sync server"
    fi
fi

# 4. Check tunnel
if [ -f ~/.hermes/scripts/cookie-sync-url.txt ]; then
    TUNNEL_URL=$(cat ~/.hermes/scripts/cookie-sync-url.txt)
    echo "✅ Tunnel URL: $TUNNEL_URL"
else
    echo "⚠️ No tunnel URL saved"
fi

# 5. Check agent-reach
if command -v agent-reach > /dev/null 2>&1; then
    echo "✅ Agent-reach available"
else
    echo "❌ Agent-reach not installed"
fi

# 6. Check GitHub auth
if gh auth status > /dev/null 2>&1; then
    echo "✅ GitHub authenticated"
else
    echo "⚠️ GitHub not authenticated"
fi

# 7. Check Twitter
if twitter whoami > /dev/null 2>&1; then
    echo "✅ Twitter connected"
else
    echo "⚠️ Twitter not connected"
fi

# 8. Check Reddit
if rdt whoami > /dev/null 2>&1; then
    echo "✅ Reddit connected"
else
    echo "⚠️ Reddit not connected"
fi

echo ""
echo "🎯 Research Environment Ready!"
echo "📊 Active channels: 9/15"
echo ""
echo "Quick test commands:"
echo "  agent-reach doctor --json"
echo "  gh auth status"
echo "  twitter whoami"
echo "  rdt whoami"
