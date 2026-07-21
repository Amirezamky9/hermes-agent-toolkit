# Validation Pass — Worked Example

From POS_MINIAPP audit session (2026-07-19).

## Example: T0.1 — Bearer Token Garbled

### Claimed Issue
`api.ts` line 10: `*** ${token}` should be `Bearer ${token}`.

### Validation

**File:** `frontend/src/services/api.ts`
**Line:** 10
**Code:**
```typescript
'Authorization': *** ${token}`,
```

**Should be:**
```typescript
'Authorization': `Bearer ${token}`,
```

**Why it's wrong:** Backtick and "Bearer" were deleted. In TypeScript strict
mode this isn't a syntax error (`***` is a valid identifier, `${token}` is
a template literal), but the header value becomes `*** <token>` instead of
`Bearer <token>`.

**Effect:** Backend expects `Bearer <token>` (via HTTPBearer security scheme).
Every frontend API call returns 401. The app is non-functional.

**Environment:** Production + Development
**False Positive:** ❌ No — 100% real
**Confidence:** ✅ 100%

**Decision:** ✅ Proceed

---

## Example: T0.3 — Habit Delete No-Op (MOVED to Phase 2)

### Claimed Issue
`HabitsPage.tsx` lines 246-254: `onConfirm` doesn't call delete API.

### Validation

**File:** `frontend/src/pages/HabitsPage.tsx`
**Lines:** 246-254
```typescript
onConfirm={() => {
  if (deleteId) {
    toastWithUndo({
      message: '🗑️ عادت حذف شد',
      onUndo: () => queryClient.invalidateQueries({ queryKey: ['habits'] }),
    })
    setDeleteId(null)
  }
}}
```

**Why it's wrong:** Handler only shows toast and closes dialog. No API call.

**But — does the API even exist?**
1. `services/index.ts` lines 31-37: `habitsService` has `list`, `create`,
   `complete`, `getStreak` — **no `delete` method**.
2. `api/v1/habits.py`: only GET list, POST create, POST complete, GET streak.
   **No DELETE endpoint.**
3. `services/habit_service.py`: only `list_by_user`, `create`, `complete`,
   `get_streak`. **No `delete` method.**

**Conclusion:** Delete functionality is NOT IMPLEMENTED anywhere — frontend,
backend, or service layer. The button is UI-only.

**Environment:** Production + Development
**False Positive:** ❌ No — 100% real
**Confidence:** ✅ 100%

**Decision:** ⚠️ **Phase Review** — This is NOT a simple Phase 0 fix.
Requires: backend endpoint + backend service method + frontend service method.
Moved to Phase 2 (Backend Architecture).

---

## Key Lesson

A "simple UI fix" (add API call to onConfirm) was actually a 3-file change
across frontend service, backend router, and backend service. Validation
caught this BEFORE execution, preventing a half-fix that would have crashed
on the missing backend endpoint.

**Always check: does the backend endpoint exist before adding a frontend call?**
