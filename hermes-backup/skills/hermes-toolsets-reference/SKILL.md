---
name: hermes-toolsets-reference
description: "Complete reference of all Hermes Agent toolsets and tools with availability status and enablement instructions"
version: 1.0.0
tags: [hermes, toolsets, tools, reference, configuration]
---

# Hermes Agent Toolsets Reference

Complete enumeration of all toolsets and tools available in Hermes Agent, with availability status for the current environment and enablement instructions.

## Overview

Toolsets are logical groupings of related tools. Tools are only exposed to the agent when:
1. Their toolset is enabled (via `hermes tools enable <toolset>` or config)
2. Their `check_fn` returns `True` (requirements met: env vars, binaries, credentials)

Run `hermes tools list` or use the registry API to see current status:
```python
from tools.registry import discover_builtin_tools, registry
discover_builtin_tools()
print(registry.get_registered_toolset_names())
```

---

## Available Toolsets (Fully/Partially Working)

| Toolset | Tools Available | Notes |
|---------|----------------|-------|
| **clarify** | `clarify` | Ask clarifying questions |
| **code_execution** | `execute_code` | Sandboxed Python execution |
| **cronjob** | `cronjob` | Scheduled task management |
| **delegation** | `delegate_task` | Subagent spawning |
| **file** | `patch`, `read_file`, `search_files`, `write_file` | Core file operations |
| **image_gen** | `image_generate` | AI image generation (disabled in current session) |
| **memory** | `memory` | Persistent cross-session memory |
| **project** | `project_create`, `project_list`, `project_switch` | Project/profile management |
| **session_search** | `session_search` | Search past conversations (FTS5) |
| **skills** | `skill_manage`, `skill_view`, `skills_list` | Skill lifecycle |
| **terminal** | `process`, `terminal` | Shell commands & background processes |
| **todo** | `todo` | In-session task tracking |
| **tts** | `text_to_speech` | Text-to-speech (Edge TTS default) — **disabled in current session** |
| **video** | `video_analyze` | Video analysis — **disabled in current session** |
| **vision** | `vision_analyze` | Image analysis — **disabled in current session** |

---

## Unavailable Toolsets (Require External Dependencies)

| Toolset | Tools | Missing Dependency |
|---------|-------|-------------------|
| **browser** | `browser_back`, `browser_click`, `browser_console`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision` | Playwright + Chromium (`pip install playwright && playwright install chromium`) |
| **browser-cdp** | `browser_cdp`, `browser_dialog` | Chrome DevTools Protocol (local Chrome/Chromium with `--remote-debugging-port`) |
| **computer_use** | `computer_use` | Computer-use backend (VM, VNC, or desktop automation) |
| **discord** | `discord` | Discord bot token + gateway config |
| **discord_admin** | `discord_admin` | Discord admin token + gateway config |
| **feishu_doc** | `feishu_doc_read` | Feishu/Lark credentials + gateway config |
| **feishu_drive** | `feishu_drive_add_comment`, `feishu_drive_list_comment_replies`, `feishu_drive_list_comments`, `feishu_drive_reply_comment` | Feishu/Lark credentials + gateway config |
| **hermes-yuanbao** | `yb_query_group_info`, `yb_query_group_members`, `yb_search_sticker`, `yb_send_dm`, `yb_send_sticker` | Yuanbao credentials + gateway config |
| **homeassistant** | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | Home Assistant URL + token |
| **kanban** | `kanban_block`, `kanban_comment`, `kanban_complete`, `kanban_create`, `kanban_heartbeat`, `kanban_link`, `kanban_list`, `kanban_show`, `kanban_unblock` | Kanban board backend (dispatcher) |
| **terminal** | `close_terminal`, `read_terminal` | PTY terminal backend |
| **video_gen** | `video_generate`, `xai_video_edit`, `xai_video_extend` | Video generation API (xAI, etc.) |
| **web** | `web_extract`, `web_search` | Web search API (Brave, Serper, etc. — set `BRAVE_API_KEY` or `SERPER_API_KEY`) |
| **x_search** | `x_search` | X (Twitter) API credentials |

---

## Enabling Unavailable Toolsets

### Web Search (`web` toolset)
```bash
# Add to ~/.hermes/.env
BRAVE_API_KEY=your_key
# or
SERPER_API_KEY=your_key

