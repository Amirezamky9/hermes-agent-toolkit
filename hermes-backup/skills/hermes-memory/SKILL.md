---
name: hermes-memory
description: "Install, configure, and verify third-party memory providers for Hermes Agent (mnemosyne, honcho, mem0, hindsight, supermemory, etc)."
version: 1.3.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, memory, plugins, mnemosyne, setup]
    related_skills: [hermes-agent]
---

# Hermes Memory Providers

Install and activate third-party memory backends for Hermes Agent. Replaces the built-in MEMORY.md/USER.md file-based memory with a plugin that provides vector search, knowledge graphs, and cross-session recall.

## ⚠️ Critical: Use Provider Tools, Not Legacy `memory()`

When a third-party memory provider (Mnemosyne, mem0, etc.) is active, **ALWAYS use the provider's tools** (e.g. `mnemosyne_remember`, `mnemosyne_recall`). **NEVER call the legacy `memory()` tool** — it is deprecated and will fail or produce no results.

Before any memory operation, verify the active provider with `mnemosyne_stats` (mnemosyne) or `hermes memory status`, then use that provider's API exclusively.

**Known upstream issues:** If `memory_enabled: false` doesn't hide the legacy tool, this is a tracked bug (#57793, #45422, #32624, #46108) — NOT a misconfiguration. See `references/legacy-memory-tool-issues.md` for the full issue tracker and why config-only fixes don't work.

## Architecture: The `memory` Toolset Paradox

The built-in `memory()` tool and the external provider's tools (e.g. 37 `mnemosyne_*` tools) have a critical dependency you MUST understand:

**The `memory` toolset MUST stay enabled in `platform_toolsets`** for external provider tools to be injected.

Why: `inject_memory_provider_tools()` in `memory_manager.py` checks:
```python
if (
    "memory" not in existing_tool_names
    and not memory_provider_tools_enabled(enabled_toolsets)
):
    return 0  # ← skips ALL external provider tools!
```

If you remove `memory` from `platform_toolsets` (or run `hermes tools disable memory`), the built-in tool disappears, AND the condition `"memory" not in existing_tool_names` becomes True. If no other toolset resolves to include `"memory"`, then `memory_provider_tools_enabled` returns False, and NONE of the external provider's tools are injected either.

**Bottom line: `hermes tools disable memory` kills ALL memory tools, including the provider plugin's.** The existing warning in Step 4 is correct — keep the `memory` toolset enabled even if you want to use only the external provider.

When `memory_enabled: false` (prevents built-in MemoryStore loading):
- The built-in `memory()` tool schema is STILL shown to the LLM by default (check_fn always returns True)
- Calling `memory()` returns an error (store=None)
- The error means `notify_memory_tool_write()` mirroring is SKIPPED — writes don't reach the external provider either
- The external provider tools DO work directly (e.g. `mnemosyne_remember`)
- The LLM learns to use the external provider tools over time

**But this leaves the useless built-in `memory()` tool in the LLM's sight, wasting context.**

### Verified Fix: Patch check_memory_requirements to Gate on memory_enabled

On source/pip installs where Hermes files are writable, you can patch `tools/memory_tool.py` so the built-in `memory()` tool is **hidden** from the LLM when `memory_enabled: false`:

```python
# In check_memory_requirements(), add this check BEFORE the "return True":
if not self.config.get("memory", {}).get("memory_enabled", True):
    return False
```

**Exact patch commands:**
```bash
# Find the file
find ~/.hermes -name "memory_tool.py" -path "*/tools/*" 2>/dev/null

# Locate check_memory_requirements — it's the function that returns True
grep -n "def check_memory_requirements\|return True" <path-to-memory_tool.py>

# Apply the patch: add the memory_enabled gate before the final return True
```

After patching:
- `memory_enabled: false` → built-in `memory()` tool **disappears** from LLM tool list entirely
- The `memory` toolset stays enabled → external provider tools still inject
- LLM sees only the provider's tools (`mnemosyne_remember`, `mnemosyne_recall`, etc.)
- No wasted context slots, no LLM confusion

**Container/read-only filesystem:** If Hermes is on a read-only overlay (some Docker deployments), this patch is not possible. Rely on `memory_enabled: false` + LLM learning to ignore the built-in tool.

