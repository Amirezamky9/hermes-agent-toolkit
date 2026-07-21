---
name: autonomous-project-engine
description: >-
  An intelligent multi-agent engine that decomposes natural-language project
  goals into atomic tasks, assigns specialized agents per task type, executes
  them in parallel with dependency-aware scheduling, verifies outputs, and
  adapts to failures. Powers autonomous full-stack project generation from
  research through deployment.
version: 3.7.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - project-engineering
      - multi-agent
      - task-orchestration
      - code-generation
    related_skills:
      - deep-research
      - web-research
      - plan
      - realtime-web-apps
      - n8n-builder
      - research-manager
---

# autonomous-project-engine

**Decompose goals → Parallel execution → Agent orchestration → Verification → Recovery**

This engine turns a high-level project description (e.g. "Build an e-commerce platform with React + FastAPI") into a managed multi-agent workflow: it researches patterns, designs architecture, implements code in parallel across 12 specialized agent types, runs verification, and adapts when tasks fail.

## Architecture

```
User Goal
  └─ GoalParser → TaskGraph (DAG)
       └─ ExecutionLoop (parallel, max_parallel=N)
            ├─ AgentManager (12 roles, lifecycle, atomic reserve)
            ├─ AgentOrchestrator (delegate_task() wrapper)
            ├─ Verifier (AST, lint, security, criteria)
            ├─ RecoveryEngine (retry, rollback, checkpoint)
            ├─ ContextManager (cross-iteration memory)
            ├─ ProgressMonitor (real-time status)
            └─ HumanLoop (clarify decisions)
```

### Core Modules

| Module | Role | Key Methods |
|--------|------|-------------|
| `schema.py` | Task, Agent, Project, State enums + dataclasses | — |
| `state_manager.py` | Atomic state, checkpoints, restore | `transition_task()`, `create_checkpoint()`, `restore()` |
| `task_graph.py` | DAG operations, critical path, parallel groups | `get_ready_tasks()`, `get_critical_path()`, `topological_sort()` |
| `agent_manager.py` | Agent lifecycle, atomic select+reserve, scoring | `create_default()`, `select_agent_for_task()`, `start_work()`, `complete_work()` |
| `agent_prompts.py` | 12 system prompts with tool restrictions + skills | `get_prompt(role, context, skills)` |
| `agent_orchestrator.py` | delegate_task() wrapper, fallback mock | `execute_task()`, `_execute_real()`, `_extract_files()` |
| `execution_loop.py` | ThreadPoolExecutor, context-aware, adaptive replan | `run()`, `_run_iteration()`, `_execute_single_task()` |
| `verifier.py` | AST analysis, security regex, complexity, lint | `verify()`, `_verify_acceptance_criteria()` |
| `planner.py` | Goal decomposition, task generation | `parse_goal()`, `generate_tasks()` |
| `recovery_engine.py` | Retry, rollback, transition validation | `recover_task()`, `validate_transition()` |
| `context_manager.py` | Cross-iteration memory | `save_iteration_context()`, `load_context_for_task()` |
| `progress_monitor.py` | Real-time tracking | `get_progress_summary()`, `get_phase_breakdown()` |
| `human_loop.py` | Clarify decisions | `ask_user()`, `confirm_action()` |
| `token_tracker.py` | Cost tracking | `get_summary()`, `estimate_remaining()` |

## Quick Start

```bash
# Clone the engine into your workspace
# Ensure the project lives at ~/.hermes/skills/autonomous-ai-agents/autonomous-project-engine/

cd your-project
python -m pytest tests/ -v  # 129+ tests should pass
```

### Run a full project benchmark

```python
from core import AutonomousProjectEngine

engine = AutonomousProjectEngine(project_dir="/tmp/benchmark")
result = engine.run("Build a React + FastAPI e-commerce platform")
print(result.summary())
```

## Reference Files

