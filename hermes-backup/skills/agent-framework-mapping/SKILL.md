---
name: agent-framework-mapping
description: "Map external AI agent frameworks to Hermes Agent — analyze skills/tools/architecture and create porting guides. Use when: adapting gstack, Codex, OpenClaw, or any agent framework for Hermes; comparing agent toolsets; porting skills between agents."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent, gstack, codex, openclaw, adaptation, mapping, skills]
    related_skills: [hermes-agent, hermes-toolsets-reference]
---

# Agent Framework Mapping

Map external AI agent frameworks' tools, skills, and workflows to Hermes Agent equivalents. Create porting guides for adapting skills between agents.

## When to Use

- User mentions adapting/p porting skills from another agent (gstack, Codex, OpenClaw, etc.)
- Comparing tool capabilities between agents
- Building a mapping table of external tools → Hermes tools
- Analyzing an agent framework's architecture for Hermes compatibility

## Not For

- Building Hermes skills from scratch (use `hermes-agent-skill-authoring`)
- Configuring Hermes (use `hermes-agent`)
- Running external agents directly

## Quick Tool Mapping (reference: `references/gstack-hermes-tools.md`)

Core pattern — map each external tool to the closest Hermes equivalent:

| External Tool | Hermes Equivalent | Notes |
|---------------|-------------------|-------|
| `Bash` | `terminal` | Hermes terminal is foreground-only by default |
| `Read` | `read_file` | 1-indexed lines in Hermes |
| `Write` | `write_file` | Overwrites entire file |
| `Edit` | `patch` | Hermes has fuzzy matching, more robust |
| `Grep` | `search_files` | regex backed |
| `Glob` | `search_files` target=files | |
| `Agent` | `delegate_task` | More features: roles, batches, background |
| `AskUserQuestion` | `clarify` | Hermes has choices[] param |
| `WebSearch` | built-in web search | |
| Browser (custom daemon) | `browser` tool | Hermes uses Browserbase/Camofox |

## Workflow

1. **Read the external skill** — understand its phases, triggers, and tool usage
2. **Map tools** using the table above (expand as needed per framework)
3. **Adapt the preamble** — strip external-specific setup (telemetry, session tracking); keep only what Hermes needs
4. **Rewrite for Hermes tools** — replace tool calls, adjust output format
5. **Add pitfalls** specific to the Hermes adaptation
6. **Test** — verify the adapted skill works end-to-end

## Key Adaptation Notes

### Preambles
gstack skills have ~100-line bash preambles for session tracking, telemetry, repo mode detection. Hermes handles these natively (sessions, memory, config). Strip them entirely — keep only skill-specific setup.

### Browser Integration
gstack uses a custom Chromium daemon (`$B` commands). Hermes has a `browser` tool with similar capabilities but different syntax. Map:
- `$B goto <url>` → browser tool navigate
- `$B snapshot -i` → browser tool snapshot
- `$B fill @e3 "text"` → browser tool fill
- `$B click @e5` → browser tool click

**gstack rejected MCP for browser automation** — too token-heavy. Uses plain CLI stdout via Bash instead. If porting browser skills, keep the CLI-call pattern rather than wrapping in MCP.

### Skill Format
Both use SKILL.md with YAML frontmatter. Key differences:
- gstack: `allowed-tools` list, `triggers` list, `preamble-tier`
- Hermes: `metadata.hermes.tags`, `related_skills`, description-based triggers
- Hermes skills are loaded via `skill_view()` or `-s` flag

### AskUserQuestion → clarify
gstack's `AskUserQuestion` has complex fallback logic (prose fallback, Conductor detection, auto-decide). Hermes's `clarify` is simpler — just pass choices[] array. No need for prose fallback.

## gstack Native Hermes Support (pair-agent)

gstack has **explicit Hermes integration** via `pair-agent` — not a port, but a runtime bridge:

### Architecture
```
User's Machine                         Hermes Agent
──────────────                         ────────────
gstack Browser Server (Chromium)          │
  ├── Local listener  127.0.0.1          │
  ├── Tunnel listener  ◄─── HTTP ────────┘
  ├── ngrok tunnel                       │
  └── Token Registry                     │
```

### How it works
1. User runs `/pair-agent` in Claude Code → generates a one-time setup key
2. User pastes instructions into Hermes chat
3. Hermes exchanges key via `POST /connect` → gets scoped session token (24h)
4. Hermes sends browser commands via `POST /command` with the token

### Command API
```json
POST /command
Headers: Authorization: Bearer <session_token>
Body: {"command": "goto", "args": ["https://example.com"], "tabId": 1}
```

### Setup
```bash
./setup --host hermes
# or: bun run gen:skill-docs --host hermes
```

