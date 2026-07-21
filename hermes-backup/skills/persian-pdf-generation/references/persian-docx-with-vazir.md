# Persian DOCX Generation with python-docx + Vazir Font

Generate professional Persian/Farsi DOCX documents (resumes, reports, forms) using `python-docx` with the Vazir font family and proper RTL support.

**Used in session:** 2026-07-15 (Amirreza resume — PDF + DOCX)

## Technique

python-docx has basic RTL support via OpenXML `w:bidi` attributes but lacks built-in Persian shaping. Unlike fpdf2, python-docx **does NOT require arabic_reshaper** — Microsoft Word and LibreOffice handle Persian glyph joining natively when `w:bidi` is set.

## Key RTL Pattern

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# Set default font + RTL on Normal style
style = doc.styles['Normal']
style.font.name = 'Vazir'
style.font.size = Pt(9)
style.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
# Enable RTL on default style
pPr = style.element.get_or_add_pPr()
pPr.set(qn('w:bidi'), '1')
```

## Helper Function for RTL Paragraphs

```python
def mk_para(text, bold=False, size=9, color=None, align=WD_ALIGN_PARAGRAPH.RIGHT,
            space_after=1, space_before=0, italic=False, font_name='Vazir', indent=None):
    p = doc.add_paragraph()
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    pPr.set(qn('w:bidi'), '1')          # <-- CRITICAL: enables RTL
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)

    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    rPr = run._r.get_or_add_rPr()
    rPr.set(qn('w:bidi'), '1')          # <-- CRITICAL: RTL on run level too
    return p
```

## Mixed-Format Paragraph (Label + Value on Same RTL Line)

```python
def mk_mixed_para(parts, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1, space_before=0):
    """parts = [(text, bold, size, color, italic), ...]"""
    p = doc.add_paragraph()
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    pPr.set(qn('w:bidi'), '1')
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    for text, bold, size, color, italic in parts:
        run = p.add_run(text)
        run.font.name = 'Vazir'
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        if color:
            run.font.color.rgb = RGBColor(*color)
        rPr = run._r.get_or_add_rPr()
        rPr.set(qn('w:bidi'), '1')
    return p
```

## Section Underline (Blue Accent Line)

```python
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def section_title(text):
    p = mk_para(text, bold=True, size=11, color=(0x25, 0x63, 0xeb), space_before=8, space_after=4)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="4" w:space="1" w:color="DDDDDD"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)
```

## Handling Persian Text in python-docx

Unlike fpdf2, python-docx **does NOT need arabic_reshaper** — the rendering engine (Word/LibreOffice) handles glyph joining natively when `w:bidi` is set.

### What DOES need attention:

| Issue | Solution |
|-------|----------|
| Persian letters not joining | Ensure `w:bidi` is set on BOTH paragraph AND run level |
| Page margins | `doc.sections[0].right_margin = Cm(2)` — note RIGHT margin is the outer margin for RTL |
| Email/URL in Persian paragraph | Just write them inline; they display correctly with `w:bidi` |
| Bullet lists | Use `•` (U+2022) prepended to text with `indent=0.3` |
| Numbers | Persian numbers (۱۲۳) render correctly; mixed English/Persian numbers may need `w:bidi` |
| Line spacing | Persian text needs slightly more vertical space — use `Pt(4.2)` line spacing or taller cells |

### What NOT to do:
- **Do NOT use arabic_reshaper** on python-docx text — it breaks the OpenXML storage
- **Do NOT use `rPr.set(qn('w:lang'), None)`** — it causes `TypeError` in lxml (must be bytes or unicode)
- **Do NOT set `cs` font** via `rPr.set(qn('w:cs'), None)` — this causes the same `NoneType` error

## Page Setup for RTL Resume

```python
for section in doc.sections:
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.5)
    section.right_margin = Cm(2)   # outer margin for RTL
    section.left_margin = Cm(2)    # inner/gutter margin for RTL
```

## Pitfalls

1. **`w:bidi` must be set on BOTH paragraph AND run.** Setting it only on the paragraph level is not enough for all viewers.
2. **`w:lang` cannot be `None`.** When removing lang attributes, pass empty string `''` not `None` — lxml rejects None.
3. **Avoid mixing `cell()` + `multi_cell()` patterns** (from fpdf2 thinking) — in python-docx, just use `add_paragraph()`.
4. **Emoji in Vazir font** — Vazir has no emoji glyphs. Replace with Persian text equivalents:
   - 📞 → `تلفن:`
   - ✉️ → `ایمیل:`
   - 🔗 → `گیت‌هاب:`
5. **Font availability** — The DOCX file stores the font name, not the font file. The font must be installed on the viewer's system. Vazir Font is standard for Persian documents.
6. **Wide tables don't wrap** — python-docx tables with RTL text can be problematic. Prefer line-separated lists over tables for Persian DOCX.
