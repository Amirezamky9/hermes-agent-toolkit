# Auxiliary Compression with Custom Providers

Diagnosing and fixing `auxiliary.compression` failures when using a custom OpenAI-compatible provider.

## The "Context → Timeout → Fallback → 401" Chain

### Symptoms
- Repeated `Auxiliary compression: timeout on the critical path` every ~120s
- Fallback to main agent model → `401 Model not supported`
- No context compression ever succeeds → session grows beyond 200K tokens → upstream `400: Upstream request failed`
- `agent.context_compressor: Failed to generate context summary` repeating every 60s

### Full error chain (from logs)
```
[auxiliary] using custom:9router (context) at https://...
  ↓ 120s later
[auxiliary] timeout on the critical path
  ↓
[auxiliary] falling back to main model (opencode200k)
  ↓
[context_compressor] 401: Model opencode200k is not supported
  ↓
[context_compressor] Further summary attempts paused for 60 seconds
  ↓
(context grows, repeats every turn until 200K+)
  ↓
[conversation_loop] 400: Error from provider: Upstream request failed
```

### Root cause
The auxiliary compression model is **not validated independently** from the main chat model. A model that works for chat may:

1. **Not exist** on the custom provider (401, 404)
2. **Timeout** because the auxiliary endpoint has a shorter timeout than chat (default ~120s vs 600s+)
3. **Not support the summarization system prompt** (extra preamble Hermes adds for compression)
4. **Be a group/alias** (`context`) that routes to different underlying models each call — some fast, some slow

### Validation checklist

```bash
# 1. Check current config
grep -A5 'auxiliary' ~/.hermes/config.yaml

# 2. Check what the fallback chain does
grep 'auxiliary.*compression\|connection error on\|falling back to' ~/.hermes/logs/agent.log | tail -20

# 3. Check if timeout is consistent (should be ~120s gap)
python3 -c "
import re
with open('/home/hermeswebui/.hermes/logs/agent.log') as f:
    lines = [l for l in f if 'Auxiliary compression: using' in l or 'timeout on the critical path' in l]
for line in lines[-10:]:
    print(line.strip()[:60])
"

# 4. Confirm the model exists on the provider via the provider's models endpoint
# For 9router/OpenRouter-compatible:
curl -s https://9router-8uoc.srv1699470.hstgr.cloud/v1/models \
  -H 'Authorization: Bearer sk-...' \
  | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin).get('data',[])]"
```

### Known working models for compression on 9router

If using `9router-8uoc.srv1699470.hstgr.cloud` as the provider:

| Model | Works for compression? | Notes |
|-------|----------------------|-------|
| `context` | ⚠️ Intermittent timeout | Group alias — routes to pool; some members timeout |
| `opencode200k` | ❌ 401 | Chat model, not allowed for auxiliary tasks |
| `kimchi/kimi-k2.7` | ✅ Probable | Fast, stable on other tests |
| `kimchi/deepseek-v4-flash` | ✅ Likely | Fast chat model |
| `groq/llama-3.3-70b-versatile` | ✅ Likely | Stable, lower cost |

### The fix (two options)

**Option A — Explicit fast model (recommended):**
```yaml
auxiliary:
  compression:
    provider: custom:9router-8uoc.srv1699470.hstgr.cloud
    model: kimchi/kimi-k2.7        # ← specific fast model, not alias
    base_url: https://9router-8uoc.srv1699470.hstgr.cloud/v1
```

**Option B — Fallback to a different provider env:**
```yaml
auxiliary:
  compression:
    provider: auto
    # inherits main provider; if main model is opencode200k, set
    # OPENROUTER_API_KEY or GOOGLE_API_KEY so auto picks a supportable model
```

### Key principle
> What works for **chat** may NOT work for **compression**.
> The auxiliary model must be independently verified — it uses a different system prompt and has a tighter timeout budget (~120s vs 600s+).
