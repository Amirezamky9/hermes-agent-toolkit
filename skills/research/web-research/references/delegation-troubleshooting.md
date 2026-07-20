# Custom Provider Truncation Bug — Delegation Workaround

## Problem
Custom provider names with special characters (dots, hyphens) get truncated during
delegation resolution. Example: `custom:9router-8uoc.srv1699470.hstgr.cloud` becomes
`custom:9ruter` — an unresolvable name.

Error: `Cannot resolve delegation provider 'custom:9ruter': Unknown provider 'custom:9ruter'`

## Symptoms
- `delegate_task` always fails with provider resolution error
- Main model works fine (custom provider resolves correctly for main model)
- Built-in providers (openrouter, nous, zai, kimi-coding, minimax) listed as available
- Custom provider endpoint is reachable and returns valid responses

## Fix
Switch delegation to a built-in provider while keeping the custom provider for the main model:

```yaml
# In config.yaml
model:
  default: opencode200k
  provider: custom:9router-8uoc.srv1699470.hstgr.cloud  # keep custom for main

delegation:
  provider: openrouter              # use built-in for delegation
  model: meta-llama/llama-3.1-8b-instruct
  subagent:
    provider: openrouter
    model: meta-llama/llama-3.1-8b-instruct
```

Requires `OPENROUTER_API_KEY` in `.env`.

## Config Reload Gotcha
Modifying `delegation.*` in config.yaml while a gateway session is running does NOT
take effect. The running session caches the old delegation config at startup. Must
`/restart` gateway or start a new CLI session.

## Verification
```bash
# Test custom provider endpoint directly
curl -s "https://PROVIDER/v1/models" -H "Authorization: Bearer $KEY" | python3 -m json.tool

# Test built-in provider works for delegation
curl -s "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta-llama/llama-3.1-8b-instruct","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":5}'
```

## Related: Gateway 409 Conflict
When starting a gateway, if you see `Another gateway instance is already running`,
kill the stale process first:
```bash
pgrep -la hermes   # find stale PIDs
kill -9 PID        # force kill
hermes gateway run  # start fresh
```
