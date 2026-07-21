# gstack QA Workflow — Adapted for Hermes

## Original: gstack `/qa` skill

Systematic QA testing with a real browser. Test → Fix → Verify loop with screenshots, health scores, and structured reports.

## Hermes Adaptation

### What Works Directly
- `browser` tool for navigation, screenshots, form interaction
- `terminal` for git commands, test framework detection
- `read_file` / `write_file` / `patch` for bug fixes
- `vision_analyze` for annotated screenshots
- `delegate_task` for parallel testing (future)

### What Needs Adaptation
- **Diff-aware mode**: gstack auto-detects branch changes via `git diff`. Hermes can do this via `terminal` + `search_files` but needs explicit instructions.
- **Health score rubric**: gstack has a weighted scoring system. Hermes would need to compute this from findings.
- **Screenshot diffing**: gstack's `$B snapshot -D` shows before/after changes. Hermes would need manual comparison via `vision_analyze`.
- **Console/network monitoring**: gstack's `$B console --errors` and `$B network` aren't directly available in Hermes browser tool.
- **Cookie import**: gstack can import browser cookies. Hermes browser tool may not support this.

### Adapted QA Phases

#### Phase 1: Initialize
```
1. Verify server is running (curl localhost:PORT)
2. Detect project type (package.json, requirements.txt, etc.)
3. Create output directory for screenshots/reports
```

#### Phase 2: Authenticate (if needed)
```
1. Navigate to login page
2. Fill credentials
3. Verify login success
```

#### Phase 3: Orient
```
1. Navigate to target URL
2. Take initial screenshot (vision_analyze)
3. List navigation links
4. Check for JS errors (if accessible)
```

#### Phase 4: Explore
```
For each page:
1. Navigate to page
2. Take screenshot
3. Test interactive elements (forms, buttons)
4. Check responsive (mobile viewport)
5. Document issues immediately
```

#### Phase 5: Document
```
For each issue:
1. Take before screenshot
2. Perform action
3. Take after screenshot
4. Write repro steps
5. Classify severity (Critical/High/Medium/Low)
```

#### Phase 6: Health Score
```
Compute weighted score:
- Console errors (15%): 0=100, 1-3=70, 4-10=40, 10+=10
- Broken links (10%): each -15
- Visual (10%): critical=-25, high=-15, medium=-8, low=-3
- Functional (20%): same scoring
- UX (15%): same scoring
- Performance (10%): same scoring
- Content (5%): same scoring
- Accessibility (15%): same scoring

Final = sum(category_score × weight)
```

#### Phase 7: Fix
```
For each high/critical issue:
1. Identify root cause in source
2. Apply fix via patch
3. Commit atomically
4. Re-verify fix
```

#### Phase 8: Report
```
Generate structured report:
- Health score (before/after)
- Issues found (with screenshots)
- Fixes applied
- Remaining issues
```

## Limitations vs gstack

| Capability | gstack | Hermes |
|------------|--------|--------|
| Browser automation | ✅ Full (Chromium daemon) | ✅ Good (Browserbase/Camofox) |
| Console monitoring | ✅ `$B console --errors` | ❌ Not directly available |
| Network monitoring | ✅ `$B network` | ❌ Not directly available |
| Screenshot diffing | ✅ `$B snapshot -D` | ⚠️ Manual via vision_analyze |
| Cookie import | ✅ `$B cookie-import` | ❌ Not available |
| Health score | ✅ Built-in rubric | ⚠️ Need to compute manually |
| Diff-aware mode | ✅ Auto git diff | ⚠️ Need explicit instructions |
| Atomic commits | ✅ Per-fix commits | ✅ Via terminal + git |

## Future Improvements

1. **Console monitoring**: Hermes browser tool could expose console errors via execute_js
2. **Screenshot diffing**: Could use vision_analyze to compare before/after screenshots
3. **Health score script**: Create a reusable script that computes the weighted score from findings
4. **Diff-aware automation**: Script that parses git diff and generates test plan
