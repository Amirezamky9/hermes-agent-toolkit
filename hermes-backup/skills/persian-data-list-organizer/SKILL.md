---
name: persian-data-list-organizer
description: >
  Process unstructured Persian/Farsi inventory lists from users into organized,
  shareable Excel (.xlsx) files. Covers raw-list parsing, categorization, duplicate
  detection, correction iteration, openpyxl file generation, and document comparison
  (reference PDF vs user list gap analysis). Delivers as .md/.xlsx files, not inline text.
triggers:
  - user sends a raw Persian text list (inventory, office supplies, warehouse items)
  - user says "لیست", "مرتب کن", "دسته‌بندی کن", "فایل اکسل", "گوگل شیت"
  - user dumps items with mixed formatting (tallles/numbers, Farsi/English mix, scattered order)
  - user asks for "قابل کپی" or "فایل" format
  - user sends two files (PDF + Excel) and asks to compare or find gaps ("چیا کسر داره", "مقایسه کن")
  - user sends two files and asks what's new/different ("چیا تو این فایل هست ک تو فایل قبلی نیست")
  - user says "این خواندنی نیس" — means switch to file delivery
---

# Persian Data-List Organizer

## When This Skill Applies

Use this when a Persian (Farsi)-speaking user sends a raw, unstructured list of items — inventory, office supplies, equipment, warehouse stock — and asks you to organize it. **Do NOT default to Markdown tables for Persian lists on Telegram.** Persian text in Telegram markdown tables often renders poorly (alignment issues, mixed RTL/LTR). Go straight to generating an `.xlsx` file.

## Workflow

### Step 1 — Parse & Deduplicate

The user will typically send a list like:
```
16 تا تابلو 
4 عدد مانیتور 
دو عدد کیس 
یک عدد پرینتر 
...
```

Key parsing rules:
- Numbers may be written as Persian digits (۴), English digits (4), or Farsi words (دو, یک, سه, چهارده)
- Units may be: `عدد`, `تا`, `دست`, `بسته`, `کارتون`, or omitted
- Items may be scattered (same item listed twice at different positions in the message)
- Some items use English names mixed with Farsi (e.g., "مودم CPE", "سویچ D-Link")

Detection:
- Keep a set of seen item names (normalized). When a near-duplicate appears, ask the user if it's a separate type or a duplicate.
- Common duplicate signals: first and last of list both say "تابلو", two entries for "ساعت"

### Step 2 — Categorize

Sort items into standard Persian inventory categories:

| Category | Persian Label | Examples |
|----------|--------------|---------|
| Electronics & IT | 🖥️ الکترونیک و IT | مانیتور, کیس, مودم, پرینتر, ساعت, وبکم, هدفون, موس پد, سویچ |
| Signs & Flags | 📋 تابلو و پرچم | تابلو, پرچم بزرگ/کوچک, تابلو سفال/لوگو |
| Stationery | ✏️ لوازم تحریر | خودکار, مداد, پاکن, غلط‌گیر, خط‌کش, قیچی, کاتر, منگنه, سبد تحریر |
| Batteries | 🔋 باتری | باتری قلمی, باتری نیم‌قلم |
| Kitchen & Serving | 🍳 آشپزخانه و پذیرایی | یخچال, مایکروفر, چایی‌ساز, سرویس غذاخوری, قاشق چنگال, لیوان, قندان |
| Packaging & Office | 📦 بسته‌بندی و اداری | پاکت نامه, کیف مدارک, سررسید, کارتن کارت تبلیغ |
| Cleaning | 🧹 نظافت | تی, جارو, سطل آشغال, دستمال, کیسه زباله |
| Misc | 🔌 متفرقه | سه‌راهی, پرچم |

### Step 3 — Generate Excel File

Use `openpyxl` to create a `.xlsx` file. Critical formatting:

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Setup
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "لیست موجودی"   # Persian sheet title

