# Hermes ↔ n8n Webhook Integration Patterns

## Architecture Overview

Two systems can connect bidirectionally via webhooks:

| Direction | Mechanism | Use Case |
|-----------|-----------|----------|
| **n8n → Hermes** | n8n HTTP Request → Hermes webhook (port 8644) | n8n catches event, sends to Hermes for AI processing |
| **Hermes → n8n** | Hermes POST → n8n webhook endpoint | Hermes triggers n8n workflow for data storage/automation |

## n8n → Hermes Pattern

### 1. Create Hermes webhook
```bash
hermes webhook subscribe <name> \
  --prompt "Process this: {payload.message}. User: {payload.user_id}. Return structured JSON." \
  --description "n8n sends events for AI processing" \
  --deliver telegram:<chat_id>
```

### 2. n8n HTTP Request node config
```
Method: POST
URL: https://<tunnel-url>/webhooks/<name>
Headers:
  Content-Type: application/json
  X-Hub-Signature-256: sha256=<HMAC-SHA256 signature>
Body (JSON):
  {"message": "{{ $json.message }}", "user_id": "{{ $json.user_id }}"}
```

### 3. HMAC signature generation in n8n (Code node)
```javascript
const crypto = require('crypto');
const secret = '<hmac-secret-from-hermes-webhook-subscribe>';
const payload = JSON.stringify($input.first().json);
const sig = crypto.createHmac('sha256', secret).update(payload).digest('hex');
return [{ json: { payload, sig } }];
```

## Hermes → n8n Pattern

### 1. Create n8n Webhook trigger
- In n8n, add a **Webhook** node
- Set method to POST
- Copy the webhook URL (e.g., `https://<n8n-host>/webhook/<uuid>`)
- Optionally set Response Mode to "Last Node" to get a response back

### 2. Hermes calls n8n via terminal/curl
```bash
curl -X POST https://<n8n-host>/webhook/<uuid> \
  -H "Content-Type: application/json" \
  -d '{"action": "store_data", "key": "value"}'
```

### 3. Or from Hermes Code/Execute tool
```python
import requests
requests.post("https://<n8n-host>/webhook/<uuid>", json={"action": "store_data"})
```

## Use Case: Daily Routine Bot

### Data Flow
```
User sends Telegram message
  → n8n Telegram Trigger
  → n8n IF/Switch (classify: reminder? habit log? query?)
  → n8n HTTP Request → Hermes (for NLU / smart response)
  → Hermes returns structured JSON
  → n8n stores in Data Table / Google Sheets
  → n8n sends Telegram reply
```

### Hermes Webhook Prompt Template
```
User message: {payload.message}
User ID: {payload.user_id}
Context: {payload.context}

Classify this message and return JSON:
{
  "intent": "habit_log|reminder_set|query|general",
  "habit": "<if habit_log>",
  "status": "done|skipped|partial",
  "time": "<if reminder_set, ISO time>",
  "response": "<natural language response to user>"
}
```

### n8n Schedule Trigger → Hermes (Morning Briefing)
```
Schedule Trigger (8:00 AM daily)
  → n8n HTTP Request → Hermes webhook
  → Hermes generates morning briefing (weather + habits + tasks)
  → Hermes sends to Telegram via --deliver
```

## Pitfalls

1. **Tunnel URL changes**: Cloudflare Quick Tunnel URLs change on restart. Store latest in `/tmp/webhook-tunnel-url.txt` and check cron job `webhook-tunnel-watchdog`.

2. **HMAC secret rotation**: If you re-run `hermes webhook subscribe`, the secret changes. Update n8n's HTTP Request node accordingly.

3. **n8n response timeout**: Hermes webhook processing can take 5-30s (LLM call). Set n8n HTTP Request timeout to 60s to avoid timeouts.

4. **Circular loops**: If Hermes calls n8n and n8n calls Hermes, add a `source` field to payloads and filter it to prevent infinite loops.

5. **Authentication**: Hermes webhook uses HMAC-SHA256 (not Bearer token). n8n webhook can use header-based auth. Never mix them up.
