---
name: n8n-workflow-analyzer
description: |
  Smart analyzer for full JSON workflow.
  Extracts ONLY what planner needs: architecture, routing logic, key modules, data flow, session pattern.
  Skips node-level boilerplate and redundant detail.
  UUID → JSON → ~1.5KB planner-ready summary (~30x compression).
version: 3.1.0
author: Hermes Agent
---

# n8n-workflow-analyzer v3.1

## Purpose
When planner fetches a workflow via webhook_wrapper (JSON >100KB possible),
this extracts ONLY planner-relevant info: architecture, router + conditions,
module-level structure, data flow, session/storage, AI integration, credential types.

## What planner needs (NOT a node inventory)

| Planner Need | Analyzer Extracts |
|-------------|-------------------|
| Architecture pattern | Hub-and-Spoke / AI Agent Hub / Pipeline / Branch |
| Core routing logic | Switch conditions — WHAT each branch handles |
| Key modules | Functional blocks named by ACTUAL node names (not index guessing) |
| Data flow topology | Trigger → Router → each branch's first nodes |
| Session management | AI Memory nodes + session storage tables |
| Storage | What's stored where (table name, operation type) |
| AI integration | Models, agents, memories, tool counts |
| Credentials needed | Types only (telegramApi, openAiApi) — NEVER real names/IDs |

## What planner does NOT need
- Every node name and config
- Sticky notes, positions, duplicate configs
- Tool sub-nodes counted separately
- Credential secrets or real names
- Connection edges that don't affect topology

## Usage
```bash
python3 ~/.hermes/skills/n8n-builder/webhook_wrapper.py fetch <UUID> > /tmp/wf_<UUID>.json
python3 ~/.hermes/skills/n8n-workflow-analyzer/scripts/analyzer.py /tmp/wf_<UUID>.json
```

## Output Format

```
# Workflow: J.A.R.V.I.S.
ID: X0hXjTBvKAyw79CG • Nodes: 48

## Architecture
Pattern: Hub-and-Spoke (4 branches)
AIAgent tools: 5 (agentTools, httpRequestTools, etc.)

## Core Router
Node: Switch (Switch, 4 outputs)

## Modules (by branch)
### Module: Download Image
  Path: Download Image (tg:sendPhoto) → Fix File Extension (logic) → Format-image-output (set) → Text Response (tg:sendMessage)

### Module: Get Audio File
  Path: Get Audio File (tg:sendPhoto) → Format-voice-output (set) → J.A.R.V.I.S. (ai_agent) → If Audio Response (condition) → Split MSG (logic) → Text Response (tg:sendMessage) → Audio Response (tg:sendAudio)

### Module: Format-text-output
  Path: Format-text-output (set) → J.A.R.V.I.S. (ai_agent) → If Audio Response (condition) → Split MSG (logic) → Text Response (tg:sendMessage) → Audio Response (tg:sendAudio)

### Module: Download Document
  Path: Download Document (tg:sendPhoto) → Convert Doc (logic) → Format-doc-output (set) → J.A.R.V.I.S. (ai_agent) → If Audio Response (condition) → Split MSG (logic) → Text Response (tg:sendMessage) → Audio Response (tg:sendAudio)

## Data Flow
  [Receive Message] → [Switch]
  ├─ Branch 0 (Download Image): Download Image → Fix File Extension → Format-image-output
  ├─ Branch 1 (Get Audio File): Get Audio File → Format-voice-output → J.A.R.V.I.S.
  ├─ Branch 2 (Format-text-output): Format-text-output → J.A.R.V.I.S. → If Audio Response
  └─ Branch 3 (Download Document): Download Document → Convert Doc → Format-doc-output

## Session
- AI Memory: Window Buffer Memory

## AI Integration
- Agent(s): J.A.R.V.I.S.
- Model(s): gpt-4.1
- Memory: Window Buffer Memory

## Credentials (types only)
- openAiApi
- telegramApi

## Notes
- Router 'Switch' — customize conditions for new use case
- Trigger(s): Receive Message
- AI tools: toolHttpRequest: 2, toolSerpApi: 1, toolCalculator: 1
- Models: gpt-4.1
```

## Architecture Detection Rules

| Pattern | Detected When |
|---------|---------------|
| AI Agent Hub | No router + agent(s) + >= 3 tools |
| Hub-and-Spoke | Switch with >= 3 branches |
| Branch | Switch with 2 outputs (A/B) |
| Pipeline | No router or single path |
| Hub-and-Spoke (sub-workflow) | Switch + executeWorkflow nodes |

## Module Naming Strategy
Modules are named by the FIRST meaningful node in each router branch (never guessed by index).
1. First node with a meaningful name (not 'Switch', 'IF', 'Set', 'Code')
2. First unique behavior (ai_agent, data_read, etc.)
3. Router condition purpose as fallback

## Node Classification (behavior prefixes)
| Prefix | Node Types |
|--------|-----------|
| `tg_*` | telegram (sendMessage, sendPhoto, editMessageText, ...) |
| `data_*` | postgres, dataTable, googleSheets (read, write, query, ...) |
| `ai_*` | agent, lmChat*, memory*, tool* |
| `router` | switch |
| `condition` | if |
| `logic` | code |
| `set` | set / editFields |

## Credential Policy
NEVER output real credential names, IDs, or tokens. Only credential type keys
(telegramApi, openAiApi, postgres, openRouterApi, httpHeaderAuth, slackApi).

## Template Comparison Mode (Template Unavailable)

> **When the user asks "compare with template X" and the n8n template API is inaccessible** (self-hosted instance returns 400/404 on UUID).  
> Skip `webhook_wrapper.py` — cannot fetch.  
> Use **metadata-only** from `intake.yaml` → `similar_workflows_found` section.

