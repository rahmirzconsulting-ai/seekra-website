#!/usr/bin/env python3
from __future__ import annotations
"""Helper functions for demo doc generation."""

"""Generate 32 demo documents for Seekra Media Holdings (Dubai).

Output directory: /home/z/my-project/scripts/demo_docs/

Each document is a real file with realistic content matching the storyline:
"Project Golden Falcon" — a feature film produced by Seekra Films, with
marketing by Seekra Creative, post-production by Seekra Studios, and
distribution by Seekra Broadcast.

File types generated: PDF (reportlab), DOCX (python-docx), XLSX (openpyxl),
PPTX (python-pptx), TXT/CSV (stdlib), MP3 (pyttsx3), MP4 (ffmpeg + PIL),
JPG/PNG (PIL).

Documents include intentional PII in 4 files (passport roster, payroll,
client list, MSA) for PII detection/masking demos.
"""

import csv
import io
import os
import random
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any

# Defer heavy imports until needed inside generator functions
OUT = Path("/home/z/my-project/scripts/demo_docs")
OUT.mkdir(parents=True, exist_ok=True)

# Color palette for branding (Seekra purple/teal)
SEEKRA_PRIMARY = (76, 41, 145)       # #4C2991
SEEKRA_ACCENT = (0, 168, 150)       # #00A896
SEEKRA_GOLD = (212, 175, 55)        # #D4AF37
SEEKRA_DARK = (24, 28, 40)
SEEKRA_LIGHT = (245, 247, 250)


def write_text(filename: str, content: str) -> Path:
    p = OUT / filename
    p.write_text(content, encoding="utf-8")
    return p


def write_csv(filename: str, rows: list[list[Any]], headers: list[str]) -> Path:
    p = OUT / filename
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return p


def write_pdf(filename: str, title: str, paragraphs: list[str],
              subtitle: str = "", metadata: dict | None = None) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

    p = OUT / filename
    doc = SimpleDocTemplate(
        str(p), pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2.5 * cm, bottomMargin=2.2 * cm,
        title=title, author="Seekra Media Holdings",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "SeekraTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=20, leading=24,
        textColor=HexColor("#4C2991"), alignment=TA_LEFT, spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "SeekraSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, leading=14,
        textColor=HexColor("#506070"), spaceAfter=18,
    )
    h2_style = ParagraphStyle(
        "SeekraH2", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=13, leading=16,
        textColor=HexColor("#1A2B40"), spaceBefore=12, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "SeekraBody", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=10.5, leading=15,
        textColor=HexColor("#182030"), alignment=TA_JUSTIFY, spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        "SeekraBullet", parent=body_style,
        leftIndent=14, bulletIndent=2, spaceAfter=4,
    )

    story = [Paragraph(title, title_style)]
    if subtitle:
        story.append(Paragraph(subtitle, sub_style))
    # Thin rule
    story.append(Table(
        [[""]], colWidths=[16.5 * cm], rowHeights=[2],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#4C2991")),
            ("LINEBELOW", (0, 0), (-1, -1), 0, HexColor("#4C2991")),
        ]),
    ))
    story.append(Spacer(1, 12))

    for para in paragraphs:
        if para.startswith("## "):
            story.append(Paragraph(para[3:], h2_style))
        elif para.startswith("- "):
            story.append(Paragraph(para[2:], bullet_style, bulletText="•"))
        elif para == "---PAGEBREAK---":
            story.append(PageBreak())
        else:
            story.append(Paragraph(para, body_style))

    if metadata:
        story.append(Spacer(1, 18))
        meta_tbl = Table(
            [[k, v] for k, v in metadata.items()],
            colWidths=[5 * cm, 11.5 * cm],
        )
        meta_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("TEXTCOLOR", (0, 0), (0, -1), HexColor("#506070")),
            ("TEXTCOLOR", (1, 0), (1, -1), HexColor("#182030")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -2), 0.25, HexColor("#E0E4E8")),
        ]))
        story.append(meta_tbl)

    doc.build(story)
    return p


