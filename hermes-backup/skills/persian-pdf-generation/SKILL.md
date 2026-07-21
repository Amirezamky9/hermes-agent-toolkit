---
name: persian-pdf-generation
description: Generate professional Persian/Farsi PDF documents with proper RTL support. Covers resumes, certificates, reports, and any Persian document needing controlled formatting. Uses reportlab (recommended) or fpdf2 with arabic_reshaper + bidi.
category: data-processing
triggers:
  - resume
  - رزومه
  - PDF فارسی
  - Persian PDF
  - "رزومه بنویس"
  - "ساخت PDF"
  - farsi pdf
  - "document PDF"
  - certificate persian
---

# Persian PDF Generation

Generate professional Persian/Farsi PDFs using Python with the Vazir font family. **reportlab** is the recommended library; fpdf2 is available as a fallback but has known issues with Persian glyph connectivity.

> ⚠️ **CRITICAL: Library Selection — reportlab vs fpdf2**
>
> **Use reportlab (RECOMMENDED)** — renders Persian text correctly out of the box with arabic_reshaper + bidi.
> **Avoid fpdf2** — even with arabic_reshaper, fpdf2 produces DISCONNECTED Persian characters in many environments. This was confirmed in production: fpdf2 scored broken/5 while reportlab scored 9/10.
>
> See "reportlab (Recommended)" section below for the production pattern.

## Installation

```bash
pip install reportlab arabic-reshaper python-bidi pymupdf
```

- `reportlab` — PDF generation (RECOMMENDED over fpdf2)
- `arabic_reshaper` + `python-bidi` — Persian text shaping (MANDATORY for both libraries)
- `pymupdf` — convert PDF to images for verification before delivery

For fpdf2 (fallback only):
```bash
pip install fpdf2 arabic_reshaper python-bidi pymupdf
```

## Persian Text Reshaping (MANDATORY)

fpdf2 renders each Unicode glyph independently, but Persian/Arabic letters change shape based on position (initial, medial, final, isolated). Without reshaping, text renders as disconnected letters.

**Always use this helper:**

```python
import arabic_reshaper
from bidi.algorithm import get_display

def persian(text):
    """Convert Persian text to properly joined display form."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
```

Then wrap ALL Persian string arguments:
```python
self.cell(0, 10, persian("امیررضا مختاری"), align="C")  # ✅ correct
# NOT: self.cell(0, 10, "امیررضا مختاری", align="R")   # ❌ broken
```

Even single Persian words need reshaping. Only ASCII text (emails, URLs, code) can pass through unreshaped.

## Quick Start (reportlab — RECOMMENDED)

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

FONTS_DIR = os.path.expanduser("~/.fonts")
FONT_REG = os.path.join(FONTS_DIR, "Vazir-Regular.ttf")  # English digits
FONT_BOLD = os.path.join(FONTS_DIR, "Vazir-Bold.ttf")

pdfmetrics.registerFont(TTFont('Vazir', FONT_REG))
pdfmetrics.registerFont(TTFont('VazirBold', FONT_BOLD))
pdfmetrics.registerFontFamily('Vazir', normal='Vazir', bold='VazirBold')

def fa(text):
    """Reshape Persian text for correct visual rendering."""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)

# Create document
doc = SimpleDocTemplate("output.pdf", pagesize=A4,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    rightMargin=1.8*cm, leftMargin=1.8*cm)

# Define styles
style_body = ParagraphStyle('Body', fontName='Vazir', fontSize=9,
    leading=12, textColor=HexColor('#333333'), alignment=TA_RIGHT)
style_bold = ParagraphStyle('Bold', fontName='VazirBold', fontSize=9,
    leading=12, textColor=HexColor('#1A1A1A'), alignment=TA_RIGHT)

