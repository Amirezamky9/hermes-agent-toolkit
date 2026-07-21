# Architecture Review Checklist — Common Bugs

Lessons from reviewing a Telegram Mini App architecture (42 issues found).
Use this checklist when reviewing or creating architecture docs.

## Critical Bugs (Will Break Functionality)

### Backup Architecture
- **n8n must NOT access SQLite directly.** Use HTTP webhooks to FastAPI endpoints.
- SQLite dump SQL is incompatible with PostgreSQL. Use pgloader or a conversion script.
- Backup endpoint must be authenticated (API key or HMAC).

### Authentication & Security
- SSE endpoints must use JWT auth, not user_id in URL path.
- Webhook endpoints (n8n → FastAPI) must have HMAC signature verification.
- n8n → FastAPI data fetch needs service-to-service auth (API key header).
- Exception handlers must return correct HTTP status codes (404, 422, 400 — not all 400).

### Data Model
- Onboarding → workspace creation flow must be explicitly defined.
  Onboarding stores JSON blobs; a separate step must create habits/tasks/courses.
- Python ORM models must cover ALL tables (not just 5 of 15).
- Unique constraints in SQL must also be declared in Python models.

## Significant Bugs (Incorrect Behavior)

### TypeScript
- `mood: 1-10` is arithmetic (-9), not a union type. Use `mood: number` with runtime validation.

### SQL Queries
- Division by zero: wrap with `CASE WHEN COUNT(*) = 0 THEN 0 ELSE ... END`.
- JSON parsing via string ops is fragile. Use `json_extract()` instead.
- Streak queries matching by habit name break on rename. Match by habit_id in metadata.
- Timestamp vs Date comparison: use `DATE(scheduled_time) BETWEEN` not raw timestamp.

### Duplicate Fields
- Don't duplicate `available_hours_per_day` in both onboarding_data and user_profile.
- Pick one source of truth (user_profile).

### Missing Endpoints
- DELETE endpoints for tasks, workspaces, courses.
- PUT/UPDATE for courses.
- Frontend services: profileService, settingsService, reviewService.
- Frontend hooks: useProfile, useSettings, useReviews.

### SSE
- Define reconnection strategy (exponential backoff).
- Add server-side heartbeat every 15-30 seconds.
- Handle connection state in frontend.

## Minor Issues

- CORS_ORIGINS should not be hardcoded to localhost in production.
- Docker Compose needs named networks and healthchecks.
- `updated_at` fields need auto-update triggers or ORM events.
- `NOT NULL` and `CHECK` constraints in SQL must be mirrored in Python models.
- Rate limit config should be consolidated in one file covering all endpoints.

## Review Process

1. Read ALL architecture files (not just one)
2. Cross-reference: do frontend services match backend endpoints?
3. Cross-reference: do database models match API schemas?
4. Check auth: every endpoint needs appropriate auth
5. Check data flow: trace a user action from UI → API → DB → response
6. Check n8n: all integration points use HTTP webhooks, not direct DB access
7. Check dynamic design: no hardcoded user-specific values
