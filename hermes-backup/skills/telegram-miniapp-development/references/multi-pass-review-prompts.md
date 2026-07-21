# Multi-Pass Review Prompts

## Code Review (3-Pass)

### Pass 1: Critical Bugs & Security
```
Read EVERY file in backend/ and frontend/src/ and check:
1. SQL Injection — parameterized queries? No f-strings in SQL?
2. Auth Bypass — every endpoint requires JWT?
3. Data Leakage — every query filters by user_id?
4. Hardcoded Secrets — any keys/tokens in source?
5. Workspace Ownership — can user A create data in user B's workspace?
6. Missing Validation — Pydantic schemas validate all inputs?
7. Error Handling — no bare except:, proper status codes?
8. N+1 Queries — any lazy loading loops?
For each: file path + line + exact fix.
```

### Pass 2: Functionality & Integration
```
Trace every user flow end-to-end:
1. Onboarding -> workspace -> habits -> tasks (any broken links?)
2. Morning check-in -> daily tasks -> evening reflection
3. Task complete -> timeline event -> dashboard update
4. Habit complete -> streak calculation -> display
5. Frontend API calls match backend endpoints?
6. TypeScript types match Pydantic schemas?
7. Persian/Gregorian toggle works everywhere?
8. RTL layout correct on all pages?
For each: file + what's broken + exact fix.
```

### Pass 3: Code Quality
```
1. DRY violations — duplicated code?
2. Missing tests — every service/endpoint has tests?
3. TODO comments — all documented?
4. SQLAlchemy relationships — all defined?
5. Docker — compose works? Services connected?
6. Frontend — loading/error/empty states on every page?
7. Performance — unnecessary re-renders? Missing memoization?
Score: X/10, list top 10 fixes.
```

## UX Review (4-Pass)

### Pass 1: Speed & Performance
```
Walk through as a user opening the app:
1. First load — spinner? Skeleton? Blank screen?
2. Page transitions — instant feedback? Unnecessary re-fetch?
3. Charts — load instantly or blank squares?
4. Form submission — loading indicator? Double-tap protection?
5. Offline — crash or friendly message?
For each: user impact + exact fix + file.
```

### Pass 2: UX Design
```
Walk through each flow as non-technical user:
1. First time — understand app? Overwhelming? Can skip?
2. Morning check-in — quick (<30s)? Intuitive? Know why?
3. Complete task — big checkbox? Satisfying feedback? Undo?
4. Complete habit — streak visible before? Celebration?
5. Dashboard — understand in 3 seconds? Readable on mobile?
6. Evening reflection — tiring? Fun mood selector?
For each: what user thinks/feels + fix.
```

### Pass 3: Security & Production
```
1. Error messages — Persian? Friendly? Not exposing internals?
2. Empty states — helpful message vs "nothing here"?
3. Input validation — empty forms? Too long? Special chars?
4. Edge cases — 0 tasks? 0 habits? First day? Double complete?
5. Logout — works? Data preserved?
6. Back button — works on every page?
7. Keyboard — pushes content up? Correct "Done" type?
8. Tap targets — all >=44px? Spaced enough?
9. Contrast — readable text everywhere?
10. Scroll — smooth? Any horizontal scroll?
```

### Pass 4: Production Checklist
```
- All API errors return Persian messages
- Loading states on EVERY async action
- Empty states on EVERY list
- Form validation on EVERY input
- Confirmation on EVERY destructive action
- Back button works on EVERY page
- Pull-to-refresh on lists
- RTL layout on EVERY page
- No horizontal scroll anywhere
- Status bar color matches theme
```
