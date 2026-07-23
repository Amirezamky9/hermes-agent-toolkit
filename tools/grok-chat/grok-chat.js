#!/usr/bin/env node
/**
 * grok-chat — Talk to Grok via Playwright
 * 
 * Sends a message to Grok on x.com/i/grok and returns the response.
 * Requires: playwright, valid x.com auth_token + ct0 cookies.
 *
 * Usage:
 *   node grok-chat.js "What is the capital of France?"
 *   node grok-chat.js --mode fast "Explain quantum computing"
 *   node grok-chat.js --mode deep "Write a poem about AI"
 *   node grok-chat.js --screenshot /tmp/grok.png "hello"
 *   node grok-chat.js --json "what time is it"
 */

const path = require('path');
const fs = require('fs');

// Resolve playwright from gstack or node_modules
function resolvePlaywright() {
  const candidates = [
    path.join(process.env.HOME, '.hermes/skills/gstack/node_modules/playwright'),
    'playwright',
  ];
  for (const p of candidates) {
    try { return require(p); } catch {}
  }
  throw new Error('playwright not found. Install: npm i -g playwright');
}

// Load cookies from agent-reach config
function loadCookies() {
  const cookiePaths = [
    path.join(process.env.HOME, '.agent-reach/cookies/twitter.env'),
    path.join(process.env.HOME, '.agent-reach/cookies/x_com.json'),
  ];

  let authToken = process.env.TWITTER_AUTH_TOKEN;
  let ct0 = process.env.TWITTER_CT0;

  if (!authToken || !ct0) {
    // Try twitter.env
    try {
      const envContent = fs.readFileSync(cookiePaths[0], 'utf8');
      const tokenMatch = envContent.match(/auth_token=([a-f0-9]+)/);
      const ct0Match = envContent.match(/ct0=([a-f0-9]+)/);
      if (tokenMatch) authToken = tokenMatch[1];
      if (ct0Match) ct0 = ct0Match[1];
    } catch {}
  }

  if (!authToken || !ct0) {
    // Try x_com.json
    try {
      const json = JSON.parse(fs.readFileSync(cookiePaths[1], 'utf8'));
      authToken = authToken || json.auth_token;
      ct0 = ct0 || json.ct0;
    } catch {}
  }

  if (!authToken || !ct0) {
    throw new Error(
      'No x.com cookies found. Set TWITTER_AUTH_TOKEN and TWITTER_CT0 env vars,\n' +
      'or ensure ~/.agent-reach/cookies/twitter.env exists.'
    );
  }

  return [
    { name: 'auth_token', value: authToken, domain: '.x.com', path: '/' },
    { name: 'ct0', value: ct0, domain: '.x.com', path: '/' },
  ];
}

// Parse CLI args
function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = {
    mode: 'fast',      // fast | deep
    screenshot: null,   // path to save screenshot
    json: false,        // output as JSON
    timeout: 20000,     // response wait time in ms
    message: '',
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--mode' && args[i + 1]) {
      opts.mode = args[++i];
    } else if (args[i] === '--screenshot' && args[i + 1]) {
      opts.screenshot = args[++i];
    } else if (args[i] === '--json') {
      opts.json = true;
    } else if (args[i] === '--timeout' && args[i + 1]) {
      opts.timeout = parseInt(args[++i], 10);
    } else if (args[i] === '--help' || args[i] === '-h') {
      printUsage();
      process.exit(0);
    } else if (!args[i].startsWith('-')) {
      opts.message = args[i];
    }
  }

  return opts;
}

function printUsage() {
  console.log(`
grok-chat — Talk to Grok via Playwright

Usage:
  node grok-chat.js "Your message"
  node grok-chat.js --mode deep "Explain quantum computing"
  node grok-chat.js --json "what time is it"
  node grok-chat.js --screenshot /tmp/grok.png "hello"
  node grok-chat.js --timeout 30000 "write a long essay"

Options:
  --mode <fast|deep>    Grok mode (default: fast)
  --screenshot <path>   Save screenshot to path
  --json                Output as JSON
  --timeout <ms>        Wait time for response (default: 20000)
  --help, -h            Show this help

Environment:
  TWITTER_AUTH_TOKEN    x.com auth_token cookie
  TWITTER_CT0           x.com ct0 cookie
  PLAYWRIGHT_BROWSERS_PATH  Browser path (auto-detected)
`);
}

