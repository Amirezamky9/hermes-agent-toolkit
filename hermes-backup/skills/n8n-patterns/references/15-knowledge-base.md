# Best Practices: Knowledge Base (RAG)

> Technique key: `knowledge_base` — Building a centralized information collection using vector stores for LLM-powered question answering (RAG)

---

## ۱. معماری کلی

```
دو workflow مجزا:

1. INGESTION: Source → Load → Split → Embed → Vector Store
2. QUERY:      User Question → AI Agent → Retrieval → Answer
```

| مرحله | نودهای n8n |
|-------|-----------|
| **Source** | هر trigger (Webhook, Schedule, File, HTTP) |
| **Load** | Default Data Loader / Binary Input Loader / JSON Input Loader / GitHub |
| **Split** | Recursive Character Text Splitter / Token Splitter / Character Text Splitter |
| **Embed** | Embeddings OpenAI / Cohere / Ollama / AWS Bedrock |
| **Store** | Simple Vector Store / Pinecone / PGVector / Redis / Supabase / MongoDB Atlas / Zep |

---

## ۲. Vector Storeها — مقایسه

| Vector Store | Credential | Self-host | Best for |
|-------------|:----------:|:---------:|----------|
| **Simple Vector Store** | ❌ | built-in | **پیش‌نهادی برای شروع** — تست و prototype |
| **Pinecone** | ✅ API Key | ❌ | Production مقیاس‌پذیر |
| **PGVector (Postgres)** | ✅ DB cred | ✅ | RAG در自家 دیتابیس |
| **Redis** | ✅ host/port | ✅ | Cache + Vector |
| **Supabase** | ✅ API Key | ✅ | Supabase users |
| **MongoDB Atlas** | ✅ ConnStr | ❌ | Document + Vector |
| **Zep** | ✅ API Key | ❌ | Long-term memory تخصصی |

### Simple Vector Store
> بهترین گزینه برای شروع و prototype. بدون credential، داخل خود n8n کار می‌کنه.

| mode | توضیح |
|------|-------|
| `insert` | اسناد رو ذخیره کن |
| `load` | جستجوی تشابه (similarity search) |
| `retrieve-as-tool` | **حالت RAG استاندارد** — به AI Agent وصلش کن |
| `retrieve` | به عنوان subnode.vectorStore برای Chain |

### سایر Vector Stores
همه از pattern مشابه پیروی می‌کنن: `insert` برای ذخیره، `retrieve-as-tool` برای Agent. تفاوت در external dependency.

---

## ۳. Document Loaderها

| Loader | ورودی | مناسب برای |
|--------|-------|-----------|
| **Default Data Loader** | `$json` از نود قبلی | JSON, CSV, دیتای پردازش‌شده |
| **Binary Input Loader** | فایل باینری | PDF, DOCX, TXT آپلود شده |
| **JSON Input Loader** | JSON struct خاص | ساختار مشخص |
| **GitHub** | مخزن GitHub | داکیومنت‌های کد |

> **پیشنهادی:** Binary Input Loader برای فایل‌های PDF/DOCX + Default Data Loader برای API data.

---

## ۴. Text Splitterها — chunk کردن اسناد

| Splitter | نحوه | chunkSize پیشنهادی |
|----------|------|:------------------:|
| **Recursive Character Text Splitter** | بر اساس پاراگراف -> جمله -> کاراکتر | ۵۰۰-۱۰۰۰ |
| **Character Text Splitter** | صرفاً بر اساس تعداد کاراکتر | ۵۰۰ |
| **Token Splitter** | بر اساس token (هماهنگ با LLM) | ۲۰۰-۵۰۰ |

> **پیشنهادی:** `RecursiveCharacterTextSplitter` با `chunkSize: 800` و `chunkOverlap: 100`. balance خوبی داره بین coherence و granularity.

---

## ۵. Embedding Models

| Embedding | Credential | Cost | Best for |
|-----------|:----------:|:----:|----------|
| **OpenAI** (`text-embedding-3-small`) | ✅ API Key | کم | استاندارد |
| **Cohere** (`embed-english-v3.0`) | ✅ API Key | کم | متن انگلیسی |
| **Ollama** | ❌ (local) | رایگان | Self-host, privacy |
| **AWS Bedrock** | ✅ AWS Keys | متغیر | داخل AWS |
| **Lemonfox** | ✅ API Key | کم | multilingual? |

> **پیشنهادی:** OpenAI Embeddings برای سادگی. Ollama برای local.

---

## ۶. RAG Pipeline — INGESTION

```
[Source: API / File / Webhook]
  ↓
[Binary Input Loader / Default Data Loader]
  ↓
[Recursive Character Text Splitter: chunkSize=800, overlap=100]
  ↓
[Embeddings OpenAI: model="text-embedding-3-small"]
  ↓
[Simple Vector Store: mode=insert | Pinecone: insert | ...]
```

**ورودی Splitter به Store:**
```
Splitter output → { "pageContent": "متن چانک شده", "metadata": { "source": "...", "index": 0 } }
```

---

## ۷. RAG Pipeline — QUERY (Chat + Agent)

```
[Telegram Trigger / Webhook]
  ↓
[AI Agent]
  │  Model: OpenAI Chat Model (gpt-4o / gpt-4o-mini)
  │  System Prompt: "You are a helpful assistant. Use the vector store tool to find relevant documents."
  │  subnodes:
  │    tools: [Vector Store Tool] ← mode=retrieve-as-tool
  │    memory: [Redis Chat Memory / Window Buffer Memory]
  │
  ↓
[AI Agent Response → Telegram/Webhook]
```

