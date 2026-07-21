# Autonomous Project Engine v3.4+ Audit — Final Fixes

## Context
v3.4 had 2 critical bugs remaining after previous audits, discovered via a **47-task real-world DAG stress test** (Multiplayer Chess Platform). A prior 30-task linear-chain test had masked them.

## Bug 1: Same-Type Parallel Starvation (BLOCKED Never Retried)

**Severity:** Critical  
**Test that caught it:** 5 RESEARCH tasks at the same DAG level (same dependency depth), max_parallel=5, 1 researcher agent.

**Timeline (before fix):**
```
Iter 1: exec=5 done=? block=?  ← 2 completed, 3 BLOCKED
Iter 2: exec=0 done=0 block=0  ← STALLED! BLOCKED tasks invisible!
```

**Root cause chain:**
1. `select_agent_for_task()` returns None for 4/5 tasks (only 1 researcher agent)
2. `_execute_single_task()` marks the 4 tasks BLOCKED via `update_task(status=BLOCKED, blocker=...)`
3. `get_ready_tasks()` queries `node.task.status != OPEN → continue` → BLOCKED tasks invisible
4. Engine goes idle, iterations spin until max_iterations

**Two-line fix:**
- `core/task_graph.py` — `get_ready_tasks()`: change `if node.task.status != TaskStatus.OPEN` to `if node.task.status not in (TaskStatus.OPEN, TaskStatus.BLOCKED)`
- `core/execution_loop.py` — `_execute_single_task()`: remove the `update_task(status=BLOCKED)` call when no agent is found. Just return early with a "blocked" status — the task stays OPEN and will be retried next iteration.

## Bug 2: Agent Selection After IN_PROGRESS Causes Stuck Tasks

**Severity:** Critical  
**Test that caught it:** Same as Bug 1 — 5 RESEARCH tasks, 1 agent.

**Root cause:** `_execute_single_task()` transitions task to `IN_PROGRESS` BEFORE calling `select_agent_for_task()`. When no agent is available, the code returns early but the task remains `IN_PROGRESS`. `get_ready_tasks()` doesn't return `IN_PROGRESS` tasks. The task is stuck forever.

**One-line fix:** Swap the order — select agent FIRST, then transition to `IN_PROGRESS` only when an agent is available:
```python
# BEFORE (broken):
self.state.transition_task(task.id, TaskStatus.IN_PROGRESS)
agent = self.agent_manager.select_agent_for_task(task)
if agent is None:
    self.state.update_task(task.id, status=TaskStatus.BLOCKED)  # ← too late, already IN_PROGRESS
    return AgentExecution(status="blocked", ...)

# AFTER (fixed):
agent = self.agent_manager.select_agent_for_task(task)
if agent is None:
    return AgentExecution(status="blocked", ...)  # ← task stays OPEN
self.state.transition_task(task.id, TaskStatus.IN_PROGRESS)
```

## Bug 3: AgentManager Atomic Select+Reserve (Level 2)

**Severity:** Medium  
**Test that caught it:** 5 threads calling `select_agent_for_task(RESEARCH)` — 5/5 got the same researcher agent.

**Root cause:** `select_agent_for_task()` finds an IDLE agent under the lock but returns it without marking it WORKING. Between the return and the caller's `start_work()` call, another thread's `select_agent_for_task()` also finds the same (still IDLE) agent.

**Level 1 fix (was already in v3.4):** Add `threading.RLock` to AgentManager wrapping all public methods. This serializes access but still has a gap between select and start_work.

**Level 2 fix (the proper one):** Merge select+reserve into one atomic operation under the lock:
```python
# Inside select_agent_for_task(), after picking the best agent:
agent = capable[0]
agent.status = AgentState.WORKING       # ← reserve atomically
agent.current_task = task.id
agent.task_start_time = time.time()
self._save_agents()
return agent
```

Then remove the separate `start_work(agent.id, task.id)` call from the execution loop.

## 47-Task DAG Stress Test Results (Post-Fix)

| Metric | Value |
|--------|-------|
| Project | Multiplayer Chess Platform |
| Total tasks | 47 |
| Tasks completed | **47/47 (100%)** |
| Tasks failed | 0 |
| Tasks blocked | 0 |
| Tasks abandoned | 0 |
| Iterations | 27 |
| Total time | 332ms |
| Checkpoints | 4 |
| Agent executions | 47 (100% success) |
| Health score | **93/100 — S (Outstanding)** |
| All agents released | ✅ 12/12 IDLE |

### Per-Phase Breakdown
```
Research   : 5/5 (100%)  
Design     : 5/5 (100%)  
Core Engine: 6/6 (100%)  
Backend    : 8/8 (100%)  
Frontend   : 8/8 (100%)  
Testing    : 7/7 (100%)  
Review     : 4/4 (100%)  
Deployment : 4/4 (100%)  
```

## Key Lesson: The Linear-DAG Trap

A linear-chain DAG (30 tasks, 5 levels) **passes trivially** because each level has 5 different task types → each iteration's ready tasks get different agents → no competition → every task completes. A **real-project DAG** (47 tasks, 8 phases, unbalanceable) stalls at 11% because 5 same-type tasks compete for 1 agent.

**Both tests are mandatory.** The linear chain tests O(N+E) performance. The same-type cluster tests starvation recovery.
