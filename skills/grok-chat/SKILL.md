---
name: grok-chat
description: >-
  Talk to Grok (xAI) via Playwright browser on x.com/i/grok.
  Load when user asks to chat with Grok, ask Grok a question, use Grok
  for research, or wants to query xAI's model.
  Triggers: "grok", "ask grok", "xai", "chat with grok", "grok-chat".
version: 1.0.0
author: Hermes Agent Toolkit
license: MIT
metadata:
  hermes:
    tags: [grok, xai, chat, browser, playwright]
    toolsets: [terminal]
    depends_on:
      - nodejs
      - playwright
      - chromium
      - x.com-cookies
---

# grok-chat

## Overview

Sends a message to Grok on x.com/i/grok and returns the cleaned response.
Uses headless Chromium via Playwright. Cookie-based auth (no API key needed).

## Requirements

- `tools/grok-chat/grok-chat.js` — the CLI script
- Node.js 18+
- Playwright + Chromium installed
- Valid x.com `auth_token` + `ct0` cookies (in agent-reach config or env vars)

## Usage

```bash
# From the repo root
node tools/grok-chat/grok-chat.js "Your question here"

# With JSON output (recommended for automation)
node tools/grok-chat/grok-chat.js --json "Your question here"
```

## As an Installed Tool

If symlinked to a PATH directory:

```bash
grok-chat "What is the capital of France?"
grok-chat --json --mode deep "Explain quantum computing"
```

## Environment

- `TWITTER_AUTH_TOKEN` — x.com auth_token cookie
- `TWITTER_CT0` — x.com ct0 cookie
- `PLAYWRIGHT_BROWSERS_PATH` — path to Playwright browser cache (auto-detected)

## When to Use

- User asks to query Grok/xAI directly
- Research that benefits from Grok's real-time knowledge
- Benchmarking: comparing Grok's answer with other assistants
- Quick questions where Grok is the intended target

## When Not to Use

- Simple lookups better served by web search (cheaper, faster)
- User explicitly wants a different assistant

## Common Issues

1. **"playwright not found"** — load gstack skill first or install playwright globally
2. **"No x.com cookies found"** — run `agent-reach twitter-auth` or use Cookie Sync
3. **"Textarea not found"** — x.com UI probably changed; check screenshot with --screenshot
4. **Browser missing libs** — run `apt-get install -y` the libraries listed in README

## Verification

```bash
node tools/grok-chat/grok-chat.js --json "Say just: OK" 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); assert d['success'] and 'OK' in d.get('response',''); print('OK')"
```

## Security

- Cookies are read from env vars or agent-reach config — never hardcoded
- Browser runs headless only
- No data is sent outside your own x.com session
