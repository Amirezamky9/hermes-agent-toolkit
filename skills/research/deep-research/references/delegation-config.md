# Multi-Provider Delegation Config Pattern

## Overview

Configure Hermes delegation with primary + fallback models across different providers
for maximum resilience. If one provider goes down, the next one picks up automatically.

## Config Location

`~/.hermes/config.yaml` — append at end:

### ⚠️ CRITICAL: `delegation.subagent.model` IS IGNORED

Hermes' `_resolve_delegation_credentials()` reads `delegation.model`, NOT `delegation.subagent.model`.
The `subagent` sub-key is documentation-only. **Set models at `delegation.model`, never under `delegation.subagent.model`.**

> **⚠️ Runtime behavior caveat (2026-07):** While `delegation.subagent.model` is ignored,
> `delegation.subagent.provider` and `delegation.subagent.fallback_models` DO appear to be
> read by the runtime. If subagents use wrong models despite `delegation.model` being correct,
> check the `subagent:` section for stale `fallback_models` or missing `provider`. The safest
> fix is: set both `delegation.model` + `delegation.provider` AND `delegation.subagent.model`
> + `delegation.subagent.provider` to the same values, and keep fallback_models identical
> in both sections. When using `hermes config set` for array fields (like fallback_models),
> the value gets serialized as a string — fix manually with Python YAML round-trip.

```yaml
delegation:
  provider: "custom:<provider-name>"
  model: "<subagent-primary>"               # ← THIS is the effective subagent model
  fallback_models:
    - provider: "custom:<provider-name>"
      model: "<subagent-fallback-1>"
    - provider: "custom:<provider-name>"
      model: "<subagent-fallback-2>"
  max_concurrent_children: 4
  max_spawn_depth: 2
  orchestrator_enabled: true
  # delegation.subagent — exists only for documentation / fallback chain reference;
  # the runtime reads delegation.model, delegation.fallback_models, and delegation.base_url.
  subagent:
    provider: "custom:<provider-name>"
    model: "<subagent-primary>"
    fallback_models:
      - provider: "custom:<provider-name>"
        model: "<subagent-fallback-1>"
      - provider: "custom:<provider-name>"
        model: "<subagent-fallback-2>"
```

**To have subagents use a different model than the main session:** set `delegation.model` (subagent model)
and leave the top-level `model.default` (main agent model) unchanged. See "Tested Pattern" below.

## Tested Pattern (9router)

### ✅ Correct config (subagents use different model than main agent)

```yaml
# Top level: main session model
model:
  default: opencode200k                    # ← main agent (you)
  provider: custom:9router-8uoc.srv1699470.hstgr.cloud

delegation:
  provider: custom
  base_url: https://9router-8uoc.srv1699470.hstgr.cloud/v1
  api_key: sk-...                          # ← same key
  model: kimchi/deepseek-v4-flash          # ← THIS controls subagent model!
  fallback_models:
    - model: kimchi/kimi-k2.7
      provider: custom
    - model: groq/llama-3.3-70b-versatile
      provider: custom
  max_concurrent_children: 4
  max_spawn_depth: 2
  orchestrator_enabled: true
  subagent:                                 # ← documentation-only, ignored by runtime
    model: kimchi/deepseek-v4-flash
    fallback_models:
      - model: kimchi/kimi-k2.7
        provider: custom
      - model: groq/llama-3.3-70b-versatile
        provider: custom
```

**Key insight:** `delegation.model: kimchi/deepseek-v4-flash` = subagent model.
`model.default: opencode200k` = your (main session) model. They are INDEPENDENT.

### ❌ Broken config (what NOT to do)

```yaml
delegation:
  model: opencode200k                      # ← WRONG: this was infecting subagents with main model
  subagent:
    model: kimchi/deepseek-v4-flash        # ← WRONG: this key is silently ignored
```

Setting `delegation.model: opencode200k` forces subagents to use the same (expensive) model
as the main session. Setting `delegation.subagent.model` does nothing at all — the runtime
never reads that path.

### Why these models?

| Model | Role | Why |
|-------|------|-----|
| `opencode200k` | Orchestrator primary | Best reasoning, handles planning/coordination |
| `groq/openai/gpt-oss-120b` | Orchestrator fallback | Fast, reliable, good reasoning |
| `groq/llama-3.3-70b-versatile` | Universal fallback | Fast, clean output, no thinking tags |
| `kimchi/deepseek-v4-flash` | Subagent primary | Fast extraction, clean output, no reasoning overhead |
| `kimchi/kimi-k2.7` | Subagent fallback | Fast, clean, reliable |

### Models to AVOID (tested broken)

| Model | Issue |
|-------|-------|
| `nvidia/deepseek-ai/deepseek-v4-flash` | 503 rate limits, verbose reasoning output |
| `nvidia/deepseek-ai/deepseek-v4-pro` | Timeout (>30s) |
| `nvidia/nemotron-3-ultra-550b-a55b` | 404 (dead endpoint) |
| `nvidia/minimaxai/minimax-m3` | Timeout |
| `nvidia/z-ai/glm-5.2` | Timeout |
| `groq/qwen/qwen3-32b` | Leaks `<think>` tags in content |
| `groq/meta-llama/llama-4-maverick-17b-128e-instruct` | 404 |
| `openrouter/tencent/hy3:free` | 429 rate limit |

## Key Principles

1. **Orchestrator**: Use the smartest available model (decision-making quality matters)
2. **Sub-agents**: Use fast + cheap models (they do narrow extraction, not reasoning)
3. **Fallback diversity**: Spread across different provider backends (NVIDIA, Kimchi, Groq)
4. **Same model, different provider**: If a model exists on multiple providers, use different providers for primary vs fallback
5. **max_concurrent_children: 4**: Matches deep-research's wave-based scheduling
6. **max_spawn_depth: 2**: Allows orchestrator → subagent nesting, but not deeper

## Verification

After updating config, restart the Hermes session for changes to take effect.
Test with: `delegate_task` call using a simple goal.

## Pitfalls

### `hermes config set` serializes arrays as strings

When using `hermes config set` for array fields like `fallback_models`, the value gets
serialized as a YAML string instead of a proper list:

```bash
# This BREAKS the config:
hermes config set delegation.subagent.fallback_models '["{...}","{...}"]'
# Result in config.yaml:
#   fallback_models: '[\"{...}\",\"{...}\"]'   ← STRING, not a list!
```

**Fix:** After setting, manually fix with Python YAML round-trip:
```bash
cat ~/.hermes/config.yaml | python3 -c "
import sys, yaml
config = yaml.safe_load(sys.stdin)
config['delegation']['subagent']['fallback_models'] = [
    {'model': 'groq/openai/gpt-oss-120b', 'provider': 'custom'},
    {'model': 'groq/llama-3.3-70b-versatile', 'provider': 'custom'}
]
print(yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False))
" > /tmp/config_fixed.yaml && cp /tmp/config_fixed.yaml ~/.hermes/config.yaml
```

**Rule:** For simple string/number/boolean values, use `hermes config set`. For arrays
and complex nested structures, edit the YAML file directly or use the Python round-trip.
