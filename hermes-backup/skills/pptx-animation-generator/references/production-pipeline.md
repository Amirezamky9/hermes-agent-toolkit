# Production Pipeline — Session Reference (2026-07-13)

## Source Project

**Networked_Insights** — Persian-language academic presentation on Computer Networks
(18 slides + 1 orphan). Built with Lovable (React 19, TanStack Start, framer-motion, GSAP).
Source: `/workspace/Networked_Insights__2_/`

## Conversion Approach Used

This session used **Track B (OOXML injection)** exclusively:
- python-pptx 1.0.2 + lxml 6.1.1
- No browser/dom-to-pptx (was considered but not needed for the initial pass)
- Dark theme matching the source `styles.css` colors
- All text in Persian (RTL) with Vazirmatn/Estedad font specification

## Architecture Evolution

### Phase 2 Engine (First Attempt — Failed)

The first engine wrapped every animation inside `<p:seq>` elements nested under a
single root `<p:par>`. This structure is **silently skipped by PowerPoint Desktop**
— shapes appear but no animation plays. User reported "انیمیشن نداره اصلا" (zero
animations).

**Root cause:** `p:seq` is designed for interactive sequencing (click-once-play-all),
not entrance effects. Individual `<p:cTn>` wrappers inside a `<p:seq>` are not
applied as entrance animations by the PPTX renderer.

### Phase 3 Engine (Fixed — Working)

The fix: use **flat `<p:par>` entries directly under `<p:tnLst>`** — one per effect,
each completely independent. No root cTn with `dur="indefinite"`, no `<p:seq>`,
no nesting. Every animation is its own parallel branch.

```xml
<p:timing>
  <p:tnLst>
    <p:par>         <!-- Effect 1: fade -->
    <p:par>         <!-- Effect 2: fly -->
    <p:par>         <!-- Effect 3: scale -->
  </p:tnLst>
</p:timing>
```

### The Fix in Code

Old core: `inject_timing` (with root cTn + childTnLst) → `_get_or_create_seq`
→ `_build_cTn_wrapper` → effect.

Fixed core: `inject_timing` (tnLst only, NO root cTn) → `_add_par_effect`
(fresh `<p:par>`/`<p:cTn>`/`<p:childTnLst>`) → effect → `_cBhvr`.

A 1-slide test with the flat par structure was built and verified BEFORE applying
the fix to the full 19-slide engine. Always test first.

## Key Files

| File | Lines | Purpose |
|---|---|---|
| `/workspace/phase1-analysis.md` | ~950 | Full deep analysis from Fase 1 |
| `/workspace/pptx_engine_v2.py` | ~1000 | Production engine (flat par-based, 171 anims) |
| `/workspace/Networked_Insights.pptx` | — | Final output (19 slides, 171 animations, 70 KB) |
| `/workspace/pptx_animation_engine.py` | 1123 | First-attempt engine (seq-based, kept for reference) |

## Engine Architecture (pptx_engine_v2.py)

```
Constants (color palette, dimensions)
  → XML Helpers (_sub, _sub_a, nid)
  → Shape Helpers (add_textbox, add_card, add_oval, add_line, add_arrow_line, add_round_kicker)
  → Animation Core (inject_timing, _add_par_effect, _add_par_loop, _cBhvr)
  → Effect Injectors (add_fade_in, add_fly_in, add_scale_in, add_pulse_emphasis,
     add_motion_path, add_keyframe_opacity, add_bounce_scale, add_glow_filter)
  → AnimTracker (per-slide shape + animation registration)
  → Slide Builders (slide_01_title through slide_08_summary — 19 functions)
  → Generator (generate_pptx — orchestrates all slides)
```

### AnimTracker Pattern

Every slide function instantiates `AnimTracker(slide)`, then calls
`tr.add(shape, delay, duration, anim_type, direction)` for every shape.
The tracker resets `_anim_counter = [20]` per slide to prevent `p:cTn` ID collisions.

## Phase 3 Injectors Added

| Injector | OOXML element | Target |
|---|---|---|
| `add_motion_path()` | `p:animMotion` + optional `repeatCount="indefinite"` | Light dots in Fiber, ARP |
| `add_keyframe_opacity()` | Multiple `p:par` entries with staggered delays | EM waves in RFID |
| `add_bounce_scale()` | `p:animScale` with spring-like timing | ARP badge |
| `add_glow_filter()` | `a:glow` + `a:softEdge` on shape spPr | Packet switching nodes |

