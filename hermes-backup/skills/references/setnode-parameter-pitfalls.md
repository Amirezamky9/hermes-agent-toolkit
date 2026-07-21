# setNodeParameter vs updateNodeParameters — The Silent No-Op Trap

## The Trap

`setNodeParameter` with `path: "/parameters"` looks like it should replace the whole parameters object, but **it may silently not apply** if the existing parameters have nested keys that don't match the path resolution.

From this session (WF04 — Deck 4):
```
❌ { "type": "setNodeParameter", "nodeName": "🆕 Check/Register User",
     "path": "/parameters", "value": { "operation": "executeQuery", ... } }
   → NO-OP. Node stayed on old "upsert" config with orders table.
```

The fix was `updateNodeParameters` with `replace: true`:
```
✅ { "type": "updateNodeParameters", "nodeName": "🆕 Check/Register User",
     "parameters": { "operation": "executeQuery", "query": "INSERT INTO ...", ... },
     "replace": true }
```

## Decision Tree

```
Node exists with parameters already set?
├── YES → use updateNodeParameters with replace: true
│         (include ALL params including resource/operation/mode)
└── NO  (node was just added, params are defaults)
        → use setNodeParameter with path for individual fields
```

## When to use which

| Op type | When | What it does | Risk |
|---------|------|-------------|------|
| `setNodeParameter` + `path` | Change ONE field | Precise JSON-pointer write | Silent no-op if path doesn't resolve |
| `updateNodeParameters` + `replace: false` (default) | Merge into existing params | Deep merge | Doesn't remove old keys |
| `updateNodeParameters` + `replace: true` | Full overwrite | Wipes ALL existing params, sets new ones | NUKES resource/operation if not included |

## The "replace: true" NUKE hazard

When you use `replace: true`, every parameter the node needs must be in the payload:

```json
// For Postgres executeQuery:
{
  "operation": "executeQuery",
  "query": "SELECT ...",
  "options": { "queryReplacement": "..." }
  // NO resource key needed (Postgres doesn't use it)
}

// For Telegram sendMessage:
{
  "resource": "message",     // ← MUST include
  "operation": "sendMessage", // ← MUST include
  "chatId": "...",
  "text": "...",
  ...
}
```

## Verification

After applying, check via `get_workflow_details` → find the node and inspect `parameters`:

```python
import json
with open('/tmp/hermes-results/call_xxx.txt') as f:
    data = json.loads(f.read())
wf = json.loads(data['result'])
for n in wf['workflow']['nodes']:
    if n['name'] == 'Your Node':
        print(json.dumps(n['parameters'], indent=2))
```

If parameters still show the OLD values → `setNodeParameter` silently no-opped. Retry with `updateNodeParameters` + `replace: true`.