- [Bug Discovery Log](references/bug-discovery-log.md) — Complete log of all bugs found during v3.3-v3.4 stress testing, including root causes, fixes, and reproduction steps
- [v3.6 Upgrade Blueprint](references/v36-upgrade-blueprint.md) — Production-ready upgrade plan: 8 module changes + 40 new tests, turning mock execution into real Hermes subagent calls
- [v3.7 Upgrade Blueprint](references/v37-upgrade-blueprint.md) — SchemaContract + ModelRouter + Phase Validation: 2 new modules, 5 file changes, solving all 7 parallel-subagent integration bugs
- [Skills.sh Installation Guide](references/skills-sh-installation.md) — How to install third-party skills from skills.sh and keep DEFAULT_SKILL_INDEX in sync
- [Parallel Subagent Integration Breakdown](references/parallel-subagent-integration-breakdown.md) — 7 specific integration bugs found in a real parallel subagent build, with root cause analysis and prevention checklist

## Workflow

```
1. PARSE GOAL → GoalParser generates 20-60 tasks across 6 phases
2. RESEARCH PHASE → deep-research / web-research for patterns & docs
3. EXECUTION LOOP (while tasks remain):
   a. get_ready_tasks() → OPEN + BLOCKED tasks
   b. Submit up to max_parallel to ThreadPoolExecutor
   c. Each task: select_agent_atomic → IN_PROGRESS → execute → COMPLETED|FAILED
   d. On FAILED: retry (exponential backoff) or adaptive re-plan
   e. After each phase: auto-checkpoint
   f. Log context, progress, and token cost
4. VERIFICATION → acceptance criteria, AST, security, lint
5. COMPLETION → summary report
```

## Phases (6)

| Phase | Task Types | Description |
|-------|-----------|-------------|
| Research | RESEARCH | Explore patterns, similar projects, tech docs |
| Design | DESIGN | System architecture, DB schema, API spec |
| Implementation | IMPLEMENTATION | Backend, frontend, fullstack coding |
| Testing | TESTING | Unit, integration, E2E tests |
| Review | REVIEW | Code review, security audit |
| Deployment | DEPLOYMENT | Docker, README, CI/CD |

## Architectural Insight: Dynamic Skill Discovery (NOT Hardcoded)

**Key lesson from v3.5 development:** Never hardcode `SKILL_MAP = {role: [skill_names]}`. Instead, use `SkillDiscoverer` from `core/skill_discoverer.py` which:

> **⚠️ Known limitation**: `SkillDiscoverer._try_online_discovery()` attempts Hermes live discovery via `skills_list()` but this path falls back silently on ImportError. In practice, the `DEFAULT_SKILL_INDEX` hardcoded in `skill_discoverer.py` is the **real source of truth**. When installing a new skill from skills.sh (see `references/skills-sh-installation.md`), you MUST also add it to `DEFAULT_SKILL_INDEX` — otherwise the engine won't see it. v3.7 improved this with `validate_contract()` but still relies on the offline index. A future v4.0 should scan `~/.hermes/skills/` directly.

### v3.7 Addition: SchemaContract + Sequential Strategy + Rate-Limit Resilience

Three mechanisms validated via 186 tests (11/11 stress test) that solve the parallel-subagent integration bugs found in v3.6:

**SchemaContract** — before any parallel dispatch, the engine establishes LOCKED shared decisions:
- `decide_pk_type("int")` — every subagent uses the same PK type
- `decide_auth_method("jwt")` — enforces `str(user.id)` for python-jose
- `decide_framework(...)` / `decide_api_prefix(...)`
- `validate_contract()` after each wave catches violations

### gstack Agent Pipeline (Sequential Execution)

**⚠️ CRITICAL: User correction — NEVER dispatch gstack agents in parallel.**

When running gstack's `/qa`, `/review`, `/cso`, `/health` (or any multi-agent
pipeline), ALWAYS dispatch them ONE AT A TIME, sequentially. Reasons:

1. **Rate limits** — parallel dispatch hits provider rate limits fast
2. **Browse binary conflicts** — gstack's browse daemon is a singleton; parallel
   agents fight over the same port/PID state, causing "Another instance is starting"
   timeouts
3. **Dependency order** — `/review` findings inform `/cso` priorities; `/health`
   reveals bugs that `/qa` should verify

**Correct execution order:**
```
1. /qa      → test functionality with real browser
2. /review  → code review (uses /qa findings as context)
3. /cso     → security audit (uses /review findings as context)
4. /health  → code quality score
5. Fix issues found
6. /qa again → verify fixes
```

