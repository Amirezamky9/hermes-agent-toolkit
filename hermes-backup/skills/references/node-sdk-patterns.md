# n8n Workflow SDK — Complete Syntax Reference

> Load this when writing SDK code for a NEW workflow (create_workflow_from_code).
> Call: `skill_view('n8n-builder', file_path='references/node-sdk-patterns.md')`

## Import

```typescript
import { workflow, trigger, node, expr, switchCase, ifElse } from '@n8n/workflow-sdk';
```

## Every workflow starts with trigger() + .add()

```typescript
export default workflow('wf01-core-hub', 'WF01 - Core Hub')
  .add(trigger({
    type: 'n8n-nodes-base.telegramTrigger',
    version: 1.3,
    config: {
      name: 'Telegram Trigger',
      parameters: { updates: ['message', 'callback_query'] }
    }
  }))
  .to(node({
    type: 'n8n-nodes-base.code',
    version: 2,
    config: {
      name: 'Extract Input Data',
      parameters: {
        mode: 'runOnceForAllItems',
        jsCode: `const item = $input.first().json;
return [{ json: { chat_id: String(item.message?.chat?.id || item.callback_query?.message?.chat?.id || '') } }];`
      }
    }
  }));
```

## Node definitions (declare all, then build workflow)

### Telegram node (sendMessage)
```typescript
const sendWelcome = node({
  type: 'n8n-nodes-base.telegram',
  version: 2,
  config: {
    name: 'Send Welcome',
    parameters: {
      resource: 'message',
      operation: 'sendMessage',
      chatId: expr('$("Extract Input Data").first().json.chat_id'),
      text: 'Hello $json.first_name! Welcome to the bot! :coffee:'
    },
    credentials: { telegramApi: { id: credentialId, name: 'bale_bot_evet_rosteri' } }
  }
});
```

### Telegram node (editMessageText with inline keyboard)
```typescript
const editProducts = node({
  type: 'n8n-nodes-base.telegram',
  version: 2,
  config: {
    name: 'Edit Products',
    parameters: {
      resource: 'message',
      operation: 'editMessageText',
      chatId: expr('$("Extract Input Data").first().json.chat_id'),
      messageId: expr('$("Session Manager").first().json.last_message_id'),
      text: 'Our Products:',
      replyMarkup: 'inlineKeyboard',
      inlineKeyboard: {
        rows: [
          { row: { buttons: [{ text: '☕ قهوه ترک', additionalFields: { callback_data: 'view_product_1' } }] }},
          { row: { buttons: [{ text: '🏠 برگشت', additionalFields: { callback_data: 'back_to_menu' } }] }}
        ]
      }
    },
    credentials: { telegramApi: { id: credentialId, name: 'bale_bot_evet_rosteri' } }
  }
});
```

### Telegram node (answerCallbackQuery)
```typescript
const answerCbq = node({
  type: 'n8n-nodes-base.telegram',
  version: 2,
  config: {
    name: 'Answer Callback Query',
    parameters: {
      resource: 'callback',
      operation: 'answerQuery',
      callbackQueryId: expr('$json.callback_query.id')
    },
    credentials: { telegramApi: { id: credentialId, name: 'bale_bot_evet_rosteri' } }
  }
});
```

### Set node (manual mode)
```typescript
const formatText = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Format Welcome Text',
    parameters: {
      mode: 'manual',
      includeOtherFields: true,
      assignments: {
        assignments: [
          { id: 'a1', name: 'text', value: expr('"Hello " + $json.first_name'), type: 'string' }
        ]
      }
    }
  }
});
```

### Code node
```typescript
const extractData = node({
  type: 'n8n-nodes-base.code',
  version: 2,
  config: {
    name: 'Extract Input Data',
    parameters: {
      mode: 'runOnceForAllItems',
      jsCode: `const item = $input.first().json;
const msg = item.message || item;
const cbq = item.callback_query;
return [{ json: {
  chat_id: String(msg?.chat?.id || cbq?.message?.chat?.id || ''),
  text: msg?.text || '',
  callback_data: cbq?.data || '',
  message_id: msg?.message_id || cbq?.message?.message_id || 0,
  first_name: msg?.from?.first_name || '',
  callback_query_id: cbq?.id || ''
} }];`
    }
  }
});
```

### If node
```typescript
const userExists = ifElse({
  version: 2,
  config: {
    name: 'User Exists?',
    parameters: {
      conditions: {
        combinator: 'and',
        conditions: [
          { id: 'c1', leftValue: expr('$json.exists'), operator: { type: 'boolean', operation: 'true' }, rightValue: true }
        ],
        options: { caseSensitive: true, typeValidation: 'strict', version: 2 }
      }
    }
  }
});
```

### Switch node (Multi-output router)
The `switchCase()` function creates a Switch. `.onCase(index, targetNode)` connects each output.

