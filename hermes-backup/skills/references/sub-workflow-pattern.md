# Sub-Workflow Modular Architecture Pattern

## Purpose
Break a monolithic n8n workflow into a caller (main) + one or more sub-workflows (callees). Each sub-workflow is a stand-alone workflow triggered by `Execute Workflow Trigger` and called via `Execute Sub-workflow` node.

## SDK Components

### 1. Sub-workflow Trigger (callee side)
```typescript
const entry = trigger({
  type: 'n8n-nodes-base.executeWorkflowTrigger',
  version: 1.2,
  config: {
    name: '⚡ My Entry',
    parameters: { inputSource: 'passthrough' }
  }
});
```
- `inputSource: 'passthrough'` — all data from the calling workflow is passed through as-is. Use `workflowInputs` if you want typed input validation.
- This trigger type has **no production triggers** — it only fires when called by another workflow.

### 2. Execute Sub-workflow node (caller side)
```typescript
const execNode = node({
  type: 'n8n-nodes-base.executeWorkflow',
  version: 1.3,
  config: {
    name: '⚙️ Execute Admin',
    parameters: {
      source: 'database',           // workflow stored in n8n DB
      workflowId: {                  // Resource Locator
        __rl: true,
        mode: 'id',
        value: '<workflow-id>'      // replace with actual ID
      },
      mode: 'once',                 // run once with all items
      workflowInputs: {              // input mapping
        mappingMode: 'defineBelow',
        value: null
      },
      options: {
        waitForSubWorkflow: true    // block until sub-workflow finishes
      }
    }
  }
});
```

## Credential Handling

Credentials **do NOT flow through** from parent to sub-workflow. Each sub-workflow must define its own credentials:

```typescript
const telegramCred = newCredential('credential_name', 'credential_id');
const postgresCred = newCredential('log_level', 'dHPJgD849RqTdON9');
```

Then reference them in each node:
```typescript
credentials: { postgres: postgresCred }
credentials: { telegramApi: telegramCred }
```

## Refactoring Monolithic → Modular (step-by-step)

### Phase 1: Create Sub-workflow
1. Write SDK code with `executeWorkflowTrigger` + all sub-module nodes
2. Validate with `validate_workflow`
3. Create with `create_workflow_from_code` (max 20 nodes per create)
4. Note the new workflow ID from the response

### Phase 2: Update Main Workflow
The correct operation sequence is critical:

```
Step 1: removeConnection — disconnect old nodes from router/trigger
Step 2: removeNode — delete old nodes from main workflow  
Step 3: addNode — add Execute Sub-workflow node (reference sub-workflow ID)
Step 4: addConnection — wire router outputs → Execute Sub-workflow
```

**Important:** The removeNode operation uses `nodeName` (NOT `name`):
```json
{ "nodeName": "🔀 Old Router", "type": "removeNode" }
```

### Phase 3: Publish Sub-workflow
Sub-workflows must be **published** (activated) before they can be called in production mode by the parent. Manual/test execution works without publishing.

## Pattern: 16-output Admin Router

When the sub-workflow handles many callback_data patterns, use an expression-mode Switch:
```typescript
output: expr(`{{ $json.callback_query.data == 'admin_dashboard' ? 0 :
   $json.callback_query.data == 'admin_orders' ? 1 :
   $json.callback_query.data.startsWith('admin_order_confirm_') ? 2 :
   ...
   15 }}`)
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Sub-workflow not published | Execute node fails in production | Activate sub-workflow via n8n UI or `publish_workflow` |
| Missing credentials in sub-workflow | Postgres/Telegram auth errors | Add `newCredential(name, id)` in sub-workflow SDK code |
| `removeNode` with `name` instead of `nodeName` | Validation error "operation 0.nodeName: Required" | Use `nodeName` field (not `name`) |
| `inputSource` not set | Sub-workflow gets empty `$json` | Set `inputSource: 'passthrough'` on trigger |
| Old nodes disconnected but not removed | DISCONNECTED_NODE warnings | Add `removeNode` operations after `removeConnection` |
| SDK `.to()` on Switch routes ALL branches to output 0 | All sub-modules fire on output 0 regardless of expression | SDK `.to()` uses **`.onCase()` internally for different outputs**. When using `.add(router).to(nodeA).add(router).to(nodeB)` — both go to output 0. Fix: create Switch via SDK as v1, then **use `update_workflow` to re-create it as v3.4** with `removeConnection` + `removeNode` + `addNode` + `addConnection` steps. Or drop SDK entirely for the routing layer and build via `update_workflow` operations. |
| Switch v1 max 4 outputs | `INVALID_OUTPUT_INDEX` when connecting to output 5+ | SDK `create_workflow_from_code` always creates Switch at typeVersion 1. Must: (1) remove connections, (2) remove node, (3) addNode with `typeVersion: 3.4` and `numberOutputs: 16`, (4) reconnect all branches |
| New nodes auto-assign wrong credentials | Telegram nodes get `@natentestbot` instead of your bot credential | Check `autoAssignedCredentials` in update response; follow with `setNodeCredential` operations |
| `create_workflow_from_code` 20-node limit | Create fails for workflows >20 nodes | Create skeleton (≤15 nodes), then add remaining modules via `update_workflow` + `addNode` + `addConnection` in batches of 30-40 ops |

### ⚠️ Telegram `resource` discriminator

All Telegram nodes (sendMessage, editMessageText) **must** have `resource: 'message'` in parameters — otherwise they produce `INVALID_PARAMETER` warnings ("Missing discriminator `parameters.resource`"):

```typescript
parameters: {
  resource: 'message',       // ← REQUIRED
  operation: 'sendMessage',  // or 'editMessageText'
  chatId: expr('...'),
  text: '...'
}
```

### ⚠️ `update_workflow` router-rebuild pattern (Switch v1 → v3.4)

When re-creating a Switch node with a higher typeVersion via `update_workflow`:

```text
Step A: removeConnection — disconnect ALL existing router outputs
Step B: removeNode — delete the old Switch (nodeName not name)
Step C: addNode — create new Switch with typeVersion: 3.4, numberOutputs: 16
Step D: addConnection — reconnect Admin Gate → Router
Step E: addConnection — reconnect Router[0]..[N] → leaf nodes
```

All 7 ops in a single batch call work; the response confirms 12+ applied operations without issue.

## SDK Import
```typescript
import { workflow, node, trigger, expr, ifElse, switchCase, newCredential } from '@n8n/workflow-sdk';
```