# Then enable
hermes tools enable web
```

### Browser Automation (`browser` toolset)
```bash
pip install playwright
playwright install chromium
hermes tools enable browser
```

### X Search (`x_search` toolset)
```bash
# Add X API credentials to ~/.hermes/.env or via hermes auth
hermes tools enable x_search
```

### Video Generation (`video_gen` toolset)
```bash
# Requires xAI or other video gen API access
hermes tools enable video_gen
```

### Discord/Feishu/Yuanbao/Home Assistant
These require gateway platform configuration:
```bash
hermes gateway setup
# Configure the platform, then:
hermes tools enable discord
hermes tools enable feishu_doc
# etc.
```

---

## Toolset ↔ Tool Mapping (Complete)

Generated from `registry.get_tool_to_toolset_map()`:

```
browser: browser_back, browser_click, browser_console, browser_get_images, browser_navigate, browser_press, browser_scroll, browser_snapshot, browser_type, browser_vision
browser-cdp: browser_cdp, browser_dialog
clarify: clarify
code_execution: execute_code
computer_use: computer_use
cronjob: cronjob
delegation: delegate_task
discord: discord
discord_admin: discord_admin
feishu_doc: feishu_doc_read
feishu_drive: feishu_drive_add_comment, feishu_drive_list_comment_replies, feishu_drive_list_comments, feishu_drive_reply_comment
file: patch, read_file, search_files, write_file
hermes-yuanbao: yb_query_group_info, yb_query_group_members, yb_search_sticker, yb_send_dm, yb_send_sticker
homeassistant: ha_call_service, ha_get_state, ha_list_entities, ha_list_services
image_gen: image_generate
kanban: kanban_block, kanban_comment, kanban_complete, kanban_create, kanban_heartbeat, kanban_link, kanban_list, kanban_show, kanban_unblock
memory: memory
project: project_create, project_list, project_switch
session_search: session_search
skills: skill_manage, skill_view, skills_list
terminal: close_terminal, process, read_terminal, terminal
todo: todo
tts: text_to_speech
video: video_analyze
video_gen: video_generate, xai_video_edit, xai_video_extend
vision: vision_analyze
web: web_extract, web_search
x_search: x_search
```

---

## Checking Tool Availability Programmatically

```python
from tools.registry import discover_builtin_tools, registry

discover_builtin_tools()

# Check a specific tool
entry = registry.get_entry("web_search")
if entry:
    available = entry.check_fn is None or entry.check_fn()
    print(f"web_search: {'available' if available else 'unavailable'}")

# Check entire toolset
available = registry.is_toolset_available("web")
print(f"web toolset: {'available' if available else 'unavailable'}")

# Get all toolset statuses
for ts, status in registry.check_toolset_requirements().items():
    print(f"{ts}: {'✅' if status else '❌'}")
```

---

## Controlling Toolsets via Config (platform_toolsets)

**Key finding from session:** Toolsets are NOT controlled by a simple `enabled_toolsets` key in config.yaml. Instead, they are managed per-platform via `platform_toolsets`:

```yaml
# ~/.hermes/config.yaml
platform_toolsets:
  cli:  # platform name (cli, telegram, discord, etc.)
    - web
    - file
    - todo
    - delegation
    - terminal
    - computer_use
    - kanban
    - skills
    - cronjob
    - memory
    - session_search
    - clarify
    - browser
    - code_execution
```

### Programmatic Toolset Management

```python
from hermes_cli.config import load_config, save_config
from hermes_cli.tools_config import _get_platform_tools

config = load_config()

# View current enabled toolsets for a platform
enabled = _get_platform_tools(config, "cli")
print(f"Enabled: {sorted(enabled)}")

# Modify platform_toolsets
config["platform_toolsets"] = {
    "cli": [
        "web", "file", "todo", "delegation", "terminal",
        "computer_use", "kanban", "skills", "cronjob",
        "memory", "session_search", "clarify", "browser",
        "code_execution"
    ]
}

save_config(config)

# Verify
enabled = _get_platform_tools(config, "cli")
print(f"New enabled: {sorted(enabled)}")
```

### Practical Example from Session

User requested:
- **Disable**: `vision`, `image_gen`, `tts`, `video`
- **Enable**: `terminal` (ensure it stays enabled)

Resulting `platform_toolsets.cli` excludes the four disabled toolsets and keeps `terminal` + 13 others. Tools from disabled toolsets (`vision_analyze`, `image_generate`, `text_to_speech`, `video_analyze`) are no longer available to the agent.

> **Note:** The WebUI uses the `cli` platform. Changes take effect on next agent/session start.

---

## Notes

- **Availability is dynamic** — `check_fn` probes run at definition time and are cached for ~30 seconds
- **Tool changes require session reset** — `/reset` in chat, or new `hermes` invocation
- **Gateway vs CLI** — some toolsets are platform-gated (e.g., `kanban` only for dispatcher workers)
- **Config location** — `~/.hermes/config.yaml` controls `enabled_toolsets` per platform

---

## Support Files

| File | Purpose |
|------|---------|
| `scripts/check_toolsets.py` | Run to display current toolset availability statuses |