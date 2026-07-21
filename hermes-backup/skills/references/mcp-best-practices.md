# MCP Best Practices Reference

> This file indexes the enriched MCP n8n pattern files in `/workspace/n8n-best-practices-mcp/`.
> Use `skill_view(name='n8n-planner', file_path='references/mcp-best-practices.md')` then `read_file(path)`
> to load a specific pattern into context.

## Available Patterns

| # | File | Status | When to use |
|---|------|--------|-------------|
| 01 | `chatbot` | ✅ Rich (Agent, Tools, Memory, Guardrails) | AI Agent workflows, chatbot with tools |
| 02 | `scheduling` | ✅ Rich | Cron jobs, Wait nodes, cache sync |
| 03 | `form-input` | ✅ Rich | Form workflows, multi-step forms |
| 04 | `scraping-research` | ✅ Full | HTTP scraping, pagination |
| 05 | `monitoring` | ⚠️ Needs enrichment | — |
| 06 | `enrichment` | ⚠️ Needs enrichment | — |
| 07 | `triage` | ✅ Full | Routing, classification, Core Router |
| 08 | `content-generation` | ✅ Full | LLM text/image/audio generation |
| 09 | `document-processing` | ✅ Full | PDF, OCR, binary handling |
| 10 | `data-extraction` | ✅ Full | Extract from file, AI extraction |
| 11 | `data-analysis` | ⚠️ Needs enrichment | — |
| 12 | `data-transformation` | ✅ Full | Set, Code, Merge, Filter |
| 13 | `data-persistence` | ✅ Full | Data Table, PostgreSQL, upsert |
| 14 | `notification` | ✅ Full | Telegram, Slack, Email alerts |
| 15 | `knowledge-base` | ⚠️ Needs enrichment | — |
| 16 | `human-in-the-loop` | ⚠️ Needs enrichment | — |
| 17 | `web-app` | ✅ Full | SPA from webhook, Alpine.js |

## How to use

1. Identify pattern from intake.yaml (`primary_pattern`, `secondary_patterns`)
2. `read_file('/workspace/n8n-best-practices-mcp/{NN}-{name}.md')`
3. Combine with `telegram-bot-patterns.md` for Telegram-specific patterns
4. Use enriched node type details in architecture design

## Migrated from MCP

These files were originally extracted via `mcp_n8n_mcp_get_workflow_best_practices()`
and enriched with:
- Exact node type definitions from `get_node_types()`
- Real-world traps from session experience
- Telegram Bot Pattern integration notes
- Architecture diagrams (Mermaid)
