# Tool Usage Reference — n8n-planner (v3.0)

> Load with: `skill_view(name='n8n-planner', file_path='references/tool-usage.md')`

---

## 1. Webhook: workflowid_to_jsonfile (Fetch)

**Purpose:** Fetch the full JSON of a workflow by its database UUID.

**Method:** `webhook_wrapper.py fetch` (Python wrapper, dual-mode)  
**Path:** `/home/hermeswebui/.hermes/skills/n8n-builder/webhook_wrapper.py`

این ابزار UUIDای که از خروجی **search** (فیلد `id`) به دست اومده رو می‌گیره و JSON کامل ورک‌فلو رو برمی‌گردونه.

**Syntax:**
```python
terminal(command="python3 /home/hermeswebui/.hermes/skills/n8n-builder/webhook_wrapper.py fetch 550e8400-e29b-41d4-a716-446655440000")
```

یا برای backward compatibility:
```python
terminal(command="python3 /home/hermeswebui/.hermes/skills/n8n-builder/webhook_wrapper.py 550e8400-e29b-41d4-a716-446655440000")
```

**Response:**
```json
{
  "error": false,
  "code": 0,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "data": { ... full workflow JSON with nodes, connections, credentials ... }
}
```

**Response includes:** Full workflow JSON with nodes, connections, credentials, trigger settings.

**Use case:** کاربر گفت "این ورک‌فلو رو که توی intake هست ببین چیه" یا UUID از search به دست اومده و باید JSON کاملش رو ببینیم.

> ⚠️ **نکته:** UUID از `webhook_wrapper.py search` میاد (فیلد `id`). این UUID از نوع **database** هست، نه n8n short ID.
>
> ⚠️ اگر webhook 404 برگردوند، به کاربر بگو توی n8n یکبار Execute کنه تا فعال بشه.

---

## 2. MCP: search_nodes

**Purpose:** Find n8n node types by service name, trigger type, or utility function.

```python
# Search one or more services (pass array)
mcp_n8n_mcp_search_nodes(queries=["telegram"])
mcp_n8n_mcp_search_nodes(queries=["postgres", "data table", "mysql"])
mcp_n8n_mcp_search_nodes(queries=["http request", "schedule trigger", "switch"])
mcp_n8n_mcp_search_nodes(queries=["openrouter", "langchain agent", "memory"])
mcp_n8n_mcp_search_nodes(queries=["slack", "gmail", "discord"])
mcp_n8n_mcp_search_nodes(queries=["code", "set", "if", "merge", "loop"])
```

**Output:** Node IDs, resource/operation discriminators, type versions.

---

## 3. MCP: get_node_types

**Purpose:** Get exact parameter schemas for confirmed nodes.

```python
# By node ID only
mcp_n8n_mcp_get_node_types(nodeIds=["n8n-nodes-base.telegram"])

# With discriminators (more precise)
mcp_n8n_mcp_get_node_types(nodeIds=[
  {"nodeId": "n8n-nodes-base.telegram", "resource": "message", "operation": "sendMessage"},
  {"nodeId": "n8n-nodes-base.switch"},
  {"nodeId": "n8n-nodes-base.httpRequest", "operation": "POST"}
])
```

**Output:** Parameter names, types, required fields, options for each resource/operation.

---

## 4. MCP: get_workflow_best_practices

**Purpose:** Research design patterns and common pitfalls.

```python
# List all available techniques
mcp_n8n_mcp_get_workflow_best_practices(technique="list")

# Load a specific technique
mcp_n8n_mcp_get_workflow_best_practices(technique="chatbot")
mcp_n8n_mcp_get_workflow_best_practices(technique="scheduling")
mcp_n8n_mcp_get_workflow_best_practices(technique="form_input")
mcp_n8n_mcp_get_workflow_best_practices(technique="data_persistence")
mcp_n8n_mcp_get_workflow_best_practices(technique="triage")
mcp_n8n_mcp_get_workflow_best_practices(technique="content_generation")
mcp_n8n_mcp_get_workflow_best_practices(technique="data_extraction")
mcp_n8n_mcp_get_workflow_best_practices(technique="notification")
mcp_n8n_mcp_get_workflow_best_practices(technique="human_in_the_loop")
mcp_n8n_mcp_get_workflow_best_practices(technique="scraping_and_research")
mcp_n8n_mcp_get_workflow_best_practices(technique="enrichment")
mcp_n8n_mcp_get_workflow_best_practices(technique="data_analysis")
mcp_n8n_mcp_get_workflow_best_practices(technique="data_transformation")
```

---

## 5. MCP: get_sdk_reference

**Purpose:** Optional — get SDK patterns for code/expression nodes.

```python
# Full reference
mcp_n8n_mcp_get_sdk_reference()

# Specific section
mcp_n8n_mcp_get_sdk_reference(section="expressions")
mcp_n8n_mcp_get_sdk_reference(section="functions")
mcp_n8n_mcp_get_sdk_reference(section="guidelines")
```

---

## 6. File Operations

```python
# Read intake file
read_file(path='/workspace/n8n-wfb-coffee-bot-intake.yaml')

# Write plan file
write_file(
  path='/workspace/n8n-wfb-coffee-bot-plan.yaml',
  content="# ..."
)
```

---

## ✅ Quick Reference Card

| Goal | Tool | Exact Call |
|------|------|-----------|
| Fetch workflow JSON by UUID | Webhook wrapper | `terminal("python3 /home/hermeswebui/.hermes/skills/n8n-builder/webhook_wrapper.py fetch <UUID>")` |
| Search workflows by query+category | Webhook wrapper | `terminal("python3 /home/hermeswebui/.hermes/skills/n8n-builder/webhook_wrapper.py search --query '...' --category '...'")` |
| Search for nodes | MCP | `mcp_n8n_mcp_search_nodes(queries=["service"])` |
| Get node param schemas | MCP | `mcp_n8n_mcp_get_node_types(nodeIds=["node.id"])` |
| Research best practices | MCP | `mcp_n8n_mcp_get_workflow_best_practices(technique="list")` |
| SDK reference | MCP | `mcp_n8n_mcp_get_sdk_reference()` |
| Read intake YAML | read_file | `read_file(path="...")` |
| Write plan YAML | write_file | `write_file(path="...", content="...")` |

---

## ❌ What NOT to Do

```python
# DON'T call these:
mcp_n8n_mcp_search_workflows()           # ❌ Already in intake
mcp_n8n_mcp_list_credentials()           # ❌ Intake's job
mcp_n8n_mcp_create_workflow_from_code()  # ❌ Builder's job
mcp_n8n_mcp_update_workflow()            # ❌ Builder's job
mcp_n8n_mcp_execute_workflow()           # ❌ Not your phase
mcp_n8n_mcp_test_workflow()              # ❌ QA's job
mcp_n8n_mcp_validate_workflow()          # ❌ Not your phase
mcp_n8n_mcp_publish_workflow()           # ❌ Not your phase
web_search()                             # ❌ Not needed
```
