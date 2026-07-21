---
name: pptx-animation-generator
description: >-
  Generate PowerPoint (.pptx) files with full shape-level animations (Fade, Fly,
  Scale, Motion Path, Stagger, Pulse) by injecting OOXML animation XML into
  python-pptx via lxml. Covers the full pipeline: parsing source animation specs
  (React/framer-motion, GSAP, etc.), building an intermediate representation,
  mapping to OOXML equivalents, and emitting valid PowerPoint output with
  RTL/Persian support.
version: 3.0.0
author: Hermes Agent
license: MIT
---

# PPTX Animation Generator

## Overview

Two approaches exist for generating PowerPoint files with native shape-level
animations from code. This skill covers both:

### Approach A — Low-Level OOXML Injection (python-pptx + lxml)

python-pptx does **not** natively support shape-level animations (Fade In, Fly In,
Motion Paths, etc.). The battle-tested workaround: inject raw OOXML animation
elements into slide `<p:timing>` nodes using lxml.

**Use when:** you need full control over every animation parameter, offline
operation, or Python-native pipeline. Best for complex SVG motion paths,
custom coordinate animations, or when you want zero browser dependency.

**Core insight:** PowerPoint OOXML stores animations in `<p:timing> →
<p:tnLst> → <p:par> → <p:cTn> → <p:childTnLst>`. Each shape-level effect is
a `<p:set>`, `<p:anim>`, `<p:animEffect>`, `<p:animMotion>`, etc. inside that
tree. Inject this XML directly onto the slide element and PowerPoint renders
the animations.

### Approach B — dom-to-pptx (npm, browser-based, v2.0.3+)