For a reference of the full architecture tracing (init flow, tool dispatch, injection gate, notification chain), see `references/deep-dive.md`.

## Provider Catalog (Bundled)

These providers ship with Hermes and require only a pip install + symlink step:

| Provider | Package | Auth | Notes |
|----------|---------|------|-------|
| mnemosyne | `mnemosyne-hermes` | None (local) | 37 tools, local SQLite + vector + graph |
| mem0 | `hermes-mem0` | API key | Cloud vector memory |
| honcho | `hermes-honcho` | API key | Cloud structured memory |
| hindsight | `hermes-hindsight` | API key | Session reflection |
| byterover | `byterover-memory` | API key / local | Cross-platform sync |
| holographic | `hermes-holographic` | None (local) | Distributed vector memory |
| openviking | `viking-memory` | API key | Enterprise-grade |
| retaindb | `retaindb-memory` | API key | Cloud persistent store |
| supermemory | `supermemory` | Requires API key | Knowledge base memory |

Pip install + symlink pattern works for all of them.

## Prerequisites

- Hermes Agent installed (source or pip)
- `pip3` available in the same Python env Hermes uses
- Know where `hermes` binary lives: `which hermes` or find it under `~/.hermes/hermes-agent/`

## Installation Pattern (all providers)

### Step 1: Install the package

```bash
pip install <provider-package>
# Examples:
pip install mnemosyne-hermes        # mnemosyne (local SQLite + vector)
pip install hermes-honcho           # honcho (cloud)
pip install hermes-mem0             # mem0
```

For mnemosyne specifically, optional extras:
- `mnemosyne-memory[embeddings]` — local vector gen (~800 MB RAM)
- `mnemosyne-memory[all]` — local embeddings + local LLM consolidation (~1.5 GB)
- Core alone (~50 MB) needs remote embedding API

### Step 2: Link plugin into Hermes

Hermes discovers plugins from `~/.hermes/plugins/`, not pip metadata. The plugin
directory must be a real directory with `__init__.py` containing a `register(ctx)`
function or a class extending `MemoryProvider`.

```bash
# Remove any stale/broken link first
rm -rf ~/.hermes/plugins/<name>

# Verify the package is actually installed
python3 -c "import hermes_memory_provider; print(hermes_memory_provider.__file__)"

# Symlink the entire package directory
ln -sfn "$(python3 -c 'import pathlib, hermes_memory_provider; print(pathlib.Path(hermes_memory_provider.__file__).resolve().parent)')" ~/.hermes/plugins/<name>
```

Verify the link is valid (not broken):
```bash
ls -la ~/.hermes/plugins/<name>/    # trailing slash — must show files, not error
ls -la ~/.hermes/plugins/<name>/__init__.py  # must exist
readlink -f ~/.hermes/plugins/<name>  # must resolve to an existing path
```

### Step 3: Configure + activate

```bash
hermes config set memory.provider <provider-name>
hermes memory setup
```

### Step 4: Disable built-in memory

**DO NOT** `hermes tools disable memory` — this kills ALL memory tools including the plugin's.

Edit `~/.hermes/config.yaml`:

```yaml
memory:
  provider: <provider-name>
  memory_enabled: false      # disables MEMORY.md system
  user_profile_enabled: false # stops USER.md injection
```

### Step 5: Verify

```bash
hermes memory status          # should show provider as active
hermes <provider> stats       # provider-specific stats (if available)
```

Double-check the `memory` toolset is still enabled in `platform_toolsets`:
```bash
grep -A10 "platform_toolsets:" ~/.hermes/config.yaml | grep "memory"
# If "memory" is missing from both cli and telegram lists, add it back.
# The memory toolset MUST stay enabled for external provider tools to inject.
```

Provider-specific test (detached from Hermes runtime):
```python
from plugins.memory import load_memory_provider
p = load_memory_provider("mnemosyne")
print(p.name, p.is_available(), len(p.get_tool_schemas()), "tools")
```

### Step 6: Restart gateway

```bash
hermes gateway restart
# or systemctl --user restart hermes-gateway
```

## Provider-Specific Notes

### Mnemosyne

