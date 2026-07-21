# Per-Action Traceability (Deep Nightly Worker)

## Format

Each action logged by `deep_nightly_worker.py`:

```json
{
  "tool": "file_scan | read_file | system | session_search",
  "query": "what was searched / read",
  "status": "success | error | empty | info",
  "result_count": N,
  "duration_ms": NNN,
  "error": "error message or null",
  "detail": "human-readable summary",
  "timestamp": "ISO datetime"
}
```

## Worker Flow (each night)

```
1. file_scan: session-logs/ + feedback/ for today → count of files found
2. read_file: bugs/manual-fixes.yaml → check for unreported bugs
3. read_file: bugs/platform-bugs.md → check for unresolved platform issues
4. read_file: reports/previous_day_actions.json → compare trends
5. system: cron job status → verify the chain is alive
6. (future) session_search: deep scan for "error|bug|fix|mistake|trap" → missed items
```

## How to Detect a Failed Action

| Signal | Meaning |
|--------|---------|
| `status: "error"` | Tool failed (file not found, permission, parse error) |
| `status: "empty"` | No results (legit — no data yet) |
| `result_count: 0` combined with `status: "success"` | File exists but empty — expected for first run |
| `duration_ms > 5000` | Possible timeout or slow operation |
| Missing action for a step | Worker didn't complete the full flow — investigate |
