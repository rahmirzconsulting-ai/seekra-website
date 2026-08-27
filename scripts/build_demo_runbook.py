#!/usr/bin/env python3
"""Generate the Seekra Client Demo Run Book as a DOCX.

Output: /home/z/my-project/download/Seekra_Demo_RunBook.docx

Structure (~28 pages):
  - Cover
  - Executive Summary
  - Pre-Demo Setup
  - Section 1: Smart Search
  - Section 2: AI Chat with Citations
  - Section 3: Audit Trail
  - Section 4: Governance, Control & Security
  - Section 5: Provenance
  - Section 6: Entity Relations
  - Section 7: Mobile + Voice
  - Section 8: Wrap-up & Q&A
  - Appendix: User Roster + Document Inventory
"""
from __future__ import annotations

from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml

OUT = Path("/home/z/my-project/download/Seekra_Demo_RunBook.docx")

# Seekra brand palette
SEEKRA_PRIMARY = RGBColor(0x4C, 0x29, 0x91)      # purple
SEEKRA_ACCENT = RGBColor(0x00, 0xA8, 0x96)       # teal
SEEKRA_GOLD = RGBColor(0xD4, 0xAF, 0x37)         # gold
SEEKRA_DARK = RGBColor(0x18, 0x20, 0x2A)         # near-black
SEEKRA_GREY = RGBColor(0x50, 0x60, 0x70)         # body grey
SEEKRA_LIGHT = RGBColor(0xF5, 0xF7, 0xFA)        # light surface


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def set_cell_shading(cell, color_hex: str):
    """Apply background color to a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def set_cell_border(cell, **kwargs):
    """Set borders on a cell. kwargs: top, bottom, left, right (each a dict
    with 'val', 'sz', 'color')."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tcBorders = tc_pr.find(qn("w:tcBorders"))
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tc_pr.append(tcBorders)
    for edge in ("top", "left", "bottom", "right"):
        if edge in kwargs:
            spec = kwargs[edge]
            elem = tcBorders.find(qn(f"w:{edge}"))
            if elem is None:
                elem = OxmlElement(f"w:{edge}")
                tcBorders.append(elem)
            elem.set(qn("w:val"), spec.get("val", "single"))
            elem.set(qn("w:sz"), str(spec.get("sz", 4)))
            elem.set(qn("w:color"), spec.get("color", "auto"))


def add_horizontal_rule(doc, color="4C2991", size=12):
    """Add a horizontal rule paragraph."""
    p = doc.add_paragraph()
    p_pr = p._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    p_bdr.append(bottom)
    p_pr.append(p_bdr)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    return p


def add_styled_paragraph(doc, text, *, size=11, bold=False, italic=False,
                         color=SEEKRA_DARK, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                         space_before=0, space_after=6, line_spacing=1.3,
                         font_name="Calibri", indent_first=False):
    p = doc.add_paragraph()
    p.alignment = alignment
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if indent_first:
        p.paragraph_format.first_line_indent = Cm(0.5)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font_name
    return p


def add_h1(doc, text, *, color=SEEKRA_PRIMARY, size=20):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = color
    r.font.name = "Calibri"
    p.style = doc.styles["Heading 1"]
    # Re-apply our run formatting (style overrides)
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color
        run.font.name = "Calibri"
    add_horizontal_rule(doc, color="00A896", size=8)
    return p


def add_h2(doc, text, *, color=SEEKRA_PRIMARY, size=14):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = color
    r.font.name = "Calibri"
    p.style = doc.styles["Heading 2"]
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return p


def add_h3(doc, text, *, color=SEEKRA_DARK, size=12):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = color
    r.font.name = "Calibri"
    p.style = doc.styles["Heading 3"]
    for run in p.runs:
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return p


def add_bullet(doc, text, *, level=0, size=11):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.color.rgb = SEEKRA_DARK
    r.font.name = "Calibri"
    return p


def add_callout(doc, label: str, text: str, *, label_color=SEEKRA_ACCENT):
    """Add a callout box (table with shaded background)."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    # Cell width to full page
    cell.width = Cm(16.5)
    set_cell_shading(cell, "F5F7FA")
    set_cell_border(
        cell,
        left={"val": "single", "sz": "24", "color": "00A896"},
        top={"val": "single", "sz": "4", "color": "E0E4E8"},
        bottom={"val": "single", "sz": "4", "color": "E0E4E8"},
        right={"val": "single", "sz": "4", "color": "E0E4E8"},
    )
    # Label paragraph
    p_label = cell.paragraphs[0]
    p_label.paragraph_format.space_before = Pt(4)
    p_label.paragraph_format.space_after = Pt(2)
    r = p_label.add_run(label)
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = label_color
    r.font.name = "Calibri"
    # Body paragraph
    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_after = Pt(4)
    p_body.paragraph_format.line_spacing = 1.3
    r2 = p_body.add_run(text)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = SEEKRA_DARK
    r2.font.name = "Calibri"
    # Spacing after table
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)
    return table


def add_screenshot_placeholder(doc, caption: str):
    """Add a placeholder box for a screenshot with caption text."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    cell.width = Cm(16.5)
    set_cell_shading(cell, "ECEAF2")
    set_cell_border(
        cell,
        top={"val": "dashed", "sz": "8", "color": "4C2991"},
        bottom={"val": "dashed", "sz": "8", "color": "4C2991"},
        left={"val": "dashed", "sz": "8", "color": "4C2991"},
        right={"val": "dashed", "sz": "8", "color": "4C2991"},
    )
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(28)
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run(f"[ Screenshot: {caption} ]")
    r.font.italic = True
    r.font.size = Pt(11)
    r.font.color.rgb = SEEKRA_GREY
    r.font.name = "Calibri"
    # Spacer
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(4)
    return table


def add_step_block(doc, step_num: int, title: str, action: str,
                   expected: str, screenshot: str = ""):
    """Add a numbered step block with action + expected result."""
    # Step header
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    r_num = p.add_run(f"Step {step_num}. ")
    r_num.font.bold = True
    r_num.font.size = Pt(12)
    r_num.font.color.rgb = SEEKRA_PRIMARY
    r_num.font.name = "Calibri"
    r_title = p.add_run(title)
    r_title.font.bold = True
    r_title.font.size = Pt(12)
    r_title.font.color.rgb = SEEKRA_DARK
    r_title.font.name = "Calibri"

    # Action
    p_act = doc.add_paragraph()
    p_act.paragraph_format.left_indent = Cm(0.5)
    p_act.paragraph_format.space_after = Pt(2)
    p_act.paragraph_format.line_spacing = 1.3
    r1 = p_act.add_run("Action: ")
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = SEEKRA_ACCENT
    r1.font.name = "Calibri"
    r2 = p_act.add_run(action)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = SEEKRA_DARK
    r2.font.name = "Calibri"

    # Expected
    p_exp = doc.add_paragraph()
    p_exp.paragraph_format.left_indent = Cm(0.5)
    p_exp.paragraph_format.space_after = Pt(4)
    p_exp.paragraph_format.line_spacing = 1.3
    r1 = p_exp.add_run("Expected: ")
    r1.font.bold = True
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = SEEKRA_GOLD
    r1.font.name = "Calibri"
    r2 = p_exp.add_run(expected)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = SEEKRA_DARK
    r2.font.name = "Calibri"

    # Screenshot placeholder (optional)
    if screenshot:
        add_screenshot_placeholder(doc, screenshot)


