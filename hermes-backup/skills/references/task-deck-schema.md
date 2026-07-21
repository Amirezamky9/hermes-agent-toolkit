# Task Deck YAML Schema — Complete Reference (Generic)

> Load via `skill_view(name='n8n-reviwer', file_path='references/task-deck-schema.md')`

## Structure

Every task deck is a YAML file with these sections:

```yaml
deck:           # Required — metadata about this deck
manifest_keys_used: []  # Required — which manifest sections needed
nodes: []           # Required — the actual n8n nodes
connections: []     # Required — how nodes connect
settings: []        # Optional — per-node execution settings
test_hints: {}      # Required — pin data for QA
```

## Top-Level Fields

### deck (object, required)

```yaml
deck:
  id: "01a"                           # sortable identifier
  title: "WF01 — Core Skeleton"       # human+LLM-readable
  architecture_ref: "ARCHITECTURE.md#3" # back to source for questions
  estimated_nodes: 11                 # for session planning
  depends_on: []                      # deck IDs that must be built first
  builder_notes: |                    # one-line context for builder
    First session. Build trigger through router.
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | ✅ | patterns: `01a`, `02`, `03b` |
| `title` | string | ✅ | ≤80 chars |
| `architecture_ref` | string | ✅ | `FILE#SECTION` format |
| `estimated_nodes` | int | ✅ | ≈ number of nodes |
| `depends_on` | string[] | ❌ | empty if first deck |
| `builder_notes` | string | ❌ | keep to 1-2 lines |

### manifest_keys_used (string[], required)

Which sections of `manifest.yaml` this deck references:

```yaml
manifest_keys_used:
  - credentials
  - data_tables
  - state_machine
  - error_handling
```

Rules:
- Only list sections actually referenced by `nodes[]` or `connections[]`
- If a deck creates a Data Table for the first time, reference `data_tables.{name}`
- Use dot notation for nesting: `postgres_schemas.orders`
- For stateless architectures, omit `state_machine` and `callback_conventions`

### nodes[] (array of objects, required)

```yaml
nodes:
  - name: "Telegram Trigger"
    type: "n8n-nodes-base.telegramTrigger"
    typeVersion: 1.3
    parameters:
      updates: ["message", "callback_query"]
    credentials: telegramApi      # key from manifest.credentials
    position: [200, 200]
    notes: "Source of all incoming data"
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✅ | unique within workflow |
| `type` | string | ✅ | full n8n type ID |
| `typeVersion` | number | ✅ | from search_nodes |
| `parameters` | object | ✅ | exact n8n param shape |
| `credentials` | string | ❌ | omit if credential-free; key from manifest |
| `position` | [int, int] | ✅ | canvas coordinates [x, y] |
| `onError` | string | ❌ | one of: `continueRegularOutput`, `continueErrorOutput`, `stopWorkflow` |
| `notes` | string | ❌ | one line max |

#### Common node type parameters

**Trigger — Telegram:**
```yaml
- name: "Telegram Trigger"
  type: "n8n-nodes-base.telegramTrigger"
  typeVersion: 1.3
  parameters:
    updates: ["message", "callback_query"]
  credentials: telegramApi
```

**Trigger — Webhook:**
```yaml
- name: "Webhook Trigger"
  type: "n8n-nodes-base.webhook"
  typeVersion: 1
  parameters:
    path: "my-webhook-path"
    httpMethod: "POST"
    options:
      responseData: "allEntries"
      responseMode: "onReceived"
  options: {}
```

**Trigger — Schedule:**
```yaml
- name: "Daily Schedule"
  type: "n8n-nodes-base.scheduleTrigger"
  typeVersion: 1.2
  parameters:
    triggerTimes:
      item:
        - mode: "everyDay"
          hour: 9
          minute: 0
