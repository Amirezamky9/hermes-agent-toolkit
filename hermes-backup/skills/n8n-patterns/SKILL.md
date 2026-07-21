---
name: n8n-patterns
description: |-
  Pattern library for n8n workflows — exact node types, parameters, wiring, and edge cases.
  Primary consumer: n8n-reviewer (loads via skill_view(file_path='references/...') when writing decks).
  Planner may browse the index; Builder uses its own SDK refs and does NOT load this skill.
version: 2.0.0
author: Amirreza Mokhtari
license: MIT
metadata:
  hermes:
    tags: [n8n, patterns, architecture, reference]
    related_skills: [n8n-reviewer, n8n-planner]
    references:
      - references/01-chatbot.md
      - references/02-scheduling.md
      - references/03-form-input.md
      - references/04-scraping-research.md
      - references/05-monitoring.md
      - references/06-enrichment.md
      - references/07-triage.md
      - references/08-content-generation.md
      - references/09-document-processing.md
      - references/10-data-extraction.md
      - references/11-data-analysis.md
      - references/12-data-transformation.md
      - references/13-data-persistence.md
      - references/14-notification.md
      - references/15-knowledge-base.md
      - references/16-human-in-the-loop.md
      - references/17-web-app.md
      - references/18-error-handling.md
      - references/19-ecommerce-scraping.md
      - references/20-telegram.md
      - references/21-checkout-validation.md
      - references/22-postgres-version-mismatch.md
      - references/23-async-polling-loop.md
      - references/22-switch-crash-normalizer.md
      - references/25-telegram-registration-otp.md
      - references/XX-n8n-expressions.md
      - references/architecture-principles.md
      - references/scraping-node-schemas.md
      - references/kie-ai-guide.md
      - references/webhook-enrichment-method.md
      - references/bulk-extraction-pattern.md
      - references/27-mcp-editing-pitfalls.md
      - references/28-state-machine-staticdata.md
---

# n8n-patterns — Pattern Catalog

## Overview

این اسکیل **فقط ایندکس پترن‌هاست**. محتوای اصلی توی `references/` هست.

## When to Use

| کی | چی کار کنه |
|----|-----------|
| **🔬 Reviewer** | مصرف‌کننده اصلی — موقع نوشتن deck: `skill_view('n8n-patterns', file_path='references/20-telegram.md')` |
| **📐 Planner** | ایندکس رو ببینه + اگه نیاز به جزئیات داشت پترن مربوطه رو لود کنه |
| **🔧 Builder** | ❌ لود نمی‌کنه — SDK refs خودش (`n8n-builder/references/*`) کافیه |
| ❌ هیچکدوم | این اسکیل رو تنها لود نکن — فقط به عنوان رفرنس استفاده کن |

## Pattern Catalog

### MCP Best Practices (اصلی — داخل references/)

