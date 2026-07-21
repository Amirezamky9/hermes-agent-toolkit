# Telegram: Email Registration + OTP Auth + Multi-Agent Router

> Registration flow, email OTP verification, whitelist access control, and state-based routing to multiple AI agents — all in one n8n workflow.

---

## Pattern Overview

A complete registration → OTP → main menu → state-router → AI Agent pattern used in Telegram bots that require:

- **Access control** (only whitelisted users can chat)
- **Email verification** (OTP sent via Gmail)
- **Multi-mode AI agents** (different agents for different tasks)
- **Usage rate limiting** (weekly cap tracked in Data Table)

---

## Architecture

```
Telegram Trigger (message + callback_query)
  │
  ▼
[Set: Classify Message] ← JavaScript regex classifier
  │  message_type: OTP | EMAIL_VALID | EMAIL_INVALID | TEXT | EMPTY
  │  extracted_email, extracted_name, otp_code, callback_data
  │
  ▼
[DataTable: Get row(s)] ← Lookup user in n8n_users
  │
  ├── NOT FOUND ──→ Registration Flow
  │                    Name+Email Input → Email Validation → Whitelist Check →
  │                    OTP Generation → Gmail Send → OTP Verify → Welcome
  │
  └── FOUND ────→ [Switch: State Router]
                    ├── has status (teacher/workflowyab/debug) → Continue session
                    └── no status → Show Main Menu (inline keyboard)
```

---

## 1. Message Classifier (Set node)

A single Set node at the very beginning classifies every incoming message using JavaScript expressions.

```javascript
// message_type — determines what kind of input we received
(() => {
   const txt = ($json.message.text || '').toString().trim();
   if (!txt) return 'EMPTY';
   if (/^\d{6}$/.test(txt)) return 'OTP';
   
   const validDomains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'icloud', 'proton'];
   const domainPattern = new RegExp(`@(${validDomains.join('|')})\\.[A-Za-z]{2,}`, 'i');
   if (domainPattern.test(txt)) return 'EMAIL_VALID';
   if (/[^@\s]+@[^@\s]+/.test(txt)) return 'EMAIL_INVALID';
   return 'TEXT';
})()
```

```javascript
// extracted_email — regex-pull the email address
($json.message.text || '').match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/)
  ? ($json.message.text || '').match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/)[0]
  : null
```

```javascript
// extracted_name — everything before the email address
(() => {
   const txt = ($json.message.text || '').toString().trim();
   const emailMatch = txt.match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/);
   if (emailMatch) {
     const rawName = txt.substring(0, emailMatch.index);
     return rawName.replace(/[-–<>\n]/g, '').trim() || null;
   }
   return null;
})()
```

```javascript
// otp_code — 6-digit code
/^\d{6}$/.test(($json.message.text || '').toString().trim())
  ? ($json.message.text || '').toString().trim()
  : null
```

```javascript
// callback_data — for inline keyboard callbacks
$json.callback_query.data
```

> **Pitfall:** The Switch node after the classifier evaluates rules top-to-bottom. Always put `callback` FIRST, then `file`, then `command`, then `text` — so callback_data is caught before it falls into text processing.

---

## 2. Registration + OTP Auth Flow

### Flow Steps

```
User sends: "امیررضا مختاری\namir@gmail.com"
  │
  ▼
[Set: Classify Message] → EMAIL_VALID, extracted_email, extracted_name
  │
  ▼
[If: Is user registered?] ← Check if user exists in DataTable (empty + no email + no callback)
  │
  ├── YES → Route to normal flow
  └── NO ──→ [If2: Is this an OTP code?]
                │
                ├── YES → [DataTable: Validate OTP] → [If3: Valid + not expired?]
                │           ├── YES → Welcome! Set userid, clear OTP → Show Main Menu
                │           └── NO  → "کد نادرست یا منقضی شده است"
                │
                └── NO ──→ [Switch: emial employee1]
                              ├── EMAIL_INVALID → "فرمت ایمیل اشتباه است"
                              └── EMAIL_VALID → [If4: Name present?]
                                    ├── NO NAME → "فرمت اسم اشتباه"
                                    └── HAS NAME → [DataTable: Get email] ← Whitelist check
                                         │
                                         └── [Switch2: Match results]
                                              ├── Not found → "شما جزو لیست نیستی"
                                              ├── Email missing → "ایمیلت موجود نیست ولی اسمت هست"
                                              ├── Name mismatch → "اسمت با ایمیل ثبت شده همخوانی ندارد"
                                              ├── Email mismatch → "ایمیلی که ما داریم متفاوته"
                                              └── ALL MATCH → [Code: Make OTP]
                                                    │   Generates: { otp: "123456", otp_expires_at: ISO }
                                                    │
                                                    ▼
                                              [DataTable: Store OTP] → [Gmail: Send code] → "کد 6 رقمی را بفرست"
```

