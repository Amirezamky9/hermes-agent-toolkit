# Session Research Record — Persian Resume Final (امیررضا مختاری, 2026-07-15)

## Context
Final iteration of a Persian resume build. User provided exact text via uploaded file and said "اینو بزار کلا | و این ک استیکر هاشو نزار فقط" — meaning: use this exact text, strip all emoji stickers.

## Key Corrections This Session

### 1. Emoji stripping requested
User: "استیکر هاشو نزار فقط"
Meaning: Strip ALL emoji from the text before rendering. The raw Persian text works fine without icon decoration.

Fix: Manually strip all Unicode emoji from the text strings before passing to the PDF/DOCX generator.

### 2. "اعداد همه انگلیسی باشه" — English digits required
User wanted numbers like 09115110174 (English/Arabic numerals) not ۰۹۱۱۵۱۱۰۱۷۴ (Persian numerals).

Fix: Use non-FD Vazir font variants:
- `Vazir-Regular.ttf` (not `Vazir-Regular-FD.ttf`)
- `Vazir-Bold.ttf` (not `Vazir-Bold-FD.ttf`)

The FD variants embed Persian digits; non-FD variants use standard Arabic numerals.

### 3. Exact text reproduction — no additions
User uploaded a file with complete Persian text and said "اینو بزار کلا" meaning reproduce exactly. Don't add sections, don't add projects from GitHub, don't add extra descriptions.

## What Was Built
- PDF: fpdf2 + arabic_reshaper + bidi + non-FD Vazir
- DOCX: python-docx + Vazir + RTL `w:bidi`

## Future Reference
When a Persian-speaking user provides source text and says "اینا باشه" / "همینا باشه" / "اینو بزار":
- Reproduce EXACTLY what they provided
- Strip emoji if asked
- Check digit style preference: Persian vs English numerals → select FD or non-FD font variant
