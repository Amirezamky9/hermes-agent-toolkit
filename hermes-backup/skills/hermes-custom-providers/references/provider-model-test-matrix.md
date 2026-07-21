# Provider Model Test Matrix

Test methodology: Direct OpenAI chat completion calls against each model, checking `choices[0].message.content` for non-empty, non-leaked content. Reasoning models (thinking) needed `max_tokens >= 200` to produce visible output.

## 9router (`https://9router-8uoc.srv1699470.hstgr.cloud/v1`)

Tested 2026-07-08. All tests used the same API key with `Authorization: Bearer sk-...`.

### Working models (✅)

| Model ID | Performance | Best for | Notes |
|----------|-----------|----------|-------|
| `opencode200k` | ✅ Excellent | Orchestrator (primary) | Reasoning model. Needs `max_tokens >= 200` for visible output. Returns thinking tokens which are suppressed in `content`. |
| `groq/openai/gpt-oss-120b` | ✅ Fast | Orchestrator (fallback) | Fast, clean responses, no conjobs leakage. |
| `groq/llama-3.3-70b-versatile` | ✅ Fast | Subagent fallback | Reliable, no leakage. |
| `kimchi/deepseek-v4-flash` | ✅ Fast | Subagent (primary) | 1M context window. Fastest reliable subagent model. |
| `kimchi/kimi-k2.7` | ✅ Good | Subagent (fallback) | Vision+reasoning, 262K ctx. Slightly slower than flash. |

### Leaky models (⚠️)

These models return **other users' conversation content** in their responses — they were never intended for multi-tenant use. Do NOT use for any Hermes agent.

| Model | Problem |
|-------|---------|
| `groq/qwen/qwen3-32b` | Returns conjunctions/metadata of other conversations |
| `groq/meta-llama/llama-4-maverick-17b-128e-instruct` | Returns other users' response fragments |
| `nvidia/minimaxai/minimax-m3` | Returns other users' conversation headers |
| `nvidia/moonshotai/kimi-k2.6` | Returns empty content or other users' data |
| `nvidia/z-ai/glm-5.2` | Leaks other users' conversations directly |
| `nvidia/nemotron-3-ultra-550b-a55b` | Returns 404 error |
| `nvidia/deepseek-ai/deepseek-v4-flash` | Returns 503 Service Unavailable (rate limited) |
| `nvidia/deepseek-ai/deepseek-v4-pro` | Timeout / non-responsive |
| `nvidia/parakeet-ctc-1.1b-asr` | Not a chat model (ASR/speech model) |
| `context` | Alias, not a real model |
| `kimchi` | Alias |
| `nvidi` | Alias |
| `mimo` | Alias |

### Proxy-only models (🔒)

| Model | Status |
|-------|--------|
| `openrouter/tencent/hy3:free` | Works for chat but uses OpenRouter path — included in model list but physically hosted by OpenRouter, not 9router. |

## Recommended delegation config

```yaml
delegation:
  provider: custom                    # bare, NOT custom:<hostname>
  base_url: https://<endpoint>/v1     # ← critical: makes path 1 fire
  api_key: <your-key>                 # optional if parent's key is inherited
  model: opencode200k                 # orchestrator primary
  fallback_models:
    - model: groq/openai/gpt-oss-120b
      base_url: https://<endpoint>/v1
    - model: groq/llama-3.3-70b-versatile
      base_url: https://<endpoint>/v1
  subagent:
    base_url: https://<endpoint>/v1
    api_key: <your-key>
    model: kimchi/deepseek-v4-flash
    fallback_models:
      - model: kimchi/kimi-k2.7
        base_url: https://<endpoint>/v1
      - model: groq/llama-3.3-70b-versatile
        base_url: https://<endpoint>/v1
```

## Verification script

```python
import os, json, requests

def test_model(base_url, api_key, model, max_tokens=100):
    """Test a model returns a valid chat response."""
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": "Say hello"}],
              "max_tokens": max_tokens, "stream": False},
        timeout=30
    )
    if resp.status_code != 200:
        return {"status": "error", "code": resp.status_code}
    try:
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"status": "ok", "content_preview": content[:80] if content else "(empty)"}
    except Exception as e:
        return {"status": "parse_error", "error": str(e), "raw": resp.text[:200]}

def benchmark_model(base_url, api_key, model):
    """Test model performance with a simple extract task."""
    import time
    resp = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Extract: 'The price is $42.99 for 3 items.' Return JSON. No other text."}],
            "max_tokens": 50, "stream": False
        },
        timeout=30
    )
    start = time.time()
    data = resp.json()
    elapsed = time.time() - start
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"model": model, "elapsed": round(elapsed, 2), "result": content[:100]}
```