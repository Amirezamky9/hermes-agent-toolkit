# Automation & AI Domain Terminology for Persian Resumes

Accurate domain descriptions sourced from Wikipedia, official docs, and professional resume samples. 
Use these when writing Persian resumes for Automation/AI engineers — do NOT guess.

## n8n (Workflow Automation)

**Source:** https://en.wikipedia.org/wiki/N8n

| Aspect | Detail |
|--------|--------|
| Type | Fair-code workflow automation platform |
| Founded | 2019, Berlin |
| Founder | Jan Oberhauser |
| Funding | $180M Series C (2025), $2.5B valuation — backed by Sequoia, Accel, Nvidia NVentures |
| Description | Visual node-based editor connecting 400+ apps/services + AI models. Self-hosted or cloud. JavaScript/Python code nodes |
| Positioning | Open-source alternative to Zapier, Make (formerly Integromat) |
| Built on | Node.js + TypeScript |

**Resume-ready description (Persian):**
«پلتفرم Fair-Code اتوماسیون گردش کار با بیش از ۴۰۰ اتصال آماده، ویرایشگر گرافیکی گره‌محور، قابلیت خودمیزبانی و پشتیبانی از کدهای Python/JavaScript»

**Resume-ready description (English):**
"Fair-code workflow automation platform connecting 400+ integrations via a visual node-based editor, with JavaScript/Python code node support"

## Hermes Agent

**Source:** https://hermes-agent.ai

| Aspect | Detail |
|--------|--------|
| Type | Open-source AI Agent framework |
| Creator | Nous Research |
| License | MIT |
| GitHub | github.com/NousResearch/hermes-agent (10k+ stars) |
| Key features | Persistent memory across sessions, reusable Skills, cron jobs, tools, 24 messaging platforms (Telegram, Discord, Slack, etc.) |
| Distinction | "Self-improving AI agent" — creates skills from experience, learns user preferences |

**Resume-ready description (Persian):**
«فریم‌ورک متن‌باز عامل هوشمند (AI Agent) از Nous Research با حافظه ماندگار، مهارت‌های قابل استفاده مجدد، زمانبندی وظایف و اتصال به پلتفرم‌های پیام‌رسان متعدد»

## RAG (Retrieval-Augmented Generation)

**Source:** https://en.wikipedia.org/wiki/Retrieval-augmented_generation

| Aspect | Detail |
|--------|--------|
| Type | AI/LLM technique |
| First proposed | 2020 |
| Purpose | Enables LLMs to retrieve external information before generating responses |
| Mechanism | Query → Document retrieval from vector database/knowledge base → LLM generation with retrieved context |
| Benefit | Reduces hallucinations, allows domain-specific knowledge without retraining, provides source citations |
| Components | Embedding model, vector database, retriever, LLM, prompt template |

**Resume-ready description (Persian):**
«سیستم Retrieval-Augmented Generation — تکنیکی که مدل‌های زبانی بزرگ (LLM) را با پایگاه دانش خارجی ترکیب می‌کند تا پاسخ‌های دقیق، مستند و مبتنی بر منابع موثق تولید کند. کاهش خطاهای توهم (Hallucination) و ارائه پاسخ بر اساس دانش سازمانی»

## RAG Agent / Intelligent Agent

A RAG Agent is a software entity that:
1. Receives a user query
2. Retrieves relevant context from a knowledge base (vector DB, documents, website)
3. Feeds query + context to an LLM
4. Returns a grounded, source-cited answer

**Resume-ready description (Persian):**
«عامل هوشمند مبتنی بر Retrieval-Augmented Generation — سامانه‌ای که پرسش کاربر را دریافت کرده، دانش مرتبط را از پایگاه داده برداری/اسناد بازیابی می‌کند، و با ترکیب آن زمینه با مدل زبانی بزرگ، پاسخی دقیق با استناد به منابع تولید می‌کند»

## Digital Worker

A Digital Worker is an autonomous software bot that performs business processes — web scraping, data entry, form filling, API calls — without human intervention. Often built with n8n, Python, or RPA tools.

**Resume-ready description (Persian):**
«کارگر دیجیتال (Digital Worker) — عامل نرم‌افزاری خودکار که وظایف مبتنی بر وب (اسکرپینگ، استخراج داده، پر کردن فرم، فراخوانی API) را بدون دخالت انسان انجام می‌دهد. طراحی و پیاده‌سازی شده با n8n و ابزارهای مدرن اتوماسیون»

## Telegram Bot / ربات تلگرام

| Aspect | Detail |
|--------|--------|
| API | https://core.telegram.org/bots/api |
| Type | HTTP-based interface for Telegram bot development |
| Capabilities | Send/receive messages, inline queries, webhooks, keyboards, payments, media |
| Languages | Any language with HTTP client — Python (python-telegram-bot, aiogram), Node.js, etc. |

**Resume-ready description (Persian):**
«طراحی و توسعه ربات تلگرام با استفاده از Telegram Bot API پیاده‌سازی قابلیت‌هایی نظیر پیام‌رسانی خودکار، منوهای تعاملی، webhook، پاسخگویی هوشمند و اتصال به سرویس‌های خارجی»

## BigQuery (Google Cloud)

| Aspect | Detail |
|--------|--------|
| Type | Serverless, highly scalable data warehouse |
| Part of | Google Cloud Platform |
| Key features | SQL-based analytics on petabyte-scale data, real-time analysis, built-in ML |
| Resume use | "تحلیل داده در مقیاس با BigQuery و نوشتن کوئری‌های SQL پیشرفته" |

## PostgreSQL

| Aspect | Detail |
|--------|--------|
| Type | Advanced open-source relational database |
| Key features | ACID-compliant, SQL, JSON support, full-text search, extensions (PostGIS, pgvector) |
| Resume use | "طراحی و بهینه‌سازی پایگاه داده رابطه‌ای PostgreSQL — ایجاد جداول، روابط، ایندکس‌ها و کوئری‌های پیشرفته SQL" |

---

## Web Scraping / اسکرپینگ وب

Professional terminology for resume:
- «فناوری اطلاعات، استخراج و جمع‌آوری داده» → "Web Scraping"
- «اسکرین اسکرول» → "Automated Data Extraction" or "Web Crawling"
- For modern JS-heavy sites: "Dynamic web scraping with headless browser automation"
- For n8n-based: "Automated data collection workflows using n8n HTTP and HTML Extract nodes"

## Resume Action Verbs (English, for mixed resumes)

Use these instead of generic verbs:

| Weak | Strong |
|------|--------|
| Was responsible for | Designed, Implemented, Led |
| Made | Built, Developed, Engineered |
| Helped with | Optimized, Automated, Streamlined |
| Used | Deployed, Integrated, Architected |
| Did | Delivered, Orchestrated, Executed |

## Color Palette for Professional Persian Resumes

| Element | Color | Hex |
|---------|-------|-----|
| Header / Primary text | Dark navy | #19376D |
| Accent / Lines | Blue | #2970C6 |
| Body text | Near-black | #212529 |
| Muted text (dates) | Gray | #6C757D |
| Header background | Light gray | #F5F7FA |
