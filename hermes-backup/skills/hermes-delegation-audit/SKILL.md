---
name: hermes-delegation-audit
description: >-
  Audit and verify Hermes Agent's delegation (subagent) configuration, including
  model routing, fallback chains, provider mapping, credential pools, and
  approval mode. Run this when the user asks "do subagents use the right model",
  "verify delegation config", or when subagent tasks fail silently.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, delegation, subagent, model, audit, configuration, verify]
    related_skills: [hermes-agent, agent-reach]
platforms: [linux, macos]
required_commands: [python3]
---

# Hermes Delegation Audit

Audit the full delegation (subagent) configuration of a running Hermes instance.
Use this when the user asks about subagent models, subagent failures, or verifying
that delegation settings are correct.

## Trigger Conditions

Load this skill when the user says:
- "Subagents work?" / "Subagent in which model?"
- "Check subagent model config"
- "Verify subagent route" / "Verify delegate_task provider"
- "Subagent fails/times out"
- "Subagent shows wrong model"

## Audit Workflow

### Step 1 — Read delegation config from config.yaml

```bash
python3 -c "
import yaml
d = yaml.safe_load(open(open('/home/hermeswebui/.hermes/config.yaml').name))
del_cfg = d.get('delegation', {})
print('=== MAIN MODEL ===')
main = d.get('model', {})
if isinstance(main, dict):
    print(f'  Model: {main.get(\"default\")}')
    print(f'  Provider: {main.get(\"provider\")}')
else:
    print(f'  Model: {main}')

print()
print('=== DELEGATION (parent) ===')
print(f'  Model: {del_cfg.get(\"model\")}')
print(f'  Provider: {del_cfg.get(\"provider\")}')
print(f'  Max concurrent: {del_cfg.get(\"max_concurrent_children\")}')
print(f'  Max spawn depth: {del_cfg.get(\"max_spawn_depth\")}')

sub = del_cfg.get('subagent', {})
print()
print('=== SUBAGENT MODEL ===')
print(f'  Model: {sub.get(\"model\")}')
print(f'  API URL: {sub.get(\"base_url\")}')
print(f'  Fallback chain:')
for fb in sub.get('fallback_models', []):
    print(f'    - {fb.get(\"model\")} (provider: {fb.get(\"provider\")})')
"
```

**Key insight:** The main model and subagent model can differ. The main session runs on
`model.default`, but subagents spawned via `delegate_task` use `delegation.subagent.model`.
The parent's own delegation (when the main agent calls delegate_task) uses `delegation.model`,
but children spawned by *that* subagent use `delegation.subagent.model`.

### Step 2 — Check approvals mode

Subagent tasks typically use terminal tools (`rdt`, `twitter`, `gh`, etc.) which
get blocked by approval prompts. Verify:

```bash
grep -A2 \"approvals:\" ~/.hermes/config.yaml
```

If `mode: manual` is set, subagent terminal commands will hang in `pending_approval`
with no user to approve, causing 504 timeouts. **Fix:** set `mode: off`.

### Step 3 — Test via delegate_task (subagent self-reports its model)

The dispatch metadata shown after `delegate_task()` displays the **parent model** (e.g.
`Model: opencode200k`), NOT the model the subagent actually runs on. This is a common
source of confusion — the user sees the parent model and thinks the subagent used it.

To prove the real subagent model, dispatch a subagent that reads its own config and
reports back:

```
delegate_task(
    goal="Tell me exactly which model you are running on. Check your system prompt, environment, config, or anything that reveals your model name and provider. Report the full model name and provider.",
    context="This is a test to see what model subagents use. Self-report accurately."
)
```

The subagent can read `~/.hermes/config.yaml` and report the `delegation.subagent.model`
it actually uses. Typical result: the parent shows `Model: opencode200k` in dispatch
metadata, but the subagent reports `kimchi/deepseek-v4-flash` (or whatever
`delegation.subagent.model` is set to).

### Step 4 — Report the model routing chain

