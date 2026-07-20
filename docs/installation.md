# 🚀 Installation Guide

> Complete guide to install Hermes Toolkit on a new Hermes instance.

## Prerequisites

- Python 3.10+
- Node.js 18+ (for CLIs)
- Git
- Telegram account (for Telegram toolkit)

## Quick Install (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/Amirezamky9/hermes-toolkit.git
cd hermes-toolkit
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Node.js CLIs

```bash
# Install yt-dlp
pip install yt-dlp

# Install Twitter CLI
pipx install twitter-cli

# Install Reddit CLI
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'

# Install Bilibili CLI
pipx install bilibili-cli

# Install GitHub CLI
sudo apt install gh

# Install mcporter (MCP tool)
npm install -g mcporter
```

### Step 4: Setup Telegram Toolkit

```bash
cd telegram-toolkit

# Create config
cp config.yaml.example config.yaml

# Edit with your API keys
nano config.yaml
# Get keys from: https://my.telegram.org/apps

# First login (requires phone number)
python3 cli.py info @telegram
```

### Step 5: Setup Cookie Sync

```bash
cd cookie-sync

# Generate token
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start server
python3 webhook.py
```

### Step 6: Setup Exa Search

```bash
# Add Exa to mcporter
mcporter config add exa https://mcp.exa.ai/mcp

# Test
mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'
```

### Step 7: Copy Skills to Hermes

```bash
# Copy agent-reach skill
cp -r skills/agent-reach ~/.hermes/skills/

# Copy research skills
cp -r skills/research ~/.hermes/skills/

# Copy deep-research-optimized
cp -r skills/deep-research-optimized ~/.hermes/skills/

# Copy telegram skill
cp -r skills/telegram ~/.hermes/skills/

# Copy scripts
cp research/scripts/*.sh ~/.hermes/scripts/
```

### Step 8: Verify Installation

```bash
# Check all tools
agent-reach doctor --json

# Test research
./research/scripts/research-web.sh "hello world"

# Test Telegram
cd telegram-toolkit
python3 cli.py info @telegram
```

## Detailed Installation

### Agent-Reach (Mother Project)

```bash
# Install agent-reach
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip

# Setup channels
agent-reach install --env=auto

# Check health
agent-reach doctor --json
```

### Twitter/X Setup

```bash
# Set tokens
export TWITTER_AUTH_TOKEN="your_token"
export TWITTER_CT0="your_ct0"

# Test
twitter whoami
```

### Reddit Setup

```bash
# Login
rdt login

# Test
rdt whoami
```

### YouTube Setup

```bash
# Create config
mkdir -p ~/.config/yt-dlp
cat > ~/.config/yt-dlp/config << 'EOF'
--js-runtimes node
--cookies ~/.agent-reach/cookies/youtube-cookies.txt
--remote-components ejs:github
EOF

# Test
yt-dlp --version
```

### Grok Setup (Optional)

```bash
# Get API key from https://console.x.ai
export XAI_API_KEY="your_key"

# Test
./research/scripts/research-grok.sh "hello"
```

## Skills Installation

### Agent-Reach Skill

```bash
# Copy skill
cp -r skills/agent-reach ~/.hermes/skills/

# Copy references
cp -r skills/agent-reach/references ~/.hermes/skills/agent-reach/

# Copy scripts
cp -r skills/agent-reach/scripts ~/.hermes/skills/agent-reach/

# Make scripts executable
chmod +x ~/.hermes/skills/agent-reach/scripts/*.sh
```

### Research Skills

```bash
# Copy all research skills
cp -r skills/research/* ~/.hermes/skills/research/

# Copy deep-research-optimized
cp -r skills/deep-research-optimized ~/.hermes/skills/
```

### Telegram Skills

```bash
# Copy telegram skills
cp -r skills/telegram/* ~/.hermes/skills/telegram/
```

## Scripts Installation

```bash
# Copy research scripts
cp research/scripts/*.sh ~/.hermes/scripts/

# Make executable
chmod +x ~/.hermes/scripts/*.sh

# Copy agent-reach scripts
cp skills/agent-reach/scripts/*.sh ~/.hermes/scripts/
cp skills/agent-reach/scripts/*.py ~/.hermes/scripts/
```

## Verification

### Check All Tools

```bash
# Agent-reach health check
agent-reach doctor --json

# Check individual tools
which yt-dlp gh twitter rdt-cli bili-cli mcporter

# Check Python packages
pip list | grep -E "telethon|pyyaml|aiofiles"
```

### Test Research Scripts

```bash
# Test web search
./research/scripts/research-web.sh "hello"

# Test Twitter
./research/scripts/research-twitter.sh "hello"

# Test YouTube
./research/scripts/research-youtube.sh "hello"

# Test Reddit
./research/scripts/research-reddit.sh "hello"

# Test Telegram
./research/scripts/research-telegram.sh "hello"
```

### Test Telegram Toolkit

```bash
cd telegram-toolkit

# Test CLI
python3 cli.py info @telegram

# Test music bot
python3 music_bot.py search "Hello Adele"

# Test bot interactor
python3 bot_interactor.py @whatsmusicbot --message "/start"
```

## Troubleshooting

### Common Issues

#### yt-dlp not found

```bash
pip install yt-dlp
# or
pip install -U yt-dlp
```

#### Twitter authentication failed

```bash
# Check tokens
echo $TWITTER_AUTH_TOKEN
echo $TWITTER_CT0

# Re-login
twitter login
```

#### Telegram login failed

```bash
# Delete session
rm -f telegram-toolkit/telegram.session

# Re-login
python3 telegram-toolkit/cli.py info @telegram
```

#### Exa search failed

```bash
# Check mcporter
mcporter call 'exa.web_search_exa(query: "test", numResults: 1)'

# Re-add Exa
mcporter config add exa https://mcp.exa.ai/mcp
```

### Getting Help

1. Check this guide
2. Read `docs/troubleshooting.md`
3. Check GitHub Issues
4. Run `agent-reach doctor --json`

## Credits

Built on top of:
- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) - Platform router
- [CacheCat](https://github.com/chinmay29hub/CacheCat) - Chrome cookie extension
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram MTProto
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video download