### OTP Generation Code

```javascript
// Code node: Make OTP
const otp = String(Math.floor(100000 + Math.random()*900000));
const exp = new Date(Date.now() + 10*60*1000).toISOString(); // 10 minutes
return { json: { email: $json.email, otp, otp_expires_at: exp } };
```

### OTP Verification Check

```javascript
// If3 conditions (both must pass):
condition 1: $json EXISTS (object not empty)
condition 2: $json.otp_expires_at.toDateTime().diffToNow('minutes').abs() < 10
```

> **Pitfall:** Store OTP in the Data Table as a **string** (because leading zeros matter — `001234`). If stored as number, `012345` becomes `12345` and the match fails.

---

## 3. State Router (Switch3)

After OTP verification, the user's `status` column tracks which mode they're in:

```javascript
// Switch3 route rules:
Rule 1: status === "teacher"      → Teacher agent branch
Rule 2: status === "workflowyab"   → Supervisor agent branch
Rule 3: status === "debug"         → Debug placeholder
Default: no status → Main Menu (inline keyboard)
```

### Updating Status

When user picks a mode from the main menu callback:

```javascript
// DataTable: Update row(s)
filters: { userid: $json.result.chat.id }
columns: {
  status: "teacher" | "workflowyab",
  massage_num: $('Get row(s)').item.json.massage_num + 1
}
```

---

## 4. Multi-Agent Configuration

| Agent | Primary Model | Fallback | Memory Table | Tools | Output |
|-------|--------------|----------|-------------|-------|--------|
| **Supervisor** (WorkflowYab) | Grok 4.1 Fast (OpenRouter) | Gemini 1.5 Pro | `n8n_chat_histories_natenagent_n8n_users` | Think + workflowyab (subworkflow) | Structured JSON via Output Parser |
| **Teacher** | Grok 4 Fast (OpenRouter) | Gemini 1.5 Pro | `n8n_chat_histories_n8n_users` | 5 MCP tools + Think1 | HTML text for Telegram |

### WorkflowYab Agent Output Parser Schema

```typescript
{
  top_workflows: [
    {
      id: string,          // "wf_123"
      score: number,       // 0.93
      name: string,        // Workflow name
      description: string, // Short description
      categories: string   // Category tags
    }
  ],
  text: string  // Farsi response to user
}
```

### Output Processing (WorkflowYab)

```
Supervisor Agent
  │
  ▼
[Structured Output Parser] → validated JSON
  │
  ▼
[If1: top_workflows empty?]
  ├── YES → "نتیجه‌ای پیدا نشد" (via Telegram sendMessage)
  └── NO  → [Split Out: output.top_workflows]
              │
              ▼
       [Postgres: Select from n8n_workflow_vector]
              │  WHERE id = $json.id
              ▼
       [Set: mean_workflow]
              │  jsonOutput = $json.metadata.workflowjson.toJsonString()
              ▼
       [Convert to File] → [Telegram: sendDocument]
              │             Caption includes: description, nodeCount, categories
              ▼
       [DataTable: Update row(s)2] ← Set rate limit timestamp
              columns: { limit: $now }
```

---

## 5. Rate Limiting

```javascript
// If6 condition — checks if 7+ days since last use
$('Get row(s)').item.json.limit.toDateTime().diffToNow('days').abs() > 6
```