Explain to the user in Persian or English:

| Layer | Model | Purpose |
|-------|-------|--------|
| Main session | `opencode200k` | The user's own chat agent |
| Delegation (parent) | `delegation.model` | Model the main agent uses when calling delegate_task |
| Subagent | `delegation.subagent.model` | Model the spawned child uses (and its own children via max_spawn_depth) |
| Fallback 1 | `delegation.subagent.fallback_models[0]` | If primary fails |
| Fallback 2 | `delegation.subagent.fallback_models[1]` | Next fallback |
| Fallback 3 | `delegation.subagent.fallback_models[2]` | Last resort |

## Common Issues

### Dispatch metadata shows parent model, not subagent model

**This is the #1 confusion.** When you dispatch `delegate_task()`, the
response says e.g. `Model: opencode200k` — but that is the **parent session's**
model, not the subagent's. The subagent actually runs on `delegation.subagent.model`.
The only way to see the real subagent model is to make the subagent self-report
(see Step 3 above).

### Custom provider naming: the \"9router\" mystery

The custom provider's display name is derived from the `base_url` hostname:
```
base_url: https://9router-8uoc.srv1699470.hstgr.cloud/v1
```
The `name:` field in `custom_providers` (or auto-derived from hostname) becomes
the provider identifier. So `custom:9router-8uoc.srv1699470.hstgr.cloud` is
just the hostname of the endpoint, not a specific model or router technology.

When debugging, check:
```yaml
custom_providers:
  - name: <display-name>    # derived from hostname or set explicitly
  - base_url: <proxy-url>   # the actual routing endpoint
```

### Subagent shows the wrong model
- Check `delegation.subagent.model` directly — it is separate from `model.default`
- The parent delegation model (`delegation.model`) is the main agent's model when delegating;
  the child model is `delegation.subagent.model`
- If the user says "use the parent model" or "use my model", update `delegation.model`, NOT `delegation.subagent.model`
- **To change the delegation model:**
  ```bash
  /app/venv/bin/hermes config set delegation.model "opencode200k"
  ```
  Verify: `cat ~/.hermes/config.yaml | grep -A2 "delegation:"`
- If fallback fires, the subagent logs should show the fallback model name
- **Known limitation**: `delegate_task()` does NOT accept a model parameter. The engine cannot assign different models to different subagents at dispatch time. The model is platform-controlled via config.yaml.

### Subagent times out (504)
- **Most likely cause:** approval prompts blocking terminal commands
- Check `approvals.mode` — must be `off` for background subagent terminal use
- Alternative: use web_search/Jina/curl fallbacks instead of rdt/twitter CLIs in subagents

### Subagent returns no useful data
- Verify the subagent's goal is narrow (one job per subagent)
- Pass explicit deliverable format: "return 3-10 bullet points with source URLs"
- Set the subagent's `role: leaf` for simple tasks, `role: orchestrator` for
  tasks that need to spawn their own workers

### Background subagent lost when parent exits
- This is expected for `delegate_task` — children are process-local, not durable
- For work that must survive parent exit, use `cronjob` or
  `terminal(background=True, notify_on_complete=True)`

### Parallel delegation causes rate limits and tool conflicts
- **NEVER dispatch multiple subagents working on the same project simultaneously.**
  Parallel agents hit the same API endpoints, port numbers, and file locks — causing
  rate limits, browse state conflicts, and silent failures.
- **Always run sequential:** dispatch one agent, wait for completion, then dispatch the next.
- User correction (Farsi): "از این به بعد همزمان ایجنت هارو نفرستی دونه دونه بفرست
  مطابق قوانین خودش وگرنه ریت لیمیت میخوریم"
- **Exception:** agents working on completely isolated projects (different repos, different ports)
  can run in parallel safely.

## References

- Hermes config: `~/.hermes/config.yaml` → `delegation.*` section
- Fallback model docs: https://hermes-agent.nousresearch.com/docs
- Agent-Reach subagent approval pitfall: see agent-reach skill