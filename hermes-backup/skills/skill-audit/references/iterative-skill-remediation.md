# Iterative Skill Remediation (Audit → Mega-Prompt → Regenerate → Re-Audit)

When a skill has multiple structural flaws that amount to a ground-up rewrite, it's often more productive to write a **mega-prompt** for an external code generator (Mimo CLI, Cursor, etc.) than to patch each file individually. This pattern was developed over three versions of the `autonomous-project-engine` skill.

## The Workflow

```
v1 (upload) → Audit → v1→v2 Mega-Prompt → Mimo generates v2 → v2 Audit
                                                      │
                                                      ▼
                                           v2→v3 Mega-Prompt → Mimo generates v3 → v3 Audit
```

### Phase 1: Deep Audit
Run a full skill-audit (all 7 dimensions). Capture findings in a structured table or severity-tier report. Key questions:
- What is **broken** (won't import/run)?
- What is **fake** (hardcoded `passed=True`, stub returns, paper agents)?
- What is **missing** (no `__init__.py`, no requirements.txt, no Hermes integration)?
- What is **dishonest** (claims "pure stdlib" but imports yaml)?

### Phase 2: Mega-Prompt Construction
Write a single comprehensive prompt for the code generator. Structure:

1. **Context** — what they're receiving (the current codebase state)
2. ✅ **What's already good** — don't let them break working things
3. ❌ **Critical gaps** — numbered, concrete, with code snippets from the audit
4. 🏗️ **Architecture vision** — diagram + file listing of the target state
5. ✅ **Requirements** — per-file: what to create, what to modify, what to delete
6. 🧪 **Test requirements** — existing tests must still pass; new tests must be added
7. ⚠️ **Critical constraints** — non-negotiables (e.g. "stdlib only", "never use the `memory` tool")

### Phase 3: Extract and Test
- Extract the generated archive
- `pip install -r requirements.txt` (or confirm stdlib-only)
- `python -m pytest tests/ -v --tb=short`
- Confirm test count matches expected (old + new)

### Phase 4: Re-Audit
Run the same audit against the output. Score changes:

| Previous Flaw | v2 Status | v3 Status |
|-------------|-----------|-----------|
| No `__init__.py` | ✅ Fixed | ✅ Retained |
| Verifier always PASS | ✅ Fixed (AST) | ✅ Retained |
| O(2^N) critical path | ✅ Fixed (O(N+E)) | ✅ Retained |
| No Hermes tools | ❌ Still missing | ✅ Fixed (delegate_task wrapper) |

### Phase 5: Iterate or Finalize
- If all criticals are resolved → ship
- If some remain → write v2→v3 mega-prompt narrowing the scope
- Common pattern: v1→v2 fixes code hygiene, v2→v3 adds Hermes integration

## Mega-Prompt Template

### Must Include

```
# 🚀 MEGA PROMPT: Build v<N> — <TITLE>

## Context

You are given the **v<N-1> codebase** at `<path>`. This is a ... skill.

**v<N-1> status:**
- ✅ Good thing 1
- ✅ Good thing 2
- ❌ Gap 1
- ❌ Gap 2

## Architectural Vision

ASCII diagram of target architecture

## Requirements

### Files to CREATE
| File | Purpose |
|------|---------|
| `path/to/file.py` | What it does |

### Files to MODIFY
| File | Change |
|------|--------|
| `path/to/file.py` | What to add/change |

### Files to DELETE
- `path/to/stale.py`

## Critical Constraints

1. **DO NOT break existing tests** — all must still pass
2. **Core uses only Python stdlib**
3. **Hermes tools** guarded with `try/except ImportError`
4. **etc.**
```

### Tone
- English (most code generators perform best with English prompts)
- Imperative: "Create", "Add", "Replace", "Delete"
- Specific: exact class/method/import names, not vague descriptions
- Test-aware: say "add 8 new tests for file X" or "all 105 existing tests must pass"

## Pitfalls

1. **Expecting one-shot perfection.** Plan for 2-3 iterations. v1→v2 fixes internal consistency; v2→v3 adds Hermes integration.
2. **Not pinning the test count.** Mimo may drop tests. Run `pytest --collect-only | grep collected` before and after to compare.
3. **Soft constraints get ignored.** "Prefer stdlib" means Mimo will add pyyaml. Say "ONLY Python stdlib — no external packages" to enforce it.
4. **Forgetting `archive/`.** Mimo loves to delete old code. Tell it to move, not delete, the previous version's files into `archive/`.
5. **Not testing the archive extraction.** RAR5 needs `unrar-nonfree`. ZIP is more portable. Request ZIP output if the generator supports it.
