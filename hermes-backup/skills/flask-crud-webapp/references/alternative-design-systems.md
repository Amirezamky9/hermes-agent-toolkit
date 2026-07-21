# Alternative Design Systems for Flask CRUD Apps

When the user provides a standalone HTML mockup with a different design, use the **migration workflow** below instead of building from scratch.

## Design Migration Workflow

1. **Read the reference HTML first** — extract CSS custom properties (`:root` vars), font imports, component class names, and layout structure before touching any project files.
2. **Map design tokens** — create a mapping table from the reference's vars to your project's vars. The reference may use different naming (e.g. `--accent` vs `--accent-primary`). Pick one naming convention and be consistent.
3. **Rewrite CSS** — use the reference's token values but keep your project's variable names. This makes future palette swaps trivial.
4. **Update base.html** — fonts, logo, navbar structure. Preserve all Jinja2 logic, CSRF tokens, theme toggle.
5. **Update child templates** — add new CSS classes from the reference (e.g. `hero-section`, `chips`, `news-grid`) while preserving all `url_for` links, `{% for %}` loops, `{% if %}` conditionals.
6. **Verify** — check every template for: CSRF tokens in forms, url_for calls intact, no hardcoded colors (use CSS vars), extends/block structure preserved.

**Pitfall:** When rewriting templates to match a new layout, it's easy to accidentally remove a `{% if %}` guard or a `csrf_token()`. Do a post-migration grep:
```bash
grep -c "csrf_token" app/templates/*.html app/templates/admin/*.html
grep -c "url_for" app/templates/*.html app/templates/admin/*.html
```
Every file with forms must have at least one csrf_token. Every file must have url_for calls.

## Bold Gaming Palette

Warm, high-energy palette for gaming/entertainment sites. Contrast with the tech-blue palette in `dark-mode-css-patterns.md`.

```css
:root {
  --bg: #0f0f1a;
  --bg-surface: #1a1a2e;
  --bg-elevated: #252540;
  --accent: #ff6b35;    /* orange — primary CTA */
  --accent2: #e63946;   /* red — badges, danger */
  --accent3: #06d6a0;   /* teal — success, tags */
  --accent4: #ffd166;   /* gold — highlights */
  --text: #ffffff;
  --text-sec: #a0a0b8;
  --border: #2a2a45;
}

[data-theme="light"] {
  --bg: #f0f2f5;
  --bg-surface: #ffffff;
  --bg-elevated: #ffffff;
  --accent: #e05a20;
  --accent2: #c5302e;
  --accent3: #05b88a;
  --accent4: #e0b050;
  --text: #1a1a2e;
  --text-sec: #555;
  --border: #dee2e6;
}
```

**Logo pattern** — gradient text using `background-clip`:
```css
.logo span {
  background: linear-gradient(135deg, var(--accent), var(--accent4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

## Component Patterns (from Bold Gaming variant)

### Hero Section (full-bleed with gradient overlay)
```css
.hero-section {
  position: relative;
  min-height: 55vh;
  display: flex;
  align-items: flex-end;
  background-size: cover;
  background-position: center;
  border-radius: var(--radius);
  overflow: hidden;
}
.hero-section::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 20%, var(--bg) 100%);
}
```

### Category Chips
```css
.chips { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.chip {
  padding: 0.4rem 1rem; border-radius: 20px;
  font-size: 0.8rem; font-weight: 700;
  border: 2px solid var(--border); color: var(--text-sec);
  transition: all 0.2s; text-decoration: none;
}
.chip:hover, .chip.active {
  border-color: var(--accent); color: var(--accent);
  background: rgba(255, 107, 53, 0.08);
}
```

### Big Card + Small Stack Grid
```css
.hero-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1.2rem;
}
.big-card { border-radius: var(--radius); overflow: hidden; }
.big-card img { width: 100%; aspect-ratio: 16/10; object-fit: cover; }
.small-stack { display: flex; flex-direction: column; gap: 0.8rem; }
.small-card {
  display: flex; gap: 1rem;
  border-radius: 12px; overflow: hidden;
  border: 1px solid var(--border); transition: all 0.3s;
}
.small-card:hover { border-color: var(--accent3); transform: translateX(-4px); }
.small-card img { width: 130px; object-fit: cover; flex-shrink: 0; }
```

### News Grid (3-col numbered cards)
```css
.news-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem;
}
.news-card {
  background: var(--bg-surface); border-radius: var(--radius);
  border: 1px solid var(--border); position: relative; overflow: hidden;
  transition: all 0.3s;
}
.news-card:hover { transform: translateY(-4px); border-color: var(--accent); }
.news-card .num {
  position: absolute; top: 1rem; left: 1rem;
  font-family: var(--font-en); font-size: 2.5rem; font-weight: 900;
  color: var(--accent); opacity: 0.2;
}
.news-card .tag {
  display: inline-block;
  background: rgba(6, 214, 160, 0.1); color: var(--accent3);
  font-size: 0.7rem; font-weight: 700;
  padding: 0.15rem 0.5rem; border-radius: 4px;
}
```

### CTA Banner (gradient)
```css
.cta-banner {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border-radius: var(--radius); padding: 2.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.cta-btn {
  background: #fff; color: var(--accent2);
  font-weight: 700; padding: 0.6rem 2rem;
  border-radius: var(--radius-sm); transition: transform 0.2s;
}
```

### Admin Stat Cards
```css
.stat-card {
  background: var(--bg-surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem; text-align: center;
}
.stat-card.stat-primary { border-top: 3px solid var(--accent); }
.stat-card.stat-success { border-top: 3px solid var(--accent3); }
.stat-card.stat-info    { border-top: 3px solid var(--accent4); }
.stat-card.stat-warning { border-top: 3px solid var(--accent2); }
```

## Responsive Breakpoints

```css
@media (max-width: 992px) {
  .hero-grid { grid-template-columns: 1fr; }
  .news-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 768px) {
  .news-grid { grid-template-columns: 1fr; }
  .hero-section { min-height: 40vh; }
  .card:hover { transform: none; }  /* disable hover lift on touch */
}
@media (max-width: 600px) {
  .small-card { flex-direction: column; }
  .small-card img { width: 100%; height: 160px; }
}
```
