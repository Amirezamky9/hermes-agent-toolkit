# Example Audit: autonomous-project-engine v3.1

A complete penetration test of a third-party Hermes Skill built via Mimo CLI. The skill claims to be a "Hermes-native autonomous project execution engine" — this audit checked whether that claim holds.

## Background

- **Project**: `autonomous-project-engine` — a Hermes Skill that turns Hermes into a long-running project execution system
- **History**: v1 (prototype with bugs) → v2 (fixed core engine, 105 tests) → v3 (added agent prompts + orchestration + mnemosyne, 123 tests) → v3.1 (fixed 6/8 critical gaps found in v3 audit)
- **Method**: 8-step integration test + 129 pytest tests + 9-step integration suite + full end-to-end flow trace
- **Auditors**: Main Hermes agent (direct analysis) + subagent auditor (dispatched for parallel penetration test)

## Key Gaps Discovered (in v3)

| # | Gap | Severity | Root Cause |
|---|-----|----------|-----------|
| 1 | `run_project()` crashed on invalid state transition | 🔴 Critical | `SPECIFICATION_READY` state omitted from transition chain |
| 2 | No agents created in production path | 🔴 Critical | `AgentManager.create_default()` never called in `run_project()` |
| 3 | `delegate_task()` output discarded | 🔴 Critical | `files_created=[], errors=[]` hardcoded, result just `str()`ed |
| 4 | Sequential execution despite `max_parallel_tasks` config | 🔴 Critical | `for` loop instead of `ThreadPoolExecutor` |
| 5 | File-based StateManager used instead of Mnemosyne | 🔴 Critical | `HermesStateManager` existed but was never imported in `__init__.py` |
| 6 | Absolute import in `agent_prompts.py` | 🟡 Medium | `from core.schema` instead of `from .schema` |
| 7 | No delegation depth limit | 🟡 Medium | PM/Reflection agents had `["delegation"]` toolset but no recursion guard |
| 8 | `project_dir` property missing from `HermesStateManager` | 🟡 Medium | `ExecutionLoop._build_context` used `self.state.project_dir` |

## v3.1 Fixes Applied

All 8 gaps fixed by Mimo v3.1:

- ✅ State transition chain fixed (`CREATED → ANALYZING → SPECIFICATION_READY → PLANNING → EXECUTING`)
- ✅ Agent auto-creation added (`loop.agent_manager.create_default()`)
- ✅ `delegate_task()` output parsed with `hasattr()` checks + regex fallback
- ✅ `ThreadPoolExecutor` with `as_completed()` for parallel execution
- ✅ `HybridStateManager` (tries Mnemosyne, falls back to files) used in `run_project()`
- ✅ `from .schema import AgentRole` (relative import)
- ✅ `max_depth=3` guard in `AgentOrchestrator.execute_task()`
- ✅ `project_dir` property added to `HermesStateManager`

## Remaining Bug in v3.1

A **9th gap** was discovered during the re-audit:

```
loop.agent_manager = AgentManager(state)       # ← empty manager
loop.agent_manager.create_default()             # ← classmethod returns new manager, DISCARDED!
```

`AgentManager.create_default()` is a `@classmethod` that returns a new populated instance. The code calls it on the existing empty manager instance and discards the return. Fix:
```
loop.agent_manager = AgentManager.create_default(state)
```

Additionally, `create_default()` sets agents to `status=CREATED` but `select_agent_for_task()` filters by `status == IDLE`. So even if correctly assigned, no agent matches. Need to call `initialize_agent()` on each after creation.

## Stress Test Results (v3.1.1)

A 7-phase stress benchmark was executed on the v3.1 codebase after the 9th gap was fixed:

```text
📦 PHASE 1: 30-task complex DAG → ✅ Created 30 tasks, 5-level deps
📊 PHASE 2: Graph operations → ✅ Build 0.43ms, Topo 0.01ms, CP 0.03ms
⚡ PHASE 3: 10 iterations → ⚠️ 0/30 completed (details below)
🔍 PHASE 4: Final state → 0 done, 2 failed, 25 open, 3 in-progress
📈 PHASE 5: Performance → 84ms total, 8.38ms avg/iter
🔄 PHASE 6: Recovery → ✅ Retry, rollback, edge cases OK
🧪 PHASE 7: Edge cases → ✅ Cycle, self-loop, empty, single node
```

### 4 New Bugs from Stress Test

| # | Bug | Root Cause | Severity |
|---|-----|-----------|----------|
| 1 | **Mock → acceptance criteria loop** 🔴 | `_execute_mock()` returns empty result without acceptance criteria keywords → verifier always fails → task spins endlessly | HIGH |
| 2 | **Parallel race condition** 🔴 | `ThreadPoolExecutor` threads read/write shared `tasks.json` without locking → state corruption across threads | CRITICAL |
| 3 | **Recovery bypasses transition validation** 🟡 | `recover_from_failure()` uses `update_task()` (raw setattr) which circumvents `transition_task()` validation | HIGH |
| 4 | **StateManager not thread-safe** 🟡 | No `threading.Lock` on `load_tasks()`/`save_tasks()`/`transition_task()` — all operations are race-prone | HIGH |

### Root Cause Analysis

**Bug 1 — Mock/Acceptance Criteria Loop:**
`_execute_mock()` returns `{"summary": "Mock execution completed...", "files_created": [], "errors": []}`. The verifier's `_verify_acceptance_criteria()` checks if `str(result)` contains the keywords from `task.acceptance_criteria`. Since "Mock execution completed..." contains none of the criteria keywords (e.g. "Criterion 0"), the check always fails → recovery resets the task to OPEN → next iteration picks it up → mock runs → verification fails → endless loop. Tasks never reach COMPLETED.

