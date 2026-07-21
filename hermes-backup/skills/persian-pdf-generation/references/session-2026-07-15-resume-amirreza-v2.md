# Session Research Record — Persian Resume v2 (امیررضا مختاری, 2026-07-15)

## Context

Updated GitHub profile README, then built a Persian PDF+DOCX resume.

## What Went Well

- **GitHub profile creation**: Smooth. Repos analyzed via API, README built from actual project data, pushed via git.
- **arabic_reshaper + bidi**: Eventually got Persian rendering working after initial attempt without it.
- **DOCX generation**: python-docx with `w:bidi` worked without reshaping.

## What Went Wrong (in priority order)

### 1. Persian text not reshaped in initial PDF (fpdf2)

**Symptom:** "فارسیش بهم ریخته" — letters disconnected, showing as separate glyphs.

**Root cause:** fpdf2 renders each Unicode glyph independently; Persian requires `arabic_reshaper` + `python-bidi` to join letters.

**Fix:** Wrap ALL Persian strings (even single words, even mixed Persian/English) in `fa()`:
```python
def fa(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
```

**Takeaway:** This is the #1 rule of fpdf2 + Persian. Never forget it.

### 2. Skills section RTL alignment broken

**Symptom:** "مهارت‌های فنی بهم ریخته" — label and items on same line not aligned.

**Root cause:** `cell()` + `multi_cell()` mix for RTL text. When `cell()` renders a bold label right-aligned, it claims width from the right, and the subsequent `multi_cell()` starts from a wrong x position.

**Fix:** Combine label and items into a single string passed to one `multi_cell()` call.

### 3. Date positioning on experience entries

**Symptom:** "تجربه حرفه‌ای تاریخ بهم ریخته" — date next to title misaligned.

**Root cause:** Mixing right-aligned `cell()` for title with left-aligned content for date — fpdf2's RTL mode doesn't support left-right split on one line cleanly.

**Fix:** Use `set_xy(left_x, get_y())` pattern: write company name right-aligned, `ln(0)` to stay on same line, then `set_xy()` to the left margin and write date left-aligned.

### 4. Four iterations of the generator script

**Root cause:** Tried to build the full resume in one script call instead of section-by-section.

**Fix:** Test incrementally — header first, then each section one at a time with user review between.

## 5. lxml TypeError: None vs string

**Symptom:** `rPr.set(qn('w:lang'), None)` → `TypeError: Argument must be bytes or unicode`.

**Fix:** Python-docx's underlying lxml rejects `None` as an attribute value. Pass `""` (empty string) or remove the call.

## Proven Patterns

### Robust font discovery (Hermes WebUI environment)
```python
def find_font_variant(name_part):
    candidates = [f for f in os.listdir("~/.fonts") if name_part in f and f.endswith(".ttf")]
    def score(fn): ...
    candidates.sort(key=score, reverse=True)
    return os.path.join(FONTS_DIR, candidates[0]) if candidates else None
```

### Experience entry with title + date on same line
```python
pdf.cell(0, 5, fa(title), align="R")
pdf.ln(5.5)  # title line height
pdf.cell(0, 4.5, fa(company), align="R")
pdf.ln(0)    # stay on same line height
pdf.set_xy(pdf.l_margin, pdf.get_y())
pdf.cell(0, 4.5, fa(date), align="L") 
pdf.ln(5)    # advance to next line
```

### Skills section (avoid cell+multi_cell mixing)
```python
combined = f"[ {label} ] {items}"
pdf.multi_cell(w=pdf.pw(), h=4.5, text=fa(combined), align="R")
```
