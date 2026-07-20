# Delegation Configuration for Research Sub-agents

## Hermes Config (config.yaml)

### ⚠️ CRITICAL: `delegation.subagent.model` IS IGNORED

Hermes reads `delegation.model`, NOT `delegation.subagent.model`. The `subagent`
sub-key is documentation-only. Set subagent models at `delegation.model`.

```yaml
# Top-level: YOUR main session model
model:
  default: <main-model>
  provider: custom:<provider>

delegation:
  provider: "custom"
  base_url: "<your-api-base-url>"
  api_key: sk-...
  model: "<fast-cheap-model-for-subagents>"   # ← THIS controls subagent model
  max_concurrent_children: 4
  max_spawn_depth: 2
  orchestrator_enabled: true
  # subagent: {}              ← entirely optional; runtime never reads it
```

**Key insight:** `delegation.model` = subagent model. `model.default` = main agent model.
They are independent keys. You can set them to DIFFERENT models.

## ⚠️ Prerequisite — Approval mode for subagents

Subagents run in background with no user present. If `approvals.mode` is
`manual` (the default), **any terminal command flagged as dangerous will block
forever** waiting for approval that never comes — causing 504 timeouts.

**Required config** (add to `~/.hermes/config.yaml`):
```yaml
approvals:
  destructive_slash_confirm: false
  mode: off
```

This bypasses approval prompts for terminal commands in all sessions.
Hardline blocks (`rm -rf /`, `mkfs`, etc.) still apply unconditionally.
Config takes effect immediately (mtime-keyed cache, no restart needed).

## Model Selection Strategy

| Role | Criteria | Current Config |
|------|----------|---------------|
| **Orchestrator** (research-manager) | Good reasoning, moderate cost | `opencode200k` (primary), `groq/openai/gpt-oss-120b` (fallback) |
| **Sub-agents** (deep-research workers) | Fast, cheap, good at extraction | `kimchi/deepseek-v4-flash` (primary), `kimchi/kimi-k2.7` (fallback) |
| **Main session** | Best available, highest quality | `opencode200k` |

**Principle:** Orchestrator needs reasoning (planning waves, resolving conflicts).
Sub-agents need speed and extraction accuracy (read page, extract facts, return bullets).

**Models to avoid (tested broken on 9router):**
- `nvidia/deepseek-ai/deepseek-v4-flash` — 503 rate limits, verbose reasoning
- `nvidia/deepseek-ai/deepseek-v4-pro` — timeout (>30s)
- `nvidia/nemotron-3-ultra-550b-a55b` — 404 dead endpoint
- `nvidia/minimaxai/minimax-m3` — timeout
- `nvidia/z-ai/glm-5.2` — timeout
- `groq/qwen/qwen3-32b` — leaks `<think>` tags in content

## Discovering Available Models

```bash
# From custom provider
curl -s "<base_url>/v1/models" -H "Authorization: Bearer $API_KEY" | python3 -c "
import sys, json
for m in json.load(sys.stdin).get('data', []):
    print(m['id'])
"
```

## Concurrency Limits

| Workload | Max concurrent children | Notes |
|----------|------------------------|-------|
| Small (3 tasks) | 2 | Avoid overhead |
| Medium (4-6 tasks) | 3 | Default safe |
| Large (7-12 tasks) | 4 | Max recommended |
| XLarge (13+ tasks) | 4 per wave | Use wave scheduling |

## Spawn Depth

- `max_spawn_depth: 1` — sub-agents cannot spawn their own (default, safest)
- `max_spawn_depth: 2` — orchestrator sub-agents can spawn workers (needed for deep-research)

## Verification

After config change, test with a simple delegation:
```
Delegate: "Echo back: delegation works"
```
If the sub-agent responds, config is correct.
