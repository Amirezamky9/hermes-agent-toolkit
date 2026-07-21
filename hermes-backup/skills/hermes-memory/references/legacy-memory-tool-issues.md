# Legacy Memory Tool — Known Upstream Issues

When `memory_enabled: false` is set but the legacy `memory()` tool still appears,
this is a **known, tracked bug** in Hermes Agent — NOT a misconfiguration.

## Don't File Duplicates

These issues already track the problem. Link to them instead of creating new ones:

| Issue | Title | Status | Key Detail |
|-------|-------|--------|------------|
| [#57793](https://github.com/NousResearch/hermes-agent/issues/57793) | Legacy memory tool should be gated when external provider configured | OPEN, P3 | Exact match — `check_memory_requirements()` ignores `memory_enabled`. Has proposed fix (Option A: remove tool from toolset). |
| [#45422](https://github.com/NousResearch/hermes-agent/issues/45422) | `hermes tools disable memory` disables entire ecosystem | OPEN, P3 | `hermes tools disable memory` kills mnemosyne tools too because both share the `memory` toolset name. |
| [#32624](https://github.com/NousResearch/hermes-agent/issues/32624) | Three config semantic traps — 14 hours wasted debugging | OPEN, P2 | Comprehensive writeup: `memory_enabled: false` doesn't hide tool, config flags don't suppress prompt injection, per-profile log path confusion. |
| [#46108](https://github.com/NousResearch/hermes-agent/issues/46108) | `memory` toolset gating blocks Mnemosyne tools | OPEN, P3 | Root cause: `agent_init.py` gates provider tool injection on `memory` toolset being enabled, conflating legacy tool with provider system. |
| [#60805](https://github.com/NousResearch/hermes-agent/issues/60805) | Legacy memory tool visible when memory_enabled: false | OPEN | **Our filing — DUPLICATE of #57793.** Should be closed as duplicate. |

## Why Config-Only Fixes Don't Work

1. `memory_enabled: false` — only affects system prompt injection (`system_prompt.py:244`), NOT tool visibility
2. `agent.disabled_toolsets: [memory]` — disables ALL memory tools including mnemosyne (same toolset name)
3. `hermes tools disable memory` — same problem as #2, kills the entire ecosystem

## What Actually Works

**Patch `check_memory_requirements()`** in `tools/memory_tool.py` (if source is writable):
```python
def check_memory_requirements() -> bool:
    try:
        from hermes_cli.config import load_config
        config = load_config()
        return config.get("memory", {}).get("memory_enabled", True)
    except Exception:
        return True
```

**If source is read-only** (containers, read-only overlays): no config-only workaround exists. The legacy `memory()` tool will remain visible. Rely on the system prompt instruction and LLM learning to prefer mnemosyne tools.

## Root Cause Summary

The `memory` toolset name is overloaded — it gates both:
1. The legacy `memory()` tool function (MEMORY.md/USER.md)
2. All memory provider tools (mnemosyne_remember, etc.)

This makes it structurally impossible to disable one without the other via config.
The fix requires either splitting the toolset or gating the legacy tool's `check_fn`.