# Style constants
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=12)
normal_font = Font(size=11)
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# Columns: ردیف | دسته‌بندی | کالا | تعداد
headers = ["ردیف", "دسته‌بندی", "کالا", "تعداد"]
widths = [6, 24, 42, 10]
```

Formatting rules:
- **Header row**: dark blue background (#1F4E79), white bold text, centered
- **Columns**: ردیف (auto-number), دسته‌بندی (category name), کالا (item name), تعداد (quantity)
- **Freeze top row** so headers stay visible
- **Borders**: thin borders on all cells
- **Alignment**: center for ردیف, دسته‌بندی, and تعداد; left for کالا
- Emoji category icons are fine in the Excel file (they render well)

### Step 4 — Handle Corrections

The user WILL have corrections. Be ready to iterate:
- "مارک دون بهم ریخته" = "the markdown is messy" → they want a FILE, not text
- "تکراری بود" = "it was a duplicate" → merge the two entries, don't double-count
- "اگه نیست اضافه کن" = "if it's not there, add it" → add missing items
- The user may remember new items after seeing the first draft
- Always confirm you understood the correction before regenerating

After each correction cycle, regenerate the full file.

### Step 5 — Deliver

Send the file via `MEDIA:/path/to/file.xlsx` syntax. Tell the user:
- The file is ready for **Google Sheets** upload (direct upload to Google Drive works)
- Highlight what changed in this version vs the last one (use a markdown table of changes)

## Step 6 — Document Comparison Workflow

There are two comparison directions. Choose based on user intent:

### Direction A: Gap Analysis (reference → user list)
User asks "چیا کسر داره" / "مقایسه کن" / "چیا ندارم". See `references/document-comparison-workflow.md` for the full pattern.

### Direction B: Delta / What's New (new file → old file)
User asks "چیا تو این فایل هست ک تو فایل قبلی نیست" / "چه فرقی داره". They want to know what was ADDED or CHANGED in the newer file.

**Workflow:**
1. Load older file (usually Excel) into a dict keyed by item identity
2. Load newer file (usually MD) into same structure
3. Compare and produce these sections:
   - **🆕 موارد جدید**: items/codes in the newer file that DON'T exist in the older
   - **✏️ تغییرات**: items present in both but with different names, quantities, or details
   - **🔍 اختلافات تعداد**: quantity mismatches (if the newer file tracks reference vs actual counts)
   - **❌ موجود نیست**: items in older file but absent from newer (if relevant)
   - **📊 خلاصه**: count of items by status
4. For coded inventory: compare by **code number** (exact match on asset code)
5. For uncoded inventory: compare by **item name/description** (normalized)
6. Deliver as `.md` file via `MEDIA:/path/to/file`

### Multi-sheet Excel handling
User's Excel files may have multiple sheets (e.g., "اموال" + "اقلام"). Always iterate all sheets:
```python
wb = openpyxl.load_workbook(path, data_only=True)
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    # process each sheet independently
```
Key each sheet's items by its own primary key (codes for اموال, item names for اقلام).

1. **Extract text from reference** (usually PDF):
   ```python
   import pymupdf
   doc = pymupdf.open('/path/to/reference.pdf')
   for page in doc:
       print(page.get_text())
   ```
   pymupdf is pre-installed on Hermes. Do NOT rely on `pdftotext` (often missing).

2. **Parse the reference** into a structured list (code, item, brand, model, description, assignee). Persian PDFs from office environments often have jumbled column alignment — reconstruct the table manually from the extracted text.

3. **Extract user's list** (usually Excel via openpyxl or pandas).

4. **Compare by key** — match on item name/description (not row number, since ordering differs). Produce three sections:
   - ❌ **کسر شده**: items in reference but missing from user's list
   - ⚠️ **اختلاف تعداد**: items present in both but with different quantities
   - 🟢 **اضافی**: items only in user's list (no reference match)

5. **Deliver as a .md file** (see Delivery Format below).

## Delivery Format — CRITICAL

**Persian users on Telegram expect downloadable files, not long inline text.** After any substantial output (comparison report, organized list, analysis):

- Generate a `.md` file for reports/analysis/comparisons
- Generate a `.xlsx` file for inventory lists and tabular data
- Send via `MEDIA:/path/to/file` syntax

The user will explicitly tell you "این خواندنی نیس" (this is not readable) if you paste a long report as Telegram text. **Do not wait for this correction** — default to file delivery for anything over ~15 lines.

Inline Telegram messages are fine for: quick confirmations, short summaries (< 10 items), yes/no answers, and status updates.

## Step 7 — Coded Inventory Lists (Asset Management)

When the user works with **coded inventory** (asset codes like 1800-1850):

### Creating a subset list from codes
The user will provide specific codes and ask for a new list:
```
این کد ها موجود :
1800
1802
1803
تا 1850
```

Workflow:
1. Extract items matching those codes from the reference PDF
2. Create a clean .md file with: ردیف | کد | تحویل‌گیرنده | برند | مدل | توضیحات
3. ALWAYS ask before creating — present the list first for confirmation

### Handling corrections on coded lists
Users will review and correct items iteratively:
- "هندزفری رو کن هدست" = change the item name
- "مک بوک هارو کن وبکم" = replace one item type with another
- "مانیتور ۴ عدد" = correct the quantity
- "وبکم هم ستاس" = webcams are also 3 (colloquial "ستا" = 3)

**Critical pattern**: When user says "X رو کن Y", they mean "change X to Y". Apply ONLY that specific change. Do NOT automatically shift subsequent codes.

**THE BIGGEST PITFALL — Code shifting**: When the user says "مک‌بوک رو کن وبکم", change ONLY the MacBook codes to webcam. Do NOT assume that adding items shifts all subsequent codes by +1. Code shifting creates cascading errors — every shifted code needs verification, and one wrong shift corrupts the entire rest of the list. If the user says "X رو N تاست" (X is N items), verify the COUNT from the source PDF first, then list the specific codes before changing. Only shift codes if the user explicitly confirms the new code assignments.

**Verify before every change**: Open the extracted PDF text and COUNT items yourself. The agent's memory of "how many monitors there are" is unreliable after multiple correction cycles. Always go back to the source.

### PDF extraction issues with coded lists
- **Duplicate codes**: PDF extraction may show the same code twice (e.g., 1812 appears for both TSCO and MacBook). This is a scanning/extraction error — the second occurrence is likely the next code (1813).
- **Garbled text**: "روتینام" = مانیتور (monitor), "ﭼﻮύﯽ" = چوبی or توری, "ﺟﺎﺭﯼ" = جا قلم
- **Row numbering mismatch**: PDF row numbers may not align with asset codes — reconstruct mapping manually.

## Pitfalls

### Data Accuracy — #1 Source of User Frustration
- **ALWAYS verify from the source PDF before applying ANY change.** When the user says "۴ تاست" or "ستا هست", open the PDF text output and COUNT the items yourself before editing. Do NOT guess or rely on memory. The #1 source of user frustration is repeated corrections on the same item because the agent didn't check the source.
- **Do NOT shift asset codes when correcting items.** If the user says "۱۸۱۲ وبکم هست نه TSCO", change ONLY that one code. Do NOT assume codes 1813+ need shifting. Code shifting creates cascading errors that compound with each correction cycle.
- **When user frustration signals appear** ("داری روانیم می‌کنی", "باز اشتباه کردی", "فهرست اصلی رو چک کن"), STOP and re-read the source document from scratch. The user is telling you that your memory-based approach is failing — go back to the primary source.
- **Confirm before bulk changes**: If the user says "۳ تاست" (it's 3), list the specific items/codes you plan to change BEFORE editing. Ask if ambiguous.
- **Don't shift items when correcting**: When the user says "اینا رو اشتباه زدیم", fix ONLY the items mentioned. Do NOT assume neighboring items are also wrong.

### Persian Colloquial Numbers
Users often use colloquial Persian for counts:
| Spoken | Meaning |
|--------|---------|
| دوتا / دوتاش | 2 |
| سه‌تا / ستا / سه‌تاش | 3 |
| چهارتا | 4 |
| پنجتا | 5 |

"ستا هست" = "there are 3 of them". Don't confuse "ستا" (colloquial for 3) with "ست" (set).

### Formatting & Delivery
- **Do NOT default to Markdown tables** for Persian lists on Telegram. They break with RTL text and long Persian words. Go straight to generating an `.xlsx` file.
- **Do NOT paste long reports as inline Telegram text.** Default to file delivery proactively for anything over ~15 lines. Send via `MEDIA:/path/to/file` syntax.
- **File delivery is mandatory for lists**: Always deliver as .md or .xlsx file for anything over 10 items.

### Technical
- **openpyxl may not be installed** — install it first with `pip install openpyxl` before attempting to create the file. NOTE: `execute_code` sandbox may not have it — use `terminal()` instead for openpyxl operations.
- **Persian digits vs English digits**: Users may mix ۴/4, ۱۲/12 in the same list. Normalize all to English digits in the spreadsheet.
- **RTL text in openpyxl**: openpyxl handles Persian text natively, but column widths should be generous enough (42+ chars for item column) to avoid clipping.
- **Version tracking**: Keep a changelog of corrections so the user doesn't repeat themselves.

## Verification

The file should open correctly in:
- Google Sheets (upload to Google Drive → Open with Google Sheets)
- Microsoft Excel
- LibreOffice Calc

Quick check: `python3 -c "import openpyxl; wb=openpyxl.load_workbook('/workspace/لیست_موجودی.xlsx'); print(wb.active.title, wb.active.max_row, 'rows')"`

## Related

- Install openpyxl: `pip install openpyxl`
- PDF extraction: use `pymupdf` (pre-installed), NOT `pdftotext` (often missing)
- See `references/document-comparison-workflow.md` for the full comparison pattern and worked example
- See `references/worked-example-office-inventory.md` for the original list-organizer worked example
