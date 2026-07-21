# v3.4 Bug Discovery & Fix Log

All bugs discovered through stress-testing the autonomous-project-engine (30-task, 47-task, 50-task benchmarks).

## Bug 1: create_default() — Agents Not IDLE

**Discovered**: v3.3 stress test (30 tasks → 0 completed)
**Root cause**: `AgentManager.create_default()` creates agents but doesn't call `initialize_agent()`.
**Status**: FIXED in v3.4
**Fix**: Add `manager.initialize_agent(agent.id)` inside the create_default loop.

```python
# BEFORE (broken)
@classmethod
def create_default(cls, state_manager=None):
    manager = cls(state_manager=state_manager)
    for role in AgentRole:
        agent = manager.create_agent(role)
    return manager  # Agents are CREATED, not IDLE!

# AFTER (fixed)
@classmethod
def create_default(cls, state_manager=None):
    manager = cls(state_manager=state_manager)
    for role in AgentRole:
        agent = manager.create_agent(role)
        manager.initialize_agent(agent.id)  # ← ADD THIS LINE
    return manager
```

## Bug 2: BLOCKED Tasks Never Retried

**Discovered**: v3.4 47-task chess benchmark (only 5/47 completed then stalled)
**Root cause**: `get_ready_tasks()` only returned OPEN status. Once a task became BLOCKED (no agent available), it was invisible forever.
**Status**: FIXED in v3.4+fix
**Fix**: `get_ready_tasks()` checks for both OPEN and BLOCKED.

```python
# BEFORE
if node.task.status != TaskStatus.OPEN:
    continue

# AFTER
if node.task.status not in (TaskStatus.OPEN, TaskStatus.BLOCKED):
    continue
```

## Bug 3: IN_PROGRESS Stuck When No Agent

**Discovered**: v3.4+fix (first attempt) — 5 task benchmark still stalled
**Root cause**: Agent selection happened AFTER `transition_task(IN_PROGRESS)`. When no agent was available, the task was stuck IN_PROGRESS forever.
**Status**: FIXED in v3.4+fix
**Fix**: Select agent FIRST, then transition to IN_PROGRESS only after agent confirmed.

```python
# BEFORE (broken order)
self.state.transition_task(task.id, TaskStatus.IN_PROGRESS)
agent = self.agent_manager.select_agent_for_task(task)  # Too late!

# AFTER (correct order)
agent = self.agent_manager.select_agent_for_task(task)  # First!
if agent is None:
    return AgentExecution(blocked=True)  # Task stays OPEN
self.state.transition_task(task.id, TaskStatus.IN_PROGRESS)  # Then transition
self.agent_manager.start_work(agent.id, task.id)
```

## Bug 4: AgentManager Race Condition

**Discovered**: v3.4 stress test — 5 threads all got the same agent
**Root cause**: `select_agent_for_task()` (under lock) and `start_work()` (separate lock call) released the lock between them, letting another thread claim the same agent.
**Status**: FIXED in v3.4+fix
**Fix**: Make `select_agent_for_task()` atomically set agent to WORKING under the same lock.

```python
def select_agent_for_task(self, task):
    with self._lock:
        available = [a for a in self._agents.values() if a.status == AgentState.IDLE]
        if not available:
            return None
        agent = max(available, key=lambda a: self._score_agent_for_task(a, task))
        # Atomically reserve the agent
        agent.status = AgentState.WORKING
        agent.current_task_id = task.id
        return agent
```

## Bug 5: JWT Subject Must Be String

**Discovered**: E-commerce API testing — all authenticated endpoints returned 401
**Root cause**: python-jose requires `sub` claim to be a string, but code passed `user.id` (integer).
**Status**: FIXED
**Fix**: Cast to string on create, cast back to int on decode.

```python
# auth_router.py — create token
token = create_access_token(data={"sub": str(user.id)})  # str() added

# auth.py — decode token
user_id: int = int(payload.get("sub"))  # int() added
```

## How to Reproduce

```bash
# Backend API test (v3.4)
cd /path/to/ecommerce/backend
python seed.py
python -m uvicorn main:app --port 8000 &
curl -X POST localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Stress Test Patterns

### 30-task Simple DAG (passes even with bugs)
```
T0 → T5 → T10 → T15 → T20 → T25
T1 → T6 → T11 → T16 → T21 → T26
T2 → T7 → T12 → T17 → T22 → T27
T3 → T8 → T13 → T18 → T23 → T28
T4 → T9 → T14 → T19 → T24 → T29
```
Each iteration only has 1 task per type → no agent contention.

### 47-task Complex DAG (exposes bugs)
```
R1───D1───E1───B1───F1───T1───RV1───DEP1
R2───D2───E2───B2───F2───T2───RV2───DEP2
R3───D3───E3───B3───F3───T3───RV3───DEP3
R4───D4───E4───B4───F4───T4───RV4───DEP4
R5───D5───E5───B5───F5───T5───RV5───DEP5
```
First iteration: 5 RESEARCH tasks all compete for 1 researcher agent.
If any bug exists, 4 tasks get BLOCKED and engine stalls.

### 50-task E-commerce (v3.4+fix: 50/50 passes)
```
Full e-commerce stack: research → design → backend → frontend → test → review → deploy
8 task types, 6 phases, 50 tasks total
```