### When to use this vs Hermes browser tool
| Scenario | gstack pair-agent | Hermes browser tool |
|----------|------------------|-------------------|
| Authenticated browsing (real cookies) | ✅ | ⚠️ no cookie import |
| Quick page check | ❌ overhead | ✅ faster |
| Visual regression | ✅ diff mode | ⚠️ manual |
| Same machine | ✅ skip tunnel | ✅ direct |
| Remote machine | ⚠️ needs ngrok | ✅ built-in |

### Limitations
- Requires Claude Code + Bun on the machine running the browser
- Requires ngrok for remote access (or same-machine)
- Console/network monitoring not exposed via HTTP API
- Only a subset of `$B` commands available via HTTP

## gstack Installation on Hermes

### Quick Install
```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack
cd ~/.hermes/skills/gstack && ./setup --host hermes
```

**Requirements:** [Bun](https://bun.sh/) v1.0+, Git

### Complete Installation (with browse binary)

```bash
# 1. Install Bun (if not present)
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.local/bin:$PATH"

# 2. Clone gstack
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack

# 3. Install dependencies
cd ~/.hermes/skills/gstack && bun install

# 4. Build browse binary
cd browse && bun run build

# 5. Install Playwright Chromium (user-space, no root needed)
cd ~/.hermes/skills/gstack && bun run node_modules/.bin/playwright install chromium

# 6. Generate Hermes skill docs
cd ~/.hermes/skills/gstack && bun run gen:skill-docs --host hermes

# 7. Copy generated skills to Hermes directory
cp -r ~/.hermes/skills/gstack/.hermes/skills/gstack-* ~/.hermes/skills/
```

### System Libraries (CRITICAL — requires root)

Playwright Chromium needs system libraries. Without them, you get:
```
error while loading shared libraries: libglib-2.0.so.0: cannot open shared object file
```

**Install inside Docker container (if applicable):**
```bash
docker exec -it <container_id> bash -c "apt-get update && apt-get install -y \
  libglib2.0-0t64 libnss3 libnspr4 \
  libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libdbus-1-3 libatspi2.0-0t64 \
  libx11-6 libxcomposite1 libxdamage1 \
  libxext6 libxfixes3 libxrandr2 \
  libgbm1 libxcb1 libxkbcommon0 \
  libasound2t64 libcups2t64 libdrm2 \
  libpango-1.0-0 libcairo2"
```

**On bare metal (with root):**
```bash
sudo apt-get install -y libglib2.0-0t64 libnss3 libnspr4 \
  libatk1.0-0t64 libatk-bridge2.0-0t64 libdbus-1-3 libatspi2.0-0t64 \
  libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
  libgbm1 libxcb1 libxkbcommon0 libasound2t64 libcups2t64 libdrm2 \
  libpango-1.0-0 libcairo2
```

**Note:** Some packages use `t64` suffix on Ubuntu 24.04+ (e.g., `libglib2.0-0t64`). If a package isn't found, try without `t64`.

### Updater Script
Create `~/.hermes/skills/gstack/bin/gstack-update`:
```bash
#!/bin/bash
set -e
export PATH="$HOME/.local/bin:$PATH"
GSTACK_DIR="$HOME/.hermes/skills/gstack"
cd "$GSTACK_DIR" && git pull origin main --ff-only
bun install && cd browse && bun run build
cd "$GSTACK_DIR" && bun run gen:skill-docs --host hermes
cp -r "$GSTACK_DIR/.hermes/skills/gstack-"* "$HOME/.hermes/skills/" 2>/dev/null || true
echo "✅ gstack updated"
```

### Hermes Host Config (hosts/hermes.ts)
gstack ships a dedicated Hermes host config that handles:
- **Path rewrites**: `~/.claude/skills/gstack` → `~/.hermes/skills/gstack`, `CLAUDE.md` → `AGENTS.md`
- **Tool rewrites**: `Bash` → `terminal`, `Read` → `read_file`, `Edit` → `patch`, `Agent` → `delegate_task`
- **Suppressed resolvers**: `DESIGN_OUTSIDE_VOICES`, `ADVERSARIAL_STEP`, `CODEX_SECOND_OPINION`, `CODEX_PLAN_REVIEW`, `REVIEW_ARMY` (not applicable to Hermes)
- **Global root**: `~/.hermes/skills/gstack` (skills install here)
- **Skills install to**: `~/.hermes/skills/gstack-*/`
- **Co-author trailer**: `Co-Authored-By: Hermes Agent <agent@nousresearch.com>`

### Generate Skills for Hermes (Alternative)
```bash
cd /path/to/gstack && bun run gen:skill-docs --host hermes
```

### Team Mode (Shared Repos)
```bash
(cd ~/.hermes/skills/gstack && ./setup --team) && \
~/.hermes/skills/gstack/bin/gstack-team-init required && \
git add .claude/ CLAUDE.md && git commit -m "require gstack for AI-assisted work"
```

### Pitfall: Setup Script Exits Early for Hermes
When you run `./setup --host hermes`, the script prints info and calls `exit 0` — it does NOT create symlinks or register skills. This is by design. For Hermes, skills are loaded via `skill_view()` at runtime, not discovered on disk. Don't mistake the exit for a failure.

## Running Multiple gstack Agents

gstack's power comes from running specialist agents for different concerns. There are TWO specialist stacks: **Code Quality** and **Design**.

### Code Quality Stack (execution order matters)
| Order | Agent | What it does | Output |
|-------|-------|-------------|--------|
| 1 | `/qa` | Browser-based QA testing (11 phases) | `qa-report/REPORT.md` |
| 2 | `/review` | Code review (SQL safety, XSS, auth) | `review-report.md` |
| 3 | `/cso` | Security audit (OWASP, STRIDE) | `security-audit.md` |
| 4 | `/health` | Code quality dashboard | `health-report.md` |

### Design Stack (execution order matters)
| Order | Agent | What it does | Output |
|-------|-------|-------------|--------|
| 1 | `/design-consultation` | Create design system (colors, fonts, layout) | `DESIGN.md` + updated CSS |
| 2 | `/design-shotgun` | Generate N design variants for comparison | `design-variants/*.html` |
| 3 | `/design-html` | Apply chosen variant to actual project templates | Updated templates + CSS |
| 4 | `/design-review` | Visual QA, fix inconsistencies | Before/after screenshots |

**User picks a variant after step 2, then steps 3-4 apply it.**

### Full gstack Cycle (audit → fix → re-audit)
```
Phase 1: Run Code Quality Stack (qa → review → cso → health)
Phase 2: Fix critical issues found
Phase 3: Re-run /qa to verify fixes
Phase 4: Run Design Stack if UI needs work
Phase 5: Final /qa pass → ready to ship
```

Repeat phases 2-3 until health score is acceptable.

### Sequential Execution (REQUIRED — user correction)

**⚠️ CRITICAL: Do NOT dispatch gstack agents in parallel batches.**

User explicitly corrected: "از این به بعد همزمان ایجنت هارو نفرستی، دونه دونه بفرست، مطابق قوانین خودش، وگرنه ریت لیمیت میخوریم، ترتیب رو هم رعایت گن"

Translation: "From now on, don't send agents simultaneously. Send them one by one, according to their rules, otherwise we'll hit rate limits. Follow the order too."

**Why sequential:**
1. **Rate limits** — parallel dispatch hits provider rate limits (429 errors)
2. **gstack rules** — each agent has its own workflow phases that must be followed in order
3. **Resource contention** — `/qa` needs the browse server; parallel agents fight for `BROWSE_PORT`
4. **Order matters** — `/review` findings inform `/cso` priorities; `/health` catches issues both miss

**Correct pattern:**
```python
# ✅ CORRECT: Sequential, one at a time
delegate_task(goal="Run gstack QA on http://localhost:PORT", role="leaf")
# wait for completion
delegate_task(goal="Run gstack code review on /path/to/project", role="leaf")
# wait for completion
delegate_task(goal="Run gstack CSO security audit on /path/to/project", role="leaf")
# wait for completion
delegate_task(goal="Run gstack health check on /path/to/project", role="leaf")
```

**❌ WRONG: Parallel batch (hits rate limits)**
```python
delegate_task(tasks=[
    {"goal": "Run gstack QA...", "role": "leaf"},
    {"goal": "Run gstack review...", "role": "leaf"},
    {"goal": "Run gstack CSO...", "role": "leaf"},
    {"goal": "Run gstack health...", "role": "leaf"}
])
```

### Pitfalls

**BROWSE_PORT Conflict**
When running `/qa`, set `BROWSE_PORT` and `BROWSE_STATE_FILE` to avoid "Another instance is starting" timeouts:
```bash
export BROWSE_PORT=9400
export BROWSE_STATE_FILE=/tmp/browse-state.json
```
Each browse session needs its own port. Kill stale processes before starting:
```bash
pkill -9 -f "browse" 2>/dev/null || true
pkill -9 -f "chromium" 2>/dev/null || true
```

**Zombie Processes**
Browse binary leaves zombie `bun` and `chrome-headless` processes. Clean up with:
```bash
kill -9 $(pgrep -f "bun.*server.ts") 2>/dev/null
kill -9 $(pgrep -f "chrome-headless") 2>/dev/null
rm -rf /workspace/.gstack/
```

## References

- `references/gstack-hermes-tools.md` — Full gstack tool mapping with examples
- `references/gstack-qa-workflow.md` — gstack's QA testing methodology adapted for Hermes
- `references/gstack-install-hermes.md` — Complete install guide with 12 pitfalls (Chromium deps, Bun install, Docker vs host, generated skills location, updater script, BROWSE_PORT conflict)
- `references/gstack-design-workflow.md` — 4-step design stack (consultation → shotgun → html → review) with pitfalls