### اتصال Vector Store به Agent

```
[AI Agent]
  subnodes:
    vectorStore: Simple Vector Store (mode: retrieve-as-tool)
    └── یا از Vector Store Retriever + Tool Vector Store
```

**جریان Query:**
1. کاربر سوال می‌پرسه
2. Agent سوال رو به embedding تبدیل می‌کنه
3. Vector Store closest chunks رو برمی‌گردونه
4. Agent context + سوال رو می‌بینه → پاسخ می‌ده

---

## ۸. پترن‌های Ingestion

### ۸.۱. Manual Upload → Store
```
[Webhook: فایل PDF/DOCX]
  → [Binary Input Loader: convert to text]
  → [Recursive Character Text Splitter: 800/100]
  → [Embeddings OpenAI]
  → [Simple Vector Store: insert]
  → [Response: "فایل پردازش شد ({chunks} chunk)"]
```

### ۸.۲. Website Scrape → Store
```
[Schedule: هر ۶ ساعت]
  → [HTTP Request: GET یک صفحه]
  → [Default Data Loader]
  → [Recursive Character Text Splitter]
  → [Embeddings OpenAI]
  → [Pinecone: insert]
```

### ۸.۳. CSV → Knowledge Base
```
[Schedule: روزانه]
  → [Read Binary Files: folder با CSV]
  → [Code: هر ردیف CSV رو به document تبدیل کن]
  → [Default Data Loader]
  → [Splitter → Embed → Store]
```

### ۸.۴. GitHub Docs → RAG
```
[GitHub Document Loader]
  → [Token Splitter]
  → [Embeddings Cohere]
  → [Supabase Vector Store: insert]
```

---

## ۹. پترن‌های Query

### ۹.۱. Chat Bot ساده
```
[Telegram Trigger: سوال کاربر]
  → [AI Agent]
      systemPrompt: "از knowledge base جواب بده. اگه جواب نبود بگو نمی‌دونم."
      tools: [Vector Store Tool (Simple Vector Store, mode: retrieve-as-tool)]
      memory: [Window Buffer Memory (last 10 messages)]
  → [Telegram: sendMessage (answer)]
```

### ۹.۲. API Question Answering
```
[Webhook: { question: "..." }]
  → [AI Agent]
      tools: [Vector Store Tool]
  → [Webhook Response: { answer: "...", sources: [...] }]
```

### ۹.۳. Report Generation from KB
```
[Schedule: هفتگی]
  → [AI Agent]
      systemPrompt: "Summarize the knowledge base about topic X"
      tools: [Vector Store Tool (mode: load, k=50)]
  → [Email: send report]
```

### ۹.۴. Multi-KB با Routing
```
[Switch: موضوع سوال]
  ├─ docs → [Agent with Simple Vector Store (documents)]
  ├─ faq → [Agent with Simple Vector Store (faq)]
  ├─ code → [Agent with GitHub Loader + Pinecone]
  └─ default → [Agent بدون RAG]
```

---

## ۱۰. Chat Memory برای RAG

| Memory | Persistence | Best for |
|--------|:-----------:|----------|
| **Window Buffer Memory** | in-memory | چت موقت |
| **Redis Chat Memory** | Redis | Session persistence |
| **MongoDB Chat Memory** | MongoDB | Production |
| **Postgres Chat Memory** | Postgres | Production + audit |

> **نکته:** Memory رو از طریق `Chat Memory Manager` (mode: load/insert/delete) مدیریت کن.

---

## ۱۱. تله‌ها

| # | تله | راه‌حل |
|---|-----|--------|
| 1 | **Chunks بیش از حد بزرگ** | `chunkSize > 1000` باعث degraded retrieval می‌شه. ۸۰۰ رو نگه دار |
| 2 | **Chunks بیش از حد کوچک** | `chunkSize < 200` یعنی context کم. حداقل ۵۰۰ |
| 3 | **فراموشی overlap** | `chunkOverlap: 100` برای continuity |
| 4 | **Simple Vector Store حافظه‌ست** | داده در RAM — بعد از restart n8n از بین می‌ره. برای production از Pinecone/PGVector استفاده کن |
| 5 | **Embedding model mismatch** | برای ingest و query از embedding یکسان استفاده کن |
| 6 | **Metadata lost** | metadata رو توی Splitter حفظ کن: `{ source, index, date, ... }` |
| 7 | **Agent system prompt بدون RAG instruction** | حتماً بگو: "از vector store استفاده کن اگه جواب رو می‌دونی" |
| 8 | **Rate limit Embedding API** | برای bulk ingestion, batch با delay بفرست |
| 9 | **File format پشتیبانی‌نشده** | Binary Input Loader فقط متن رو extract می‌کنه. PDF/image OCR نیاز به Step Function |
| 10 | **حذف اسناد قدیمی از Vector Store** | Simple Vector Store replace نمی‌کنه. Pinecone/PGVector با ID آپدیت کن |

---

## خلاصه

```
شروع سریع (بدون Credential):
  Source → [Default Data Loader] → [RecursiveCharSplitter: 800/100]
    → [Embeddings OpenAI] → [Simple Vector Store: insert]

  Chat Agent:
    [Telegram] → [AI Agent + Vector Store Tool (retrieve-as-tool)]
    → [Telegram: answer]

Production:
  Ingest:  Binary Loader → Splitter → Embed → Pinecone/PGVector
  Query:   Agent + Vector Store Tool + Redis Memory
```

> **نکته کلیدی:** همیشه از دو workflow جدا استفاده کن — یکی برای ingest، یکی برای query. ingest رو با Schedule اجرا کن، query رو با Trigger.