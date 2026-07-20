#!/bin/bash
# Apply twitter-cli ClientTransaction cookie patch
# Fixes: 'NoneType' object has no attribute 'group' error in _ensure_client_transaction()
# Root cause: x.com fetch without cookies returns logged-out page

set -e

# Find the twitter-cli client.py
VENV_PATH=$(find ~/.local/share/pipx/venvs/twitter-cli -name "client.py" -path "*/twitter_cli/*" 2>/dev/null | head -1)

if [ -z "$VENV_PATH" ]; then
    echo "❌ twitter-cli not found in pipx venvs"
    exit 1
fi

# Check if already patched
if grep -q 'ct_headers\["Cookie"\] = self._cookie_string' "$VENV_PATH" 2>/dev/null; then
    echo "✅ Patch already applied"
    exit 0
fi

# Backup
cp "$VENV_PATH" "${VENV_PATH}.bak"

# Apply patch
sed -i '/ct_headers = _gen_ct_headers/a\            # Include cookies so x.com returns the logged-in homepage\n            # (needed for ondemand.s reference and twitter-site-verification meta)\n            ct_headers["Cookie"] = self._cookie_string or "auth_token=%s; ct0=%s" % (self._auth_token, self._ct0)' "$VENV_PATH"

# Clear cache
rm -f ~/.cache/twitter-cli/ct_cache.json 2>/dev/null

# Verify
if grep -q 'ct_headers\["Cookie"\] = self._cookie_string' "$VENV_PATH"; then
    echo "✅ Patch applied successfully"
    echo "   File: $VENV_PATH"
    echo "   Test: twitter search \"test\" -n 3"
else
    echo "❌ Patch failed to apply"
    exit 1
fi
