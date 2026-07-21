# Update Workflow — Decision Tree & Operation Patterns

> **REQUIRED READING before writing any code.**
> Call: `skill_view('n8n-builder', file_path='references/update-workflow.md')`

## Decision tree

```
WF already exists in n8n?
├── NO  → create_workflow_from_code (see node-sdk-patterns.md):
│          1. Write SDK code (≤20 nodes)
│          2. validate_workflow
│          3. create_workflow_from_code
│          4. setNodeCredential on every Telegram/API node
│          5. get_workflow_details → verify nodeCount
│
└── YES → user explicitly said "از اول بساز"?
          ├── YES → archive + create (only with explicit permission)
          └── NO  → use update_workflow with addNode operations:
                      1. get_workflow_details → see current nodes
                      2. Plan which nodes to ADD (not rewrite)
                      3. update_workflow([addNode × N, addConnection × N, setNodeCredential × N])
                      4. get_workflow_details → verify
```

## The ONE rule: never archive

❌ "I'll archive WF01 and rebuild it from scratch" — destroys execution history, credentials, webhook URL, active status
✅ "I'll use `update_workflow` with `addNode` + `addConnection` + `setNodeCredential`" — preserves everything

The ONLY case where archive+create is allowed: user explicitly says "از اول بساز". Do not suggest it yourself.

---

## Complete addNode patterns by node type

### Telegram — sendMessage (static keyboard)

```json
{ "type": "addNode", "node": {
  "name": "Send Welcome",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 2,
  "parameters": {
    "resource": "message",
    "operation": "sendMessage",
    "chatId": "={{ $('Extract Input Data').first().json.chat_id }}",
    "text": "Welcome text",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        { "row": { "buttons": [
          { "text": "🛍 Products", "additionalFields": { "callback_data": "view_products" } }
        ]}}
      ]
    }
  },
  "position": [800, 600]
}},
{ "type": "setNodeCredential", "nodeName": "Send Welcome",
  "credentialKey": "telegramApi",
  "credentialId": "78sfmXZgmLK4r8lq",
  "credentialName": "bale_bot_evet_rosteri" }
```

> **Static keyboard only.** `inlineKeyboard` with `rows[].row.buttons[]` is native to the Telegram node. NO Code node needed.

### Telegram — editMessageText (static keyboard only)

```json
{ "type": "addNode", "node": {
  "name": "Edit Menu",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 2,
  "parameters": {
    "resource": "message",
    "operation": "editMessageText",
    "chatId": "={{ $('Extract Input Data').first().json.chat_id }}",
    "messageId": "={{ $('Get Session').first().json.last_message_id }}",
    "text": "Menu text",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        { "row": { "buttons": [
          { "text": "🔙 Back", "additionalFields": { "callback_data": "back_to_menu" } }
        ]}}
      ]
    }
  },
  "position": [1000, 600]
}},
{ "type": "setNodeCredential", "nodeName": "Edit Menu",
  "credentialKey": "telegramApi",
  "credentialId": "78sfmXZgmLK4r8lq",
  "credentialName": "bale_bot_evet_rosteri" }
```

### Re-wiring existing trigger paths (proven pattern — 36 ops in 1 batch)

When you need to **insert nodes between existing connected nodes** (e.g., insert Read Products + Bundle Products between Trigger → Core Router):

```json
[
  // Step 1: Cut the old connection
  { "type": "removeConnection", "source": "📱 Telegram Trigger", "target": "🔀 Core Router" },
  // Step 2: Add new nodes
  { "type": "addNode", "node": { "name": "☕ Read Products", ... } },
  { "type": "addNode", "node": { "name": "📦 Bundle Products", ... } },
  // Step 3: Wire new path
  { "type": "addConnection", "source": "📱 Telegram Trigger", "target": "☕ Read Products" },
  { "type": "addConnection", "source": "☕ Read Products", "target": "📦 Bundle Products" },
  { "type": "addConnection", "source": "📦 Bundle Products", "target": "🔀 Core Router" }
]
```

