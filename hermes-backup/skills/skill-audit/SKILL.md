---
name: skill-audit
description: "Review, audit, and verify Hermes Skill implementations for correctness, Hermes integration quality, code hygiene, and production readiness. Use when a user asks you to review their skill code, check if a skill will work, analyze a skill package for issues, or diagnose why a skill is failing."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, audit, review, quality, hermes-agent]
    related_skills: [hermes-agent-skill-authoring]
---

# Hermes Skill Audit

## Overview

Users build Hermes Skills — sometimes as standalone projects, sometimes as packages they intend to install. A skill audit examines the full package for structural correctness, Hermes integration fidelity, code hygiene, dependency honesty, and production readiness. The audit produces a scored, dimension-by-dimension report the user can act on.

This is **not** a code-style lint pass. It's a **system integrity check**: does this skill actually work with Hermes, or is it a self-contained prototype that merely *mentions* Hermes?

## When to Use

- User uploads or links a skill package and asks "what do you think?" / "review my skill" / "check if this works"
- User reports a skill failing and asks for diagnosis
- User asks "does this skill follow Hermes conventions?"
- User says "I'm building a skill — review my approach before I go further"

## Audit Dimensions

Audit in this order. Each dimension builds on the one before it.

### 1. Package Structure
- Does the skill have a `SKILL.md` at the root?
- Is the frontmatter valid (name, description, version, author, license, metadata)?
- Does `SKILL.md` have been written in the correct location (`~/.hermes/skills/` or the appropriate directory)?
- Are `references/`, `scripts/`, `templates/` directories used appropriately?
- If scripts exist, are they in a proper Python package (with `__init__.py`)?
- Is the directory structure consistent with Hermes conventions?

### 2. Dependency Honesty
- Scan all Python imports across scripts.
- Cross-reference against `INSTALL.md`, `requirements.txt`, or any dependency declarations.
- Flag undeclared dependencies (e.g. using `import yaml` but claiming "uses only Python standard library").
- Check for missing `requirements.txt` / `pyproject.toml` when external packages are used.

### 3. Hermes Integration
This is the most important dimension. A Hermes Skill must *use Hermes tools and primitives*, not just document them.

- **Does the skill use `delegate_task` to spawn subagents?** If it only has Python classes called "Agent" that are never wired to `delegate_task`, the agents are simulated, not real.
- **Does each agent role have a dedicated system prompt AND a restricted toolset?** A role enum without a prompt is a label, not an agent. Each role needs: (a) a system prompt defining its job, (b) a toolset restriction limiting which Hermes tools it can call (e.g. Developer gets `["file", "terminal"]`, Reviewer gets `["file"]` only). Without tool restriction, a Researcher agent could accidentally write files — violating principle of least privilege.
- **Does the skill use `terminal()` to execute commands?** If it only documents shell commands in markdown, it produces instructions, not execution.
- **Does the skill use `write_file` / `read_file` / `patch`?** If it only documents file operations, the automation is aspirational.
- **Does the skill invoke Hermes memory tools (`mnemosyne_remember`, `mnemosyne_recall`)?** If it implements its own YAML-based "memory" instead of using Hermes' built-in provider, that's a portability concern.
- **Are Hermes imports guarded with a fallback?** Production skills should use `try: from hermes_tools import delegate_task; except ImportError: HERMES_AVAILABLE = False` so unit tests can run without a live Hermes runtime.
- **Can the SKILL.md actually be loaded by Hermes?** Check for commands like `hermes run <skill-name>` that don't exist as Hermes CLI commands. Skills are invoked via `/skill-name` in chat or loaded by the agent via `skill_view`.

### 4. Code Hygiene
- **Duplicate definitions**: same class/constant/list defined in multiple files (e.g. agent configurations in both `dispatcher.py` and `agent_manager.py`).
- **Import hygiene**: imports at module level vs inside function bodies (latter is a code smell).
- **Unused imports**: imported symbols never used.
- **Dead code**: unreachable branches, functions that are never called.
- **Inconsistent naming**: same concept called different things in different files (e.g. enum values vs raw strings).

