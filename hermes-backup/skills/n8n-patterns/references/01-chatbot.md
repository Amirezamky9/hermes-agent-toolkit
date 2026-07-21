# Pattern: Chatbot — ربات‌های چت هوشمند (AI Agent)

> Technique key: `chatbot`
> این پترن برای ربات‌هایی هست که با **AI Agent** کار می‌کنن — چه چت ساده، چه ربات تلگرام با Agent، چه فرم‌های هوشمند.

---

## ۱. معرفی

ربات چتی که از AI Agent استفاده می‌کنه. می‌تونه:
- سوال جواب ساده بده
- از **tools** استفاده کنه (API، دیتابیس، سرچ)
- **حافظه** داشته باشه
- با **Execute Sub-workflow** به ورک‌فلوهای دیگه وصل بشه
- از طریق **Webhook** صدا زده بشه

**با Telegram Bot Pattern فرق داره:** اینجا Agent تصمیم می‌گیره چیکار کنه. توی Telegram Bot، خودمون مسیریابی رو با Switch می‌کنیم.

---

## ۲. Triggerها (ورودی‌ها)

ربات چت می‌تونه از چند طریق ورودی بگیره:

### a) Chat Trigger (n8n داخلی)
اگه کاربر فقط گفت "chatbot" بدون اسم پلتفرم → از Chat Trigger استفاده کن

### b) Telegram Trigger
```typescript
نوع: n8n-nodes-base.telegramTrigger
تنظیمات:
  updates: ["message", "callback_query"]
  createSession: true  // session خودکار
```

### c) Webhook Trigger
```typescript
نوع: n8n-nodes-base.webhook
httpMethod: POST  // یا GET
responseMode: "responseNode"  // برای پاسخ با Respond to Webhook
```

### d) Execute Workflow Trigger (ساب‌ورک‌فلو)
وقتی یه ورک‌فلو دیگه این ورک‌فلو رو صدا می‌زنه:
```
نوع: n8n-nodes-base.executeWorkflowTrigger
ورودی: workflow inputs (از WF والد میاد)
```

> **نکته مهم:** وقتی ربات چت به عنوان sub-workflow صدا زده می‌شه،
> **خودش نباید به کاربر پیام بده** — فقط داده برمی‌گردونه.
> WF والد پیام رو می‌فرسته.

---

## ۳. معماری پایه

```
[Trigger] → [AI Agent] → [Respond]
                 ↓
          ┌──────┴──────┐
          │              │
     [Chat Model]   [Memory/Tools]
```

### گام به گام:

1. **Trigger** — پیام کاربر رو می‌گیره
2. **System Prompt** — پرامپت سیستمی Agent رو تنظیم می‌کنه
3. **AI Agent** — منطق اصلی:
   - ورودی: پیام کاربر + context
   - خروجی: پاسخ متن یا JSON
   - subnodes: model, memory, tools, outputParser
4. **Respond** — پاسخ به کاربر (sendMessage / respondToWebhook / بازگشت خروجی)

---

## ۴. AI Agent — ساختار کامل

### پارامترهای اصلی AI Agent (v3.1)

| پارامتر | توضیح | پیش‌فرض |
|---------|-------|---------|
| `promptType` | auto (خودکار از trigger) یا define (دستی) | auto |
| `text` | متن پرامپت کاربر (فقط وقتی promptType=define) | — |
| `hasOutputParser` | خروجی ساختاریافته JSON | false |
| `needsFallback` | مدل fallback داره؟ | false |

### تنظیمات (options)

| تنظیم | توضیح | مقدار پیشنهادی |
|-------|-------|---------------|
| `systemMessage` | دستور سیستمی Agent | بسته به کاربرد |
| `maxIterations` | حداکثر تعداد iteration | 10 |
| `returnIntermediateSteps` | نمایش مراحل میانی | false |
| `enableStreaming` | استریم پاسخ | true |
| `passthroughBinaryImages` | ارسال خودکار عکس به Agent | true |
| `maxTokensFromMemory` | محدودیت توکن از حافظه | 0 (همه) |
| `batchSize` | پردازش همزمان (rate limiting) | 1 |
| `delayBetweenBatches` | تأخیر بین batchها | 0 |

### subnodes (کامپوننت‌های Agent)

```
┌─────────────────────┐
│      AI Agent       │
├─────────────────────┤
│ Chat Model(s)  ◄────│──── model[] (required)
│ Memory         ◄────│──── memory (optional)
│ Tools          ◄────│──── tools[] (optional)
│ Output Parser  ◄────│──── outputParser (hasOutputParser=true)
└─────────────────────┘
```

---

## ۵. Chat Model — نودهای مدل زبانی

### مدل‌های پشتیبانی شده:

| نود | توضیح |
|-----|-------|
| `lmChatOpenAi` | OpenAI (GPT) |
| `lmChatGoogleGemini` | Google Gemini |
| `lmChatDeepSeek` | DeepSeek |
| `lmChatGroq` | Groq |
| `lmChatMistralCloud` | Mistral |
| `lmChatOllama` | Ollama (محلی) |
| `lmChatCohere` | Cohere |
| `lmChatXAiGrok` | xAI Grok |
| `lmChatMoonshot` | Moonshot Kimi |
| `modelSelector` | انتخاب مدل بر اساس داده |

> **نکته:** Agent می‌تونه **چند مدل** داشته باشه. اولی اصلی، بقیه fallback.

### Fallback Model

برای fallback:
1. دو تا `lmChat*` به Agent وصل کن
2. پارامتر `needsFallback: true` رو بذار
3. Agent اگه اولی جواب نداد، می‌ره سراغ دومی

> **مهم:** `needsFallback` پارامتر مستقیم Agent هست.
> در SDK از `model: [mainModel, fallbackModel]` استفاده کن.

---

## ۶. System Prompt — تنظیم پرامپت

از پارامتر `systemMessage` توی options Agent:

### ساختار پرامپت پیشنهادی:

```
شما یک [نقش] هستید.
وظیفه شما: [توضیح]

اطلاعات مفید:
- [اطلاعات ثابت]

ابزارهای در دسترس:
- [نام tool] : [توضیح]

نحوه پاسخ:
- پاسخ نهایی رو با [tool_name] به کاربر بده
- همیشه مودب و حرفه‌ای پاسخ بده
- اگه از چیزی مطمئن نیستی، بپرس

زبان: فارسی
```

### نکات پرامپت نویسی:

- **نام دقیق ابزارها رو توی پرامپت بگو** تا Agent بلد باشه ازشون استفاده کنه
- اگه Agent باید با یه tool پاسخ بده، توی پرامپت بگو
- context کاربر رو با expression بده: `{{ $json.chat_id }}`

---

## ۷. Tools — ابزارهای Agent

Agent می‌تونه tools داشته باشه که ازشون استفاده کنه:

### Toolهای built-in:

| نود | کاربرد |
|-----|--------|
| `httpRequest` | API خارجی |
| `dataTable` | خوندن/نوشتن Data Table |
| `postgres` / `mySql` | دیتابیس |
| `telegram` | ارسال پیام به کاربر |
| `slack` | پیام به اسلک |
| `serpApi` | جستجوی وب |
| `perplexityTool` | جستجوی AI |
| `code` | پردازش سفارشی |

### Custom Tool:

Agent Tool (`@n8n/n8n-nodes-langchain.agentTool`) رو می‌تونی به Agent وصل کنی تا از sub-workflow دیگه به عنوان tool استفاده کنه.

> `ai_tool` connection — ابزار رو به Agent وصل کن.

---

## ۸. Memory — حافظه

Agent نیاز به حافظه داره تا مکالمه رو حفظ کنه.

### انواع Memory:

| Memory | توضیح |
|--------|-------|
| `memoryBufferWindow` (Simple Memory) | حافظه ساده با محدودیت پیام |
| `postgresChatMemory` | حافظه دائمی در PostgreSQL |
| `redisChatMemory` | حافظه در Redis |

### Session Key:

```typescript
// Telegram:
sessionIdType: "customKey"
sessionKey: nodeJson(telegramTrigger, 'message.chat.id')

// n8n Chat Trigger:
sessionIdType: "fromInput"
// sessionKey رو نذار — trigger خودش می‌ده

// Webhook:
sessionIdType: "customKey"
sessionKey: expression از body
```

### نکات:
- **از `$json` برای sessionKey توی memory subnode استفاده نکن** — memory subnode دسترسی مستقیم نداره
- همیشه از `nodeJson(triggerNode, 'path')` استفاده کن
- `maxTokens` رو تنظیم کن تا context محدود بشه

---

## ۹. Output Parser — خروجی ساختاریافته

وقتی `hasOutputParser: true` باشه، Agent نیاز به outputParser داره.

| Output Parser | توضیح |
|---------------|-------|
| `outputParserStructured` (v1.3) | خروجی JSON با schema مشخص |
| `outputParserItemList` | خروجی به صورت آیتم‌های جداگانه |

### نکات:
- خروجی Structured توی key `output` میاد: `{ "output": { ... } }`
- توی نودهای بعدی: `$json.output.fieldName`

---

## ۱۰. Respond — خروجی‌ها

Agent می‌تونه به این روش‌ها پاسخ بده:

### ۱. Output مستقیم (text یا JSON)
خروجی Agent توی `$json.output` میاد.

