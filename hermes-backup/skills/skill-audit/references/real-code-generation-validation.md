# Real Code Generation Validation Methodology

## Why Internal Benchmarks Are Not Enough

When auditing a skill that claims autonomous project execution, internal benchmarks with mock execution produce false positives. The mock executor returns `{success: True, files_created: []}` which satisfies the execution loop but produces no actual output.

**User signal that you're in this trap:** "I don't see any results" / "you didn't actually build anything" / "where's the website?"

## Progressive Validation Ladder

### Level 1: Internal Tests (pytest)
- Import checks, unit tests, edge cases
- Proves modules work in isolation
- **Does NOT prove integration works**

### Level 2: Stress Benchmarks (30→47→50 task DAGs)
- Execute the real execution loop with increasing complexity
- 30-task linear DAG: catches basic state machine bugs
- 47-task complex DAG: catches same-type starvation (same-type parallel tasks compete for 1 agent)
- 50-task real project: catches dependency resolution bugs
- **Does NOT prove the output is useful**

### Level 3: Real Code Generation (MANDATORY)
- Spawn actual subagents via `delegate_task()` to write real code
- Verify: files exist → code imports → API runs → tests pass
- **This is the only level that catches:**
  - Auth bugs (JWT sub must be string)
  - Import path errors
  - Missing dependencies
  - API contract mismatches
  - Frontend/backend integration issues

## Real-World Test Case: E-Commerce Platform

### Project Design
- 50 tasks across 7 phases (Research → Design → Backend → Frontend → Testing → Review → Deploy)
- Backend: FastAPI + SQLAlchemy + SQLite + JWT auth
- Frontend: React SPA (single HTML file with CDN)
- Supporting: seed data, Docker, tests, README

### Execution
1. Spawn 3 subagents in parallel:
   - Backend subagent: writes 11 Python files (main, database, auth, models, 5 routers, seed, tests)
   - Frontend subagent: writes 1 HTML file (React SPA with 50 mock products)
   - Supporting subagent: writes seed data, Docker files, README
2. Install dependencies: `pip install fastapi uvicorn sqlalchemy python-jose bcrypt pydantic`
3. Run seed data: `python seed.py` → creates 50 products, 3 users, sample orders
4. Start server: `uvicorn main:app --port 8000`
5. Test all 15 API endpoints with real HTTP requests

### Bugs Found in Real Execution (not caught by internal tests)
1. **JWT sub must be string** — `python-jose` requires `sub` claim to be string, not integer. Internal tests passed because they used mock auth. Real JWT generation failed.
2. **Auth router used `username` field** — login endpoint expected `username` not `email`. Seed data stored users with `username` field. No internal test caught this because mock auth bypassed the actual login flow.
3. **Product API returned paginated response** — `{items: [...], total: 50}` not a flat list. Internal tests assumed flat list.

### What Passed
- All 15 API endpoints returned correct status codes and data
- 50 products seeded with realistic names, prices, categories
- Authentication flow: register → login → get token → use token → checkout
- Cart operations: add, get, checkout → order created
- Reviews: add and list working
- Categories: 5 categories with proper filtering

## Methodology for Future Audits

When a skill claims "builds projects autonomously":

1. Run internal tests (Level 1) — fix any failures
2. Run stress benchmarks (Level 2) — fix same-type starvation and thread safety
3. **Design a real project** appropriate to the skill's domain
4. **Spawn subagents** to write actual code using the skill's execution mechanism
5. **Run the code** — start servers, execute scripts, test endpoints
6. **Report results** showing both what works and what's broken
7. Fix bugs and re-test

**Never skip Level 3.** A skill that only passes Levels 1-2 is untested for real use.