**Proven:** This exact pattern with 36 ops (removeConnection + 15 addNode + 18 addConnection) succeeded atomically. removeConnection + addConnection in same batch is safe — the batch processes sequentially, not concurrently.

**DO NOT** use the Telegram node for dynamic keyboards. Use **Code node → HTTP Request** instead.

**Step 1: Code node** builds `{ text, inline_keyboard }` — raw Telegram 2D array:
```json
{ "type": "addNode", "node": {
  "name": "Build Product Keyboard",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const items = $input.all();\nlet text = '📦 Products:\\n\\n';\nconst inline_keyboard = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const item = items[i].json;\n  text += (i + 1) + '. ☕ ' + item.name + '\\n';\n  inline_keyboard.push([\n    { text: '☕ ' + item.name, callback_data: 'view_product_' + item.id }\n  ]);\n}\n\ninline_keyboard.push([\n  { text: '🏠 Back to menu', callback_data: 'back_to_menu' }\n]);\n\nreturn [{ json: { text, inline_keyboard } }];"
  },
  "position": [1200, 800]
}}
```

**Step 2: HTTP Request node** calls Bale/Telegram API directly — **chat_id/message_id from Trigger, not intermediate nodes**:
```json
{ "type": "addNode", "node": {
  "name": "Edit Products",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.4,
  "parameters": {
    "method": "POST",
    "url": "={{ 'https://api.telegram.org/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText'}}",
    "sendBody": true,
    "contentType": "json",
    "specifyBody": "keypair",
    "bodyParameters": {
      "parameters": [
        { "name": "chat_id", "value": "={{ $('📱 Telegram Trigger').item.json.callback_query?.message?.chat?.id }}" },
        { "name": "message_id", "value": "={{ $('📱 Telegram Trigger').item.json.callback_query?.message?.message_id }}" },
        { "name": "text", "value": "={{ $json.text }}" },
        { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
        { "name": "parse_mode", "value": "HTML" }
      ]
    }
  },
  "position": [1400, 600]
}}
```

**Key points:**
- Token resolves via `$credentials('name').accessToken` — no credential assignment on HTTP Request node
- `inline_keyboard` is a **raw 2D array** `[[{text, callback_data}], [{text}]]` — Telegram/Bale native wire format, NOT n8n's `rows[].row.buttons[]`
- **🚨 HTTP Request MUST set `contentType: "json"` and `specifyBody: "keypair"`** — without these, body parameters are silently ignored
- `reply_markup` is `JSON.stringify({ inline_keyboard: ... })` as a string, not an object
- **🚨 chat_id/message_id** must reference the **Telegram Trigger node** directly (`$('📱 Telegram Trigger').item.json...`), NOT intermediate Extract/Get Session nodes that may not exist yet when adding nodes via update_workflow
- Fix: use optional chaining (`?.`) for defensive access — `callback_query?.message?.chat?.id`

### Telegram — answerCallbackQuery

```json
{ "type": "addNode", "node": {
  "name": "Answer Callback Query",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 2,
  "parameters": {
    "resource": "callback",
    "operation": "answerQuery",
    "callbackQueryId": "={{ $json.callback_query.id }}"
  },
  "position": [480, 200],
  "onError": "continueRegularOutput"
}},
{ "type": "addConnection", "source": "Telegram Trigger", "target": "Answer Callback Query" },
{ "type": "setNodeCredential", "nodeName": "Answer Callback Query",
  "credentialKey": "telegramApi",
  "credentialId": "78sfmXZgmLK4r8lq",
  "credentialName": "bale_bot_evet_rosteri" }
```

### Set node (manual mode)