## Animation Mapping (Complete)

| framer-motion | OOXML equivalent | Status |
|---|---|---|
| `opacity: 0→1` | `p:animEffect filter="fade"` | ✅ Direct |
| `y: -40→0` | `p:anim ppt_y offset(-0.4)` | ✅ Direct |
| `y: 24→0` | `p:anim ppt_y offset(0.4)` | ✅ Direct |
| `x: -20→0` | `p:anim ppt_x offset(-0.3)` | ✅ Direct |
| `scale: 0.8→1` | `p:animScale from=0.3 to=1.0` | ✅ Direct |
| `repeat: Infinity` | `repeatCount="indefinite"` on pulse | ✅ Emphasis loop |
| `offsetDistance: 0→100%` | `p:animMotion` (path-based) | ⚠️ Lossy for beziers |
| `opacity: [0,1,0]` + `times: [0,0.3,0.8,1]` | N `p:par` staggered seq entries | ⚠️ Approximate |
| `type: "spring"` | `calcMode="spline"` ease-out | ⚠️ Approximate |
| SVG glow (feGaussianBlur) | `a:glow` on spPr | ⚠️ Static only |
| SVG gradient | `a:gradFill` on spPr | ⚠️ Static only |
| `pathLength: 0→1` / `filter: blur` | No OOXML | ❌ Not supported |
| `whileHover` / `whileTap` | No OOXML | ❌ Not supported |
| `rotateX` / `rotateY` (3D) | No OOXML | ❌ Not supported |

## Animation Stats per Slide (Final)

| Slide | Shapes | Anims | Features |
|---|---|---|---|
| S01 Title | 6 | 6 | fade, fly, scale |
| S02 Fiber | 8 | 6 | **motion_path x3** |
| S03 Fiber Modes | 6 | 3 | fade |
| S04 ARP | 11 | 9 | **motion_path x3**, bounce scale |
| S05 ARP Steps | 14 | 9 | scale stagger |
| S06 App Layer | 12 | 11 | fly stagger |
| S07 DNS Why | 11 | 10 | scale, fade |
| S08 DNS | 19 | 9 | scale stagger |
| S09 Error Intro | 12 | 8 | fade, fly |
| S10 Error Timer | 12 | 7 | scale, fade |
| S11 Error Control | 14 | 7 | fade |
| S12 Datagram | 13 | 8 | fly stagger |
| S13 Packet Switching | 15 | 8 | **glow x2**, scale |
| S14 Routing | 18 | 11 | fly, fade |
| S15 RFID | 18 | 17 | **keyframe x3**, fly, fade |
| S16 Sensor | 24 | 14 | **pulse x4**, scale |
| S17 Multi-hop | 17 | 8 | fade stagger |
| S18 Sensor+RFID | 24 | 18 | fly, scale, fade |
| S19 Summary | 9 | 8 | fly stagger, scale |
| **Total** | **263** | **171** | |

## Verification

```python
from pptx import Presentation
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
prs = Presentation('output.pptx')
for i, slide in enumerate(prs.slides):
    timing = slide._element.find(f'{{{P}}}timing')
    if timing is None: print(f"S{i+1}: ❌ NO TIMING"); continue
    pars = len(timing.findall(f'{{{P}}}tnLst/{{{P}}}par'))
    seqs = len(timing.findall(f'.//{{{P}}}seq'))
    effects = (len(timing.findall(f'.//{{{P}}}animEffect'))
               + len(timing.findall(f'.//{{{P}}}anim'))
               + len(timing.findall(f'.//{{{P}}}animScale'))
               + len(timing.findall(f'.//{{{P}}}animMotion')))
    flag = '🔴 HAS SEQ!' if seqs > 0 else '✅'
    print(f"S{i+1}: {pars} pars, {effects} effects {flag}")
```

## Lessons Learned

1. **Never use `<p:seq>` for entrance animations.** Flat `<p:par>` entries only.
2. **Test 1 slide before building all 19.** A single-slide test PPTX with the target
   animation structure catches structural issues instantly.
3. **User-level signal "انیمیشن نداره" means 0 animations play.** Check for `<p:seq>`
   in the XML — if present, that's the root cause. Replace with flat `<p:par>`.
4. **Motion paths work** but degrade for complex bezier curves. Linear and simple
   quadratic paths (light dots, network pulses) work acceptably.
5. **Pulse emphasis** with `repeatCount="indefinite"` works in slideshow for loops.
