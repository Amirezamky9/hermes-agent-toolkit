# v3.6 Upgrade: Production-Ready Hermes-Native Engine

## CRITICAL CORRECTION: Dynamic Skill Discovery (NOT Hardcoded)

**The single most important architectural lesson from v3.5 testing:**
SKILL_MAP must NOT be hardcoded. Use `SkillDiscoverer` (tag/keyword matching at runtime) instead of `{FRONTEND_DEV: ["realtime-web-apps"]}`.

Why:
- New skills installed tomorrow are automatically discovered
- Skills that rename still match via tags + description keywords
- Works standalone (offline DEFAULT_SKILL_INDEX) AND in Hermes (live skills_list())

Do NOT build these (they already exist as Hermes skills):
- `research_engine.py` — use deep-research + web-research + research-manager
- `skill_loader.py` — use skill_view() + skill_manage()
- Custom web scraper — use web-research patterns (DDG HTML, Jina Reader)

## Change Summary

8 module changes + ~35 new tests = 170+ total tests.

## Module Changes

### NEW: core/skill_discoverer.py (~130 lines)
- `DEFAULT_SKILL_INDEX` shipped with engine (8 skills pre-defined)
- `discover_skills()` loads default index + optionally enriches via skills_list()
- `get_skills_for_role(role)` scoring: tag overlap (3x) + keyword in desc (1x) + domain match (2x)
- `get_assignment_table()` — human-readable skill→role map
- `DominHermesSkillDomain` — 12 domain enum (FRONTEND, BACKEND, RESEARCH, N8N, etc.)

### CHANGED: core/agent_orchestrator.py (~+80 lines)
- Replace `_execute_mock()` with `_execute_real()` using `delegate_task()` from hermes_tools
- Toolset per role (`_get_tools_for_role()`)
- File extraction + verification (`_extract_files()`, `_verify_files_exist()`)
- Fall back to mock when hermes_tools unavailable

### CHANGED: core/execution_loop.py (~+100 lines)
- Context-aware `_build_context()` includes existing files, architecture, decisions
- Auto-checkpoint after each phase transition
- Stuck detection (3 iterations with 0 progress → re-plan)
- Adaptive phase tracking via _current_phase() and _phase_changed()

### CHANGED: core/agent_prompts.py (~+50 lines)
- Replace hardcoded SKILL_MAP → dynamic `SkillDiscoverer.get_skills_for_role()`
- Replit-style context section: "You have these Hermes skills available..."
- add role-specific domain expertise blocks (RESEARCHER_SKILLS, FRONTEND_SKILLS, etc.)

### NEW: core/context_manager.py (~120 lines)
- `.hermes-context/` directory per project
- `file_listing.json` — recursive file listing (excludes .git, __pycache__ etc.)
- `iteration_log.json` — history of all iterations
- `phase_log.json` — phase transitions
- `checkpoints.json` — checkpoint references for recovery

### NEW: core/progress_monitor.py (~80 lines)
- `get_progress_summary()` — total, completed, failed, blocked, remaining, percentage
- `report_status()` — visual progress bar `[████░░░░░░] 50%`
- `get_phase_breakdown()` — per-task-type completion
- Stuck detection feed (`get_recent_results(3)`)

### NEW: core/human_loop.py (~50 lines)
- `ask_user(question, choices, default)` — uses clarify() when available
- `confirm_action(action, details)` — defaults to False (safe)
- `resolve_conflict(conflict, options)` — defaults to first option
- All decisions logged for audit

### NEW: core/token_tracker.py (~50 lines)
- `log(task_id, input_tokens, output_tokens)` — per-task tracking
- `get_summary()` — model, total tokens, cost, tasks tracked
- `estimate_remaining(n)` — average-based projection
- Model-aware pricing (default, deepseek-v4-flash, opencode200k)

## Test Additions

- `tests/test_skill_discoverer.py` — 7 tests (discover, match, edge cases)
- `tests/test_context_manager.py` — 3 tests (dir, listing, persistence)
- `tests/test_progress_monitor.py` — 2 tests (summary, format)
- `tests/test_human_loop.py` — 2 tests (disabled, confirm default)
- `tests/test_token_tracker.py` — 2 tests (track, cost diff)

## Critical Rules

1. All 129 existing tests MUST still pass (backward compatibility)
2. schema.py enums MUST NOT change
3. No new external dependencies (Python stdlib only + existing packages)
4. All new functions MUST have type hints and docstrings
5. Use threading.RLock for all shared state
6. Mock executions must still work (when hermes_tools unavailable)
7. SKILL_MAP is DEAD — use skill_discoverer.py dynamic discovery only
8. Never hardcode skill names — always use tag/keyword matching
