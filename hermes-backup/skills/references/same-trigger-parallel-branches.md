# Same-Trigger Parallel Branches (SDK Pattern)

## Problem

You have one trigger (e.g. `Telegram Trigger`) that needs to feed **two parallel pathways** that converge on a common downstream node. Standard chaining would multiply items: `trigger.to(nodeA.to(nodeB.to(converge)))` runs nodeB once per item from nodeA, not once.

## Solution — `.add(trigger).to(...) .add(trigger).to(...) .add(converge)`

Tell the SDK both branches originate from the same trigger by calling `.add(trigger).to(...)` twice, then `.add(converge)` to collect the merge point:

```typescript
import { workflow, trigger, node, expr } from '@n8n/workflow-sdk';

const tg = trigger({
  type: 'n8n-nodes-base.telegramTrigger',
  version: 1.3,
  config: { name: 'Telegram Trigger', parameters: { updates: ['message', 'callback_query'] } }
});

const branchA = node({ type: 'n8n-nodes-base.telegram', version: 1.2, config: { name: 'Answer Callback Query', ... } });

const branchB = node({ type: 'n8n-nodes-base.code', version: 2, config: { name: 'Extract Input Data', ... } });

const converge = node({ type: 'n8n-nodes-base.dataTable', version: 1.1, config: { name: 'Get Session', ... } });

export default workflow('id', 'name')
  // Branch 1: Trigger → branchA → converge
  .add(tg)
  .to(branchA.to(converge))
  // Branch 2: Trigger → branchB → converge (same trigger, isolated item stream)
  .add(tg)
  .to(branchB.to(converge));
```

## How it works

- Each `.add(tg)` creates a **separate connection** from the trigger to a branch.
- The trigger fires once; both branches receive the **same input item independently**.
- Each item goes down exactly one branch path — no multiplication.
- The converge node receives two independent inputs via n8n's multi-input system.

## Key detail: `.add()` vs `.to()`

| Method | What it does |
|--------|-------------|
| `.to(child)` | Wires a linear chain downstream from the current node |
| `.add(parent)` | Declares a new entry point for a separate chain segment. Use when adding a parallel branch starting from an already-declared node. |

Without the second `.add(tg)`, this would be equivalent to:

```
❌ tg.to(branchA.to(converge)).to(branchB.to(converge))  // branchB runs after converge, wrong!
```

## When to use this pattern

- **Bot workflows**: single Telegram/webhook trigger → Answer Callback + Extract Data → merge at Session lookup
- **Webhook processing**: receive payload → validate headers + parse body → merge
- **Fan-out**: one trigger → N independent parallel data sources → merge

## Frequently confused with: independent triggers

The SDK's standard parallel pattern declares **two separate triggers** when they're truly independent (e.g. a webhook AND a schedule). Same-trigger branching is for **one trigger, multiple parallel consumers**:

```typescript
// ❌ Independent triggers — wrong for same-trigger fan-out
.add(triggerA).to(branchA)
.add(triggerB).to(branchB)

// ✅ Same-trigger fan-out — correct
.add(tg).to(branchA.to(converge))
.add(tg).to(branchB.to(converge))
```

## Runtime behavior

- Both branches execute in the same execution context
- The converge node waits for ALL upstream branches to finish before running
- If branchA returns N items and branchB returns M items, converge sees N+M items (append) or pairs them (combine by position), depending on the converge node's mode