```json
{ "type": "addNode", "node": {
  "name": "Format Welcome Text",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "manual",
    "includeOtherFields": true,
    "assignments": {
      "assignments": [
        { "id": "a1", "name": "text", "value": "={{ 'Hello ' + $json.first_name }}", "type": "string" }
      ]
    }
  },
  "position": [1200, 800]
}}
```

**CRITICAL:** `assignments` must be a nested object `{ "assignments": [...] }`, NOT directly an array.

### If node

```json
{ "type": "addNode", "node": {
  "name": "User Registered?",
  "type": "n8n-nodes-base.if",
  "typeVersion": 2,
  "parameters": {
    "conditions": {
      "combinator": "and",
      "conditions": [
        { "id": "c1", "leftValue": "={{ $json.exists }}",
          "operator": { "type": "boolean", "operation": "true" }, "rightValue": true }
      ],
      "options": { "caseSensitive": true, "typeValidation": "strict", "version": 2 }
    }
  },
  "position": [1400, 800]
}},
{ "type": "addConnection", "source": "Check/Register User", "target": "User Registered?" },
// output 0 (true) → Register New User
{ "type": "addConnection", "source": "User Registered?", "sourceIndex": 0, "target": "Register New User" },
// output 1 (false) → already registered, skip
{ "type": "addConnection", "source": "User Registered?", "sourceIndex": 1, "target": "Format Welcome Text" }
```

### Switch node (rules mode)

```json
{ "type": "addNode", "node": {
  "name": "Route by State",
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "rules",
    "rules": {
      "values": [
        {
          "conditions": {
            "combinator": "and",
            "conditions": [
              { "id": "c1", "leftValue": "={{ $json.state }}",
                "operator": { "type": "string", "operation": "equals" }, "rightValue": "idle" }
            ],
            "options": { "caseSensitive": true, "typeValidation": "strict", "version": 3 }
          }
        },
        {
          "conditions": {
            "combinator": "and",
            "conditions": [
              { "id": "c2", "leftValue": "={{ $json.state }}",
                "operator": { "type": "string", "operation": "equals" }, "rightValue": "selecting_weight" }
            ],
            "options": { "caseSensitive": true, "typeValidation": "strict", "version": 3 }
          }
        }
      ]
    },
    "options": {}
  },
  "position": [1600, 600]
}},
// output 0 → idle → Route by Type
{ "type": "addConnection", "source": "Route by State", "sourceIndex": 0, "target": "Route by Type" },
// output 1 → selecting_weight → Weight Handler
{ "type": "addConnection", "source": "Route by State", "sourceIndex": 1, "target": "Weight Handler" },
```

**CRITICAL for Switch (rules mode):**
- `rules` must be an OBJECT with `values[]` — each value has `conditions` (NOT a raw conditions array at top level)
- Each value's conditions has `combinator`, `conditions[]`, `options`
- Each condition needs a unique `id` (c1, c2, c3, ...)
- `options.version` should be `3` for Switch, `2` for If
- Output indices correspond to `values` array order — index 0 = first rule
- For fallback: `options.fallbackOutput: 'extra'` creates an extra output at index = values.length
- Do NOT set `dataType`/`value1` — those are for `expression` mode, not `rules` mode

### Code node (simple jsCode)

```json
{ "type": "addNode", "node": {
  "name": "Extract Input Data",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForAllItems",
    "language": "javaScript",
    "jsCode": "const item = $input.first().json;\nreturn [{ json: { chat_id: String(item.message?.chat?.id || '') } }];"
  },
  "position": [400, 200]
}}
```

**CRITICAL:** Use `jsCode` NOT `sourceCode`. The `sourceCode` field is silently ignored by addNode. Position must be set explicitly — Code nodes default to [0, 0].

### PostgreSQL node (executeQuery)