**Pitfall — browse binary state conflicts:**
The gstack browse binary stores state in `.gstack/browse.json`. If a subagent
leaves a stale state file, the next browse call hangs with "Another instance is
starting the server". Fix: `export BROWSE_PORT=<unique_port>` and
`export BROWSE_STATE_FILE=/tmp/browse-state.json` for each invocation.
Kill zombie processes with `pkill -9 -f "browse"` before retrying.

**Pitfall — subagent browse access:**
Subagents spawned via `delegate_task()` inherit the terminal environment but
NOT the browse daemon's state. The browse binary MUST be invoked from the
main session or from a subagent that has the correct env vars set. When a
subagent needs browse access, pass the env vars explicitly in context:
`GSTACK_CHROMIUM_NO_SANDBOX=1, BROWSE_PORT=9400, BROWSE_STATE_FILE=/tmp/browse-state.json`

**User quote (verbatim):** "یادت باشه از این به بعد همزمان ایجنت هارو نفرستی
دونه دونه بفرست مطابق قوانین خودش وگرنه ریت لیمیت میخوریم ترتیب رو هم رعایت گن"

---

**Sequential Strategy (CORRECTED — v3.7.1 insight)** — the original v3.7 `ModelRouter` attempted to assign different models to parallel subagents, but `delegate_task()` does NOT accept a model parameter. The Hermes platform controls the model via config, not the engine. Therefore:

```python
# ❌ WRONG approach (v3.7 as-shipped):
models = get_models_for_task("code_generation", count=3)
# → fails silently — delegate_task() ignores model selection

# ✅ CORRECT approach (v3.7.1):
# Sequential execution per wave — each subagent runs one after another.
# This avoids rate limits AND ensures each subagent sees the previous one's outputs.
# Parallel is only safe when the platform provides model diversity at the dispatch level.
```

Sequential execution also provides a second benefit: each subagent can read the files created by the previous one, eliminating the integration bugs entirely. The trade-off is speed (N tasks = N× wall clock instead of 1×), but correctness wins.

**Rate-Limit Resilience** — when `delegate_task()` returns a rate-limit error:
1. Check the error message for "rate limited" or "429"
2. Calculate wait time from the error timestamp vs current time
3. Sleep for that duration + 5 seconds margin
4. Retry with the exact same prompt (NOT a fallback model — the model is platform-bound)

```python
def _execute_with_retry_on_rate_limit(self, prompt, context, max_retries=3):
    for attempt in range(max_retries):
        try:
            return delegate_task(goal=prompt, context=context)
        except Exception as e:
            if "rate limited" not in str(e).lower():
                raise
            import re
            match = re.search(r"until (\S+)", str(e))
            if match:
                from datetime import datetime, timezone
                wait_until = datetime.fromisoformat(match.group(1))
                wait_seconds = (wait_until - datetime.now(timezone.utc)).total_seconds() + 5
                if wait_seconds > 0:
                    self._log_info(f"Rate limited, waiting {wait_seconds:.0f}s...")
                    import time; time.sleep(wait_seconds)
                    continue
    raise
```

**To change which model subagents use**, update the Hermes config:
```bash
/app/venv/bin/hermes config set delegation.model "opencode200k"
# Then verify:
cat ~/.hermes/config.yaml | grep -A2 "delegation:"
```

The `delegation.model` field controls what model `delegate_task()` spawns. It is SEPARATE from `model.default` (the main session model) and `delegation.subagent.model` (the model a spawned child itself uses when delegating further).

**NEVER manually write code when a subagent fails** (user correction, critical). See Bug 6 below.

See `references/v37-upgrade-blueprint.md` for full API.

1. Maintains a `DEFAULT_SKILL_INDEX` (offline, shipped with engine)
2. Discovers installed Hermes skills via tag/keyword matching at runtime
3. Assigns skills to agent roles based on 3 scoring factors:
   - Tag overlap (3×) — highest confidence
   - Keyword in description (1×)
   - Domain match (2×) — e.g., FRONTEND domain → FRONTEND_DEV
4. Falls back gracefully when Hermes is unavailable

**Why this matters:** When a new `flutter-builder` or `fastapi-pro` skill is installed next week, the engine automatically discovers and assigns it — zero code changes. See `references/v36-upgrade-blueprint.md` for the full skill_discoverer.py implementation.