### 5. Execution Readiness
- **Can the scripts actually be imported?** Try importing the package structure mentally — does `from scripts.bootstrap_project import X` work without `__init__.py`?
- **Are there circular dependencies** between classes?
- **Are schemas consistent with code?** YAML schemas should match what the Python code actually reads/writes.
- **Are there hardcoded stub returns** (e.g. `passed=True` in verifier logic that never actually validates)?

### 6. Robustness & Resilience
- **Error handling**: are there try/except blocks, or would an exception crash the whole loop?
- **Checkpoint/recovery**: is state actually persisted to disk and recoverable?
- **Idempotency**: can operations be safely retried?
- **Resource limits**: are there any guards on token consumption, execution time, parallelism?

### 7. Documentation Truthfulness
- Does `INSTALL.md` (or equivalent) match reality?
- Are code examples in markdown files syntactically valid?
- Does the `SKILL.md` description accurately summarize what the skill does?
- Are claimed features actually implemented?

## Audit Report Format

Deliver findings in three severity tiers, ordered from most to least severe:

```
## 📊 Summary

| Dimension | Score | Notes |
|-----------|-------|-------|
| Package Structure | 🟢/🟡/🔴 | ... |
| Dependency Honesty | 🟢/🟡/🔴 | ... |
| Hermes Integration | 🟢/🟡/🔴 | ... |
| Code Hygiene | 🟢/🟡/🔴 | ... |
| Execution Readiness | 🟢/🟡/🔴 | ... |
| Robustness | 🟢/🟡/🔴 | ... |
| Documentation | 🟢/🟡/🔴 | ... |

### 🚨 Critical (blocks use entirely)
1. ...

### ⚠️ Serious (significant rework needed)
1. ...
### 📝 Minor (polish / best practice)
1. ...

```

Then follow with **targeted recommendations**, ordered by impact. Each recommendation should be a concrete action, not general advice.

## Expanded Audit: End-to-End Flow Dimension

Standard dimension checks verify modules independently, but cross-module orchestration bugs are the #1 cause of "123 tests pass yet the skill crashes on first use." Add this dimension explicitly:

### 8. End-to-End Flow Integrity

Trace a complete execution path from entry point through every module call. Do NOT stop at module-level test coverage.

- **Can the entry-point function (`run_project`, `handle_goal`, etc.) be called without error?** Import the module and call `help(entry_point)` — does the signature match what the user-facing docs describe?
- **Are all state transitions in the entry point *valid per the project's own transition table*?** Trace every `transition_project()` / `transition_task()` call in the main flow against the `VALID_PROJECT_TRANSITIONS` / `VALID_TASK_TRANSITIONS` dict. A single missing transitional state (e.g. skipping `SPECIFICATION_READY` before `PLANNING`) crashes the entire pipeline.
- **Are agent pools populated before agents are selected?** An `AgentManager` instantiated without calling `create_default()` (or the equivalent) has zero agents. `select_agent_for_task()` returns `None`, every task blocks with `"no_available_agent"`, and the loop spins until max iterations — producing zero output. **A manager is not a pool.**
- **Is `delegate_task` (or similar Hermes tool) output actually parsed?** Look at the handler that calls `delegate_task()`:
  - Does it just do `str(result)` and discard the structured `TaskResult` fields?
  - Are `files_created`, `files_modified`, `errors` hardcoded to `[]`?
  - Does the return structure match what the *caller* (e.g. verifier or execution loop) expects downstream?
  - **If the output is not parsed, verification has no input — it's running against an empty directory.**
- **Does a mock / testing-mode code path mask real failures?** If `_execute_mock()` returns `{"success": True, "files_created": [], "errors": []}` unconditionally, the execution loop will believe work was done. This sets up a "tested OK, prod broken" surface. Check whether mock mode is guarded by `try/except ImportError` and only triggers in test contexts.
- **Does the execution loop actually execute?** Run one iteration with a minimal project. Does a task move from OPEN → IN_PROGRESS → COMPLETED? Or does it get stuck in BLOCKED? Run `run_until_complete()` with a small `max_iterations` — does it return normally or timeout on a silent loop?

