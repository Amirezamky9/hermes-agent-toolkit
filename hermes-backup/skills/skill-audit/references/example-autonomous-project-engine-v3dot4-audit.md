# v3.4 Audit: The Same-Type Parallel Starvation Bug

## Context
The autonomous-project-engine had been iteratively fixed through v1 → v3.3. By v3.4, all 6 known bugs were fixed:
- StateManager thread safety (threading.RLock)
- AgentManager thread safety (threading.RLock)
- Acceptance criteria matching in mock
- max_retries guard against infinite loops
- Recovery transition validation
- Agent pool initialization (CREATED→IDLE)

The 30-task linear-DAG stress test passed perfectly (30/30 in 158ms). **The engine appeared production-ready.**

## The Real-Project Test That Broke It

A 47-task Multiplayer Chess Platform project was built with real-world dependency structure:
- 5 RESEARCH tasks (Phase 0) → 5 DESIGN tasks (Phase 1) → 6 Core Engine (Phase 2) → etc.
- All 5 RESEARCH tasks become ready simultaneously
- **Only 1 researcher agent exists** (one per role)

## The Bug: BLOCKED Tasks Never Retried

```
Iter 1: exec=5 done=2 block=3  <- 3 tasks couldn't get researcher agent
Iter 2: exec=0 done=0 block=0  <- STALLED forever!
...
Iter 100: exec=0 done=0 block=0
Final: 5/47 (11%) completed. 2 BLOCKED, 40 OPEN (never started).
```

**Root cause chain:**
1. `select_agent_for_task()` returns `None` for 3/5 tasks (only 1 researcher, 12 agents total but only 1 for RESEARCH role)
2. `_execute_single_task()` marks the 3 tasks `BLOCKED` via `update_task(status=TaskStatus.BLOCKED)`
3. `get_ready_tasks()` in task_graph.py filters: `if node.task.status != TaskStatus.OPEN: continue` -> BLOCKED tasks are invisible
4. Engine reports `idle` every iteration until max_iterations, zero additional progress

**Why the 30-task test didn't catch this:**
The 30-task test used a linear chain: T0->T5->T10->T20->T25 where each level has exactly one task of each type. No iteration ever contains multiple tasks of the same type. The agent pool's 1-per-role design was never stressed.

## The Fix (2 lines)

**File: core/task_graph.py** -- `get_ready_tasks()`:
```python
# BEFORE:
if node.task.status != TaskStatus.OPEN:
    continue

# AFTER:
if node.task.status not in (TaskStatus.OPEN, TaskStatus.BLOCKED):
    continue
```

**File: core/execution_loop.py** -- `_execute_single_task()`:
```python
# BEFORE:
if agent is None:
    self.state.update_task(task.id, status=TaskStatus.BLOCKED)  
    return AgentExecution(..., status="blocked")

# AFTER:
if agent is None:
    # Don't persist BLOCKED -- task stays OPEN, retried next iteration
    return AgentExecution(..., status="blocked")
```

## Detection Heuristic

For any autonomous skill engine, run TWO stress tests:
1. **Chain DAG**: 30 tasks, 5-level linear chain -> tests basic execution loop
2. **Same-Type Cluster**: 5+ tasks of the SAME type at the same DAG level -> tests agent pool contention

If test 1 passes but test 2 stalls, the engine has the BLOCKED-task starvation bug regardless of all other metrics.
