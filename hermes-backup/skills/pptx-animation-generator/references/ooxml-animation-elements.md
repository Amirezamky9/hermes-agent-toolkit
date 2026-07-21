# OOXML Animation Elements — Complete Reference

Discovered during python-pptx animation injection research on a React/framer-motion → PowerPoint conversion task.

## Namespaces

```xml
p  = "http://schemas.openxmlformats.org/presentationml/2006/main"
a  = "http://schemas.openxmlformats.org/drawingml/2006/main"
p14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
```

## OOXML Animation Tree Structure

```
p:timing                  ← appended to <p:sld> element
  p:tnLst                 ← time node list (CT_TimeNodeList)
    p:par                 ← parallel time node
      p:cTn               ← common time node (id=1, dur="indefinite", nodeType="tmRoot")
        p:childTnLst
          p:seq           ← sequence (concurrent="0", nextAc="seek")
            p:cTn         ← sequence timing (id=2+, dur="1.5", fill="hold")
              p:stCondLst
                p:cond    ← start condition (evt="onClick"|"after", delay="0")
              p:childTnLst
                p:anim            ← animate property
                p:animEffect      ← preset effect (fade, grow, pulse, etc.)
                p:animMotion      ← motion path
                p:animRotate      ← rotation
                p:animScale       ← scale/zoom
                p:animColor       ← color animation
                p:set             ← set property (simpler than anim)
```

## Effect Nodes in Detail

### 1. `<p:animEffect>` — Preset Effects (Fade, Pulse, etc.)

Simplest approach. PowerPoint handles the interpolation.

```xml
<p:animEffect transition="in" filter="fade" scale="large">
  <p:cBhvr>
    <p:cTn id="3" dur="0.75" fill="hold"/>
    <p:tgtEl>
      <p:spTgt spid="2"/>
    </p:tgtEl>
  </p:cBhvr>
</p:animEffect>
```

| Attribute `filter` | Effect |
|---|---|
| `fade` | Fade In / Out |
| `dissolve` | Dissolve |
| `grow` | Grow / Shrink |
| `pulse` | Pulse emphasis |
| `growAndSpin` | Grow + Spin |
| `spin` | Spin |
| `lighten` | Lighten |
| `darken` | Darken |
| `desaturate` | Desaturate |

| `transition` | Direction |
|---|---|
| `in` | Entrance |
| `out` | Exit |
| `none` | Emphasis |

### 2. `<p:anim>` — Custom Property Animation

For Fly In animations (position-based).

```xml
<p:anim>
  <p:cBhvr>
    <p:cTn id="3" dur="0.8" fill="hold"/>
    <p:tgtEl>
      <p:spTgt spid="2"/>
    </p:tgtEl>
    <p:attrNameLst>
      <p:attrName>ppt_y</p:attrName>
    </p:attrNameLst>
  </p:cBhvr>
  <p:from>
    <p:strVal val="#ppt_y.offset(0.5)"/>
  </p:from>
  <p:to>
    <p:strVal val="#ppt_y"/>
  </p:to>
</p:anim>
```

**Attribute names:**

| `p:attrName` | Animates |
|---|---|
| `ppt_x` | Horizontal position (0 = left, 1 = right edge) |
| `ppt_y` | Vertical position (0 = top, 0.5 = half slide) |
| `ppt_w` | Width |
| `ppt_h` | Height |
| `ppt_r` | Rotation (degrees) |
| `style.opacity` | Opacity (0.0–1.0) |

**Offset values:**
- `#ppt_y.offset(0.5)` — start half slide height below final position
- `#ppt_x.offset(-0.3)` — start 30% slide width left of final
- `#ppt_x.offset(0.5)` — start 50% slide width right of final

### 3. `<p:animMotion>` — Motion Path

```xml
<p:animMotion origin="layout" pathEditMode="relative">
  <p:cBhvr>
    <p:cTn id="3" dur="2.0" fill="hold"/>
    <p:tgtEl>
      <p:spTgt spid="2"/>
    </p:tgtEl>
  </p:cBhvr>
  <p:path>
    <p:fillToRect l="0" t="0" r="0" b="0"/>
  </p:path>
</p:animMotion>
```