- **Package:** `mnemosyne-hermes` (wraps `mnemosyne-memory[embeddings]`)
- **Data dir:** `~/.hermes/mnemosyne/data/mnemosyne.db`
- **37 tools registered:** mnemosyne_remember, mnemosyne_recall, mnemosyne_shared_remember, mnemosyne_shared_recall, mnemosyne_shared_forget, mnemosyne_shared_stats, mnemosyne_sleep, mnemosyne_stats, mnemosyne_invalidate, mnemosyne_validate, mnemosyne_get, mnemosyne_triple_add, mnemosyne_triple_query, mnemosyne_triple_end, mnemosyne_remember_canonical, mnemosyne_recall_canonical, mnemosyne_model_card, mnemosyne_model_refresh, mnemosyne_scratchpad_write, mnemosyne_scratchpad_read, mnemosyne_scratchpad_clear, mnemosyne_export, mnemosyne_update, mnemosyne_forget, mnemosyne_import, mnemosyne_diagnose, mnemosyne_recall_diagnostics, mnemosyne_task_progress, mnemosyne_graph_query, mnemosyne_graph_link, mnemosyne_sync_push, mnemosyne_sync_pull, mnemosyne_sync_status, mnemosyne_persona_promote, mnemosyne_persona_demote, mnemosyne_persona_list, mnemosyne_persona_reinforce
- **Lifecycle hooks:** pre_llm_call (context injection), on_session_start, post_tool_call
- **Scratchpad API:** `scratchpad_write(content: str) → id` (ONE arg, not key+content), `scratchpad_read() → list[dict]`, `scratchpad_clear()`
- **CLI:** `hermes mnemosyne stats`, `hermes mnemosyne sleep`, `hermes mnemosyne export/import`
- **Docs:** https://github.com/mnemosyne-oss/mnemosyne → `docs/hermes-integration.md`

#### Embedding Setup (OpenAI)

```bash
# In ~/.hermes/.env — set these (user sets API key themselves):
MNEMOSYNE_EMBEDDING_API_URL=https://api.openai.com/v1
MNEMOSYNE_EMBEDDING_MODEL=text-embedding-3-small
# MNEMOSYNE_EMBEDDING_API_KEY=sk-xxx  ← user sets this
```

