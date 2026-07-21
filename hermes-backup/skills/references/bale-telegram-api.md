# Bale / Telegram Direct API Reference

> Used by n8n-builder RULE 4 Pattern B: Code node → HTTP Request for dynamic inline keyboards.
> Base URLs: Bale → `https://tapi.bale.ai` | Telegram → `https://api.telegram.org`

## Token resolution in HTTP Request nodes

The bot token is embedded in the URL via `$credentials()`:
```
{{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText'}}
```

No credential assignment needed on the HTTP Request node. `$credentials('name')` resolves any matching credential instance.

## Common endpoints

### editMessageText (POST)

```json
{
  "method": "POST",
  "url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/editMessageText'}}",
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      { "name": "chat_id", "value": "={{ $('📱 Telegram Trigger').item.json.callback_query?.message?.chat?.id }}" },
      { "name": "message_id", "value": "={{ $('📱 Telegram Trigger').item.json.callback_query?.message?.message_id }}" },
      { "name": "text", "value": "={{ $json.text }}" },
      { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
      { "name": "parse_mode", "value": "HTML" }
    ]
  }
}
```

> **chat_id/message_id:** Always resolve from `$('📱 Telegram Trigger').item.json.callback_query?.message?.*`. Never reference intermediate nodes like `$('Extract Input Data')` — they may not exist when using update_workflow + addNode. The Telegram Trigger node always carries the raw callback data.
```

### sendMessage (POST)

```json
{
  "method": "POST",
  "url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/sendMessage'}}",
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      { "name": "chat_id", "value": "={{ $('📱 Telegram Trigger').item.json.message?.chat?.id }}" },
      { "name": "text", "value": "={{ $json.text }}" },
      { "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" },
      { "name": "parse_mode", "value": "HTML" }
    ]
  }
}
```

> **chat_id برای sendMessage:** برای کامندهای متنی (مثل /menu)، `chat_id` رو از `$('📱 Telegram Trigger').item.json.message?.chat?.id` بگیر. برای کالبک‌ها (دکمه) از `callback_query?.message?.chat?.id`.

### answerCallbackQuery (POST)

```json
{
  "method": "POST",
  "url": "={{ 'https://tapi.bale.ai/bot' + $credentials('bale_bot_evet_rosteri').accessToken + '/answerCallbackQuery'}}",
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      { "name": "callback_query_id", "value": "={{ $('Extract Input Data').first().json.callback_query.id }}" },
      { "name": "text", "value": "✅ Done!" },
      { "name": "show_alert", "value": false }
    ]
  }
}
```

## Wire format: inline_keyboard (raw Telegram) vs inlineKeyboard (n8n wrapper)

| Format | Shape | Where used |
|--------|-------|------------|
| `inline_keyboard` (Telegram API) | `[[{text, callback_data}], [{text, callback_data}]]` — array of button-row arrays | HTTP Request body (`reply_markup`) |
| `inlineKeyboard` (n8n Telegram node) | `{ rows: [{ row: { buttons: [...] } }] }` — nested object | Telegram node native params |

**Code node output for Pattern B:**
```javascript
return [{ json: { text, inline_keyboard } }];
// inline_keyboard is a 2D array: [[{text, callback_data}], [{text}]]
```

**HTTP Request `reply_markup` field:**
```json
{ "name": "reply_markup", "value": "={{ JSON.stringify({ inline_keyboard: $json.inline_keyboard }) }}" }
```

## Why not Telegram node for dynamic keyboards?

- `inlineKeyboard` + expression → `INVALID_PARAMETER` false positive warning
- The Telegram node wraps the API call with n8n's own translation layer — expression-based values for the keyboard wrapper are unreliable across n8n versions and Bale's fork
- HTTP Request eliminates the translation layer entirely — you control the exact API payload
