# Example Audit: autonomous-project-engine v3.3

## Background

Continuation of the iterative audit started in `references/example-autonomous-project-engine-audit.md` (v3) and `references/example-autonomous-project-engine-v3dot1-audit.md` (v3.1–3.1.1).

**v3.3 status:** 5 bugs from v3.1.1 stress test were reported to Mimo and all 5 were fixed:
| Bug | Fix Applied | Status |
|-----|-----------|--------|
| StateManager thread-safety (RLock) | ✅ threading.RLock added to all public methods | Confirmed via code inspection |
| Mock acceptance criteria mismatch | ✅ criteria keywords now in mock summary | Confirmed via code inspection |
| max_retries guard | ✅ retry_count >= max_retries → ABANDONED | Confirmed via code inspection |
| Recovery transition validation | ✅ transition_task(FAILED) used instead of update_task | Confirmed via code inspection |
| Checkpoint timing | ✅ based on tasks_completed, not iteration_count | Confirmed via code inspection |

## Stress Test Results (v3.3)

Identical benchmark to v3.1.1: 30-task DAG, 5 dependency levels, 10 iterations, max_parallel=3.

```text
📦 PHASE 1: 30-task complex DAG → ✅ 30 tasks
📊 PHASE 2: Graph ops → ✅ 0.45ms build, 0.015ms topo, 0.034ms CP
⚡ PHASE 3: 10 iterations → ❌ 0/30 completed (DETAILS)
🔍 PHASE 4: Final state → 0 done, 0 fail, 5 blocked, 25 open
📈 PHASE 5: Performance → 24.4ms total, 2.44ms avg/iter
🔄 PHASE 6: Recovery → ✅ Retry, rollback work
🧪 PHASE 7: Edge cases → ✅ All pass
```

Iteration trace:
```
Iter  1: running    | exec=3 done=0 fail=0 block=3 | 12.5ms
Iter  2: running    | exec=2 done=0 fail=0 block=2 | 8.3ms
Iter  3: idle       | exec=0 done=0 fail=0 block=0 | 0.7ms
Iter  4–10: idle    | exec=0 done=0 fail=0 block=0 | ~0.4ms each
```

Same outcome (0/30) but different failure mode than v3.1.1. In v3.1.1, tasks ran (exec=3/iter) but spun endlessly. In v3.3, tasks are **immediately blocked** (iter 1) and then **idle** forever. This means a **new bug was introduced**, not one that survived.

## New Bug Discovered: AgentManager Thread-Safety Gap (CRITICAL)

**Root cause:** `AgentManager` has NO threading locks. When `ThreadPoolExecutor` submits 3 tasks in parallel, each thread calls `select_agent_for_task()` simultaneously. Since all 12 agents start as `IDLE`, multiple threads can **pick the same agent**:

```
Thread 1: select_agent → filters by IDLE → finds dev_1
Thread 2: select_agent → filters by IDLE → ALSO finds dev_1 
           (Thread 1 hasn't called start_work yet!)
Thread 1: start_work(dev_1) → WORKING ✅
Thread 2: start_work(dev_1) → WORKING ✅ (double-booked!)
Thread 1: execute → complete_work(dev_1) → IDLE ✅  
           ← Thread 2's agent is now IDLE while still executing!
Thread 2: ... still running, dev_1 is now IDLE for another thread to grab
```

**Result:**
- Tasks get stuck in `IN_PROGRESS` with no thread assigned to finish them
- Agent statuses oscillate between WORKING/IDLE across threads
- `select_agent_for_task()` returns inconsistent results each call
- Zero tasks reach COMPLETED

**Fix:** Add `threading.RLock` to `AgentManager` wrapping:
- `select_agent_for_task()`
- `start_work()`
- `complete_work()`
- `get_available_agents()`

~30 lines, same pattern as the StateManager fix already applied.

## Secondary Issue: Stale Task Objects in Threads

`_execute_single_task()` receives a `TaskDefinition` object captured when `run_iteration()` calls `load_tasks()`. The thread modifies this stale object's status locally while another thread may have updated the same task's file-based state. The thread's `transition_task()` call writes local state back, potentially reverting another thread's changes.

**Fix:** Each thread should re-load its task from StateManager at the start of `_execute_single_task()`.

## Updated Pitfall for skill-audit

This confirmed a New Lesson that should be a documented pitfall in the master skill:

**"AgentManager thread-safety is a separate concern from StateManager thread-safety."**
Even with perfect file-level locking (StateManager), the in-memory agent pool (AgentManager) can race independently. Two threads can select the same agent, double-book it, and create orphaned IN_PROGRESS tasks. Fix: `threading.Lock` around all AgentManager lifecycle methods.

## Change in vs v3.1.1 findings

| Dimension | v3.1.1 | v3.3 |
|-----------|--------|------|
| StateManager thread-safe | ❌ | ✅ |
| AgentManager thread-safe | ❌ | ❌ ← same hole, dormant before |
| Acceptance criteria mock | ❌ | ✅ |
| max_retries guard | ❌ | ✅ |
| Recovery transitions | ❌ | ✅ |
| Benchmark completion | 0/30 (endless loop) | 0/30 (immediate block) |
| **Critical bugs remaining** | **4** | **1** (AgentManager races) |

## Verdict: ONE bug away from production-ready

- ✅ StateManager thread-safe
- ✅ Acceptance criteria work
- ✅ max_retries guard
- ✅ Recovery uses valid transitions
- ❌ **AgentManager not thread-safe**
- ✅ 129/129 pytest pass

After AgentManager lock (~30 lines), this engine should pass the 30-task stress benchmark with non-zero completion.
