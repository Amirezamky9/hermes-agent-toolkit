# gstack Design Workflow Reference

## 4-Step Design Stack

### Step 1: `/design-consultation`
- Creates `DESIGN.md` — the project's design source of truth
- Updates `style.css` with design system (CSS custom properties, component styles)
- Updates `base.html` with fonts, theme toggle, structure
- Covers: color palette, typography, layout, components, dark/light mode

### Step 2: `/design-shotgun`
- Generates N standalone HTML variants (typically 3)
- Each variant: complete CSS inline, no external deps except Google Fonts
- User reviews and picks one
- Output: `design-variants/variant-N-name.html` + `INDEX.html`

### Step 3: `/design-html`
- Takes the chosen variant and applies it to ALL project templates
- Rewrites CSS to match variant's design system
- Updates all HTML templates (keeps Jinja2 variables, CSRF tokens, URL_for links)
- Heavy subagent work — typically 10-14 files

### Step 4: `/design-review`
- Visual QA with browser screenshots
- Finds: spacing issues, visual inconsistency, hierarchy problems
- Iteratively fixes and re-screenshots
- Produces before/after comparison

## Common Pitfalls

### Template variable breakage
When `/design-html` rewrites templates, it can miss Jinja2 variables. Always re-run `/qa` after design changes to catch:
- Missing `categories` variable in article sidebar
- Missing `current_user` checks for anonymous users
- Broken `url_for()` links

### CSS specificity wars
The variant CSS often conflicts with Bootstrap. Use the variant's CSS custom properties and override Bootstrap classes explicitly. Don't rely on `!important` chains.

### Dark mode toggle
If adding dark/light toggle, persist preference in `localStorage`. The toggle button should be in the navbar. CSS should use `data-theme` attribute on `<html>`.

## Variant Selection UX
After `/design-shotgun`, take screenshots of all variants and send them to the user. Use the gstack browse binary:
```bash
export BROWSE_PORT=<unique_port>
export BROWSE_STATE_FILE=/tmp/browse-state-<N>.json
B=~/.hermes/skills/gstack/browse/dist/browse
$B goto "file:///path/to/variant.html"
$B viewport 1280x900
$B screenshot /path/to/screenshot.png
```