### 9. Stress-Test Benchmark (Long-Running Readiness)

A skill can pass all 7 standard dimensions plus the e2e flow check and still **spin silently for 50 iterations producing zero output** under real workload. Run a **stress-test benchmark** when the skill claims long-running autonomous capability.

The full methodology is in `references/stress-test-benchmark-methodology.md`. Key signals:

- **Phase 1–2**: Build a 30-task complex DAG (5-level dependency chain). Benchmark graph operations (build, sort, critical path, validation, parallel groups) — should all complete in <10ms O(N+E).
- **Phase 1b — Same-Type Starvation Test (MANDATORY)**: Build 5+ tasks of the SAME type at the same DAG level (e.g. 5 RESEARCH tasks with no dependencies). Run execution loop. **Pass = all 5 complete within 10 iterations. Fail = stalls at N/5 with the rest BLOCKED forever.** A linear-chain DAG is NOT sufficient — real projects always have same-type clusters.
- **Phase 3**: Run 10 iterations of the execution loop. Track `executed/completed/failed/blocked` per iteration. If `completed=0` for 10 iterations, the loop is spinning on a bug. If iteration time grows monotonically, there's a leak.
- **Phase 4–5**: Inspect final state (project state, task statuses, checkpoints, agent statuses). Compute throughput (tasks/s, avg iter time).
- **Phase 6**: Recovery edge cases (retry, max retries, rollback, cycles, self-loops, empty/single graphs).
- **Phase 7**: Scale up (30 → 200 → 1000 nodes) to verify O(N+E) stays linear.

**Pass = no crashes, >0 tasks completed, flat iteration-time trend, recovery passes, agent lifecycle cycles correctly.**

### 10. Real Code Generation (Final Validation)

**Internal benchmarks with mock execution are NOT sufficient.** A skill that claims to "build projects" or "generate code" must be tested by actually generating code. This catches bugs that mock execution masks entirely.

**Progressive validation ladder:**
1. **Internal tests** (pytest) — verify module correctness in isolation
2. **Stress benchmarks** (30→47→50 task DAGs) — verify execution loop under load
3. **Real project generation** — spawn actual subagents via `delegate_task()` to write real code, then verify the output runs

**Step 3 methodology:**
- Design a real project (e.g. e-commerce site, game, API)
- Break it into tasks that map to the skill's task types
- Use `delegate_task()` to have subagents write actual files
- Verify: files exist? Code runs? API responds? Tests pass?
- **This is the only test that catches auth bugs, import errors, and integration issues** that mock execution hides

**Red flag:** If a skill's tests all pass but it has never been used to generate real output, it is untested. Internal benchmarks prove the engine runs; real generation proves it produces value.

**User signal:** When a user says "I don't see any results" or "you didn't actually build anything" after you ran benchmarks, they are pointing at this gap. Respond by spawning real subagents immediately — do not defend the benchmarks.

### Pitfall 0: The Deceptive-Linear-DAG Trap (Same-Type Parallel Starvation)

**This is the most dangerous bug pattern in autonomous execution engines because it passes simple tests and fails on real projects.**

A linear DAG like `T0→T5→T10→T20→T25` naturally distributes task types across iterations — each iteration's ready tasks tend to be different types (research, design, implementation, etc.), each with its own dedicated agent. No two tasks compete for the same agent. The engine appears flawless.

But a **real project** often has 5+ RESEARCH tasks at the same DAG level. All become ready simultaneously. With only 1 researcher agent, only 1 gets the agent; the other 4 are marked BLOCKED — and if the loop never retries BLOCKED tasks, the engine stalls permanently at `completed/(completed+blocked)`.

