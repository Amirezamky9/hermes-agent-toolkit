# gstack Installation on Hermes — Reference

## Source
- GitHub: `https://github.com/garrytan/gstack`
- Host config: `hosts/hermes.ts` in the gstack repo
- Setup script: `setup` (bash) in the gstack repo root

## Install Commands

```bash
# Clone (shallow, single branch)
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack

# Run setup for Hermes
cd ~/.hermes/skills/gstack && ./setup --host hermes
```

Alternative: generate Hermes-specific skill files from source:
```bash
cd /path/to/gstack && bun run gen:skill-docs --host hermes
```

## Requirements
- **Bun** v1.0+ (`curl -fsSL https://bun.sh/install | bash`)
- **Git**

## What `./setup --host hermes` Does

The setup script (`setup`, line 117-125) detects `--host hermes` and prints integration info, then calls `exit 0`. No symlinks, no file copies, no skill registration.

**Why:** Hermes uses `skill_view()` at runtime to load skills, not filesystem discovery.

## Hermes Host Config (hosts/hermes.ts)

Key config values from the gstack repo:

- **globalRoot**: `.hermes/skills/gstack`
- **Skills install to**: `~/.hermes/skills/gstack-*/`
- **Suppressed resolvers**: `DESIGN_OUTSIDE_VOICES`, `ADVERSARIAL_STEP`, `CODEX_SECOND_OPINION`, `CODEX_PLAN_REVIEW`, `REVIEW_ARMY`
- **Skipped skills**: `codex` (no OpenAI second opinion)
- **Co-author trailer**: `Co-Authored-By: Hermes Agent <agent@nousresearch.com>`

### Tool Rewrites
| gstack tool | Hermes tool |
|-------------|------------|
| `Bash` | `terminal` |
| `Read` | `read_file` |
| `Write` | `patch` |
| `Edit` | `patch` |
| `Agent` | `delegate_task` |
| `Grep` | `search_files` |

### Path Rewrites
| From | To |
|------|-----|
| `~/.claude/skills/gstack` | `~/.hermes/skills/gstack` |
| `.claude/skills/gstack` | `.hermes/skills/gstack` |
| `.claude/skills` | `.hermes/skills` |
| `CLAUDE.md` | `AGENTS.md` |

## Team Mode

```bash
(cd ~/.hermes/skills/gstack && ./setup --team) && \
~/.hermes/skills/gstack/bin/gstack-team-init required && \
git add .claude/ CLAUDE.md && git commit -m "require gstack for AI-assisted work"
```

- `required` blocks teammates without gstack; `optional` just nudges
- Auto-update check runs on each session start (throttled once/hour)

## Complete Installation Steps

```bash
# 1. Install Bun (if not present)
# Option A: official installer (needs unzip)
curl -fsSL https://bun.sh/install | bash
# Option B: manual download (if unzip unavailable)
BUN_VERSION="1.3.10"
tmpfile=$(mktemp)
curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-x64.zip" -o "$tmpfile"
python3 -c "import zipfile; zipfile.ZipFile('$tmpfile').extractall('/tmp/bun-extract')"
mkdir -p "$HOME/.local/bin"
cp /tmp/bun-extract/bun-linux-x64/bun "$HOME/.local/bin/bun"
chmod +x "$HOME/.local/bin/bun"
rm -rf /tmp/bun-extract "$tmpfile"
export PATH="$HOME/.local/bin:$PATH"

# 2. Clone gstack
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack

# 3. Install dependencies
cd ~/.hermes/skills/gstack && bun install

# 4. Build browse binary
cd browse && bun run build
# Creates: browse/dist/browse (~100MB compiled binary)

# 5. Install Playwright Chromium
cd ~/.hermes/skills/gstack
bun run node_modules/.bin/playwright install chromium
# Downloads to: ~/.cache/ms-playwright/chromium_headless_shell-*/

# 6. Install Chromium system dependencies (REQUIRES ROOT)
# Inside Docker container:
apt-get update && apt-get install -y \
  libglib2.0-0t64 libnss3 libnspr4 \
  libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libdbus-1-3 libatspi2.0-0t64 \
  libx11-6 libxcomposite1 libxdamage1 \
  libxext6 libxfixes3 libxrandr2 \
  libgbm1 libxcb1 libxkbcommon0 \
  libasound2t64 libcups2t64 libdrm2 \
  libpango-1.0-0 libcairo2
# On host (if not in container): use sudo

# 7. Generate Hermes skill docs
cd ~/.hermes/skills/gstack
bun run gen:skill-docs --host hermes

# 8. Copy generated skills to Hermes skills directory
cp -r ~/.hermes/skills/gstack/.hermes/skills/gstack-* ~/.hermes/skills/

# 9. Verify
~/.hermes/skills/gstack/browse/dist/browse goto https://example.com
# Should print: "Navigated to https://example.com (200)"
```

