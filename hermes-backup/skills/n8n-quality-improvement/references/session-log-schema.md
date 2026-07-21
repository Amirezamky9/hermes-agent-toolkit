# Session Log Schema Reference

## File Location
`session-logs/YYYY-MM-DD_session-log.yaml`

## YAML Schema

```yaml
session:
  id: "[session_id from /status or session_search]"
  date: "YYYY-MM-DD"
  phase: "intake | planner | reviewer | builder"
  topic: "brief topic"
  model_used: "model name"

# ── USER FILLS ──

user_manual_fixes:
  - symptom: "what went wrong"
    manual_fix: "how I fixed it in n8n UI"
    root_cause: "why it broke"
    n8n_ui_fix: true/false

user_feedback:
  - topic: "subject"
    detail: "the feedback"
    type: "correction | improvement | best_practice"

user_suggestions:
  - "new idea"

user_missed:
  - "something you felt I misunderstood"

# ── JUDGE FILLS ──

judge_model_mistakes:
  - detail: "what the model did wrong"
    model: "opencode200k | deepseek-v4-flash | ..."
    in_trap_ref: true/false

judge_observations:
  - detail: "thing I noticed"
    priority: low | medium | high

judge_stats:
  successful_nodes: N
  failed_attempts: N
  tokens_used: N
```

## Field Guide

| Field | Who | When | Required |
|-------|-----|------|----------|
| `session.id` | Both | After session | Yes |
| `user_manual_fixes` | User | After manual fix | If applicable |
| `user_feedback` | User | After giving feedback | If applicable |
| `user_suggestions` | User | Any time | Optional |
| `user_missed` | User | Any time | Optional |
| `judge_model_mistakes` | Judge | End of session | Yes (can be empty) |
| `judge_observations` | Judge | End of session | Yes (can be empty) |
| `judge_stats` | Judge | End of session | Yes |