```json
{ "type": "addNode", "node": {
  "name": "Register New User",
  "type": "n8n-nodes-base.postgres",
  "typeVersion": 2.6,
  "parameters": {
    "operation": "executeQuery",
    "query": "INSERT INTO users (telegram_id, first_name) VALUES ($1, $2) ON CONFLICT (telegram_id) DO NOTHING",
    "options": {
      "queryReplacement": "={{ $('Extract Input Data').first().json.chat_id }},{{ $('Extract Input Data').first().json.first_name }}"
    }
  },
  "position": [1600, 1000]
}},
{ "type": "setNodeCredential", "nodeName": "Register New User",
  "credentialKey": "postgres",
  "credentialId": "3pjdkIFwE1sGBCvJ",
  "credentialName": "locall main db" }
```

**CRITICAL:** `queryReplacement` lives INSIDE `options`, NOT at the top level of parameters. This is a common mistake with addNode.

**🚨 executeQuery must NOT have a `columns` field.** Including `"columns": {}` or `"columns": { "mappingMode": ... }` on an executeQuery node produces `INVALID_PARAMETER` warning: "This field is only allowed when operation=insert/update/upsert". Strip `columns` entirely — if accidentally included, use `updateNodeParameters(nodeName, { operation: "executeQuery", query: "...", options: {...} }, true)` to clean it.

### HTTP Request node (for dynamic Telegram keyboard / Bale API)

```json
{ "type": "addNode", "node": {
  "name": "Edit Products",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.4,
  "parameters": {
    "method": "POST",
    "url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText'}}",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        { "name": "chat_id", "value": "={{ $('Extract Input Data').first().json.chat_id }}" },
        { "name": "message_id", "value": "={{ $('Get Session').first().json.last_message_id }}" },
        { "name": "text", "value": "={{ $json.text }}" },
        { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
        { "name": "parse_mode", "value": "Markdown" }
      ]
    }
  },
  "position": [1400, 600]
}}
```

No credential assignment needed — token is embedded in URL via `$credentials()`.

---

## DataTable workaround (trap-37)

addNode **may silently drop** `columns.schema`, `columns.matchingColumns`, and `data.keyValue` for DataTable nodes. However, `resource`, `operation`, `dataTableId`, `filters`, `matchType`, and `columns.value` DO survive (proven in a 36-ops batch with 3 DataTable addNodes).

**Nuance — which fields survive addNode:**

| Field | Survives? | Proven |
|-------|-----------|--------|
| `resource`, `operation` | ✅ Yes | 36-ops batch |
| `dataTableId`, `filters` | ✅ Yes | 36-ops batch |
| `columns.value`, `columns.mappingMode` | ✅ Yes | Update Session Cart in batch |
| `matchType` | ✅ Yes | 36-ops batch |
| `columns.schema` | ⚠️ May drop | Trap-37 caution |
| `columns.matchingColumns` | ⚠️ May drop | Trap-37 caution |
| `data.keyValue` | ❌ Drops | Trap-37 |

**For GET nodes (read-only):** addNode with full params works fine — no workaround needed.
**For UPDATE/upsert nodes without `data.keyValue`:** use `columns: { mappingMode: "defineBelow", value: { field1: "...", field2: "..." } }` directly — this survives and is sufficient for simple update operations.

**Only use the SDK workaround** when you absolutely need `data.keyValue` or `columns.schema`.

**🚨 CRITICAL — Trap 41: `columns.value` must NOT be `{}`.**

The `schema` defines WHICH columns exist. The `value` defines WHAT to write — it is NOT optional. `"value": {}` = silent write failure, n8n shows empty fields on the canvas.

For UPDATE/upsert DataTable nodes: **BOTH `columns.value` AND `data.keyValue` must be populated** with the same expressions. They are redundant components but both required — omitting either causes silent data loss.