The path is stored in the `<p:cTn>` as a `path` attribute or via `<a:path>` inside. For simple paths, editable from PowerPoint UI.

### 4. `<p:animScale>` — Scale / Zoom

```xml
<p:animScale zoomContent="0">
  <p:cBhvr>
    <p:cTn id="3" dur="1.0" fill="hold"/>
    <p:tgtEl>
      <p:spTgt spid="2"/>
    </p:tgtEl>
  </p:cBhvr>
  <p:from>
    <p:nVal val="0.1"/>
    <p:nVal val="0.1"/>
  </p:from>
  <p:to>
    <p:nVal val="1.0"/>
    <p:nVal val="1.0"/>
  </p:to>
</p:animScale>
```

### 5. `<p:set>` — Simple Property Setter

Good for toggling visibility or setting final values.

```xml
<p:set>
  <p:cBhvr>
    <p:cTn id="3" dur="0.01" fill="hold"/>
    <p:tgtEl>
      <p:spTgt spid="2"/>
    </p:tgtEl>
    <p:attrNameLst>
      <p:attrName>hidden</p:attrName>
    </p:attrNameLst>
  </p:cBhvr>
  <p:to>
    <p:strVal val="false"/>
  </p:to>
</p:set>
```

## Staggered (Stagger) Animation Pattern

Multiple effects in sequence, each with increasing delay:

```xml
<p:seq concurrent="0" nextAc="seek">
  <!-- Effect 1 — delay 0s -->
  <p:cTn id="10" dur="0.5" fill="hold">
    <p:stCondLst>
      <p:cond evt="onClick" delay="0"/>
    </p:stCondLst>
    <p:childTnLst>
      <p:animEffect transition="in" filter="fade">
        <p:cBhvr>
          <p:cTn id="11" dur="0.5" fill="hold"/>
          <p:tgtEl><p:spTgt spid="2"/></p:tgtEl>
        </p:cBhvr>
      </p:animEffect>
    </p:childTnLst>
  </p:cTn>
  <!-- Effect 2 — delay 0.3s -->
  <p:cTn id="12" dur="0.5" fill="hold">
    <p:stCondLst>
      <p:cond evt="after" delay="0.3"/>
    </p:stCondLst>
    <!-- same structure targeting a DIFFERENT shape -->
  </p:cTn>
</p:seq>
```

## Slide Transitions

Added as `<p:transition>` on `<p:sld>`, **not** inside timing:

```python
trans_xml = '''<p:transition xmlns:p="..." spd="slow" advClick="1">
  <p:push/><p:sndVol/>  <!-- or <p:fade/>, <p:wipe/>, etc. -->
</p:transition>'''
trans_elem = parse_xml(trans_xml)
slide._element.append(trans_elem)
```

Common transition types: `<p:fade/>`, `<p:push/>`, `<p:wipe/>`, `<p:split/>`, `<p:uncover/>`, `<p:morph/>` (p14 namespace).

## Farsi / RTL Considerations

- Set `bodyPr.rtlCol="1"` on the shape's text body XML
- Set `pPr.rtl="1"` on each paragraph
- Use python-pptx alignment: `paragraph.alignment = PP_ALIGN.RIGHT`
- Font recommendation: "B Nazanin", "IRANSans", or "Segoe UI" for Farsi
- PowerPoint 2019+ and Office 365 handle RTL correctly inside animated text frames
- Motion Paths and position animations (ppt_x/ppt_y) work identically for RTL slides

## Known Limitations

- ppt_x/ppt_y offsets don't mirror for RTL slides — positions are absolute in the coordinate system
- `repeatCount="indefinite"` works in presenter mode but may not loop on PowerPoint Online
- p:animEffect `filter="dissolve"` may fall back to `filter="fade"` on older PowerPoint versions
- Motion Paths with complex bezier curves can lose fidelity across PowerPoint versions
- Text-level (character) animations not covered — only shape-level