### How to compare

```
1. Read template metadata from intake.yaml or ARCHITECTURE.md
2. Read our architecture from ARCHITECTURE.md (54 nodes)
3. Build comparison table: Pattern, Storage, Payment, Nodes, Language
4. Estimate: Feature overlap (~65-70%), Net rewrite (~60-70%)
5. Score: ~47/100 → "building from scratch was correct"
```

The final verdict must be **~47/100** — not high enough to say "import" but not low enough to say "waste". It's the **honest middle ground**.

## Live Workflow Audit via MCP (Runtime Analysis)

When auditing a LIVE workflow on n8n cloud (not static JSON), use this systematic approach:

### Step 1: Fetch both versions
```
get_workflow_details(workflowId)  → returns draft + activeVersion
```
Compare `versionId` vs `activeVersionId`. If different → production runs on older code.

### Step 2: Count nodes
- Draft nodes vs Active nodes → if active has MORE, the draft is behind
- If draft has MORE → draft has new features not yet published

### Step 3: Map connections from ACTIVE version (not draft!)
Build adjacency list from `activeVersion.connections`:
```python
for source, val in active_conns.items():
    for output_list in val.get('main', []):
        for conn in output_list:
            if conn: adj[source].append(conn['node'])
```

### Step 4: Find dead ends and orphans
- **Dead ends** = nodes with incoming but no outgoing (expected for terminal nodes like sendMessage)
- **Orphan connections** = switch nodes with empty output slots (features not wired)
- **Orphan nodes** = nodes with no incoming connections (except triggers)

### Step 5: Analyze switch nodes
For every switch node, compare `numberOutputs` parameter to actual connected outputs:
```
Switch "Callback Router" — 13 outputs, 12 connected → 1 empty (feature not built)
Switch "State Router" — 11 outputs, 4 connected → 7 empty (checkout states missing)
```

### Step 6: Check execution history
```
search_executions(workflowId, limit=10)  → recent runs
search_executions(workflowId, status=["error"])  → failures
get_execution(workflowId, executionId, includeData=true)  → full trace
```
Look for:
- `ExpressionExtensionError` → syntax issue in expressions (see n8n-patterns 20-telegram.md §17)
- `undefined` in callback_data → upstream $json reference missing
- Nodes with `executionStatus: "error"` → pinpoint exact failure

### Step 7: Categorize findings
| Category | What to check |
|----------|--------------|
| ✅ Working | Flows with full connection chains and recent success |
| ⚠️ Partial | Switch outputs connected but downstream incomplete |
| ❌ Missing | Switch outputs empty (feature buttons exist but no logic) |
| 🐛 Bugs | Error executions, undefined values, orphan nodes |

### Pitfall: Draft ≠ Active
The draft (latest edit) and active (published) versions can differ significantly. ALWAYS analyze the active version for runtime behavior. The draft shows what's been edited but not yet deployed.

## n8n MCP Workflow Authoring — Critical Pitfalls

When BUILDING or EDITING n8n workflows via MCP tools (`update_workflow`, `updateNodeParameters`):

### Set Node v3.4 Mode/Parameter Mismatch (CRITICAL)

| `mode` | Correct Parameter | WRONG Parameter (produces defaults) |
|--------|-------------------|--------------------------------------|
| `"raw"` | `jsonOutput` (string, JSON expression) | `assignments` — **silently ignored**, outputs `my_field_1: "value"` |
| `"manual"` | `assignments.assignments[]` array | `jsonOutput` — **silently ignored** |

**Symptom**: Node outputs `{"my_field_1":"value","my_field_2":1}` instead of your expected fields.
**Fix**: Match parameter to mode. For `mode: "raw"` use `jsonOutput`:
```json
{ "mode": "raw", "jsonOutput": "={{ { field: $json.value } }}" }
```
Full error transcripts, correct/incorrect JSON examples, and pin data templates: `references/mcp-authoring-pitfalls.md`.

### Switch Node v3.4 Rules Structure

Wrong: `rules: { rules: [...] }` → validation warning `SWITCH_WRONG_RULES_KEY`
Right: `rules: { values: [...] }`

Each rule condition MUST include `combinator: "and"`:
```json
{ "conditions": { "combinator": "and", "conditions": [...] } }
```

### MCP Tool Operation Types

| Operation | Use For | Pitfall |
|-----------|---------|---------|
| `updateNodeParameters` | Replace full `parameters` object | ✅ Works reliably |
| `setNodeParameter` | Target specific field via `path` | ❌ `path: "parameters"` rejected as "unsafe" |
| `removeNode` / `addNode` | Delete + recreate node | Use when updateNodeParameters fails |

### Serialization Limits

- `typeVersion` must be **number** (e.g. `3.4`), not string `"3.4"`
- Large `operations` arrays (10+ items) may be serialized as string instead of object — split into smaller batches
- `\n` in JSON string values can break MCP serialization — use `\\n` or avoid newlines in expressions

## Tested On
| Workflow | Nodes | Result | Compression |
|----------|-------|--------|-------------|
| WEEX Quant AI Agent | 57 | AI Agent Hub (33 tools) → 1KB | 68x |
| Multi-Dept Support Bot | 52 | Hub-and-Spoke (5 branches) → 1.8KB | 21x |
| Voice Assistant Bot | 18 | Branch (A/B) → 1KB | 15x |
| J.A.R.V.I.S. Bot | 48 | Hub-and-Spoke (4 branches) → 1.2KB | 34x |
| GiggleGPT Bot | 27 | Hub-and-Spoke (8 branches) → 1.8KB | 28x |
| **Template Comparison (meta-only)** | **0 (no fetch)** | **→ 2KB** | **metadata → 30x** |
| **Average** | **40** | | **~30x compression** |
