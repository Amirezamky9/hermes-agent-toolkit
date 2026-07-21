#!/usr/bin/env python3
"""Example: Generate a professional Persian resume PDF using fpdf2 + Vazir font.
Usage:  python3 resume-example.py
Output: Resume_Amirreza_Mokhtari.pdf
"""

from fpdf import FPDF
import os

FONT_PATH = os.path.expanduser("~/.fonts/Vazir-Regular.ttf")
FONT_BOLD_PATH = os.path.expanduser("~/.fonts/Vazir-Bold.ttf")


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("Vazir", "", FONT_PATH)
        self.add_font("Vazir", "B", FONT_BOLD_PATH)
        self.set_auto_page_break(auto=True, margin=18)

    # ── Header block ──────────────────────────────────────────────
    def header_block(self):
        self.set_font("Vazir", "B", 22)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, "امیررضا مختاری", new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Vazir", "", 12)
        self.set_text_color(73, 80, 87)
        self.cell(0, 7, "طراح اتوماسیون و هوش مصنوعی | Automation & AI Engineer",
                  new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Vazir", "", 9)
        self.set_text_color(52, 58, 64)
        contact = "ایمیل: amirrezamokhtari2000@gmail.com    تلفن: 09115110174    ایران"
        self.cell(0, 6, contact, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)

    # ── Section title with underline ──────────────────────────────
    def section_title(self, title):
        self.set_font("Vazir", "B", 13)
        self.set_text_color(13, 110, 253)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", align="R")
        self.set_draw_color(13, 110, 253)
        self.set_line_width(0.5)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(3)

    # ── Bullet point (Persian RTL) ────────────────────────────────
    def bullet(self, text, bold_prefix=""):
        self.set_font("Vazir", "", 10)
        self.set_text_color(33, 37, 41)
        if bold_prefix:
            self.set_font("Vazir", "B", 10)
            self.write(5, bold_prefix + " ")
            self.set_font("Vazir", "", 10)
        self.multi_cell(0, 5, "• " + text, align="R")
        self.ln(1)

    # ── Job entry (company, period, role, bullet items) ───────────
    def job_entry(self, company, period, role, items, is_last=False):
        self.set_font("Vazir", "B", 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 6, company, new_x="LMARGIN", new_y="NEXT", align="R")

        self.set_font("Vazir", "", 9)
        self.set_text_color(108, 117, 125)
        self.cell(0, 5, period, new_x="LMARGIN", new_y="NEXT", align="R")

        self.set_font("Vazir", "", 10)
        self.set_text_color(73, 80, 87)
        self.cell(0, 5, role, new_x="LMARGIN", new_y="NEXT", align="R")
        self.ln(1)

        for item in items:
            self.bullet(item)
        if not is_last:
            self.ln(2)

    # ── Convenience for a paragraph ─────────────────────────────
    def multi_line(self, text, size=10, bold=False):
        style = "B" if bold else ""
        self.set_font("Vazir", style, size)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 5.5, text, align="R")
        self.ln(0.5)

    # ── Skill category row ────────────────────────────────────────
    def skill_row(self, title, body):
        self.set_font("Vazir", "B", 10)
        self.set_text_color(33, 37, 41)
        self.write(5, title + " ")
        self.set_font("Vazir", "", 10)
        self.set_text_color(73, 80, 87)
        self.multi_cell(0, 5, body, align="R")
        self.ln(0.5)


# ═══════════════════════════════════════════════════════════════════
#  BUILD DOCUMENT
# ═══════════════════════════════════════════════════════════════════
pdf = ResumePDF()
pdf.add_page()

# ── Header ────────────────────────────────────────────────────────
pdf.header_block()

# ── Summary ───────────────────────────────────────────────────────
pdf.section_title("خلاصه")
pdf.multi_line(
    "طراح اتوماسیون و هوش مصنوعی با حدود ۸ ماه سابقه کار حرفه‌ای در دو شرکت فناوری. "
    "مسلط به طراحی ربات‌های تلگرام و بله، ساخت دیجیتال‌ورکر با n8n، پیاده‌سازی RAG Agent، "
    "اتوماسیون فرآیندها با ابزارهای مدرن و تحلیل دیتا با PostgreSQL. "
    "دارای تجربه کار با ابزارهای Google (Sheets, BigQuery) و اسکرپ داده از وبسایت‌ها."
)
pdf.ln(2)

# ── Work Experience ───────────────────────────────────────────────
pdf.section_title("سابقه کاری")