**[dom-to-pptx](https://www.npmjs.com/package/dom-to-pptx)** is a mature
client-side library (~230k downloads/month) that converts HTML/CSS DOM elements
into fully editable PowerPoint slides. It maps CSS animation/transition classes
directly to native PowerPoint animation effects.

**Use when:** you have HTML/React/TSX slides, want the highest visual fidelity
with minimal code, or need 20+ animation types and 70+ slide transitions.
Animations are declared via CSS classes — no XML injection needed.

```bash
npm install dom-to-pptx
```

**Key features (v2.0.3+):**
- 20+ entrance/exit animation types: `fade-in`, `zoom-in`, `fly-in` `to-up/down/left/right`, `wipe-in`
- 70+ slide transitions via `.slide-transition-*` classes
- Stagger/sequencing with `animate-trigger-on-click`, `animate-trigger-with`, `animate-trigger-after`
- Character-by-character (`letter`) and paragraph-by-paragraph (`paragraph`) reveals
- Timing control: `animate-duration-[MS]`, `animate-delay-[MS]`
- Auto-font-embedding, gradient/shadow preservation, SVG-as-vector export
- Headless CLI: `npx dom-to-pptx-exporter slides.html --output out.pptx`

### Strategy Recommendation

For React/framer-motion → PowerPoint conversion jobs, use **both**:
1. **dom-to-pptx** for the main pipeline (render slides to HTML with animation CSS classes, export)
2. **OOXML injection** as a fallback for animations dom-to-pptx can't express (custom SVG motion paths, coordinate-based fly-in positions, off-axis rotations)

## Mandatory Phase Structure (User-Driven Workflow)

**CRITICAL RULE:** Do NOT skip phases. The user says "go to next phase" or equivalent. Until then stay in the current phase. Jumping ahead without permission wastes output and frustrates the user.

A user correction like "کی بهت گفت تو ی فاز انجام بدی" means you already skipped ahead. Stop immediately, return to the current phase, and complete it before even discussing the next one.

### Phase 1 — Deep Analysis: Exhaustive Animation Extraction

The user saying "بررسی کن" is NOT Phase 1 complete. They will say "عمیق تر تحلیل کن" until every animation is catalogued. The **completeness criteria** below define when Phase 1 is actually done:

1. **Inventory** every `.tsx` file in the slides directory. Check if all are imported in `slides.ts` — orphan `.tsx` files (present on disk, absent from slides.ts) should be noted as extras.
2. **Extract ALL** `<motion.*>` elements with full props (initial, animate, transition, variants, exit, whileHover, whileTap, style). Count them. Every slide needs a count.
3. **Classify** each effect into categories: fade, slide_h, slide_v, scale, svg_path, motion_path, loop, hover, tap, spring, keyframe, variants.
4. **Parse timing** from every `transition={}` block: delay, duration, ease, spring type, stiffness, repeat, times[], evt.
5. **Extract SVG diagrams** — viewBox, node coordinates, arrow markers, gradients, filters, template-literal path `d=""`.
6. **Extract stagger formulas** — every `delay: base + i*step` pattern, documented as `(base, step, count)`.
7. **Resolve custom timing constants** — `T_CACHE=0.6`, `T_REPLY=4.6`, `delayBase`, etc. to concrete values.
8. **Extract CSS keyframes** from stylesheets (`@keyframes` blocks), not just class names.
9. **Check for unused components** — `gsap` imports in `package.json` vs actual usage (GSAP is often unused in this project style).
10. **Document per-slide totals** and per-effect-type grand totals.
11. **Identify conversion challenges** specific to this project (3D rotations, SVG motion paths, spring physics, blur filters).

**Output:** A structured markdown file (`/workspace/phase1-analysis.md`) with:
- Slide data table (file, title, lines, anim count)
- Per-slide breakdown: every unique animation with its exact parameters
- SVG diagram coordinates and arrow definitions
- Stagger timing table
- Custom timing constants
- Conversion challenge list

Example of sufficient depth — the analysis should answer questions like:
- "اسلاید ۴ دقیقاً چندتا stagger داره و stepش چقدره؟"
- "کدوم اسلایدها offsetPath دارن و مسیرشون چیه؟"
- "تایمینگ T_REPLY چقدره و کجا استفاده شده؟"

PHASE 2 — Engine Build (only when user says "go")
  → Build the Python OOXML injector or dom-to-pptx renderer

PHASE 3 — Generation & Polish (only when user says "go")
  → Run engine, validate output, fix layout, test animations in PowerPoint
```

## Pipeline (Two-Track)

```
Source React/TSX Slides (framer-motion / GSAP)
  │
  ├── TRACK A (primary): dom-to-pptx
  │     Parse framer-motion props → CSS animation classes
  │     Render slides as HTML with 1920×1080 containers
  │     Export via domToPptx.exportToPptx() or headless CLI
  │     Result: .pptx with native PowerPoint animations
  │
  └── TRACK B (fallback): OOXML injection
        Phase 1 → Intermediate Representation: { shape_id, effect_type, params }
        Phase 2 → OOXML Generator: map IR to XML, inject into slide timing
        Phase 3 → python-pptx saves and verifies the file
```

### framer-motion to dom-to-pptx Mapping Reference

| framer-motion prop | dom-to-pptx CSS class | Notes |
|---|---|---|
| `initial={{opacity:0}} animate={{opacity:1}}` | `fade-in` | Simplest, most reliable |
| `initial={{y:-40}} animate={{y:0}}` | `fly-in to-up` | Negative y = fly in from top |
| `initial={{y:40}}` | `fly-in to-down` | Positive y = fly in from bottom |
| `initial={{x:-80}}` | `fly-in to-left` | Negative x = from left |
| `initial={{x:80}}` | `fly-in to-right` | Positive x = from right |
| `initial={{scale:0.8}}` | `zoom-in` | Scale entrance |
| `initial={{filter:"blur(8px)"}}` | `fade-in` (no blur equivalent) | PowerPoint has no native blur entrance |
| `staggerChildren: 0.15` | `animate-trigger-after` on each child | Chain them sequentially |
| `whileHover={{scale:1.06}}` | `animate-trigger-on-click` | Hover not supported; use click |
| `repeat: Infinity` | (loop via PowerPoint emphasis) | Use OOXML injection for p:cTn repeatCount |
| `spring stiffness: 200` | — | PowerPoint ease-out is closest |
| `duration: 0.6` | `animate-duration-[600]` | Value in milliseconds |
| `delay: 0.3` | `animate-delay-[300]` | Value in milliseconds |

## Prerequisites

```bash
pip install python-pptx lxml Pillow
```

- **python-pptx** ≥ 1.0.0 — slide/shape creation, text formatting, table/chart support
- **lxml** — XML injection into OOXML structure (always bundled with python-pptx)
- **Pillow** — image handling (bundled)

## Animation OOXML Quick Reference

| PowerPoint Effect | OOXML Element | Usage |
|---|---|---|
| Fade In | `<p:animEffect filter="fade" transition="in"/>` | Easiest, single element |
| Fly In (from bottom) | `<p:anim>` with `ppt_y` | Animate Y position |
| Fly In (from right) | `<p:anim>` with `ppt_x` | Animate X position |
| Grow / Scale | `<p:animScale>` | Zoom effect |
| Motion Path | `<p:animMotion>` with `<p:path>` | SVG path motion |
| Rotate | `<p:animRotate>` | Rotation |
| Color change | `<p:animColor>` | Color animation |
| Pulse / emphasis | `<p:animEffect filter="pulse"/>` | Loopable emphasis |
| Staggered | Multiple `<p:seq>` entries with delays | Sequenced children |

### OOXML Structure Template

**WARNING: Use flat `<p:par>` entries, NOT `<p:seq>` wrappers.**  
See Pitfalls section for why `<p:seq>` silently fails in PowerPoint.

```xml
<p:timing xmlns:p="..." xmlns:a="...">
  <p:tnLst>
    <p:par>                              <!-- Each animation is its own <p:par> -->
      <p:cTn id="10" dur="0.75" fill="hold">
        <p:stCondLst>
          <p:cond evt="after" delay="0.0"/>
        </p:stCondLst>
        <p:childTnLst>
          <!-- EFFECT NODE HERE -->
        </p:childTnLst>
      </p:cTn>
    </p:par>
    <p:par>                              <!-- Next animation (delayed) -->
      <p:cTn id="12" dur="0.5" fill="hold">
        <p:stCondLst>
          <p:cond evt="after" delay="0.3"/>
        </p:stCondLst>
        <p:childTnLst>
          <!-- ANOTHER EFFECT -->
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>
```

### Effect Node Examples

**Fade In (p:animEffect):**
```xml
<p:animEffect transition="in" filter="fade">
  <p:cBhvr>
    <p:cTn id="3" dur="0.75" fill="hold"/>
    <p:tgtEl><p:spTgt spid="2"/></p:tgtEl>
  </p:cBhvr>
</p:animEffect>
```

**Fly In (p:anim on ppt_y):**
```xml
<p:anim>
  <p:cBhvr>
    <p:cTn id="3" dur="0.8" fill="hold"/>
    <p:tgtEl><p:spTgt spid="2"/></p:tgtEl>
    <p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst>
  </p:cBhvr>
  <p:from><p:strVal val="#ppt_y.offset(0.5)"/></p:from>
  <p:to><p:strVal val="#ppt_y"/></p:to>
</p:anim>
```

**Motion Path:**
```xml
<p:animMotion origin="layout" pathEditMode="relative">
  <p:cBhvr>
    <p:cTn id="3" dur="2.0" fill="hold"/>
    <p:tgtEl><p:spTgt spid="2"/></p:tgtEl>
  </p:cBhvr>
  <p:path>
    <p:fillToRect l="0" t="0" r="0" b="0"/>
  </p:path>
</p:animMotion>
```

## Pipeline

```
Source Animation Specs (framer-motion, GSAP, etc.)
  → Parser: extract shape, type, params (delay, duration, repeat, stagger)
  → Intermediate Representation: { shape_id, effect_type, params }
  → OOXML Generator: map IR to XML, inject into slide timing
  → PPTX Output: python-pptx saves the file
```

### Key Rules

1. **Shape IDs are sequential (1-indexed):** `slide.shapes[0].shape_id` returns the OOXML spid. The first shape added is typically ID 2 (slide layout shapes take ID 1). Print shape_id to be sure.

2. **p:cTn IDs must be unique per slide:** Use a counter starting from 10 to avoid collisions with root (1).

3. **`dur` is in seconds** (ISO 8601 duration or simple decimal; Python uses float then converted to string).

4. **`evt="onClick"`** is default trigger. Use `delay="0.5"` for auto-after-previous.

5. **Staggered animations** = multiple `<p:cTn>` entries inside the `<p:seq>`, each with increasing `delay="0"` but offset by the sequence position.

6. **Farsi/Persian/RTL text:** Set `pPr.rtl=1` and `bodyPr.rtlCol=1` on the text body elements. python-pptx handles this if you set text on the paragraph and shape-level paragraph alignment PP_ALIGN.RIGHT.

7. **Slide transitions** use `<p:transition>` element on the slide, NOT inside timing. python-pptx supports this with XML injection too.

## 🏗 Practical Patterns

### AnimTracker — Unified Shape + Animation Registration

Instead of creating shapes and then calling separate `add_fade_in`/`add_fly_in`/etc., use a tracker
that wraps creation and animation declaration in one call:

```python
tr = AnimTracker(slide)
card = add_card(slide, Inches(1), Inches(1), Inches(3), Inches(0.5), 'متن')
tr.add(card, 0.2, 0.5, 'fly', 'up')           # Fly in from up with 0.2s delay
tr.add(card, 0.4, 0.5, 'fade')                 # Fade in
tr.add(card, 0.6, 0.6, 'scale')                # Scale in
tr.add(card, 0.8, 2.0, 'pulse')                # Loop emphasis
tr.add(card, 1.0, 0.5, 'none')                 # No animation (connectors/lines)
```

Supported anim types: `'fade'`, `'fly'`, `'scale'`, `'pulse'`, `'none'`.

### Phase 3 Effect Injectors (Advanced)

Built on top of Phase 2's core injectors, these handle patterns that framer-motion
expresses but OOXML lacks a direct equivalent for:

| Injector | OOXML element | framer-motion target | Caveat |
|---|---|---|---|
| `add_keyframe_opacity` | Multiple `p:animEffect` seq entries | `opacity: [0,1,0]` + `times: [0,0.3,0.8,1]` | Each keyframe point becomes a separate seq entry; approximate timing |
| `add_bounce_scale` | `p:animScale` + `calcMode="spline"` | `type: "spring"` with `stiffness: 200` | Bounce is approximated; no true spring OOXML |
| `add_glow_filter` | `a:glow` + `a:softEdge` on `spPr/a:effectLst` | SVG `feGaussianBlur` filter | Static glow on shape, not animated |
| `add_shape_gradient` | `a:gradFill/a:lin` with `a:gsLst` | SVG `linearGradient`/`radialGradient` | Static gradient; no animated color transitions |

**Animation Mapping Status (framer-motion → OOXML):**

| Pattern | Status | Strategy |
|---|---|---|
| Fade (`opacity: 0→1`) | ✅ Direct | `p:animEffect filter="fade"` |
| Fly (`y: N→0`, `x: N→0`) | ✅ Direct | `p:anim` on `ppt_y`/`ppt_x` |
| Scale (`scale: 0.8→1`) | ✅ Direct | `p:animScale from=0.3 to=1.0` |
| Stagger (`delay: i*step`) | ✅ Direct | N seq entries with `evt=after delay=step*i` |
| Loop (`repeat: Infinity`) | ✅ Emphasis | `p:animEffect filter="pulse"` + `repeatCount="indefinite"` |
| Motion Path (`offsetDistance: 0→100%`) | ⚠️ Lossy | `p:animMotion` with SVG path (complex curves degrade) |
| Keyframe + times[] | ⚠️ Approx | N seq entries with staggered delays (no true `tmPct`) |
| Spring physics | ⚠️ Approx | `calcMode="spline"` easy-out, no bounce |
| Glow filter (SVG feGaussianBlur) | ⚠️ Static | `a:glow` on spPr effect list, not animatable |
| Gradient fills | ⚠️ Static | `a:gradFill` on spPr, not animatable |
| SVG path draw (`pathLength: 0→1`) | ❌ | No OOXML equivalent; use fade-in approximation |
| `filter: blur(8px)` | ❌ | No PPTX equivalent; replace with fade-in |
| `whileHover` / `whileTap` | ❌ | Not supported; use `onClick` trigger |
| 3D rotateX / rotateY | ❌ | No 3D rotation in OOXML animation |

### SVG Diagram Approximation with pptx Shapes

Converting complex SVG diagrams (node-link networks, fiber paths, broadcast waves)
to exact OOXML shapes is often impractical. Approximate with pptx-native shapes:

```python
# Router nodes → Cards (rounded rect)
add_card(slide, Inches(x), Inches(y), Inches(0.7), Inches(0.5), 'A', ...)
# Sensor nodes → Ovals
add_oval(slide, Inches(x), Inches(y), Inches(0.5), Inches(0.5), C_GREEN, C_GREEN)
# Links → Connector lines (with optional arrowheads)
add_line(slide, Inches(x1), Inches(y1), Inches(x2), Inches(y2), color, width)
add_arrow_line(slide, Inches(x1), Inches(y1), Inches(x2), Inches(y2), color, width)
# EM waves / pulse rings → Pulse emphasis animation on ovals
tr.add(oval, 0.5, 2.0, 'pulse')  # repeatCount="indefinite"
```

Trade-off: animation timing fidelity is preserved across all PPTX viewers, but exact
path curves and gradients may differ from the original SVG.

### Slide Count Mismatch Debugging

When the source has N slides in `slides.ts` but the generated PPTX has N+1 or N-1:

1. Check for **orphan child slides** — `.tsx` files in the slides/ directory that
   are NOT imported in slides.ts (e.g. `Slide07SensorRFID.tsx` exists but isn't
   in the array).
2. Check **blank layout** — `prs.slide_layouts[6]` (blank) may still carry template
   elements. Verify with `len(slide.shapes)`.
3. Validate: `len(prs.slides) == len(slides_array)`.
4. If extra, investigate with per-slide shape count before deleting.

## Pitfalls / Gotchas

### 🚨 Critical: `parse_xml` namespace trap

**Never build OOXML animation fragments with `parse_xml` (string -> XML).** The
pptx.oxml.parser uses a restricted namespace dictionary — elements like
`<p:cTn>` inside a standalone XML string will fail with:
```
XMLSyntaxError: Namespace prefix p on cTn is not defined
```
Because the fragment string lacks the `xmlns:p` declaration, and python-pptx's
internal parser does **not** inherit namespace context from parent elements.

> **CONFIRMED on python-pptx 1.0.2, lxml 6.1.1 in a production session.** All
> three effect injectors (fade, fly, scale) hit this initially. One hour of
> debugging traced to this single root cause.

**Fix:** Build animation XML programmatically with `lxml.etree.SubElement()`,
passing the namespace explicitly on every element:

```python
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

def _sub(parent, tag, attrib=None):
    return etree.SubElement(parent, f'{{{P}}}{tag}', attrib=attrib or {})

# Inside an existing slide._element.p:timing tree:
seq = _get_or_create_seq(timing)
cTn = _sub(seq, 'cTn', {'id': '42', 'dur': '1.5', 'fill': 'hold'})
stCondLst = _sub(cTn, 'stCondLst')
_sub(stCondLst, 'cond', {'evt': 'after', 'delay': '0.3'})
childTnLst = _sub(cTn, 'childTnLst')
animEffect = etree.SubElement(childTnLst, f'{{{P}}}animEffect',
                               {'transition': 'in', 'filter': 'fade'})
cBhvr = _sub(animEffect, 'cBhvr')
_sub(cBhvr, 'cTn', {'id': '43', 'dur': '1.5', 'fill': 'hold'})
tgtEl = _sub(cBhvr, 'tgtEl')
_sub(tgtEl, 'spTgt', {'spid': str(shape_id)})
```

**Why this works:** `etree.SubElement` appends directly into the existing element
tree that already has the `p:` namespace bound — no string round-trip, no
namespace re-declaration needed.

### 🚨 Critical: `p:seq` animation structure DOES NOT WORK in PowerPoint

**Never wrap individual effects inside `<p:seq>`.** PowerPoint Desktop silently
skips `p:seq` entries during slideshow — the `<p:cTn>` wrappers under `<p:seq>`
have no effect. The user will see the shape but no animation plays.

**Fix:** Use flat `<p:par>` entries directly under `<p:tnLst>`, one per effect.
Every animation is an independent `<p:par>` → `<p:cTn>` → `<p:childTnLst>` → effect:

```xml
<p:timing>
  <p:tnLst>
    <p:par>                        <!-- Effect 1 -->
      <p:cTn id="10" dur="0.75" fill="hold">
        <p:stCondLst>
          <p:cond evt="after" delay="0.0"/>
        </p:stCondLst>
        <p:childTnLst>
          <p:animEffect transition="in" filter="fade">
            <p:cBhvr>
              <p:cTn id="11" dur="0.75" fill="hold"/>
              <p:tgtEl><p:spTgt spid="2"/></p:tgtEl>
            </p:cBhvr>
          </p:animEffect>
        </p:childTnLst>
      </p:cTn>
    </p:par>
    <p:par>                        <!-- Effect 2 (delayed) -->
      <p:cTn id="12" dur="0.5" fill="hold">
        <p:stCondLst>
          <p:cond evt="after" delay="0.3"/>
        </p:stCondLst>
        <p:childTnLst>
          <!-- different shape, different effect -->
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>
```

**CONFIRMED:** A 19-slide, 171-animation deck was built with this structure after
the first pass (using `p:seq`) yielded "انیمیشن نداره اصلا" from the user.
Switching to flat `p:par` fixed every animation.

**The canonical Python implementation:**

```python
def inject_timing(slide_element):
    """Ensure slide has a timing element."""
    timing = slide_element.find(f'{{{P}}}timing')
    if timing is not None:
        return timing
    timing = etree.Element(f'{{{P}}}timing')
    _sub(timing, 'tnLst')                     # <p:tnLst> child only
    slide_element.append(timing)
    return timing

def _add_par_effect(timing, duration, delay, trigger='after'):
    """Add one <p:par> → <p:cTn> → <p:childTnLst>, return (childTnLst, bhv_id)."""
    tnLst = timing.find(f'{{{P}}}tnLst')
    if tnLst is None: tnLst = _sub(timing, 'tnLst')
    par = _sub(tnLst, 'par')
    evt = 'onClick' if trigger == 'onClick' else 'after'
    cTn = _sub(par, 'cTn', {
        'id': str(nid()), 'dur': str(duration), 'fill': 'hold'})
    _sub(_sub(cTn, 'stCondLst'), 'cond', {'evt': evt, 'delay': str(delay)})
    bhv_id = nid()
    return _sub(cTn, 'childTnLst'), bhv_id

def _add_par_loop(timing, duration, delay):
    """Same as _add_par_effect but with repeatCount='indefinite'."""
    tnLst = timing.find(f'{{{P}}}tnLst')
    if tnLst is None: tnLst = _sub(timing, 'tnLst')
    par = _sub(tnLst, 'par')
    cTn = _sub(par, 'cTn', {'id': str(nid()), 'dur': str(duration),
                              'fill': 'hold', 'repeatCount': 'indefinite'})
    _sub(_sub(cTn, 'stCondLst'), 'cond', {'evt': 'after', 'delay': str(delay)})
    return _sub(cTn, 'childTnLst'), nid()

def _cBhvr(childTnLst, shape_id, bhv_id, duration):
    """Append <p:cBhvr> to the LAST element in childTnLst, targeting the shape."""
    ae_elem = childTnLst[-1]
    cb = _sub(ae_elem, 'cBhvr')
    _sub(cb, 'cTn', {'id': str(bhv_id), 'dur': str(duration), 'fill': 'hold'})
    _sub(_sub(cb, 'tgtEl'), 'spTgt', {'spid': str(shape_id)})

def add_fade_in(slide, shape, delay=0.0, duration=0.75, trigger='after'):
    timing = inject_timing(slide._element)
    childTnLst, bhv_id = _add_par_effect(timing, duration, delay, trigger)
    ae = etree.SubElement(childTnLst, f'{{{P}}}animEffect',
                           {'transition': 'in', 'filter': 'fade'})
    _cBhvr(childTnLst, shape.shape_id, bhv_id, duration)
```

**How to verify animations are properly injected, not skipped:**

```python
from pptx import Presentation
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
prs = Presentation('my_output.pptx')
for i, slide in enumerate(prs.slides):
    timing = slide._element.find(f'{{{P}}}timing')
    if timing is not None:
        # Count <p:par> entries directly under <p:tnLst>
        pars = len(timing.findall(f'{{{P}}}tnLst/{{{P}}}par'))
        effects = (len(timing.findall(f'.//{{{P}}}animEffect'))
                   + len(timing.findall(f'.//{{{P}}}anim'))
                   + len(timing.findall(f'.//{{{P}}}animScale'))
                   + len(timing.findall(f'.//{{{P}}}animMotion')))
        # If there are <p:seq> elements, the animations will NOT play
        seqs = len(timing.findall(f'.//{{{P}}}seq'))
        print(f"S{i+1}: {pars} pars, {effects} effects, {'🔴 HAS SEQ!' if seqs > 0 else '✅ flat'}")

    else:
        print(f"S{i+1}: ❌ NO TIMING")
```

### Other Pitfalls

- **Phase-jumping is the No.1 user frustration.** The user will say when to move forward. Do NOT write engine code before the analysis is accepted. A user correction like "کی بهت گفت تو ی فاز انجام بدی" means you skipped ahead. Stop and go back to complete the current phase.
- **Shape ID targeting:** Always verify `shape_id` matches what PowerPoint expects. Shapes inside groups have nested IDs.
- **Animation preview:** PowerPoint Desktop shows all effects. PowerPoint Online / Web may not render complex animations (especially Motion Paths).
- **`ppt_x` vs `style.opacity`:** For position animation use `ppt_x`/`ppt_y`; for opacity/fade use `p:animEffect`, NOT `style.opacity`.
- **Stagger timing:** Setting `delay` on `<p:cond>` inside a sequence achieves stagger; do NOT set it on the outer `<p:seq>` timing node.
- **Repeat count:** Use `<p:cTn repeatCount="indefinite"` for loops, but PowerPoint may limit this in slideshow mode.
- **Infinite loops:** `repeatCount="indefinite"` works for emphasis animations but may behave unpredictably for entrance effects.
- **`filter: blur` has no PowerPoint equivalent.` framer-motion `filter: "blur(8px)"` (common in title reveals) cannot map to a native PowerPoint animation. Replace with `fade-in` on the same timing. Document this trade-off when the user expects blur.
- **Spring physics has no PPTX counterpart.** framer-motion `type: "spring"` / `stiffness: 200` maps to PowerPoint built-in ease-out curve. No bounce or spring emulation in OOXML.
- **SVG motion-path conversion is lossy.** framer-motion `offsetPath`/`pathLength` (common in network diagrams) maps to `<p:animMotion>` but bezier curves lose fidelity across PowerPoint versions. For paths with 3+ control points, rasterise the SVG and animate position + scale instead.
- **offsetPath lives in `style={}` not `animate={}` in framer-motion.** When extracting motion-path data, search the `style` prop, NOT `animate`. Common extraction trap.
- **SVG template literals are in backticks, not strings.** Extract with `re.findall(r'd=\s*`([^`]+)`', code)`. Plain string patterns miss these.
- **Keyframe arrays with `times: [x, y, z]` need per-element OOXML handling.** Each keyframe point becomes a separate `<p:cTn>` with `tmPct` for the time fraction.
- **Custom timing constants** (like T_CACHE=0.6, T_REPLY=4.6) must be resolved to concrete values at extraction time.
- **Empty slide shells count as slides.** When user has 18 source slides but `len(prs.slides)` returns 19, an extra slide was created. Investigate before deleting.
- **RTL shapes and slide dimensions:** ppt_x/ppt_y offsets are absolute in the coordinate system — they do NOT mirror for RTL slides. A `to-left` fly-in on an RTL deck still enters from viewer-left. Build animation positions manually if RTL-mirrored behaviour is expected.

## Verification

After generating a .pptx, test with:

```python
from pptx import Presentation
prs = Presentation("/tmp/output.pptx")
for i, slide in enumerate(prs.slides):
    timing = slide._element.find(
        '{http://schemas.openxmlformats.org/presentationml/2006/main}timing'
    )
    has_anim = timing is not None
    print(f"Slide {i+1}: {len(slide.shapes)} shapes, timing={has_anim}")
print(f"Total slides: {len(prs.slides)}")
```

## References

- `references/ooxml-animation-elements.md` — Complete OOXML animation element reference
- `references/additional-research.md` — Research notes on third-party tools (dom-to-pptx, GitHub repos, key findings)
- `references/framer-motion-extraction.md` — Regex patterns and methodology for extracting framer-motion animation parameters from TSX source code (stagger formulas, SVG coordinates, offsetPath, keyframe times, CSS keyframes)
- `references/production-pipeline.md` — Full session reference: engine architecture, animation mapping decisions, what was deferred
- `scripts/animation-builder.py` — Standalone reference implementation with self-test (run with `python3 scripts/animation-builder.py`)