## Pitfalls

1. **Setup exits early for Hermes**: `./setup --host hermes` prints info and exits 0. NOT a failure — by design. Skills load via `skill_view()`, not disk discovery.

2. **Bun required**: Check with `command -v bun`. Install: `curl -fsSL https://bun.sh/install | bash`.

3. **Browse binary needs build**: `/browse` and `/pair-agent` require `cd browse && bun install && bun run build`. Check `browse/dist/browse` exists.

4. **`/codex` suppressed**: No OpenAI second opinion on Hermes — has own model routing.

5. **Chromium system dependencies**: Playwright Chromium needs system libraries. Check with: `ldd ~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell | grep "not found"`. If any show, install the missing packages.

6. **Ubuntu 24.04 package names**: Some packages have `t64` suffix (e.g., `libglib2.0-0t64`), some don't (e.g., `libx11-6`). Use the non-t64 name if t64 version not found, and vice versa. `libasound2` is a virtual package — use `libasound2t64` instead.

7. **Docker vs host**: If running inside a Docker container, system packages must be installed INSIDE the container, not on the host. Use `docker exec -it <container> bash` to enter, then run apt-get.

8. **GSTACK_CHROMIUM_NO_SANDBOX**: In containers or non-root environments, set `export GSTACK_CHROMIUM_NO_SANDBOX=1` before running browse commands.

9. **Generated skills location**: `bun run gen:skill-docs --host hermes` generates skills inside `~/.hermes/skills/gstack/.hermes/skills/gstack-*/`. You must COPY them to `~/.hermes/skills/` for Hermes to find them: `cp -r ~/.hermes/skills/gstack/.hermes/skills/gstack-* ~/.hermes/skills/`

10. **Updater script**: Create `~/.hermes/skills/gstack/bin/gstack-update` that runs: git pull → bun install → browse build → gen:skill-docs → copy skills. Then `chmod +x` it.

11. **BROWSE_PORT conflict**: If you see `"Another instance is starting the server, waiting..."` followed by timeout, another browse process is already running on the default port. Fix: set `export BROWSE_PORT=9222` (or any free port) before running browse commands. All `$B` commands in the same session share the same server instance.

12. **Using gstack browse standalone**: The browse binary works without Hermes integration. Set env vars and run directly:
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    export GSTACK_CHROMIUM_NO_SANDBOX=1
    export BROWSE_PORT=9222
    B=~/.hermes/skills/gstack/browse/dist/browse
    
    $B goto https://example.com
    $B screenshot /tmp/page.png
    $B snapshot -i          # list interactive elements with @e refs
    $B fill @e3 "text"      # fill form field by ref
    $B click @e5            # click element by ref
    $B press Enter          # press keyboard key
    $B text                 # get clean page text
    $B links                # list all links
    $B console --errors     # check JS console errors
    ```

13. **Running multiple gstack agents**: For comprehensive audits, run QA, review, CSO, and health agents **SEQUENTIALLY** (one at a time), NOT in parallel. User correction: "از این به بعد همزمان ایجنت هارو نفرستی، دونه دونه بفرست، مطابق قوانین خودش، وگرنه ریت لیمیت میخوریم، ترتیب رو هم رعایت گن" — parallel dispatch hits rate limits and violates each agent's workflow order. Each agent writes its own report. Set BROWSE_PORT to avoid conflicts when QA agent needs the browser.