**Detection test (must be run deliberately):**
```python
# 5 research tasks, 1 researcher agent, max_parallel=5
for i in range(5):
    sm.add_task(TaskDefinition(id=f'R{i}', ..., type=TaskType.RESEARCH, ...))
loop = ExecutionLoop(sm, ExecutionConfig(max_parallel_tasks=5))
loop.agent_manager = AgentManager.create_default(sm)
for it in range(10):
    r = loop.run_iteration()
    # If completed=0 after the first iteration where all tasks are
    # RESEARCH type, the engine is stuck — BLOCKED tasks never retried.
```

**Pass = all 5 complete within 6 iterations.**
**Fail = stalls at N/5 with the rest BLOCKED forever.**

This test **must** be run in addition to any linear-scenario DAG (30-task chain, etc.). A linear chain can trick you into believing the engine is production-ready when it has a fatal starvation bug.

**Root cause chain when this fails:**
1. `select_agent_for_task()` returns `None` for 4/5 tasks (only 1 researcher agent exists)
2. `_execute_single_task()` marks the 4 tasks `BLOCKED` via `update_task(status=BLOCKED)`
3. `get_ready_tasks()` queries `node.task.status != OPEN → continue` → BLOCKED tasks invisible
4. Engine goes idle, iterations spin until max_iterations, zero additional progress

**Two-line fix:**
- `get_ready_tasks()` must also return BLOCKED tasks: `if node.task.status not in (OPEN, BLOCKED): continue`
- `_execute_single_task()` should NOT persist BLOCKED status (let the task stay OPEN, just skip it this iteration)

## Common Pitfalls

1. **Treating agent `.md` files as real agents.** Files like `agents/developer_agent.md` that describe what an agent *would* do are documentation, not implementation. Real skill agents use `delegate_task` to spawn Hermes subagents.

2. **Duplicating agent configuration.** Defining the same list of agents (with IDs, types, capabilities) in multiple Python files guarantees they'll drift apart. Keep one source of truth.

3. **Declaring "pure stdlib" while importing `yaml`.** `pyyaml` is an external package. Honesty in dependency declarations prevents activation failures.

4. **Writing `SKILL.md` commands that don't exist.** `hermes run <skill>` is not a Hermes CLI command. Skills are loaded via `/skill-name` chat invocation or `skill_view`. Documenting nonexistent commands erodes trust.

5. **Building standalone automation that ignores Hermes tooling.** A skill that only has Python file I/O and never calls `delegate_task`, `terminal()`, or `write_file` is a standalone Python project, not a Hermes Skill.

6. **Hardcoding verification pass.** `passed=True` in a verifier without actual checks means the skill will declare success for any input. Every verification method must do real work.

7. **Missing `__init__.py` in script directories.** Python will not discover packages without it. Cross-file imports fail silently at runtime.

8. **Defining competing state machines.** Having `ProjectPhase` enum in one file and raw string phase names in another guarantees inconsistency.

9. **Assuming `AgentManager` is populated.** Creating a manager and expecting it to have agents is a classic gap. Check whether `create_default()` is called in the entry point flow. It's the most common single-line missing fix.

10. **Calling `@classmethod` factory on an existing instance instead of assigning the return.** A `@classmethod` factory like `AgentManager.create_default(state)` returns a **new, fully populated** instance. Writing `manager = AgentManager(state); manager.create_default()` calls the classmethod on the instance but discards the returned populated manager — the original empty manager is untouched. The correct form is `manager = AgentManager.create_default(state)` — one call, one assignment. Always verify: does this factory return a new instance or mutate in-place?

11. **Freshly-created agent pool has status=CREATED but selection logic expects IDLE.** A default agent factory typically creates agents with `CREATED` status. Selection algorithms (like `select_agent_for_task()`) filter by `status == IDLE`. Every agent gets skipped, tasks block with `"no_available_agent"`, and the execution loop spins silently until max iterations. After `create_default()`, either call `initialize_agent()` on each agent or modify the factory to set initial status to `IDLE` directly.

