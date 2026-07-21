# Production Readiness Checklist — 13 Categories

Use this after code review + UX review to score overall production readiness.
Each category: items → tick/cross → score → total percentage.

## ⚠️ What's Overkill for Personal Apps

For a Telegram Mini App with limited personal users (<100), skip these entirely:
- **Category 10 (Caching/CDN):** Redis, CDN, browser caching — NOT needed. SQLite is fast enough.
- **Category 11 (Load Balancing):** Multi-worker, horizontal scaling — NOT needed. Single uvicorn worker is fine.
- **Category 6 (Cloud):** Cloud deployment plan, resource limits — NOT needed for self-managed Docker.
- **Category 7 (CI/CD):** Full pipeline, auto-deploy — Simple GitHub Actions for tests is enough.
- **Category 9 (Rate Limiting):** Per-user limits, burst protection — Basic SlowAPI is enough.

Focus score on: Frontend (1), API (2), Database (3), Auth (4), Security (8), Logging (12).
These 6 categories = ~70% of production readiness for a personal app.

## Categories

### 1. Frontend (React/TypeScript)
- [ ] Loading states on all pages (skeleton, not text)
- [ ] Error states with retry on all pages
- [ ] Empty states with helpful messages on all lists
- [ ] Toast notifications on all mutation errors
- [ ] Undo on destructive actions (task complete, habit complete)
- [ ] Confirmation dialogs on delete/logout
- [ ] Tap feedback (active:scale-95) on all buttons
- [ ] RTL layout on all pages
- [ ] No horizontal scroll anywhere
- [ ] Input maxLength on all text fields
- [ ] Pull-to-refresh on lists
- [ ] Status bar color matches theme
- [ ] prefers-reduced-motion support
- [ ] ARIA labels on interactive elements
- [ ] Keyboard navigation works
- [ ] Charts responsive on mobile
- [ ] Persian text throughout

### 2. API & Backend
- [ ] FastAPI async throughout
- [ ] Pydantic schemas on all inputs/outputs
- [ ] Service layer (not raw endpoint logic)
- [ ] Workspace ownership validation on all writes
- [ ] Auth endpoint uses JSON body (not query param)
- [ ] API versioning (/api/v1/)
- [ ] Structured error responses
- [ ] Rate limit definitions exist
- [ ] Rate limit middleware applied
- [ ] Input validation on all endpoints
- [ ] Health check endpoint
- [ ] CORS configured (not ["*"])

### 3. Database
- [ ] ForeignKey constraints on all relations
- [ ] Unique constraints on important fields
- [ ] Database indexes on query-heavy columns
- [ ] Alembic migrations created
- [ ] JSON columns for flexible data (schedule, metadata)
- [ ] updated_at auto-update trigger
- [ ] Backup workflow functional
- [ ] SQLite → PostgreSQL conversion tested
- [ ] 25 event/day limit enforced
- [ ] No N+1 queries

### 4. Authentication & Authorization
- [ ] Telegram initData validation (HMAC)
- [ ] JWT generation and verification
- [ ] get_current_user dependency
- [ ] get_internal_user (service-to-service)
- [ ] Token expiry configured
- [ ] Logout works (frontend clears state)
- [ ] No hardcoded secrets

### 5. Hosting & Deployment
- [ ] Docker Compose configured
- [ ] Dockerfiles for backend + frontend
- [ ] Caddyfile / nginx.conf with content
- [ ] Health checks in Docker
- [ ] .env template with all vars
- [ ] Environment variables documented
- [ ] Production env vars separated

### 6. Cloud & Compute
- [ ] Resource limits in Docker (memory, CPU)
- [ ] Database connection pooling
- [ ] Async I/O throughout
- [ ] Stateless API design
- [ ] Cloud deployment plan documented

### 7. CI/CD & Version Control
- [ ] Git repository initialized
- [ ] .gitignore configured
- [ ] GitHub Actions / GitLab CI
- [ ] Auto tests on push
- [ ] Auto deploy on merge
- [ ] Branch protection rules

