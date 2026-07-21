# MCP Editing Pitfalls — update_workflow Gotchas

> Pitfalls discovered when editing existing n8n workflows via MCP `update_workflow`.
> Covers `updateNodeParameters`, `setNodeParameter`, `addNode`, `addConnection`, Set v3.4 modes, Switch routing, and batch operation limits.

---

## 1. Set Node v3.4 — assignments Must Be an Object

**The #1 trap.** When editing Set (Edit Fields) node v3.4 parameters via MCP:

```jsonc
// ✅ CORRECT — assignments is an object with an `assignments` array property
{
  "assignments": {
    "assignments": [
      {"id": "field1", "name": "field1", "type": "string", "value": "={{ $json.x }}"}
    ]
  },
  "mode": "manual"
}

// ❌ WRONG — bare array (causes validation warning + eventual node corruption)
{
  "assignments": [
    {"id": "field1", "name": "field1", "type": "string", "value": "={{ $json.x }}"}
  ],
  "mode": "manual"
}
```

**Consequence of wrong format:** First call appears to succeed (`appliedOperations: 1`) but the node enters a corrupt state. Subsequent `updateNodeParameters` calls fail with `"node '...' not found"` even though the node exists in the workflow JSON. The only recovery is `addNode` to recreate.

---

## 2. Node Corruption Recovery — addNode + addConnection

When a node becomes unfindable after a bad edit:

1. **Remove stale connections** (if any reference the corrupt node) — or just `addNode` which creates a fresh node
2. **addNode** with correct parameters
3. **addConnection** to wire input → new node → output

```jsonc
// All in one update_workflow call — works atomically
{
  "operations": [
    {
      "type": "addNode",
      "node": {
        "name": "My Node",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [1120, 0],
        "parameters": {
          "assignments": {"assignments": [...]},
          "mode": "manual"
        }
      }
    },
    {"type": "addConnection", "source": "Previous Node", "target": "My Node"},
    {"type": "addConnection", "source": "My Node", "target": "Next Node"}
  ]
}
```

**Key:** Operations in the array must all be objects (not mixed types). The `node` property inside `addNode` must include `name`, `type`, `typeVersion`, `position`, and `parameters`.

---

## 3. setNodeParameter as Fallback

When `updateNodeParameters` can't find a node but `setNodeParameter` can (different internal lookup):

```jsonc
// Set a single parameter by JSON pointer path
{
  "operations": [{
    "type": "setNodeParameter",
    "nodeName": "✅ Extract Order ID",
    "path": "/parameters/mode",
    "value": "manual"
  }]
}
```

**Limitation:** `setNodeParameter` only sets one parameter at a time. For multiple params (mode + includeOtherFields + assignments), you need multiple calls OR use `updateNodeParameters` with all params at once.

**When it helps:** After a node has been partially corrupted or renamed, `setNodeParameter` sometimes succeeds where `updateNodeParameters` fails with "not found".

---

## 4. Version Management — Publish Creates New Version

- `publish_workflow` creates a new active version from the current draft
- `versionId` and `activeVersionId` converge after publish
- Changes made between publish calls create new draft versions
- After publish, `get_workflow_details` returns the published version (versionId == activeVersionId)
- **Always verify after publish** — read back the nodes to confirm changes stuck

---

## 5. updateNodeParameters — Full Parameter Replacement

When using `updateNodeParameters`, the `parameters` object **replaces** the node's existing parameters entirely (not merge). Include ALL parameters you want to keep:

```jsonc
// This KEEPS assignments but REPLACES mode — include assignments to preserve it
{
  "type": "updateNodeParameters",
  "nodeName": "📊 Dashboard Builder",
  "parameters": {
    "assignments": {"assignments": [...]},  // must include or it's lost
    "mode": "manual"
  }
}
```

If you only pass `{"mode": "manual"}` without assignments, the assignments may be cleared.

---

## 6. Emoji Node Names — Unicode Normalization

Emoji-prefixed node names (📊, ✅, ❌, 🚚, 📢) sometimes cause lookup failures after corruption. The node exists in the JSON but the tool can't match the name. Recovery: recreate with `addNode`.

