# Pitfall: Postgres typeVersion 2 vs 2.6 Mismatch

## Symptoms
Postgres query fails with `relation "orders" does not exist` (or any
`"<table>" does not exist`) even though the table clearly exists in the
database.

Other Postgres nodes in the same workflow work fine.

## Root Cause
n8n Postgres v2.0 and v2.2+ (up to v2.6) use **different database
connections** even when they share the same credential name. The v2
nodes hit a database instance/schema that lacks your tables, while v2.6
nodes hit the correct one.

## Detection
```
get_workflow_details → scan all nodes for type="n8n-nodes-base.postgres"
                         check each node's typeVersion
any mix of 2.0 and 2.6  →  problem
```

## Fix
Replace every v2 Postgres node with a v2.6 copy:
1. Term: `removeNode` the v2 node
2. Term: `addNode` a v2.6 node with identical parameters
3. Term: `addConnection` to reconnect inputs/outputs

Credentials auto-assign if the credential name matches an existing one
(check `autoAssignedCredentials` in the response).

## Prevention
When a workflow has *any* Postgres v2.6 node already, always create new
Postgres nodes at v2.6 to stay consistent.

---

# Pitfall: queryReplacement with shifted $json (session-read upstream)

## Symptoms
Postgres `executeQuery` with `$1` parameter fails with:
```
Query Parameters must be a string of comma-separated values or an array of values
```
OR returns `0` / NaN because the regex fallback triggers on missing data.

## Root Cause
The `queryReplacement` expression references `$json.callback_query.data` (or
similar trigger data), but by the time the Postgres node executes, `$json` has
shifted to the output of a **session-read**, **DataTable-get**, or any node that
queries a different data source upstream.

Example chain:
```
🔀 Admin Action Router → 🔍 Get Admin Comment → 📦 Reject Order with Comment
                                                        ↑
                                          $json = session data {user_id, state, ...}
                                          $json.callback_query = undefined!
```

The `queryReplacement` tries `$json.callback_query.data.match(...)` on session
data → undefined → expression error or NaN.

## Fix
Reference the **specific upstream node** that has the order ID, not `$json`:

```typescript
// ❌ Shifted context — $json is session data, not trigger data
queryReplacement: "={{ parseInt($json.callback_query.data.replace('admin_rj_','')) }}"

// ✅ Explicit reference to the node that extracted order_id
queryReplacement: "={{ parseInt($('📝 Process Reject Comment').first().json.order_id) || 0 }}"
```

## Prevention
**Never use `$json` in Postgres `queryReplacement` when the node sits after a
session-read, DataTable-get, or any node that queries a different data source.**
Always reference the specific upstream node by name: `$('NodeName').first().json.field`.

This applies to ANY `queryReplacement`, not just reject flows — any Postgres
node in a multi-step pipeline where `$json` context may have shifted.

---

# Pitfall: Aggregate node typeVersion 2 does not exist

## Symptoms
An `n8n-nodes-base.aggregate` node has empty `parameters: {}` — no
`aggregate` mode selected. It passes no data and silently produces no
output.

## Root Cause
`aggregate` only has typeVersion **1**. Calling `get_node_types` for
v2 returns: `Version '2' not found for node
'n8n-nodes-base.aggregate'`.  A node created at v2 has zero valid
parameters and never executes.

## Fix
- `removeNode` the broken v2 aggregate
- `addNode` a v1 aggregate with `aggregate: "aggregateAllItemData"`
  (or `"aggregateIndividualFields"`)
- reconnect

---

# Pitfall: Column name mismatch — `weight` vs `weight_g`

## Symptoms
Postgres query `SELECT product_name, weight ... FROM order_items` fails
with `column item.weight does not exist`, but the query looks correct.

## Root Cause
The table `order_items` uses `weight_g` (grams) as the column name, not
`weight`. This is a schema-naming convention column. The subquery in the
`items_summary` field of the main query also references `item.weight`.

## Fix
Change column references from `weight` to `weight_g`:
```sql
-- ❌ Before
SELECT product_name, weight, quantity, price FROM order_items

-- ✅ After
SELECT product_name, weight_g, quantity, price FROM order_items

-- ✅ Also fix in subqueries
(SELECT string_agg(item.product_name || ' (' || item.weight_g || 'g) × ' ...
```

## Prevention
Always check the actual table schema before writing Postgres queries.
Look at `INSERT` or `CREATE TABLE` nodes in the same workflow for the
canonical column names.

---

# Pitfall: `items_summary` with subquery eliminates need for Aggregate + Code

## Problem
The photo route had this unnecessarily complex pipeline:
```
🔍 Get Pending Order (main query with order data)
  → 🔍 Get Items for Pending Order (fetch items separately)
  → 📊 Aggregate Items (combine items rows into arrays)
  → 📝 Build Receipt Caption (reference aggregate output)
```

But `🔍 Get Pending Order` already had a subquery producing
`items_summary` in the SQL. The Aggregate + Items chain was redundant.

## Fix
Simplify by referencing `items_summary` directly:
```
🔍 Get Pending Order (already has items_summary in output)
  → 📝 Build Receipt Caption (use $('...').first().json.items_summary)
```

Remove the now-redundant Get Items and Aggregate nodes (and their
connections).

## Pattern
When a parent Postgres query already produces a formatted aggregate
via subquery (`string_agg`, `json_agg`), the child "fetch items +
aggregate" chain is redundant. Reference the parent's pre-formatted
field instead.

---

# Pitfall: update_workflow edit-conflict

## Symptoms
```
error: "Cannot modify workflow while it is being edited by a user
in the editor."
```

## Fix
Wait 2–3 seconds and retry. The editor lock releases quickly once
the UI tab is closed. If persistent, ask the user to close/refresh
their n8n Editor tab.
