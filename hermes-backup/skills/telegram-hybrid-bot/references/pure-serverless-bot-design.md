# Pure Serverless Bot: Maximum Capability Design ("Life Organizer")

A complete blueprint for a Telegram bot with **zero backend** — everything runs
inside Telegram Serverless using only the built-in SQLite + `sdk/fetch`.

## Capability Matrix

| Feature | Implementation | Limit/Boundary |
|---------|---------------|----------------|
| Smart notes with tags/categories | SQLite via `sdk/db` | None |
| Todo list with inline ✅/❌ buttons | SQLite + `api.sendMessage` reply_markup | None |
| Paginated lists | Track offset in callback_data | None |
| Inline search from any chat | `handlers/inline_query.js` | None |
| AI chat (Gemini/Claude/Groq) | `sdk/fetch` → external AI API | Needs free API key |
| Translation / summarization | Same as AI chat — separate prompt | Depends on AI API |
| Personal stats dashboard | SQLite aggregate queries | None |
| Multi-language | `user.lang` column → conditional strings | None |
| Category filter buttons | Inline keyboard + callback routing | None |
| User preferences | JSON column in users table | None |
| **File download from user** | ❌ Not supported by Serverless | Requires backend |
| **File upload to user** | ❌ Not supported by Serverless | Requires backend |
| **Scheduled reminders** | ❌ No cron/serverless | Requires backend |
| **Postgres / external DB** | ❌ Only built-in SQLite | Requires backend |

## Schema Pattern (4 tables)

```js
// schema.js — minimal viable schema for a personal bot
import { table, integer, text, json, boolean, sql, index } from 'sdk/db';

export const users = table('users', {
  tgId:      integer('tg_id').primaryKey(),
  lang:      text('lang').default('fa'),
  prefs:     json('prefs').default({}),
  stats:     json('stats').default({ notes:0, done:0 }),
  createdAt: integer('created_at', { mode: 'timestamp' })
               .default(sql`(unixepoch())`),
});

export const notes = table('notes', {
  id:       integer('id').primaryKey({ autoIncrement: true }),
  userId:   integer('user_id').notNull(),
  text:     text('text').notNull(),
  category: text('category').default('general'),
  tags:     json('tags').default([]),
  isUrl:    boolean('is_url').default(false),
  url:      text('url'),
  createdAt: integer('created_at', { mode: 'timestamp' })
               .default(sql`(unixepoch())`),
}, (t) => ({
  userIdx:  index('idx_notes_user').on(t.userId),
}));

export const todos = table('todos', {
  id:       integer('id').primaryKey({ autoIncrement: true }),
  userId:   integer('user_id').notNull(),
  text:     text('text').notNull(),
  category: text('category').default('general'),
  priority: integer('priority').default(0),
  done:     boolean('done').default(false),
  createdAt: integer('created_at', { mode: 'timestamp' })
               .default(sql`(unixepoch())`),
  doneAt:   integer('done_at', { mode: 'timestamp' }),
}, (t) => ({
  userTodoIdx: index('idx_todos_user').on(t.userId),
}));

export const aiChats = table('ai_chats', {
  id:       integer('id').primaryKey({ autoIncrement: true }),
  userId:   integer('user_id').notNull(),
  role:     text('role').notNull(),
  text:     text('text').notNull(),
  tokens:   integer('tokens').default(0),
  createdAt: integer('created_at', { mode: 'timestamp' })
               .default(sql`(unixepoch())`),
}, (t) => ({
  userAiIdx: index('idx_ai_user').on(t.userId),
}));
```

## Classifier Pattern

The key to a seamless UX: classify every incoming message without requiring
explicit commands.

```js
// lib/classifier.js
const LOCAL_PATTERNS = [
  /^\/start$/, /^\/help$/, /^\/settings/,
  /^(hi|hello|hey|سلام|خوبی|چطوری)$/i,
];
const LONG_TEXT_THRESHOLD = 200; // characters

export function classify(text, userPrefs) {
  for (const p of LOCAL_PATTERNS) if (p.test(text)) return 'local';

  // Explicit commands
  if (text.startsWith('/note')) return 'save_note';
  if (text.startsWith('/ask'))  return 'ask_ai';
  if (text.startsWith('/todo')) return 'add_todo';
  if (text.startsWith('/bookmark')) return 'save_bookmark';

  // Smart default: short text = note, long or question = AI query
  if (text.length < 100 && !text.includes('?') && !text.includes('چرا'))
    return 'save_note';
  return 'ask_ai';
}
```

## AI API Proxy Pattern

```js
// lib/ai.js — uses free Gemini API, no backend needed
import { fetch } from 'sdk';

const GEMINI_KEY = process.env.GEMINI_API_KEY;

export async function askAI(prompt) {
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/` +
    `gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
      }),
    }
  );
  const data = await res.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text ?? '(no response)';
}
```

Free AI providers suitable for serverless `fetch`:
- **Google Gemini API** — free tier, 60 req/min, `gemini-2.0-flash`
- **Groq Cloud** — free tier, Llama 3/Mixtral, 30 req/min
- **DeepSeek** — very cheap, GPT-4-class model at 1/20 cost
- **OpenAI** — paid but `gpt-4o-mini` is inexpensive

## Inline Keyboard Pagination Pattern

```js
// In handlers — paginated note list
async function showNotes(chatId, userId, page = 0) {
  const all = await db.select().from(notes)
    .where(eq(notes.userId, userId))
    .orderBy(desc(notes.createdAt)).all();
  const chunk = all.slice(page * 5, (page + 1) * 5);
  const totalPages = Math.ceil(all.length / 5);

  const rows = chunk.map(n => ([{
    text: `📌 ${n.text.slice(0, 30)}`,
    callback_data: `view_note_${n.id}`,
  }]));

  if (totalPages > 1) rows.push([
    { text: '⬅️', callback_data: `page_notes_${page - 1}` },
    { text: `${page + 1}/${totalPages}`, callback_data: 'noop' },
    { text: '➡️', callback_data: `page_notes_${page + 1}` },
  ]);

  await api.sendMessage({
    chat_id: chatId,
    text: `📚 Notes (page ${page + 1}/${totalPages})`,
    reply_markup: { inline_keyboard: rows },
  });
}
```

## Handler Map

```
handlers/
├── message.js         # main entry — classifier → route
├── callback_query.js  # all button clicks: done/delete/view/page/settings
├── inline_query.js    # search from any chat (Inline Mode)
└── my_chat_member.js  # welcome new users
```