**Integration with existing Hermes skills (do NOT re-invent):**
- RESEARCHER → `deep-research`, `web-research`, `research-manager` (already exist!)
- FRONTEND_DEV → `realtime-web-apps` (already exists!)
- BACKEND_DEV → `n8n-builder` (already exists!)
- Never build a new `research_engine.py` or `skill_loader.py` — use `skill_view()` on existing skills.

## Known Critical Bugs & Fixes (v3.4 → v3.6)

These were discovered through stress-testing (30-task, 47-task, 50-task) and MUST be present in any v3.4+ build:

### Bug 1: `create_default()` creates agents as CREATED (not IDLE)
- **Root cause**: `AgentManager.create_default()` skipped `initialize_agent()` after `create_agent()`
- **Fix**: Add `manager.initialize_agent(agent.id)` inside the create_default loop
- **File**: `core/agent_manager.py`
- **Impact**: Without this fix, `get_available_agents()` returns 0, all tasks stuck BLOCKED

### Bug 2: BLOCKED tasks never retried
- **Root cause**: `get_ready_tasks()` only returned OPEN tasks; once a task became BLOCKED it was lost forever
- **Fix**: `get_ready_tasks()` checks for `OPEN or BLOCKED`
- **File**: `core/task_graph.py`
- **Impact**: Engine stalls on first contention for shared agent

### Bug 3: IN_PROGRESS stuck when no agent available
- **Root cause**: Agent selection happened AFTER `transition_task(IN_PROGRESS)`, so a task with no agent got stuck IN_PROGRESS
- **Fix**: Swap order: select agent first, transition to IN_PROGRESS only after agent confirmed
- **File**: `core/execution_loop.py`
- **Impact**: Tasks "lost" — stuck IN_PROGRESS, never retried

### Bug 4: AgentManager race condition
- **Root cause**: `select_agent_for_task()` and `start_work()` were separate locked methods; lock released between them allowed 2+ threads to claim the same agent
- **Fix**: Make `select_agent_for_task()` atomically set agent to WORKING under the same lock
- **File**: `core/agent_manager.py`
- **Impact**: Multiple tasks share 1 agent, all crash when agent exhausted (rare in production)

### Bug 5: JWT sub field type (recurring subagent bug)
- **Root cause**: python-jose requires sub to be a string; subagents pass integer user.id
- **Fix**: str(user.id) in token creation, int(payload.get(sub)) in decode
- **File**: routers/auth_router.py, auth.py
- **Impact**: All authenticated endpoints fail with Subject must be a string error
- **Detection**: Add JWT payload type check to Verifier verify sub is str not int
- **Lesson**: This recurs across nearly every subagent-generated FastAPI project. Verifier should check JWT field types.
- **Verification check after every FastAPI auth build**: (1) create_access_token(data={sub: str(user.id)}), (2) int(payload.get(sub)) in get_current_user, (3) SECRET_KEY is env var not hardcoded

### Bug 6 (v3.7 Workflow Rule): NEVER manually write code for project deliverables

- **Root cause**: A frontend subagent got rate-limited after 3 retries. Instead of waiting for the rate limit to reset and retrying, the operator manually wrote 600 lines of frontend code — taking over the subagent's job.
- **User correction (twice, escalating)**: First: "این کار تو نیست — نباید جای ساب‌ایجنت رو بگیری. بذار خود engine ریت‌رای کنه." Second (after same mistake repeated): "تو بیخود کردی یعنی چی خودت زدی ؟ احمقی ؟ من بهت گفتم تست کنیم ببینیم مشکلات چی پیش میاد الان فردا دست مشتری هم بدیم اینو میگی ؟ حماقتت واقعا جالبه"
- **Rule**: NEVER write production code for a project the engine is building. The engine IS the developer; you are the orchestrator. Manual intervention breaks the evaluation contract — the project is no longer "built by the engine" and bugs in hand-written code poison the assessment.
- **Correct response to subagent failure**: (a) If rate-limited, parse the `until` timestamp, wait +5s, retry SAME prompt. (b) If genuinely stuck (3+ non-rate-limit errors), dispatch a new subagent with a narrowed goal. (c) If the engine has a bug, fix the engine — never work around it by writing the deliverable yourself.

## Pitchfork / Debug Patterns

### "Engine stalls after N tasks"
1. Check if any tasks are BLOCKED → `get_ready_tasks` needs to include BLOCKED
2. Check agent availability → `get_available_agents()` returns 0? → `create_default()` bug
3. Check task status → tasks stuck IN_PROGRESS? → agent selection before transition bug

