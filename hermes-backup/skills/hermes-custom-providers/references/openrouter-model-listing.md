# OpenRouter Model Discovery

## API Endpoint

```
GET https://openrouter.ai/api/v1/models
```

No auth required for listing. Returns JSON with `data[]` array of model objects.

## Model Object Shape

```json
{
  "id": "deepseek/deepseek-v4-flash",
  "name": "DeepSeek V4 Flash",
  "context_length": 1048576,
  "pricing": {
    "prompt": "0.00000009",
    "completion": "0.00000018",
    "image": "0",
    "request": "0"
  },
  "top_provider": { "max_completion_tokens": 131072, "is_moderated": false },
  "architecture": { "modality": "text->text", "tokenizer": "other", "instruct_type": null }
}
```

**Key fields:**
- `id` — model identifier used in API calls (e.g. `deepseek/deepseek-v4-flash`)
- `pricing.prompt` / `pricing.completion` — per-token cost (string, $/token). `"0"` = free
- `context_length` — max context window in tokens
- Free models have `id` ending in `:free` or pricing `"0"` for both prompt/completion

## Quick Python Listing (curl | python3)

```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import json,sys
data=json.load(sys.stdin)
models=data.get('data',[])
free=[m for m in models if m.get('pricing',{}).get('prompt','1')=='0']
for m in sorted(free, key=lambda x: x['id']):
    print(f\"{m['id']} | ctx={m.get('context_length','?')}\")
"
```

## Notable Free Models (as of 2025)

| Model | Context | Notes |
|-------|---------|-------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1M | Largest free model |
| `nvidia/nemotron-3-super-120b-a12b:free` | 1M | Good balance |
| `qwen/qwen3-coder:free` | 1M | Code-specialized |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 131K | Hermes-branded |
| `meta-llama/llama-3.3-70b-instruct:free` | 131K | Solid general |
| `google/gemma-4-31b-it:free` | 262K | Google open model |
| `openai/gpt-oss-120b:free` | 131K | OpenAI open model |

## Integration with Hermes Custom Providers

OpenRouter is an OpenAI-compatible endpoint. To use it as a custom provider:

```yaml
custom_providers:
  - name: openrouter
    base_url: https://openrouter.ai/api/v1
    key_env: OPENROUTER_API_KEY
    discover_models: true
```

```bash
echo 'OPENROUTER_API_KEY=sk-or-...' >> ~/.hermes/.env
```

Then reference models as `custom:openrouter/<model-id>` (e.g. `custom:openrouter/deepseek/deepseek-v4-flash`).