---

## 7. Set v3.4 — `mode: "raw"` Requires `jsonOutput`, Not `assignments`

**Silent failure trap.** Set node v3.4 has TWO modes with different parameter shapes:

```jsonc
// ✅ mode: "manual" → uses assignments
{
  "assignments": { "assignments": [{ "id": "f", "name": "f", "type": "string", "value": "={{ $json.x }}" }] },
  "mode": "manual"
}

// ✅ mode: "raw" → uses jsonOutput (single expression returning an object)
{
  "jsonOutput": "={{ { field: $json.x } }}",
  "mode": "raw"
}

// ❌ WRONG — mode: "raw" with assignments → silently outputs DEFAULT VALUES
{
  "assignments": { "assignments": [...] },
  "mode": "raw"  // ignores assignments entirely!
}
```

**Symptom:** Node appears to work but outputs `{"my_field_1": "value", "my_field_2": 1}` (Set node defaults) instead of your fields. No error — just wrong data.

**Fix:** Use `updateNodeParameters` to set `parameters` with the correct shape for the chosen mode:

```jsonc
// Fix for mode: "raw"
{
  "type": "updateNodeParameters",
  "nodeName": "My Set Node",
  "parameters": {
    "mode": "raw",
    "duplicateItem": false,
    "jsonOutput": "={{ { field: $json.data } }}",
    "includeOtherFields": false,
    "options": {}
  }
}
```

**When to use which:**
- `mode: "manual"` — adding/renaming specific fields, keeping others
- `mode: "raw"` — replacing entire output with a single expression (cleaner for simple extractions)

---

## 8. Large Operations Array — Serialization Failure

**MCP `update_workflow` fails silently when the operations array is too large.** The tool receives the operations as a string instead of an object:

```jsonc
// ❌ Fails with "Expected object, received string" at path operations[0]
{
  "operations": [
    {"type": "updateNodeParameters", "nodeName": "A", "parameters": {...}},
    {"type": "updateNodeParameters", "nodeName": "B", "parameters": {...}},
    // ... 10+ operations
  ]
}
```

**Workaround:** Send ONE `updateNodeParameters` operation per call:

```
// Call 1: Fix node A
update_workflow({ operations: [{ type: "updateNodeParameters", nodeName: "A", ... }] })

// Call 2: Fix node B
update_workflow({ operations: [{ type: "updateNodeParameters", nodeName: "B", ... }] })
```

**Alternative for bulk changes:** Use the n8n REST API directly (`/api/v1/workflows/{id}`) via curl with API key. The MCP server's auth token (`Bearer eyJ...`) is for the MCP proxy, not the REST API.

---

## 9. Switch v3.4 — `expression` vs `rules` Mode

**expression mode works correctly when the expression returns a valid integer.** The key is that the expression must evaluate to a NUMBER (0, 1, 2, ...) that maps to an output index:

```jsonc
// ✅ expression mode — WORKS when expression returns integer
{
  "mode": "expression",
  "numberOutputs": 17,
  "options": { "fallbackOutput": "extra" },
  "output": "={{ $json.routeIndex }}"
}
// Route Index = 0 → output 0, Route Index = 1 → output 1, etc.
```

```jsonc
// ❌ expression mode — FAILS when expression contains single quotes via MCP
{
  "output": "={{ $json.route==='admin_dashboard' ? 0 : 1 }}"
}
// MCP serialization error: "Expected object, received string"
// (see Pitfall #12)
```

```jsonc
// ❌ expression mode — FAILS when expression returns undefined
{
  "output": "={{ $json.callback_query.data }}"
}
// If callback_query is undefined → Switch crashes with "Cannot read properties of undefined (reading 'push')"
// (see 22-switch-crash-normalizer.md)
```

**rules mode works correctly but MCP can't store the rules structure:**

```jsonc
// rules mode — works in n8n UI but MCP stores rules.rules instead of rules.values
{
  "mode": "rules",
  "numberOutputs": 16,
  "rules": {
    "values": [...]  // MCP may convert to rules.rules → Switch ignores all rules
  }
}
```

