# Gstack Design Tools — Telegram Mini App Reference

## Tool Availability Matrix

| Tool | Command | API Key Required | Works Without | Use Case |
|------|---------|------------------|---------------|----------|
| **design** | `design generate` / `design variants` | ✅ OpenAI | ❌ | AI mockup generation |
| **design-shotgun** | `design-shotgun` | ✅ OpenAI | ❌ | Multiple design variants |
| **design-consultation** | `/design-consultation` | ❌ | ✅ | Design system proposal + DESIGN.md |
| **design-html** | `/design-html` | ❌ | ✅ | HTML/CSS from description |
| **design-review** | `/design-review` | ❌ | ✅ | Visual audit of existing designs |
| **plan-design-review** | `/plan-design-review` | ❌ | ✅ | Design plan review |

## Recommended Path Without OpenAI API Key

### For New Projects (no existing design)
```
/design-consultation → Creates DESIGN.md with complete design system
    ↓
/design-html → Generates HTML/CSS from approved design system
    ↓
/design-review → Iterates and polishes
```

### For Existing Projects (want to improve design)
```
/design-review → Audits current design, finds issues
    ↓
/design-html → Generates improved HTML/CSS
    ↓
/design-review → Verifies improvements
```

## Design Consultation Workflow

The `/design-consultation` skill works without API key:

1. **Phase 1: Product Context** — Asks about product, users, space
2. **Phase 2: Research** (optional) — Competitive analysis via browse
3. **Phase 3: Complete Proposal** — Aesthetic, typography, color, spacing, motion
4. **Phase 4: Drill-downs** (if needed) — Adjust specific sections
5. **Phase 5: Preview** — Generates HTML preview page (no API key needed)

**Output:** `DESIGN.md` file + HTML preview page

## Design HTML Workflow

The `/design-html` skill generates production HTML/CSS:

**Input:** Design brief or approved mockup
**Output:** Single HTML file with inline CSS

**Features:**
- Pretext-native HTML/CSS
- Text reflows dynamically
- Heights computed automatically
- Layouts are dynamic
- 30KB overhead, zero deps

**When to use:**
- After `/design-consultation` approves a design system
- When converting a design description to actual code
- For Telegram Mini App prototypes

## Design Review Workflow

The `/design-review` skill audits existing designs:

**Modes:**
- **Full** (default) — All pages, 5-8 pages reviewed
- **Quick** — Homepage + 2 key pages
- **Deep** — 10-15 pages, exhaustive
- **Diff-aware** — Only pages affected by branch changes

**Output:**
- Design score (letter grade)
- AI slop score
- Per-page analysis
- Screenshots with annotations
- Recommended fixes

## Telegram Mini App Specific Design Considerations

### Theme Sync
Mini Apps receive Telegram's color theme in real time. Use `ThemeParams` to match dark/light mode. The `design-consultation` skill proposes both light and dark mode palettes.

### RTL/Persian Support
The `design-consultation` skill proposes RTL-aware typography and spacing. For Persian text:
- Font: Vazirmatn (web-safe) or IRANYekan (standard Iranian)
- Direction: `<html lang="fa" dir="rtl">`
- TailwindCSS: `rtl:` modifier

### Mobile-First
Mini Apps are always mobile (WebView on phones). The `design-consultation` skill proposes mobile-first layouts.

### Telegram Native Feel
The design should feel native to Telegram. The `design-consultation` skill considers:
- Telegram's color scheme
- Bottom navigation patterns
- Card-based layouts
- Minimal chrome

## Quick Wins Without API Key

1. **Run `/design-consultation`** — Get a complete design system proposal
2. **Create `DESIGN.md`** — Document the approved design system
3. **Run `/design-html`** — Generate HTML/CSS from the design system
4. **Run `/design-review`** — Audit and polish the result
5. **Iterate** — Repeat steps 3-4 until satisfied

### ⚠️ Don't Patch design-consultation SKILL.md

The `gstack-design-consultation` SKILL.md is **auto-generated** (`bun run gen:skill-docs`)
and exists in 10+ copies. Patching it is wasted work — changes get overwritten.
To add design workflow learnings, add pitfalls to `telegram-miniapp-development` SKILL.md
or reference files here instead.

## Design Consultation Interaction Pattern (No API Key)

When running `/design-consultation` without OpenAI, the interaction follows
this pattern (discovered in POS_MINIAPP session):

```
Phase 0: Pre-checks (no DESIGN.md? continue)
    ↓
Phase 1: Product Context — AskUserQuestion Q1:
    - Confirm product, users, space
    - Web app vs marketing site
    - Research competitors or use built-in knowledge?
    ↓
Phase 2: Research (if user said yes) — Browse top 3-5 competitor sites
    ↓
Phase 3: Complete Proposal — AskUserQuestion Q2:
    - Present AESTHETIC, COLOR, TYPOGRAPHY, LAYOUT, SPACING, MOTION, DECORATION
    - SAFE choices (category baseline) vs RISKS (departure from convention)
    - User picks: approve, change font, change color, change both
    ↓
Phase 4: Drill-downs (if user wants changes) — AskUserQuestion Q3+:
    - Font: 3-5 candidates with rationale
    - Color: 2-3 palette options with hex values
    - Each drill-down → re-check coherence with rest of system
    ↓
Phase 5: Create DESIGN.md + HTML preview
    ↓
Commit: git add DESIGN.md && git commit -m "docs: add DESIGN.md — [aesthetic] design system"
```

**Key:** Phase 3 proposal must be ONE coherent package, not separate questions
for font, color, layout. Present everything together so user sees how choices
reinforce each other.

**After DESIGN.md is created:** Apply the design system to the actual frontend:
1. Update `index.html` — add font import (e.g., Google Fonts link)
2. Update `globals.css` — CSS variables for colors, spacing
3. Verify — `tsc --noEmit` + screenshots
4. Commit — `style(design): apply DESIGN.md system`

## Reference Files

- [telegram-miniapp-tech-stack.md](telegram-miniapp-tech-stack.md) — Tech stack comparison
- [telegram-miniapp-realtime-storage.md](telegram-miniapp-realtime-storage.md) — SSE, storage, auth
