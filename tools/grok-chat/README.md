# grok-chat

Talk to Grok (xAI) on x.com via Playwright — from the terminal, from scripts, or from Hermes.

## Requirements

- Node.js 18+
- Playwright with Chromium (installed via gstack or separately)
- Valid x.com cookies (`auth_token` + `ct0`)

## Quick Start

```bash
# Simple message
node grok-chat.js "What is the capital of France?"

# JSON output (for scripts)
node grok-chat.js --json "Explain quantum computing in 3 bullet points"

# Deep mode
node grok-chat.js --mode deep "Write a poem about AI"

# Save screenshot
node grok-chat.js --screenshot /tmp/grok.png "hello world"

# Set response timeout (ms)
node grok-chat.js --timeout 30000 "Write a long essay about climate change"
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--mode <fast\|deep>` | Grok thinking mode | `fast` |
| `--json` | Output as JSON | false |
| `--screenshot <path>` | Save screenshot | none |
| `--timeout <ms>` | Max wait for response | 20000 |
| `--help`, `-h` | Show usage | — |

## Cookies

The script loads cookies from (in order):

1. **Env vars**: `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`
2. **agent-reach**: `~/.agent-reach/cookies/twitter.env`
3. **agent-reach**: `~/.agent-reach/cookies/x_com.json`

To get fresh cookies, use the [Cookie Sync](../../cookie-sync/) extension.

## Playwright Setup

If not already installed:

```bash
# From gstack (already bundled)
PLAYWRIGHT_BROWSERS_PATH=~/.cache/ms-playwright node grok-chat.js "hello"

# Or install Playwright globally
npm i -g playwright
npx playwright install chromium
```

If Chromium shows missing library errors, install system deps:

```bash
# Debian/Ubuntu
apt-get install -y libglib2.0-0t64 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libcups2t64 libdrm2 libxkbcommon0 libatspi2.0-0t64 libxfixes3 libgbm1 \
  libcairo2 libasound2 libnspr4 libx11-6 libxcb1 libxcomposite1 libxdamage1 \
  libxrandr2 libxext6 libpango-1.0-0 libpangocairo-1.0-0
```

## JSON Output

```json
{
  "success": true,
  "message": "What is 2+2?",
  "response": "4",
  "mode": "fast",
  "timestamp": "2026-07-23T11:00:53.922Z"
}
```

## Limitations

- No conversation history (each call is a fresh session)
- Depends on x.com UI structure — may break if Twitter changes DOM
- Headless browser required (~100MB Chromium)
- Response wait is polling-based, not real-time streaming

## How It Works

1. Launches headless Chromium via Playwright
2. Sets x.com auth cookies
3. Navigates to `x.com/i/grok`
4. Types message in chat textarea
5. Presses Enter to send
6. Polls page text until response stabilizes (no changes for 6s)
7. Extracts and cleans response text
8. Closes browser

## License

MIT
