# framer-motion → IR Extraction Reference

Collected 2026-07-13 during a Persian networking-presentation project (18 slides, 176 motion elements).

## Overview

When converting a React/framer-motion presentation to PowerPoint, the critical pre-conversion
step is systematically extracting every animation parameter from the source code. This reference
documents the regex patterns and methodology for exhaustively cataloguing framer-motion props
from TSX components.

## Extraction Strategy

### Pass 1 — Element Discovery

Find all `<motion.*` elements with their type and inline props:

```python
motion_re = re.compile(
    r'<motion\.(div|g|p|button|span|path|circle|line|rect|text|ellipse|svg|h\d|figure|section)'
    r'([\s\S]*?)>'
)
```

Extract the opening-tag props by tracking brace depth to find the matching `>`:

```python
for elem_type, props_block in motion_elements:
    depth = 0
    props_text = ""
    for ch in props_block:
        if ch == '{':
            depth += 1
            props_text += ch
        elif ch == '}':
            depth -= 1
            props_text += ch
        elif ch == '>' and depth == 0:
            break
        else:
            props_text += ch
```

### Pass 2 — Prop Extraction

Extract all animation-relevant props from each element:

```python
initial = re.search(r'initial=\{(.*?)\}(?:\s|>)', props_text)
animate = re.search(r'animate=\{(.*?)\}(?:\s|>)', props_text)
transition = re.search(r'transition=\{(.*?)\}(?:\s|>)', props_text)
variants = re.search(r'variants=\{(.*?)\}(?:\s|>)', props_text)
exit_prop = re.search(r'exit=\{(.*?)\}(?:\s|>)', props_text)
while_hover = re.search(r'whileHover=\{(.*?)\}(?:\s|>)', props_text)
while_tap = re.search(r'whileTap=\{(.*?)\}(?:\s|>)', props_text)
style = re.search(r'style=\{(.*?)\}(?:\s|>)', props_text)
```

### Pass 3 — Parameter Parsing

Extract exact timing values from each `transition={}` block:

```python
delay = re.search(r'delay:\s*([.\d]+)', transition_str)
duration = re.search(r'duration:\s*([.\d]+)', transition_str)
ease = re.search(r'ease:\s*[\[\]\w\s.,()\"-]+?(?=\}|,|\s*//)', transition_str)
spring = re.search(r'type:\s*"(\w+)"', transition_str)
stiffness = re.search(r'stiffness:\s*([\d.]+)', transition_str)
repeat = re.search(r'repeat:\s*(\S+)', animate_str + transition_str)
times = re.search(r'times:\s*(\[.*?\])', transition_str)
```

### Pass 4 — SVG-Specific Extraction

For SVG diagram slides, extract coordinate systems:

