# Mnemosyne ↔ Hermes Integration Reference

Source: https://github.com/mnemosyne-oss/mnemosyne → docs/hermes-integration.md

## Install Profiles

| Profile | RAM | Use case | Build deps |
|---------|-----|----------|------------|
| `mnemosyne-memory` (core) | ~50 MB | Low-resource or remote embedding API | none |
| `mnemosyne-memory[embeddings]` | ~800 MB | Local vector gen, single-user desktop | none |
| `mnemosyne-memory[all]` | ~1.5 GB | Local embeddings + local LLM consolidation | **cmake + gcc** (for llama-cpp-python) |
| `mnemosyne-hermes` | same as base | Plugin manifest + entry points (always needed) | none |

> **On bare VPS without build tools**, `[all]` will fail at `llama-cpp-python`. Use `[embeddings]` or install `build-essential cmake` first.

## Registered Tools (23)

Core memory: remember, recall, sleep, stats, get, update, forget, invalidate, validate
Knowledge graph: triple_add, triple_query, graph_query, graph_link
Multi-agent: shared_remember, shared_recall, shared_forget, shared_stats
Scratchpad: scratchpad_write, scratchpad_read, scratchpad_clear
Ops: export, import, diagnose

## Lifecycle Hooks

| Hook | Behavior |
|------|----------|
| pre_llm_call | Injects relevant working memory context into the prompt |
| on_session_start | Initializes session-scoped memory state |
| post_tool_call | Captures tool results as memories (if configured) |

## Key Config Vars

- `MNEMOSYNE_DATA_DIR` → `~/.hermes/mnemosyne/data` (default)
- `MNEMOSYNE_VEC_TYPE` → `int8` (float32, int8, bit)
- `MNEMOSYNE_EMBEDDING_MODEL` → `BAAI/bge-small-en-v1.5` (English)
- `MNEMOSYNE_EMBEDDING_MODEL` → `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)
- `MNEMOSYNE_HOST_LLM_ENABLED=true` → route sleep/consolidation through Hermes' LLM

### OpenAI Embedding Setup (common choice)

Add to `~/.hermes/.env` (user sets the API key themselves):

```
MNEMOSYNE_EMBEDDING_API_URL=https://api.openai.com/v1
MNEMOSYNE_EMBEDDING_MODEL=text-embedding-3-small
MNEMOSYNE_EMBEDDING_API_KEY=sk-...
```

`text-embedding-3-small` (1536-dim) is lightweight and fast. `text-embedding-3-large` (3072-dim) for higher accuracy. Agent can set the URL and model; API key must come from the user.

## CLI Commands

```
hermes mnemosyne stats [--global]
hermes mnemosyne inspect "query"
hermes mnemosyne sleep
hermes mnemosyne export --output backup.json
hermes mnemosyne import --input backup.json
hermes mnemosyne clear
hermes mnemosyne version
```

## Sync

```bash
# Server side:
mnemosyne sync serve --port 8765 --api-key "secret"

# Client side:
mnemosyne sync --remote https://my-vps:8765
mnemosyne sync --remote https://my-vps:8765 --encrypt  # XChaCha20-Poly1305
```

## Scratchpad API

The scratchpad is a flat key-value workspace for temporary notes within a session:

```python
from mnemosyne import Mnemosyne
m = Mnemosyne()

# Write — takes content only (no key arg), returns ID
sid = m.scratchpad_write("debug note for current task")

# Read — returns list of dicts: [{id, content, created_at, updated_at}]
notes = m.scratchpad_read()

# Clear — wipes all scratchpad entries
m.scratchpad_clear()
```

## Docker Notes

Inside Docker, Hermes home is `/opt/data/`. Use wrapper mode:
```bash
mnemosyne-hermes install --hermes-home /opt/data --mode wrapper --python /path/to/venv/bin/python
mnemosyne-hermes status --hermes-home /opt/data
hermes gateway restart
```

## Uninstall

```bash
pip uninstall mnemosyne-hermes
hermes config set memory.provider memory
hermes memory setup
rm -rf ~/.hermes/plugins/mnemosyne
rm -rf ~/.hermes/mnemosyne/
```
