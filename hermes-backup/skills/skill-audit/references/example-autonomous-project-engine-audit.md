# Example Audit: "autonomous-project-engine" (v3 — 2026-07-13)

**Session**: 2026-07-13 — User uploaded `v3_out` of the autonomous-project-engine, a Hermes-native skill for autonomous project execution with agent delegation.

## Key Differentiator from v2

v3 is a **complete rewrite** — the entire architecture changed from v2's ad-hoc scripts to a proper Python package with dataclass-based schema, atomic file persistence, real AST-based verification, and O(N+E) DAG algorithms. Unlike v2 which was purely aspirational, v3 has **123 passing tests** and every module is actually importable.

## Audit Framework Used

This audit followed the **8-step penetration test methodology**:

1. **Package Import** — `from core import ...` all modules
2. **Entry Point** — `help(run_project)` to verify signature/documentation
3. **Logic Gap** — Read `__init__.py` and `agent_orchestrator.py` to trace execution path
4. **Import Paths** — Test from inside vs outside the package directory
5. **State Simulation** — All CRUD operations: create, read, update, delete, transition, checkpoint
6. **Graph Execution** — Topological sort, critical path, parallel groups on real DAG
7. **Verifier Execution** — Real AST analysis with syntactically good and bad files
8. **Full Execution Loop** — Run `run_iteration()` with real state manager

## Findings

### ✅ 1. Package Structure — PASSED
- `SKILL.md` at root with valid frontmatter
- `core/` has `__init__.py` (proper package)
- `tests/` has 8 test files (123 tests total)
- `references/` directory exists
- **All** Python files are importable

### ✅ 2. Entry Point — PASSED
```python
def run_project(goal: str, project_dir: str = None) -> str
    Main entry point called by Hermes.
```
Proper signature, typed parameters, docstring with Args/Returns.

### ⚠️ 3. Execution Path — CROSS-TALK BUG FOUND

**`run_project()` state transitions are wrong.** The code does:
```python
state.transition_project(ProjectState.ANALYZING, ...)  # CREATED → ANALYZING ✓
# ... create_plan() ...
state.transition_project(ProjectState.PLANNING, ...)   # ANALYZING → PLANNING ✗
```

The valid transition table in `schema.py` says:
```
ANALYZING → [SPECIFICATION_READY, CREATED]  # NOT PLANNING
SPECIFICATION_READY → [PLANNING, ANALYZING]  # THIS IS WHERE PLANNING GOES
```

**Actual:** `run_project()` calls `state.transition_project(ProjectState.PLANNING, ...)` while in `ANALYZING` state → **ValueError**. User never reaches execution.

The fix: insert `SPECIFICATION_READY` between `ANALYZING` and `PLANNING`:
```python
state.transition_project(ProjectState.ANALYZING, ...)           # CREATED → ANALYZING
state.transition_project(ProjectState.SPECIFICATION_READY, ...)  # ANALYZING → SPEC_READY
state.transition_project(ProjectState.PLANNING, ...)            # SPEC_READY → PLANNING
state.transition_project(ProjectState.EXECUTING, ...)          # PLANNING → EXECUTING
```

### ⚠️ 4. Agent Spawning — NOT WIRED

`AgentOrchestrator._execute_with_hermes()` imports `delegate_task`:
```python
try:
    from hermes_tools import delegate_task
    HERMES_AVAILABLE = True
except ImportError:
    HERMES_AVAILABLE = False
```

**When `HERMES_AVAILABLE = True`:**
```python
result = delegate_task(goal=prompt, context=..., toolsets=..., role="leaf")
return {
    "success": True,
    "summary": str(result),      # ← str() of TaskResult object
    "files_created": [],          # ← ALWAYS empty
    "files_modified": [],         # ← ALWAYS empty
    "errors": [],                 # ← ALWAYS empty
}
```

**The `delegate_task` result is never parsed.** It's a `TaskResult` object with `files_created`, `files_modified`, `errors` fields — but `_execute_with_hermes()` just does `str(result)` and discards the structured data.

**When `HERMES_AVAILABLE = False` (mock):**
Same thing — hardcoded `[]` for everything.

### ⚠️ 5. Execution Loop — AGENTS DON'T EXIST

The `run_project()` flow:
```python
planner = Planner(state)
plan = planner.create_plan(specification)  # Creates TaskDefinitions with IDs
loop = ExecutionLoop(state, config)        # Creates AgentManager, AgentOrchestrator
loop.run_until_complete(max_iterations=50)  # Runs iterations...
```

