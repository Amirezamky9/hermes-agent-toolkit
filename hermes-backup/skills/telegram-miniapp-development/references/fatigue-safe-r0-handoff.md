# Fatigue-safe R0 pause and cross-chat handoff

Use when a user asks to stop because of headache, fatigue, time, or cognitive overload during an interactive product/engineering/design review.

## Goal

Stop immediately at a resumable boundary without pretending the review is complete. Preserve confirmed decisions, exact remaining work, and implementation prohibitions so the next chat resumes without repeating gates.

## Procedure

1. **Stop asking questions.** Do not squeeze in “one last decision.”
2. **Name the state honestly:** `in progress; intentionally paused`, not complete/approved.
3. **Create or update the phase plan** (`R0-DESIGN-PLAN.md`, engineering plan, etc.) with:
   - canonical inputs;
   - completed review step/pass;
   - confirmed decisions and user rationale;
   - existing artifact paths;
   - exact ordered remaining work;
   - hard stop on implementation.
4. **Update the canonical roadmap:** timestamp, current phase, exact resume point.
5. **Update the next-chat handoff:** replace stale prompts rather than appending another conflicting prompt.
6. **Create an append-only checkpoint** under the gstack project checkpoint directory.
7. **Verify from disk:** all files exist, key decisions appear, artifact exists, and prohibited actions remain unperformed.
8. **Return one copy-paste prompt** for the next chat. Explicitly say which gates/reviews must not be restarted.

## Design-review specifics

When pausing after visual feedback, record:

- selected variant and why the user preferred it;
- mandatory theme requirements such as Dark Mode;
- known weakness to improve without reopening the direction;
- whether the artifact is generated imagery or an HTML fallback;
- the next visual deliverable (for example, approved direction in light/dark) before later review passes.

## Minimal checkpoint template

```markdown
---
status: in-progress
branch: unknown-pre-git
timestamp: <ISO-8601>
files_modified:
  - docs/ROADMAP.md
  - docs/NEXT-CHAT-HANDOFF.md
  - docs/R0-<PHASE>-PLAN.md
---

## Working on: <phase>

### Summary
<completed and exact pause point>

### Decisions Made
- <decision + rationale>

### Remaining Work
1. <exact next action>

### Notes
- <artifact paths>
- <hard prohibitions>
```

## Pitfalls

- Do not mark the phase complete merely to “wrap up.”
- Do not leave the old next-chat prompt in place.
- Do not rely only on conversation history.
- Do not re-ask already completed scope gates in the next session.
- Do not treat a visual HTML planning artifact as application code.
