"""
generate_pdfs_v2.py — Markdown to PDF using ReportLab (pure Python, no system deps)
Run: python generate_pdfs_v2.py
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ─── Color palette ───────────────────────────
INDIGO    = colors.HexColor("#6366F1")
INDIGO_LT = colors.HexColor("#EDE9FE")
SLATE     = colors.HexColor("#1E293B")
GRAY      = colors.HexColor("#64748B")
WHITE     = colors.white
GREEN     = colors.HexColor("#22C55E")
RED       = colors.HexColor("#EF4444")

def build_styles():
    base = getSampleStyleSheet()
    styles = {}
    styles["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20,
                                   textColor=INDIGO, spaceAfter=8, spaceBefore=14,
                                   leading=24)
    styles["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                                   textColor=SLATE, spaceAfter=6, spaceBefore=12,
                                   leading=18)
    styles["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11,
                                   textColor=colors.HexColor("#4F46E5"),
                                   spaceAfter=4, spaceBefore=8, leading=14)
    styles["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                                     textColor=SLATE, spaceAfter=6, leading=14)
    styles["bullet"] = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10,
                                       textColor=SLATE, leftIndent=16,
                                       spaceAfter=4, leading=14)
    styles["code"] = ParagraphStyle("code", fontName="Courier", fontSize=8,
                                     textColor=colors.HexColor("#E2E8F0"),
                                     backColor=colors.HexColor("#1E293B"),
                                     spaceAfter=8, leading=12, leftIndent=8,
                                     rightIndent=8)
    styles["title"] = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24,
                                      textColor=WHITE, alignment=TA_CENTER,
                                      leading=30)
    styles["subtitle"] = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11,
                                         textColor=colors.HexColor("#A0AEC0"),
                                         alignment=TA_CENTER, spaceAfter=20)
    return styles


def md_to_elements(md_text, styles):
    """Parse markdown into ReportLab flowable elements (simplified parser)."""
    elements = []
    in_code = False
    code_buf = []
    in_table = False
    table_rows = []

    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                in_code = False
                code_text = "\n".join(code_buf)
                elements.append(Spacer(1, 4))
                # wrap code in a box
                code_table = Table([[Paragraph(
                    code_text.replace("&", "&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br/>"),
                    styles["code"]
                )]], colWidths=[16*cm])
                code_table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1E293B")),
                    ("ROUNDEDCORNERS", [6]),
                    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#2D3148")),
                    ("TOPPADDING", (0,0), (-1,-1), 8),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ]))
                elements.append(code_table)
                elements.append(Spacer(1, 6))
                code_buf = []
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Tables
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r"[-:]+", c) for c in cells if c):
                i += 1
                continue
            table_rows.append(cells)
            i += 1
            if i >= len(lines) or not lines[i].startswith("|"):
                if table_rows:
                    col_count = max(len(r) for r in table_rows)
                    col_w = 16*cm / max(col_count, 1)
                    tbl_data = []
                    for ri, row in enumerate(table_rows):
                        row_data = []
                        style_key = "h3" if ri == 0 else "body"
                        for cell in row:
                            row_data.append(Paragraph(clean_inline(cell), styles[style_key]))
                        tbl_data.append(row_data)
                    tbl = Table(tbl_data, colWidths=[col_w]*col_count)
                    tbl.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), INDIGO),
                        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                        ("ROWBACKGROUNDS", (0,1), (-1,-1),
                         [colors.HexColor("#F8FAFC"), colors.HexColor("#EDE9FE")]),
                        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                        ("TOPPADDING", (0,0), (-1,-1), 5),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                        ("LEFTPADDING", (0,0), (-1,-1), 8),
                    ]))
                    elements.append(tbl)
                    elements.append(Spacer(1, 8))
                    table_rows = []
            continue

        # HR
        if re.match(r"^[-*]{3,}$", line.strip()):
            elements.append(HRFlowable(width="100%", thickness=0.5,
                                        color=colors.HexColor("#CBD5E1"),
                                        spaceAfter=8, spaceBefore=8))
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            elements.append(Paragraph(clean_inline(line[2:]), styles["h1"]))
            i += 1
            continue
        if line.startswith("## "):
            elements.append(Paragraph(clean_inline(line[3:]), styles["h2"]))
            i += 1
            continue
        if line.startswith("### "):
            elements.append(Paragraph(clean_inline(line[4:]), styles["h3"]))
            i += 1
            continue

        # Bullets
        if line.startswith("- ") or line.startswith("* "):
            elements.append(Paragraph("• " + clean_inline(line[2:]), styles["bullet"]))
            i += 1
            continue
        if re.match(r"^\d+\. ", line):
            txt = re.sub(r"^\d+\. ", "", line)
            elements.append(Paragraph(clean_inline(txt), styles["bullet"]))
            i += 1
            continue

        # Arrows / special chars
        if line.strip().startswith("→"):
            elements.append(Paragraph("→ " + clean_inline(line.strip()[1:]), styles["bullet"]))
            i += 1
            continue

        # Blank
        if not line.strip():
            elements.append(Spacer(1, 6))
            i += 1
            continue

        # Body
        elements.append(Paragraph(clean_inline(line), styles["body"]))
        i += 1

    return elements


def clean_inline(text):
    """Convert inline markdown to ReportLab XML."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r'<font name="Courier" size="9">\1</font>', text)
    # Links
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


def create_pdf(md_path: str, pdf_path: str, title: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    styles = build_styles()
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2*cm,
    )

    story = []

    # Cover header block
    cover_data = [[Paragraph(title, styles["title"])]]
    cover_tbl = Table(cover_data, colWidths=[17*cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), INDIGO),
        ("TOPPADDING", (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Volopay Growth Squad Assessment | July 2026", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=INDIGO,
                              spaceAfter=12, spaceBefore=4))

    story.extend(md_to_elements(md_text, styles))

    doc.build(story)
    print(f"Generated: {pdf_path}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))

    files = [
        (
            os.path.join(base, "Task1", "Task1_LinkedIn_Content.md"),
            os.path.join(base, "Task1", "Task1_LinkedIn_Content.pdf"),
            "LinkedIn Content Strategy",
        ),
        (
            os.path.join(base, "docs", "Approach_Document.md"),
            os.path.join(base, "docs", "Approach_Document.pdf"),
            "Customer 360 - Approach Document",
        ),
    ]

    for md_path, pdf_path, title in files:
        if os.path.exists(md_path):
            create_pdf(md_path, pdf_path, title)
        else:
            print(f"SKIP (not found): {md_path}")

    print("Done.")
