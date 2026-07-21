# n8n MCP Authoring Pitfalls — Session Reference

## 1. Set Node v3.4 Mode/Parameter Mismatch

### The Bug
Set node v3.4 has two modes with DIFFERENT parameter schemas:

**`mode: "raw"`** — expects `jsonOutput` (a string containing a JSON expression):
```json
{
  "parameters": {
    "mode": "raw",
    "jsonOutput": "={{ { route: $json.callback_query.data } }}",
    "includeOtherFields": false,
    "options": {}
  }
}
```

**`mode: "manual"`** — expects `assignments.assignments[]` array:
```json
{
  "parameters": {
    "mode": "manual",
    "assignments": {
      "assignments": [
        { "id": "route", "name": "route", "type": "string", "value": "={{ $json.callback_query.data }}" }
      ]
    },
    "includeOtherFields": true
  }
}
```

### The Error
When `mode: "raw"` is set but `assignments` is passed (instead of `jsonOutput`):
- The `assignments` parameter is **silently ignored**
- The node outputs its DEFAULT values: `{"my_field_1": "value", "my_field_2": 1}`
- Downstream nodes crash because expected fields are missing

### Execution Evidence
```
⚡ Normalize Input → {"route": "admin_dashboard"}           ✅ (jsonOutput was correct)
✅ Extract Order ID → {"my_field_1": "value", "my_field_2": 1}  ❌ (assignments ignored)
```

### Fix Pattern
```
For raw mode:     parameters.jsonOutput = "={{ { field: expr } }}"
For manual mode:  parameters.assignments.assignments = [{ id, name, type, value }]
```

---

## 2. Switch Node v3.4 Rules Structure

### Correct Structure
```json
{
  "parameters": {
    "mode": "rules",
    "rules": {
      "values": [
        {
          "conditions": {
            "combinator": "and",
            "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict", "version": 2 },
            "conditions": [
              {
                "id": "r0",
                "leftValue": "={{ $json.route }}",
                "operator": { "operation": "equals", "type": "string" },
                "rightValue": "admin_dashboard"
              }
            ]
          }
        }
      ]
    }
  }
}
```

### Common Mistakes
1. **Wrong key**: `rules: { rules: [...] }` → `SWITCH_WRONG_RULES_KEY`, should be `rules: { values: [...] }`
2. **Missing combinator**: Each rule needs `"combinator": "and"` → `FILTER_MISSING_COMBINATOR`
3. **Expression mode**: may route to ALL outputs in test — prefer `rules` mode

---

## 3. MCP Tool Operation Reference

### updateNodeParameters (RELIABLE)
Replaces entire `parameters` object:
```json
{ "operations": [{ "nodeName": "X", "type": "updateNodeParameters", "parameters": {...} }] }
```

### setNodeParameter (LIMITED)
❌ `path: "parameters"` → rejected as "unsafe"
❌ `path: "parameters.jsonOutput"` → same error

**Use `updateNodeParameters` instead.**

### addNode / removeNode
Most reliable for changing node type/structure.

---

## 4. Serialization Gotchas

| Issue | Fix |
|-------|-----|
| `typeVersion` as string | Use number: `3.4` not `"3.4"` |
| Large operations array | Split into smaller batches |
| `\n` in expression values | Use `\\n` or avoid newlines |
| MCP server rate limit | Wait 30-60s, retry |

---

## 5. Testing Pin Data Patterns

See pin data templates in the conversation for admin callback queries and text messages.