def add_table(doc, headers: list[str], rows: list[list[str]],
              col_widths: list[float] | None = None):
    """Add a styled table with header row + body rows."""
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for col_idx, header in enumerate(headers):
        cell = table.rows[0].cells[col_idx]
        if col_widths:
            cell.width = Cm(col_widths[col_idx])
        set_cell_shading(cell, "4C2991")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(header)
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.name = "Calibri"
        set_cell_border(
            cell,
            top={"val": "single", "sz": "4", "color": "4C2991"},
            bottom={"val": "single", "sz": "4", "color": "4C2991"},
            left={"val": "single", "sz": "4", "color": "4C2991"},
            right={"val": "single", "sz": "4", "color": "4C2991"},
        )
    # Body rows
    for row_idx, row in enumerate(rows, 1):
        for col_idx, val in enumerate(row):
            cell = table.rows[row_idx].cells[col_idx]
            if col_widths:
                cell.width = Cm(col_widths[col_idx])
            if row_idx % 2 == 0:
                set_cell_shading(cell, "F5F7FA")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.2
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
            r.font.color.rgb = SEEKRA_DARK
            r.font.name = "Calibri"
            set_cell_border(
                cell,
                top={"val": "single", "sz": "2", "color": "E0E4E8"},
                bottom={"val": "single", "sz": "2", "color": "E0E4E8"},
                left={"val": "single", "sz": "2", "color": "E0E4E8"},
                right={"val": "single", "sz": "2", "color": "E0E4E8"},
            )
    # Spacer
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    return table


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


# --------------------------------------------------------------------------
# Build the document
# --------------------------------------------------------------------------

doc = Document()

# Page setup
for section in doc.sections:
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

# Default style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.paragraph_format.line_spacing = 1.3

# Add footer with page numbers
for section in doc.sections:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Seekra Client Demo Run Book · © 2026 Seekra Media Holdings · Page ")
    r.font.size = Pt(9)
    r.font.color.rgb = SEEKRA_GREY
    r.font.name = "Calibri"
    # PAGE field
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = "PAGE \\* arabic \\* MERGEFORMAT"
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    r2 = p.add_run()
    r2.font.size = Pt(9)
    r2.font.color.rgb = SEEKRA_GREY
    r2._r.append(fld_char_begin)
    r2._r.append(instr)
    r2._r.append(fld_char_end)

# ==========================================================================
# COVER PAGE
# ==========================================================================

# Top brand band
table = doc.add_table(rows=1, cols=1)
cell = table.rows[0].cells[0]
cell.width = Cm(16.5)
set_cell_shading(cell, "4C2991")
p = cell.paragraphs[0]
p.paragraph_format.space_before = Pt(8)
p.paragraph_format.space_after = Pt(8)
r = p.add_run("SEEKRA MEDIA HOLDINGS")
r.font.size = Pt(10)
r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
r.font.name = "Calibri"

# Spacer (using paragraph spacing instead of empty paragraphs)
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(0)
p.paragraph_format.space_after = Pt(160)

# Title
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(4)
r = p.add_run("Seekra")
r.font.size = Pt(44)
r.font.bold = True
r.font.color.rgb = SEEKRA_PRIMARY
r.font.name = "Calibri"

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.paragraph_format.space_after = Pt(4)
r = p.add_run("Client Demo Run Book")
r.font.size = Pt(36)
r.font.bold = True
r.font.color.rgb = SEEKRA_DARK
r.font.name = "Calibri"

# Gold accent line
add_horizontal_rule(doc, color="D4AF37", size=18)

# Subtitle
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("A storytelling demonstration of Seekra's content-aware intelligence platform —")
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = SEEKRA_GREY
r.font.name = "Calibri"

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run("smart search, AI chat with citations, audit, governance, provenance, and entity relations.")
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = SEEKRA_GREY
r.font.name = "Calibri"

# Meta block
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(120)
p.paragraph_format.space_after = Pt(0)

