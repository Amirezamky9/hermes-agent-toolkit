# Provider Verification Pattern

This reference captures the discovery/verification approach when setting up a custom OpenAI-compatible provider.

## Endpoint model discovery

Custom providers with `discover_models: true` call `{base_url}/models` with the API key in `Authorization: Bearer <key>`.
The `/v1/models` response must follow the OpenAI format:
```json
{
  "object": "list",
  "data": [
    {"id": "model-id-1", "object": "model", "owned_by": "combo"},
    {"id": "model-id-2", "object": "model", "owned_by": "nvidia"}
  ]
}
```

## Direct curl test

```bash
curl -s -H "Authorization: Bearer $API_KEY" \
  https://your-endpoint.example.com/v1/models | python3 -m json.tool
```

## Direct Python verification (bypasses all caches)

```python
import os
from hermes_cli.models import fetch_api_models

key = os.environ.get("MY_KEY_ENV", "")
url = "https://your-endpoint.example.com/v1"
live = fetch_api_models(key, url)
if live:
    print(f"{len(live)} models:")
    for m in sorted(live):
        print(f"  {m}")
```

This calls the exact same `fetch_api_models()` that `list_authenticated_providers()` section 4 uses for custom providers. No caching, no fallback.

## Script verification

Use the bundled script:
```bash
python3 scripts/verify-live-models.py            # all custom providers
python3 scripts/verify-live-models.py 9ruter     # single provider
python3 scripts/verify-live-models.py --refresh  # force live fetch
```

## Python verification chain

```python
from hermes_cli.config import get_compatible_custom_providers, load_config
from hermes_cli.model_switch import list_authenticated_providers

cfg = load_config()
cps = get_compatible_custom_providers(cfg)

providers = list_authenticated_providers(
    custom_providers=cps, refresh=True
)
```

## The `should_probe` gate

Controls whether section 4 hits the live `/v1/models` endpoint:

```python
should_probe = (
    bool(api_url)                              # base_url is set
    and (bool(api_key) or not grp["models"])    # has key OR no explicit list
    and grp.get("discover_models", True)        # not opt-out
)
```

If `should_probe` is `False`, only the explicit `models:` list from config.yaml is shown, even if the endpoint is live.

## Two caching layers (important)

| Cache | Path | Scope | Used by custom providers? |
|-------|------|-------|--------------------------|
| `provider_models_cache.json` | `~/.hermes/provider_models_cache.json` | `cached_provider_model_ids()` → `provider_model_ids()` | **No** — custom providers call `fetch_api_models` directly |
| `model_catalog.json` | `~/.hermes/cache/model_catalog.json` | WebUI curated catalog (openrouter + nous) | **No** — custom providers not in this file |

**Fallacy**: Clearing `provider_models_cache.json` does NOT fix a stale custom provider model list. Custom providers bypass it.

## Internal flow (Hermes source)

`list_authenticated_providers()` in `hermes_cli/model_switch.py`:

1. **Section 1-2**: Built-in canonical providers (OpenRouter, Anthropic, etc.)
2. **Section 3**: User-defined `providers:` dict entries
3. **Section 3b**: Bare `model.provider: custom` fallback
4. **Section 4**: `custom_providers:` list entries — grouped by (api_url, credential_identity, api_mode, extra_headers)

`fetch_api_models()` in `hermes_cli/models.py` calls `probe_api_models()` which tries `{base_url}/models` with URL heuristics (appends `/v1` or strips it as needed).

## Source file locations for debugging

- `hermes_cli/model_switch.py` — `list_authenticated_providers()`, `parse_model_flags()`
- `hermes_cli/models.py` — `fetch_api_models()` (line 3598), `probe_api_models()` (line 3513), `cached_provider_model_ids()` (line 2622), `clear_provider_models_cache()` (line 2676)
- `hermes_cli/inventory.py` — `build_models_payload()`, `load_picker_context()`
