# Telegram Mini App — Tech Stack Reference (Jul 2026)

## Frontend Framework Comparison

| Criterion | React | Vue | Svelte | SolidJS |
|-----------|-------|-----|--------|---------|
| @tma.js SDK version | **v3.0.23** ✅ | v1.0.23 | v1.0.23 | v1.0.23 |
| @telegram-apps/telegram-ui | **✅ Full support** | ❌ | ❌ | ❌ |
| Community examples | **Most** | Medium | Medium | Few |
| Charting library support | **Best** | Good | Limited | Limited |
| RTL/Persian components | **Best** | Custom | Custom | Custom |
| TypeScript support | ✅ | ✅ | ✅ | ✅ |

**Verdict: React is the only pragmatic choice** due to SDK maturity (v3 vs v1),
official UI toolkit support, and community ecosystem.

## Charting Libraries — Bundle Size Analysis

Source: bundlephobia.com (verified Jul 2026)

| Library | Min (kB) | Gzip (kB) | Charts Supported | Fit for Mini App |
|---------|----------|-----------|-----------------|------------------|
| **Chart.js** | 194.3 | **66.2** | Bar, Line, Pie, Doughnut, Radar, Scatter | ✅ **Best choice** |
| Recharts | 483 | 117.6 | Bar, Line, Area, Pie, Radar, Scatter | ⚠️ Acceptable but heavy |
| uPlot | ~35 | ~13 | Time series, lines, areas, bars | ⚠️ Limited chart types |
| lightweight-charts | 160 | 49.9 | Financial/candlestick | ❌ Wrong use case |
| ECharts | 1000 | 324.7 | Everything | ❌ Too heavy |
| @ant-design/charts | 2100 | 583.6 | Everything | ❌ Way too heavy |

## POS Dashboard Charts Needed → Chart.js Coverage

| Dashboard Widget | Chart.js Type | Notes |
|-----------------|---------------|-------|
| Completion Rate (daily/weekly/monthly) | Bar chart | Simple bar per day |
| Habit Streak | Number + progress bar | Not a chart — CSS component |
| Sleep Trend | Line chart | Time-series, 7/30 day |
| Wake-up Trend | Line chart | Time-series, 7/30 day |
| Course Progress | Doughnut / progress bar | Percentage display |
| Activity Heatmap | Custom CSS grid | GitHub-style heatmap, not Chart.js |
| Tasks Done vs Missed | Stacked bar | Two-color comparison |

## Full-Stack Bundle Budget (WebView Target)

Target: < 300kB gzipped total for fast load in Telegram WebView.

| Layer | Library | Gzip (kB) |
|-------|---------|-----------|
| Framework | React 18 | ~40 |
| Telegram SDK | @tma.js/sdk-react | ~15 |
| UI Components | @telegram-apps/telegram-ui | ~20 |
| Charts | Chart.js + react-chartjs-2 | ~66 |
| Animations | Framer Motion | ~30 |
| Styling | TailwindCSS (JIT) | ~10 |
| Routing | React Router v7 | ~14 |
| State | Zustand | ~3 |
| HTTP | ky (fetch wrapper) | ~2 |
| Date | date-fns (tree-shaken) | ~5 |
| **Total** | | **~205kB** |

## Authentication Flow — Detailed

```
┌─ Mini App (React) ─────────────────────────────────┐
│ 1. import { init, initData } from '@tma.js/sdk-react' │
│ 2. init() → Telegram passes initData with:          │
│    - user (id, first_name, username, photo_url)     │
│    - auth_date (timestamp)                          │
│    - hash (HMAC-SHA256 of data using bot_token)     │
│ 3. Send initData.raw to backend                     │
└──────────────────────┬──────────────────────────────┘
                       │ POST /api/auth/telegram
                       ▼
┌─ FastAPI Backend ───────────────────────────────────┐
│ 1. Receive initData string                           │
│ 2. Validate HMAC using python-telegram-bot or        │
│    @tma.js/init-data-node pattern:                   │
│    - Parse key=value pairs                           │
│    - Remove 'hash' from data                        │
│    - Sort alphabetically                             │
│    - HMAC-SHA256(sorted_data, bot_token)            │
│    - Compare with received hash                      │
│ 3. Check auth_date freshness (< 24h)                │
│ 4. Find or create user in SQLite                    │
│ 5. Issue JWT (access + refresh tokens)              │
│ 6. Return JWT to Mini App                           │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
  All subsequent requests: Authorization: Bearer <JWT>
```