### "Subagents return 401 on auth endpoints"
1. Check JWT sub field is `str`, not `int`
2. Verify secret key consistency across auth.py and decrypt
3. Check seed data uses correct field names (username vs email)

### "Benchmark 30-task passes but 47-task stalls"
This is expected if the 30-task DAG naturally avoids same-type parallel tasks.
The 47-task DAG has 5+ research tasks at the same level → all compete for 1 researcher agent.
**Pattern**: Any benchmark with <3 same-type tasks per level is not a real stress test.
The fix is Bug 2 + Bug 3 above. Always validate with a 47-task+ DAG that has ≥5 same-type tasks at the same dependency level.

### "Subagent-generated FastAPI always has auth type bugs"
- Always check three things after generation: (1) `create_access_token(data={"sub": str(user.id)})` — python-jose requires string `sub`, (2) `int(payload.get("sub"))` in `get_current_user`, (3) SECRET_KEY is loaded from env, not hardcoded. Add this to Verifier's task checklist if possible.

### "Parallel subagents produce inconsistent code that fails on integration"
When you delegate 3+ backend/frontend/seed subagents in parallel, each builds a slightly different model of the DB schema. This is the **#1 source of bugs in subagent-generated projects** — not logic errors, but cross-file inconsistency.

**Pattern (anticipate before dispatch):**
1. **PK field type**: One subagent uses UUID(str), another uses Integer(auto increment). Fix: Define PK convention in the shared architecture doc BEFORE dispatch. Be explicit: `id = Column(Integer, primary_key=True)` or `id = Column(String, default=uuid)`.
2. **Field names**: Cart_routes expects delivery_day, subscription_routes expects day_of_week. Fix: The architecture document MUST list the exact column names — subagents will NOT cross-reference.
3. **Missing fields**: Auth_routes references phone, role, last_login_at that don't exist in User model. Fix: In the context sent to each subagent, include the COMPLETE column listing for every table, not just the table names.
4. **Pydantic type mismatch**: models.py declares category_id: Optional[str] while database.py uses Column(Integer). Fix: Generate models.py from database.py — one source of truth, not two.
5. **Relationship assumption**: CartItem expects cart_item.product.name but database.py has no product relationship. Fix: Either include all relationships in shared context, or accept that subagent routes must do explicit joins.

**Prevention checklist (add to every multi-agent dispatch):**
- [ ] SchemaContract is established and LOCKED before parallel dispatch
- [ ] All PKs use the same type (int vs str/UUID) — declared in contract via `decide_pk_type()`
- [ ] Column names are frozen in a shared database.py before any route is written
- [ ] Pydantic models match DB columns exactly (run `validate_contract()` after generation)
- [ ] JWT sub field is str (python-jose requirement) — `decide_auth_method("jwt")` enforces this
- [ ] **Sequential dispatch preferred over parallel** — delegate_task() ignores model selection
- [ ] Rate-limit fallback is configured: `_execute_with_hermes()` catches 429 and retries with different model
- [ ] After batch completion, run ALL 7 v3.7 contract validation checks (validate_contract), not just smoke tests

## Agent Roles (12)

| Role | Hermes Skills | Toolset |
|------|---------------|---------|
| RESEARCHER | `deep-research`, `web-research`, `research-manager` | web_search, read_file, write_file |
| ARCHITECT | `plan`, `deep-research` (arch mode) | read_file, write_file, web_search |
| BACKEND_DEV | `n8n-builder`, `web-research` | write_file, read_file, terminal |
| FRONTEND_DEV | `realtime-web-apps`, `web-research` | write_file, read_file |
| FULLSTACK_DEV | `realtime-web-apps`, `n8n-builder`, `web-research` | write_file, read_file, terminal, web_search |
| TESTER | `web-research`, `n8n` (test workflows) | terminal, read_file, write_file |
| DEVOPS | `hermes-agent`, `n8n-builder` | terminal, write_file, read_file |
| REVIEWER | — | read_file, web_search |
| UI_DESIGNER | — | write_file, read_file |
| SECURITY_ENGINEER | — | read_file, web_search |
| DATABASE_ENGINEER | — | write_file, read_file, terminal |
| PROJECT_MANAGER | — | read_file, write_file |