meta_table = doc.add_table(rows=4, cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
meta_rows = [
    ("Audience", "Client stakeholders, prospective customers, partners"),
    ("Runtime", "35–40 minutes (scripted); 60 minutes with Q&A"),
    ("Demo Environment", "https://app-internal.seekra.pk"),
    ("Version", "1.0 · August 2026"),
]
for i, (label, value) in enumerate(meta_rows):
    cell_l = meta_table.rows[i].cells[0]
    cell_l.width = Cm(4)
    p = cell_l.paragraphs[0]
    r = p.add_run(label)
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = SEEKRA_GREY
    r.font.name = "Calibri"
    cell_r = meta_table.rows[i].cells[1]
    cell_r.width = Cm(12)
    p = cell_r.paragraphs[0]
    r = p.add_run(value)
    r.font.size = Pt(11)
    r.font.color.rgb = SEEKRA_DARK
    r.font.name = "Calibri"

add_page_break(doc)

# ==========================================================================
# EXECUTIVE SUMMARY
# ==========================================================================

add_h1(doc, "Executive Summary")

add_styled_paragraph(
    doc,
    "This run book guides you through a complete demonstration of Seekra — a content-aware intelligence platform built for Gulf enterprises that need cited AI answers, PII masking, tamper-evident audit trails, and granular access control over multilingual (Arabic + English) content.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_styled_paragraph(
    doc,
    "The demo is framed around Seekra Media Holdings, a fictional Dubai media production holding company with four subsidiaries (Films, Creative, Studios, Broadcast). The repository contains 32 realistic documents — contracts, financial statements, screenplays, call sheets, vendor invoices, payroll, passport rosters, pitch decks, and stock footage — distributed across all four subsidiaries with four classification levels (Public, Internal, Confidential, Restricted).",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "What the Client Will See")

add_bullet(doc, "Smart Search that finds documents across organizational silos, respecting each user's department scope and clearance level — with classification badges (Public / Internal / Confidential / Restricted) and PII indicators on every result.")
add_bullet(doc, "AI Chat with Citations that answers business questions in natural language (English or Arabic), always citing the source document and page/timestamp — never hallucinating, always abstaining when the answer isn't in the library.")
add_bullet(doc, "PII Masking that automatically detects Emirates IDs, passport numbers, IBANs, phone numbers, and emails — and masks them before any content reaches the LLM, so chat answers never leak personal data.")
add_bullet(doc, "Audit Trail with hash-chained, tamper-evident event logging — every login, search, chat, file upload, scope change, override grant, and user deactivation is recorded for compliance.")
add_bullet(doc, "Governance, Control & Security — a 4-company organizational tree with department/team scoping, clearance levels per user, per-document overrides that cross the org boundary without elevating clearance, and soft-delete users whose tokens invalidate instantly.")
add_bullet(doc, "Provenance — every chat answer can be traced back through the full pipeline: question reformulation, retrieval legs, LLM call, and final answer, with confidence scores per source chunk.")
add_bullet(doc, "Entity Relations — automatically extracted persons, organizations, and locations from Arabic + English text, with a knowledge graph showing co-occurrence relationships.")
add_bullet(doc, "Voice + Mobile — Arabic-first voice commands for document navigation, with a responsive mobile UI for on-the-go access.")

add_h2(doc, "Three Things to Emphasize")

add_callout(
    doc,
    "EMPHASIZE",
    "Every answer is cited. If Seekra cannot find the answer in your documents, it says so — no hallucination, no fabricated sources. This is the single most important differentiator for enterprise buyers.",
)

add_callout(
    doc,
    "EMPHASIZE",
    "PII never reaches the LLM. Personal data is masked at the chunk level before retrieval, so even if a chat question references a passport number or an IBAN, the model never sees the raw value. The audit trail proves this.",
)

add_callout(
    doc,
    "EMPHASIZE",
    "Access is enforced at the database level, not in the UI. A viewer in Films Production cannot see Sales documents — not because the UI hides them, but because the SQL query itself filters them out. This is defense in depth.",
)

add_page_break(doc)

# ==========================================================================
# PRE-DEMO SETUP
# ==========================================================================

add_h1(doc, "Pre-Demo Setup Checklist")

add_styled_paragraph(
    doc,
    "Complete this checklist 15 minutes before the demo. All items are required.",
    italic=True, color=SEEKRA_GREY,
)

add_h2(doc, "Environment")

add_table(
    doc,
    headers=["Item", "Requirement", "Verified"],
    rows=[
        ("URL", "https://app-internal.seekra.pk", "[ ]"),
        ("Browser", "Chrome 120+ or Edge 120+ (Chrome preferred for voice)", "[ ]"),
        ("Network", "Stable broadband; no VPN that blocks UAE domains", "[ ]"),
        ("Audio", "Working speakers/headphones for MP3 + voice demos", "[ ]"),
        ("Display", "1920×1080 minimum; second monitor for presenter notes", "[ ]"),
        ("Backup", "Mobile device with Chrome for the mobile + voice section", "[ ]"),
    ],
    col_widths=[3.5, 11, 2],
)

add_h2(doc, "Demo Accounts")

add_styled_paragraph(
    doc,
    "All demo accounts share the same password: Demo@2026 (except admin which is A!!!@@@2026). Use the accounts in the order below to walk through the demo narrative.",
)

add_table(
    doc,
    headers=["#", "Username", "Role", "Clearance", "Department", "Purpose in Demo"],
    rows=[
        ("1", "khalid.alsoodi", "admin", "3", "Group Executive", "CEO — full visibility, admin features"),
        ("2", "layla.almehrabi", "viewer", "2", "Films · Production", "Shows scoped search + clearance cap"),
        ("3", "ahmed.alketbi", "viewer", "1", "Films · Production", "Shows clearance 1 cannot see Confidential"),
        ("4", "fatima.almansouri", "editor", "3", "Group Finance", "Shows Restricted financials access"),
        ("5", "omar.alhashimi", "auditor", "3", "Group Legal & Compliance", "Shows auditor role (read-only, all access)"),
    ],
    col_widths=[0.8, 3.8, 1.8, 1.8, 4.0, 4.3],
)

add_h2(doc, "Content Repository State")

add_styled_paragraph(
    doc,
    "The repository contains 32 documents across all four subsidiaries. Verify the state by logging in as admin and navigating to /files/. If the count is not 32, pause and re-run the upload script.",
)

add_table(
    doc,
    headers=["Classification", "Count", "Visible To"],
    rows=[
        ("Public (0)", "4", "Everyone — even cross-scope viewers"),
        ("Internal (1)", "6", "Anyone in the document's scope"),
        ("Confidential (2)", "13", "Users with clearance ≥ 2"),
        ("Restricted (3)", "9", "Users with clearance = 3 only"),
        ("Total", "32", "—"),
    ],
    col_widths=[5, 3, 8.5],
)

add_callout(
    doc,
    "TIP",
    "Before the client arrives, log in as khalid.alsoodi (admin) and open three browser tabs: /search, /chat, /admin/organization. This lets you transition between sections without re-logging in during the demo.",
)

add_page_break(doc)

# ==========================================================================
# SECTION 1: SMART SEARCH
# ==========================================================================

add_h1(doc, "Section 1 — Smart Search")
add_styled_paragraph(
    doc,
    "Duration: 6 minutes · Login as: khalid.alsoodi (admin) → layla.almehrabi → ahmed.alketbi",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "Smart Search is the front door to Seekra. It demonstrates three things at once: (1) the system finds documents across all organizational silos in a single query; (2) each result carries classification badges and PII indicators so the user instantly understands sensitivity; (3) the same query returns different results for different users based on their org scope and clearance level — enforced at the database, not the UI.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 1.1 — Search as the CEO (full visibility)")

add_step_block(
    doc, 1, "Login as Khalid Alsoodi (Group CEO, admin, clearance 3)",
    "Open https://app-internal.seekra.pk and sign in with username khalid.alsoodi, password A!!!@@@2026.",
    "Dashboard loads. Sidebar shows all sections. Top-right shows the user's name and role.",
    screenshot="Dashboard view after admin login",
)

add_step_block(
    doc, 2, "Navigate to /search and run the query 'Golden Falcon'",
    "Click 'Search' in the sidebar. Type 'Golden Falcon' in the search box and press Enter.",
    "8–10 results appear, including: 12_Golden_Falcon_Script_v3.pdf (Films · Creative Direction, Confidential), 13_Golden_Falcon_Creative_Treatment.pptx, 14_Director_Vision_Notes.txt, 15_Golden_Falcon_Budget_Breakdown.xlsx (Restricted), 17_Scene12_Take3_OnSet.mp4, 23_Golden_Falcon_Logo_Concept.png (Public). Each result shows: filename, scope name (department), classification badge, PII badge if applicable, and a relevance score.",
    screenshot="Search results for 'Golden Falcon' as admin",
)

add_callout(
    doc,
    "SAY",
    "Notice the badges on each result. The orange 'Confidential' badge tells me this document requires clearance level 2 or higher. The red 'Restricted' badge on the budget means only clearance 3 users can see it. The green 'Public' badge on the logo means anyone in the company can see it — even someone outside the Films department. This is classification done right — visible, intuitive, enforced.",
)

add_h2(doc, "Step 1.2 — Search for financial content (Restricted)")

add_step_block(
    doc, 3, "Run the query 'Q3 earnings'",
    "In the same search bar, replace the query with 'Q3 earnings' and press Enter.",
    "2–3 results appear: 05_Q3_Earnings_Briefing.mp3 (Group Finance, Restricted), 06_Q3_Financial_Statements.xlsx (Group Finance, Restricted), and possibly 07_Budget_Review_Photo.jpg (Group Finance, Confidential). All carry the red Restricted badge.",
    screenshot="Search results for 'Q3 earnings' as admin",
)

add_callout(
    doc,
    "SAY",
    "Both results are audio and spreadsheet — different file types, same topic. Seekra indexed both the audio transcript and the XLSX cell content, so a single query surfaces both. As the CEO with clearance 3, I can see them. Let me show you what a viewer in a different department sees.",
)

add_h2(doc, "Step 1.3 — Switch to Layla (Films Production, clearance 2)")

add_step_block(
    doc, 4, "Log out and log in as Layla Al Mehrabi",
    "Click the user menu (top-right) → Sign out. Then sign in with username layla.almehrabi, password Demo@2026.",
    "Dashboard loads. Notice the sidebar may show fewer admin items (no Organization, no Users).",
)

add_step_block(
    doc, 5, "Run the same query 'Q3 earnings' as Layla",
    "Navigate to /search. Type 'Q3 earnings' and press Enter.",
    "Zero results, OR only public/internal docs that match — but NOT the Restricted financials. The access filter has excluded Group Finance documents because Layla is in Films · Production (a different subtree).",
    screenshot="Search results for 'Q3 earnings' as Layla — empty or scoped",
)

add_callout(
    doc,
    "SAY",
    "Same query, different user — different results. This is not a UI filter that a clever user could bypass. The SQL query itself was rewritten by Seekra's access layer to exclude any document whose scope_path is not under Layla's department (Films · Production) AND whose classification exceeds her clearance (2). Even if she knew the document ID and tried to fetch it directly, the API would return 404. Defense in depth.",
)

add_h2(doc, "Step 1.4 — Switch to Ahmed (same dept, clearance 1)")

add_step_block(
    doc, 6, "Log out and log in as Ahmed Al Ketbi",
    "Sign out, then sign in with username ahmed.alketbi, password Demo@2026.",
    "Dashboard loads. Ahmed is in the same department as Layla (Films · Production) but has clearance 1 (Internal only).",
)

add_step_block(
    doc, 7, "Run the query 'Golden Falcon call sheet'",
    "Navigate to /search. Type 'Golden Falcon call sheet' and press Enter.",
    "1–2 results: 16_Daily_Call_Sheet_2026-09-15.pdf (Films · Production, Internal — visible to Ahmed). But 17_Scene12_Take3_OnSet.mp4 (Films · Production, Confidential) is NOT visible to Ahmed, even though it's in his department — because his clearance is 1 and the doc requires clearance 2.",
    screenshot="Search results for Ahmed — clearance cap in action",
)

add_callout(
    doc,
    "SAY",
    "Ahmed and Layla are in the same department, working on the same film. But Layla (clearance 2) can see the confidential scene footage, and Ahmed (clearance 1) cannot. This is how Seekra enforces need-to-know without breaking collaboration. When Ahmed gets promoted or the project lead grants him an override, access is instant — no IT ticket, no provisioning delay.",
)

add_page_break(doc)

# ==========================================================================
# SECTION 2: AI CHAT WITH CITATIONS
# ==========================================================================

add_h1(doc, "Section 2 — AI Chat with Citations")
add_styled_paragraph(
    doc,
    "Duration: 8 minutes · Login as: khalid.alsoodi (admin)",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "AI Chat is where Seekra's value becomes unmistakable. Unlike generic ChatGPT, Seekra's chat (1) only answers from your documents — never the open internet; (2) always cites the source with filename + page/timestamp; (3) abstains when it cannot find the answer, rather than hallucinate; (4) masks PII before the LLM sees the content; (5) works in Arabic and English with full RTL support.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 2.1 — Inventory question (the warm-up)")

add_step_block(
    doc, 1, "Navigate to /chat and ask 'how many documents are in the library?'",
    "Click 'Chat' in the sidebar. Type 'how many documents are available and can you list them here?' and press Enter.",
    "Within 5–10 seconds, Seekra returns an inventory answer: 'There are 32 documents in the library. (X text, Y images, Z PDF, ...)' — with a breakdown by file type. The answer cites no specific source because it's a metadata query, but the response includes a complete document list with thumbnails.",
    screenshot="Chat answer for inventory question",
)

add_callout(
    doc,
    "SAY",
    "This is the warm-up question. It shows the client that Seekra understands the entire repository, not just one document. The breakdown by file type — text, images, PDF, Office, video, audio — demonstrates that Seekra handles every format your team uses, not just text.",
)

add_h2(doc, "Step 2.2 — Substantive question with citation")

add_step_block(
    doc, 2, "Ask 'what is Project Golden Falcon about?'",
    "Type 'what is Project Golden Falcon about?' and press Enter.",
    "Seekra returns a 3–4 sentence answer summarizing the film's logline, genre, and key characters. The answer cites 12_Golden_Falcon_Script_v3.pdf (and possibly 13_Golden_Falcon_Creative_Treatment.pptx and 14_Director_Vision_Notes.txt). Each citation shows the filename, page number, and a relevance score.",
    screenshot="Chat answer citing the Golden Falcon script",
)

add_callout(
    doc,
    "SAY",
    "Notice the citations. Every claim in the answer is traceable to a specific document. If the client asks 'where did you get that?', you click the citation and Seekra opens the source at the exact page. This is what 'cited AI' means — no black boxes, no 'the model said so'. The model is just a summarizer over your own content.",
)

add_h2(doc, "Step 2.3 — Audio source citation (timestamp deep-link)")

add_step_block(
    doc, 3, "Ask 'what were the main highlights of the Q3 earnings briefing?'",
    "Type the question and press Enter.",
    "Seekra returns a summary of the Q3 earnings (revenue AED 247.8M, +18% YoY, EBITDA 22.4%, etc.) citing 05_Q3_Earnings_Briefing.mp3. The citation includes a timestamp chip (e.g. '0:42') that, when clicked, opens the audio player at that exact moment.",
    screenshot="Chat answer with audio timestamp citation",
)

add_callout(
    doc,
    "SAY",
    "The audio file is 30 seconds of synthesized narration, but Seekra transcribed it, indexed the transcript, and surfaced the exact moment when the CFO mentions the revenue number. For your real audio — earnings calls, interviews, podcasts — this means every spoken word becomes searchable and citable. Click the timestamp chip to jump straight to the source.",
)

add_h2(doc, "Step 2.4 — Arabic question (RTL + Arabic NER)")

add_step_block(
    doc, 4, "Ask in Arabic: 'ماذا يقول دليل السلامة عن مخارج الطوارئ؟'",
    "Type or paste the Arabic question. Seekra auto-detects Arabic and switches to RTL rendering.",
    "Seekra returns an Arabic answer (RTL-aligned) summarizing the emergency exit procedures from 27_Warehouse_Safety_Procedures.docx or 10_Internal_Policies_Arabic.docx. The citation appears in Arabic with the original Arabic filename.",
    screenshot="Arabic chat question and answer",
)

add_callout(
    doc,
    "SAY",
    "Arabic-first is not a translation layer — it is a native pipeline. Seekra uses a dedicated Arabic NER model (CAMeL Tools) to extract persons, organizations, and locations from Arabic text. The chat reformulation, retrieval, and answer generation all happen in Arabic. This is critical for Gulf enterprises where Arabic is the language of record.",
)

add_h2(doc, "Step 2.5 — PII masking in action")

add_step_block(
    doc, 5, "Ask 'show me the payroll for the Films department'",
    "Type 'show me the payroll for Films department' and press Enter.",
    "Seekra returns a summary citing 20_Films_Payroll_October_2026.xlsx. The answer mentions positions and gross salary ranges, but ALL IBANs, bank account numbers, and exact salary figures are masked: 'AE07••••••••••••56' or '[IBAN REDACTED]'. The PII was masked at the chunk level BEFORE retrieval, so the LLM never saw the raw values.",
    screenshot="Chat answer with PII masked",
)

add_callout(
    doc,
    "SAY",
    "This is the PII masking in action. The payroll spreadsheet has real-looking IBANs and bank account numbers. But Seekra's PII detector — running on Arabic AND English text — masked them before the LLM saw the content. The audit trail in /admin/pii will show exactly which chunks were masked and when. Your compliance team can prove to a regulator that no personal data ever left your tenant.",
)

add_h2(doc, "Step 2.6 — Abstention (the most important demo)")

add_step_block(
    doc, 6, "Ask 'what is the capital of France?'",
    "Type the question and press Enter.",
    "Seekra responds with an abstention: 'I don't have enough information in the provided documents to answer that question.' No fabricated answer, no Wikipedia lookup, no hallucination. The system stays within its knowledge boundary.",
    screenshot="Abstention answer for out-of-scope question",
)

add_callout(
    doc,
    "EMPHASIZE",
    "This is the single most important moment in the demo. Enterprise buyers are terrified of AI hallucinations — of a chatbot that confidently invents an answer when it doesn't know. Seekra's abstention is a feature, not a bug. It tells the client: 'This system knows what it doesn't know. You can trust it.'",
)

add_page_break(doc)

# ==========================================================================
# SECTION 3: AUDIT TRAIL
# ==========================================================================

add_h1(doc, "Section 3 — Audit Trail")
add_styled_paragraph(
    doc,
    "Duration: 4 minutes · Login as: khalid.alsoodi (admin)",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "Every action in Seekra — login, search, chat, upload, scope change, override grant, user deactivation — emits an audit event. Events are hash-chained: each event's hash incorporates the previous event's hash, so any tampering is mathematically detectable. This is tamper-evident logging, suitable for regulatory submission.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 3.1 — Open the audit page")

add_step_block(
    doc, 1, "Navigate to /admin/audit",
    "In the sidebar, expand 'Admin' and click 'Audit Trail'.",
    "The audit page loads, showing the most recent 50 events in reverse chronological order. Each event shows: timestamp, username, action code, IP address, and details.",
    screenshot="Audit trail page with recent events",
)

add_h2(doc, "Step 3.2 — Filter by user")

add_step_block(
    doc, 2, "Filter by username 'layla.almehrabi'",
    "In the filter bar, type 'layla.almehrabi' in the username field and apply.",
    "The list filters to show all events by Layla — her login, her search queries, her chat questions, and the override grant that was created earlier (if you ran the cache-flush demo).",
    screenshot="Audit trail filtered by Layla",
)

add_callout(
    doc,
    "SAY",
    "Every query Layla ran, every document she opened, every chat question she asked — all here, all timestamped, all with her IP address. If a regulator asks 'who accessed the customer list and when?', you can answer in 30 seconds.",
)

add_h2(doc, "Step 3.3 — Show the hash chain")

add_step_block(
    doc, 3, "Click on any event to expand the hash chain details",
    "Click the 'view' or 'details' icon next to any event.",
    "The detail view shows: event_hash (SHA-256 of the event content + previous event's hash), previous_hash, and a 'Chain verified' indicator. If any event in the chain were modified, the verification would fail.",
    screenshot="Hash chain verification on a single event",
)

add_callout(
    doc,
    "SAY",
    "The hash chain is what makes this admissible in court. Each event's hash depends on the previous event's hash, all the way back to the genesis event. If anyone — even a database administrator — tries to modify or delete an event, the chain breaks and the provenance API reports tampering. This is the same technique used in blockchain, applied to your audit log.",
)

add_h2(doc, "Step 3.4 — Show security events")

add_step_block(
    doc, 4, "Filter by action 'SECURITY_*'",
    "In the filter bar, type 'SECURITY' in the action field.",
    "The list filters to show all security events: SECURITY_LOGIN_SUCCESS, SECURITY_LOGIN_FAILED (for the deactivated account attempt), SECURITY_USER_DEACTIVATED, SECURITY_USER_REACTIVATED, SECURITY_ACCESS_DENIED. These are the events your compliance team will care about most.",
    screenshot="Security events in audit trail",
)

add_page_break(doc)

# ==========================================================================
# SECTION 4: GOVERNANCE, CONTROL & SECURITY
# ==========================================================================

add_h1(doc, "Section 4 — Governance, Control & Security")
add_styled_paragraph(
    doc,
    "Duration: 7 minutes · Login as: khalid.alsoodi (admin)",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "This section demonstrates the Brief #17 organizational access control model: a four-company org tree with departments and teams, document scoping with four classification levels, per-user clearance, per-document overrides, and Phase 6 soft-delete users with instant token invalidation.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 4.1 — Show the org tree")

add_step_block(
    doc, 1, "Navigate to /admin/organization",
    "In the sidebar, expand 'Admin' and click 'Organization'.",
    "The org tree page loads, showing 22 active nodes: Organization (root), 3 group departments (Executive, Finance, Legal & Compliance), 4 companies (Seekra Films, Seekra Creative, Seekra Studios, Seekra Broadcast), each with 3 teams. Each node shows member count and document count. Archived nodes are at the bottom, clearly marked.",
    screenshot="Organization tree admin page",
)

add_callout(
    doc,
    "SAY",
    "This is the org tree. Documents are scoped to any node — a document scoped to 'Seekra Films' is visible to anyone in Films Creative Direction, Films Production, or Films Finance & Admin (access flows DOWN the tree). A document scoped to 'Films · Production' is visible ONLY to Production team members. This is how Seekra enforces department-level confidentiality without per-document ACLs.",
)

add_h2(doc, "Step 4.2 — Show user management with clearance levels")

add_step_block(
    doc, 2, "Navigate to /admin/users",
    "Click 'Users' in the admin sidebar.",
    "The users page loads, showing all 16 active demo users. Each row shows: username, role, clearance level (1, 2, or 3), and an actions menu. 3 additional users are shown as deactivated (the UAT users).",
    screenshot="Users admin page with clearance levels",
)

add_callout(
    doc,
    "SAY",
    "Each user has a clearance level from 0 to 3. Level 1 (Internal) is the default — they can see Internal and Public documents in their scope. Level 2 (Confidential) adds Confidential documents. Level 3 (Restricted) adds Restricted. Admins and auditors bypass the clearance check entirely. This is the same model used in government and defense — finally available to commercial enterprises.",
)

add_h2(doc, "Step 4.3 — Live demo: soft-delete a user")

add_step_block(
    doc, 3, "Soft-delete the user 'hassan.alzaabi'",
    "In the users page, find hassan.alzaabi. Click the actions menu (three dots) and select 'Deactivate'.",
    "A confirmation dialog appears. Confirm. The user is immediately deactivated — their is_active flag is set to false, but the row is preserved for audit. A SECURITY_USER_DEACTIVATED event is logged.",
)

add_step_block(
    doc, 4, "Attempt to log in as Hassan",
    "Open a new incognito window. Navigate to https://app-internal.seekra.pk. Attempt to sign in with username hassan.alzaabi, password Demo@2026.",
    "Login fails with HTTP 403 'Account deactivated. Contact an administrator.' A SECURITY_LOGIN_FAILED event is logged with details 'Deactivated account hassan.alzaabi attempted sign-in'.",
    screenshot="Failed login for deactivated account",
)

add_step_block(
    doc, 5, "Verify Hassan's old token is invalidated",
    "If Hassan had been logged in elsewhere (e.g. a mobile device), his existing JWT token is now rejected on the next API call with HTTP 401 'Account deactivated'. The token check happens on every request — there is no grace period.",
    "Existing JWT tokens for Hassan are immediately rejected with HTTP 401 'Account deactivated' on the next API call.",
)

add_callout(
    doc,
    "SAY",
    "Soft-delete is the right way to offboard an employee. Their row stays in the database — so historical audit events still reference them — but they cannot log in, and any existing tokens are immediately rejected. Compare this to the alternative: hard-deleting the user would break the foreign key on every audit row they appear in. Soft-delete preserves the audit trail AND revokes access instantly.",
)

add_h2(doc, "Step 4.4 — Live demo: cross-scope override grant")

add_step_block(
    doc, 6, "Show that Ahmed (Films Production, clearance 1) cannot see doc 17 (Scene 12 Take 3, Confidential)",
    "Log in as ahmed.alketbi in an incognito window. Search for 'Scene 12 take 3'. Confirm zero results.",
    "Ahmed cannot see the confidential scene footage — it's in his department but above his clearance.",
)

add_step_block(
    doc, 7, "Grant Ahmed an override on doc 17",
    "Back in the admin window (as Khalid), navigate to /files/, find doc 17 (17_Scene12_Take3_OnSet.mp4), click the 'Manage Access' icon (key icon). In the overrides dialog, select ahmed.alketbi from the user dropdown, set can_read=true, add a reason 'cross-team review for VFX coordination', and click Grant.",
    "The override is created. An ACCESS_OVERRIDE_GRANTED audit event is logged. The smart-search cache is immediately flushed so the grant takes effect on Ahmed's next search — no 3-minute TTL wait.",
)

add_step_block(
    doc, 8, "Have Ahmed search again",
    "Back in Ahmed's incognito window, refresh the search page and search for 'Scene 12 take 3' again.",
    "Doc 17 now appears in Ahmed's results — the override crossed the clearance boundary. The classification badge still shows 'Confidential' (the override did NOT change the classification — it just granted Ahmed read access).",
    screenshot="Override grant takes effect immediately",
)

add_callout(
    doc,
    "SAY",
    "The override is the escape hatch for cross-team collaboration. When a project lead needs to bring in someone from another department for a specific document — without elevating their overall clearance — they grant an override. The override never elevates clearance: if the doc is Restricted (3) and the user is clearance 1, the override alone is NOT enough — they would also need clearance 3. This is defense in depth, designed in.",
)

add_h2(doc, "Step 4.5 — PII detection panel")

add_step_block(
    doc, 9, "Navigate to /admin/pii",
    "Click 'PII Detection' in the admin sidebar.",
    "The PII page lists all documents with detected personal data: 11_Employee_Passport_Roster.xlsx (passport numbers, Emirates IDs), 20_Films_Payroll_October_2026.xlsx (IBANs, account numbers), 25_Active_Client_List.csv (emails, phones, Emirates IDs), 08_Master_Services_Agreement_MiraStudios.pdf (signatory Emirates IDs, bank details). Each row shows: PII count, risk level (low/medium/high), and a masked sample (e.g. '784-••••-•••••••-•').",
    screenshot="PII detection admin page",
)

add_callout(
    doc,
    "SAY",
    "PII detection is report-only — it does not block uploads or modify stored content. But it does two critical things: (1) it masks PII before any content is sent to the LLM in chat, so the model never sees raw personal data; (2) it provides a complete inventory for your DPO, with masked samples that can be shared with regulators without exposing the actual data. This is the UAE PDPL and GDPR alignment story.",
)

add_h2(doc, "Step 4.6 — Governance overview")

add_step_block(
    doc, 10, "Navigate to /admin/governance",
    "Click 'Governance' in the admin sidebar.",
    "The governance page shows Seekra's policy framework: data classification policy, retention policy, access control policy, PII handling policy, audit chain verification status, and the hash-chain integrity check.",
    screenshot="Governance dashboard",
)

add_page_break(doc)

# ==========================================================================
# SECTION 5: PROVENANCE
# ==========================================================================

add_h1(doc, "Section 5 — Provenance")
add_styled_paragraph(
    doc,
    "Duration: 4 minutes · Login as: khalid.alsoodi (admin)",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "Provenance is the answer to 'how did the AI arrive at that answer?'. For every chat response, Seekra records the full pipeline: the original question, any reformulation, the retrieval legs (text, visual, cross-reference), the chunks that were retrieved, the LLM call (with model + token count), and the final answer. This pipeline is auditable and replayable.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 5.1 — Open provenance for a chat answer")

add_step_block(
    doc, 1, "Navigate to /chat and ask 'what is the budget for Project Golden Falcon?'",
    "Type the question and press Enter. Wait for the answer.",
    "Seekra returns an answer citing 15_Golden_Falcon_Budget_Breakdown.xlsx with specific figures (AED 48.2M total, AED 14.2M above-the-line, etc.).",
)

add_step_block(
    doc, 2, "Click the 'provenance' icon on the answer",
    "Below the answer, click the icon that looks like a tree/graph (or the 'Provenance' / 'Trace' link).",
    "The provenance view opens, showing a vertical timeline of the pipeline: (1) User question, (2) Query reformulation (if any), (3) Retrieval legs with chunk IDs and similarity scores, (4) LLM call with model name and token count, (5) Final answer with citations.",
    screenshot="Provenance timeline view",
)

add_callout(
    doc,
    "SAY",
    "This is the full lineage of the answer. You can see exactly which chunks were retrieved, what their similarity scores were, which model was called, and how many tokens were used. If a regulator or auditor asks 'why did the AI say that?', you can show them — chunk by chunk, score by score. There is no black box.",
)

add_h2(doc, "Step 5.2 — Confidence scores per source")

add_step_block(
    doc, 3, "Inspect the retrieval leg details",
    "In the provenance view, expand the 'Retrieval' section.",
    "Each retrieved chunk shows: document filename, page/chunk index, similarity score (0.0 to 1.0), and a confidence tier (high ≥ 0.65, medium ≥ 0.50, low < 0.50). High-confidence chunks are highlighted in green; low-confidence in amber.",
    screenshot="Retrieval leg with confidence scores",
)

add_callout(
    doc,
    "SAY",
    "Confidence scores tell you how strongly the system believes each source is relevant. If the answer cites a chunk with 0.42 similarity (low confidence), the client knows to verify. If it cites a chunk with 0.89 similarity (high confidence), they can trust it. This is the difference between 'the AI said X' and 'the AI said X, with 89% confidence, based on page 4 of the budget spreadsheet'.",
)

add_h2(doc, "Step 5.3 — Timestamp deep-link on video sources")

add_step_block(
    doc, 4, "Find a chat answer that cites a video (e.g. 'what happens in Scene 12?')",
    "Ask 'what happens in Scene 12 of Golden Falcon?'. Wait for the answer.",
    "Seekra cites 17_Scene12_Take3_OnSet.mp4 with a timestamp chip (e.g. '0:08'). Clicking the chip opens the viewer at that exact moment, showing the specific frame where the telescope lifts from the altar.",
    screenshot="Video timestamp deep-link from chat citation",
)

add_callout(
    doc,
    "SAY",
    "For video evidence — security footage, training videos, film dailies — this is transformative. You can ask 'when did the forklift operator first enter the frame?' and Seekra will cite the exact second. No more scrubbing through hours of footage.",
)

add_page_break(doc)

# ==========================================================================
# SECTION 6: ENTITY RELATIONS
# ==========================================================================

add_h1(doc, "Section 6 — Entity Relations")
add_styled_paragraph(
    doc,
    "Duration: 4 minutes · Login as: khalid.alsoodi (admin)",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "Seekra automatically extracts persons, organizations, locations, and other entities from every document — in Arabic and English. These entities form a knowledge graph: 'Sara Al Kindy' appears in the script, the budget, the call sheet, and the contract — Seekra links them all. This is brief 16's entity graph feature.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 6.1 — Open the entities page")

add_step_block(
    doc, 1, "Navigate to /admin/entities",
    "Click 'Entities' in the admin sidebar.",
    "The entities page loads, showing extracted entities grouped by type: Persons (e.g. Khalid Alsoodi, Sara Al Kindy, Yousef Al Saedi, Mira Hassan Bensaleh, Fatima Al Mansouri), Organizations (Seekra Films, Mira Studios, Netflix MENA, Dubai Tourism), Locations (Dubai, Jebel Jais, Al Fahidi, DIFC, Dubai Studio City). Each entity shows a document count.",
    screenshot="Entities admin page",
)

add_h2(doc, "Step 6.2 — Inspect an entity's neighborhood")

add_step_block(
    doc, 2, "Click on the entity 'Project Golden Falcon'",
    "In the entities list, find 'Project Golden Falcon' (it may be under 'Concepts' or 'Titles') and click it.",
    "The entity detail page opens, showing: (a) all documents that mention this entity (12_Golden_Falcon_Script, 13_Creative_Treatment, 14_Director_Vision_Notes, 15_Budget_Breakdown, 16_Call_Sheet, 17_Scene12_Take3, 18_Field_Audio_Update, 29_VFX_Shot_List, 30_Sound_Design_Brief — 9 documents), (b) co-occurring entities (Sara Al Kindy, Yousef Al Saedi, Jebel Jais, Mira Studios, Scene 12).",
    screenshot="Entity detail page for Project Golden Falcon",
)

add_h2(doc, "Step 6.3 — View the entity graph visualization")

add_step_block(
    doc, 3, "Click 'View Graph' or 'Relationships'",
    "On the entity detail page, click the graph icon or 'Relationships' tab.",
    "A force-directed graph visualization loads. 'Project Golden Falcon' is the central node. Connected nodes radiate outward: people (Yousef, Sara, Layla), places (Jebel Jais, Al Fahidi), organizations (Mira Studios, Netflix), and other entities (Scene 12, the telescope). Edge labels show the relationship type: CO_OCCURS, MENTIONED_IN, DIRECTED_BY, PRODUCED_BY.",
    screenshot="Entity relationship graph visualization",
)

add_callout(
    doc,
    "SAY",
    "This graph was built automatically — no human tagged these relationships. Seekra's entity extraction ran on every document during indexing, found the named entities, and inferred co-occurrence relationships. The graph updates every time you upload a new document. This is your enterprise knowledge graph — answering 'who works on what?', 'where is this project happening?', 'who are our key vendors?' — without anyone curating it.",
)

add_h2(doc, "Step 6.4 — Entity-aware chat")

add_step_block(
    doc, 4, "In chat, ask 'who is the director of Golden Falcon?'",
    "Navigate to /chat. Type 'who is the director of Golden Falcon?' and press Enter.",
    "Seekra answers 'Yousef Al Saedi is the director of Project Golden Falcon' — citing 12_Golden_Falcon_Script_v3.pdf (which lists him as writer/director) and 15_Golden_Falcon_Budget_Breakdown.xlsx (which lists his director fee). The entity-aware retrieval recognized 'Yousef Al Saedi' as a person entity and 'Project Golden Falcon' as a title entity, then matched them via the entity graph.",
    screenshot="Entity-aware chat answer",
)

add_callout(
    doc,
    "SAY",
    "The chat didn't just keyword-match 'director' — it understood that 'Yousef Al Saedi' is a person and 'Project Golden Falcon' is a project, and it used the entity graph to find the relationship between them. This is what 'content-aware intelligence' means: the system understands the structure of your content, not just the words.",
)

add_page_break(doc)

# ==========================================================================
# SECTION 7: MOBILE + VOICE
# ==========================================================================

add_h1(doc, "Section 7 — Mobile + Voice")
add_styled_paragraph(
    doc,
    "Duration: 3 minutes · Use: mobile device or responsive view",
    italic=True, color=SEEKRA_GREY,
)

add_styled_paragraph(
    doc,
    "Seekra is fully responsive and supports Arabic-first voice commands. On a phone, the sidebar collapses to a hamburger menu, the chat input supports voice-to-text, and the viewer supports voice-driven page navigation. This is Brief #11's voice-driven document navigation feature.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

add_h2(doc, "Step 7.1 — Mobile layout")

add_step_block(
    doc, 1, "Open the demo URL on a phone (or use Chrome DevTools mobile view)",
    "On your mobile device, open Chrome and navigate to https://app-internal.seekra.pk. Sign in as khalid.alsoodi.",
    "The mobile layout loads: top bar with hamburger menu (left) and user avatar (right). The sidebar is hidden by default and slides in as a drawer when the hamburger is tapped. Search, Chat, and Files are accessible from the bottom navigation bar.",
    screenshot="Mobile layout with bottom nav",
)

add_h2(doc, "Step 7.2 — Voice commands in chat")

add_step_block(
    doc, 2, "Open chat and tap the microphone icon",
    "Tap 'Chat' in the bottom nav. Tap the microphone icon next to the chat input. Browser prompts for microphone permission. Grant it. Speak a command: 'search for customer list' or 'next page' or 'summarize this document'.",
    "Seekra recognizes the spoken command (English or Arabic) and executes it. 'Search for X' navigates to the search page with the query. 'Next page' / 'previous page' navigates within the document viewer. 'Summarize' triggers a summary of the currently open document.",
    screenshot="Voice command in chat",
)

add_callout(
    doc,
    "SAY",
    "Voice is critical for hands-busy professionals — a film director on set, a safety officer walking a warehouse, a CFO in a meeting. Speak in Arabic or English, Seekra understands both. This is not a generic speech-to-text layer; the voice command grammar is tuned for document navigation use cases.",
)

add_page_break(doc)

# ==========================================================================
# SECTION 8: WRAP-UP & Q&A
# ==========================================================================

add_h1(doc, "Section 8 — Wrap-up & Q&A")
add_styled_paragraph(
    doc,
    "Duration: 3 minutes",
    italic=True, color=SEEKRA_GREY,
)

add_h2(doc, "Recap the Three Pillars")

add_callout(
    doc,
    "PILLAR 1 — Trustworthy AI",
    "Every answer is cited. PII is masked before the LLM sees it. The system abstains rather than hallucinates. Provenance is auditable. The audit trail is hash-chained and tamper-evident.",
)

add_callout(
    doc,
    "PILLAR 2 — Granular Access Control",
    "A four-company org tree with departments and teams. Four classification levels. Per-user clearance. Per-document overrides that cross the org boundary without elevating clearance. Soft-delete users with instant token invalidation. All enforced at the SQL layer — defense in depth.",
)

add_callout(
    doc,
    "PILLAR 3 — Arabic-first, Air-gap Ready",
    "Native Arabic NER, RTL rendering, Arabic voice commands. Self-hosted (no cloud dependency). Air-gap deployment option for sensitive environments. UAE PDPL and GDPR aligned. Your data never leaves your tenant.",
)

add_h2(doc, "Pricing Tiers (for the Q&A)")

add_table(
    doc,
    headers=["Tier", "Deployment", "Best For", "Indicative Pricing"],
    rows=[
        ("Cloud Native", "Seekra-managed AWS UAE region", "SMBs, pilots, fast start", "[Contact sales]"),
        ("Self-Hosted", "Customer's cloud or on-prem", "Mid-market, regulated industries", "[Contact sales]"),
        ("Air-Gapped", "Fully disconnected, customer data center", "Government, defense, classified", "[Contact sales]"),
    ],
    col_widths=[3, 4.5, 5, 4],
)

add_h2(doc, "Common Questions to Anticipate")

add_h3(doc, "Q: How does Seekra handle documents in languages other than Arabic and English?")
add_styled_paragraph(
    doc,
    "Seekra's pipeline is language-agnostic for indexing (any UTF-8 text is indexed). The Arabic NER model is specialized for Arabic; English uses spaCy. For other languages (French, Hindi, Urdu), we can integrate additional NER models on request. Chat answers are generated in the language of the question.",
)

add_h3(doc, "Q: What LLMs does Seekra support?")
add_styled_paragraph(
    doc,
    "Seekra is LLM-agnostic. The current deployment uses Groq (llama-3.3-70b-versatile) for speed, with Gemini 2.5 Flash as fallback. For air-gapped deployments, we support Ollama with Qwen 2.5 (7B or 3B) running on customer GPUs. The retrieval pipeline (embeddings, reranking) uses BGE-M3 via Ollama.",
)

add_h3(doc, "Q: How is PII detected? Can it be customized?")
add_styled_paragraph(
    doc,
    "Seekra uses regex patterns for structured PII (Emirates IDs, passports, IBANs, phone numbers, emails) plus a CAMeL-based Arabic NER model for unstructured PII (person names, organizations, locations). Custom PII patterns (e.g. internal employee IDs, project codenames) can be added via configuration. PII detection is report-only — it never blocks uploads or modifies stored content.",
)

add_h3(doc, "Q: What's the maximum document size? File count?")
add_styled_paragraph(
    doc,
    "Max upload size: 500 MB (configurable). No hard limit on file count — performance degrades gracefully past 100K documents due to vector index size. For larger corpora, we recommend sharding by department or year.",
)

add_h3(doc, "Q: How long does deployment take?")
add_styled_paragraph(
    doc,
    "Cloud Native: 1 day (Seekra-managed). Self-Hosted: 1–2 weeks (customer infrastructure team + Seekra support). Air-Gapped: 4–8 weeks (includes hardware procurement, security hardening, and acceptance testing).",
)

add_h2(doc, "Next Steps")

add_bullet(doc, "Schedule a technical deep-dive with the Seekra solutions architect (2 hours) to map your specific use cases to the platform.")
add_bullet(doc, "Provision a 30-day proof-of-concept tenant with your own documents (we provide the upload script and content classification guidance).")
add_bullet(doc, "If self-hosted: share your infrastructure details (cloud provider, region, GPU availability) for a deployment plan.")
add_bullet(doc, "Reference: this run book, the Seekra product profile, and the Brief #17 (Enterprise Access Control) technical brief — all available in /home/z/my-project/download/.")

add_page_break(doc)

# ==========================================================================
# APPENDIX A: USER ROSTER
# ==========================================================================

add_h1(doc, "Appendix A — Demo User Roster")
add_styled_paragraph(
    doc,
    "All 16 demo users share password: Demo@2026 (except admin which is A!!!@@@2026). 3 additional UAT users are soft-deactivated and preserved for audit history.",
    italic=True, color=SEEKRA_GREY,
)

add_table(
    doc,
    headers=["#", "Username", "Role", "Clr", "Department", "Arabic Name"],
    rows=[
        ("1", "khalid.alsoodi", "admin", "3", "Group Executive", "خالد السودي"),
        ("2", "fatima.almansouri", "editor", "3", "Group Finance", "فاطمة المنصوري"),
        ("3", "omar.alhashimi", "auditor", "3", "Group Legal & Compliance", "عمر الهاشمي"),
        ("4", "sara.alkindy", "editor", "3", "Seekra Films (GM)", "سارة الكندي"),
        ("5", "yousef.alsaedi", "editor", "2", "Films · Creative Direction", "يوسف السعيدي"),
        ("6", "layla.almehrabi", "viewer", "2", "Films · Production", "ليلى المهرابي"),
        ("7", "ahmed.alketbi", "viewer", "1", "Films · Production", "أحمد الكتبي"),
        ("8", "mohammed.almarri", "editor", "3", "Seekra Creative (GM)", "محمد المري"),
        ("9", "nora.alsuwaidi", "viewer", "2", "Creative · Direction", "نورة السويدي"),
        ("10", "hassan.alzaabi", "viewer", "1", "Creative · Sales & Client Services", "حسن الزعبي"),
        ("11", "reem.alfalasi", "editor", "3", "Seekra Studios (GM)", "ريم الفلاسي"),
        ("12", "khalid.almazrouei", "viewer", "2", "Studios · VFX", "خالد المزروعي"),
        ("13", "mouna.bensaleh", "viewer", "1", "Studios · Sound Design", "منى بن صالح"),
        ("14", "tariq.alqassimi", "editor", "3", "Seekra Broadcast (GM)", "طارق القاسمي"),
        ("15", "amira.benhassan", "viewer", "2", "Broadcast · Programming", "أميرة بن حسن"),
        ("16", "salem.aldhaheri", "viewer", "1", "Broadcast · Sales & Distribution", "سالم الظاهري"),
    ],
    col_widths=[0.8, 4.0, 1.8, 0.8, 5.5, 3.6],
)

add_page_break(doc)

# ==========================================================================
# APPENDIX B: DOCUMENT INVENTORY
# ==========================================================================

add_h1(doc, "Appendix B — Document Inventory (32 docs)")

add_styled_paragraph(
    doc,
    "All 32 documents in the demo repository, grouped by department and showing classification, file type, and PII status.",
    italic=True, color=SEEKRA_GREY,
)

add_table(
    doc,
    headers=["ID", "Filename", "Type", "Scope", "Cls", "PII"],
    rows=[
        # Group Executive
        ("01", "Employee_Handbook_2026.pdf", "PDF", "Group Executive", "1", "Y"),
        ("02", "Q3_Board_Meeting_Minutes.docx", "DOCX", "Group Executive", "2", "N"),
        ("03", "Group_Strategy_2026-2027.pptx", "PPTX", "Group Executive", "3", "N"),
        ("04", "All_Hands_Team_Photo.jpg", "JPG", "Group Executive", "0", "N"),
        # Group Finance
        ("05", "Q3_Earnings_Briefing.mp3", "MP3", "Group Finance", "3", "N"),
        ("06", "Q3_Financial_Statements.xlsx", "XLSX", "Group Finance", "3", "N"),
        ("07", "Budget_Review_Photo.jpg", "JPG", "Group Finance", "2", "N"),
        # Group Legal & Compliance
        ("08", "Master_Services_Agreement_MiraStudios.pdf", "PDF", "Group Legal & Compliance", "3", "Y"),
        ("09", "Customer_Data_Protection_Policy.docx", "DOCX", "Group Legal & Compliance", "2", "Y"),
        ("10", "Internal_Policies_Arabic.docx", "DOCX", "Group Legal & Compliance", "1", "Y"),
        ("11", "Employee_Passport_Roster.xlsx", "XLSX", "Group Legal & Compliance", "3", "Y"),
        # Films Creative Direction
        ("12", "Golden_Falcon_Script_v3.pdf", "PDF", "Films · Creative Direction", "2", "N"),
        ("13", "Golden_Falcon_Creative_Treatment.pptx", "PPTX", "Films · Creative Direction", "2", "N"),
        ("14", "Director_Vision_Notes.txt", "TXT", "Films · Creative Direction", "2", "N"),
        # Films Production
        ("15", "Golden_Falcon_Budget_Breakdown.xlsx", "XLSX", "Films · Production", "3", "N"),
        ("16", "Daily_Call_Sheet_2026-09-15.pdf", "PDF", "Films · Production", "1", "N"),
        ("17", "Scene12_Take3_OnSet.mp4", "MP4", "Films · Production", "2", "N"),
        ("18", "Field_Audio_Update_Day4.mp3", "MP3", "Films · Production", "2", "N"),
        # Films Finance & Admin
        ("19", "Films_Vendor_Invoices.csv", "CSV", "Films · Finance & Admin", "2", "N"),
        ("20", "Films_Payroll_October_2026.xlsx", "XLSX", "Films · Finance & Admin", "3", "N"),
        # Creative Direction
        ("21", "Emirates_Advertising_Awards_Brief.pdf", "PDF", "Creative · Direction", "2", "N"),
        ("22", "Dubai_Tourism_Pitch_Deck.pptx", "PPTX", "Creative · Direction", "2", "N"),
        # Creative Production
        ("23", "Golden_Falcon_Logo_Concept.png", "PNG", "Creative · Production", "0", "N"),
        ("24", "Branding_Display.jpg", "JPG", "Creative · Production", "0", "N"),
        # Creative Sales
        ("25", "Active_Client_List.csv", "CSV", "Creative · Sales & Client Services", "3", "N"),
        ("26", "Dubai_Tourism_Contract.pdf", "PDF", "Creative · Sales & Client Services", "2", "N"),
        # Studios Post-Production
        ("27", "Warehouse_Safety_Procedures.docx", "DOCX", "Studios · Post-Production", "1", "N"),
        ("28", "Golden_Falcon_Edit_Schedule.xlsx", "XLSX", "Studios · Post-Production", "1", "N"),
        # Studios VFX
        ("29", "VFX_Shot_List_Scene12.pdf", "PDF", "Studios · VFX", "2", "N"),
        # Studios Sound Design
        ("30", "Sound_Design_Brief.docx", "DOCX", "Studios · Sound Design", "1", "N"),
        # Broadcast Programming
        ("31", "City_Street_Stock_Footage.mp4", "MP4", "Broadcast · Programming", "0", "N"),
        # Broadcast Sales & Distribution
        ("32", "Streaming_Distribution_Agreement.pdf", "PDF", "Broadcast · Sales & Distribution", "3", "N"),
    ],
    col_widths=[0.8, 6.5, 1.2, 5.5, 0.8, 0.8],
)

add_styled_paragraph(
    doc,
    "Classification legend: 0 = Public (visible to all, even cross-scope) · 1 = Internal (default, anyone in scope) · 2 = Confidential (clearance ≥ 2) · 3 = Restricted (clearance = 3 only).",
    italic=True, color=SEEKRA_GREY, size=10,
)

add_page_break(doc)

# ==========================================================================
# APPENDIX C: TROUBLESHOOTING
# ==========================================================================

add_h1(doc, "Appendix C — Troubleshooting")

add_h2(doc, "Login fails with 'Too many failed sign-in attempts'")
add_styled_paragraph(
    doc,
    "Wait 15 minutes for the throttle to clear, or ask the demo admin to unlock the account via /admin/users → Unlock. The throttle is per-username + per-IP, so switching networks also clears it.",
)

add_h2(doc, "Smart search returns zero results for an obviously-relevant query")
add_styled_paragraph(
    doc,
    "Check that the document is in the user's scope. Log in as admin and run the same query — if admin sees results but the viewer doesn't, it's a scope/clearance issue (expected behavior). If admin also sees nothing, the document may still be in 'processing' status — wait 60 seconds and retry.",
)

add_h2(doc, "Chat returns 'I don't have enough information' for a question that should be answerable")
add_styled_paragraph(
    doc,
    "Three common causes: (1) the document is still being indexed (wait 60s); (2) the document is outside the user's scope (verify as admin); (3) the query reformulation layer rewrote the question in a way that didn't match — try rephrasing or click 'debug legs' in the chat UI to see what was retrieved.",
)

add_h2(doc, "Audio/video file won't play in the viewer")
add_styled_paragraph(
    doc,
    "Browser autoplay policies may block media until the user clicks play. Ensure the browser has audio enabled. For MP4, Seekra uses native HTML5 video — no plugin required. For MP3, the audio player supports seeking via the timestamp chips in chat citations.",
)

add_h2(doc, "Mobile voice command doesn't recognize speech")
add_styled_paragraph(
    doc,
    "Verify microphone permission is granted to the browser. Chrome on Android and Safari on iOS both support the Web Speech API used by Seekra. If recognition is poor, try speaking more slowly or moving to a quieter environment. Arabic recognition uses CAMeL-trained models tuned for Gulf dialect.",
)

add_h2(doc, "Need to reset the demo state")
add_styled_paragraph(
    doc,
    "If the demo gets into a bad state (e.g. a user was hard-deleted, or a document was mis-scoped), the cleanup + re-upload scripts are in /home/z/my-project/scripts/. Run demo_cleanup.py first, then upload_demo_docs_v2.py. The full reset takes ~5 minutes.",
)

# Save
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
print(f"Run book saved: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")