### ۲. Tool response
Agent با یه tool (مثل Telegram sendMessage) پاسخ میده.
> **نکته:** توی system prompt بگو: `"پاسخ نهایی رو با [tool_name] به کاربر بده"`

### ۳. Response به webhook
وقتی trigger = webhook با `responseMode: "responseNode"`:
- بعد از Agent → `respondToWebhook`

### ۴. خروجی به WF والد
وقتی sub-workflow هست:
- آخرین Set نود = output → WF والد می‌گیره

---

## ۱۱. Memory Session Keys (از MCP)

| Platform | Session Key |
|----------|-------------|
| Telegram | `nodeJson(telegramTrigger, 'message.chat.id')` |
| Slack | `nodeJson(slackTrigger, 'event.channel')` |
| WhatsApp | `nodeJson(whatsAppTrigger, 'messages.0.from')` |
| n8n Chat Trigger | `fromInput` (بدون custom key) |

---

## ۱۲. Execute Sub-workflow (وقتی chatbot sub-workflow هست)

وقتی chatbot به عنوان sub-workflow استفاده می‌شه:

```
WF Parent:
  → [Execute Workflow] (waitForSubWorkflow: true/false)
  
WF Child (chatbot):
  → [Execute Workflow Trigger]
  → [AI Agent]
  → [Set: خروجی]
```

### waitForSubWorkflow:
| مقدار | توضیح |
|-------|--------|
| `true` | والد صبر می‌کنه، خروجی رو می‌گیره و خودش response می‌ده |
| `false` | والد صبر نمی‌کنه، فرزند خودش response می‌ده |

---

## ۱۳. خطاهای رایج (از MCP)

### 🕳️ Leaving Chatbot Disconnected
اگه chatbot با schedule trigger مشترک باشه، chatbot رو حتماً به data source وصل کن.

### 🕳️ Mixing Trigger/Response Types
اگه Telegram تریگر هست → با Telegram جواب بده.

### 🕳️ $json در Memory Subnode
توی memory subnode از `$json` استفاده نکن — از `nodeJson()` استفاده کن.

### 🕳️ نداشتن Fallback Model
اگه model اصلی خطا داد، یه fallback model داشته باش.

---

## ۱۴. Guardrails — امنیت ورودی و خروجی Agent

> نود: `@n8n/n8n-nodes-langchain.guardrails` (v2)
> **محل قرارگیری:** بین Trigger و AI Agent — قبل از اینکه ورودی به Agent برسه.

### دو عملیات:

| عملیات | توضیح | خروجی |
|--------|-------|-------|
| **classify** | بررسی متن ورودی با قوانین امنیتی | خروجی ۰ = Pass ✅ / خروجی ۱ = Fail ❌ |
| **sanitize** | پاک‌سازی و ماسک کردن داده‌های حساس | یک خروجی (داده پاک‌سازی شده) |

### قوانین قابل تنظیم (classify):

| گاردریل | توضیح | پیش‌فرض |
|---------|-------|---------|
| **keywords** | کلمات کلیدی ممنوعه (کاما جدا) | — |
| **jailbreak** | تشخیص تلاش برای bypass امنیت | threshold: 0.7 |
| **nsfw** | تشخیص محتوای نامناسب | threshold: 0.7 |
| **pii** | تشخیص اطلاعات شخصی (همه یا انتخابی) | all |
| **secretKeys** | تشخیص کلیدهای API، توکن و رمز | balanced |
| **topicalAlignment** | خروج از محدوده کسب‌وکار | threshold: 0.7 |
| **urls** | بلاک/محدود کردن URLها | فقط https مجاز |
| **custom** | گاردریل سفارشی با پرامپت دلخواه | — |
| **customRegex** | regex سفارشی | — |

### subnode مورد نیاز:

```
Guardrails (classify)
  ├── model: ChatModel   ← برای گاردریل‌های jailbreak, nsfw, topicalAlignment, custom
  ├── output 0 (Pass) → AI Agent
  └── output 1 (Fail) → Fallback Handler
```

### معماری پیشنهادی با Guardrails:

```
[Trigger]
    ↓
[Guardrails (classify)]
    ├── (Pass) → [AI Agent] → [Respond]
    └── (Fail) → [Fallback: "درخواست شما قابل پردازش نیست"]
```

### نکات:
- **PI detection بدون model کار می‌کنه** — فقط با متن
- **jailbreak, nsfw, topicalAlignment, custom** نیاز به Chat Model subnode دارن
- **sanitize** یک خروجی داره (داده ماسک شده)
- **threshold** از ۰.۰ تا ۱.۰ — هر چی پایین‌تر، حساسیت بیشتر

---