pdf.job_entry(
    "شرکت دنیا هوشمند کندو",
    "آبان ۴۰۴ – اسفند ۴۰۴ (حدود ۴ ماه)",
    "طراح اتوماسیون و هوش مصنوعی",
    [
        "طراحی و پیاده‌سازی دیجیتال‌ورکر با n8n برای اتوماسیون فرآیندهای وب",
        "اسکرول و اسکرپ هوشمند داده از وبسایت‌ها و جمع‌آوری خودکار اطلاعات",
        "اتوماتیک‌سازی گردش کار شرکت‌های مختلف با ترکیب ابزارهای مدرن",
        "ساخت RAG Agent برای پاسخگویی هوشمند مبتنی بر دانش سازمانی",
    ],
)

pdf.job_entry(
    "شرکت اندیشه هوشمند نوآوران",
    "مرداد ۴۰۴ – آبان ۴۰۴ (۳ ماه) — دورکاری",
    "طراح اتوماسیون",
    [
        "طراحی و توسعه ربات‌های تلگرام برای اتوماسیون خدمات و ارتباط با مشتری",
        "کار با ابزارهای Google Workspace: Sheets, BigQuery برای تحلیل و مدیریت داده",
        "طراحی و پیاده‌سازی فرآیندهای اتوماسیون با n8n",
    ],
    is_last=True,
)
pdf.ln(2)

# ── Skills ────────────────────────────────────────────────────────
pdf.section_title("مهارت‌ها")

skills_data = [
    ("اتوماسیون:", "n8n — Hermes Agent — OpenClaw — طراحی و مدیریت گردش کار"),
    ("دیتابیس:", "PostgreSQL — SQL — طراحی جداول رابطه‌ای — تحلیل داده"),
    ("برنامه‌نویسی:", "Python — HTML — CSS"),
    ("Google Workspace:", "Google Sheets — BigQuery — ابزارهای اتوماسیون گوگل"),
    ("ربات و پیام‌رسان:", "تلگرام Bot API — بله — طراحی ربات FAQ"),
    ("هوش مصنوعی:", "RAG Agent — ایجنت‌های هوشمند — Prompt Engineering"),
    ("زبان:", "فارسی (زبان مادری) — انگلیسی (B2)"),
]
for title, body in skills_data:
    pdf.skill_row(title, body)

pdf.ln(2)

# ── Education ─────────────────────────────────────────────────────
pdf.section_title("تحصیلات")
pdf.set_font("Vazir", "B", 11)
pdf.set_text_color(33, 37, 41)
pdf.cell(0, 6, "کارشناسی پیوسته مهندسی کامپیوتر",
         new_x="LMARGIN", new_y="NEXT", align="R")
pdf.set_font("Vazir", "", 10)
pdf.set_text_color(73, 80, 87)
pdf.cell(0, 5, "دانشگاه آزاد اسلامی شاهرود | ورودی ۱۴۰۱",
         new_x="LMARGIN", new_y="NEXT", align="R")
pdf.ln(3)

# ── Projects ──────────────────────────────────────────────────────
pdf.section_title("پروژه‌ها و دستاوردها")
for p in [
    "ربات تلگرام و بله — طراحی و پیاده‌سازی ربات‌های پیام‌رسان برای اتوماسیون خدمات",
    "ایجنت FAQ — ساخت agent هوشمند برای پاسخگویی خودکار به سوالات متداول",
    "اتوماسیون جمع‌آوری داده سایت کوکوین — اسکرپ داده‌های بازار رمزارز به صورت خودکار",
    "تحلیل داده با PostgreSQL — طراحی پایگاه داده رابطه‌ای و تحلیل داده‌های ساختاریافته",
    "اسکرپ و اسکرول پیشرفته — جمع‌آوری هوشمند داده از وبسایت‌های داینامیک",
]:
    pdf.bullet(p)

pdf.ln(2)

# ── Certifications ────────────────────────────────────────────────
pdf.section_title("گواهینامه‌ها و دوره‌ها")
for c in [
    "مدرک برق ساختمان (۳ مدرک) — سازمان فنی و حرفه‌ای کشور",
    "دوره آموزشی n8n — (یوتیوب) — خودآموز تخصصی",
    "دوره n8n — در حال برگزاری (شروع: تیر ۱۴۰۴)",
]:
    pdf.bullet(c)

pdf.ln(2)

# ── Other ─────────────────────────────────────────────────────────
pdf.section_title("سایر")
pdf.set_font("Vazir", "", 10)
pdf.set_text_color(33, 37, 41)
pdf.multi_cell(0, 5.5,
    "مدیریت پیج گلخانه باغ کاکتوس با ۲۰۰۰+ فالوور (۱۳۹۷ – ۱۴۰۲) — "
    "تجربه در مدیریت محتوا، بازاریابی و ارتباط با مخاطب در فضای مجازی",
    align="R",
)

# ── Output ────────────────────────────────────────────────────────
output_path = os.path.expanduser("~/Resume_Amirreza_Mokhtari.pdf")
pdf.output(output_path)
print(f"✅ Resume saved to: {output_path}")
