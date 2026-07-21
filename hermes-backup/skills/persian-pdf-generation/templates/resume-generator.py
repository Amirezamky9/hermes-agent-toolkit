#!/usr/bin/env python3
"""
Production-ready Persian Resume Generator.

Features:
  - Professional header with background
  - Achievement-oriented bullet points
  - Skills section with two modes: categorized (label: value) or flat (bullet list)
  - Blue accent lines for sections
  - Proper arabic_reshaper + bidi rendering
  - Vazir font for clean Persian typography

Usage:
  1. Edit the RESUME dict below
  2. python3 resume-generator.py
  3. Find your PDF in the current directory

Design rules:
  - MAX 2 pages (prefer 1 for <5 years experience)
  - NO emoji (Vazir has no emoji glyphs)
  - Color: navy header, blue section underlines
  - Bullet points for achievements, not paragraphs
"""

from fpdf import FPDF
import os
import arabic_reshaper
from bidi.algorithm import get_display

FONT = os.path.expanduser("~/.fonts/Vazir-Regular.ttf")
FONT_B = os.path.expanduser("~/.fonts/Vazir-Bold.ttf")

# ─── Colors ───
C_PRIMARY = (25, 55, 109)   # Navy
C_ACCENT  = (41, 112, 198)  # Blue
C_TEXT    = (33, 37, 41)     # Dark
C_MUTED   = (108, 117, 125)  # Gray
C_LIGHT   = (245, 247, 250)  # Light bg


def fa(t):
    """Reshape Persian text for fpdf2 rendering."""
    return get_display(arabic_reshaper.reshape(t))


# ═══════════════════════════════════════════════
# EDIT THIS DICT for each new person/resume
# ═══════════════════════════════════════════════
RESUME = {
    # ─── Identity ───
    "name": "امیررضا مختاری",
    "title": "مهندس اتوماسیون و هوش مصنوعی | Automation & AI Engineer",
    "contact": "ایمیل: amirrezamokhtari2000@gmail.com  |  تلفن: 09115110174",

    # ─── Summary (optional — set None to skip) ───
    "summary": None,

    # ─── Work Experience ───
    # Each entry: company, subtitle (city only — no "دورکاری" unless user says so),
    #             period, bullets (list of strings)
    "experiences": [
        {
            "company": "شرکت اندیشه هوشمند نوآوران",
            "subtitle": "قم",
            "period": "مرداد تا آبان ۴۰۴",
            "bullets": [],
        },
        {
            "company": "شرکت دنیا هوشمند کندو",
            "subtitle": "شاهرود",
            "period": "آبان تا اسفند ۴۰۴",
            "bullets": [],
        },
        {
            "company": "تاسیس و اداره گلخانه باغ کاکتوس",
            "subtitle": "شاهرود، جاده امیریه",
            "period": "۱۳۹۷ تا ۱۴۰۲",
            "bullets": [],
        },
    ],

    # ─── Skills ───
    # MODE A (categorized): tuple of (label, description)
    # MODE B (flat): list of strings — each becomes a bullet
    # Set to empty list [] to skip the section
    "skills": [
        "اتوماسیون n8n",
        "ایجنت‌های هوشمند Hermes",
        "بات تلگرام و بله (با پایتون و n8n)",
        "دیتابیس (,SQL, postgresql)",
        "پایتون",
        "برق ساختمان (مدرک فنی حرفه‌ای)",
        "مسلط به زبان انگلیسی — سطح B2",
        "دوره دیتا ساینس (کاویانی)",
        "فرانت‌اند مبتدی",
        "شبکه مبتدی",
    ],

    # ─── Education ───
    "education": ("کارشناسی مهندسی کامپیوتر", "دانشگاه آزاد اسلامی، واحد شاهرود (۱۴۰۱ تا ۱۴۰۵)"),

    # ─── Projects (optional — set empty list to skip) ───
    "projects": [],

    # ─── Certifications (optional — set empty list to skip) ───
    "certifications": [
        "برق ساختمان (مدرک فنی حرفه‌ای)",
        "دوره دیتا ساینس (کاویانی)",
    ],

    # ─── Other / Online Profiles (optional — set None to skip) ───
    "profiles": "GitHub: github.com/Amirezamky9",

    # ─── Extra bullets (optional) ───
    "other": None,
}


