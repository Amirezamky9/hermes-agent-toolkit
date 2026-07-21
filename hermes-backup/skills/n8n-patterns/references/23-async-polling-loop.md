# Pattern: Async Polling Loop — حلقه بررسی وضعیت job ناهمگام

> General pattern for APIs that return a task ID and require polling until completion.
> Covers: image generation, video rendering, batch processing, any async job.

---

## 1. Core Pattern

```
[Trigger]
    ↓
[Set: prepare payload]
    ↓
[HTTP POST: submit job → get task_id]
    ↓
[Store task_id in item data]
    ↓
┌── Polling Loop ───────────────────┐
│  [Wait: N seconds]                │
│  [HTTP GET: check status by ID]   │
│  [IF: status == "done"?]          │
│   ├─ TRUE  → [process result]     │
│   └─ FALSE → [loop back to Wait]  │
└───────────────────────────────────┘
```

## 2. n8n SDK: Creating Circular Connections

The SDK `.to()` only creates forward edges. To create a loop (IF false → back to Wait):

### Step 1: Create workflow with forward connections only
```javascript
export default workflow('my-pipeline', 'Pipeline')
  .add(trigger)
  .to(submitJob)
  .to(waitNode)
  .to(checkStatus)
  .to(isDone
    .onTrue(processResult)
    // NO .onFalse() — leave unwired
  );
```

### Step 2: Add loop connection via update_workflow
```javascript
await mcp_n8n_mcp_update_workflow({
  workflowId: createdId,
  operations: [{
    type: 'addConnection',
    source: 'Image Ready?',      // IF node name
    sourceIndex: 1,              // false output (0=true, 1=false)
    target: 'Wait 15 Seconds',   // Wait node name
    targetIndex: 0               // Wait input
  }]
});
```

**Key insight:** `sourceIndex: 0` = true branch, `sourceIndex: 1` = false branch for IF nodes.

## 3. Store Task ID Pattern

After submitting a job, store the task_id in item data so it survives the Wait node:

```javascript
// Set node after HTTP POST:
assignments: [
  { id: 'task-id', name: 'taskId', value: '={{ $json.id }}', type: 'string' },
  { id: 'task-status', name: 'taskStatus', value: '={{ $json.status }}', type: 'string' }
]
```

Reference later in Check Status node:
```
{{ $("Store Task Data").item.json.taskId }}
```

**Why:** The Wait node may not preserve the original HTTP response context. Explicitly storing task_id ensures it is available in the loop.

## 4. Known APIs Using This Pattern

| API | Submit Endpoint | Check Endpoint | Status Field |
|-----|----------------|----------------|--------------|
| **Stability AI** | `POST /v2beta/stable-image/generate/async` | `GET /v2beta/stable-image/generate/result/{id}` | `status` |
| **KIE.AI** | `POST /v1/text2video` or `/v1/image2video` | `GET /v1/task/{taskId}` | `state` (success/fail/generating/queuing) |
| **Replicate** | `POST /v1/predictions` | `GET /v1/predictions/{id}` | `status` (starting/processing/succeeded/failed) |
| **FAL.ai** | `POST /fal-ai/{model}` | `GET /fal-ai/{model}/requests/{id}/status` | `status` |
| **DALL-E 3** | Synchronous (no polling needed) | — | — |

## 5. LongCat API — OpenAI-Compatible Text LLM

> By Meituan. Text-only LLM, NOT image generation. Useful as AI Agent for prompt writing.

- **Base URL:** `https://api.longcat.chat/openai`
- **Endpoint:** `POST /v1/chat/completions` (OpenAI format)
- **Auth:** `Authorization: Bearer YOUR_KEY`
- **Model:** `LongCat-2.0`
- **Context:** 1M tokens, max output 128K tokens

```bash
curl -X POST https://api.longcat.chat/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"LongCat-2.0","messages":[{"role":"user","content":"Hello!"}],"max_tokens":1000}'
```

**n8n config:** Use `lmChatOpenAi` node with:
- `model: 'LongCat-2.0'`
- Credential: OpenAI API type, base URL = `https://api.longcat.chat/openai`

**Pricing (limited-time discount):**
- Uncached Input: $0.30/1M tokens
- Cached Input: $0.006/1M tokens
- Output: $1.20/1M tokens

## 6. Pitfalls

| Pitfall | Solution |
|---------|----------|
| **Loop runs forever** | Add max iteration counter in Code node; break after N attempts |
| **Task ID lost after Wait** | Store task_id in Set node before Wait; reference with `$('Node Name').item.json.taskId` |
| **Status field varies by API** | Check API docs for exact status string (done/success/succeeded vs generating/in_progress) |
| **SDK cannot create back-edges** | Use `update_workflow` with `addConnection` after creation |
| **Wait node uses server time** | Use relative duration (`amount: 15, unit: 'seconds'`), not absolute time |
| **429 Rate Limit on polling** | Increase Wait interval (15-30s); implement exponential backoff |

## 7. Usage with AI Agent + Image Gen

Common architecture: AI writes prompt, submits to image API, polls, outputs:

```
[Schedule Trigger]
    ↓
[AI Agent (LongCat/GPT): write creative prompt]
    ↓
[Code: extract prompt text]
    ↓
[HTTP POST: submit to image API]
    ↓
[Set: store task_id]
    ↓
[Wait 15s] → [HTTP GET: check status] → [IF done?]
                                              ├─ YES → [Format output]
                                              └─ NO  → [Wait 15s] (loop)
```