For multilingual (Persian/Arabic/etc):
```bash
MNEMOSYNE_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

#### Per-Topic Memory (Telegram)

Each Telegram topic = separate session. `scope='session'` (default) means memories are topic-isolated automatically.

- `remember("fact", scope="session")` — only in current topic
- `remember("fact", scope="global")` — visible across ALL topics
- Use `scope='global'` for user preferences, identity, cross-topic context
- Use `scope='session'` (default) for topic-specific work context

**Per-Topic Presets:** When user wants the agent to "know what this topic is for" across `/new` resets, store topic context as `scope='global'` memories with a `topic:<name>` prefix:

```python
from mnemosyne import Mnemosyne
m = Mnemosyne()
m.remember("topic:ریسرچ - این تاپیک برای تحقیق و تحلیل ارزهاست. پاسخ فارسی و تحلیلی باشه.", importance=0.9, source="preference", scope="global")
```

This way, when a new session starts in that topic, mnemosyne's context injection surfaces the topic purpose automatically.

**Configuring topic names:** Add topic names to `dm_topics` in config.yaml so Hermes labels sessions. Use Python + yaml for nested structures (terminal `hermes config set` can't handle arrays-of-objects):

```python
import yaml
from pathlib import Path
config_path = Path.home() / ".hermes" / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)
topics = config["gateway"]["platforms"]["telegram"]["extra"]["dm_topics"]
topics.append({"chat_id": "943724562", "thread_id": "123456", "name": "topic-name"})
with open(config_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
```

## Health Check Script

Run after installation to verify everything works end-to-end:

```python
from mnemosyne import Mnemosyne
m = Mnemosyne()

# Remember + Recall
rid = m.remember("test fact", importance=0.7, source="healthcheck")
results = m.recall("test fact", top_k=1)
assert len(results) >= 1, "Recall failed"

# Multilingual (use broader query — exact-match in different language may score low)
results_fa = m.recall("language preference", top_k=1)  # broader semantic query
assert len(results_fa) >= 1, "Multilingual recall failed"

# Update + Forget
m.update(rid, content="updated fact")
m.forget(rid)

# Scratchpad (API: write(content) → id, read() → list, clear())
sid = m.scratchpad_write("debug note")
assert m.scratchpad_read(), "Scratchpad read failed"
m.scratchpad_clear()

# CLI stats
import subprocess
subprocess.run(["hermes", "mnemosyne", "stats"], check=True)
```

## Pitfalls

- **Broken symlink is silent:** A symlink at `~/.hermes/plugins/<name>/` may exist but point to a non-existent target. `ls -la` shows a symlink-entry, but `ls -la ~/.hermes/plugins/<name>/` (trailing slash) fails with "No such file or directory". Always verify with `readlink -f ~/.hermes/plugins/<name>` or `ls -la ~/.hermes/plugins/<name>/`. If the target doesn't exist, `hermes memory status` shows `Plugin: NOT installed ✗`.
- **Plugin discovery is filesystem-based:** `load_memory_provider()` scans `$HERMES_HOME/plugins/<name>/` for `__init__.py` containing `register(ctx)` or a class extending `MemoryProvider`. The directory must exist as a real directory (not a broken symlink). The provider module must also be importable by the Hermes Python environment's `importlib`.
- **Read-only app filesystem:** In SOME container deployments (Docker unpacked overlay), Hermes source files are read-only. Patching `check_memory_requirements()` is NOT possible there. **But** if Hermes was installed via `pip install hermes-agent` (source install where `~/.hermes/hermes-agent/tools/memory_tool.py` is writable), the patch WORKS. Always check first: `ls -la ~/.hermes/hermes-agent/tools/memory_tool.py`. Rely on config-only changes only when the file is truly read-only.
- **Hermes binary not in PATH:** On some deployments (pip install to custom dir), `hermes` isn't in PATH. Use the full path: `~/.hermes/hermes-agent/hermes` or find with `find ~/.hermes -name hermes -type f`.
- **Symlink wrong Python:** If using a venv, the `python3 -c` auto-detect must run in the same env where the package is installed. Check with `python3 -c "import <package>; print(<package>.__file__)"`.
- **Re-symlink fails on stale `__pycache__`:** `ln -sfn` can't overwrite a directory with a symlink. Clean first: `rm -rf ~/.hermes/plugins/<name>/*` before re-running the symlink step. Happens on reinstall. The `__pycache__` subdirectory is the usual culprit.
- **`[all]` needs cmake + C compiler:** `mnemosyne-memory[all]` pulls `llama-cpp-python` which fails to build without cmake/gcc. On bare VPS without build tools, use `[embeddings]` instead — same local vector search, no local LLM consolidation. Install `build-essential cmake` first if you need `[all]`.
- **Plugin not appearing:** After linking, check `hermes memory status`. If "not found", re-run the symlink step. The plugin directory must contain `__init__.py` and `plugin.yaml`.
- **memory_enabled:** Setting this to `false` via `hermes config set` uses Python boolean `False` (capitalized) in YAML. This is correct — don't hand-edit to lowercase `false` unless you know what you're doing.
- **User manages their own API keys:** Don't auto-set embedding API keys. Show the user which env vars they need (`MNEMOSYNE_EMBEDDING_API_KEY`, `MNEMOSYNE_EMBEDDING_API_URL`, `MNEMOSYNE_EMBEDDING_MODEL`) and let them set from terminal. Only configure the provider activation and built-in memory disable.
- **Appending env vars to `.env`:** Use `printf '\nVAR=value\n' >> ~/.hermes/.env` — not `echo` with complex quoting. The `echo 'VAR=val' >> file` pattern breaks on shells with special-quote handling (common in containers). `printf` is reliable everywhere and doesn't need an editor.
- **No nano/vim in containers:** Container images often lack text editors. Use `printf` or `hermes config set` for config changes — never assume an editor is available.
- **Gateway restart in containers:** `hermes gateway restart` may block or timeout because it kills then starts a new process. Use background mode: `hermes gateway run` in background, then `hermes gateway status` to confirm. In containers without systemd, `gateway install` won't persist — the init script handles restart.
- **Gateway process died silently — stale lock file:** If `gateway_state.json` shows `"state":"running"` but the PID in `gateway.lock` is gone (check with `kill -0 <PID>` or `ls /proc/<PID>/status`), the gateway crashed without cleanup. The lock file won't block a new instance — just start a fresh one: `/app/venv/bin/hermes gateway run` (use full path if `hermes` isn't in PATH). Gateway logs at `~/.hermes/logs/gateway.log` stop writing when the process dies — a gap in timestamps is the tell.
- **Package duplication check:** Before installing, verify no duplicate packages exist: `pip3 list | grep -iE "mnemosyne|sqlite.vec|fastembed"`. Multiple versions of `mnemosyne-memory` or `mnemosyme-hermes` cause import conflicts.
- **Two separate plugin loading paths:** Hermes uses TWO discovery mechanisms for mnemosyne: (1) `plugins.memory.load_memory_provider()` scans `~/.hermes/plugins/mnemosyne/` for a `MemoryProvider` subclass — this registers the 37 tools; (2) `from mnemosyne import Mnemosyne` resolves via the pip-installed package at its actual filesystem path. The symlink at `~/.hermes/plugins/mnemosyne/` links to the **Hermes provider glue** (`hermes_memory_provider`), not the core `mnemosyne` package. If the core package is missing, the provider loads but fails at `BeamMemory()` init. Install BOTH: `pip3 install mnemosyne-hermes` provides both.
- **`plugin.yaml` is required:** The `~/.hermes/plugins/<name>/` directory must contain a `plugin.yaml` for Hermes to register it as a known plugin:
  ```yaml
  name: mnemosyne
  description: Mnemosyne memory provider
  version: 1.0.0
  ```
  Without it, `hermes plugins list` shows nothing and some discovery paths may skip it.
- **Embedding config: remote API vs local fallback:** mnemosyne reads `MNEMOSYNE_EMBEDDING_*` env vars at init. When `MNEMOSYNE_EMBEDDING_API_URL` is set (e.g. OpenAI API), mnemosyne uses the **remote API** for all embeddings. The local `fastembed`/`sentence-transformers` (pip dependencies) are only used when no `API_URL` is configured. Having `fastembed` installed does NOT mean local embeddings are active — check the env vars, not package presence. If an assistant claims mnemosyne uses a default local model, **verify the actual config** — generic architecture descriptions may be wrong for your setup. The `.env` file is read at process startup; edits require a restart.
- **`hermes config set` wraps list values as strings — and PyYAML can duplicate the key:** YAML list config like `sync_roles: [user]` gets stored as `sync_roles: '[user]'` (a string). Mnemosyne warns `unknown sync_roles ignored` and falls back to defaults. **Worse: if you then read/write the YAML with PyYAML's `yaml.dump`, the serializer can create a DUPLICATE key** — the malformed string stays under `mnemosyne.sync_roles` AND a correct YAML list appears at the `memory.sync_roles` flat level. Now you have TWO `sync_roles` keys, one wrong-format and one misplaced. The fix must remove BOTH and put one correct one in the right place:

  ```bash
  # 1. Find ALL sync_roles entries
  grep -n "sync_roles" ~/.hermes/config.yaml
  
  # 2. Use Python to fix this cleanly (sed is error-prone with nested YAML)
  python3 << 'PYEOF'
  import yaml
  path = '/home/username/.hermes/config.yaml'
  with open(path) as f:
      data = yaml.safe_load(f)
  
  memory = data.get('memory', {})
  
  # Remove flat memory.sync_roles (wrong level) if present
  if 'sync_roles' in memory:
      del memory['sync_roles']
  
  # Fix mnemosyne.sync_roles if it's a string
  mnemosyne = memory.get('mnemosyne', {})
  if isinstance(mnemosyne.get('sync_roles'), str):
      mnemosyne['sync_roles'] = ['user']
  
  with open(path, 'w') as f:
      yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
  PYEOF
  ```
  
  **Root cause:** `hermes config set` always serializes the value as a YAML scalar (quoted string), never as a sequence. Any config value that should be a YAML list or object needs `hermes config set` followed by a manual YAML fix. The safest approach is to **never use `hermes config set memory.sync_roles`**. Instead edit `~/.hermes/config.yaml` directly with `hermes config edit` (opens $EDITOR) or the Python recipe above.
  Any config value that should be a YAML list or object needs manual `sed`/edit — `hermes config set` always quotes the value as a string.

- **`hermes memory status` can be misleading:** It may show "Plugin: installed" even when the symlink is broken or the package unimportable. Always verify with a direct Python test:
  ```python
  from plugins.memory import load_memory_provider
  p = load_memory_provider("mnemosyne")
  print(p.is_available(), len(p.get_tool_schemas()), "tools")
  ```

- **NEVER use platform metadata for user identity:** When the user asks about themselves ("what is my name", "what do you know about me"), ALWAYS check Mnemosyne memory first (`mnemosyne_recall`, `mnemosyne_recall_canonical`). Do NOT rely on Telegram metadata (username, display name from topic config) or session context — these are often wrong or incomplete. The user explicitly corrected this pattern: the Telegram chat config said "Amir" but the user's real name stored in Mnemosyne was "Amirreza Mokhtari". Platform metadata is a fallback for routing, not a source of truth for identity.

- **NEVER guess the embedding model — use `mnemosyne_diagnose`:** The actual embedding model depends on env vars (`MNEMOSYNE_EMBEDDING_MODEL`), provider config, and install extras. Generic docs may say "all-MiniLM-L6-v2" but real deployments often use OpenAI `text-embedding-3-small` or other models. **Always** run `mnemosyne_diagnose` to get ground truth. Key fields: `embeddings_model` (actual model name), `vec_type` (int8/float32), `vec_working_status` (vector coverage). The user corrected this assumption sharply — it's a first-class pitfall.

- **Hermes log locations for diagnostics:**
  - `~/.hermes/logs/agent.log` — agent-level warnings (tool failures, provider errors)
  - `~/.hermes/logs/errors.log` — full error traces (superset of agent.log)
  - `~/.hermes/logs/gateway.log` — gateway lifecycle, Telegram/webhook connect/disconnect
  - `~/.hermes/logs/mcp-stderr.log` — MCP server stderr (n8n-mcp ping spam, startup failures)
  - `~/.hermes/mnemosyne/logs/diagnose_*.jsonl` — mnemosyne diagnostic snapshots

## Per-Topic Presets (Telegram Forum Topics)

When user wants the agent to "know what this topic is for" across `/new` resets, store topic context as `scope='global'` memories. These get injected into every session's context automatically.

```python
from mnemosyne import Mnemosyne
m = Mnemosyne()

# Store topic purpose as global memory
m.remember(
    "topic:ریسرچ - این تاپیک برای تحقیق و تحلیل ارزهاست. پاسخ فارسی و تحلیلی باشه.",
    importance=0.9,
    source="preference",
    scope="global"
)
```

**Why this works:** mnemosyne's `pre_llm_call` hook injects relevant working memories into the prompt. Global memories with high importance surface in every session, so the agent "remembers" the topic purpose even after `/new`.

**Configuring topic names in dm_topics:**

```python
import yaml
from pathlib import Path

config_path = Path.home() / ".hermes" / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

topics = config["gateway"]["platforms"]["telegram"]["extra"]["dm_topics"]
topics.append({
    "chat_id": "943724562",
    "thread_id": "123456",
    "name": "topic-name"
})

with open(config_path, "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
```

**Verify topic sessions:**

```python
import sqlite3
conn = sqlite3.connect(str(Path.home() / ".hermes" / "state.db"))
c = conn.cursor()
c.execute("""
    SELECT thread_id, COUNT(*) as sessions, SUM(message_count) as msgs
    FROM sessions WHERE source='telegram' AND thread_id IS NOT NULL
    GROUP BY thread_id ORDER BY msgs DESC
""")
for row in c.fetchall():
    print(f"thread:{row[0]} | {row[1]} sessions | {row[2]} msgs")
conn.close()
```

## Uninstall

```bash
pip uninstall mnemosyne-hermes
hermes config set memory.provider memory
hermes memory setup
rm -rf ~/.hermes/plugins/mnemosyne
rm -rf ~/.hermes/mnemosyne/
```
```