**Key rules mode gotchas:**
- `rules.values` (NOT `rules.rules`) — wrong key causes all rules to be ignored
- Each rule needs `conditions.combinator: "and"` and `conditions.options` with `version: 2`
- Via MCP, rules.mode is unreliable — prefer expression mode with Code node pre-processing

**Definitive pattern — Code node + expression Switch:**
1. Code node computes `routeIndex` (integer) from string conditions
2. Switch in expression mode: `{{ $json.routeIndex }}`
3. This avoids: single-quote serialization, rules key mismatch, undefined crashes

**When to use which:**
- `expression` mode + Code node index: ✅ **RECOMMENDED** — works via MCP, no quote issues
- `expression` mode + inline ternary: ⚠️ only if expression has no quotes (numeric-only)
- `rules` mode: ⚠️ only if editing via n8n UI directly (MCP serializes rules incorrectly)

---

## 10. setNodeParameter — Path Restrictions

Some paths are rejected by `setNodeParameter`:

```jsonc
// ❌ "path 'parameters' is invalid or contains unsafe segments"
{ "type": "setNodeParameter", "path": "parameters.jsonOutput", ... }

// ❌ "path 'parameters' is invalid or contains unsafe segments"
{ "type": "setNodeParameter", "path": "parameters", ... }
```

**Workaround:** Use `updateNodeParameters` instead — it replaces the entire `parameters` object and doesn't have path restrictions.

---

## 11. addConnection Without sourceIndex — All Nodes on Output 0

**Critical Switch routing bug.** When using `addConnection` to wire a Switch node's outputs, omitting `sourceIndex` defaults to output 0:

```jsonc
// ❌ ALL connections go to Switch output 0 — wrong!
[
  {"type": "addConnection", "source": "🔀 Router", "target": "📊 Dashboard"},
  {"type": "addConnection", "source": "🔀 Router", "target": "📦 Products"},
  {"type": "addConnection", "source": "🔀 Router", "target": "👤 Users"},
]
// Result: Router main[0] → [Dashboard, Products, Users, ...]
// Dashboard, Products, Users ALL execute on every input!
```

**Fix:** Always use `sourceIndex` for multi-output nodes:

```jsonc
// ✅ Each node on its correct output
[
  {"type": "addConnection", "source": "🔀 Router", "sourceIndex": 0, "target": "📊 Dashboard"},
  {"type": "addConnection", "source": "🔀 Router", "sourceIndex": 1, "target": "📦 Products"},
  {"type": "addConnection", "source": "🔀 Router", "sourceIndex": 2, "target": "👤 Users"},
]
// Result: Router main[0] → Dashboard only
//         Router main[1] → Products only
//         Router main[2] → Users only
```

**Symptom:** When `/admin` (text message) is sent, the Switch routes to output 0 (Dashboard). But if Extract Order ID is also on output 0, it crashes with `"Cannot convert undefined or null to object"` because it tries to access `callback_query.data` which doesn't exist for text messages.

**Recovery:** Remove all wrong connections first, then re-add with correct `sourceIndex`:

```jsonc
// Step 1: Remove all wrong connections from Switch
[
  {"type": "removeConnection", "source": "🔀 Router", "target": "📦 Products"},
  {"type": "removeConnection", "source": "🔀 Router", "target": "👤 Users"},
  // ... remove ALL
]

// Step 2: Re-add with correct sourceIndex
[
  {"type": "addConnection", "source": "🔀 Router", "sourceIndex": 0, "target": "📊 Dashboard"},
  {"type": "addConnection", "source": "🔀 Router", "sourceIndex": 1, "target": "📦 Products"},
  // ...
]
```

---

## 12. Single Quotes in Expressions — Serialization Failure (Different from #8)

**Even ONE operation with single quotes in an expression value causes the MCP tool to serialize the entire `operations` array as a string.** This is separate from the "large operations" issue in #8 — even a single, short operation fails:

```jsonc
// ❌ Fails: "Expected object, received string" at path operations[0]
{
  "operations": [{
    "type": "updateNodeParameters",
    "nodeName": "🔀 Router",
    "parameters": { "output": "={{ $json.route==='admin_dashboard' ? 0 : 1 }}" }
  }]
}
// The single quotes in ==='admin_dashboard' break JSON serialization
```

**Why it happens:** The MCP tool's JSON serializer can't handle single quotes inside string values that are themselves inside a JSON string. The entire operations array gets stringified.

**Workaround — avoid single quotes entirely in MCP-sent expressions:**

```jsonc
// ✅ No quotes needed for numeric Switch expression
{ "parameters": { "output": "={{ $json.routeIndex }}" } }

// ✅ Use double quotes if string comparison needed (but may still fail)
{ "parameters": { "output": "={{ $json.route===\"admin_dashboard\" ? 0 : 1 }}" } }

// ✅ BEST: Use a Code node to compute the numeric index
// Code node: routeIndex computed from route string (no quote issues in JS)
// Switch: {{ $json.routeIndex }} (no quotes at all)
```

**Definitive pattern — Code node + numeric Switch:**
1. Code node computes `routeIndex` (integer) from `route` (string)
2. Switch in expression mode: `{{ $json.routeIndex }}` — zero quotes, zero serialization issues
3. This is the ONLY reliable routing pattern via MCP when you have string-based conditions

**Related:** Pitfall #8 (large arrays), Section 9 in `22-switch-crash-normalizer.md` (expression mode)

---

## 13. Set Node `$json` Context in Sub-Workflows

**In sub-workflows, `$json` in a Set node's `jsonOutput` refers to the INPUT from the previous node, NOT the original trigger data.** After passing through nodes that transform data (Postgres, Set, etc.), the original Telegram message/callback data is lost:

```javascript
// ❌ WRONG — $json only has {"value": "943724562"} from Get Admin Settings
"jsonOutput": "={{ { route: $json.message.text || '' } }}"
// Result: { route: "" } — no message field exists

// ✅ CORRECT — reference the original trigger node by name
"jsonOutput": "={{ (() => { const e = $('⚡ Admin Entry').first().json; return { route: e.callback_query ? e.callback_query.data : (e.message && e.message.text === '/admin' ? 'admin_dashboard' : e.message ? e.message.text : '') }; })() }}"
// Result: { route: "admin_dashboard" } — reads from original data
```

**Rule:** In sub-workflows with intermediate nodes (Gate, Auth, Settings), ALWAYS use `$('NodeName').first().json` to reference original data, never bare `$json`.