```

**Telegram Send/Edit Message:**
```yaml
- name: "Send Message"
  type: "n8n-nodes-base.telegram"
  typeVersion: 1.2
  parameters:
    resource: "message"
    operation: "sendMessage"  # or editMessageText
    chatId: "={{ $('Input Processor').first().json.chat_id }}"
    text: "Message text here"
    replyMarkup: "inlineKeyboard"
    inlineKeyboard:
      rows:
        - row:
            buttons:
              - text: "📋 Menu"
                additionalFields:
                  callback_data: "menu"
    additionalFields:
      parse_mode: "HTML"
  credentials: telegramApi
  onError: "continueRegularOutput"
```

**Telegram Answer Callback:**
```yaml
- name: "Answer Callback"
  type: "n8n-nodes-base.telegram"
  typeVersion: 1.2
  parameters:
    resource: "callback"
    operation: "answerQuery"
    callbackQueryId: "={{ $json.callback_query.id }}"
  credentials: telegramApi
  onError: "continueRegularOutput"  # CRITICAL: pass text messages silently
```

**Switch (Router) — TWO modes:**

> 🚨 **Critical: Type-First routing (Telegram bots, callback routing) MUST use `mode: "expression"`.** Expression mode matches first-true rule, supports `startsWith()`, `!==`, `||` operators, and is cleaner for multi-output routers. Rules mode works for simple value-equality checks.

**Mode A — expression (for Type-First routing, callback routing, state routing):**
```yaml
- name: "Route by Type"
  type: "n8n-nodes-base.switch"
  typeVersion: 3.4
  parameters:
    mode: "expression"
    outputs: 5
    conditions:
      options:
        caseSensitive: true
        leftValue: ""
        typeValidation: "strict"
      conditions:
        - id: "c1"
          expression: "={{ $json.callback_query !== undefined }}"
        - id: "c2"
          expression: "={{ $json.message.photo || $json.message.document || $json.message.voice || $json.message.audio || $json.message.video !== undefined }}"
        - id: "c3"
          expression: "={{ $json.message.text && $json.message.text.startsWith('/') }}"
        - id: "c4"
          expression: "={{ $json.message.text && !$json.message.text.startsWith('/') }}"
```

Use `startsWith()` in expression mode for callback data routing:
```yaml
- id: "c2"
  expression: "={{ $json.callback_query.data.startsWith('menu_') && $json.callback_query.data != 'menu_main' }}"
```

**Mode B — rules (for simple value matching, numeric comparisons):**
```yaml
- name: "Route by Value"
  type: "n8n-nodes-base.switch"
  typeVersion: 3.4
  parameters:
    mode: "rules"
    rules:
      values:
        - name: "callback"
          conditions:
            combinator: "and"
            conditions:
              - id: "c1"
                leftValue: "={{ $json.type }}"
                operator:
                  type: "string"
                  operation: "equals"
                rightValue: "callback"
            options:
              caseSensitive: true
              typeValidation: "strict"
              version: 3
        - name: "command"
          conditions:
            combinator: "and"
            conditions:
              - id: "c2"
                leftValue: "={{ $json.type }}"
                operator:
                  type: "string"
                  operation: "equals"
                rightValue: "command"
            options:
              caseSensitive: true
              typeValidation: "strict"
              version: 3
```

**IF (Binary):**
```yaml
- name: "Check Condition"
  type: "n8n-nodes-base.if"
  typeVersion: 2
  parameters:
    conditions:
      combinator: "and"
      conditions:
        - id: "c1"
          leftValue: "={{ $json.value }}"
          operator:
            type: "number"
            operation: "largerEqual"
          rightValue: 1
      options:
        caseSensitive: true
        typeValidation: "strict"
        version: 2
```

**Set (Manual):**
```yaml
- name: "Format Output"
  type: "n8n-nodes-base.set"
  typeVersion: 3.4
  parameters:
    mode: "manual"
    includeOtherFields: true
    assignments:
      assignments:
        - id: "a1"
          name: "text"
          value: "Formatted message text"
          type: "string"