```python
# ViewBox
re.search(r'viewBox=["\']([^"\']+)["\']', code[:500])

# Node positions (various patterns)
re.findall(r'(\w+):\s*\{\s*x:\s*(\d+),\s*y:\s*(\d+)', code)  # Router coords
re.findall(r'id:\s*"(\w+)"[^}]*x:\s*(\d+)[^}]*y:\s*(\d+)', code)  # DNS node coords

# Arrow markers / defs
re.findall(r'<marker[^>]*>', code)
re.findall(r'<linearGradient[^>]*>', code)
re.findall(r'<filter[^>]*>([\s\S]*?)</filter>', code)

# Template-literal path d=
re.findall(r'd=\s*`([^`]+)`', code)
re.findall(r'path:\s*`([^`]+)`', code)

# Motion path (offsetPath / offsetDistance)
re.search(r'offsetPath[^;]*path\(["\u201d]', line)
re.search(r'offsetDistance[^:]*:\s*"([^"]+)"', line)

# SVG-specific animated properties
re.findall(r'offsetDistance', code)
re.findall(r'pathLength', code)
re.findall(r'strokeDashoffset', code)
re.findall(r'cx[^}]*cy', code)
```

### Pass 5 — CSS Animation Detection

Extract CSS keyframe-based animations referenced by class names:

```python
# CSS keyframes
re.findall(r'@keyframes\s+(\w+)', stylesheet)
re.findall(r'animate-(\w+[\w-]*)', code)   # class references
re.findall(r'animation:\s*(.*?);', stylesheet)
```

## Effect Classification Matrix

Classify each extracted element into an OOXML target:

```python
def classify_effect(initial, animate, transition, style):
    effects = []
    if 'opacity' in animate:        effects.append('fade')
    if 'x:' in animate:             effects.append('slide_h')
    if 'y:' in animate:             effects.append('slide_v')
    if 'scale' in animate:          effects.append('scale')
    if 'pathLength' in animate:     effects.append('svg_path_draw')
    if 'offsetDistance' in animate: effects.append('motion_path')
    if 'cx' in animate or 'cy' in animate: effects.append('svg_position')
    if 'rotateX' in animate:        effects.append('rotate_3d')
    if 'spring' in transition:      effects.append('spring')
    if 'repeat: Infinity' in str([animate, transition]): effects.append('loop')
    if 'whileHover' in ...:         effects.append('hover_trigger')
    return effects
```

## Coordinate Extraction Examples

### Slide06bRouting.tsx (6-node router graph)
```python
# Coordinates
R = {"A": (90, 220), "B": (190, 90), "C": (220, 260),
     "D": (360, 90), "E": (380, 260), "F": (500, 175)}
# mainPath via C,E
mainPath = f"M {R['A'].x} {R['A'].y} L {R['C'].x} {R['C'].y} L {R['E'].x} {R['E'].y} L {R['F'].x} {R['F'].y}"
# altPath via B,D
altPath = f"M {R['A'].x} {R['A'].y} L {R['B'].x} {R['B'].y} L {R['D'].x} {R['D'].y} L {R['F'].x} {R['F'].y}"
```

### Slide04DNS.tsx (6 nodes, 1800×820 viewBox)
```
6 query nodes + 4 response nodes, connected by lines with arrQ/arrR arrow markers.
```

## Stagger Pattern Extraction

Every `motion.*` inside a `.map()` with `i`-based delay is a stagger. Extract the formula:

```python
# Pattern: delay: base + i * step
reveal_delays = {
    'S01Title.words':      (0.3, 0.15, 6),
    'S02Fiber.cards':      (0.4, 0.2, 3),
    'S04DNS.query_nodes':  (0.15, 0.1, 6),
    'S08Summary.cards':    (0.2, 0.12, 6),
}
# Pattern: delay: base + n * step (multi-index stagger)
multi_index_delays = {
    'S07bSensor.pulse_rings': (1.2, 0.2, 1.2),  # base + i*0.2 + k*1.2
}
```

## Output Format

Write analysis to a structured markdown file with:

```markdown
# Fase 1 — Analysis: <Project Name>

## Slide Data
| # | File | Title | Lines | Anims | Key Effects |

## Per-Slide Detail
### Slide<N> — <Title> (N anims)
| Element | Tag | Type | Delay | Duration | Spring | Loop | Initial | Animate |

## SVG Diagrams
| Slide | ViewBox | Coordinates | Markers |

## Stagger Timings
| Slide | Base | Step | Count |

## Custom Timing Constants
| Constant | Value | Meaning |
```

## Tools

The following can be used from `execute_code` with `from hermes_tools import terminal`:

```python
# Quick animation count per file
terminal(f"grep -c 'initial=' {' '.join(tsx_files)}")

# Count motion element types
terminal(f"grep -oP '<motion\\.\\w+' {' '.join(tsx_files)} | sort | uniq -c | sort -rn")

# Find all offsetPath/offsetDistance
terminal(f"grep -rn 'offsetPath\\|offsetDistance' {slides_dir}/")
```
