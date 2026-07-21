# Hermes Memory Architecture — Deep Dive

How the memory system works under the hood, based on source-code tracing
of `hermes-agent` (agent_init.py, tool_executor.py, memory_manager.py,
memory_tool.py, model_tools.py, system_prompt.py, context_breakdown.py).

## Initialization Flow (`agent_init.py`)

```
skip_memory=True? → _memory_enabled = False, no store, no manager
skip_memory=False → read memory config from config.yaml
                     ↓
  _memory_enabled = mem_config.get("memory_enabled", False)
  _user_profile_enabled = mem_config.get("user_profile_enabled", False)
                     ↓
  if _memory_enabled or _user_profile_enabled:
      → MemoryStore loaded from disk (MEMORY.md / USER.md files)
  else:
      → _memory_store stays None (built-in memory tool breaks)
                     ↓
  provider = mem_config.get("provider", "")
  if provider:
      → _memory_manager = MemoryManager()
      → try load_memory_provider(provider_name)
            ↓
         Scans bundled: plugins/memory/<name>/
         Then user: $HERMES_HOME/plugins/<name>/
            ↓
         If __init__.py found with register(ctx) or MemoryProvider class:
            → instantiate, add to manager
            → if manager has providers: initialize_all()
                     ↓
  inject_memory_provider_tools(agent)
      → appends external provider tool schemas to agent.tools[]
```

## Built-in `memory()` Tool Registration (`memory_tool.py`)

```python
check_fn=check_memory_requirements  # ← ALWAYS returns True
```

This means: **the built-in `memory()` tool schema is always presented to the LLM, regardless of any config setting.** The `check_fn` does NOT read `memory_enabled` from config.

When called with `store=None` (because `_memory_enabled = False`):
→ returns `{"success": false, "error": "Memory is not available..."}`

The `memory` toolset (containing only `"memory"` tool) MUST stay in
`platform_toolsets` because of the injection gate (see below).

## External Provider Tool Injection (`inject_memory_provider_tools`)

```python
if (
    "memory" not in existing_tool_names          # built-in tool missing?
    and not memory_provider_tools_enabled(...)    # AND no "memory" in enabled_toolsets?
):
    return 0  # → DON'T inject external tools!
```

**This is the critical gate:** If the built-in `memory` tool is removed from the
toolset (e.g. via `hermes tools disable memory` or removing it from
`platform_toolsets`), the external provider's 37 tools are ALSO not injected.

`memory_provider_tools_enabled` returns True if:
- `enabled_toolsets` is None (all tools enabled → rarely the case)
- `"memory"` is in `enabled_toolsets` list
- Any resolved toolset contains `"memory"` tool

## Tool Dispatch (`tool_executor.py`)

Two paths for memory-related tools:

1. **Built-in `memory()` tool** (line ~1215):
   - Calls `memory_tool(store=agent._memory_store)`
   - After call, mirrors to external provider via `notify_memory_tool_write()`
   - Mirroring only works if the built-in write SUCCEEDED
   - When `_memory_store is None` → error → no mirroring

2. **External provider tools** (line ~1361):
   - Any tool name NOT in built-in dispatch but IN `_memory_manager.has_tool(name)`
   - → `agent._memory_manager.handle_tool_call(name, args)`
   - All 37 `mnemosyne_*` tools go through this path

## `notify_memory_tool_write` Mirroring

Only fires on **committed, successful** built-in writes:
```python
if not self._memory_tool_result_succeeded(tool_result):
    return  # ← stops if built-in failed
```

This means when `memory_enabled: false`, the built-in `memory()` tool:
1. Returns error (because `_memory_store is None`)
2. Does NOT mirror to external provider
3. LLM sees both `memory()` (error-prone) and `mnemosyne_*` (working) tools

## Memory Content Injection (`system_prompt.py` + `context_breakdown.py`)

MEMORY.md / USER.md content is injected into the system prompt ONLY when:
- `agent._memory_store is not None` AND
- `agent._memory_enabled` (for memory) / `_user_profile_enabled` (for user)

External provider context is injected via `agent._memory_manager.build_system_prompt()`
when the manager has providers and they return non-empty blocks.

## Read-Only Filesystem Constraint

In container deployments (Docker), the Hermes application code under
`~/.hermes/hermes-agent/` may be on a read-only filesystem. Patching
`check_memory_requirements` in `memory_tool.py` is impossible from within
the container. All configuration must be done via `config.yaml` and `.env`.

## Common Failure Modes

| Symptom | Root Cause |
|---------|-----------|
| `Provider: <X>` but `Plugin: NOT installed ✗` | Broken symlink or missing package |
| External provider tools not showing up | `memory` toolset disabled in platform_toolsets |
| `memory()` tool always returns error | `memory_enabled: false` and no fallback |
| Memory not persisted across restarts | Provider plugin not initialized (needs `/reset`) |
| Provider shows "Available: True" in test but not in Hermes | Plugin was loaded in a test process, not Hermes venv |