**Gotcha:** The expression `$('⚡ Admin Entry').first().json` contains single quotes → **will fail in MCP updateNodeParameters** (see #12). Use a Code node instead, where JS string syntax works normally:

```javascript
// Code node — safe, no MCP serialization issue
const e = $('⚡ Admin Entry').first().json;
const route = e.callback_query ? e.callback_query.data
  : (e.message && e.message.text === '/admin' ? 'admin_dashboard'
  : e.message ? e.message.text : '');
return [{ json: { ...$json, route } }];
```

---

## 14. Workflow Preference — Don't Chase Workarounds When MCP Tools Exist

When MCP `update_workflow` fails on a specific operation (e.g. Switch rules serialization), the correct response is **NOT** to:
- Try curl/REST API directly
- Try Docker exec  
- Try finding API keys in env files
- Build alternative pipelines

Instead, **find the MCP-compatible approach** within the same tool:
- Switch `rules` mode fails → switch to `expression` mode (same MCP tool)
- Long expression with quotes fails → use Code node + short expression (same MCP tool)
- `updateNodeParameters` fails → use `removeNode` + `addNode` (same MCP tool)

**Rule:** Exhaust MCP-native options before considering external access. Every n8n node type has multiple modes/versions — if one mode doesn't work via MCP, try another mode, not a different access path.

---

## 15. Credential Mismatch in Sub-Workflows

**Symptom:** Query fails with `relation "X" does not exist` even though the table exists and other Postgres nodes in the same workflow work fine.

**Root Cause:** Each Postgres node has its own credential assignment. When building a sub-workflow, nodes may get different credentials than the parent workflow. The `📦 Products List` might use credential `log_level` (correct DB) while `🔍 Fetch Order for Approve` uses credential `locall main db` (different DB without the table).

**Detection:**
```
get_execution → check each failed node's credential name/ID
compare with working nodes → different credential = wrong DB
```

**Fix:** Use `setNodeCredential` to assign the correct credential:
```jsonc
{
  "type": "setNodeCredential",
  "nodeName": "🔍 Fetch Order for Approve",
  "credentialName": "log_level"
}
```

**Rule:** When building a sub-workflow with multiple DB nodes, verify ALL Postgres nodes use the same credential. MCP `addNode` may auto-assign based on last-used credential, not the correct one.

---

## 16. setNodeParameter Can't Change Enum Values

**`setNodeParameter` silently fails to change discriminated enum fields** (e.g., `parameters/mode` on Switch or Set nodes). The value appears to be set in the draft but validation rejects it, and the test runs against the published version which still has the old enum:

```jsonc
// ❌ "index" → "expression" — setNodeParameter returns success but doesn't stick
{
  "type": "setNodeParameter",
  "nodeName": "🔀 Route Switch",
  "path": "/parameters/mode",
  "value": "expression"
}
// Validation warning: "Invalid value for 'parameters.mode': got 'index', expected 'expression'"
// But appliedOperations: 1 — looks like it worked!
// Test still runs the OLD published version → same error
```

**Symptom:** `setNodeParameter` reports success but the node still has the old mode when tested. The draft change didn't actually take effect for enum fields.

**Fix:** Delete and recreate the node:

```jsonc
// ✅ removeNode + addNode with correct enum value
{"type": "removeNode", "nodeName": "🔀 Route Switch"},
{"type": "addNode", "node": {
  "name": "🔀 Route Switch",
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3.4,
  "parameters": {"mode": "expression", "numberOutputs": 16, "output": "={{ $json.routeIndex }}"},
  "position": [896, 384]
}},
{"type": "addConnection", "source": "Previous Node", "target": "🔀 Route Switch"}
```

**Rule:** If you need to change a discriminated enum (mode, resource, operation), always `removeNode` + `addNode`. Don't waste time trying `setNodeParameter` or `updateNodeParameters`.

---

## 17. Subagent Interference — Concurrent MCP Edits on Same Workflow

**When using `delegate_task` to run a subagent that edits the same workflow while you're also editing it, changes conflict.** The subagent may:
- Add orphan nodes (e.g., `📮 Save Tracking to DB`, `📝 Process Reject Comment`)
- Overwrite the Switch expression with a different value
- Create duplicate nodes with the same name

**Symptom:** After subagent finishes, `get_workflow_details` shows nodes you didn't add, or the Switch `output` expression is different from what you set.

**Detection:** Check for `DISCONNECTED_NODE` warnings — orphan nodes from the subagent will appear as disconnected.

**Fix:** Remove orphan nodes immediately after the subagent completes, before your next publish:

```jsonc
// Remove all orphan nodes before publishing
{"type": "removeNode", "nodeName": "📮 Save Tracking to DB"},
{"type": "removeNode", "nodeName": "📝 Process Reject Comment"},
// Then verify: no DISCONNECTED_NODE warnings remain
```

**Prevention:** If you need parallel work on the same workflow, don't use `delegate_task`. Do all edits sequentially in the main session. If delegation is needed for research/planning, ensure the subagent only READS the workflow (no write operations).

---

## Quick Reference — Operation Types

| Operation | Use Case | Atomically? |
|-----------|----------|-------------|
| `updateNodeParameters` | Set multiple params on a known node | ✅ per call |
| `setNodeParameter` | Set one param by JSON path (fallback) | ✅ per call |
| `addNode` | Create new node | ✅ with other ops |
| `addConnection` | Wire nodes | ✅ with other ops |
| `removeNode` | Delete node | ✅ with other ops |
| `renameNode` | Rename node | ✅ per call |
| `setNodeCredential` | Attach credential | ✅ per call |
| `setWorkflowSettings` | Error workflow, timezone, etc. | ✅ per call |