# Build content
story = []
story.append(Paragraph(fa("سلام دنیا"), style_bold))
story.append(Paragraph(fa("این یک متن فارسی است"), style_body))
doc.build(story)
```

**Why reportlab over fpdf2:**
- reportlab's `Paragraph` + `SimpleDocTemplate` handle RTL natively
- Arabic reshaping + bidi works reliably with reportlab
- No glyph disconnection issues
- Better spacing and layout control with Platypus flowables
- Scored 9/10 in production testing vs broken/5 with fpdf2

## Quick Start (fpdf2 — FALLBACK only)

Use fpdf2 only if reportlab is unavailable. **Expect disconnected Persian characters** even with arabic_reshaper in some environments.

```python
from fpdf import FPDF
import os
import arabic_reshaper
from bidi.algorithm import get_display

FONT_PATH = os.path.expanduser("~/.fonts/Vazir-Regular.ttf")
FONT_BOLD_PATH = os.path.expanduser("~/.fonts/Vazir-Bold.ttf")

def persian(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

class PersianPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_font("Vazir", "", FONT_PATH)
        self.add_font("Vazir", "B", FONT_BOLD_PATH)
        self.set_auto_page_break(auto=True, margin=18)
```

### Font Variant Selection: FD vs non-FD for Digits

Vazir font comes in TWO digit variants — this is a frequent source of user corrections:

| Variant | Digit Style | Example | Use Case |
|---------|-------------|---------|----------|
| **Non-FD** (e.g. `Vazir-Regular.ttf`) | Arabic numerals (English) | `09115110174` | Professional resumes, CVs, tech docs — most employers want English digits |
| **FD** (e.g. `Vazir-Regular-FD.ttf`) | Persian/Arabic digits | `۰۹۱۵۱۱۰۱۷۴` | Traditional Persian documents, formal letters, literary content |

When the user says "اعداد همه انگلیسی باشه" (all numbers should be English), use the **non-FD** variants:
```python
FONT_REGULAR = os.path.expanduser("~/.fonts/Vazir-Regular.ttf")      # English digits
FONT_BOLD    = os.path.expanduser("~/.fonts/Vazir-Bold.ttf")
```

When the user wants traditional Persian digits, use the FD variants:
```python
FONT_REGULAR = os.path.expanduser("~/.fonts/Vazir-Regular-FD.ttf")   # Persian digits
FONT_BOLD    = os.path.expanduser("~/.fonts/Vazir-Bold-FD.ttf")
```

**Always ask or check the user's source text** to determine which digit style they expect. If their provided text uses English digits (09115110174), use non-FD. If they use Persian digits (۰۹۱۵۱۱۰۱۷۴), use FD.

**Pitfall:** The default `find_font_variant()` function in this skill prefers FD (score +10). If the user's text has English digits but gets FD font, the numbers will render as Persian digits. Explicitly bypass the scorer for FD preference when the user wants English digits.

### فونت وزیر نصب (از GitHub Release)
```python
import zipfile, os, urllib.request

url = "https://github.com/rastikerdar/vazir-font/releases/download/v30.1.0/vazir-font-v30.1.0.zip"
urllib.request.urlretrieve(url, "/tmp/vazir.zip")
z = zipfile.ZipFile("/tmp/vazir.zip")
for f in z.namelist():
    if f.endswith(".ttf"):
        data = z.read(f)
        outname = os.path.basename(f)
        os.makedirs(os.path.expanduser("~/.fonts"), exist_ok=True)
        with open(os.path.expanduser(f"~/.fonts/{outname}"), "wb") as out:
            out.write(data)
```
> **Do NOT use `master/dist/` URLs from GitHub** — they return 404. Always use release tag paths.

## Font Discovery at Runtime (for environments with unknown font locations)

In environments like Hermes WebUI, font paths aren't guaranteed. Use a robust discovery function:

```python
import os

FONTS_DIR = os.path.expanduser("~/.fonts")

def find_font_variant(name_part):
    """Find best-matching Vazir font. Prefers FD (fully digit) with no WOL/UI suffix."""
    candidates = [f for f in os.listdir(FONTS_DIR)
                  if name_part in f and f.endswith(".ttf")]
    def score(fn):
        s = 0
        if "FD" in fn: s += 10
        if "WOL" not in fn: s += 5
        if "UI" not in fn: s += 5
        return s
    if candidates:
        candidates.sort(key=score, reverse=True)
        return os.path.join(FONTS_DIR, candidates[0])
    return None
```

## Companion Service: GitHub Portfolio

After building a Persian resume, users often want to showcase projects on GitHub. Be ready to:

1. Create a GitHub repository for their portfolio (`gh repo create portfolio --public`)
2. Upload project files with meaningful folder structure
3. Write professional Persian+English README for each project
4. Suggest a consistent username/organization (e.g., github.com/username)

This is NOT part of the PDF generation but is a natural follow-up — mention it when wrapping up a resume build.
> **Do NOT use `master/dist/` URLs from GitHub** — they return 404. Always use release tag paths.

## Key Techniques

### RTL & Alignment
- fpdf2 has NO `set_rtl()` method (removed in v2.5+)
- With `persian()` reshaping, `align="R"` for multi-line, `align="C"` for centered titles
- After every cell: `new_x="LMARGIN"`, `new_y="NEXT"`
- `align="C"` works naturally for centered Persian text after reshaping

### Emoji / Special Chars
Vazir font **has no emoji glyphs**. Replace with text:
| Emoji | Replacement |
|-------|-------------|
| 📧 | `"ایمیل:"` |
| 📞 | `"تلفن:"` |
| 🌐 / 🔗 | `"پیوند:"` or omit |
| • / ▸ / ❤️ | Use `"-"` or `"—"` or just omit |
| 🐙 | `"گیت‌هاب:"` or `"GitHub:"` |
| 💡 | `"نکته: "` or omit |
| 🛠️ | omit — section title is enough |
| 💼 | omit — section title is enough |
| 🚀 | omit or use `"پروژه‌ها:"` |
| 🎓 | omit — section title is enough |
| 🏅 | omit — section title is enough |
| 🗣️ | omit — section title is enough |
| 📄 | omit |

**When the user says "استیکر هاشو نزار فقط" (don't put emojis):** Strip ALL Unicode emoji characters from their text before generating. Use regex to remove emoji ranges. The raw Persian text without emojis is preferred — section headers like "خلاصه حرفه‌ای" and "مهارت‌های فنی" stand fine on their own without icon decoration.

### Mixed Persian/English
```python
self.set_font("Vazir", "B", 10)
self.write(5, persian("عنوان: "))
self.set_font("Vazir", "", 10)
self.multi_cell(0, 5, persian("English + ادامه فارسی"), align="R")
```

### Line Height
Persian text needs slightly more vertical space than Latin:
- `cell(0, 6, ...)` for single lines (not 5)
- `multi_cell(0, 5.5, ...)` for paragraphs (not 5)

### Experience Entry with Date on Same Line (RTL)

`set_xy()` is the reliable way to place date on the left while title is right-aligned:

```python
# Title right-aligned
pdf.set_font("Vazir", "B", 9.5)
pdf.set_text_color(0x1a, 0x1a, 0x1a)
pdf.cell(0, 5, fa(exp["title"]), align="R")
pdf.ln(5.5)

# Company name (right-aligned)
pdf.set_font("Vazir", "", 9)
pdf.set_text_color(0x44, 0x44, 0x44)
left_x = pdf.l_margin  # save left margin for date positioning
pdf.cell(0, 4.5, fa(exp["company"]), align="R")
pdf.ln(0)  # don't advance — stay on same line
# Now place date from the left margin
pdf.set_xy(left_x, pdf.get_y())
pdf.set_font("Vazir", "", 8.5)
pdf.set_text_color(0x66, 0x66, 0x66)
pdf.cell(0, 4.5, fa(exp["date"]), align="L")
pdf.ln(5)
```

**Important:** The `pdf.ln(0)` after the company cell is critical — it prevents advancing the y-position so `set_xy` overwrites correctly within the same line height.

### Bullet Points with Indentation

```python
pdf.set_x(24)   # indent by 4mm
pdf.set_font("Vazir", "", 8.5)
pdf.set_text_color(0x44, 0x44, 0x44)
pdf.multi_cell(w=pdf.pw() - 4, h=4.2, text=fa(f"• {text}"), align="R")
```

### Skills Section: Avoid mixing cell() + multi_cell()

**CRITICAL:** For RTL text, mixing `cell()` (for a bold label) followed by `multi_cell()` (for the value) on the same line **breaks alignment** — the label's right-aligned cell claims some width, then the multi_cell starts from the wrong x. Instead, combine them into a single `multi_cell()`:

```python
# ✅ CORRECT — single multi_cell with bold+regular combined
combined = f"[ {label} ] {items}"
pdf.set_text_color(0x1a, 0x1a, 0x1a)
pdf.set_font("Vazir", "B", 9)
pdf.multi_cell(w=pdf.pw(), h=4.5, text=fa(combined), align="R")

# ❌ WRONG — mixed cell() + multi_cell() breaks RTL alignment
pdf.cell(label_width, 4.5, fa(label), align="R")
pdf.multi_cell(rest_width, 4.5, fa(items), align="R")  # wrong x position
```

## Document Types

### Resume / رزومه — Best Practices from Professional Samples

**CRITICAL RULE: Research First, Code Second (NEVER skip)**
When a Persian-speaking user asks for a resume, ALWAYS:
1. Research the EXACT domain terminology for each technology they mention (search sample resumes, Wikipedia, official docs)
2. Don't guess job titles — ask the user for their exact official title
3. Look up professional resume standards for their specific field (Automation Engineer, AI Engineer, etc.)
4. Present the outline to the user BEFORE writing code
5. This rule exists because the user WILL notice if you use wrong terminology — and will be frustrated

**Domain research resources (free, always available):**
- Wikipedia for technology descriptions (r.jina.ai/https://en.wikipedia.org/wiki/...)
- DuckDuckGo HTML search for sample resumes: `https://html.duckduckgo.com/html/?q=automation+engineer+resume+sample`
- Professional resume samples on Zety, MaxResumes, LiveCareer (via Jina Reader)
- For Persian resumes: IranEstekhdam, CVBuilder.me samples

**Common Automation/AI domain terms that need precise description:**
| Term | Precise Professional Description |
|------|--------------------------------|
| n8n | "Workflow Automation Platform — 400+ integrations, visual node-based editor, self-hosted alternative to Zapier" |
| Hermes Agent | "Open-source AI Agent framework from Nous Research — persistent memory, reusable skills, cron jobs, 24 messaging platforms" |
| RAG Agent | "Retrieval-Augmented Generation system — combines LLMs with external knowledge bases for grounded, accurate responses" |
| Digital Worker | "Automation script/agent that performs web-based tasks autonomously (scraping, data extraction, form filling)" |
| Telegram Bot | "Telegram Bot API-based automation for messaging, customer service, notifications" |

Professional Persian resume structure:

**Header:**
- Full name (large, centered, bold, ~22pt)
- Professional title (e.g. "مهندس اتوماسیون و هوش مصنوعی")
- Contact: ایمیل | تلفن | لینکدین (single centered line)

**Sections (in order):**
1. **خلاصه / Summary** — 2-3 line professional summary focusing on years of experience, key technologies, what you deliver
2. **سابقه کاری / Experience** — Each entry: company name (BOLD), date range (gray, smaller), role title, then bullet points of achievements (not just duties)
3. **مهارت‌ها / Skills** — Categorized: use bold labels with descriptions. Avoid walls of comma-separated tags for Persian resumes — use category: detail format
4. **تحصیلات / Education** — Degree, university, year
5. **پروژه‌ها / Projects** — Bullet points with project name, short description, technologies used, your role
6. **گواهینامه‌ها / Certifications** — Certificate name + issuer + year
7. **دستاوردهای دیگر / Other** — Side projects, social media, open source

**Design rules:**
- MAXIMUM 2 pages (prefer 1 for <5 years experience)
- NO emoji/icons in the PDF body (font can't render them)
- Use color sparingly: dark header text, blue (#0d6efd) for section underlines only
- Bullet points for achievements, not paragraphs
- Dates: always right-aligned with consistent format
- White space between sections: 10-14pt gap

### Report / گزارش
Can use similar structure but with numbered sections and table support.

## fpdf2 Pitfalls & Solutions

| Issue | Solution |
|-------|----------|
| Persian letters disconnected ("س ل ا م") | **BLOCKER for fpdf2**: even with arabic_reshaper, fpdf2 produces disconnected text in many environments. **Switch to reportlab** — it works reliably. See "reportlab (Recommended)" section. |
| `DeprecationWarning: "uni" parameter` | Remove `uni=True` — fpdf2 2.5.1+ dropped it |
| `AttributeError: no set_rtl` | No RTL mode — use `align="R"` throughout |
| Missing glyphs for emoji | Replace with plain text equivalents |
| `cell()` right-aligned but next cell wrong | Always specify `new_x="LMARGIN"` |
| Skills section alignment broken (label right, items broken) | **Pitfall: mixing cell() + multi_cell() for RTL labels breaks x-position.** Combine label and items into a single `multi_cell()` call. |
| Date on same line as title misaligned | Use `set_xy(left_x, get_y())` pattern with `ln(0)` between the company and date calls |
| `w:lang = None` causes `TypeError: Argument must be bytes or unicode` | NEVER pass `None` to `rPr.set(qn('w:lang'), ...)` or any lxml `set()`. Pass `""` (empty string) or omit the call entirely. See `references/persian-docx-with-vazir.md` for exact fix. |
| Four script iterations wasted time | Each version tried to generate the FULL resume in one run. Instead: build one section at a time, show user, get feedback, then add next section. If layout breaks mid-way, fix BEFORE adding more content — adding more content while broken multiplies rework |
| Text cut off at page bottom | Increase `bottom_margin` or reduce content spacing |
| Numbers appear reversed (۱۳۴ → ۴۳۱) | This is a bidi issue — `persian()` handles it if input uses Persian digits |
| Mixed LTR/RTL text alignment wrong | Wrap the full mixed string in `persian()` at once; don't split LTR/RTL parts |

## Resume-Building Workflow (CRITICAL — avoid user frustration)

### GOLDEN RULE: Research → Show Results → Plan → Approve → Build

This sequence is MANDATORY. Every time you skip it, the user corrects you.
The phases are:

```
1. GATHER info from user         ← collect ALL data first
2. RESEARCH domain terms          ← search web, Wikipedia, resume samples
3. SHOW research to user          ← present findings inline as tables/ bullet points (CRITICAL)
4. PRESENT outline                ← show proposed structure, get sign-off
5. build_resume.py && execute     ← one clean run, then deliver
```

**NEVER jump from step 2 directly to step 5.** If the user says "سرچ کن قشنگ" or "منم نمیبینم", it means you did the research silently instead of presenting it. Always surface search results inline (titles, URLs, key findings) before making decisions.

### Step 1: Deep Information Gathering (NEVER skip)
Do NOT start coding immediately. Collect ALL of these FIRST:
- Exact job titles at each company (what the company called the role, not your translation)
- What technologies they actually used vs. just know about — be precise
- Specific achievements with numbers where possible ("designed 5 bots", "reduced processing time by X%")
- Company description if it's not well-known (what the company does)
- The target position/company (if known — if not, design a general-purpose resume)
- Whether they want 1-page or 2-page
- Preferred style: traditional Persian (section-based) or modern infographic

### Step 2: Research Standards (MANDATORY — NEVER SKIP)
This step is NOT optional. The user WILL notice and correct you if you skip it.

Search the web for:
- "sample resume [field]" or "CV sample [job title]" (English and Persian)
- Read domain documentation for EACH technology the user mentions — Wikipedia, official docs, GitHub README
- Professional resume samples on Zety, MaxResumes, LiveCareer (via Jina Reader)
- For Persian resumes: IranEstekhdam, CVBuilder.me samples
- Research WHAT each tool/technology does — don't just rewrite the user's description

**Pitfall: "نمی‌دونم تحقیق کن"** — If the user says this, it means you already wrote content without understanding the domain. STOP writing immediately. Research every single technology they mentioned until you can explain each in 1-2 accurate sentences. This is the #1 frustration signal from Persian resume users.

### Step 3: SHOW Your Research to the User (CRITICAL — most-often missed)

**This is the step the user complained about.** Do NOT consume search results silently and move on to writing code.

✅ CORRECT presentation format:
```
## نتایج تحقیق از نمونه رزومه‌های حرفه‌ای

📄 نمونه ۱: QwikResume.com — Automation Engineer
ساختار: Summary → Skills → Experience → Education
بولت‌ها: action verbs + measurable results

📄 نمونه ۲: HireKit.co — ATS-optimized
ساختار: Professional Summary → Core Skills → Experience (Action + Metric)

💡 نکات مهم برای رزومه شما:
1. عنوان شغلی دقیق بالای هر سابقه
2. ۱ صفحه (برای زیر ۵ سال سابقه)
3. ATS-Friendly

این رزومه شامل این بخش‌هاست: 
• سربرگ
• تحصیلات  
• سوابق کاری
• مهارت‌ها
• پروفایل آنلاین

این ساختار درسته؟
```

❌ WRONG (what happened this session): Run searches, collect data into variables, silently process it all, start writing Python code, user never sees what you found. Result: user says "منم نمیبینم ک اینکارو کرده باشی سرچ کن قشنگ".

### Step 4: Present Only What the User Provided — NO Extra Additions
**CRITICAL RULE: When the user sends a file and says "همینا باشه" (just these), reproduce EXACTLY what they provided. Do NOT add:**
- Projects found on their GitHub that they didn't list in their file
- Sections they didn't include (summary, cover letter intro, etc.)
- Additional skills or descriptions you think would be good
- Any "توضیحات اضافی" (extra explanations)

If you find more info on their GitHub or elsewhere, ask first: "توی گیت‌هاتون پروژه‌های دیگه‌ای هست که اضافه کنم؟"

### Step 5: Get Location Details Right
- Never add "دورکاری" after a city/location unless the user explicitly said so
- Use the EXACT location (city, company office) the user provides
- If unsure about a location, ask rather than guess

### Step 4: Present Only What the User Provided — NO Extra Additions
**CRITICAL RULE: When the user sends a file and says &quot;اینو بزار کلا&quot; (just put all of this), reproduce EXACTLY what they provided. Do NOT add:**
- Projects found on their GitHub that they didn't list in their file
- Sections they didn't include (summary, cover letter intro, etc.)
- Additional skills or descriptions you think would be good
- Any &quot;توضیحات اضافی&quot; (extra explanations)

If you find more info on their GitHub or elsewhere, ask first: &quot;توی گیت‌هاتون پروژه‌های دیگه‌ای هست که اضافه کنم؟&quot;

### Step 5: Get Location Details Right
- Never add &quot;دورکاری&quot; after a city/location unless the user explicitly said so
- Use the EXACT location (city, company office) the user provides
- If unsure about a location, ask rather than guess

### Step 6: Present a Plan
Before generating the PDF, show the user the outline:
"این رزومه شامل این بخش‌هاست: ..."
Get their sign-off on structure before writing code.

### Step 7: Build with Testing
- Always test the output visually after generation
- The user might not have a PDF viewer that renders Persian correctly — offer to send a screenshot
- If text renders incorrectly, check arabic_reshaper FIRST before changing layout

### Common Pitfalls (User Frustration Signals)

| User says | What went wrong | Fix |
|-----------|----------------|------|
| "به هم ریخته" / "این چ چرته" | Persian text not reshaped — letters disconnected | Add arabic_reshaper + python-bidi to every string |
| "زمینه‌ها درست نیست" / "فعالیت‌ها درست نیست" | Wrong domain description — you generalized instead of researching | Research EACH technology domain explicitly: read Wikipedia, official docs. NEVER guess what a tool does |
| "حرفه‌ای نیست" | Layout is amateur, no design standards | Research professional templates before building (Zety, MaxResumes, LiveCareer) |
| "عنوان شغلی رو اشتباه گفتی" | Incorrect role title | Ask for exact official title from company — present 2-3 options for user to pick |
| "تحقیق کن" / "نمی‌دونم تحقیق کن" | You wrote content without understanding the domain | **#1 frustration signal**. STOP. Research each term via web search, THEN write. Don't start coding until you can explain each technology in 1-2 sentences |
| "توضیحات اضافی ندی" | You added content not in the user's original file | Reproduce EXACTLY what the user provided. Nothing more. |
| "مهارت‌ها راست‌چین چپ‌چینش خراب شده" | RTL alignment broken by mixed cell() + multi_cell() pattern | Use uniform approach — either all cell() for single-line items, or all multi_cell(). Avoid mixing label (fixed-width cell) + value (multi_cell) for RTL — it breaks alignment. |
| "شاهرود دورکاری نمیشه" | You added "دورکاری" after a city name when user didn't say it | Use exact location as provided. Never append working mode to city name. |
| English mixing looks wrong | English and Persian on same line without proper shaping | Wrap FULL mixed string in `fa()` at once |

### WORKFLOW RULE: Test Incrementally, Not All at Once

**This session generated 4 versions of the script** because each iteration tried to do everything at once. Instead:

1. **Generate ONE section at a time** — start with just the header and summary. Show to user.
2. **Add skills section next** — run, show, get feedback.
3. **Add experience section next** — test date positioning specifically.
4. **Add remaining sections**.

If the user says "به هم ریخته" or "خراب شده", **STOP adding new content** and fix the layout issue FIRST. Adding more sections while layout is broken multiplies the rework:

```
❌ WRONG: header + summary + skills + experience + projects + education + certificates
         all in one script, one call. User sees 7 broken sections at once.
         
✅ RIGHT: header + summary    → user reviews → fix
         + skills              → user reviews → fix
         + experience          → user reviews → fix  
         ... remaining sections
```

This also helps with `fpdf2`'s PDF rendering — you can visually inspect each section's alignment without the noise of other content pushing auto-page-breaks.

### MANDATORY: Visual Verification Before Delivery (pymupdf + vision_analyze)

**User expectation:** "از این به بعد قبل این ک کامل بسازی اسکیرن بگیر و برسی کامل" — BEFORE delivering any PDF, render it to images and verify with vision analysis.

```bash
pip install pymupdf  # one-time
```

**Verification script (run after every PDF generation):**

```python
import fitz  # pymupdf

doc = fitz.open("output.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=200)
    pix.save(f"/workspace/verify_page_{i+1}.png")
    print(f"Page {i+1}: {pix.width}x{pix.height}")
doc.close()
```

Then use `vision_analyze` to check each page:
```
vision_analyze(image_url="/workspace/verify_page_1.png",
    question="Examine this Persian resume. Check:
    1. Are Persian characters CONNECTED (not separated)?
    2. Is RTL direction correct?
    3. Any overlapping text?
    4. Any garbled characters?
    5. Are bullet points visible?
    6. Is spacing balanced?
    Rate 1-10.")
```

**Only deliver to the user after verification scores 8/10+.** If below 8, fix issues first, re-render, re-verify.

## References

- `references/reportlab-vs-fpdf2-production-test.md` — Head-to-head comparison: reportlab scored 9/10, fpdf2 scored broken. Includes production-ready code pattern and verification workflow.
- `references/session-2025-07-14-resume-amirreza.md` — Session research record: user corrections, GitHub profile scan, sources used for domain research
- `references/session-2026-07-15-resume-amirreza-v2.md` — Session v2 record: RTL alignment fixes (skills section cell+multi_cell, experience date set_xy), font discovery, and the &quot;test incrementally&quot; workflow rule
- `references/session-2026-07-15-resume-final-text.md` — Session final: user-provided exact Persian text (processed, no emoji), font variant selection guidance (FD vs non-FD for Arabic/Persian digits), and the English-digit requirement for professional resumes
- `references/automation-ai-domain-terms.md` — Accurate domain terminology for Automation/AI engineer resumes (n8n, Hermes Agent, RAG Agent, etc.) sourced from Wikipedia and official docs
- `references/persian-docx-with-vazir.md` — Persian DOCX generation with python-docx + Vazir font: RTL patterns, helper functions, pitfalls, no arabic_reshaper needed
- `references/fpdf2-compatibility-notes.md` — Version-specific pitfalls: `uni` parameter removed in v2.5.1, only B/I style characters valid, font weight workarounds
- `templates/resume-generator.py` — **Production-ready, runnable template.** Copy this file, edit the `RESUME` dict at the top, and run. Features: professional header with background, flat or categorized skills, location-aware city fields, blue accent lines.
