# Schema-First Pattern — Create Tables Before Queries

## The Trap

Postgres nodes fail with `relation "settings" does not exist` when the workflow references tables that haven't been created yet. The schema must exist *before* the production webhook flow runs.

## Fixed Pattern

**Step 1: Create a setup node** (temporary, disconnected)

Add a Postgres `executeQuery` node with all CREATE TABLE IF NOT EXISTS + seed INSERT statements attached to the trigger (or any startable node). Pin-data test it once, then remove.

```json
{
  "node": {
    "name": "🔧 Create Tables",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 2.6,
    "parameters": {
      "operation": "executeQuery",
      "query": "CREATE TABLE IF NOT EXISTS settings (\n    key VARCHAR(100) PRIMARY KEY,\n    value TEXT\n);\n\nCREATE TABLE IF NOT EXISTS orders (\n    id SERIAL PRIMARY KEY,\n    order_code VARCHAR(20) UNIQUE NOT NULL,\n    user_id INT REFERENCES users(id),\n    total BIGINT NOT NULL,\n    status VARCHAR(30) DEFAULT 'pending',\n    shipping_name VARCHAR(100),\n    shipping_phone VARCHAR(20),\n    shipping_address TEXT,\n    shipping_postal VARCHAR(20),\n    tracking_code VARCHAR(100),\n    notes TEXT,\n    created_at TIMESTAMP DEFAULT NOW(),\n    updated_at TIMESTAMP DEFAULT NOW()\n);\n\nINSERT INTO settings (key, value)\nVALUES \n    ('order_counter', '1'),\n    ('admin_card_number', '6037-9975-1234-5678'),\n    ('admin_telegram_id', '943724562'),\n    ('order_prefix', 'CB-')\nON CONFLICT (key) DO NOTHING;"
    },
    "credentials": {"postgres": {"id": "<CREDENTIAL_ID>", "name": "<CREDENTIAL_NAME>"}}
  }
}
```

**Step 2: Pin-data test**

```python
pinData = {
  "📱 Telegram Trigger": [{"json": {"update_id": 1, "message": {
    "message_id": 1, "from": {"id": 1, "is_bot": false, "first_name": "Test"},
    "chat": {"id": 1, "type": "private"}, "date": 1700000000, "text": "test"
  }}}]
}
```

Call `test_workflow(workflowId, pinData, triggerNodeName="📱 Telegram Trigger")`. Status should be `success`.

**Step 3: Remove the node**

```json
{"type": "removeNode", "nodeName": "🔧 Create Tables"}
```

## Reference Tables for Coffee-Bean-Bot

| Table | Key Columns | Seed data |
|-------|-------------|-----------|
| `users` | id, telegram_id (UNIQUE), first_name, phone, address, postal_code, is_admin | — |
| `products` | id, name, category, price_250..1000, stock_250..1000, is_active | Already exists from earlier task |
| `orders` | id, order_code (UNIQUE), user_id → users.id, total, status, shipping_*, tracking_code | — |
| `order_items` | id, order_id → orders.id, product_id → products.id, product_name, weight, quantity, price | — |
| `settings` | key (PK), value | `order_counter=1`, `admin_card_number`, `admin_telegram_id`, `order_prefix=CB-` |

## When to Do This

- **Before first production execution** of any flow that reads/writes Postgres
- **After adding new Postgres queries** that reference tables never queried before
- **Only once per environment** — subsequent runs should skip CREATE TABLE