12. **Leaving `delegate_task` output unparsed.** Calling `delegate_task()` then returning `str(result)` with hardcoded empty lists for `files_created`/`errors` means downstream verification runs blind. The caller needs the structured output, not a repr string.

13. **Tracing only module-level test coverage.** 123 passing unit tests + a crashing entry point = not production ready. The integration test (`run_project()` with real parameters) catches cross-module bugs no unit test finds. Always trace the end-to-end execution path.

15. **Mock executor acceptance-criteria trap.** `_execute_mock()` returning hardcoded `success=True` with empty results creates a false-positive loop when the verifier checks acceptance criteria against the mock output. The criteria keywords never appear in mock output → verification always fails → recovery resets task → endless loop with zero completion. Mock mode should either include criteria keywords or skip acceptance checks entirely when Hermes is unavailable.

16. **Parallel execution + file-backed state = race condition.** `ThreadPoolExecutor` running N tasks simultaneously on a shared `tasks.json` file means each thread reads N tasks, modifies 1, and writes N tasks back. Thread A's write overwrites Thread B's changes. The result is oscillating statuses and zero tasks reaching COMPLETED. StateManager must have `threading.Lock` around every read-modify-write operation (transition_task, add_task, update_task, save_tasks, load_tasks) when the execution loop supports parallelism.

17. **AgentManager is also not thread-safe — the pool races separately from file state.** Two threads calling `select_agent_for_task()` simultaneously can **pick the same agent** because the first thread hasn't reached `start_work()` yet to transition the agent's status from IDLE to WORKING. Timeline:
    ```
    Thread 1: select_agent_for_task() → filters by IDLE → finds dev_1
    Thread 2: select_agent_for_task() → filters by IDLE → ALSO finds dev_1 (Thread 1 hasn't called start_work yet!)
    Thread 1: start_work(dev_1) → WORKING ✅
    Thread 2: start_work(dev_1) → WORKING ✅ (same agent, double-booked!)
    Thread 1: execute → complete_work(dev_1) → IDLE ✅  ← Thread 2's work not done yet!
    Thread 2: ... still running but dev_1 is now IDLE (another thread can grab it)
    ```
    This pattern causes tasks stuck IN_PROGRESS with no thread owning them, agent statuses oscillating between WORKING/IDLE across threads, and zero tasks reaching COMPLETED in parallel mode.
    
    **Fix (two-level):** 
    **Level 1 (minimal):** add `threading.RLock` to AgentManager wrapping `select_agent_for_task()`, `start_work()`, `complete_work()`, and `get_available_agents()` — exactly like the StateManager lock pattern. This prevents two threads from being inside select_agent_for_task at the same time, but still allows Thread 1 to release the lock after finding dev_1 but before Thread 2 calls select_agent_for_task, finds dev_1 still IDLE, and grabs it.
    
    **Level 2 (proper — atomic select+reserve):** merge `select_agent_for_task()` and `start_work()` into a single atomic operation. After finding the best IDLE agent under the lock, immediately mark it WORKING (set `status = AgentState.WORKING`, `current_task = task.id`, and call `_save_agents()`) before releasing the lock. The agent is reserved before any other thread can see it. This eliminates the gap entirely. The caller then skips the separate `start_work()` call. Verification: assert that `select_agent_for_task()` already set `agent.status == WORKING` on return.
    
    **Sanity test:** 5 threads each calling `select_agent_for_task(RESEARCH)` against a pool with 1 researcher agent + 11 other agents (fallback to DEVELOPER). With Level-1 fix, the 4 loser threads still collide on the researcher agent as it cycles IDLE→WORKING→IDLE across threads. With Level-2 fix, 1 thread reserves the researcher, the other 4 get different developers (or None if only researchers are suitable), and no two threads share an agent at any moment.

