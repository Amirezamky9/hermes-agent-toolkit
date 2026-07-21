# Example: Crypto Ingestion Pipeline

This reference documents the actual first project published via the project-publisher workflow.

## Project Overview

- **Name:** crypto_ingestion_pipeline
- **Type:** FastAPI on-demand OHLCV ingestion from KuCoin to PostgreSQL
- **Output:** https://github.com/Amirezamky9/crypto_ingestion_pipeline
- **Files:** 6 Python files + Dockerfile + .env.example + requirements.txt

## What was produced

| File | Content |
|---|---|
| `README.md` | Rich English doc — 16 sections, 15k+ chars |
| `README.fa.md` | Full Persian translation — same sections as English |
| `LICENSE` | MIT License |

## README structure used

1. Badge header + Overview
2. Table of Contents
3. Features table (14 rows)
4. ASCII architecture flow diagram
5. How It Works — Smart Ingestion (delta mode + backfill mode with code-flow)
6. Tech Stack table
7. Prerequisites
8. Quick Start (local + Docker)
9. API Reference (healthz + ingest with schemas and curl)
10. Configuration (env vars table + tunable constants)
11. Database Schema (full CREATE TABLE DDL)
12. Deployment (Docker + Kubernetes YAML + Render notes)
13. Security (6-point breakdown)
14. Development (extending, adding exchanges)
15. Contributing
16. License

## Persian translation notes

- All 16 sections translated
- Technical terms kept consistent with glossary (references/persian-tech-glossary.md)
- Code blocks left in English
- Table headers and field descriptions fully translated
- Added "فارسی" marker at top of README.fa.md

## GitHub publishing commands

```bash
cd /workspace/crypto_ingestion_pipeline

# Existing .gitignore was adequate. Existing repo had `origin` pointing to old account.
gh repo create crypto_ingestion_pipeline \
  --public \
  --description "On-demand, webhook-triggered OHLCV ingestion service." \
  --push \
  --source . \
  --remote upstream

gh repo view Amirezamky9/crypto_ingestion_pipeline --json name,visibility,url,description
```

## Key decisions

- Used `--remote upstream` because the project already had `origin` pointing to a different account
- `gh repo create --push` handles git init, add, and commit if needed
- MIT License with user's real name from memory (Amirreza Mokhtari, 2026)
- ASCII diagram used markdown fenced code block with labels and arrows