def write_docx(filename: str, title: str, paragraphs: list[tuple[str, str]],
               subtitle: str = "") -> Path:
    """paragraphs is a list of (style, text) tuples where style is one of:
    'h1', 'h2', 'body', 'bullet', 'quote'"""
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    p = OUT / filename
    doc = Document()
    # Page setup
    for section in doc.sections:
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.2)

    # Title
    t = doc.add_paragraph()
    run = t.add_run(title)
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x4C, 0x29, 0x91)
    run.font.name = "Calibri"

    if subtitle:
        sp = doc.add_paragraph()
        srun = sp.add_run(subtitle)
        srun.font.size = Pt(11)
        srun.font.color.rgb = RGBColor(0x50, 0x60, 0x70)
        srun.font.italic = True

    # Horizontal rule via paragraph border
    def add_hr(paragraph):
        p_pr = paragraph._p.get_or_add_pPr()
        p_bdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "4C2991")
        p_bdr.append(bottom)
        p_pr.append(p_bdr)
    hr_para = doc.add_paragraph()
    add_hr(hr_para)

    for style, text in paragraphs:
        if style == "h1":
            para = doc.add_paragraph()
            r = para.add_run(text)
            r.font.bold = True
            r.font.size = Pt(14)
            r.font.color.rgb = RGBColor(0x1A, 0x2B, 0x40)
            para.paragraph_format.space_before = Pt(14)
            para.paragraph_format.space_after = Pt(6)
        elif style == "h2":
            para = doc.add_paragraph()
            r = para.add_run(text)
            r.font.bold = True
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(0x4C, 0x29, 0x91)
            para.paragraph_format.space_before = Pt(10)
            para.paragraph_format.space_after = Pt(4)
        elif style == "body":
            para = doc.add_paragraph(text)
            para.paragraph_format.line_spacing = 1.3
            para.paragraph_format.space_after = Pt(6)
            for r in para.runs:
                r.font.size = Pt(11)
        elif style == "bullet":
            para = doc.add_paragraph(text, style="List Bullet")
            for r in para.runs:
                r.font.size = Pt(11)
        elif style == "quote":
            para = doc.add_paragraph(text)
            para.paragraph_format.left_indent = Inches(0.5)
            para.paragraph_format.right_indent = Inches(0.5)
            para.paragraph_format.line_spacing = 1.3
            for r in para.runs:
                r.font.size = Pt(10.5)
                r.font.italic = True
                r.font.color.rgb = RGBColor(0x50, 0x60, 0x70)
        elif style == "pagebreak":
            doc.add_page_break()

    doc.save(str(p))
    return p


