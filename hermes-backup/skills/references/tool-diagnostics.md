# Tool Diagnostics — Systematic Troubleshooting

When agent-reach tools fail, follow this diagnostic sequence before assuming local misconfiguration.

## Diagnostic Workflow

```
Step 1: agent-reach doctor --json    → per-platform status + active_backend
Step 2: Test the specific command    → reproduce the failure
Step 3: Verbose mode                 → twitter -v, rdt --verbose
Step 4: Manual API test              → curl directly to API endpoint
Step 5: Check upstream               → GitHub issues for the tool repo
Step 6: Apply workaround or fix
```

## Step-by-Step

### 1. Health Check
```bash
agent-reach doctor --json
```
Shows per-platform: `status` (ok/warn/off), `active_backend`, `backends` list.

### 2. Reproduce
Run the exact failing command. Note the error code and message.

### 3. Verbose Mode
```bash
twitter -v search "query" -n 5    # shows auth flow, endpoint URLs, HTTP codes
rdt search "query" --limit 5      # rdt has no -v, check exit code
```
Verbose output reveals: cookie loading, ClientTransaction init, retry attempts, HTTP status codes.

### 4. Manual API Verification
Bypass the CLI entirely to test if credentials are valid:
```bash
# Twitter — test auth_token directly
source ~/.agent-reach/cookies/twitter.env
curl -s "https://api.x.com/1.1/account/verify_credentials.json" \
  -H "Cookie: auth_token=${TWITTER_AUTH_TOKEN}; ct0=${TWITTER_CT0}" \
  -H "x-csrf-token: ${TWITTER_CT0}"
# Expected: user JSON. Error code 89 = invalid/expired token.
```

### 5. Check Upstream
```bash
# Find the tool's repo
pipx list | grep TOOLNAME
# Check issues
gh issue list --repo OWNER/REPO --search "error message keywords"
gh release list --repo OWNER/REPO --limit 5
```

## Known Issues (as of 2026-07)

### twitter-cli: ClientTransaction init failure (FIXED)
- **Symptom**: `WARNING: Failed to init ClientTransaction: 'NoneType' object has no attribute 'group'`
- **Impact**: `whoami` works, `search`/`feed`/`timeline` fail with 404
- **Root cause**: `_ensure_client_transaction()` fetches x.com WITHOUT cookies → gets logged-out page (73KB vs 269KB) → `ON_DEMAND_FILE_REGEX` finds index but hash lookup fails → `get_ondemand_file_url()` returns None → `'NoneType' object has no attribute 'group'`
- **Fix**: 1-line patch to `twitter_cli/client.py`:
  ```python
  # In _ensure_client_transaction(), after ct_headers = _gen_ct_headers():
  ct_headers["Cookie"] = self._cookie_string or "auth_token=%s; ct0=%s" % (self._auth_token, self._ct0)
  ```
  File: `~/.local/share/pipx/venvs/twitter-cli/lib/python3.12/site-packages/twitter_cli/client.py` (line ~1073)
- **After patching**: `rm -f ~/.cache/twitter-cli/ct_cache.json` then test
- **Upstream**: [public-clis/twitter-cli#69](https://github.com/public-clis/twitter-cli/issues/69) (OPEN — fix not yet merged upstream)
- **Caveat**: Patch is on pipx venv file. `pipx upgrade twitter-cli` will overwrite it. Save patch to `~/.agent-reach/patches/twitter-client-cookies.patch` for easy re-application.
- **Workaround (no patch)**: Use Exa via mcporter for Twitter content search:
  ```bash
  mcporter call 'exa.web_search_exa(query: "site:twitter.com QUERY", numResults: 10)'
  ```
- **Diagnostic technique**: Compare response sizes — logged-out page ~73KB (no `ondemand.s`), logged-in page ~269KB (has `ondemand.s`). If curl_cffi returns small page, cookies aren't being sent.

### rdt-cli: credential.json empty fields
- `~/.config/rdt-cli/credential.json` may show `username: ""` and `token length: 0`
- **This is normal** — rdt-cli uses Reddit session cookie from `~/.agent-reach/cookies/hermes-cookies.json` instead
- If search/read still work, ignore empty credential.json

### Jina Search (s.jina.ai): Authentication Required
- **Symptom**: `401 AuthenticationRequiredError`
- **Cause**: Jina search endpoint now requires API key (no longer free tier)
- **Workaround**: Use Exa via mcporter instead (free, no API key needed)

### Jina Reader (r.jina.ai) + Reddit: 403 Forbidden
- Reddit blocks Jina's server-side requests
- **Workaround**: Use `rdt read POST_ID` instead — always works for logged-in Reddit content

## Cookie Sync Verification

After syncing cookies via webhook:
```bash
# Check file exists and is recent
ls -la ~/.agent-reach/cookies/twitter.env
ls -la ~/.agent-reach/cookies/hermes-cookies.json

# Verify env vars are set
source ~/.agent-reach/cookies/twitter.env
echo "AUTH_TOKEN: ${#TWITTER_AUTH_TOKEN} chars"
echo "CT0: ${#TWITTER_CT0} chars"
```

Expected lengths: AUTH_TOKEN ~40 chars, CT0 ~160 chars.
