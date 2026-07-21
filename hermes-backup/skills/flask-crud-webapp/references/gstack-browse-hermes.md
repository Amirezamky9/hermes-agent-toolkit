# gstack Browse on Hermes — Setup & Pitfalls

## Setup

```bash
# 1. Install Bun
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.local/bin:$PATH"

# 2. Clone gstack
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack

# 3. Install deps + build browse binary
cd ~/.hermes/skills/gstack && bun install
cd browse && bun run build

# 4. Install Playwright Chromium + system libs
cd ~/.hermes/skills/gstack && bun run node_modules/.bin/playwright install chromium
# System libs (needs root):
apt-get install -y libglib2.0-0t64 libnss3 libnspr4 libatk1.0-0t64 \
  libatk-bridge2.0-0t64 libdbus-1-3 libatspi2.0-0t64 libx11-6 \
  libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 \
  libxcb1 libxkbcommon0 libasound2t64 libcups2t64 libdrm2 \
  libpango-1.0-0 libcairo2

# 5. Generate Hermes skill docs
cd ~/.hermes/skills/gstack && bun run gen:skill-docs --host hermes
cp -r .hermes/skills/gstack-* ~/.hermes/skills/
```

## Usage

```bash
export PATH="$HOME/.local/bin:$PATH"
export GSTACK_CHROMIUM_NO_SANDBOX=1
export BROWSE_PORT=9400  # use unique port per session
B=~/.hermes/skills/gstack/browse/dist/browse

$B goto https://example.com
$B screenshot /tmp/test.png
$B snapshot -i
$B fill @e3 "text"
$B click @e4
```

## Agent Execution Order

**CRITICAL: Run gstack agents SEQUENTIALLY, never in parallel.**

gstack agents share the browse server state. Running them in parallel causes:
- `"Another instance is starting the server"` errors
- Race conditions on `.gstack/browse.json`
- Rate limiting on API calls
- Lost screenshots and report data

### Correct order for a new project:

```
Phase 1: Design (BEFORE code)
  1. /design-consultation → design system (colors, fonts, layout)
  2. /design-shotgun → multiple design variants
  3. /design-html → HTML/CSS implementation
  4. /design-review → visual QA + fixes

Phase 2: Quality (AFTER code)
  5. /qa → functional testing with browser
  6. /review → code review
  7. /cso → security audit
  8. /health → code quality score

Phase 3: Ship
  9. Fix critical issues found
 10. Re-run /qa to verify fixes
 11. /ship → create PR
```

### Running a single agent:

```bash
# Use delegate_task with role="leaf", ONE at a time
delegate_task(
    goal="Run gstack /qa on http://localhost:5001",
    role="leaf"
)
# Wait for result, then run next agent
```

### Common mistake (DO NOT):

```bash
# WRONG: parallel execution
delegate_task(tasks=[
    {goal: "run /qa", role: "leaf"},
    {goal: "run /review", role: "leaf"},  # ← RACE CONDITION
    {goal: "run /cso", role: "leaf"}      # ← RATE LIMITED
])
```

## Pitfalls

### 1. "Another instance is starting the server"

**Cause:** Stale PID/state in `.gstack/browse.json` from a previous session or crashed process.

**Fix:**
```bash
pkill -9 -f "browse" 2>/dev/null; pkill -9 -f "chromium" 2>/dev/null
sleep 2
echo '{}' > /workspace/.gstack/browse.json
# Or use a unique BROWSE_PORT:
export BROWSE_PORT=9400
```

### 2. System libs missing (Playwright Chromium)

Playwright's bundled Chromium needs ~20 system libraries. Without root, you CANNOT install them.
If `sudo` is unavailable, ask the user to run the apt-get command on the host.

### 3. Unique port per session

Each browse server binds to a port. If two sessions use the same port, the second gets
"Another instance is starting". Always set `BROWSE_PORT` to a unique value:
```bash
export BROWSE_PORT=$((9400 + RANDOM % 100))
```

### 4. `libasound2` is virtual on Ubuntu 24+

`apt-get install libasound2` fails with "has no installation candidate". Use `libasound2t64` instead.
Similarly, some `lib*64` packages exist alongside non-`t64` names — try both if one fails.

### 5. Zombie processes accumulate

Browse sessions leave zombie `bun` and `chrome-headless` processes. Before starting a new session:
```bash
pkill -9 -f "browse" 2>/dev/null
pkill -9 -f "chromium" 2>/dev/null
sleep 2
```

### 6. Design tools must come FIRST

Users expect the full design workflow when building a project. Don't skip to code.
Run `/design-consultation` → `/design-shotgun` → `/design-html` → `/design-review` BEFORE `/qa`.
If the user says "the design is bad", it means you skipped the design phase.