## RTL/Persian CSS Patterns

```css
/* TailwindCSS RTL */
<div className="rtl:text-right ltr:text-left">

/* HTML root */
<html lang="fa" dir="rtl">

/* Form inputs in RTL */
<input className="text-right" dir="rtl" />

/* Mirrored icons */
<Icon className="rtl:scale-x-[-1]" />

/* Flex direction for RTL */
<div className="flex flex-row-reverse rtl:flex-row">
```

## Docker Compose — No SQLite Service

```yaml
# CORRECT — SQLite is just a file
services:
  backend:
    build: ./backend
    volumes:
      - sqlite-data:/app/data  # SQLite DB file
    environment:
      DATABASE_URL: sqlite+aiosqlite:///./data/pos.db

# WRONG — Don't do this
services:
  sqlite:  # ← This doesn't exist, SQLite is not a service
    image: sqlite:3
```

## n8n Workflow Architecture for POS

### Workflow: Chat Agent (Setup Wizard)
```
Webhook Trigger (POST /webhook/chat)
  → Switch (message type)
    → OpenAI Agent (with system prompt for setup wizard)
      → Code Node (parse agent response, extract entities)
        → HTTP Request (POST to backend /api/ai/plan)
          → Respond to Webhook (return to Mini App)
```

### Workflow: Daily Reflection
```
Schedule Trigger (22:00 daily)
  → HTTP Request (GET backend /api/timeline/today?incomplete=true)
    → IF (has incomplete tasks)
      → OpenAI Agent (generate reflection questions)
        → Telegram Bot API (sendMessage to user)
          → Webhook Wait (user reply)
            → Code Node (parse reasons)
              → HTTP Request (POST to backend /api/ai/reflection)
```

### Workflow: Weekly Review (auto-generated)
```
Schedule Trigger (Saturday 20:00)
  → HTTP Request (GET backend /api/analytics/week)
    → OpenAI Agent (analyze patterns, generate insights)
      → HTTP Request (POST to backend /api/ai/review)
        → Telegram Bot API (send formatted report)
```

## FastAPI Package Requirements

```
# Backend requirements.txt
fastapi[standard]>=0.115
uvicorn[standard]>=0.32
sqlalchemy[asyncio]>=2.0
aiosqlite>=0.20
pydantic>=2.0
pydantic-settings>=2.0
python-jose[cryptography]>=3.3
passlib[bcrypt]>=1.7
python-multipart>=0.0.9
httpx>=0.27
alembic>=1.13
python-telegram-bot>=21.0
```

## Project Structure

```
pos/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── habit.py
│   │   │   ├── task.py
│   │   │   ├── course.py
│   │   │   └── timeline.py
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API route modules
│   │   │   ├── auth.py
│   │   │   ├── habits.py
│   │   │   ├── tasks.py
│   │   │   ├── courses.py
│   │   │   ├── timeline.py
│   │   │   └── webhooks.py
│   │   ├── services/            # Business logic
│   │   └── utils/               # Auth helpers, validators
│   ├── alembic/                 # DB migrations
│   ├── tests/
│   └── requirements.txt
├── miniapp/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Chat.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── Habits.tsx
│   │   │   ├── Tasks.tsx
│   │   │   ├── Courses.tsx
│   │   │   ├── WeeklyReport.tsx
│   │   │   ├── MonthlyReport.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── stores/              # Zustand stores
│   │   ├── api/                 # HTTP client (ky)
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
├── n8n/
│   └── workflows/               # Exported n8n workflow JSONs
├── docker/
│   ├── backend.Dockerfile
│   └── miniapp.Dockerfile
├── docs/
├── .env.example
├── docker-compose.yml
└── Caddyfile
```