18. **BLOCKED tasks never retried (Same-Type Starvation).** Multiple tasks of the same type that become ready simultaneously compete for a single agent (1 agent per role). The losers get marked `BLOCKED` via `update_task(status=BLOCKED)`. But `get_ready_tasks()` only returns tasks with `status == OPEN` — BLOCKED tasks are invisible. The engine stalls permanently at `N_completed/(total_tasks)` with the rest stuck BLOCKED. Passes 30-task linear DAG tests; fails 47-task real-world projects. **Fix:** (a) `get_ready_tasks()` must also return BLOCKED tasks: `if node.task.status not in (OPEN, BLOCKED): continue`. (b) `_execute_single_task()` must NOT persist BLOCKED status — just skip the task and leave it OPEN for retry.

19. **Agent selection after IN_PROGRESS transition causes stuck tasks.** Calling `transition_task(task.id, TaskStatus.IN_PROGRESS)` *before* `select_agent_for_task()` means that when no agent is found, the task is left in `IN_PROGRESS` — and `IN_PROGRESS` is not a status that `get_ready_tasks()` returns. The task stays stuck forever. **Fix:** swap the order: select the agent FIRST, then transition to IN_PROGRESS only when an agent is available. If no agent, return early — the task remains OPEN for the next iteration.

## Verification Checklist

- [ ] All Python imports identified and cross-referenced against dependency declarations
- [ ] Each agent implementation checked for real `delegate_task` usage (vs. just documentation)
- [ ] Every claim in `SKILL.md` and `INSTALL.md` verified against actual code
- [ ] No duplicate class/constant/agent-list definitions across files
- [ ] `__init__.py` present in every directory that needs to be a Python package
- [ ] Verifier/validator functions do real checks, not hardcoded `passed=True`
- [ ] Any `hermes run ...` or similar CLI commands in documentation confirmed to exist
- [ ] Entry-point function called end-to-end: `transition_project()` chain is valid against the project's own transition table
- [ ] Agent pool is populated before selection: `AgentManager.create_default()` or equivalent is called in the flow
- [ ] `delegate_task()` output is parsed, not discarded: `files_created`, `files_modified`, and `errors` are extracted from the result object
- [ ] Mock/testing-only code paths don't mask real failures: mock returns are distinguishable from real returns
- [ ] Report delivered in structured tiers (Critical → Serious → Minor) with concrete next steps

## Related References

- `references/iterative-skill-remediation.md` — full workflow for fixing multi-flaw skills via audit → mega-prompt → regenerate → re-audit cycle
- `references/example-autonomous-project-engine-audit.md` — full 8-step penetration test of a complete codebase (v3), covering state-transition bugs, agent-spawning gaps, unparsed delegate_task output, and the distinction between "123 passing tests" and "production-ready integration".
- `references/example-autonomous-project-engine-v3dot1-audit.md` — re-audit of v3.1 after fixes were applied, including a 9th discovered bug (`@classmethod` factory return discarded, agent CREATED vs IDLE status mismatch), lessons learned on factory-method assignment patterns.
- `references/example-autonomous-project-engine-v3dot3-audit.md` — stress-test re-audit of v3.3 after all 5 critical bugs were fixed, discovering the **AgentManager thread-safety gap** as a separate concern from StateManager thread-safety — even with perfect file-level locking, the in-memory agent pool can double-book agents under `ThreadPoolExecutor`.
- `references/example-autonomous-project-engine-v3dot5-audit.md` — final v3.5 audit: 2 critical bugs found and fixed (BLOCKED-never-retried + IN_PROGRESS ordering), plus Level-2 atomic select+reserve for AgentManager race. Documents the **Linear-DAG Trap** where a 30-task chain passes but a 47-task real-project DAG stalls at 11%, and the mandatory same-type starvation test that catches it.
- `references/stress-test-benchmark-methodology.md` — 7-phase stress-test benchmark for long-running autonomous skills: 30-task DAG, 10+ execution iterations, performance metrics, recovery edge cases, and scale-up testing (30→200→1000 nodes) to verify O(N+E) scaling and detect silent-loop bugs.
