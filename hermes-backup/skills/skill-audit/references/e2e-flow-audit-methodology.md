# End-to-End Execution Flow Audit Methodology

Definitive pattern for catching cross-module orchestration bugs that unit tests miss. Developed during the autonomous-project-engine v3 audit (July 2026).

## The Problem

A skill passes 123/123 unit tests across 8 test files. Every module imports. Every class instantiates. Every method returns the right type. Yet calling `run_project("Build an API")` produces zero output — all tasks block, state transitions crash, and the loop spins to max iterations.

**Root cause:** Unit tests verify modules in isolation. Orchestration bugs live in the gaps *between* modules — a missing transition state here, an unpopulated agent pool there, unparsed subagent output everywhere. These bugs are invisible to pytest and lethal to production use.

## The 8-Step Penetration Test

Follow these steps in order. Each builds on the one before.

### Step 1: Package Import Smoke Test

```bash
cd <skill-root>
python -c "from core import run_project, StateManager, TaskGraph, AgentManager, Verifier, ExecutionLoop, AgentOrchestrator; print('ALL IMPORTS OK')"
```

If any import fails (especially `from .` vs `from core.` absolute imports), stop and fix before proceeding.

### Step 2: Entry Point Signature

```bash
python -c "from core import run_project; help(run_project)"
```

Verify: does the signature match what `SKILL.md` describes? Are `Args` and `Returns` documented? Is `project_dir` optional or required?

### Step 3: Trace the Full Entry Point Path

Read the entry-point function (e.g. `run_project()` in `__init__.py`). For every module call, answer:

1. **State transitions** — trace every `transition_project()` call against the project's `VALID_PROJECT_TRANSITIONS` dict. Is each `from_state → to_state` pair listed? A single skipped intermediate state (e.g. `ANALYZING → PLANNING` when the dict requires `ANALYZING → SPECIFICATION_READY → PLANNING`) crashes the pipeline at runtime.

2. **Agent pool** — is `AgentManager` instantiated? Is `create_default()` (or equivalent) called before any `select_agent_for_task()` call? If not, every task blocks with `"no_available_agent"`.

3. **Subagent output parsing** — find the `delegate_task()` call. Does the handler return structured data (`files_created`, `files_modified`, `errors`) or is it `str(result)` with hardcoded `[]` for file lists?

### Step 4: State Manager Simulation

Write a throwaway script that exercises the full state lifecycle:

```python
import tempfile; from pathlib import Path
from core import StateManager, TaskDefinition, TaskType, TaskPriority, TaskStatus

tmp = Path(tempfile.mkdtemp())
sm = StateManager(tmp)
sm.create_project("test-proj", "Test", "Build API")
t1 = TaskDefinition(id="T1", title="Research", description="Research", type=TaskType.RESEARCH, priority=TaskPriority.HIGH)
t2 = TaskDefinition(id="T2", title="Implement", description="Implement", type=TaskType.IMPLEMENTATION, priority=TaskPriority.HIGH, dependencies=["T1"])
sm.add_task(t1); sm.add_task(t2)

# Valid task transition chain: OPEN → IN_PROGRESS → COMPLETED
sm.transition_task("T1", TaskStatus.IN_PROGRESS)
sm.transition_task("T1", TaskStatus.COMPLETED)
ready = sm.get_ready_tasks()
print(f"Ready: {[t.id for t in ready]}")  # Should include T2
assert "T2" in [t.id for t in ready]

# Checkpoint
cp = sm.create_checkpoint()
```

Key signals: `get_ready_tasks()` should return T2 after T1 is COMPLETED. Checkpoint must not raise.

### Step 5: TaskGraph Real DAG

```python
from core import TaskGraph, TaskDefinition, TaskType, TaskPriority

graph = TaskGraph()
t1 = TaskDefinition(...); t2 = TaskDefinition(...); t3 = TaskDefinition(...); t4 = TaskDefinition(...)
graph.add_node(t1); graph.add_node(t2); graph.add_node(t3); graph.add_node(t4)
graph.add_edge("A", "B"); graph.add_edge("A", "C"); graph.add_edge("B", "D"); graph.add_edge("C", "D")

print(f"Topo sort: {graph.topological_sort()}")     # ['A', 'B', 'C', 'D'] or ['A', 'C', 'B', 'D']
print(f"Critical path: {graph.find_critical_path()}") # ['A', 'B', 'D'] (longest)
print(f"Parallel groups: {graph.get_parallel_groups()}") # [['B', 'C']]
print(f"Validate: {graph.validate()}")                 # {'valid': True}
```

### Step 6: Verifier Real Check

```python
import tempfile; from pathlib import Path
from core import Verifier, TaskDefinition, TaskType, TaskPriority, VerificationMethod

tmp = Path(tempfile.mkdtemp())
(tmp / "good.py").write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
(tmp / "bad.py").write_text("def broken(:\n")

v = Verifier()
task = TaskDefinition(id="T1", title="Code", description="Code", type=TaskType.IMPLEMENTATION, priority=TaskPriority.HIGH, verification_method=VerificationMethod.CODE_REVIEW)
result = v.verify_task(task, tmp)
print(f"Passed: {result.passed}")
for c in result.checks:
    print(f"  {c.name}: {'✅' if c.passed else '❌'}")
```

### Step 7: Execution Loop Iteration

