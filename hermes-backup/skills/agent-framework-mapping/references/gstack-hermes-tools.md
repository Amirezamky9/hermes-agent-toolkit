# gstack → Hermes Tool Mapping

## Source: gstack (github.com/garrytan/gstack)

gstack is Garry Tan's (YC CEO) open-source AI engineering workflow — **122,500+ GitHub stars** (July 2026). 23+ specialist Claude Code skills + a custom Chromium browser daemon. MIT license. Built with Bun + Playwright, compiled to a single ~58MB binary.

### Architecture

```
Claude Code → CLI (compiled binary, ~58MB) → HTTP POST → Chromium Daemon (Playwright)
                                              ~100-200ms/call
```
- Persistent Chromium daemon: cookies/tabs/login state survive between commands
- Auto-starts on first use, auto-shuts down after 30min idle
- State in `.gstack/browse.json`

### gstack Explicitly Rejects MCP for Browser

> "Everything that was a Chrome MCP server in the early days now happens through plain stdout. No JSON-schema framing, no protocol negotiation, no persistent WebSocket — Claude's Bash tool already exists, so we use it."
> — BROWSER.md

MCP was considered too token-heavy for complex browser interactions. gstack uses direct CLI commands (`$B snapshot`, `$B click @e30`) via Bash instead. The `@kedra/gstack-pi` package confirms: "Instead of utilizing network overhead or the MCP protocol (which is often too token-heavy for complex browser interactions), gstack-pi adopts a 'native' approach."

### npm Ecosystem

| Package | Purpose |
|---------|---------|
| `gstack-browser` (npm) | Standalone browser CLI — `npm i -g gstack-browser` |
| `gstack-codex` (npm) | gstack workflow for OpenAI Codex — `npx gstack-codex init --project` |
| `@gstack-vibehard/installer` (npm) | Cross-harness installer (Codex, Claude Code, OpenCode) |
| `@kedra/gstack-pi` (npm) | 60 native Pi tools + 23 workflow skills for Pi coding agent |
| `gstack-browse` (GitHub: juanheyns/gstack-browse) | Standalone persistent headless browser fork — `brew install juanheyns/tap/browse` |

### Install Methods

```bash
# Main repo (Claude Code)
git clone https://github.com/garrytan/gstack.git && cd gstack && bun install && bun run build

# Standalone browser (npm)
npm i -g gstack-browser && npx playwright install chromium

# Codex adapter (npm)
npx gstack-codex init --project

# macOS (homebrew)
brew install juanheyns/tap/browse
```

## Tool Translation Table

### Core Tools

| gstack (Claude Code) | Hermes | Migration Notes |
|----------------------|--------|-----------------|
| `Bash` | `terminal` | Hermes is foreground-only by default; use `background=true` for long tasks |
| `Read` | `read_file` | Hermes returns `{"content": "...", "total_lines": N}`, 1-indexed |
| `Write` | `write_file` | Overwrites entire file (same as gstack) |
| `Edit` | `patch` | Hermes has fuzzy matching (9 strategies), more robust than gstack's exact match |
| `Grep` | `search_files` target=content | Regex-backed, output modes: content, files_only, count |
| `Glob` | `search_files` target=files | Pattern-based file finding |
| `Agent` | `delegate_task` | Richer: roles (leaf/orchestrator), batch mode, background, context injection |
| `AskUserQuestion` | `clarify` | Simpler API: `choices[]` array, no prose fallback needed |
| `WebSearch` | Built-in web search | Hermes has native web search, no tool needed |
| Browser (custom) | `browser` tool | Hermes uses Browserbase/Camofox, not custom daemon |

### gstack Browser Commands → Hermes Browser Tool

| gstack `$B` Command | Hermes Equivalent | Notes |
|---------------------|-------------------|-------|
| `$B goto <url>` | browser navigate | |
| `$B snapshot -i` | browser snapshot | Interactive element listing |
| `$B snapshot -i -a -o file.png` | browser snapshot + vision_analyze | Annotated screenshots |
| `$B snapshot -D` | (no direct equivalent) | Diff before/after — manual in Hermes |
| `$B fill @e3 "text"` | browser fill | |
| `$B click @e5` | browser click | |
| `$B links` | browser snapshot | Links visible in snapshot |
| `$B console --errors` | (no direct equivalent) | Console errors not directly accessible |
| `$B network` | (no direct equivalent) | Network monitoring not built-in |
| `$B is visible ".class"` | browser snapshot + check | Verify element presence |
| `$B screenshot file.png` | browser screenshot | |
| `$B viewport 375x812` | browser viewport | |
| `$B responsive dir` | Multiple viewport screenshots | Manual iteration |
| `$B js "code"` | browser execute_js | |
| `$B cookie-import cookies.json` | (no direct equivalent) | Cookie import not built-in |
| `$B upload "#input" path` | browser upload | |
| `$B dialog-accept "yes"` | browser dialog | |

### Hermes-Only Tools (no gstack equivalent)

| Hermes Tool | What It Does |
|-------------|--------------|
| `vision_analyze` | Load image into context for analysis |
| `video_analyze` | Analyze video content |
| `execute_code` | Run Python with tool access |
| `session_search` | Search past conversations (FTS5) |
| `mnemosyne_*` | Persistent memory across sessions |
| `todo` | In-session task tracking |
| `cronjob` | Scheduled task management |
| `skill_manage` | Create/update/delete skills |
| `skill_view` | Load skill content |

## Skill Format Differences

### gstack SKILL.md Frontmatter
```yaml
---
name: qa
preamble-tier: 4
version: 2.0.0
description: Systematically QA test a web application... (gstack)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - WebSearch
triggers:
  - qa test this
  - find bugs on site
  - test the site
---
```

### Hermes SKILL.md Frontmatter
```yaml
---
name: my-skill
description: "Use when <trigger>. <behavior>."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [relevant, tags]
    related_skills: [other-skill]
---
```

Key differences:
- gstack: `allowed-tools`, `triggers`, `preamble-tier`
- Hermes: `metadata.hermes.{tags, related_skills}`, description-based triggers
- Hermes skills are loaded via `skill_view()` or `-s` flag, not slash commands

## Preamble Strategy

gstack preambles (~100 lines bash) handle:
- Session tracking (`~/.gstack/sessions/`)
- Telemetry logging
- Repo mode detection
- Update checks
- Feature discovery
- Learning file loading

Hermes handles these natively:
- Sessions: built-in session store
- Memory: `mnemosyne_*` tools
- Config: `config.yaml`
- Skills: `skill_view()`

**Strip all gstack preambles** when porting. Keep only skill-specific setup (e.g., "find the browse binary" becomes "ensure browser tool is enabled").

## Known gstack Skills Worth Porting

| Skill | Complexity | Hermes Value |
|-------|-----------|--------------|
| `/review` | Medium | High — code review methodology |
| `/qa` | High | High — QA testing with browser |
| `/cso` | Medium | High — security audit |
| `/investigate` | Low | High — debugging methodology |
| `/office-hours` | Low | Medium — product thinking |
| `/plan-ceo-review` | Low | Medium — strategic review |
| `/ship` | Medium | Medium — release workflow |
| `/design-html` | Medium | Low — Hermes has different UI approach |
