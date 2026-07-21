# Stress-Test Benchmark Methodology

## Purpose

Unit tests and even end-to-end flow tests verify correctness, but they don't answer: **"Can this skill actually run for multi-hour autonomous projects without stalling?"**

A stress-test benchmark fills that gap. It exercises the skill under a workload large enough to expose:
- Silent infinite loops (loop spins until `max_iterations` with zero output)
- State-transition bugs that only appear after N iterations
- Agent-pool exhaustion or incorrect lifecycle management
- Checkpoint/recovery degradation over time
- Parallel-execution correctness (are tasks truly parallel or sequential?)
- Memory/resource leaks across iterations

## When to Use

After the standard audit (package structure → deps → Hermes integration → code hygiene → execution readiness → robustness → docs → e2e flow), run this benchmark when:

- The skill claims to support **long-running autonomous execution** (multi-hour projects)
- The skill has an **execution loop** that runs multiple iterations
- The skill **spawns and manages agents** over multiple cycles
- The skill has a **task graph / DAG** with dependencies
- The user asks "is this actually ready for production?"

## Benchmark Structure

### Phase 1a: Complex Task DAG

Create a non-trivial project with **30+ tasks** and multi-level dependency chains:

| Level | Tasks | Depends On | Task Types | Purpose |
|-------|-------|------------|------------|---------|
| 1 | T0–T4 | none | Research | Root tasks — independent |
| 2 | T5–T9 | T0–T4 | Design | Fan-out from level 1 |
| 3 | T10–T19 | T5–T9 | Implementation | Heaviest level — fan-out |
| 4 | T20–T24 | T10–T14 | Testing | Depends on half of level 3 |
| 5 | T25–T29 | T15–T19, T20–T24 | Review/Deploy | Depends on level 3 + 4 |

Mix task types and priorities across all 30 tasks to simulate real project diversity:
- **Task types**: RESEARCH, DESIGN, IMPLEMENTATION, TESTING, REVIEW, DEPLOYMENT (cycle through them)
- **Priorities**: CRITICAL, HIGH, MEDIUM, LOW (cycle through them)

### Phase 1b: Same-Type Starvation Test (MANDATORY)

**This is the most dangerous bug pattern because it passes linear-chain tests and fails on real projects.**

Build 5+ tasks of the SAME type at the same DAG level (e.g. 5 RESEARCH tasks with no dependencies). A linear chain like `T0→T5→T10→T20→T25` naturally distributes types across iterations, so each task type gets its own agent. Real projects often have 5+ RESEARCH tasks ready simultaneously. With only 1 agent per role, 4 tasks will be starved.

```python
for i in range(5):
    sm.add_task(TaskDefinition(id=f'R{i}', title=f'R{i}', description='',
        type=TaskType.RESEARCH, priority=TaskPriority.MEDIUM))
loop = ExecutionLoop(sm, ExecutionConfig(max_parallel_tasks=5))
loop.agent_manager = AgentManager.create_default(sm)
for it in range(10):
    r = loop.run_iteration()
# PASS = all 5 complete within 6 iterations
# FAIL = stalls at N/5 with rest BLOCKED/OPEN forever  
```

**Root cause when this fails:**
1. `select_agent_for_task()` returns None for 4/5 tasks (only 1 researcher)
2. `_execute_single_task()` marks them BLOCKED via `update_task(status=BLOCKED)`
3. `get_ready_tasks()` only returns OPEN tasks → BLOCKED tasks invisible
4. Engine stalls permanently

**Two-line fix:**
- `get_ready_tasks()`: `if node.task.status not in (OPEN, BLOCKED): continue`
- Don't persist BLOCKED status — just skip the task and let it stay OPEN for next iteration. Also: swap the order so agent selection happens BEFORE `transition_task(IN_PROGRESS)`, otherwise tasks get stuck IN_PROGRESS when no agent is found.

### Phase 1c: Real-World Project Scale (Optional)

After the 30-task DAG and same-type test, optionally test with a **real-world project** (40-50 tasks with realistic dependency structure like Research→Design→Core→Backend→Frontend→Testing→Review→Deployment). A 30-task chain test passed at 100% but a 47-task chess platform with the same engine stalled at 11% — the difference was that the 30-task chain naturally avoided same-type parallelism while the 47-task project had clusters of same-type tasks. The same-type starvation test (Phase 1b) catches this directly.

### Phase 2: Graph Operations Benchmark

Measure the TaskGraph's raw performance under load:

| Operation | Metric | Expected (O(N+E)) | Red Flag |
|-----------|--------|--------------------|----------|
| Graph build | `time` | <10ms for 30 nodes | >100ms |
| Topological sort | `time` | <5ms | >50ms |
| Critical path (DP) | `time` | <5ms | >50ms |
| Parallel groups | `time` | <5ms | >50ms |
| Validation | `time` | <5ms | >50ms |

