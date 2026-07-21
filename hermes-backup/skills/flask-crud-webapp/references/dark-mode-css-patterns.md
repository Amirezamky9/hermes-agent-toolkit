# Dark Mode CSS Patterns for Flask CRUD Apps

## Full CSS Custom Properties Template

```css
/* ============================================
   CSS Custom Properties — Dark-first theming
   ============================================ */
:root {
    /* Dark theme (default) */
    --bg-primary: #0d1117;
    --bg-surface: #161b22;
    --bg-elevated: #1c2333;
    --bg-hover: #21262d;
    --accent-primary: #00d4ff;
    --accent-secondary: #7c3aed;
    --accent-success: #10b981;
    --accent-danger: #ef4444;
    --accent-warning: #f59e0b;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #484f58;
    --border-color: #30363d;
    --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
    --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.15);
    --radius-card: 12px;
    --radius-sm: 8px;
    --blur-nav: blur(12px);
    --font-body: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;
    --font-en: 'Inter', 'Segoe UI', sans-serif;
}

[data-theme="light"] {
    --bg-primary: #f0f2f5;
    --bg-surface: #ffffff;
    --bg-elevated: #ffffff;
    --bg-hover: #e8eaed;
    --accent-primary: #0066cc;
    --accent-secondary: #6d28d9;
    --text-primary: #1a1a2e;
    --text-secondary: #555;
    --text-muted: #999;
    --border-color: #dee2e6;
    --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.08);
    --shadow-glow: none;
}
```

## Navbar Pattern (translucent dark)

```css
.navbar {
    background: rgba(13, 17, 23, 0.85) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-color);
}
[data-theme="light"] .navbar {
    background: rgba(255, 255, 255, 0.9) !important;
}
```

## Card Hover Glow Pattern

```css
.card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-card);
    box-shadow: var(--shadow-card);
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-glow), var(--shadow-card);
    border-color: var(--accent-primary);
}
/* Disable hover lift on mobile */
@media (max-width: 768px) {
    .card:hover { transform: none; }
}
```

## Button Glow on Hover

```css
.btn-primary {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: #000;
}
.btn-primary:hover {
    background: #00b8e6;
    box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
}
```

## Form Focus Ring

```css
.form-control {
    background: var(--bg-hover);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}
.form-control:focus {
    background: var(--bg-surface);
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15);
    color: var(--text-primary);
}
```

## Alert Theme Variants

```css
.alert-success { background: rgba(16, 185, 129, 0.15); color: var(--accent-success); border-color: rgba(16, 185, 129, 0.3); }
.alert-danger  { background: rgba(239, 68, 68, 0.15);  color: var(--accent-danger);  border-color: rgba(239, 68, 68, 0.3); }
.alert-warning { background: rgba(245, 158, 11, 0.15); color: var(--accent-warning); border-color: rgba(245, 158, 11, 0.3); }
.alert-info    { background: rgba(0, 212, 255, 0.1);    color: var(--accent-primary); border-color: rgba(0, 212, 255, 0.3); }
```

## Category Color Mapping (gaming sites)

| Category | CSS class | Hex |
|---|---|---|
| اکشن (Action) | `.badge-cat-action` | `#ef4444` |
| ماجراجویی (Adventure) | `.badge-cat-adventure` | `#f59e0b` |
| ورزشی (Sports) | `.badge-cat-sports` | `#10b981` |
| RPG | `.badge-cat-rpg` | `#7c3aed` |
| استراتژی (Strategy) | `.badge-cat-strategy` | `#0ea5e9` |
| تیراندازی (Shooter) | `.badge-cat-shooter` | `#f97316` |

## Color Palette Quick Reference

### Dark Theme (gaming/tech)
- Page bg: `#0d1117` (near-black with blue undertone)
- Surface: `#161b22` (card/panel bg)
- Primary accent: `#00d4ff` (cyan — energetic, gaming)
- Secondary accent: `#7c3aed` (purple — premium feel)
- Borders: `#30363d` (subtle separation)

### Light Theme (professional)
- Page bg: `#f0f2f5` (warm gray)
- Surface: `#ffffff`
- Primary accent: `#0066cc` (professional blue)

## Pitfalls

1. **Don't hardcode colors in templates.** Every `bg-dark`, `text-white`, `bg-primary` in Bootstrap classes should be replaced by CSS var references. Bootstrap's utility classes use Bootstrap's own color scale, not your design tokens.

2. **`backdrop-filter` needs `-webkit-` prefix** for Safari. Always include both.

3. **`data-theme` default must match `:root`** — if `:root` defines dark colors, `<html>` must have `data-theme="dark"`. Mismatches cause flash of wrong theme on load.

4. **localStorage theme must be set BEFORE first paint** — use an IIFE in `<head>` or inline script before body content to read localStorage and set the attribute. Setting it at end of `<body>` causes a flash.

5. **Vazirmatn weight range** — load 400, 700 for body/headings. Loading all 9 weights wastes bandwidth on a news site. Use `font-display: swap` (Google Fonts does this by default).
