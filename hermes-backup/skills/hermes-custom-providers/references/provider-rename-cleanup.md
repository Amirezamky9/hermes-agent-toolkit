# Provider Rename Cleanup

When you rename a custom provider's `name` field in `config.yaml`, the slug changes (e.g., `custom:9ruter` → `custom:9router-8uoc.srv1699470.hstgr.cloud`). Multiple files retain stale references to the old slug that must be cleaned up.

## Files to update

| File | What to do |
|------|-----------|
| `~/.hermes/config.yaml` | Update `name`, `model.provider`, `delegation.provider`, `delegation.subagent.provider`, `delegation.fallback_models[*].provider`, `delegation.subagent.fallback_models[*].provider`, **`delegation.base_url`**, **`delegation.api_key`**, **`delegation.subagent.base_url`**, **`delegation.subagent.api_key`** |
| `~/.hermes/auth.json` | Remove old slug from `credential_pool` dict |
| `~/.hermes/provider_models_cache.json` | Remove old slug entry, add new slug entry with model list |
| Running session | **Must `/reset` or restart** — session caches the provider slug at startup |

## Step-by-step

### 1. Update config.yaml

```bash
# Replace all occurrences of old slug with new slug in provider fields
sed -i 's/custom:old-name/custom:new-name/g' ~/.hermes/config.yaml

# If base_url also changed, update delegation base_url fields
sed -i 's|old-endpoint.example.com/v1|new-endpoint.example.com/v1|g' ~/.hermes/config.yaml
```

Or use `hermes config set` for individual fields:
```bash
hermes config set model.provider custom:new-name
hermes config set delegation.provider custom:new-name
hermes config set delegation.base_url https://new-endpoint.example.com/v1
hermes config set delegation.subagent.provider custom:new-name
hermes config set delegation.subagent.base_url https://new-endpoint.example.com/v1
```

### 2. Clean up auth.json

```python
import json
with open('/home/$USER/.hermes/auth.json') as f:
    auth = json.load(f)
pool = auth.get('credential_pool', {})
old_key = 'custom:old-name'
if old_key in pool:
    del pool[old_key]
    print(f"Removed stale '{old_key}'")
with open('/home/$USER/.hermes/auth.json', 'w') as f:
    json.dump(auth, f, indent=2)
```

### 3. Update provider_models_cache.json

```python
import json, time
with open('/home/$USER/.hermes/provider_models_cache.json') as f:
    cache = json.load(f)
# Remove old entry
cache.pop('custom:old-name', None)
# Add new entry (fetch models from API first)
cache['custom:new-name'] = {
    "models": ["model1", "model2", ...],
    "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
with open('/home/$USER/.hermes/provider_models_cache.json', 'w') as f:
    json.dump(cache, f, indent=2)
```

### 4. Reset session

The running Hermes session cached the old provider slug at startup. Config changes only take effect after:
- `/reset` in CLI/chat
- `hermes gateway restart` for gateway
- New process start

## Why this matters

If you only update `config.yaml` but forget auth.json and the cache:
- `delegate_task` fails with "Cannot resolve delegation provider 'custom:old-name'" because the session's credential pool still has the old slug
- Model discovery may show stale results
- The gateway may fail to authenticate requests using the old slug's (now-empty) credential pool