**Check**: Does `topological_sort()` preserve dependency ordering? Test with the 30-task DAG.

### Phase 3: Execution Loop — 10+ Iterations

Run the execution loop for 10 iterations and track:

```python
for iteration in range(10):
    iter_start = time.time()
    result = loop.run_iteration()
    iter_time = time.time() - iter_start
    
    # Track per-iteration
    tasks_executed     = result.tasks_executed
    tasks_completed    = result.tasks_completed
    tasks_failed       = result.tasks_failed
    tasks_blocked      = result.tasks_blocked
```

**Key metrics:**
- Tasks per iteration (should be `min(ready_tasks, max_parallel_tasks)`)
- Completion per iteration (should be >0 if agents are working)
- Blocked per iteration (should be 0 unless legitimately blocked)
- Iteration time trend (flat = healthy, increasing = leak/slowdown)

**Red flags:**
- `tasks_executed=0` every iteration → execution loop has a bug
- `tasks_blocked=N` and `tasks_completed=0` every iteration → agent pool not populated or agents wrong status
- Iteration time grows linearly → resource leak per iteration
- Loop completes all 10 iterations with `status="running"` and never hits `"completed"` → missing completion transition

### Phase 4: Final State Analysis

After the benchmark iterations, inspect the full state:

| Check | Expected | Red Flag |
|-------|----------|----------|
| Project state | `executing` or `completed` | `failed` |
| Tasks completed | >0 | 0 |
| Tasks blocked | Should be 0 for ready tasks | All tasks blocked |
| Checkpoints created | At least 1 | 0 |
| Agent statuses | Mix of IDLE, WORKING | All CREATED |

### Phase 5: Performance & Throughput

Compute aggregate metrics:

```python
total_time        = sum(iteration_times)
avg_iter_time     = total_time / iterations
min_iter_time     = min(iteration_times)
max_iter_time     = max(iteration_times)
tasks_per_second  = total_completed / total_time
```

**Compare to baseline:**
- With `_execute_mock` (no real Hermes): expect ~0.01–0.05s/iter, ~50-200 tasks/s
- With real `delegate_task`: expect ~5-15s/iter (depends on model + task complexity)

### Phase 6: Recovery & Edge Cases

Separate from the main loop — test recovery mechanisms directly:

| Test | What to Verify |
|------|---------------|
| Task retry | `recover_from_failure({"type":"task_failure", ...})` → `status="recovered"` |
| Max retries | Task with `retry_count = max_retries` → `status="escalated"` |
| Rollback | `rollback_to_checkpoint(id)` → check state restored |
| Cycle detection | Adding edge that creates cycle → `ValueError` |
| Self-loop | Adding edge to self → `ValueError` |
| Empty graph | `topological_sort()` → `[]` (no crash) |
| Single node | `find_critical_path()` → `[node_id]` |

### Phase 7: Stress Under Scale

If time permits, test with progressively larger task graphs:

| Scale | Nodes | Edges | Expected Build Time | Expected Sort Time |
|-------|-------|-------|---------------------|--------------------|
| Small | 30 | ~50 | <10ms | <5ms |
| Medium | 200 | ~400 | <50ms | <30ms |
| Large | 1000 | ~3000 | <500ms | <300ms |

If O(N+E) algorithms are correctly implemented, build and sort should scale linearly with (nodes + edges). Quadratic or exponential algorithms will show dramatic slowdown at the Large scale.

## Interpreting Results

### PASS threshold
- ✅ All 7 phases complete without crash
- ✅ >0 tasks completed in Phase 3
- ✅ Iteration time doesn't grow monotonically
- ✅ Recovery tests pass
- ✅ Edge cases handled correctly

### PARTIAL threshold
- ⚠️ Loop runs but 0 tasks completed (agent pool issue or wrong agent status)
- ⚠️ Recovery works but some retries don't restore state
- ⚠️ Performance degrades >2x across 10 iterations

### FAIL threshold
- ❌ Crash on `run_project()` with standard goal
- ❌ Infinite loop (never hits completion or max iterations)
- ❌ 0 tasks executed across all iterations
- ❌ All tasks BLOCKED due to agent creation bug
- ❌ Checkpoint/restore corrupts state

## Critical Question: "Is this suitable for multi-hour projects?"

