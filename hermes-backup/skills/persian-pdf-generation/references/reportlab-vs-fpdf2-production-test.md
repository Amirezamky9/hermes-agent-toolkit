# reportlab vs fpdf2 — Production Test Results (2026-07-15)

## Context
User requested a 2-page Persian resume PDF. Went through 5+ iterations with fpdf2 before switching to reportlab.

## Test Results

| Library | Score | Persian Characters | RTL | Layout | Verdict |
|---------|-------|--------------------|-----|--------|---------|
| fpdf2 (with arabic_reshaper + bidi) | Broken/5 | DISCONNECTED — letters isolated | Partially correct | Overlapping header, broken spacing | **REJECT** |
| reportlab (with arabic_reshaper + bidi) | 9/10 | CONNECTED — proper cursive | Correct | Clean, professional | **USE THIS** |

## Why fpdf2 Fails
- fpdf2 embeds fonts but renders each glyph independently
- Even with arabic_reshaper reshaping text, fpdf2's glyph placement algorithm doesn't handle RTL cursive properly
- `align="R"` positions text but doesn't fix glyph connectivity
- The `set_xy()` workarounds for mixed content create alignment chaos
- cell() + multi_cell() mixing for RTL breaks x-position

## Why reportlab Works
- `Paragraph` class in reportlab's Platypus handles RTL natively
- Arabic reshaping + bidi applied correctly to the text before rendering
- `SimpleDocTemplate` manages page layout, margins, and auto-page-break
- No glyph disconnection — characters render as connected cursive
- Styles (ParagraphStyle) give clean control over fonts, colors, alignment

## reportlab Code Pattern (Production-Ready)

```python
import os
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Font registration
pdfmetrics.registerFont(TTFont('Vazir', '/path/to/Vazir-Regular.ttf'))
pdfmetrics.registerFont(TTFont('VazirBold', '/path/to/Vazir-Bold.ttf'))
pdfmetrics.registerFontFamily('Vazir', normal='Vazir', bold='VazirBold')

def fa(text):
    """Reshape Persian text for correct visual rendering."""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)

# Document setup
doc = SimpleDocTemplate("output.pdf", pagesize=A4,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    rightMargin=1.8*cm, leftMargin=1.8*cm)

# Styles
BLUE = HexColor('#1D4EC5')
DARK = HexColor('#1A1A1A')
BODY = HexColor('#333333')

style_section = ParagraphStyle('Section', fontName='VazirBold', fontSize=10,
    leading=13, textColor=BLUE, alignment=TA_RIGHT, spaceBefore=6, spaceAfter=2)
style_body = ParagraphStyle('Body', fontName='Vazir', fontSize=9,
    leading=12, textColor=BODY, alignment=TA_RIGHT, spaceAfter=1)
style_bullet = ParagraphStyle('Bullet', fontName='Vazir', fontSize=8,
    leading=11, textColor=BODY, alignment=TA_RIGHT, rightIndent=8, spaceAfter=0.5)

# Build
story = []
story.append(Paragraph(fa("عنوان بخش"), style_section))
story.append(Paragraph(fa("متن فارسی"), style_body))
story.append(Paragraph(fa("• نکته اول"), style_bullet))
doc.build(story)
```

## Verification Pattern

```python
import fitz  # pymupdf
doc = fitz.open("output.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f"/workspace/verify_page_{i+1}.png")
doc.close()
# Then use vision_analyze to check each page
```

## Environment Notes
- Vazir fonts located at `~/.fonts/Vazir-*.ttf`
- Non-FD variants: English digits (09115110174)
- FD variants: Persian digits (۰۹۱۱۵۱۱۰۱۷۴)
- pymupdf available via `pip install pymupdf`
- No root/libreoffice needed for reportlab