- First-time use (limit is NULL) → passes (because `NULL.toDateTime()` doesn't exist — use a fallback)
- Within 6 days since last use → "به حد استفاده رسیدی دوست عزیز"
- 7+ days since last use → access granted

> **Pitfall:** The `.abs()` makes future dates also pass, but `diffToNow('days')` on a future date returns a negative number that `.abs()` converts to positive. If limit is somehow in the future, user gets denied. Use a Code node for robust checking instead:

```javascript
const limit = $('Get row(s)').item.json.limit;
if (!limit) return { json: { allowed: true } };  // No limit set → allow
const daysSinceLastUse = new Date().getTime() - new Date(limit).getTime();
return { json: { allowed: daysSinceLastUse > 7 * 24 * 60 * 60 * 1000 } };
```

---

## 6. WorkflowYab — Workflow File Export

When RAG search returns results, each workflow is sent as a downloadable `.json` file:

1. **Split Out** the `top_workflows` array from the Supervisor
2. **Postgres SELECT** from `n8n_workflow_vector` WHERE `id` matches
3. **Set node** extracts `metadata.workflowjson` as raw JSON string
4. **Convert to File** (operation: `toJson`, mode: `each`, filename: `{{$now.format('yyyyMMdd')}} - {{ $('Split Out').item.json.name.trim() }}.json`)
5. **Telegram sendDocument** with binary data + caption showing description, node count, categories
6. **Error output** from Convert→File → notifies developer via `Send error message` node

```javascript
// Caption format (HTML):
"👈توضیحات: {{ $('Split Out').item.json.description }}
👈تعداد نود: {{ $('Select rows from a table1').item.json.metadata.nodeCount }}
👈دسته بندی: {{ $('Split Out').item.json.categories }}"
```

---

## 7. MCP Tools in Telegram Bot

The Teacher agent connects to 5 MCP tools via a remote MCP server:

```typescript
credentials: { httpBearerAuth: { id: "...", name: "mcpbarer" } }
endpointUrl: "http://<server>:3000/mcp"
```

| Tool Name | MCP Method | Purpose |
|-----------|-----------|---------|
| `search_node` | `search_nodes` | Search n8n nodes by service name |
| `tools_documentation` | `tools_documentation` | Get node documentation |
| `search_templates` | `search_templates` | Search workflow templates |
| `get_node` | `get_node` | Inspect node configuration |
| `validate_node` | `validate_node` | Validate node parameters |

---

## 8. Cleanup After AI Agent Response (PostgreSQL)

After the Teacher agent responds, a SQL query cleans up the chat history by replacing the last AI message:

```sql
UPDATE n8n_chat_histories_n8n_users
SET message = jsonb_build_object('type', 'ai', 'content', $1)
WHERE id = (
    SELECT id
    FROM n8n_chat_histories_n8n_users
    WHERE session_id = $2 
      AND message->>'type' = 'ai'
    ORDER BY id DESC
    LIMIT 1
);
```

This removes tool-calling noise from the visible chat history (the original memory entry contains the full tool call chain which is ugly when read back).

---

## Key Pitfalls

| # | Pitfall | Solution |
|---|---------|----------|
| 1 | `$json` in DataTable filters shows wrong data | Use `$('NodeName').item.json.field` instead — DataTable's `$json` context can shift |
| 2 | OTP stored as number → leading zeros lost | Store OTP as **string** column type |
| 3 | Rate limit with future date breaks access | Use Code node for robust date check, not If node with `.abs()` |
| 4 | Tool-calling noise in chat history | Post-query SQL to rewrite last AI message (strip internal tool context) |
| 5 | Multiple outputs from Convert to File → error path | Wire error output of Convert→File and all downstream nodes to a Telegram alert to developer |
| 6 | `$json` undefined for 2+ steps back | Always reference with `$('NodeName').first().json.field` |
| 7 | Callback_data leaking `undefined` | Use `.match(/\d+/)` with `['0']` fallback instead of `.split('_').pop()` |