But `ExecutionLoop.__init__` creates:
```python
self.agent_manager = AgentManager(state_manager)   # No default agents
self.orchestrator = AgentOrchestrator(state_manager)
```

**`AgentManager.__init__`** loads agents from `state_manager` — which has **zero** agents. When `run_iteration()` calls `self.agent_manager.select_agent_for_task(task)`, it returns `None` → task gets `blocker="no_available_agent"` → BLOCKED.

**Fix**: Call `AgentManager.create_default()` before the loop starts:
```python
loop = ExecutionLoop(state, config)
loop.agent_manager.create_default()  # ← Pre-create all 12 agents
```
Or better: move agent creation into `run_project()` before `ExecutionLoop`:
```python
agent_mgr = AgentManager(state)
agent_mgr.create_default()  # Creates one agent per role
```

### ✅ 6. State Manager — PASSED

All CRUD operations work:
- `create_project()` ✓
- `transition_project()` ✓ (with correct chain)
- `add_task()` / `get_task()` / `update_task()` ✓
- `create_checkpoint()` ✓ (atomic writes)
- `get_ready_tasks()` ✓ (correctly identifies dependency-satisfied tasks)

### ✅ 7. TaskGraph — PASSED

- `topological_sort()` → `['A', 'B', 'C', 'D']` ✓
- `find_critical_path()` → `['A', 'B', 'D']` ✓
- `get_parallel_groups()` → `['B', 'C']` ✓
- `validate()` → `{'valid': True}` ✓

### ✅ 8. Verifier — PASSED (does real work)

- `ast.parse()` for syntax checking ✓
- Cyclomatic complexity via AST walk ✓
- Security pattern detection (hardcoded passwords, SQL injection, XSS) ✓
- Line length / trailing whitespace linting ✓

Does NOT just hardcode `passed=True` — unlike v2.

## Summary Table

| Dimension | Score | Key Finding |
|----------|-------|-------------|
| Package Structure | 🟢 | Proper package with `__init__.py`, valid SKILL.md |
| Entry Point | 🟢 | `run_project(goal, project_dir)` exists with docstring |
| Execution Path | 🔴 | State machine skips `SPECIFICATION_READY` → crashes |
| Agent Spawning | 🔴 | `AgentManager` has no agents → all tasks BLOCKED |
| Agent Output | 🔴 | `_execute_with_hermes()` returns `[]` always, never parses `delegate_task` |
| State Manager | 🟢 | All CRUD, atomic writes, checkpoints work |
| TaskGraph | 🟢 | 123/123 tests pass |
| Verifier | 🟢 | Does real AST/code analysis |

## Key Lessons for This Version

1. **State transition chains are fragile** — a single missing step in `__init__.py` (`SPECIFICATION_READY`) crashes the entire entry point. Always trace the `VALID_PROJECT_TRANSITIONS` dict when writing a new chain.

2. **Proxy agents (e.g. `AgentManager`) need to be populated** — creating a manager and expecting it to have agents is not enough. `create_default()` or equivalent must be called explicitly in the entry-point flow.

3. **Subagent work product must be parsed** — `delegate_task()` returns a `TaskResult` object with structured fields. `str(result)` discards everything. The correct approach:
   ```python
   result = delegate_task(...)
   return TaskResult(
       files_created=result.get("files_created", result.files_created if hasattr(result, "files_created") else []),
       ...
   )
   ```

4. **123 passing tests + crashing entry point = NOT production-ready** — test coverage on individual modules is necessary but not sufficient. The integration test (`run_project()` with real parameters) caught a cross-module bug that no unit test would find.

5. **Mock mode is never a substitute for real execution** — `_execute_mock()` returns `success=True, files_created=[]` which makes the execution loop think work was done. In real Hermes, this produces an empty project.

## Recommended Fix (80-100 lines)

```python
# In core/__init__.py, around line 83-100:
# Fix state transition chain
state.transition_project(ProjectState.ANALYZING, "Starting goal analysis")
state.transition_project(ProjectState.SPECIFICATION_READY, "Specification ready")  # NEW

# Set up agents before execution
agent_mgr = AgentManager(state)
agent_mgr.create_default()  # NEW — populate agent pool

# ... create plan ...
plan = planner.create_plan(specification)

# Transition through planning
state.transition_project(ProjectState.PLANNING, "Plan created")
state.transition_project(ProjectState.EXECUTING, "Starting execution")

# Build execution loop
loop = ExecutionLoop(state, config)
# Run
result = loop.run_until_complete(max_iterations=50)
```