**Bug 2 — Parallel State Corruption:**
`ThreadPoolExecutor` (max_workers=3) runs `_execute_single_task()` concurrently. Each thread: (a) reads all tasks from `tasks.json`, (b) modifies one task's status, (c) writes ALL tasks back. Thread A writes T0=OPEN, T1=IN_PROGRESS, T2=OPEN. Thread B writes T0=IN_PROGRESS, T1=COMPLETED, T2=OPEN. If Thread A's write finishes after Thread B's, T1 reverts from COMPLETED to IN_PROGRESS. Over 10 iterations, tasks oscillate and zero reach COMPLETED.

**Bug 3 — Recovery bypasses validation:**
`recover_from_failure()` calls `update_task()` which does `setattr(task, 'status', new_status)` directly, bypassing `transition_task()`. This means `IN_PROGRESS → OPEN` succeeds (it's invalid per the state machine). With no transition validation, the state machine's integrity is broken.

**Bug 4 — No thread safety:**
`StateManager.load_tasks()`, `save_tasks()`, `transition_task()`, `add_task()`, and `update_task()` all operate on shared state without any `threading.Lock`. Every operation is a read-modify-write race condition when called from multiple threads.

### Verdict: Production Readiness for Multi-Hour Projects

**❌ NOT READY.** Despite 129 passing unit tests and 8 passing integration tests, the stress benchmark reveals 4 critical bugs that prevent the engine from completing a single task under realistic load:

| Criterion | Result |
|-----------|--------|
| Core engine (Schema, Graph, State) | ✅ 9/10 |
| DAG operations | ✅ 10/10 |
| Execution loop | ❌ 2/10 (race + endless loop) |
| Recovery | 🟡 5/10 (works but bypasses validation) |
| Thread safety | ❌ 1/10 |
| Verifier | 🟡 6/10 (acceptance criteria broken in mock) |
| **Total** | **❌ 4.5/10** |

| Required Fix | Lines of Code |
|--------------|---------------|
| `threading.Lock` in StateManager | ~30 |
| Fix mock acceptance criteria mismatch | ~5 |
| Fix recovery to use valid transitions | ~15 |
| Disable parallel for file-backed state | ~5 |
| **Total** | **~55 lines** |

## Lessons Learned (v3.1 stress test)

1. **Mock mode creates false-positive loops.** `_execute_mock()` returning `{"success": True}` makes the execution loop believe real work was done. When the verifier then checks acceptance criteria against mock output, no keywords match → verification fails → recovery → retry → infinite loop. Fix: mock mode should either include acceptance criteria text in results, or skip acceptance checks when `HERMES_AVAILABLE == False`.

2. **File-backed state + parallel execution = data corruption.** A `StateManager` storing all tasks in a single JSON file cannot safely serve parallel threads without locks. Each thread's read-modify-write cycle is a race condition. Fix: `threading.Lock` around every state operation.

3. **Recovery must respect the state machine.** `recover_from_failure()` bypassing `transition_task()` via raw `setattr` breaks the state machine contract. `IN_PROGRESS → OPEN` is never valid. Fix: recovery should transition through valid paths like `IN_PROGRESS → FAILED → OPEN`.

4. **"Works in test" ≠ "works under load."** 123/123 unit tests pass. 129 passing after fixes. The 8-step e2e flow passes. Yet the 7-phase stress benchmark reveals 4 critical bugs only visible under realistic load (30 tasks, parallel execution, 10+ iterations). Always run a stress benchmark before signing off on production readiness.

## Methodology

### 8-Step Integration Test

1. **Package Import Test**: Verify all modules import without circular dependency errors
2. **Entry Point Test**: Call `run_project("Build a test API")` — does it crash?
3. **State Transitions Test**: Trace the full `transition_project()` chain against `VALID_PROJECT_TRANSITIONS` table
4. **Agent Auto-Creation Test**: Verify `create_default()` populates all 12 agent roles with proper status
5. **Execution Loop Test**: Run one iteration with a populated agent pool — do tasks move from OPEN → IN_PROGRESS?
6. **Parallel Execution Test**: Verify `ThreadPoolExecutor` is used and `max_parallel_tasks` config is respected
7. **HybridStateManager Test**: Create project via `HybridStateManager`, save/load state
8. **Prompt Import Test**: Import `get_prompt()` from a different working directory to verify relative import works

### Subagent Auditor

Dispatched a real Hermes subagent with `delegate_task()` to independently run the same test suite. The subagent found the state-transition crash independently (confirmed finding).

## Lessons Learned

1. **`@classmethod` factories are not mutators.** Always verify whether `create_default()` (or equivalent) returns a new instance or mutates in-place. Most factories return — assign, don't chain.
2. **Every transition must be traced against the project's OWN transition table.** A single missing state (`SPECIFICATION_READY`) crashes an otherwise-working pipeline.
3. **Agent pools have a lifecycle too.** `CREATED ≠ IDLE`. A `create_default()` that sets status=CREATED is half the work — the other half is a loop calling `initialize_agent()`.
4. **Mock mode is a liability, not a feature.** `_execute_mock()` returning `{"success": True, ...}` makes the execution loop believe work was done. 123 passing tests + a crashing entry point = not production ready.
5. **Cross-module bugs are invisible to unit tests.** The 123 unit tests all pass, but the cross-module state-transition bug crashes on first use. Always run an integration test with `run_project()`.
