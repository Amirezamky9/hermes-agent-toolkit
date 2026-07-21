# Model Availability Testing

The `/v1/models` endpoint only tells you what models are **listed** — not which ones actually **work**. Models can be listed but return 503 (rate limited), timeout, 404 (dead endpoint), or produce unusable output (leaking thinking tags, empty content). Always test with actual chat completion requests.

## Quick test script

```python
import yaml, json, requests, time

with open('/home/$USER/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)

key = cfg['custom_providers'][0]['api_key']
base_url = cfg['custom_providers'][0]['base_url']

def test_model(model, max_tokens=200):
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say exactly: TEST OK"}],
                "max_tokens": max_tokens,
                "stream": False,
            },
            timeout=45,
        )
        raw = resp.text.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            decoder = json.JSONDecoder()
            data, _ = decoder.raw_decode(raw)

        if resp.status_code == 200 and "choices" in data:
            content = (data["choices"][0].get("message", {}).get("content") or "")
            reasoning = data["choices"][0].get("message", {}).get("reasoning_content") or ""
            finish = data["choices"][0].get("finish_reason", "?")
            usage = data.get("usage", {})
            has_think = "<think>" in content
            return f"✅ finish={finish} content='{content[:60]}' {'[leaks-think]' if has_think else ''}"
        else:
            error = data.get("error", {}).get("message", str(data)[:80])
            return f"❌ HTTP {resp.status_code}: {error[:80]}"
    except requests.Timeout:
        return "⏰ TIMEOUT"
    except Exception as e:
        return f"💥 {type(e).__name__}: {str(e)[:80]}"

# Fetch model list first
resp = requests.get(f"{base_url}/models", headers={"Authorization": f"Bearer {key}"}, timeout=10)
models = [m['id'] for m in resp.json().get('data', [])]
print(f"Found {len(models)} listed models\n")

for model in sorted(models):
    result = test_model(model)
    print(f"  {model}: {result}")
    time.sleep(0.3)
```

## What to look for

| Signal | Meaning | Action |
|--------|---------|--------|
| `✅ finish=stop` with clean content | Model works | Use it |
| `✅ finish=length` with empty content | Reasoning model consumed all tokens on thinking | Increase `max_tokens` to ≥200, or avoid for subagents |
| `❌ HTTP 503` | Rate limited / overloaded backend | Avoid as primary; use as distant fallback only |
| `❌ HTTP 404` | Dead endpoint, model removed | Remove from config entirely |
| `⏰ TIMEOUT` (>30s) | Model too slow or backend unresponsive | Avoid entirely |
| `[leaks-think]` in content | Model leaks `<think>` tags into output | Avoid for subagents (pollutes extracted data) |

## Model role selection

| Role | Needs | Good candidates |
|------|-------|----------------|
| **Orchestrator** | Reasoning, planning | Models with reasoning tokens that produce clean output at ≥200 tokens |
| **Subagent worker** | Speed, clean extraction | Fast models with no reasoning overhead, clean output |

**Rule**: Never use a reasoning model as a subagent worker unless you've verified it produces clean output at the token limit subagents typically use (50-200 tokens per response).

## Example: 9router provider results (July 2026)

| Model | Status | Notes |
|-------|--------|-------|
| `opencode200k` | ✅ | Reasoning model, needs ≥200 tokens |
| `groq/openai/gpt-oss-120b` | ✅ | Fast, clean |
| `groq/llama-3.3-70b-versatile` | ✅ | Fast, clean, no reasoning overhead |
| `kimchi/deepseek-v4-flash` | ✅ | Fast, clean, good for subagents |
| `kimchi/kimi-k2.7` | ✅ | Fast, clean |
| `groq/qwen/qwen3-32b` | ⚠️ | Leaks `<think>` tags |
| `nvidia/deepseek-ai/deepseek-v4-flash` | ❌ | 503 rate limits, verbose reasoning |
| `nvidia/deepseek-ai/deepseek-v4-pro` | ❌ | Timeout (>30s) |
| `nvidia/nemotron-3-ultra-550b-a55b` | ❌ | 404 dead endpoint |
| `nvidia/minimaxai/minimax-m3` | ❌ | Timeout |
| `nvidia/z-ai/glm-5.2` | ❌ | Timeout |

These are environment-specific and will change — re-run the test periodically.