# ═══════════════════════════════════════════════
# PDF Builder — do not edit below unless needed
# ═══════════════════════════════════════════════
class ResumePDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("V", "", FONT)
        self.add_font("V", "B", FONT_B)
        self.set_auto_page_break(True, 15)

    # Right-aligned cell
    def rc(self, txt, sz=10, st="", col=C_TEXT, h=5.5):
        self.set_font("V", st, sz)
        self.set_text_color(*col)
        self.cell(0, h, fa(txt), new_x="LMARGIN", new_y="NEXT", align="R")

    # Right-aligned multi-cell (paragraph)
    def rm(self, txt, sz=10, st="", col=C_TEXT, h=5.5):
        self.set_font("V", st, sz)
        self.set_text_color(*col)
        self.multi_cell(0, h, fa(txt), align="R")
        self.ln(0.5)

    def sec(self, title):
        self.rc(title, 12, "B", C_PRIMARY, 7)
        self.set_draw_color(*C_ACCENT)
        self.set_line_width(0.6)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(3)

    def bul(self, txt, sz=10):
        self.set_font("V", "", sz)
        self.set_text_color(*C_TEXT)
        self.multi_cell(0, 5, fa("• " + txt), align="R")
        self.ln(0.8)

    def header_block(self):
        self.set_fill_color(*C_LIGHT)
        self.rect(0, 0, 210, 38, "F")
        self.set_fill_color(*C_ACCENT)
        self.rect(0, 38, 210, 1.5, "F")
        self.ln(4)
        self.rc(RESUME["name"], 22, "B", C_PRIMARY, 9)
        self.rc(RESUME["title"], 12, "", C_ACCENT, 6)
        self.ln(2)
        self.rc(RESUME["contact"], 9, "", C_MUTED, 5)
        self.ln(5)


def build():
    pdf = ResumePDF()
    pdf.add_page()
    pdf.header_block()

    # ─── Summary ───
    if RESUME.get("summary"):
        pdf.sec("خلاصه")
        pdf.rm(RESUME["summary"])
        pdf.ln(2)

    # ─── Education ───
    if RESUME.get("education"):
        pdf.sec("تحصیلات")
        pdf.rc(RESUME["education"][0], 10, "B", C_PRIMARY)
        pdf.rc(RESUME["education"][1], 10, "", C_MUTED)
        pdf.ln(3)

    # ─── Experience ───
    if RESUME.get("experiences"):
        pdf.sec("سوابق کاری")
        for exp in RESUME["experiences"]:
            pdf.rc(exp["company"], 11, "B", C_PRIMARY)
            pdf.rc(exp["subtitle"], 10, "", C_MUTED)
            pdf.rc(exp["period"], 9, "", C_MUTED)
            pdf.ln(2)
            for b in exp["bullets"]:
                pdf.bul(b)
        pdf.ln(2)

    # ─── Skills ───
    if RESUME.get("skills"):
        pdf.sec("مهارت‌ها")
        for s in RESUME["skills"]:
            # Support both tuple (categorized) and str (flat) items
            if isinstance(s, tuple):
                pdf.rm(f"{s[0]} {s[1]}")
            else:
                pdf.bul(s)
        pdf.ln(1)

    # ─── Projects ───
    if RESUME.get("projects"):
        pdf.sec("پروژه‌ها")
        for p in RESUME["projects"]:
            pdf.bul(p)
        pdf.ln(1)

    # ─── Certifications ───
    if RESUME.get("certifications"):
        pdf.sec("گواهینامه‌ها و دوره‌ها")
        for c in RESUME["certifications"]:
            pdf.bul(c)
        pdf.ln(1)

    # ─── Online Profiles ───
    if RESUME.get("profiles"):
        pdf.sec("پروفایل آنلاین")
        pdf.set_font("V", "", 10)
        pdf.set_text_color(*C_ACCENT)
        pdf.cell(0, 5, RESUME["profiles"], new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(2)

    # ─── Other ───
    if RESUME.get("other"):
        pdf.sec("سایر")
        pdf.bul(RESUME["other"])

    out = f"Resume_{RESUME['name'].replace(' ', '_')}.pdf"
    pdf.output(out)
    print(f"✅ Resume saved: {out} ({os.path.getsize(out)/1024:.1f} KB)")


if __name__ == "__main__":
    build()
