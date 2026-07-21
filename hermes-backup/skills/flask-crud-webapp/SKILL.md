---
name: flask-crud-webapp
description: Lightweight Flask + SQLite CRUD web apps with Docker. University projects, admin panels, RTL/Persian support. One-command deployment.
---

# Flask CRUD Web App

## When to use

Building simple Python web apps for university projects, portfolios, or internal tools. Flask + SQLite + Bootstrap + Docker. Covers CRUD operations, auth, admin panels, and RTL/Persian support.

For real-time apps, see `realtime-web-apps`. For FastAPI backends, see `fastapi-ecommerce-backend`.

## Architecture

```
project/
├── app/
│   ├── __init__.py          # Flask app factory + db init
│   ├── models.py            # SQLAlchemy models
│   └── routes/
│       ├── main.py          # Public pages
│       ├── auth.py          # Login/register/logout
│       └── admin.py         # CRUD admin panel
├── templates/
│   ├── base.html            # Base template with navbar
│   ├── index.html
│   ├── login.html / register.html
│   └── admin/
├── static/css/style.css
├── instance/                # SQLite DB lives here
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── seed.py                  # Demo data
└── run.py                   # Entry point
```

## Key patterns

### App factory (`__init__.py`)
```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # CRITICAL: __file__ is app/__init__.py, so go UP two levels for project root
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    instance_dir = os.path.join(basedir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_dir, 'game.db')
    # ... rest of config
```

### Blueprint registration
```python
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
```

### Slug for URLs
```python
from slugify import slugify
slug = slugify(title, allow_unicode=True)  # supports Persian/Arabic
```
**pip install python-slugify** — not included in Flask core.

### Seed script pattern
Create `seed.py` at project root that imports `create_app`, creates tables, and inserts demo data. Run once before first launch.

### Docker (one command)
```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
```

### Docker production hardening
The minimal compose above is fine for dev. For anything real:
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