```typescript
const routeByState = switchCase({
  version: 3,
  config: {
    name: 'Route by State',
    parameters: {
      dataType: 'string',
      value1: expr('$json.state'),
      rules: {
        combinator: 'and',
        conditions: [
          { id: 'c1', leftValue: expr('$json.state'), operator: { type: 'string', operation: 'equal' }, rightValue: 'idle' },
          { id: 'c2', leftValue: expr('$json.state'), operator: { type: 'string', operation: 'equal' }, rightValue: 'selecting_weight' },
          { id: 'c3', leftValue: expr('$json.state'), operator: { type: 'string', operation: 'equal' }, rightValue: 'checkout_address' }
        ],
        options: { caseSensitive: true, typeValidation: 'strict', version: 3 }
      },
      fallbackOutput: ''
    }
  }
});

export default workflow('wf01-core-hub', 'WF01 - Core Hub')
  .add(sessionManager)
  .to(routeByState
    .onCase(0, routeByType)    // output 0: idle → Route by Type
    .onCase(1, weightHandler)  // output 1: selecting_weight → Weight Handler
    .onCase(2, addressHandler) // output 2: checkout_address → Address Handler
    .onCase(3, errorHandler)   // output 3: fallback → Error Handler
  );
```

**CRITICAL:** Each `.onCase()` within the chain. Do NOT write `.onCase()` calls outside the `.to()` chain — validator loses the connections.

### Nested switches (route by state → route by type)
```typescript
export default workflow('wf01-core-hub', 'WF01 - Core Hub')
  .add(sessionManager)
  .to(routeByState
    .onCase(0, routeByType
      .onCase(0, answerCbq.to(sessionManager2))  // callback → Answer Callback
      .onCase(1, sendWelcome)                      // /start → Welcome
      .onCase(2, sendProducts)                     // /menu → Products
      .onCase(3, sendHelp)                         // /help → Help
      .onCase(4, cartHandler)                      // /cart → Cart
      .onCase(5, orderHandler)                      // /orders → Orders
      .onCase(6, adminHandler)                      // /admin → Admin
      .onCase(7, routeCallback)                     // text → Route Callback
    )
    .onCase(1, weightHandler)
    .onCase(2, addressHandler)
    .onCase(3, searchHandler)
    .onCase(4, executeAdmin)
    .onCase(5, errorHandler)
  );
```

### Execute Workflow node (sub-workflow)
```typescript
const executeAdmin = node({
  type: 'n8n-nodes-base.executeWorkflow',
  version: 2,
  config: {
    name: 'Execute Admin WF03',
    parameters: {
      source: 'database',
      workflowId: 'WORKFLOW_ID',  // Replace with actual ID after WF03 is created
      mode: 'each'
    }
  }
});
```

### DataTable node (SDK — only for create_workflow_from_code)
```typescript
const createSession = node({
  type: 'n8n-nodes-base.dataTable',
  version: 1.1,
  config: {
    name: 'Create Session',
    parameters: {
      resource: 'row',
      operation: 'upsert',
      primaryKey: 'telegram_id',
      dataTableId: { __rl: true, mode: 'id', value: 'TABLE_ID' },
      data: {
        keyValue: [
          { keyName: 'telegram_id', keyValue: expr('$("Extract Input Data").first().json.chat_id') },
          { keyName: 'state', keyValue: 'idle' }
        ]
      },
      options: { alwaysOutputData: true }
    }
  }
});
```

**⚠️ DataTable nodes work in SDK. They do NOT work via addNode (trap-37).**
Only create DataTable nodes through SDK. Never through addNode.

### AI Agent with OpenRouter
```typescript
const model = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatOpenRouter',
  version: 1.2,
  config: {
    name: 'OpenRouter Model',
    parameters: { model: 'google/gemini-2.5-flash', temperature: 0.7 },
    credentials: { openRouterApi: { id: credentialId, name: credentialName } }
  }
});

const agent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: {
    name: 'AI Support Agent',
    parameters: { promptType: 'define', text: 'You are a coffee shop assistant. پاسخ فارسی بده.' },
    subnodes: { model }
  }
});
```

---

## ⚠️ CRITICAL RULES for SDK

### Rule 1: No TypeScript annotations
❌ `function makeNode(name: string) {`
✅ `function makeNode(name) {`

### Rule 2: No function declarations — everything inline
❌ `function createPlaceholder(name, desc) { return node({...}); }`
✅ Each node as a separate `const` or inline

### Rule 3: No `settings` in SDK config
❌ `config: { name: 'X', parameters: {...}, settings: { onError: '...' } }`
✅ Create first, then `setNodeSettings` via `update_workflow`

### Rule 4: ≤20 nodes per create_workflow_from_code
If >20 nodes, split into skeleton + addNode batches.
Always verify actual count with `get_workflow_details` after create.

### Rule 5: Set credentials immediately after create
```typescript
// In SDK code, include credentials in each node:
credentials: { telegramApi: { id: '78sfmXZgmLK4r8lq', name: 'bale_bot_evet_rosteri' } }
```
Or immediately after create via `update_workflow` + `setNodeCredential`.

### Rule 6: expr() for expressions
```typescript
chatId: expr('$("Extract Input Data").first().json.chat_id')
```
NOT: `chatId: '$("Extract Input Data").first().json.chat_id'` (missing expr())

### Rule 7: jsCode is a backtick string, not an array
✅ ```jsCode: `const x = $input.first();` ```
❌ `jsCode: ['const x = ', '$input.first();']`

---

## Verifying after create

```typescript
get_workflow_details(workflowId)
// Check:
// - nodeCount matches what you wrote
// - trigger exists
// - connections are present
// - credentials are set (or set them now)
```