Correct full params for an UPDATE node:
```json
{
  "resource": "row",
  "operation": "update",
  "dataTableId": { "__rl": true, "mode": "id", "value": "YHSI56AWMmXbAtat" },
  "matchType": "allConditions",
  "filters": {
    "conditions": [
      { "keyName": "telegram_id", "keyValue": "={{ $('Extract Input Data').first().json.chat_id }}" }
    ]
  },
  "columns": {
    "mappingMode": "defineBelow",
    "matchingColumns": [],
    "schema": [
      { "id": "state", "displayName": "state", "type": "string" },
      { "id": "selected_product_id", "displayName": "selected_product_id", "type": "string" }
    ],
    "value": {
      "state": "selecting_weight",
      "selected_product_id": "={{ $json.selected_product_id }}"
    }
  },
  "data": {
    "keyValue": [
      { "keyName": "state", "keyValue": "selecting_weight" },
      { "keyName": "selected_product_id", "keyValue": "={{ $json.selected_product_id }}" }
    ]
  }
}
```

For GET nodes (read-only) — no `columns.value` or `data` needed, only `operation: "get"`, `dataTableId`, and `filters`:
    }
  }
}
```

**🚨 CRITICAL — `columns.value` is WHAT n8n writes to the database:**
- `schema` defines which columns CAN be written (the column list)
- `value` defines WHAT to write (the actual field values)
- Without `value: { "field": "value" }`, the DataTable node receives an UPDATE request with no values → writes nothing → the n8n canvas shows empty fields
- Always populate `value` with ALL the keys you want to set. Each key is the column name, each value is the value or expression.
- For empty values that should stay as-is, simply omit them from `value` or explicitly set to `"={{ $json.existing_field }}"`


---

## Common state management patterns (Set + DataTable)

These three patterns are the MOST commonly broken by addNode. Values come out empty because the parameter structure is wrong. Copy these exactly.

### Pattern 1: Set node — update session state (e.g., "Set State: selecting_weight")

```json
{ "type": "addNode", "node": {
  "name": "Set State: selecting_weight",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "manual",
    "includeOtherFields": true,
    "assignments": {
      "assignments": [
        { "id": "a1", "name": "state", "value": "selecting_weight", "type": "string" }
      ]
    }
  },
  "position": [1800, 800]
}}
```

**CRITICAL:** The `value` field is a plain string `"selecting_weight"`. NOT an expression. NOT `={{ }}`. Just the string. If you need a dynamic value, then use `"value": "={{ $json.some_field }}"`.

### Pattern 2: Set node — Save data from Code/Telegram (e.g., "Save Welcome message_id")

```json
{ "type": "addNode", "node": {
  "name": "Save Welcome message_id",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "manual",
    "includeOtherFields": true,
    "assignments": {
      "assignments": [
        { "id": "a1", "name": "last_message_id", "value": "={{ $json.message_id }}", "type": "string" }
      ]
    }
  },
  "position": [2000, 800]
}}
```

**CRITICAL:** `{{ $json.message_id }}` MUST be wrapped in quotes: `"={{ $json.message_id }}"`. Without the `=` prefix + outer quotes, n8n treats it as literal text `$json.message_id`.

### Pattern 3: DataTable — Create/Update Session row

For new WF (SDK code) — use this syntax:
```typescript
const createSession = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Create Session',
    parameters: {
      resource: 'row',
      operation: 'upsert',
      primaryKey: 'telegram_id',
      dataTableId: { __rl: true, mode: 'id', value: 'TABLE_ID' },
      data: {
        keyValue: [
          { keyName: 'telegram_id', keyValue: expr('$("Extract Input Data").first().json.chat_id') },
          { keyName: 'state', keyValue: 'idle' },
          { keyName: 'last_message_id', keyValue: '0' }
        ]
      },
      options: { alwaysOutputData: true }
    }
  }
});
```

For existing WF (addNode) — DataTable nodes DON'T work with addNode (Trap 37). Use the workaround:
1. `create_workflow_from_code` with just the DataTable node
2. `get_workflow_details(temp_wf)` → extract parameters
3. `updateNodeParameters(real_wf, "Create Session", extracted_params, true)`

Actually, for the addNode case, the DataTable node's `data.keyValue` is silently dropped. So you MUST use the SDK workaround.

### Pattern 4: Set node — increment counter or toggle boolean

```json
{ "type": "addNode", "node": {
  "name": "Set Try Count",
  "type": "n8n-nodes-base.set",
  "typeVersion": 3.4,
  "parameters": {
    "mode": "manual",
    "includeOtherFields": true,
    "assignments": {
      "assignments": [
        { "id": "a1", "name": "try_count", "value": "={{ Number($json.try_count || 0) + 1 }}", "type": "number" }
      ]
    }
  },
  "position": [2200, 800]
}}
```

---

## Common pitfalls with addNode

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Node created but empty | Wrong parameter path (e.g. `sourceCode` vs `jsCode`) | Use correct field name per node type |
| DataTable has no columns/operation | addNode drops `resource`/`operation`/`columns` | Use `setNodeParameter` + `updateNodeParameters` after add |
| Postgres has no query params | `queryReplacement` at top level, not in `options` | Move `queryReplacement` inside `options` object |
| Credential not set | No `setNodeCredential` after add | Always include credential operation |
| Connection not visible | Wrong `sourceIndex`/`targetIndex` | Match Switch output index to condition order |
| Assignments empty | Set node `assignments` is array, not nested object | Wrap in `{ assignments: [...] }` |
| Code node has no code | Used `sourceCode.javascript` instead of `jsCode` | Use `jsCode` field directly |
| Code node at [0,0] | Position not set in addNode | Always set position for Code nodes |
| Send Welcome has no resource/operation | `replace: true` on updateNodeParameters nuked sibling keys | Always include `resource`/`operation` in replace payload |
| Switch outputs wrong index | Used `expression` mode params on `rules` mode | For rules mode, use `rules.values[n]`, NOT `dataType`/`value1`/`conditions` |
| HTTP Request 404 | Wrong token or base URL | Bale: `https://tapi.bale.ai/bot{token}/`; Telegram: `https://api.telegram.org/bot{token}/` |
| addConnection validation error | Nested `addConnection` key inside the operation | `source` and `target` must be at the TOP LEVEL of the operation object, not nested |
| "node type X does not accept credential Y" | Wrong credential type on node (e.g. telegramApi on DataTable) | Only set credentials on nodes that support them; DataTable/Postgres use different types |
| "settings must specify at least one field" | Used `setNodeSettings` with `{ "disabled": false }` | Use `setNodeDisabled` operation instead |
| "Expected object, received string" on batch | 2+ updateNodeParameters with Persian/Unicode expressions in one batch | Split into one call per node — simple ops batch fine |
| Telegram node missing chatId after replace:true | `replace: true` nukes ALL params including chatId/messageId | Re-include chatId/messageId/inlineKeyboard in replace payload |