| # | فایل | موضوع | خط | Reviewer |
|---|------|-------|-----|----------|
| 01 | `01-chatbot.md` | 🤖 ربات چت هوشمند (AI Agent) | 377 | Agent, Guardrails, Tools, Memory |
| 02 | `02-scheduling.md` | ⏰ زمان‌بندی و Cron | 260 | Schedule Trigger, Wait |
| 03 | `03-form-input.md` | 📝 فرم و ورودی | 256 | Multi-step forms |
| 04 | `04-scraping-research.md` | 🔍 وب اسکرپینگ | 744 | HTTP Request, Pagination, RSS |
| 19 | `19-ecommerce-scraping.md` | 🏪 ای‌کامرس اسکرپینگ | 95 | Two-pass product + price scraper, CSS selectors, Persian numerals |
| 05 | `05-monitoring.md` | 📊 مانیتورینگ | 587 | 9 pattern از 7 workflow واقعی |
| 06 | `06-enrichment.md` | 🧠 غنی‌سازی داده | 603 | 10 pattern از 13 workflow واقعی |
| 07 | `07-triage.md` | 🚦 دسته‌بندی و مسیریابی | 578 | 8 pattern از 9 workflow واقعی |
| 08 | `08-content-generation.md` | 🎨 تولید محتوا | 179 | 5 pattern + KIE.AI |
| 09 | `09-document-processing.md` | 📄 پردازش اسناد | 92 | PDF, Office, OCR |
| 10 | `10-data-extraction.md` | 📋 استخراج داده | 190 | File parsing, AI extraction |
| 11 | `11-data-analysis.md` | 📈 تحلیل داده | 294 | 7 pattern واقعی |
| 12 | `12-data-transformation.md` | 🔄 تبدیل داده | 706 | 6 pattern + 19 pitfall |
| 13 | `13-data-persistence.md` | 💾 ذخیره‌سازی | 236 | Data Table, SQL, Redis |
| 14 | `14-notification.md` | 🔔 اعلان‌ها | 246 | 10 platform + 6 pattern |
| 15 | `15-knowledge-base.md` | 📚 پایگاه دانش | 284 | ⚠️ نیاز به enrichment |
| 16 | `16-human-in-the-loop.md` | 👤 تایید انسانی | 294 | ⚠️ نیاز به enrichment |
| 17 | `17-web-app.md` | 🌐 Web App | 45 | SPA از webhook |
| 18 | `18-error-handling.md` | 🛡 مدیریت خطا | 450 | Retry, Circuit Breaker, Fallback |
| 20 | `20-telegram.md` | 📱 ربات تلگرام | 700+ | 4-route dispatcher, state machine, sub-workflow $json fix, dual input (text+callback), appendAttribution |
| 21 | `21-checkout-validation.md` | ✅ اعتبارسنجی چک‌اوت | ~200 | If node boolean expression, Telegram checkout validation |
| 22 | `22-postgres-version-mismatch.md` | 🐘 Postgres v2↔v2.6, Aggregate v2, queryReplacement shift, edit-lock | ~200 | Credential split, $json shift, column names, edit-lock |
| 23 | `22-switch-crash-normalizer.md` | 🔀 Switch crash: "Cannot read properties of undefined (reading 'push')" + Code node normalizer | ~120 | Switch v3.4 push crash, dual-input normalize, removeNode+rebuild |
| 25 | `25-telegram-registration-otp.md` | 📧 ثبت‌نام ایمیلی + OTP + Multi-Agent Router | ~400 | email OTP auth, whitelist, rate limit, MCP tools, workflow export |
| 23 | `23-async-polling-loop.md` | 🔄 Async Polling Loop + SDK Circular Connections | ~150 | Submit→Wait→Check→IF loop, update_workflow addConnection, LongCat API |
| XX | `XX-n8n-expressions.md` | 🧮 Expressions | 375 | `{{ }}` syntax, Luxon, 11 var |

### Curated References (دستی)

| فایل | موضوع |
|------|-------|
| `scraping-node-schemas.md` | اسکیمای نودهای Scraping (HTTP Request, HTML Extract, RSS) |
| `kie-ai-guide.md` | راهنمای KIE.AI برای تولید عکس/ویدئو |
| `webhook-enrichment-method.md` | روش غنی‌سازی پترن با webhook |
| `bulk-extraction-pattern.md` | الگوی استخراج حجیم |
| `architecture-principles.md` | اصول معماری n8n (Telegram routing, Session, AI Agent, DataTable) |
| 27 | `27-mcp-editing-pitfalls.md` | 🛠 MCP `update_workflow` pitfalls — Set v3.4 assignments format, node corruption recovery, setNodeParameter fallback, version management |
| 28 | `28-state-machine-staticdata.md` | 🔄 State machine via `$getWorkflowStaticData('global')` — cross-execution state for admin reject/comment flows |

## How to Access

```python
# فقط ایندکس:
skill_view('n8n-patterns')

# پترن خاص:
skill_view('n8n-patterns', file_path='references/20-telegram.md')

# اصول معماری:
skill_view('n8n-patterns', file_path='references/architecture-principles.md')
```

> **نکته:** وقتی `skill_view` با `file_path` صدا زده می‌شه، فقط محتوای اون فایل برگشته می‌شه — SKILL.md لود نمی‌شه. می‌تونی بدون نگرانی از نویز کانتکس استفاده کنی.

## Verification

- [ ] پترن‌ها فقط در `references/` — SKILL.md فقط ایندکس
- [ ] `file_path` درست به فایل‌های موجود اشاره می‌کنه
- [ ] توضیحات ≤ 1024 chars
- [ ] Builder از SDK refs خودش استفاده می‌کنه، نه از پترن‌ها
- [ ] Reviewer از پترن‌ها برای پارامترهای دقیق نودها استفاده می‌کنه
- [ ] هر دامنه فقط یک فایل canonical داره (e.g. Telegram فقط `20-telegram.md`)
