# Scoring Rubric — Project Health Analysis

## Category Weights

All 7 categories are equally weighted at **15 points** each, for a total of **100**.

## Per-Category Scoring

### 1. Syntax/Compilation (15 pts)

| Criteria | Points |
|---|---|
| All .py files compile | 15 |
| 1 syntax error | 12 |
| 2-3 syntax errors | 8 |
| 4+ syntax errors or critical parse failure | 3 |
| No Python files found | 0 |

### 2. Security (15 pts)

| Criteria | Points |
|---|---|
| SECRET_KEY from env/config (not hardcoded) | +3 |
| Debug mode OFF by default | +3 |
| CSRF protection on all state-changing forms | +3 |
| No hardcoded secrets (API keys, passwords) | +3 |
| SQL injection prevention (ORM or parameterized) | +2 |
| No XSS vectors (autoescaping, sanitization) | +1 |
| Deductions: missing rate limiting (-1), no HTTPS enforcement (-1) |

### 3. Documentation (15 pts)

| Criteria | Points |
|---|---|
| 90%+ docstring coverage | 15 |
| 70-89% | 12 |
| 50-69% | 9 |
| 30-49% | 6 |
| 10-29% | 3 |
| <10% | 1 |
| 0% (no docstrings at all) | 0 |

Coverage = (functions_with_docstrings + classes_with_docstrings) / (total_functions + total_classes)

### 4. Test Coverage (15 pts)

| Criteria | Points |
|---|---|
| Tests exist AND pass | 15 |
| Tests exist but some fail | 10 |
| Test files exist but empty / no assertions | 5 |
| Test directory exists but no test files | 2 |
| No test infrastructure at all | 0 |

### 5. Code Quality (15 pts)

Start at 15, deduct:

| Issue | Deduction |
|---|---|
| Each unused import | -0.5 (max -3) |
| Each true dead code item | -1 (max -5) |
| Each complex function (3+ branches) | -0.5 (max -3) |
| Very long file (>500 LOC) | -1 per file |
| Very long function (>80 LOC) | -1 per function |

Floor: 0. Ceiling: 15.

Note: Decorator-defined functions (e.g., `@admin_required`) are false positives for dead code. Template-called model methods (`has_liked`, `like_count`) may also appear dead — verify before deducting.

### 6. Dependencies (15 pts)

| Criteria | Points |
|---|---|
| All packages in requirements.txt are imported | +5 |
| No unlisted imports (imported but not in requirements) | +3 |
| All versions pinned (==) | +3 |
| No known CVEs in pinned versions | +2 |
| Dev dependencies separated (requirements-dev.txt) | +1 |
| Deductions: each unused package (-2), each unlisted import (-1) |

Note: `lxml` is a bs4 parser backend — it's "used" even if not directly imported. Check the actual relationship.

### 7. Architecture (15 pts)

| Criteria | Points |
|---|---|
| Blueprint/module separation | +3 |
| Models in separate file | +2 |
| Config from environment (not hardcoded) | +3 |
| Templates in organized directory structure | +2 |
| No circular imports | +2 |
| Entry point is minimal (run.py / wsgi.py) | +1 |
| .env.example or config documentation | +1 |
| Deductions: monolithic app.py with all routes (-3), inline HTML (-2) |

## Grade Bands

| Score | Grade | Meaning |
|---|---|---|
| 90-100 | A | Production-ready, well-maintained |
| 80-89 | B | Solid, minor improvements needed |
| 70-79 | C | Functional, several areas need work |
| 60-69 | D | Working but significant gaps |
| 50-59 | F | Major issues across multiple categories |
| <50 | F- | Critical problems, not production-ready |

## Trend Tracking

When comparing across runs:
- **+10 or more**: Significant improvement — celebrate and document what changed
- **+5 to +9**: Good progress — note which categories improved
- **+1 to +4**: Marginal — may be noise; check if fixes were substantive
- **0**: Stagnant — identify highest-impact next action
- **Negative**: Regression — immediately investigate which category dropped and why