## ⚠️ REPLACE: TRUE NUKE HAZARD

When using `updateNodeParameters` with `replace: true`, you MUST include **ALL** parameters the node needs, including `resource`, `operation`, `mode`, etc. The replace flag **completely overwrites** the parameters object — it does NOT merge.

**Telegram-specific:** `replace: true` on a Telegram node also wipes `chatId`, `messageId`, `inlineKeyboard`, etc. You MUST re-include them:

```json
// ❌ WRONG — only passes text, nukes chatId/messageId/inlineKeyboard
{ "type": "updateNodeParameters", "nodeName": "Edit Menu",
  "parameters": { "text": "={{ 'new text' }}" },
  "replace": true }

// ✅ CORRECT — re-includes ALL Telegram params
{ "type": "updateNodeParameters", "nodeName": "Edit Menu",
  "parameters": {
    "resource": "message",
    "operation": "editMessageText",
    "chatId": "={{ $('📱 Telegram Trigger').first().json.callback_query.message.chat.id }}",
    "messageId": "={{ $('📱 Telegram Trigger').first().json.callback_query.message.message_id }}",
    "text": "={{ 'new text' }}",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": { "rows": [...] }
  },
  "replace": true }
```

❌ If you only pass `{"text": "..."}` with `replace: true`, chatId/messageId become undefined → `"Type mismatches"` validation error.