Answer based on:
1. **No silent failures**: Did all tasks either complete or fail explicitly? (Not just stuck silently.)
2. **State persistence**: Are checkpoints created and restorable? (Needed for crash recovery in hour-long runs.)
3. **Agent lifecycle**: Do agents reset to IDLE after each task? (Otherwise pool exhausts after N tasks.)
4. **Parallelism**: Does `max_parallel_tasks` actually launch simultaneous work? (Sequential = no speedup for large projects.)
5. **Throughput stability**: Does iteration time stay flat across 10+ iterations? (Growing time = leak.)
6. **No iteration-count dependence**: Does the loop compute next work correctly regardless of iteration number? (Hardcoded `iter_count` thresholds are fragile.)

### Phase 3.5: Parallel-Execution Integrity (Critical)

If the execution loop uses `ThreadPoolExecutor` (or similar) for parallel task execution AND the state manager is file-backed, explicitly test for **race conditions**. This is the #1 silent killer of autonomous engines.

**Why it fails:** Each parallel thread:
1. Reads `tasks.json` (gets all N tasks)
2. Modifies one task (e.g. T1 → IN_PROGRESS)
3. Writes ALL N tasks back to `tasks.json`

Thread A and Thread B run concurrently. Thread A writes T1=IN_PROGRESS, T2=PENDING. Thread B writes T2=COMPLETED, T1=PENDING (old read). **Thread A's write overwrites Thread B's changes** — T2 goes from COMPLETED back to PENDING. Over enough iterations, all tasks end up IN_PROGRESS or OPEN — zero reach COMPLETED.

**Detection script:**
```python
import tempfile, time, threading
from pathlib import Path
from core import *

tmp = Path(tempfile.mkdtemp())
sm = StateManager(tmp)
sm.create_project("race-test", "Race Test", "Detect parallel corruption")
sm.transition_project(ProjectState.ANALYZING)
sm.transition_project(ProjectState.SPECIFICATION_READY)
sm.transition_project(ProjectState.PLANNING)
sm.transition_project(ProjectState.EXECUTING)

# Add tasks
for i in range(6):
    t = TaskDefinition(id=f"T{i}", title=f"T{i}", description=f"T{i}",
        type=TaskType.IMPLEMENTATION, priority=TaskPriority.MEDIUM)
    sm.add_task(t)

# Run with parallel=3
loop = ExecutionLoop(sm, ExecutionConfig(max_parallel_tasks=3))
loop.agent_manager = AgentManager.create_default(sm)

state_histories = []
for _ in range(5):
    loop.run_iteration()
    tasks = sm.load_tasks()
    state_histories.append({t.id: t.status.value for t in tasks})

# Check: did any COMPLETED task revert to OPEN/IN_PROGRESS in a later snapshot?
for i in range(1, len(state_histories)):
    for task_id, status in state_histories[i].items():
        prev_status = state_histories[i-1].get(task_id)
        if prev_status == "completed" and status in ("open", "in_progress"):
            print(f"❌ RACE CONDITION: {task_id} went {prev_status} → {status} (iteration {i})")
```

**Red flags:**
- `completed` counts oscillate across iterations (2 → 1 → 2 → 0 → 1)
- Same task ID appears in multiple statuses across parallel threads
- `StateManager` has no `threading.Lock` around any read-modify-write operation
- More tasks completed in iteration N than all previous iterations combined (sign of stale overwrites being "corrected")

**Fix:** Either (a) add `threading.Lock` to every `StateManager` operation that reads then writes, or (b) disable parallelism when using file-backed state (`max_parallel_tasks=1`). Option (a) is correct — the lock serializes file access while keeping logical parallelism.

### Phase 3.6: Mock Executor Compliance Trap

`_execute_mock()` returning `{"success": True, "files_created": [], "errors": [], "summary": "Mock execution completed..."}` creates a **false-success loop**. The execution loop believes work was done, but:

1. The verifier's `_verify_acceptance_criteria()` checks if acceptance criteria keywords appear in `str(task.result)`
2. The mock summary does NOT contain those keywords → verification fails
3. Recovery resets the task to OPEN → next iteration picks it up → mock runs again → verification fails again
4. **Endless loop to max_iterations with zero output**

**Detection:** If `tasks_executed > 0` but `tasks_completed == 0` and iteration time is very fast (<0.5s), this is the culprit. Check `task.result` after mock execution — does it contain the acceptance criteria?

**Fix:** Either (a) make mock mode return criteria keywords in its summary, or (b) skip acceptance criteria check when `HERMES_AVAILABLE == False` (mock mode). Option (b) is safer — mock mode should never produce real-looking results.

## When NOT to Use

- Quick single-turn skills (one lookup, one file write, one web search) — they don't have an execution loop
- Skills with no state machine / DAG / agent lifecycle — there's nothing to stress
- Skills that the user explicitly asks for a shallow review of only
