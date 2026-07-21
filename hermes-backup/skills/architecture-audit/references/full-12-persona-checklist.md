# Full 12-Persona Audit Checklist

Used when user requests a "professional team" or "tیم حرفه‌ای" level audit.

## 1. CEO Review
- Product viability assessment
- MVP readiness
- Strategic concerns
- Business model gaps

## 2. Product Review
- Feature completeness matrix (Complete/Partial/Placeholder)
- UX issues (broken flows, misleading toggles)
- Missing features vs documented features

## 3. Engineering Manager Review
- Code duplication (DRY violations)
- Inconsistent patterns (service layer vs inline)
- Unused code (schemas, exceptions, config)
- Deprecated API usage
- Field naming confusion

## 4. Software Architecture Review
- Dual infrastructure (DB, proxy)
- Wrong model for data (settings on wrong table)
- Missing rehydration/session restore
- Missing middleware architecture

## 5. Database Review
- Missing constraints (CHECK, UNIQUE)
- SQLite-only functions (will break on PG migration)
- Missing indexes on frequent queries
- Deprecated datetime usage
- Schema vs code mismatches

## 6. Backend Review
- Auth bypass conditions
- Unauthenticated endpoints
- Zero-validation endpoints
- Stub/fake service methods
- N+1 query patterns
- Custom exceptions never used

## 7. Frontend Review
- Broken imports (runtime crashes)
- No-op operations (delete that doesn't delete)
- Missing error states
- `||` vs `??` for zero values
- `any` casts defeating TypeScript
- Redundant Chart.js registration
- Missing debounce
- Deprecated APIs (onKeyPress)
- Session not rehydrated
- Type mismatches (store vs interface)

## 8. Security Review
- Hardcoded secrets in docker-compose
- CORS allow-all
- Unauthenticated webhook/SSE endpoints
- Auth bypass in dev mode
- No input validation (raw dict)
- Backend runs as root
- No TLS/HTTPS
- No security headers
- SQL injection in scripts

## 9. Performance Review
- N+1 queries (count per endpoint)
- Missing database indexes
- No caching
- No pagination
- No debounce on frequent saves
- Duplicated heavy computations

## 10. QA Review
- Test coverage estimate vs target
- Tests that only verify auth rejection (no functional tests)
- Test structure mismatch (docs vs reality)
- Missing test factories
- Hardcoded test URLs
- Missing E2E critical path tests

## 11. DevOps Review
- Dual reverse proxy (Caddy + nginx)
- Broken healthcheck (curl in slim image)
- Unpinned versions (:latest)
- Missing .dockerignore
- Running as root
- No CI/CD pipeline
- Unused services (PostgreSQL defined but not used)

## 12. Documentation Review
- Docs vs reality mismatch
- Missing architecture diagram
- Missing deployment guide
- Incomplete "fixed" claims
- AI prompts mixed with docs