```python
from core import StateManager, ExecutionLoop, ExecutionConfig, TaskDefinition, TaskType, TaskPriority

tmp = Path(tempfile.mkdtemp())
sm = StateManager(tmp)
sm.create_project("proj-1", "Test", "Goal")
for i in range(3):
    sm.add_task(TaskDefinition(id=f"T{i+1}", title=f"Task {i+1}", description=f"Do {i+1}", type=TaskType.IMPLEMENTATION, priority=TaskPriority.MEDIUM))

loop = ExecutionLoop(sm)
result = loop.run_iteration()
print(f"Status: {result.status}, executed: {result.tasks_executed}, completed: {result.tasks_completed}")
```

### Step 8: Full Loop With Recovery

```python
loop2 = ExecutionLoop(sm, ExecutionConfig(checkpoint_interval=1))
for _ in range(3):
    loop2.run_iteration()
status = loop2.get_status()
print(f"After 3 iterations: {status}")
```

### Step 9: Parallel-Execution Race Check (if applicable)

If the execution loop uses any parallel execution mechanism (`ThreadPoolExecutor`, `asyncio`, etc.) AND the state manager is file-backed, do NOT skip this step. Parallel race conditions are the #1 silent killer of autonomous engines — all unit tests pass, e2e flow passes, but under load the engine silently produces zero output.

Write a script that runs 5 iterations of a 6-task project with `max_parallel_tasks=3` and checks for state corruption:

```python
import tempfile
from pathlib import Path
from core import *

tmp = Path(tempfile.mkdtemp())
sm = StateManager(tmp)
sm.create_project("race-test", "Race Test", "Detect parallel corruption")
sm.transition_project(ProjectState.ANALYZING)
sm.transition_project(ProjectState.SPECIFICATION_READY)
sm.transition_project(ProjectState.PLANNING)
sm.transition_project(ProjectState.EXECUTING)

for i in range(6):
    sm.add_task(TaskDefinition(id=f"T{i}", title=f"T{i}", description=f"T{i}",
        type=TaskType.IMPLEMENTATION, priority=TaskPriority.MEDIUM))

loop = ExecutionLoop(sm, ExecutionConfig(max_parallel_tasks=3))
loop.agent_manager = AgentManager.create_default(sm)

histories = []
for _ in range(5):
    loop.run_iteration()
    tasks = sm.load_tasks()
    histories.append({t.id: t.status.value for t in tasks})

# Check: did any COMPLETED task revert to a prior status?
races_found = 0
for i in range(1, len(histories)):
    for task_id, status in histories[i].items():
        prev = histories[i-1].get(task_id)
        if prev == "completed" and status in ("open", "in_progress"):
            races_found += 1

# Also check: did any iteration show tasks_completed=0 despite tasks_executed>0?
```

**Red flags:**
- `histories` shows tasks oscillating between statuses across iterations
- Completed count goes up then down then up again
- Multiple tasks end IN_PROGRESS after 5 iterations of a 6-task project with enough retries
- `StateManager` has no `threading.Lock` around any read-modify-write operation

**Diagnosis guide:**
- If `tasks_executed > 0` and `tasks_completed == 0` AND iteration times are fast (<0.5s/iter), check for **mock → acceptance criteria loop**: the mock executor's empty result lacks acceptance criteria keywords → verifier always fails → recovery resets → endless loop. Fix: skip acceptance checks when `HERMES_AVAILABLE == False`, or make mock results include criteria text.
- If task statuses oscillate across iterations (COMPLETED → OPEN → COMPLETED → IN_PROGRESS), check for **parallel race corruption**: threads overwrite each other's state changes. Fix: add `threading.Lock` to StateManager or disable parallelism for file-backed state.
- If recovery always resets tasks to OPEN without increasing their retry count or moving through valid transitions, check **recovery bypasses transition validation**. Fix: recovery must use `transition_task()` with valid paths (e.g. `FAILED → OPEN`) not raw `setattr`.

## Reading the Results

| Signal | Interpretation | Severity |
|--------|---------------|----------|
| Import fails with `ModuleNotFoundError` | Missing `__init__.py` or wrong Python path | 🔴 |
| `transition_project()` raises `ValueError` | Missing intermediate state in transition chain | 🔴 |
| `get_ready_tasks()` returns empty after deps satisfied | Bug in `_reverse_edges` or dependency logic | 🔴 |
| `tasks_executed > 0` but `tasks_completed == 0` | Agent pool empty OR mock returns unprocessed | 🔴 |
| Blocked tasks show `blocker="no_available_agent"` | `AgentManager.create_default()` never called | 🔴 |
| Verifier checks return passed with 0 files checked | `delegate_task` output not parsed → empty dir scanned | 🟡 |
| `find_critical_path()` returns wrong path | DP bug or missing edge direction | 🔴 |
| `run_until_complete()` hits `max_iterations` | Silent loop — tasks never move to COMPLETED | 🔴 |

## The 50-Line Fix Pattern

Most E2E bugs resolve in under 100 lines. The autonomous-project-engine v3 needed:

| Fix | Lines | File to Modify |
|-----|-------|---------------|
| Add `SPECIFICATION_READY` state transition | 1 | `__init__.py` |
| Call `agent_mgr.create_default()` before loop | 1 | `__init__.py` |
| Parse `delegate_task` output for `files_created` | ~20 | `agent_orchestrator.py` |
| Add `ThreadPoolExecutor` for parallel execution | ~15 | `execution_loop.py` |
| Import `HermesStateManager` in entry point | ~3 | `__init__.py` |
| Fix absolute import to relative | 1 | `agent_prompts.py` |
| **Total** | **~41** | |

## Principle

A skill that passes all unit tests but crashes on `run_project()` is not "almost there" — it is disconnected. The E2E flow audit connects the dots. Run it every time before signing off on a skill's production readiness.