```

**Data Table Read/Insert/Update/Upsert:**
```yaml
- name: "Read Data"
  type: "n8n-nodes-base.dataTable"
  typeVersion: 1.1
  parameters:
    resource: "row"
    operation: "get"  # or search, create, update, delete
    dataTableId:
      __rl: true
      mode: "id"
      value: "{{manifest.data_tables.table_name}}"  # Builder replaces
    filters:
      conditions:
        - keyName: "id"
          keyValue: "={{ $json.id }}"
    options:
      alwaysOutputData: true
```

**Postgres Query:**
```yaml
- name: "Postgres Query"
  type: "n8n-nodes-base.postgres"
  typeVersion: 2
  parameters:
    operation: "executeQuery"
    query: "SELECT * FROM table_name WHERE id = $1"
    queryReplacement:
      - "={{ $json.id }}"
  credentials: postgres
```

**Execute Sub-Workflow:**
```yaml
- name: "Execute Sub-workflow"
  type: "n8n-nodes-base.executeWorkflow"
  typeVersion: 2
  parameters:
    source: "database"
    workflowId: "{WF02_ID}"  # placeholder — Builder fills in
    mode: "once"
    workflowInputs:
      values:
        - name: "input_key"
          value: "={{ $json.value }}"
    options:
      waitForSubWorkflow: true
```

**Code (JavaScript):**
```yaml
- name: "Transform Data"
  type: "n8n-nodes-base.code"
  typeVersion: 2
  parameters:
    mode: "runOnceForAllItems"
    language: "javaScript"
    jsCode: |
      const item = $input.first().json;
      return [{
        json: {
          id: String(item.id || ''),
          value: item.value || ''
        }
      }];
```

**HTTP Request:**
```yaml
- name: "API Call"
  type: "n8n-nodes-base.httpRequest"
  typeVersion: 4.2
  parameters:
    method: "GET"
    url: "https://api.example.com/endpoint"
    authentication: "genericCredentialType"
    genericAuthType: "httpHeaderAuth"
    sendHeaders: true
    headerParameters:
      parameters:
        - name: "Authorization"
          value: "Bearer {{ $json.token }}"
    options:
      timeout: 30000
  credentials: httpHeaderAuth
```

**AI Agent:**
```yaml
- name: "AI Agent"
  type: "@n8n/n8n-nodes-langchain.agent"
  typeVersion: 1.6
  parameters:
    agentType: "toolsAgent"
    systemMessage: "You are a helpful assistant."
    options:
      sessionId:
        __rl: true
        mode: "id"
        value: "={{ $json.session_id }}"
```

**OpenRouter/LLM Model:**
```yaml
- name: "OpenRouter Model"
  type: "@n8n/n8n-nodes-langchain.lmChatOpenRouter"
  typeVersion: 1.2
  parameters:
    model: "openai/gpt-4o"
  credentials: openRouterApi
```

### switch_outputs (array, CRITICAL for Switch nodes)

**Required for EVERY Switch with 3+ outputs.** This is the #1 anti-routing-error weapon.

```yaml
switch_outputs:
  - node: "Route by Type"
    outputs:
      - { index: 0, condition: "type == 'callback'", target: "Callback Router" }
      - { index: 1, condition: "type == 'command' and text == '/start'", target: "Welcome Handler" }
      - { index: 2, condition: "type == 'command' and text == '/menu'", target: "Menu Handler" }
      - { index: 3, condition: "type == 'text'", target: "Text Handler" }
      - { index: 4, condition: "fallback (no match)", target: "Fallback Handler" }
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `node` | string | ✅ | Switch node name |
| `outputs[]` | array | ✅ | one per output port |
| `outputs[].index` | int | ✅ | 0-based, matches Switch condition order |
| `outputs[].condition` | string | ✅ | summary of the rule |
| `outputs[].target` | string | ✅ | target node connected to this port |