async function sendToGrok(message, opts) {
  const { chromium } = resolvePlaywright();
  const cookies = loadCookies();

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  await ctx.addCookies(cookies);

  const page = await ctx.newPage();

  try {
    // Navigate to Grok
    await page.goto('https://x.com/i/grok', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });
    await page.waitForTimeout(4000);

    // Set mode if not default
    if (opts.mode !== 'fast') {
      try {
        const modeBtn = await page.$(`text=${opts.mode === 'deep' ? 'Deep' : opts.mode}`);
        if (modeBtn) await modeBtn.click();
        await page.waitForTimeout(1000);
      } catch {}
    }

    // Find textarea
    const textarea = await page.$('textarea');
    if (!textarea) throw new Error('Chat textarea not found — page might not be loaded');

    // Type message
    await textarea.fill('');
    await textarea.type(message, { delay: 20 });
    await page.waitForTimeout(300);

    // Press Enter to send
    await page.keyboard.press('Enter');

    // Wait for response (poll for text changes)
    const startTime = Date.now();
    let lastText = '';
    let stableCount = 0;

    while (Date.now() - startTime < opts.timeout) {
      await page.waitForTimeout(2000);
      const currentText = await page.evaluate(() => document.body.innerText);

      if (currentText !== lastText) {
        lastText = currentText;
        stableCount = 0;
      } else {
        stableCount++;
        if (stableCount >= 3) break; // Text stable for 6s = done
      }
    }

    // Extract response
    const fullText = await page.evaluate(() => document.body.innerText);

    // Screenshot if requested
    if (opts.screenshot) {
      await page.screenshot({ path: opts.screenshot, fullPage: false });
    }

    // Parse response — everything after the user message
    const lines = fullText.split('\n');
    const msgIdx = lines.findIndex(l => l.includes(message.substring(0, 30)));
    let response = '';
    if (msgIdx >= 0) {
      response = lines.slice(msgIdx + 1).join('\n').trim();
      // Strip footer: mode indicator, suggested topics, Done, explore links
      const stopPatterns = [
        '\nFast\n', '\nDeep\n', '\nDone',
        '\nExplore ', '\nLearn about', '\nWhy does', '\nWhat color',
        '\nHow does', '\nCan you', '\nTell me',
        // Persian suggested topics
        '\nتاریخچه', '\nشهرهای', '\nدرباره', '\nچیست', '\nچرا',
        '\nچگونه', '\nآیا', '\nمقایسه', '\nمراحل', '\nمراحل',
      ];
      for (const pat of stopPatterns) {
        const idx = response.indexOf(pat);
        if (idx > 0) response = response.substring(0, idx).trim();
      }
      // Remove trailing single-line suggestions (short lines after main answer)
      const respLines = response.split('\n');
      if (respLines.length > 1) {
        const lastLine = respLines[respLines.length - 1].trim();
        if (lastLine.length > 0 && lastLine.length < 60 && lastLine.endsWith('.')) {
          // Probably a suggestion, not part of answer
        }
      }
    }

    return { success: true, response, fullText };

  } finally {
    await browser.close();
  }
}

// Main
(async () => {
  const opts = parseArgs(process.argv);

  if (!opts.message) {
    printUsage();
    process.exit(1);
  }

  try {
    const result = await sendToGrok(opts.message, opts);

    if (opts.json) {
      console.log(JSON.stringify({
        success: true,
        message: opts.message,
        response: result.response,
        mode: opts.mode,
        timestamp: new Date().toISOString(),
      }, null, 2));
    } else {
      console.log(result.response);
    }
  } catch (err) {
    if (opts.json) {
      console.log(JSON.stringify({ success: false, error: err.message }));
    } else {
      console.error('Error:', err.message);
    }
    process.exit(1);
  }
})();
