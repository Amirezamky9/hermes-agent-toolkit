# Session Research Record — Persian Resume (امیررضا مختاری)

## GitHub Profile
**Account:** github.com/Amirezamky9

**Repositories:**

| Repo | Description | Tech Stack |
|------|-------------|-----------|
| n8n-teacher-bot | Multi-mode Telegram bot for n8n learning — AI teacher + WorkflowYab semantic RAG search. Built entirely in n8n with MCP tools, email OTP auth, PostgreSQL memory | n8n, MCP tools, PostgreSQL, Telegram Bot API |
| n8n-torob-scraper | n8n workflow that scrapes product listings/prices from torob.com (Persian e-commerce). Two-pass scraping: first pass finds product page URLs, second extracts details. No API keys required | n8n, HTML content extraction, CSS selectors |
| crypto_ingestion_pipeline | Webhook-triggered FastAPI service ingesting KuCoin OHLCV candles into PostgreSQL. Smart delta+backfill, retry with exponential backoff, Docker-ready | Python, FastAPI, PostgreSQL, Docker, KuCoin API |

## Key User Corrections This Session

1. **"این چه چرتیه نوشتی"** — Wrote content without researching domain terms first. Fix: ALWAYS research each technology (Wikipedia, official docs) before writing resume content.
2. **"زمینه‌هایی که فعالیت کردم هم درست نیست"** — User provided file with specific data; I added extra descriptions and inaccurate terminology.
3. **"توضیحات اضافی ندی"** — Added sections/content not in the user's original file.
4. **"شاهرود دورکاری نمیشه"** — Appended "دورکاری" to location without user confirmation.
5. **"مهارت‌ها راست‌چین چپ‌چینش خراب شده"** — Mixed `cell()` + `multi_cell()` for RTL skills broke alignment. Use uniform approach (all `multi_cell()` or all `cell()`) for RTL text.
6. **"منم نمیبینم ک اینکارو کرده باشی سرچ کن قشنگ"** — Did web research silently (collected data into terminal, never showed findings to user). User wants to SEE the search results (titles, snippets, structure) inline before any code is written. Fix: always present research findings as a visible section in the reply before moving to planning/coding.

## Sources Used for Research
- https://en.wikipedia.org/wiki/N8n
- https://en.wikipedia.org/wiki/Retrieval-augmented_generation
- https://hermes-agent.ai
- https://zety.com/blog/automation-engineer-resume-example
- https://maxresumes.com/resume-examples/production/automation-engineer/
- https://www.qwikresume.com/resume-samples/automation-engineer/
- https://www.hirekit.co/resume-examples/automation-engineer (ATS-optimized, action+metric pattern)
- https://rockstarcv.com/automation-engineer-achievements/ (achievement formula)
- https://github.com/Amirezamky9 (all repos)
- https://iranestekhdam.ir/ (Persian resume guidelines)
