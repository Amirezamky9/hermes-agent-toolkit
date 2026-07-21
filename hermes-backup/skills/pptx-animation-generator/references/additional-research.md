# Additional Tools & Repositories — PPTX Animation Generation Research

Collected 2026-07-13 during a React/framer-motion → PowerPoint conversion task
for a Persian-language networking-presentation project (18 slides).

## 📦 npm Packages

### dom-to-pptx (v2.0.3) — ⭐ Recommended for HTML/React → PPTX

- **npm:** https://www.npmjs.com/package/dom-to-pptx
- **Usage:** ~230k downloads/month. Client-side library that converts DOM elements
  to editable .pptx slides. Maps CSS animation classes to native PowerPoint effects.
- **Animation support (v2+):** 20+ entrance/exit types (fade-in, fly-in to-up/down/left/right,
  zoom-in, wipe-in), 70+ slide transitions, stagger/sequencing via
  `animate-trigger-after/with/on-click`, character/paragraph reveals.
- **CLI (headless):** `npx dom-to-pptx-exporter slides.html --output out.pptx`
- **Key strength:** High visual fidelity — preserves gradients, shadows, SVG-as-vector,
  auto-font-embedding. Best first choice for React → PPTX pipelines.
- **Limitations:** Runs in browser (Puppeteer/Playwright for headless). No direct
  coordinate-based fly-in or custom SVG motion-path animation — use OOXML fallback.

### pptx-automizer (v0.8.2)

- **npm:** https://www.npmjs.com/package/pptx-automizer
- **Usage:** Template-based .pptx generator for Node.js. Wraps PptxGenJS.
  Best for merging existing .pptx templates, not for greenfield animation generation.

## 🐍 Python-Path GitHub Repos

### krzem5/Python-Powerpoint_Animation_Generator (3 stars)

- **URL:** https://github.com/krzem5/Python-Powerpoint_Animation_Generator
- **Stack:** Python, JSON-driven
- **Supported:** Motion, Rotation, Scale animations via OOXML injection
- **Input:** JSON file with object definitions + animation commands
- **Notable:** Good reference for OOXML animation structure, especially
  acceleration/deceleration (ease-in/ease-out) as percentages. Uses
  percentage-based coordinate system (`20%+80` for slide-relative positioning).
- **Weakness:** Image-only objects (no text boxes), no text animation.

### ptrw0311/tsx_convert_pptx (0 stars)

- **URL:** https://github.com/ptrw0311/tsx_convert_pptx
- **Stack:** TypeScript, Tailwind CSS parser
- **Purpose:** Converts React TSX slide components to PowerPoint, preserving
  Tailwind classes as PPTX styles.
- **Limitation:** No animation support detected; layout-only conversion.
  But useful reference for TSX-to-PPTX text/style parsing strategy.

### Zaki-kek/pptx-recolor (0 stars)

- **URL:** https://github.com/Zaki-kek/pptx-recolor
- **Purpose:** Recolor and localize PowerPoint decks at OOXML level.
- **Relevance:** OOXML manipulation reference, but not animation-specific.

## 💡 Key Findings

1. **No library covers all framer-motion → PowerPoint animations natively.**
   A dual-track approach (dom-to-pptx for standard animations + OOXML injection
   for custom path/cordinate animations) is the right architecture.

2. **dom-to-pptx v2.0.3+ is the most mature option** for standard conversion.
   Its CSS-class-based animation system maps well to framer-motion's declarative
   style. 230k downloads/month indicates active maintenance.

3. **OOXML injection is the universal fallback.** The `p:timing` → `p:tnLst` →
   `p:par` → `p:cTn` → `p:childTnLst` → `p:anim*/p:set*` structure is standard
   across all PowerPoint versions (2007+).

4. **No existing repo handles Persian/RTL + animations.** pptx-animation-generator
   is the only skill that covers this combination.