FROM python:3.12-slim
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY . .
RUN mkdir -p instance && chown -R appuser:appuser /app
USER appuser
EXPOSE 5001
HEALTHCHECK --interval=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/')"
CMD ["gunicorn", "-b", "0.0.0.0:5001", "-w", "4", "run:app"]
```
Key points: non-root user, gunicorn instead of Flask dev server, HEALTHCHECK, multi-stage build. Add `gunicorn` to requirements.txt.

### RTL/Persian support
- Bootstrap RTL CDN: `bootstrap.rtl.min.css`
- HTML tag: `<html lang="fa" dir="rtl">`
- No additional RTL libraries needed for basic layouts

### Dark mode design system (CSS custom properties)
When building a Flask CRUD app that needs a professional look (gaming sites, dashboards, portfolios), use CSS custom properties for theming. Dark-first is the default for gaming/tech sites.

**Three-file approach**: `DESIGN.md` (color palette docs) → `style.css` (CSS vars + component styles) → `base.html` (theme toggle + font loading).

**Design migration** (applying a mockup to an existing project): See `references/alternative-design-systems.md` for the migration workflow and the Bold Gaming palette. Key: read reference HTML first → map tokens → rewrite CSS → update base.html → update child templates → verify CSRF/url_for preservation.

**Base pattern** — `:root` for dark (default), `[data-theme="light"]` for light:
```css
:root {
    --bg-primary: #0d1117; --bg-surface: #161b22; --bg-elevated: #1c2333;
    --accent-primary: #00d4ff; --accent-secondary: #7c3aed;
    --text-primary: #e6edf3; --text-secondary: #8b949e;
    --border-color: #30363d; --radius-card: 12px; --radius-sm: 8px;
    --font-body: 'Vazirmatn', sans-serif; /* Persian web font */
    --font-en: 'Inter', sans-serif;        /* English/numbers */
}
[data-theme="light"] {
    --bg-primary: #f0f2f5; --bg-surface: #ffffff;
    --accent-primary: #0066cc; --text-primary: #1a1a2e;
    /* ... */
}
```

**HTML toggle** — `data-theme` attribute on `<html>`, persisted to localStorage:
```html
<html lang="fa" dir="rtl" data-theme="dark">
<!-- In <head>: -->
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap" rel="stylesheet">
<!-- Before </body>: -->
<script>
(function() {
    var saved = localStorage.getItem('theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
})();
function toggleTheme() {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}
</script>
```

**Key CSS choices for Persian/RTL**:
- Line height 1.75 (RTL scripts need more vertical space than Latin)
- Vazirmatn font — modern web-optimized Naskh, better than Tahoma/Vazir for body text
- Bootstrap RTL CDN (`bootstrap.rtl.min.css`) handles direction-aware spacing
- Remove hardcoded `bg-dark` from templates — let CSS vars drive all colors
- Navbar: translucent dark with `backdrop-filter: blur(12px)` — works in both themes
- Cards: `var(--bg-surface)` bg, glow on hover via `box-shadow: 0 0 20px rgba(accent)`
- See `references/dark-mode-css-patterns.md` for full implementation template

### Admin panel pattern
- Decorator `admin_required` wrapping `login_required`
- Check `current_user.is_admin`
- Standard CRUD: list → new → edit → delete (with POST confirm)

## Pitfalls

### 0. Explain packages before asking user to install
When telling the user to run `apt-get install ...`, ALWAYS explain what each package does first. Users get frustrated by "install this" without context. Example:
- ❌ "Run `apt-get install -y libglib2.0-0 libnss3 ...`"
- ✅ "These are system libraries Chromium needs. `libglib` is the Linux core, `libnss` handles encryption, `libx11` is the graphics interface..." THEN give the command.

### 1. **`| safe` filter = stored XSS.**

2. **Debug mode = RCE.** `app.run(debug=True)` exposes the Werkzeug interactive debugger, which executes arbitrary Python on the server. Combined with a hardcoded SECRET_KEY (anyone can authenticate to the debugger PIN), this is full server compromise. Never ship with debug=True.

3. **SQLite path in `__init__.py`** — `os.path.dirname(__file__)` gives the `app/` directory, NOT the project root. Use `os.path.dirname(os.path.dirname(__file__))` to get project root. Always `os.makedirs(instance_dir, exist_ok=True)`.

4. **Missing `python-slugify`** — Flask doesn't include it. Add to requirements.txt: `python-slugify==8.0.4`.

5. **`instance/` directory must exist** — SQLite can't create parent directories. Always `os.makedirs()` before first connection.

6. **Flask-Login `user_loader`** — Must be decorated with `@login_manager.user_loader` and accept `user_id` as string. Place in `models.py` or `__init__.py`.

7. **Blueprint import order** — Models must be imported BEFORE `db.create_all()`. Use lazy imports or import in `create_app()` after registering blueprints.

8. **Bootstrap RTL** — Use `bootstrap.rtl.min.css`, not `bootstrap.min.css` + manual RTL. The RTL version handles direction-aware spacing automatically.

9. **`db.create_all()` does NOT alter existing tables** — This is the #1 debugging trap. If you add a column to a model (e.g. `source_url`) and the SQLite file already exists from a previous run, `create_all()` silently skips it. You get `no such column` errors at runtime. Fix: delete `instance/game.db` before re-running, or use `flask-migrate` for schema evolution. Never trust that "it worked before" — check `PRAGMA table_info(tablename)` to verify actual columns.

10. **Port 5000 held by zombie Flask processes** — Flask debug mode auto-reloads, and leftover processes can hold the port. When you get `Address already in use`, kill ALL python processes (`pgrep -a python` / `kill $(pgrep -f "python.*run.py")`) before retrying. Or just use port 5001 to avoid collisions with macOS AirPlay (which also claims 5000).

11. **Hardcoded SECRET_KEY** — `app.config['SECRET_KEY'] = 'my-secret'` is the #1 security mistake in Flask CRUD templates. Always use `os.environ.get('SECRET_KEY')` with a fallback to `os.urandom(24)`. Hardcoded keys let anyone forge session cookies.

10. **Open redirect in login** — The pattern `next_page = request.args.get('next'); return redirect(next_page)` lets an attacker craft `?next=https://evil.com` to redirect users after login. Validate: `if next_page and next_page.startswith('/'): redirect(next_page)`.

11. **Model methods defined but never called** — After scaffolding, common to have model helper methods (`has_liked`, `like_count`) that no route or template actually uses. Run the AST dead-code check to catch these before they rot.

12. **Template variable mismatch = silent 500.** Every `{% for x in some_var %}` or `{{ var.field }}` in a template requires the route's `render_template()` to pass that variable. Missing → Jinja2 `UndefinedError` → 500 with no obvious cause. Cross-reference:
   ```bash
   # Variables used in templates (Jinja2 names)
   grep -rPoh '\{\{[\s]*(?:for\s+\w+\s+in\s+)?(\w+)' app/templates/ | sort -u
   # Variables passed in render_template calls
   grep -rPoh 'render_template\([^)]+\)' app/routes/
   ```
   Common miss: sidebar in `article.html` iterates `{% for cat in categories %}` but the `article()` route only passes `article`, `comments`, `user_like` — no `categories`. Instant crash on every article page.

13. **AnonymousUserMixin has no profile attributes.** `current_user.username` in Jinja2 crashes for anonymous visitors — `AnonymousUserMixin` only has `is_authenticated=False`. Always guard:
   ```jinja2
   {% if current_user.is_authenticated and current_user.username == profile_user.username %}
   ```

14. **N+1 queries in profile/list pages.** Iterating `Like.query.filter_by(user_id=X).all()` then doing `Article.query.get(like.article_id)` per item = one SQL query per like. Fix with JOIN:
   ```python
   liked_articles = Article.query.join(Like).filter(
       Like.user_id == user.id, Like.like_type == 'like'
   ).all()
   ```

15. **Deprecated `datetime.utcnow`.** `datetime.utcnow` is deprecated since Python 3.12 (returns naive datetime, breaks DST). Use `datetime.now(timezone.utc)` and store timezone-aware datetimes. Or use `db.func.now()` as server_default.

16. **Template redesign = silent Jinja2 breakage.** When rewriting templates for a new design, it's easy to drop a `{% if %}` guard, a `{% for %}` loop, or a `csrf_token()`. After any bulk template rewrite, verify:
    ```bash
    grep -c "csrf_token" app/templates/*.html app/templates/admin/*.html
    grep -c "url_for" app/templates/*.html app/templates/admin/*.html
    ```
    Every form file needs ≥1 csrf_token. Every template needs url_for calls. Missing either = broken functionality that looks visually fine.

## gstack Workflow (on Hermes)

When using gstack to test/review a Flask CRUD project, follow this **exact order**:

1. **`/design-consultation`** — Create design system (colors, fonts, layout) BEFORE coding UI
2. **`/design-shotgun`** — Generate multiple design variants
3. **`/design-html`** — Convert approved design to HTML/CSS
4. **`/design-review`** — Visual QA, fix spacing/hierarchy/consistency
5. **`/qa`** — Functional testing with browser (login, CRUD, forms, responsive)
6. **`/review`** — Code review (security, quality, best practices)
7. **`/cso`** — Security audit (OWASP Top 10, secrets, dependencies)
8. **`/health`** — Code quality score (syntax, tests, docstrings)

**CRITICAL: Run agents SEQUENTIALLY, never in parallel.** gstack agents share the browse server state. Running them in parallel causes:
- `"Another instance is starting the server"` errors
- Race conditions on state files
- Rate limiting on API calls

```bash
# CORRECT: one at a time
# Step 1: design-consultation
# Step 2: design-shotgun
# ... etc

# WRONG: all at once
# delegate_task(tasks=[design, qa, review, cso])  ← DO NOT DO THIS
```

**User preference:** When building a new project, proactively suggest design tools (`/design-consultation`, `/design-shotgun`) BEFORE asking about code. Users expect the full workflow, not just code + tests.

## References

- `references/rss-scraping.md` — RSS feed parsing, gaming news sources, category auto-detection
- `references/like-system-profile.md` — Like/dislike toggle model + profile page with tabs
- `references/dark-mode-css-patterns.md` — CSS custom properties for dark/light theming, RTL typography, component styles, pitfalls
- `references/alternative-design-systems.md` — Design migration workflow, Bold Gaming palette, hero/chips/grid/CTA component patterns
- `references/gstack-browse-hermes.md` — gstack browse binary setup on Hermes, state conflict fixes, system lib requirements

## Verification

```bash
# Without Docker
pip install -r requirements.txt
python seed.py
python run.py
# Open http://localhost:5000

# With Docker
docker compose up --build
# Open http://localhost:5000

# Test endpoints
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/           # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/auth/login  # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/admin/      # 302 (redirect to login)
```

## Health Check (AST-based, no external tools)

For quick inline scans, use the script below. For **comprehensive scoring** with category breakdowns, comparison to previous runs, and trend tracking, use the `project-health-analysis` skill (has a reusable `scripts/ast-health.py` and `references/scoring-rubric.md`).

Run after any build or before shipping. Uses only Python stdlib — no ruff/flake8/pytest needed for the scan itself.

```python
#!/usr/bin/env python3
"""One-shot health check — run from project root, delete after."""
import ast, os, json

results = {}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'instance']
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path) as fh:
                source = fh.read()
            tree = ast.parse(source)
            funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            missing_func = sum(1 for f in funcs if not ast.get_docstring(f))
            missing_cls = sum(1 for c in classes if not ast.get_docstring(c))
            # Unused imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names: imports.append(a.asname or a.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for a in node.names: imports.append(a.asname or a.name)
            unused = [i for i in imports if i != '*' and source.count(i) <= 1]
            # Complex funcs (3+ branches)
            complex_ = []
            for node in funcs:
                branches = sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try)))
                if branches >= 3: complex_.append((node.name, branches))
            results[path] = {
                'lines': len(source.splitlines()),
                'funcs': len(funcs), 'missing_docstrings': missing_func,
                'classes': len(classes), 'missing_class_docs': missing_cls,
                'unused_imports': unused, 'complex': complex_,
            }
for p, r in sorted(results.items()):
    print(f"{p}: {r['lines']}L | {r['funcs']} funcs ({r['missing_docstrings']} no doc) | "
          f"{r['classes']} classes ({r['missing_class_docs']} no doc) | "
          f"unused={r['unused_imports']} complex={r['complex']}")
```

### What to check after the AST scan

| Check | How | Pass criteria |
|---|---|---|
| Syntax | `python -m py_compile *.py` | Zero errors |
| Unused imports | AST script above | None |
| Dead code | Define graph: which funcs are called? Route handlers count as used | Zero or explain why |
| Docstrings | AST script above | Models + routes should have them |
| Template vars | Grep templates for `{{ var }}` / `{% for x in var %}`, grep routes for `render_template` args | Every template var passed by its route |
| Tests | `ls tests/` + `ls pytest.ini conftest.py tox.ini` | At least one test file |
| Dependencies | `pip list \| grep -iE "pytest\|ruff\|mypy"` | Some dev/lint tools present |
| CVEs | `pip-audit -r requirements.txt` | Zero known vulnerabilities |

### Security checklist (common in Flask CRUD apps)

Run this checklist on EVERY Flask CRUD app before shipping. These are the bugs that ship in real projects (verified from audits).

| # | Issue | How to find | Severity | Fix |
|---|---|---|---|---|
| 1 | Hardcoded SECRET_KEY | `grep -r "SECRET_KEY.*=.*'" app/` | 🔴 CRITICAL | `os.environ.get('SECRET_KEY')` + fail in prod |
| 2 | Debug mode in production | `debug=True` in run.py or env | 🔴 CRITICAL | `debug=os.environ.get('FLASK_DEBUG') == '1'` |
| 3 | `{{ content \| safe }}` XSS | Grep templates for `\| safe` on user/admin content | 🔴 CRITICAL | Sanitize with `bleach` before storage |
| 4 | No CSRF on forms | Check for `flask-wtf` in requirements + `csrf_token()` in forms | 🟠 HIGH | See CSRF setup below |
| 5 | Hardcoded seed passwords | `grep -r "password.*=.*'" seed.py` | 🟠 HIGH | `os.environ.get('ADMIN_PASSWORD')` |
| 6 | Open redirect in login | `request.args.get('next')` → `redirect()` | 🟠 HIGH | Validate: reject absolute URLs |
| 7 | No password policy | Registration accepts any length password | 🟠 HIGH | Server-side: min 8 chars, complexity |
| 8 | No rate limiting | Login/register/comment endpoints | 🟠 HIGH | `pip install flask-limiter` |
| 9 | No security headers | No CSP, X-Frame-Options, etc. | 🟡 MEDIUM | `@app.after_request` handler |
| 10 | Missing session cookie flags | No SECURE/HTTPONLY/SAMESITE | 🟡 MEDIUM | Set all three in app config |
| 11 | GET-based logout | `@app.route('/logout')` without `methods=['POST']` | 🟡 MEDIUM | POST only, update nav to form |
| 12 | Unvalidated form inputs | No server-side validation on registration | 🟡 MEDIUM | Validate username/email/password |

**Dependency scan (always run):**
```bash
pip install pip-audit && pip-audit -r requirements.txt
```
Pinned dependencies go stale. `pip-audit` catches known CVEs. Run before every deploy.

### CSRF setup (Flask-WTF)

Add `flask-wtf` to `requirements.txt`, then:

```python
# app/__init__.py
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    # ... config ...
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)          # ← enables CSRF globally
    # ...
```

Every `<form method="post">` needs a token:
```html
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- fields -->
</form>
```

Without this, all POST forms (login, register, admin CRUD, like/dislike, comments) are vulnerable to cross-site request forgery.

## Pitfalls