### 8. Security & Access Control
- [ ] SECRET_KEY from env (not hardcoded)
- [ ] CORS restricted to specific domains
- [ ] SQL injection prevention (ORM)
- [ ] XSS prevention (React auto-escape)
- [ ] CSRF protection
- [ ] Security headers (Helmet, CSP)
- [ ] Input sanitization
- [ ] Webhook HMAC verification
- [ ] Rate limiting applied
- [ ] No sensitive data in logs
- [ ] HTTPS enforced
- [ ] Content Security Policy

### 9. Rate Limiting
- [ ] Rate limit definitions per endpoint
- [ ] Middleware applied and working
- [ ] Per-user limits
- [ ] Burst protection
- [ ] 429 response with retry-after
- [ ] SlowAPI or equivalent configured

### 10. Caching & CDN
- [ ] Redis for session/cache
- [ ] HTTP cache headers
- [ ] CDN for static assets
- [ ] Browser caching configured
- [ ] API response caching where appropriate
- [ ] In-memory cache for hot paths

### 11. Load Balancing & Scalability
- [ ] Multi-worker (gunicorn/uvicorn workers)
- [ ] Load balancer configured
- [ ] Horizontal scaling plan
- [ ] Database connection pooling
- [ ] Stateless API (no server-side sessions)
- [ ] Async I/O for concurrent requests

### 12. Logging & Error Tracking
- [ ] Structured logging (JSON format)
- [ ] Log levels configured (debug/info/warning/error)
- [ ] Request ID tracking
- [ ] Error aggregation (Sentry or similar)
- [ ] Log rotation configured
- [ ] Audit trail for sensitive operations
- [ ] Error alarm to Telegram/email
- [ ] Performance logging (response times)

### 13. Accessibility & Recovery
- [ ] RTL layout correct
- [ ] Persian text throughout
- [ ] Keyboard navigation
- [ ] Screen reader (ARIA labels)
- [ ] Color contrast sufficient
- [ ] Focus management
- [ ] prefers-reduced-motion
- [ ] Error recovery (retry buttons)
- [ ] Offline support (service worker)
- [ ] Data backup/restore functional

## Scoring

| Category | Items | Score |
|----------|-------|-------|
| 1. Frontend | 17 | __/17 |
| 2. API & Backend | 12 | __/12 |
| 3. Database | 10 | __/10 |
| 4. Auth | 7 | __/7 |
| 5. Hosting | 7 | __/7 |
| 6. Cloud | 5 | __/5 |
| 7. CI/CD | 6 | __/6 |
| 8. Security | 12 | __/12 |
| 9. Rate Limiting | 6 | __/6 |
| 10. Caching | 6 | __/6 |
| 11. Scalability | 6 | __/6 |
| 12. Logging | 8 | __/8 |
| 13. Accessibility | 10 | __/10 |
| **Total** | **121** | **__** |

## Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 80%+ | 🟢 Ready | Deploy with monitoring |
| 60-79% | 🟡 Almost | Fix P0 items, then deploy |
| 40-59% | 🟠 MVP only | Internal testing only |
| <40% | 🔴 Not ready | Significant work needed |

## Priority Fix Order

1. Security (category 8) — always first
2. Auth (category 4) — before any user data
3. Database (category 3) — before data corruption
4. API (category 2) — before frontend integration
5. Frontend (category 1) — before user testing
6. Hosting (category 5) — before deployment
7. Rate Limiting (category 9) — before public launch
8. Logging (category 12) — before production
9. CI/CD (category 7) — before team collaboration
10. Caching (category 10) — after basic perf testing
11. Scalability (category 11) — after user growth
12. Cloud (category 6) — after architecture finalized
13. **Accessibility (category 13)** — ongoing improvement

## Related

See [references/production-fix-file-pattern.md](references/production-fix-file-pattern.md) for
the file-per-fix pattern used when closing production gaps.
