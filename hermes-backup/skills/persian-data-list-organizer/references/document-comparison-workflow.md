# Document Comparison Workflow — Reference

## Pattern

User sends two files:
1. **Reference file** (PDF or Excel) — the authoritative inventory list, often with asset codes, brand/model, assignee info
2. **User's file** (Excel) — their own simplified version, usually just item name + quantity + category

Goal: identify what's missing, what has quantity discrepancies, and what the user added beyond the reference.

## PDF Text Extraction

Use pymupdf (pre-installed on Hermes):
```python
import pymupdf
doc = pymupdf.open(path)
for page in doc:
    print(page.get_text())
```

Common issues with Persian office PDFs:
- Column alignment is often jumbled in extraction (RTL/LTR mix)
- Asset codes may be separated from item names
- Brand/model may appear inline with item name, not in separate columns
- Some cells span multiple lines — reconstruct manually from raw text

## Comparison Output Structure

Deliver as `.md` file with three sections:

```
## ❌ اقلام کسر شده (در PDF هست ولی در Excel نیست)
| ردیف | کالا | تعداد | کد مرجع |
|------|------|-------|---------|

## ⚠️ اختلاف تعداد در اقلام مشترک
| کالا | تعداد PDF | تعداد Excel | تفاوت |
|------|-----------|-------------|--------|

## 🟢 اقلام اضافی (فقط در Excel)
| ردیف | کالا | تعداد |
|------|------|-------|
```

## Direction B: Delta / "What's New?" Pattern

When the user asks "چیا تو این فایل هست ک تو فایل قبلی نیست", they want what's ADDED or CHANGED — the inverse of gap analysis.

### Output Structure

```markdown
## 🆕 موارد جدید (فقط در فایل جدید وجود دارد)

### اموال — کد جدید
| ردیف | کد | تحویل‌گیرنده | برند | مدل | توضیحات |
|------|-----|-------------|------|-----|---------|

### اقلام — قلم جدید
| ردیف | قلم | تعداد | توضیح |
|------|-----|-------|-------|

## ✏️ تغییرات در موارد موجود
| مورد | فایل قدیم | فایل جدید |
|------|-----------|-----------|

## 🔍 اختلافات تعداد
| قلم | مرجع | موجود | تفاوت |
|-----|------|-------|-------|

## ❌ موجود نیست (فقط در فایل قدیم)
| کد | کالا |
|----|------|

## 📊 خلاصه
| وضعیت | تعداد |
|-------|-------|
| ✅ موجود | N قلم |
| ⚠️ اختلاف تعداد | N مورد |
| 🔄 وضعیت خاص | N مورد |
| ❌ موجود نیست | N مورد |
```

### Matching Rules for Direction B
- **Coded inventory**: match on **asset code** (exact integer match)
- **Uncoded inventory**: match on **normalized item name** (strip whitespace, ignore brand unless it changed)
- Changes to brand/model/description count as ✏️ تغییرات even if quantity is the same
- Items only in old file → ❌ موجود نیست
- Items only in new file → 🆕 موارد جدید

### Real Example (Session: 2026-07-18)
Older file: Excel with 50 coded assets (1800–1851) + 49 consumable items
Newer file: MD with same structure + 3 new items + 3 text changes

Result:
- 🆕 1 new code (1848), 2 new items (LED 120W ×12, چندراهی ۳ کورز ×1)
- ✏️ 3 text changes (جا قلم توری→قلمقاج توری, تخته پاک‌کن + suffix, رابط 12→30)
- ❌ 2 missing codes (1801, 1805) surfaced in summary

## Matching Strategy

- Match on **item description/brand+model**, NOT row number or position
- For items with assignee info (محمدی, مختاری, رحمانی, دفتر), match on item identity regardless of assignee
- Normalize Persian/English mixed names (e.g., "مانیتور Samsung" = "روتینام Samsung")
- Handle missing model info by matching on category + partial name

## Real Example (Session: 2026-07-17)

Reference PDF: مسئول دفتر شاهرود.pdf
- 57 asset rows (codes 1800-1850) + 49 consumable items
- Columns: کد اموال, تحویل‌گیرنده, برند, مدل, توضیحات
- Assignees: محمدی, مختاری, رحمانی, دفتر

User Excel: لیست_موجودی.xlsx
- 52 items in 8 categories
- Simplified: ردیف, دسته‌بندی, کالا, تعداد

Result: ~48 items missing from user's Excel, 16 items only in Excel (no reference), 1 quantity discrepancy (پرچم کوچک: 6 vs 4)

## Common PDF Extraction Issues

### Duplicate codes
PDF extraction may show the same asset code twice:
```
12
1812رﺣﻤﺎﻧﯽ
ﺳﺖ ﻣﻮس و ﮐﯿﺒﻮردTSCO
TK 7019W
13
1812ﻣﺤﻤﺪی
مکبو
```
**Diagnosis**: Two items with code 1812. The second is likely code 1813 (extraction error).
**Fix**: Check the sequence — if codes should be unique, the second occurrence is probably the next code.

### Garbled Persian text
Common misreadings in PDF extraction:
| Extracted | Actual | Meaning |
|-----------|--------|---------|
| روتینام | مانیتور | Monitor |
| ﭼﻮύﯽ | چوبی or توری | Wooden/Mesh |
| ﺟﺎﺭﯼ | جا قلم | Pen holder |
| ﮐﯿﺒﻮرد | کیبورد | Keyboard |
| ﺗﺤﻮﱘﻞ | تحویل | Delivery |

### Row numbering vs asset codes
PDF row numbers (1, 2, 3...) are NOT the same as asset codes (1800, 1801...). Always extract the code column separately and map it to the item.

## Correction Iteration Pattern

When the user reviews the file and provides corrections:

1. **List all corrections first** before applying — don't apply one at a time
2. **Check for cascading effects** — changing one item might affect counts of others
3. **Confirm ambiguous corrections** — "منظورتون ۱۸۱۲ هم TSCO هست؟" is better than guessing
4. **Apply all corrections in one patch** — use the patch tool for efficiency
5. **Regenerate the file** after all corrections are applied
6. **Send the updated file** via MEDIA: syntax

### Example correction flow
```
User: "مانیتور ۴ عدد" → Check which code is the 4th monitor
User: "وبکم هم ستاس" → Add the missing webcam code
User: "موس کیبورد ستا هست نه دوتا" → Verify TSCO count, add missing code
```

Each correction should be verified against the PDF reference before applying.

## ⚠️ Critical Lesson: Code Shifting Errors

**Do NOT shift codes when correcting items.** This was the #1 source of errors in the 2026-07-17 session.

When the user says "مک‌بوک رو کن وبکم", the agent shifted codes 1813→1816, 1814→1817, etc., which cascaded into:
- Duplicate codes (two items at 1819)
- Wrong item assignments (HP EliteDesk ended up at wrong codes)
- 6+ correction cycles before the list was correct

**Correct approach:**
1. Change ONLY the specific items mentioned
2. Verify the count from the source PDF
3. List the affected codes before editing
4. Do NOT assume subsequent items need shifting

**Persian colloquial numbers to watch for:**
- "ستا" = 3 (not "set")
- "دوتا" = 2
- "چهارتا" = 4

User frustration signals that mean "STOP AND CHECK THE SOURCE":
- "داری روانیم می‌کنی" = you're driving me crazy
- "فهرست اصلی رو چک کن" = check the main list
- "باز اشتباه کردی" = you made a mistake again