### sdk_translation (string, recommended for every 3+ output Switch)

Shows the exact SDK chain the Builder must produce:

```yaml
sdk_translation: |
  // Route by Type — 5 outputs
  routeByType
    .onCase(0, callbackRouter)       // type == 'callback' 🎯
    .onCase(1, welcomeHandler)       // type == 'command' / /start 👋
    .onCase(2, menuHandler)          // type == 'command' / /menu 📋
    .onCase(3, textHandler)          // type == 'text' 💬
    .onCase(4, fallbackHandler);     // fallback — no matching type ❓
```

### connection_integrity_check (string[], recommended)

Checklist the Builder validates before create:

```yaml
connection_integrity_check:
  - "Route by Type has EXACTLY 5 outputs (index 0-4)"
  - "Output 0 (callback → Callback Router) is connected"
  - "Output 1 (/start → Welcome Handler) is connected"
  - "Output 2 (/menu → Menu Handler) is connected"
  - "Output 3 (text → Text Handler) is connected"
  - "Output 4 (fallback → Fallback Handler) is connected"
```

### routing_table (object, preferred over Mermaid)

Replaces Mermaid flowcharts with explicit path traces:

```yaml
routing_table:
  entry_point: "Telegram Trigger"
  paths:
    - path_id: "callback → process action"
      steps:
        - { from: "Telegram Trigger",     index: 0, to: "Input Processor" }
        - { from: "Input Processor",      index: 0, to: "Session Manager" }
        - { from: "Session Manager",      index: 0, to: "Route by State" }
        - { from: "Route by State",       index: 0, to: "Route by Type" }
        - { from: "Route by Type",        index: 0, to: "Callback Router" }
        - { from: "Callback Router",      index: 0, to: "Handler Node" }

    - path_id: "/start command"
      steps:
        - { from: "Telegram Trigger",     index: 0, to: "Input Processor" }
        - { from: "Input Processor",      index: 0, to: "Session Manager" }
        - { from: "Session Manager",      index: 0, to: "Route by State" }
        - { from: "Route by State",       index: 0, to: "Route by Type" }
        - { from: "Route by Type",        index: 1, to: "Welcome Handler" }
```

### connections[] (array of objects, required)

```yaml
connections:
  - source: "Route by State"
    sourceIndex: 0      # MUST match switch_outputs index
    target: "Route by Type"
    targetIndex: 0
  - source: "Route by State"
    sourceIndex: 1
    target: "Handler"
    targetIndex: 0
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source` | string | ✅ | node name |
| `sourceIndex` | int | ✅ | **MUST match switch_outputs index** |
| `target` | string | ✅ | node name |
| `targetIndex` | int | ❌ | default 0 |
| `connectionType` | string | ❌ | default "main". For AI: `ai_languageModel`, `ai_memory`, `ai_tool` |

#### AI Agent connections (special)

```yaml
# Main data connection:
- source: "AI Agent"
  target: "OpenRouter Model"
  connectionType: "ai_languageModel"

- source: "AI Agent"
  target: "Postgres Memory"
  connectionType: "ai_memory"

- source: "AI Agent"
  target: "Data Table Tool"
  connectionType: "ai_tool"

# Data flow:
- source: "Input Processor"
  target: "AI Agent"
  sourceIndex: 0
  targetIndex: 0
```

### settings[] (array of objects, optional)

```yaml
settings:
  - nodeName: "Answer Callback"
    onError: "continueRegularOutput"
```

### test_hints (object, required)

