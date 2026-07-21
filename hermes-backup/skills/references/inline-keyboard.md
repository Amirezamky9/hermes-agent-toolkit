# Inline Keyboard Patterns — Telegram & Bale

> Load this when building any Telegram/Bale bot with inline keyboards.
> Call: `skill_view('n8n-builder', file_path='references/inline-keyboard.md')`

## Two patterns — pick by scenario

| Scenario | Approach | Wire format |
|----------|----------|-------------|
| **Static** — 2-5 fixed buttons, known at design time | Telegram node native `inlineKeyboard` param | `rows[].row.buttons[]` |
| **Dynamic** — buttons from DB, stock-aware, per-user | Code node → HTTP Request to bot API | `inline_keyboard: [[{text, callback_data}]]` |

---

## Pattern A: Static keyboard (Telegram node native)

Write `inlineKeyboard` directly in the Telegram node — NO Code node needed.

### With sendMessage / editMessageText

```json
{ "type": "addNode", "node": {
  "name": "Send Menu",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 2,
  "parameters": {
    "resource": "message",
    "operation": "sendMessage",
    "chatId": "={{ $('Extract Input Data').first().json.chat_id }}",
    "text": "Main Menu:",
    "replyMarkup": "inlineKeyboard",
    "inlineKeyboard": {
      "rows": [
        { "row": { "buttons": [
          { "text": "🛍 Products", "additionalFields": { "callback_data": "view_products" } }
        ]}},
        { "row": { "buttons": [
          { "text": "🛒 Cart", "additionalFields": { "callback_data": "view_cart" } },
          { "text": "📦 Orders", "additionalFields": { "callback_data": "view_orders" } }
        ]}}
      ]
    }
  },
  "position": [1400, 600]
}}
```

**Rules:**
- `replyMarkup` must be `"inlineKeyboard"` (string), not `"none"` or omitted
- Each `row` is a horizontal line of buttons — put 1-3 buttons per row
- `callback_data` is a short string the bot uses to route the callback
- You can also use `url` in `additionalFields` for link buttons

---

## Pattern B: Dynamic keyboard (Code → HTTP Request)

**Never** use the Telegram node's `inlineKeyboard` with an expression for dynamic keyboards — it produces a false-positive `INVALID_PARAMETER` warning and is unreliable at runtime.

Use a Code node to build the payload, then an HTTP Request node to call the bot API directly.

### Step 1: Code node — builds text + inline_keyboard

```javascript
const items = $input.all();
let text = '📦 Products:\n\n';
const inline_keyboard = [];

for (let i = 0; i < items.length; i++) {
  const item = items[i].json;
  text += String(i + 1) + '. ☕ ' + item.name + '\n';
  inline_keyboard.push([
    { text: '☕ ' + item.name, callback_data: 'view_product_' + item.id }
  ]);
}

inline_keyboard.push([
  { text: '🏠 Back to Menu', callback_data: 'back_to_menu' }
]);

return [{ json: { text, inline_keyboard } }];
```

Config for Code node:
```json
{ "type": "addNode", "node": {
  "name": "Build Product Keyboard",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "const items = $input.all();\nlet text = '📦 Products:\\n\\n';\nconst inline_keyboard = [];\n\nfor (let i = 0; i < items.length; i++) {\n  const item = items[i].json;\n  text += String(i + 1) + '. ☕ ' + item.name + '\\n';\n  inline_keyboard.push([\n    { text: '☕ ' + item.name, callback_data: 'view_product_' + item.id }\n  ]);\n}\n\ninline_keyboard.push([\n  { text: '🏠 Back to Menu', callback_data: 'back_to_menu' }\n]);\n\nreturn [{ json: { text, inline_keyboard } }];",
    "runOnceForAllItems": true
  },
  "position": [1200, 600]
}}
```

### Step 2: HTTP Request node — calls bot API

```json
{ "type": "addNode", "node": {
  "name": "Edit Products Message",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "parameters": {
    "method": "POST",
    "url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText' }}",
    "authentication": "none",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        { "name": "chat_id", "value": "={{ $('Extract Input Data').first().json.chat_id }}" },
        { "name": "message_id", "value": "={{ $('Get Session').first().json.last_message_id }}" },
        { "name": "text", "value": "={{ $json.text }}" },
        { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
        { "name": "parse_mode", "value": "Markdown" }
      ]
    },
    "options": {}
  },
  "position": [1600, 600]
}}
```

**Key details:**
- Bot token is resolved via `$credentials('name').accessToken` in the URL — no credential assignment needed
- `reply_markup` is a JSON.stringify'd object with `inline_keyboard` as a flat 2D array (`[[{text, callback_data}], [{text, callback_data}]]`)
- `parse_mode: "Markdown"` enables bold, italic, links in button text

### sendMessage (new message, not edit)

Change the URL and drop `message_id`:
```json
"url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/sendMessage' }}",
"bodyParameters": {
  "parameters": [
    { "name": "chat_id", "value": "={{ $('Extract Input Data').first().json.chat_id }}" },
    { "name": "text", "value": "={{ $json.text }}" },
    { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
    { "name": "parse_mode", "value": "Markdown" }
  ]
}
```

---

## Wire format reference

| Format | When to use | Example |
|--------|-------------|--------|
| `rows[].row.buttons[]` | Telegram node native `inlineKeyboard` | `{ "rows": [{ "row": { "buttons": [{"text":"A","additionalFields":{"callback_data":"a"}}] }}] }` |
| `[[{text,callback_data}]]` | HTTP Request to bot API (Pattern B) | `[[{"text":"A","callback_data":"a"}]]` (the `inline_keyboard` value) |
| `JSON.stringify({ inline_keyboard: ... })` | `reply_markup` body parameter | `"={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}"` |

**Common mistake:** Mixing the two formats. If you use `inline_keyboard` (Telegram API raw format) in a Telegram node's `inlineKeyboard` param, it won't work. If you use `rows[].row.buttons[]` in an HTTP Request, the bot API won't recognize it.

---

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Keyboard not showing | Wrong wire format (mixed rows vs inline_keyboard) | Match format to approach per table above |
| False positive `INVALID_PARAMETER` | Using expression in Telegram node's `inlineKeyboard` | Switch to Pattern B (Code → HTTP Request) |
| Button press does nothing | `callback_data` too long (>64 chars) or has unsupported chars | Keep callback_data short: `view_product_123` not `view_product_with_long_name` |
| "token not found" | Wrong credential name or URL format | Use `$credentials('credential_name').accessToken` for Bale; for Telegram use `api.telegram.org` |
| Buttons show in wrong order | Array order wrong in Code node | `inline_keyboard` is a 2D array — outer array = rows, inner = buttons per row |