def write_xlsx(filename: str, sheets: list[dict]) -> Path:
    """sheets is a list of {'name': str, 'headers': list[str], 'rows': list[list]}"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    p = OUT / filename
    wb = Workbook()
    wb.remove(wb.active)
    header_font = Font(bold=True, color="FFFFFF", size=11, name="Calibri")
    header_fill = PatternFill("solid", fgColor="4C2991")
    body_font = Font(size=10.5, name="Calibri")
    thin_border = Border(
        left=Side(style="thin", color="E0E4E8"),
        right=Side(style="thin", color="E0E4E8"),
        top=Side(style="thin", color="E0E4E8"),
        bottom=Side(style="thin", color="E0E4E8"),
    )
    for sheet in sheets:
        ws = wb.create_sheet(sheet["name"])
        # Headers
        for col_idx, header in enumerate(sheet["headers"], 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.border = thin_border
        # Body
        for row_idx, row in enumerate(sheet["rows"], 2):
            for col_idx, val in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = body_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="left", vertical="top")
        # Auto-width
        for col_idx, header in enumerate(sheet["headers"], 1):
            max_len = len(str(header))
            for row in sheet["rows"]:
                if col_idx - 1 < len(row):
                    max_len = max(max_len, len(str(row[col_idx - 1])))
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 40)
        ws.row_dimensions[1].height = 22
        ws.freeze_panes = "A2"
    wb.save(str(p))
    return p


def write_pptx(filename: str, title: str, slides: list[dict]) -> Path:
    """slides is a list of {'title': str, 'body': list[str]}"""
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    p = OUT / filename
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Title slide
    slide = prs.slides.add_slide(blank_layout)
    # Background — use a full-slide rectangle shape instead of raw XML
    from pptx.enum.shapes import MSO_SHAPE
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height,
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = RGBColor(0x4C, 0x29, 0x91)
    bg_shape.line.fill.background()
    # Send to back (already first shape, but ensure z-order)
    spTree = bg_shape._element.getparent()
    spTree.remove(bg_shape._element)
    spTree.insert(2, bg_shape._element)
    # Title text
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.7), Inches(2))
    tf = tb.text_frame
    tf.word_wrap = True
    p_para = tf.paragraphs[0]
    p_para.text = title
    p_para.alignment = PP_ALIGN.LEFT
    for r in p_para.runs:
        r.font.size = Pt(44)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.name = "Calibri"

    # Body slides
    for slide_data in slides:
        slide = prs.slides.add_slide(blank_layout)
        # Title bar
        title_bar = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12.3), Inches(1))
        tf = title_bar.text_frame
        tf.word_wrap = True
        p_para = tf.paragraphs[0]
        p_para.text = slide_data.get("title", "")
        for r in p_para.runs:
            r.font.size = Pt(28)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x4C, 0x29, 0x91)
            r.font.name = "Calibri"

        # Underline
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.5), Inches(1.4), Inches(12.3), Pt(2),
        )
        line.fill.solid()
        line.fill.fore_color.rgb = RGBColor(0x00, 0xA8, 0x96)
        line.line.fill.background()

        # Body
        body = slide_data.get("body", [])
        if body:
            body_tb = slide.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(12.1), Inches(5.2))
            bf = body_tb.text_frame
            bf.word_wrap = True
            for i, line_text in enumerate(body):
                if i == 0:
                    para = bf.paragraphs[0]
                else:
                    para = bf.add_paragraph()
                para.text = line_text
                para.alignment = PP_ALIGN.LEFT
                para.space_after = Pt(8)
                for r in para.runs:
                    r.font.size = Pt(16)
                    r.font.color.rgb = RGBColor(0x18, 0x20, 0x30)
                    r.font.name = "Calibri"

    prs.save(str(p))
    return p


def write_jpg(filename: str, label: str, subtitle: str = "",
              bg_color: tuple = (244, 247, 252)) -> Path:
    from PIL import Image, ImageDraw, ImageFont
    p = OUT / filename
    img = Image.new("RGB", (1280, 960), bg_color)
    d = ImageDraw.Draw(img)
    # Top color bar
    d.rectangle([(0, 0), (1280, 160)], fill=SEEKRA_PRIMARY)
    # Gold accent line
    d.rectangle([(0, 160), (1280, 168)], fill=SEEKRA_GOLD)
    # Brand mark
    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72
        )
        sub_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28
        )
        tag_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22
        )
    except IOError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()
    # Title in top bar
    d.text((60, 50), "SEEKRA MEDIA HOLDINGS", font=sub_font, fill=(255, 255, 255))
    # Main label (centered)
    bbox = d.textbbox((0, 0), label, font=title_font)
    w = bbox[2] - bbox[0]
    d.text(((1280 - w) / 2, 380), label, font=title_font, fill=SEEKRA_DARK)
    if subtitle:
        bbox = d.textbbox((0, 0), subtitle, font=sub_font)
        w = bbox[2] - bbox[0]
        d.text(((1280 - w) / 2, 510), subtitle, font=sub_font, fill=SEEKRA_ACCENT)
    # Footer
    d.text((60, 880), "© 2026 Seekra Media Holdings · Dubai, UAE", font=tag_font, fill=(120, 130, 150))
    img.save(str(p), quality=85)
    return p


def write_png(filename: str, label: str, subtitle: str = "") -> Path:
    return write_jpg(filename, label, subtitle)


def write_mp3(filename: str, text: str, rate: int = 150) -> Path:
    """Generate an MP3 audio file with synthesized narration via pyttsx3 + ffmpeg."""
    import pyttsx3
    p = OUT / filename
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_wav.close()
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.save_to_file(text, tmp_wav.name)
        engine.runAndWait()
        engine.stop()  # critical: ensures WAV file is fully flushed
        # Convert wav -> mp3
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_wav.name, "-codec:a", "libmp3lame",
             "-b:a", "96k", str(p)],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(tmp_wav.name)
    return p


def write_mp4(filename: str, label: str, subtitle: str = "",
              duration: int = 12) -> Path:
    """Generate a short MP4 video with a branded still frame + audio narration."""
    from PIL import Image, ImageDraw, ImageFont
    p = OUT / filename
    # 1. Generate a still frame (1920x1080)
    frame = Image.new("RGB", (1920, 1080), (245, 247, 252))
    d = ImageDraw.Draw(frame)
    d.rectangle([(0, 0), (1920, 200)], fill=SEEKRA_PRIMARY)
    d.rectangle([(0, 200), (1920, 210)], fill=SEEKRA_GOLD)
    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100
        )
        sub_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 44
        )
        tag_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30
        )
    except IOError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()
    d.text((100, 70), "SEEKRA MEDIA HOLDINGS — DUBAI", font=sub_font, fill=(255, 255, 255))
    bbox = d.textbbox((0, 0), label, font=title_font)
    w = bbox[2] - bbox[0]
    d.text(((1920 - w) / 2, 420), label, font=title_font, fill=SEEKRA_DARK)
    if subtitle:
        bbox = d.textbbox((0, 0), subtitle, font=sub_font)
        w = bbox[2] - bbox[0]
        d.text(((1920 - w) / 2, 580), subtitle, font=sub_font, fill=SEEKRA_ACCENT)
    d.text((100, 1000), "© 2026 Seekra Media Holdings · Dubai International Financial Centre",
           font=tag_font, fill=(120, 130, 150))

    tmp_frame = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp_frame.close()
    frame.save(tmp_frame.name)

    # 2. Generate silent MP4 from the still frame
    tmp_mp4 = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp_mp4.close()
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", tmp_frame.name,
             "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p",
             "-r", "30", "-vf", "scale=1920:1080", tmp_mp4.name],
            check=True, capture_output=True,
        )
        # 3. Add silent audio track (so the MP4 is recognized as having audio)
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp4.name,
             "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
             "-c:v", "copy", "-c:a", "aac", "-shortest", str(p)],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(tmp_frame.name)
        os.unlink(tmp_mp4.name)
    return p


# ==========================================================================
# Document definitions — content for each of the 32 demo documents
# ==========================================================================
