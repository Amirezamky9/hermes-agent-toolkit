#!/usr/bin/env python3
"""
Production-ready Persian Resume Generator using fpdf2 + arabic_reshaper + python-bidi.

Usage:
    python3 resume-template.py

Output: resume.pdf in current directory.

STRUCTURE (professional Persian resume standard):
  1. Header: name (large, centered), title, contact info
  2. Summary: 2-3 line professional profile
  3. Work Experience: company, date range, role, achievement bullets
  4. Skills: categorized (label: detail)
  5. Education: degree, university, year
  6. Projects: bullet list with brief description
  7. Certifications: name + issuer
  8. Other (optional)

DESIGN RULES enforced:
  - NO emoji/icons (Vazir font can't render them)
  - MAX 2 pages
  - Blue (#0d6efd) section underlines
  - Proper arabic_reshaper rendering for ALL Persian text
  - Achievement-oriented bullet points (not just duties)
"""

import os
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

# ── Configuration ─────────────────────────────────────────────
FONT_REGULAR = os.path.expanduser("~/.fonts/Vazir-Regular.ttf")
FONT_BOLD = os.path.expanduser("~/.fonts/Vazir-Bold.ttf")
OUTPUT = "resume.pdf"

# ── Text Helper ───────────────────────────────────────────────
def fa(text):
    """
    Reshape Persian/Arabic text for correct rendering.
    CRITICAL: fpdf2 renders each glyph independently — without this,
    "سلام" appears as "س ل ا م" (four separate glyphs).
    """
    if not text:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


# ── PDF Class ──────────────────────────────────────────────────
class ResumePDF(FPDF):
    """A4 Persian resume with professional styling."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("Vazir", "", FONT_REGULAR)
        self.add_font("Vazir", "B", FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=18)

    # ── Header ─────────────────────────────────────────────────
    def add_header(self, name, title, contact_lines):
        """RTL header block: name -> title -> contact (one line per item)."""
        self.set_font("Vazir", "B", 22)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, fa(name), new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Vazir", "", 12)
        self.set_text_color(73, 80, 87)
        self.cell(0, 7, fa(title), new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Vazir", "", 9)
        self.set_text_color(52, 58, 64)
        for line in contact_lines:
            self.cell(0, 5, fa(line), new_x="LMARGIN", new_y="NEXT", align="C")

        self.ln(3)

    # ── Section Titles ─────────────────────────────────────────
    def section(self, title):
        """Blue-underline section header."""
        self.set_font("Vazir", "B", 13)
        self.set_text_color(13, 110, 253)
        self.cell(0, 8, fa(title), new_x="LMARGIN", new_y="NEXT", align="R")

        y = self.get_y()
        self.set_draw_color(13, 110, 253)
        self.set_line_width(0.5)
        self.line(10, y, 200, y)
        self.ln(3)

    # ── Paragraph Text ─────────────────────────────────────────
    def paragraph(self, text, size=10):
        """Right-aligned paragraph."""
        self.set_font("Vazir", "", size)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 5.5, fa(text), align="R")
        self.ln(2)

    # ── Work Experience Entry ──────────────────────────────────
    def experience(self, company, period, role, bullets, is_last=False):
        """Single job entry: company bold, period gray, role, then bullet list."""
        self.set_font("Vazir", "B", 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 6, fa(company), new_x="LMARGIN", new_y="NEXT", align="R")

        self.set_font("Vazir", "", 9)
        self.set_text_color(108, 117, 125)
        self.cell(0, 5, fa(period), new_x="LMARGIN", new_y="NEXT", align="R")

        self.set_font("Vazir", "", 10)
        self.set_text_color(73, 80, 87)
        self.cell(0, 5, fa(role), new_x="LMARGIN", new_y="NEXT", align="R")
        self.ln(1)

        for b in bullets:
            self.bullet(b)

        if not is_last:
            self.ln(2)

    # ── Bullet Point ───────────────────────────────────────────
    def bullet(self, text, indent=4):
        """Single bullet point, right-aligned, with dash marker."""
        self.set_font("Vazir", "", 10)
        self.set_text_color(33, 37, 41)
        self.multi_cell(0, 5, fa("-- " + text), align="R")
        self.ln(0.5)

    # ── Skill Row ──────────────────────────────────────────────
    def skill_row(self, label, detail):
        """Bold label + regular detail."""
        self.set_font("Vazir", "B", 10)
        self.set_text_color(33, 37, 41)
        self.write(5, fa(label + " "))
        self.set_font("Vazir", "", 10)
        self.set_text_color(73, 80, 87)
        self.multi_cell(0, 5, fa(detail), align="R")
        self.ln(0.5)

    # ── Education ──────────────────────────────────────────────
    def education(self, degree, school, extra=""):
        """Degree bold on first line, school on second."""
        self.set_font("Vazir", "B", 11)
        self.set_text_color(33, 37, 41)
        self.cell(0, 6, fa(degree), new_x="LMARGIN", new_y="NEXT", align="R")

        self.set_font("Vazir", "", 10)
        self.set_text_color(73, 80, 87)
        school_text = school + (" | " + extra if extra else "")
        self.cell(0, 5, fa(school_text), new_x="LMARGIN", new_y="NEXT", align="R")
        self.ln(3)