```yaml
test_hints:
  trigger_node: "Telegram Trigger"    # which node to trigger from
  cases:
    - name: "/start command"
      pin:
        message:
          text: "/start"
          chat: { id: 123 }
          from: { id: 1, first_name: "Test" }
          message_id: 50
      expected_path: "→ Route by Type → /start → Welcome"
      expected_nodes_executed:
        - "Telegram Trigger"
        - "Input Processor"
        - "Session Manager"
        - "Route by State"
        - "Route by Type"
        - "Welcome Handler"
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `trigger_node` | string | ✅ | name of trigger node |
| `cases[]` | array | ✅ | at least 1 happy + 1 edge case |
| `cases[].name` | string | ✅ | describes the scenario |
| `cases[].pin` | object | ✅ | input data shape (omit for schedule triggers with no input) |
| `cases[].expected_path` | string | ✅ | brief routing summary |
| `cases[].expected_nodes_executed` | string[] | ❌ | used by QA for validation |

## Manifest File Schema

See main SKILL.md for the manifest structure. Key points:
- `credentials` maps credential keys → {name, used_by[]}
- `data_tables` maps table names → {columns, pk}
- `postgres_schemas` maps table names → column definition list
- `state_machine` maps states → {handler, valid_inputs} (omit for stateless)
- `callback_conventions` maps callback_data → action (omit for non-chatbot)
- `message_editing` maps interaction type → behavior (omit for non-bot)
- `error_handling` structured error patterns
- `pending_config` (optional) — items the user must configure before production:
  ```yaml
  pending_config:
    - item: "Admin Telegram ID"
      status: "❌ Not set"
      what_to_do: "Add to settings table: admin_telegram_id = YOUR_ID"
    - item: "PostgreSQL Credential"
      status: "⚠️ Verify"
      what_to_do: "Create postgres credential in n8n"
  ```

## ⚠️ DataTable Session Lookup Behavior (Common Pitfall)

When using `dataTable` with `operation: "get"` and a filter, if **no row matches**, the node **outputs nothing** (zero items). The next node receives no input, causing it to either error or silently do nothing.

**Two workarounds:**

**A) Use `alwaysOutputData: true`** — the node outputs `{ empty: true }` when no match:
```yaml
- name: "🔍 Session Lookup"
  type: "n8n-nodes-base.dataTable"
  typeVersion: 1.1
  parameters:
    resource: "row"
    operation: "get"
    filters:
      conditions:
        - keyName: "user_id"
          keyValue: "={{ $json.from.id }}"
    options:
      alwaysOutputData: true
```

Then wire the output to an **IF** node checking `$json.empty`:
```yaml
conditions:
  - id: "c1"
    leftValue: "={{ $json.empty }}"
    operator:
      type: "boolean"
      operation: "equals"
    rightValue: true
# Output 0 (true) → session doesn't exist → create new
# Output 1 (false) → session exists → route by state
```

> **For `operation: "search"`, `alwaysOutputData` is not needed** — it always returns an array (possibly empty). Use `search` when you need multiple matches.

**B) Use `operation: "search"` + `limit: 1`** when you prefer an array output:
```yaml
- name: "🔍 Session Lookup"
  type: "n8n-nodes-base.dataTable"
  typeVersion: 1.1
  parameters:
    resource: "row"
    operation: "search"
    dataTableId: "..."
    filters:
      conditions:
        - keyName: "user_id"
          keyValue: "={{ $json.from.id }}"
    options:
      limit: 1
```
Then check `$json.length === 0` in an IF node.

**Recommendation:** Use `operation: "get"` + `alwaysOutputData: true` for session lookups — it's simpler and the `empty` boolean is cleaner than checking array length.

## File Naming Convention

```
deck-{ORDER}{LETTER}-{WF_NAME}-{MODULE}.yaml

ORDER   = 2-digit number: 01, 02, 03
LETTER  = optional letter for sub-splits: a, b, c, d
WF_NAME = wf01, wf02, wf03 (or single-workflow projects: just the module name)
MODULE  = short hyphenated module name

Examples multi-workflow:
deck-01a-wf01-core-skeleton.yaml
deck-01b-wf01-module-a.yaml
deck-02-wf02-ai-agent.yaml

Examples single-workflow:
deck-01-trigger-ingest.yaml
deck-02-transform.yaml
deck-03-delivery.yaml
```