## ⚠️ Batch updateNodeParameters with complex Unicode expressions

**Symptom:** Batching 2+ `updateNodeParameters` operations with long Persian/Unicode expressions in a single `update_workflow` call returns `"Input validation error: Expected object, received string"` at `operations[0]`.

**Cause:** The MCP tool's JSON parser chokes on complex Unicode strings when multiple operations are batched. Simple ASCII operations batch fine; mixed Persian + long JS expressions don't.

**Fix:** Split into individual `update_workflow` calls — one per node:

```json
// ❌ FAILS — 2+ ops with Persian text in expressions
{ "operations": [
    { "type": "updateNodeParameters", "nodeName": "A", "parameters": { "text": "={{ long Persian }}" } },
    { "type": "updateNodeParameters", "nodeName": "B", "parameters": { "text": "={{ another Persian }}" } }
]}

// ✅ WORKS — one call per node
{ "operations": [{ "type": "updateNodeParameters", "nodeName": "A", "parameters": { "text": "={{ Persian }}" } }] }
{ "operations": [{ "type": "updateNodeParameters", "nodeName": "B", "parameters": { "text": "={{ Persian }}" } }] }
```

**Exception:** Batching works fine for simple operations (addNode, removeNode, addConnection, setNodeCredential) and for `updateNodeParameters` with short/ASCII-only expressions.

## 🚨 Auto-Assigned Credential Verification

After every `update_workflow` batch that includes Telegram addNode operations, **check the `autoAssignedCredentials` field** in the response:

```json
// Response snippet to inspect:
"autoAssignedCredentials": [
  { "nodeName": "📜 Show Orders List (v2)", "credentialName": "@natentestbot:", "credentialType": "telegramApi" }
]
```

If the assigned credential name is wrong (e.g. `@natentestbot:` instead of `bale_bot_evet_rosteri`), n8n auto-picked a different credential. Fix immediately with a follow-up `setNodeCredential` operation.

**🚨 CRITICAL:** Even when you explicitly set `"credentials"` inside the addNode payload, n8n may still auto-override with a different credential. Always verify.

## 🚨 Telegram nodes MUST have `resource: "message"`

Every Telegram node used for sending/editing messages **must** include `"resource": "message"` in its parameters. Without it, n8n throws:

```
INVALID_PARAMETER: Missing discriminator "parameters.resource". Expected one of: "chat", "callback", "file".
```

```json
// CORRECT — includes resource
{ "type": "addNode", "node": {
  "name": "Send Alert",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "resource": "message",        // ← REQUIRED
    "operation": "sendMessage",   // ← REQUIRED  
    "chatId": "...",
    "text": "..."
  },
  "credentials": { "telegramApi": { "id": "78sfmXZgmLK4r8lq", "name": "bale_bot_evet_rosteri" } },
  "position": [1000, 500]
}}
```

## 🚨 DataTable output replaces context — DO NOT reference trigger fields after a DB node

After a DataTable or Postgres executeQuery node, `$json` **only contains the database columns** — trigger fields like `callback_query.from.id` are NOT available.

**Wrong** (after DataTable → expects trigger fields that no longer exist):
```json
"queryReplacement": "={{ $json.callback_query.from.id }}"
```

