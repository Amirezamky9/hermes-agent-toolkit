# Agent-Reach: Reinstall From Scratch

Complete recipe when all tools are missing (e.g. after container rebuild).
Tested 2026-07-07 — all commands succeed in order.

## Prerequisites
- `python3` (always present)
- `curl` (always present)
- No `pipx`, no `node`, no `gh`, no agent-reach

## Step 1 — pipx
```bash
pip3 install --user pipx
export PATH="$HOME/.local/bin:$PATH"
```

## Step 2 — Node.js (needed for mcporter, yt-dlp js runtime, agent-reach install)
```bash
mkdir -p ~/.local/node
curl -sL https://nodejs.org/dist/v22.15.0/node-v22.15.0-linux-x64.tar.xz -o /tmp/node.tar.xz
tar xf /tmp/node.tar.xz -C /tmp
cp -r /tmp/node-v22.15.0-linux-x64/* ~/.local/node/
ln -sf ~/.local/node/bin/node ~/.local/bin/node
ln -sf ~/.local/node/bin/npm ~/.local/bin/npm
ln -sf ~/.local/node/bin/npx ~/.local/bin/npx
```

## Step 3 — agent-reach itself
```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

## Step 4 — gh CLI
```bash
curl -sL https://github.com/cli/cli/releases/download/v2.70.0/gh_2.70.0_linux_amd64.tar.gz -o /tmp/gh.tar.gz
tar xzf /tmp/gh.tar.gz -C /tmp
cp /tmp/gh_2.70.0_linux_amd64/bin/gh ~/.local/bin/
```

## Step 5 — yt-dlp + config
```bash
pip3 install --user yt-dlp
mkdir -p ~/.config/yt-dlp
cat > ~/.config/yt-dlp/config << 'EOF'
--js-runtimes node
--cookies ~/.agent-reach/cookies/youtube-cookies.txt
--remote-components ejs:github
EOF
```
- `--cookies` requires cookie-sync webhook delivering YouTube cookies
- `--remote-components ejs:github` is REQUIRED — without it, only storyboards
  are returned (YouTube 2025+ JS challenge protection blocks real formats)

## Step 6 — mcporter (Exa search)
```bash
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
npm install -g mcporter
ln -sf ~/.local/node/bin/mcporter ~/.local/bin/mcporter
```

## Step 7 — Platform CLIs (all via pipx)
```bash
pipx install twitter-cli
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'
pipx install bilibili-cli
```

## Step 8 — Verify
```bash
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
agent-reach doctor --json
```

Expected: 6/15 channels `ok` (YouTube, Bilibili, V2EX, RSS, Exa Search, Web).
Remaining channels need user cookies/auth.

## PATH note
Always export before using tools:
```bash
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
```

## Pitfall: pipx may need approval
pipx install can trigger security scan warnings about package name similarity
(e.g. pipx ≈ pip). These are false positives — approve and continue.

## Pitfall: tar extraction warning
Node.js tar extraction may trigger archive extraction warnings. Approve and continue.

## Pitfall: tools lost after workspace cleanup
Agent-reach and all CLIs installed via pipx/npm live in user directories
(~/.local/bin, ~/.local/share/pipx/venvs, ~/.local/node). These survive
container restarts but NOT full environment rebuilds.

**Critical**: tools must NEVER be installed in the workspace directory
(`/workspace/` or any subdirectory). The workspace has weekly automated
cleanup. If tools were installed there (e.g. via `pip install` without
`--user` or `pipx install` into workspace), they will be silently deleted.

**Safe locations** (outside workspace, survive cleanup):
- `~/.local/bin/` — pipx-exposed binaries, manual binary installs
- `~/.local/share/pipx/venvs/` — pipx virtualenvs
- `~/.local/node/` — Node.js installation

When diagnosing "tools missing but I installed them before":
1. First check `~/.local/bin/` — if tools are there, PATH issue only
2. Check `~/.local/share/pipx/venvs/` — if venvs exist but binaries gone, symlink broke
3. Check if tools were in workspace (`/workspace/`) — if yes, they got cleaned
4. Fall back to this reinstall recipe

After reinstalling, always verify: `agent-reach doctor --json`
