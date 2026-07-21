# AI Coding Agent — Mega Prompt Pattern

## MiMo Code (Xiaomi)

**Repository:** github.com/XiaomiMiMo/MiMo-Code
**Install:** `npm install -g @mimo-ai/cli` or `curl -fsSL https://mimo.xiaomi.com/install | bash`
**Website:** mimo.xiaomi.com/coder

### Key Features
- **3 Agents:** build (full permissions), plan (read-only), compose (orchestration)
- **Persistent Memory:** SQLite FTS5 + MEMORY.md + session checkpoints
- **Subagent System:** parallel subagents with lifecycle tracking
- **Workflows:** deterministic JS scripts (compose, deep-research, fact-check)
- **Skills:** builtin skill system for reusable instruction sets
- **Dream & Distill:** self-improvement capabilities

### How to Use MiMo for Project Implementation

1. Create project folder with standard structure
2. Write `docs/MASTER-GUIDE.md` — overview for the agent
3. Write numbered mega prompts in `docs/mega-prompts/`:
   - `01-INFRASTRUCTURE.md` — project setup
   - `02-AUTH-ONBOARDING.md` — authentication + wizard
   - `03-MORNING-HABITS.md` — daily check-in + habits
   - `04-TASKS-REFLECTION.md` — tasks + evening reflection
   - `05-DASHBOARD-CHARTS.md` — dashboard + charts
   - `06-PROFILE-SETTINGS.md` — user profile + settings
   - `07-TIMELINE-REPORTS.md` — timeline + reports
   - `08-N8N-INTEGRATION.md` — n8n placeholder
   - `09-TESTING-POLISH.md` — tests + polish
4. Run `mimo` in the project directory
5. Feed each mega prompt sequentially

### Other AI Coding Agents (same pattern works)

| Agent | Command | Notes |
|-------|---------|-------|
| MiMo Code | `mimo` | Terminal-native, free tier available |
| Claude Code | `claude` | Anthropic's CLI agent |
| Codex | `codex` | OpenAI's CLI agent |
| Cursor | IDE | VS Code fork with AI |
| Cline | VS Code ext | Popular VS Code extension |

All agents benefit from the same mega prompt structure: complete code, exact file paths, testing instructions, checklists.

## Dynamic User-Specific Design Pattern

### Principle
**Nothing is hardcoded.** Each user has their own configuration generated during onboarding.

### Data Flow
```
Onboarding Wizard → user_profile + onboarding_data
↓
Daily Use → habits (per-user schedule) + tasks (per-user time_slot)
↓
Reminders → generated dynamically from user's schedule
↓
Dashboard → shows only current user's data
↓
AI Context → system prompt + user profile + user history
↓
Weekly Report → personalized HTML for each user
```

### Anti-Patterns
```python
# ❌ Hardcoded
REMINDER_HOUR = 8
MAX_TASKS = 10
COURSE_DAYS = ["sat", "mon"]

# ✅ Dynamic
reminder_time = user.settings.morning_checkin_time
max_tasks = calculateFromHours(user.profile.available_hours_per_day)
course_days = course.schedule.preferred_days
```

### Database Pattern
Every entity has a foreign key to `users` or to a user-owned entity (`workspaces`).
Queries always filter by `user_id`. API endpoints always use `current_user` dependency.