**Correct** (use DataTable's own field):
```json
"queryReplacement": "={{ $json.user_id }}"
```

**Pain lesson from session:** 🆕 Check/Register User node errored with "Column to match on not found" because it was still referencing `$json.callback_query.from.id`, but the input came from DataTable which only has `user_id`, `chat_id`, `cart_json`, etc.

## ⚠️ The silent no-op: setNodeParameter path vs updateNodeParameters replace

`setNodeParameter` with `path: "/parameters"` may silently not apply to an existing node. If after applying it the node still shows old config, retry with `updateNodeParameters` with `replace: true` (see `references/setnode-parameter-pitfalls.md` for details).

## Batch operations: up to 100 per call

Combine multiple operations in one `update_workflow` call:

```json
[
  // Add 3 nodes
  { "type": "addNode", "node": { "name": "A", ... } },
  { "type": "addNode", "node": { "name": "B", ... } },
  { "type": "addNode", "node": { "name": "C", ... } },
  // Connect them
  { "type": "addConnection", "source": "Parent", "target": "A" },
  { "type": "addConnection", "source": "A", "target": "B" },
  { "type": "addConnection", "source": "B", "target": "C" },
  // Set credentials
  { "type": "setNodeCredential", "nodeName": "A", ... },
  { "type": "setNodeCredential", "nodeName": "C", ... }
]
```

If any operation fails, ALL are rolled back atomically.

### Telegram — sendPhoto (with inline keyboard)

```json
{ "type": "addNode", "node": {
  "name": "Forward Receipt to Admin",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "parameters": {
    "resource": "message",
    "operation": "sendPhoto",
    "chatId": "={{ $json.admin_chat_id }}",
    "file": "={{ $('📂 File Extractor').first().json.fileId }}",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        { "row": { "buttons": [
          { "text": "✅ تأیید", "additionalFields": { "callback_data": "={{ 'admin_ap_' + $json.order_id }}" } },
          { "text": "❌ رد", "additionalFields": { "callback_data": "={{ 'admin_rj_' + $json.order_id }}" } }
        ]}}
      ]
    },
    "additionalFields": {
      "caption": "={{ '🧾 فیش واریزی\\n📦 سفارش: ' + $json.order_code }}",
      "parse_mode": "HTML"
    }
  },
  "position": [560, -308]
}},
{ "type": "setNodeCredential", "nodeName": "Forward Receipt to Admin",
  "credentialKey": "telegramApi",
  "credentialId": "78sfmXZgmLK4r8lq",
  "credentialName": "bale_bot_evet_rosteri" }
```

**Key points:**
- `file` parameter accepts a Telegram `file_id` (from message.photo array) or HTTP URL — no `binaryData: true` needed
- `caption` goes in `additionalFields`, NOT as a top-level parameter
- `inlineKeyboard` works the same as sendMessage — `rows[].row.buttons[]` format
- Photo file_id must be sourced from the original trigger node (`$('📂 File Extractor').first().json.fileId`), NOT from intermediate DataTable nodes

### Enable/disable a node

```json
{ "type": "setNodeDisabled", "nodeName": "📂 File Extractor", "disabled": false }
```

**CRITICAL:** Do NOT use `setNodeSettings` with `{ "disabled": false }` — that fails with "settings must specify at least one field". Use the dedicated `setNodeDisabled` operation type.

---

## Quick reference

| Goal | Operation type | Notes |
|------|--------------|-------|
| Add a node | `addNode` | Provide full parameters |
| Remove a node | `removeNode` | Auto-removes its connections |
| Change one parameter | `setNodeParameter` + path | Small payload, targeted |
| Replace all parameters | `updateNodeParameters` + `replace: true` | Full reset — include ALL keys |
| Set credential | `setNodeCredential` | Required after every add |
| Connect two nodes | `addConnection` | source/target at TOP LEVEL, not nested |
| Disconnect | `removeConnection` | Do in SEPARATE batch from add |
| Change onError/retry | `setNodeSettings` | After create, not in SDK config |
| Enable/disable node | `setNodeDisabled` | `{ "disabled": false/true }` — NOT setNodeSettings |
| Rename a node | `renameNode` | New name must be unique |
| Move on canvas | `setNodePosition` | [x, y] coordinates |
