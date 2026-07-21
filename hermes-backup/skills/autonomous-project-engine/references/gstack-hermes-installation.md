# gstack Installation on Hermes — Complete Workflow

## Prerequisites

- Bun runtime (~/.local/bin/bun)
- System libraries for Chromium (requires root/sudo access)

## Step-by-Step

### 1. Install Bun

```bash
BUN_VERSION="1.3.10"
curl -fsSL "https://github.com/oven-sh/bun/releases/download/bun-v${BUN_VERSION}/bun-linux-x64.zip" -o /tmp/bun.zip
python3 -c "import zipfile; zipfile.ZipFile('/tmp/bun.zip').extractall('/tmp/bun-extract')"
mkdir -p ~/.local/bin
cp /tmp/bun-extract/bun-linux-x64/bun ~/.local/bin/bun
chmod +x ~/.local/bin/bun
```

### 2. Clone + Build

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.hermes/skills/gstack
cd ~/.hermes/skills/gstack
bun install
cd browse && bun run build  # produces browse/dist/browse (~100MB)
```

### 3. Install Chromium

```bash
cd ~/.hermes/skills/gstack
bun run node_modules/.bin/playwright install chromium
```

### 4. System Libraries (requires root)

```bash
apt-get update && apt-get install -y \
  libglib2.0-0t64 libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libdbus-1-3 libatspi2.0-0t64 libx11-6 libxcomposite1 libxdamage1 \
  libxext6 libxfixes3 libxrandr2 libgbm1 libxcb1 libxkbcommon0 \
  libasound2t64 libcups2t64 libdrm2 libpango-1.0-0 libcairo2
```

### 5. Generate Hermes Skills

```bash
cd ~/.hermes/skills/gstack
bun run gen:skill-docs --host hermes
cp -r .hermes/skills/gstack-* ~/.hermes/skills/
```

## Browse Binary Usage

```bash
export PATH="$HOME/.local/bin:$PATH"
export GSTACK_CHROMIUM_NO_SANDBOX=1
export BROWSE_PORT=9400
export BROWSE_STATE_FILE=/tmp/browse-state.json
B=~/.hermes/skills/gstack/browse/dist/browse

$B goto https://example.com
$B screenshot /tmp/page.png
$B snapshot -i           # accessibility tree with @e refs
$B fill @e3 "text"       # fill form field
$B click @e5             # click element
$B press Enter           # press key
$B console --errors      # JS console errors
```

## Troubleshooting

### "Another instance is starting the server"

```bash
pkill -9 -f "browse" 2>/dev/null; pkill -9 -f "chromium" 2>/dev/null
rm -rf /workspace/.gstack/ ~/.gstack/
echo '{}' > /tmp/browse-state.json
export BROWSE_PORT=9400
```

### libasound2 "no installation candidate"

Use `libasound2t64` instead of `libasound2`.

### Chromium missing libraries

```bash
ldd ~/.cache/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-linux64/chrome-headless-shell | grep "not found"
apt-get install -y <missing-package>
```
