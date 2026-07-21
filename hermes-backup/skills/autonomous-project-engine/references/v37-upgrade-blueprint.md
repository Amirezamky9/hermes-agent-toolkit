# v3.7 Upgrade Blueprint — SchemaContract + Sequential Strategy + Rate-Limit Resilience

## Why v3.7 Exists

v3.6's field test (coffee e-commerce with 3 parallel subagents) revealed 7 integration bugs caused by subagents independently deciding schema details. v3.7 adds three things:

1. **SchemaContract** — shared architectural decisions LOCKED before parallel dispatch
2. **Sequential Strategy** — dispatch tasks one-at-a-time per wave instead of parallel (corrected from v3.7's original ModelRouter approach, which didn't work because delegate_task() ignores model selection)
3. **Phase Validation** — contract compliance check after every wave

## Correction: ModelRouter is Dead; Sequential is the Answer

**Original v3.7 assumption:** `ModelRouter` could assign different models to parallel subagents to avoid rate limits.

**Reality:** `delegate_task()` does NOT accept a model parameter. The Hermes platform controls the model via `delegation.model` in config.yaml — the engine has no control over which model a subagent uses.

**To change the delegation model:**
```bash
/app/venv/bin/hermes config set delegation.model "opencode200k"
# Or any model name available in your provider
```

**Replacement strategy:** Sequential execution per wave. Disadvantage: slower (N subagents = N × wall clock). Advantage: each subagent reads previous outputs, eliminating integration bugs entirely.

```python
# ✅ CORRECTED v3.7.1 approach:
phase_tasks = [research, backend, seed, frontend]  # ordered
for task in phase_tasks:
    result = delegate_task(goal=task.goal, context=context)
    # Next task can read this task's outputs
```

## SchemaContract API

```python
cm = ContextManager(project_dir)
cm.decide_pk_type("int")
cm.decide_auth_method("jwt")
cm.decide_framework("fastapi", "react")
cm.decide_api_prefix("/api")
cm.schema.lock()

task_context = cm.to_task_context()

violations = cm.validate_contract()
```

## Rate Limit Resilience

```python
import re, time
from datetime import datetime, timezone

def execute_with_retry(prompt, context, max_retries=3):
    for attempt in range(max_retries):
        try:
            return delegate_task(goal=prompt, context=context)
        except Exception as e:
            if "rate limited" not in str(e).lower():
                raise
            match = re.search(r"until (\S+)", str(e))
            if match:
                wait = (datetime.fromisoformat(match.group(1)) - datetime.now(timezone.utc)).total_seconds() + 5
                if wait > 0:
                    time.sleep(wait)
                    continue
    raise Exception(f"Rate limited after {max_retries} retries")
```

## CRTICAL: Never Do Manual Work for the Engine

When a subagent fails (rate limit, error, stuck):
1. **Parse the error**: if rate limited, extract the `until` timestamp
2. **Wait**: sleep(wait_seconds + 5)
3. **Retry**: same prompt, same context
4. If retry fails 3 times → dispatch a new subagent with narrowed goal
5. **NEVER** write the code yourself — the engine builds, you orchestrate

This was the #1 workflow mistake discovered in v3.7 field testing, and it received the strongest user correction in the entire session history.

## Test Suite

```bash
cd skills/autonomous-project-engine
python3 -m pytest tests/ -v  # 186 passed in 0.21s
```
