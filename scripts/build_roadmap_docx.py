#!/usr/bin/env python3
"""Generate Seekra_Roadmap_Options_E_F_G_H.docx — the 4 strategic options
for the next big work after Brief #31, with recommended sequence.

Output: /home/z/my-project/download/Seekra_Roadmap_Options_E_F_G_H.docx
"""
from __future__ import annotations
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = Path("/home/z/my-project/download/Seekra_Roadmap_Options_E_F_G_H.docx")

SEEKRA_PRIMARY = RGBColor(0x4C, 0x29, 0x91)
SEEKRA_ACCENT = RGBColor(0x00, 0xA8, 0x96)
SEEKRA_GOLD = RGBColor(0xD4, 0xAF, 0x37)
SEEKRA_DARK = RGBColor(0x18, 0x20, 0x2A)
SEEKRA_GREY = RGBColor(0x50, 0x60, 0x70)


def set_cell_shading(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def add_horizontal_rule(doc, color="4C2991", size=12):
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


def add_p(doc, text, *, size=11, bold=False, italic=False, color=SEEKRA_DARK,
          alignment=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6,
          line_spacing=1.3, font_name="Calibri", indent_first=False):
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


def add_callout(doc, label, text, *, label_color=SEEKRA_ACCENT):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    cell.width = Cm(16.5)
    set_cell_shading(cell, "F5F7FA")
    tc_pr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge, color, sz in [("left", "00A896", "24"), ("top", "E0E4E8", "4"),
                            ("bottom", "E0E4E8", "4"), ("right", "E0E4E8", "4")]:
        elem = OxmlElement(f"w:{edge}")
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), sz)
        elem.set(qn("w:color"), color)
        tcBorders.append(elem)
    tc_pr.append(tcBorders)
    p_label = cell.paragraphs[0]
    p_label.paragraph_format.space_before = Pt(4)
    p_label.paragraph_format.space_after = Pt(2)
    r = p_label.add_run(label)
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = label_color
    r.font.name = "Calibri"
    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_after = Pt(4)
    p_body.paragraph_format.line_spacing = 1.3
    r2 = p_body.add_run(text)
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = SEEKRA_DARK
    r2.font.name = "Calibri"
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(6)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
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
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


# --------------------------------------------------------------------------
# Build document
# --------------------------------------------------------------------------

doc = Document()
for section in doc.sections:
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.paragraph_format.line_spacing = 1.3

# Footer with page numbers
for section in doc.sections:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Seekra Strategic Roadmap · © 2026 Seekra Media Holdings · Page ")
    r.font.size = Pt(9)
    r.font.color.rgb = SEEKRA_GREY
    r.font.name = "Calibri"
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

# ====================== COVER ======================
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

# Spacer
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
r = p.add_run("Strategic Roadmap")
r.font.size = Pt(36)
r.font.bold = True
r.font.color.rgb = SEEKRA_DARK
r.font.name = "Calibri"

add_horizontal_rule(doc, color="D4AF37", size=18)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
p.paragraph_format.space_after = Pt(2)
r = p.add_run("Four options for the next major work after Brief #31 —")
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = SEEKRA_GREY
r.font.name = "Calibri"

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
r = p.add_run("production hardening, multi-tenant SaaS, AD/SSO, and data connectors.")
r.font.size = Pt(14)
r.font.italic = True
r.font.color.rgb = SEEKRA_GREY
r.font.name = "Calibri"

# Meta
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(120)
p.paragraph_format.space_after = Pt(0)

meta_table = doc.add_table(rows=4, cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
meta_rows = [
    ("Audience", "Seekra leadership + Kimi (implementer)"),
    ("Decision Required", "Pick one option to start, or run two in parallel"),
    ("Total Roadmap Window", "8–12 weeks across 2–4 options"),
    ("Date", "30 August 2026"),
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

# ====================== EXECUTIVE SUMMARY ======================
add_h1(doc, "Executive Summary")

add_p(doc,
    "After completing Briefs #1 through #31, Seekra has a demo-ready, production-grade content intelligence platform with cited AI chat, PII masking, four-level access control, agent mode, deep answer mode, and a curated 32-document demo repository. The next major work should be one (or two in parallel) of four strategic directions, each addressing a different business gap:",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_table(doc,
    ["Option", "Name", "Effort", "Demo Impact", "Unblocks"],
    [
        ("E", "Production Deployment Hardening", "3–4 wks", "Low (backstage)", "Enterprise procurement"),
        ("F", "Multi-Tenant SaaS Prep", "4–6 wks", "High (tenant spin-up)", "System integrators, holding cos"),
        ("G", "AD / SSO (OIDC + SCIM)", "2–3 wks", "Medium (login demo)", "~70% of enterprise deals"),
        ("H", "Data Connectors + Bulk Ingest", "3–4 wks", "High (drag folder → instant library)", "Any customer with existing corpus"),
    ],
    col_widths=[1.2, 5.8, 1.8, 3.7, 4.0])

add_h2(doc, "Recommendation")

add_callout(doc, "RECOMMENDED SEQUENCE",
    "1. Option H (Data Connectors) — 3–4 weeks. Highest-leverage for closing deals; the local-folder-watcher is a killer demo moment. Brief #32 drafted.\n"
    "2. Option G (AD/SSO) — 2–3 weeks. Table-stakes for enterprise deals; runs in parallel with H if capacity allows. Brief #33 drafted.\n"
    "3. Option E (Prod Hardening) — 3–4 weeks. Once you have real customers ingesting real content with real SSO logins, do the reliability work.\n"
    "4. Option F (Multi-Tenant SaaS) — 4–6 weeks. Defer until 3+ customers ask for white-label; premature optimization otherwise.")

add_p(doc,
    "Briefs #32 (Option H) and #33 (Option G) are drafted in the accompanying files Brief_32_Data_Connectors.md and Brief_33_AD_SSO.md. Hand them to Kimi in order.",
    italic=True, color=SEEKRA_GREY)

add_page_break(doc)

# ====================== OPTION E ======================
add_h1(doc, "Option E — Production Deployment Hardening")

add_p(doc,
    "Effort: 3–4 weeks · Demo impact: Low (backstage) · Strategic value: Foundational",
    italic=True, color=SEEKRA_GREY)

add_h2(doc, "What it sounds like")
add_p(doc, "Tighten the deployment for production-grade reliability.")

add_h2(doc, "What it actually means (full scope)")

add_h3(doc, "High availability")
add_bullet(doc, "Postgres streaming replication + automatic failover (Patroni or Stolon)")
add_bullet(doc, "Redis Sentinel for cache HA")
add_bullet(doc, "MinIO distributed mode (4+ nodes) for object storage HA")
add_bullet(doc, "Backend ≥2 replicas behind nginx upstream with health checks")

add_h3(doc, "Backups & disaster recovery")
add_bullet(doc, "Automated daily PITR (Point-In-Time Recovery) via pgBackRest")
add_bullet(doc, "MinIO bucket replication to a second region")
add_bullet(doc, "Tested restore runbook (currently scripts/backup.sh is manual)")

add_h3(doc, "Observability")
add_bullet(doc, "Structured JSON logging → shipped to Loki or Datadog")
add_bullet(doc, "Prometheus /metrics endpoint (latency, error rate, embedding queue depth)")
add_bullet(doc, "Grafana dashboards + alerting rules (PagerDuty or Slack)")

add_h3(doc, "Secrets management")
add_bullet(doc, "Move .env to HashiCorp Vault or AWS Secrets Manager")
add_bullet(doc, "Auto-rotate JWT secret + DB password on a schedule (quarterly)")

add_h3(doc, "TLS + container hardening")
add_bullet(doc, "OCSP stapling, TLS 1.3-only, certificate pinning for PWA")
add_bullet(doc, "Distroless backend image (currently python:3.12 base)")
add_bullet(doc, "Read-only root filesystem, non-root user, network policies")

add_h3(doc, "Rate limiting + cost guardrails")
add_bullet(doc, "nginx limit_req per IP + per user; AWS WAF or Cloudflare in front")
add_bullet(doc, "Ollama GPU autoscaling; embedding queue backpressure; MinIO lifecycle policies")

add_h2(doc, "Why this option")
add_p(doc,
    "Less demo-able but unblocks every enterprise procurement checklist. "
    "Buyer signal: 'We need 99.9% uptime SLA and a DR plan signed off by our infra team.'",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_h2(doc, "Why NOT first")
add_p(doc,
    "Hardening is best done once you have real production load and real customer-failure modes to learn from. Doing it before customer #1 ships is premature — you'll harden for hypothetical problems instead of real ones.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_page_break(doc)

# ====================== OPTION F ======================
add_h1(doc, "Option F — Multi-Tenant SaaS Prep")

add_p(doc,
    "Effort: 4–6 weeks · Demo impact: High (tenant spin-up) · Strategic value: Transforms business model",
    italic=True, color=SEEKRA_GREY)

add_h2(doc, "What it sounds like")
add_p(doc, "Convert Seekra from single-tenant to multi-tenant so you can serve multiple customers from one deployment.")

add_h2(doc, "What it actually means (full scope)")

add_h3(doc, "Tenant isolation model decision")
add_p(doc, "Three options, ordered by isolation strength and cost:")
add_bullet(doc, "Shared DB with tenant_id column — cheapest, weakest isolation, highest multi-tenancy density")
add_bullet(doc, "Schema-per-tenant — middle ground; clean separation, still manageable (RECOMMENDED for media-holding client mix)")
add_bullet(doc, "DB-per-tenant — strongest, most expensive, lowest density")

add_h3(doc, "Tenant context propagation")
add_bullet(doc, "Every API request resolves tenant from subdomain (acme.seekra.pk) or JWT claim")
add_bullet(doc, "Every SQL query auto-scoped to tenant")
add_bullet(doc, "Celery workers inherit tenant context (ContextVar)")

add_h3(doc, "Tenant onboarding flow")
add_bullet(doc, "Self-service signup → provision schema → seed root org node → create first admin → send invite")

add_h3(doc, "Per-tenant configuration")
add_bullet(doc, "Branding (logo, colors, custom domain)")
add_bullet(doc, "LLM provider keys (tenant brings their own OpenAI / Groq key)")
add_bullet(doc, "Retention policies, classification labels")

add_h3(doc, "Billing + cross-tenant admin")
add_bullet(doc, "Stripe or Chargebee; metering by document count, seat count, or API calls")
add_bullet(doc, "Super-admin console for Seekra staff: see all tenants, suspend, audit, run migrations")
add_bullet(doc, "Data residency: tenant-pinned region (UAE tenant → UAE datacenter, EU tenant → EU)")

add_h2(doc, "Why this option")
add_p(doc,
    "Big architectural lift — every existing query, every cache key, every audit event needs a tenant_id. Demo-able as 'watch me spin up a new tenant in 60 seconds.' Transforms the business model from on-prem licenses to SaaS subscriptions.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_h2(doc, "Why NOT first")
add_p(doc,
    "It's the biggest architectural lift and only makes sense once you have 3+ customers asking for it. Doing it earlier is premature optimization — you don't yet know what tenant-level config variations you'll need. Wait until customer #3 says 'we want to white-label Seekra for our portfolio companies' and then build exactly what they need.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_p(doc,
    "Buyer signal: 'We want to offer Seekra as a service to our 12 portfolio companies' or 'We're a system integrator and want to resell.'",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_page_break(doc)

# ====================== OPTION G ======================
add_h1(doc, "Option G — Active Directory / SSO Authentication")

add_p(doc,
    "Effort: 2–3 weeks · Demo impact: Medium (login demo) · Strategic value: Table-stakes for enterprise",
    italic=True, color=SEEKRA_GREY)

add_h2(doc, "What it sounds like")
add_p(doc, "Let users log in with their corporate AD credentials instead of Seekra-managed passwords.")

add_h2(doc, "What it actually means (full scope)")

add_h3(doc, "Protocol choice")
add_p(doc,
    "SAML 2.0 (Microsoft AD FS, Okta, Azure AD) vs. OIDC (modern Azure AD, Google Workspace, Keycloak). "
    "Implement OIDC FIRST — it's the modern standard, simpler, and Azure AD supports it natively. SAML can be a follow-up brief for AD FS on-prem customers.")

add_h3(doc, "Just-in-time provisioning")
add_bullet(doc, "First SSO login auto-creates the Seekra user row")
add_bullet(doc, "Mapped to a default department + clearance (configurable per IdP)")
add_bullet(doc, "Hash a random unusable password (so local login is impossible for SSO users)")

add_h3(doc, "Group / role mapping")
add_bullet(doc, "IdP groups → Seekra roles + department memberships (e.g. 'Seekra-Films-Editors' → editor role + Films department)")
add_bullet(doc, "This is the killer feature — zero admin overhead when joining/leaving")
add_bullet(doc, "Highest-privilege wins: if user is in 'Seekra-Admins' and 'Seekra-Viewers', they get admin")

add_h3(doc, "SCIM provisioning (phase 4)")
add_bullet(doc, "Automatic user create/update/delete from Azure AD")
add_bullet(doc, "HR-driven offboard in Workday → AD → SCIM → Seekra deactivates within minutes — no manual step")
add_bullet(doc, "SCIM 2.0 endpoint at /api/scim/v2 (Users CRUD)")

add_h3(doc, "Session bridging + multi-IdP")
add_bullet(doc, "SSO session ↔ Seekra JWT; logout propagation (single logout)")
add_bullet(doc, "Support multiple SSO configs per tenant (one for employees, one for contractors)")
add_bullet(doc, "Fallback local login for break-glass admin accounts (default 1 per tenant)")

add_h2(doc, "Why this option")
add_p(doc,
    "This is a hard requirement for ~70% of enterprise deals in the Gulf. Without it, IT security review fails. "
    "When SSO is wired up, the group-to-role mapping means new hires auto-provision, offboards auto-deactivate — 10x reduction in operational overhead vs. manual user management.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_p(doc,
    "Buyer signal: 'We can't deploy anything that doesn't integrate with our Azure AD' — this is the #1 enterprise procurement gate in the region.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_callout(doc, "BRIEF DRAFTED",
    "Brief #33 (AD/SSO) is fully drafted in Brief_33_AD_SSO.md — 6 phases, OIDC + group mapping + SCIM + multi-IdP + single logout. Hand to Kimi after Brief #32 lands.")

add_page_break(doc)

# ====================== OPTION H ======================
add_h1(doc, "Option H — External Data Connectors + Bulk Folder Ingestion")

add_p(doc,
    "Effort: 3–4 weeks · Demo impact: High (drag folder → instant library) · Strategic value: Critical for onboarding velocity",
    italic=True, color=SEEKRA_GREY)

add_h2(doc, "What it sounds like")
add_p(doc, "Pull files from SharePoint / Google Drive / Dropbox / network shares into Seekra automatically.")

add_h2(doc, "What it actually means (full scope)")

add_h3(doc, "Connector framework (pluggable adapters)")
add_p(doc, "Each connector implements: list_changes(since) → stream_bytes(file) → infer_scope(file). Initial set:")
add_bullet(doc, "Local/network folder watcher — inotify or polling on /ingest/ mount point (HIGHEST VALUE — easiest demo win)")
add_bullet(doc, "SharePoint / OneDrive (Microsoft Graph API)")
add_bullet(doc, "Google Drive (Drive API v3 with service account)")
add_bullet(doc, "S3 / Azure Blob (already have MinIO client, easy)")
add_bullet(doc, "SMTP / email attachment ingest — forward ingest@{tenant}.seekra.pk → auto-upload")

add_h3(doc, "Scheduled sync + incremental")
add_bullet(doc, "Cron-style polling per connector (default every 15 min, configurable)")
add_bullet(doc, "Track last_synced_at per connector; only fetch new/modified files; detect deletions")
add_bullet(doc, "Backpressure: pause sync if indexing queue > 1000 items")

add_h3(doc, "Scope + classification inference")
add_bullet(doc, "When a connector pulls a file, infer scope from the source folder path ('/Films/Production/' → Films · Production team)")
add_bullet(doc, "Classification from filename keywords or per-connector default")
add_bullet(doc, "Per-connector path rules table: glob pattern → (scope_org_id, classification)")

add_h3(doc, "Conflict resolution")
add_bullet(doc, "Source file modified externally + Seekra doc unchanged → version it (Brief #39)")
add_bullet(doc, "Source modified + Seekra doc also modified → conflict logged, Seekra version preserved (no overwrite)")
add_bullet(doc, "Admin conflict resolution UI: keep Seekra / overwrite / merge (phase 7+)")

add_h3(doc, "Bulk upload UX")
add_bullet(doc, "Drag-drop multiple files at once (currently upload is one-file-per-request)")
add_bullet(doc, "Per-file progress bars; per-file scope + classification override; retry on failure")
add_bullet(doc, "Folder structure preservation option (recreate source tree inside Seekra)")
add_bullet(doc, "Rate limiting + resume for large folders (10k+ files)")

add_h2(doc, "Why this option")
add_p(doc,
    "This is the #1 onboarding blocker. A customer who sees the demo, loves it, then asks 'ok but how do I get my 50,000 SharePoint docs in?' — without connectors, the answer is 'manually, one at a time' and the deal stalls. With connectors, the answer is 'point us at your SharePoint, we'll have it indexed by morning' and the deal closes.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_p(doc,
    "The local folder watcher is the easiest demo win: drop a folder of files on a mounted volume during the demo and watch them appear in Seekra within seconds. Genuinely magical.",
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_callout(doc, "BRIEF DRAFTED",
    "Brief #32 (Data Connectors) is fully drafted in Brief_32_Data_Connectors.md — 6 phases covering connector framework, local folder watcher, SharePoint, Google Drive, SMTP ingest, and conflict resolution. Hand to Kimi first.")

add_page_break(doc)

# ====================== COMPARISON + SEQUENCE ======================
add_h1(doc, "Comparison + Recommended Sequence")

add_h2(doc, "Side-by-side comparison")
add_table(doc,
    ["Dimension", "E — Hardening", "F — Multi-Tenant", "G — AD/SSO", "H — Connectors"],
    [
        ("Effort", "3–4 wks", "4–6 wks", "2–3 wks", "3–4 wks"),
        ("Demo impact", "Low", "High", "Medium", "High"),
        ("Deal unblock", "Procurement", "Integrators", "~70% of deals", "Any w/ corpus"),
        ("Architectural lift", "Low", "High", "Medium", "Medium"),
        ("Demo moment", "—", "Spin up tenant", "Login via Azure AD", "Drop folder → instant library"),
        ("Strategic value", "Foundational", "Business model", "Table-stakes", "Onboarding velocity"),
    ],
    col_widths=[3.5, 3.0, 3.0, 3.0, 3.0])

add_h2(doc, "Recommended sequence (single stream)")

add_callout(doc, "PHASE 1 (Weeks 1–4)",
    "Option H — Data Connectors + Bulk Ingestion. Brief #32 drafted. Highest-leverage for closing deals. Local-folder-watcher is a killer demo moment.")

add_callout(doc, "PHASE 2 (Weeks 5–7)",
    "Option G — AD / SSO. Brief #33 drafted. Table-stakes for enterprise. Once customers can ingest content, SSO is the next procurement gate.")

add_callout(doc, "PHASE 3 (Weeks 8–11)",
    "Option E — Production Hardening. Once you have real customers with real load, do the reliability work. Less demo-able but unblocks the SLA conversation.")

add_callout(doc, "PHASE 4 (Weeks 12–17)",
    "Option F — Multi-Tenant SaaS. Defer until 3+ customers ask for white-label. The biggest architectural lift — only worth doing once you know exactly what tenant-level config variations you need.")

add_h2(doc, "Alternative: parallel streams (faster)")

add_p(doc,
    "If you have capacity to run two streams (Kimi on one, you on the other), H and G can ship in parallel in ~3 weeks instead of 5–6 sequential:")

add_table(doc,
    ["Stream", "Owner", "Brief", "Duration", "Dependencies"],
    [
        ("Stream 1", "Kimi", "Brief #32 — Data Connectors", "3–4 wks", "Brief #17 (org tree) ✓"),
        ("Stream 2", "You", "Brief #33 — AD/SSO", "2–3 wks", "Brief #17 (users) ✓"),
    ],
    col_widths=[2.5, 2.5, 5.5, 2.5, 3.0])

add_p(doc,
    "These two have zero overlap — H is backend + filesystem + connector framework; G is auth + identity + frontend login. Running them in parallel cuts total time from 6 weeks to ~3 weeks.")

add_page_break(doc)

# ====================== APPENDIX: BRIEF INVENTORY ======================
add_h1(doc, "Appendix — Briefs #32 and #33 Inventory")

add_p(doc,
    "Two fully-drafted briefs accompany this roadmap document. Hand them to Kimi in order:",
    italic=True, color=SEEKRA_GREY)

add_table(doc,
    ["Brief", "Title", "Phases", "Effort", "File"],
    [
        ("#32", "External Data Connectors + Bulk Folder Ingestion", "6", "3–4 wks", "Brief_32_Data_Connectors.md"),
        ("#33", "Active Directory / SSO Authentication (OIDC + SCIM)", "6", "2–3 wks", "Brief_33_AD_SSO.md"),
    ],
    col_widths=[1.5, 6.5, 1.5, 1.8, 4.7])

add_h2(doc, "Brief #32 — Phase summary (Data Connectors)")
add_bullet(doc, "Phase 1: Connector framework + local folder watcher (Week 1)")
add_bullet(doc, "Phase 2: Multi-file bulk upload UI (Week 1, parallel)")
add_bullet(doc, "Phase 3: SharePoint / OneDrive connector (Week 2–3)")
add_bullet(doc, "Phase 4: Google Drive connector (Week 3)")
add_bullet(doc, "Phase 5: SMTP email attachment ingest (Week 3–4)")
add_bullet(doc, "Phase 6: Conflict resolution + versioning integration (Week 4)")

add_h2(doc, "Brief #33 — Phase summary (AD/SSO)")
add_bullet(doc, "Phase 1: OIDC provider config + login flow (Week 1)")
add_bullet(doc, "Phase 2: Group-to-role mapping (Week 2)")
add_bullet(doc, "Phase 3: Frontend polish + error handling (Week 2)")
add_bullet(doc, "Phase 4: SCIM 2.0 endpoint (Week 3)")
add_bullet(doc, "Phase 5: Multi-IdP support (Week 3)")
add_bullet(doc, "Phase 6: Single Logout + session bridging (Week 3, stretch)")

add_h2(doc, "Key technical decisions in the briefs")

add_h3(doc, "Brief #32 — Data Connectors")
add_bullet(doc, "Pluggable Connector ABC in backend/app/services/connectors/base.py")
add_bullet(doc, "3 new tables: data_connectors, connector_files (incremental sync tracking), connector_path_rules (scope inference)")
add_bullet(doc, "Connector credentials AES-256 encrypted at rest with per-tenant key")
add_bullet(doc, "Conflict resolution integrates with Brief #39's existing versioning")
add_bullet(doc, "Backpressure: pause sync if indexing queue > 1000 items")

add_h3(doc, "Brief #33 — AD/SSO")
add_bullet(doc, "OIDC first (SAML deferred to follow-up brief)")
add_bullet(doc, "Just-in-time provisioning with per-IdP defaults (role, clearance, scope)")
add_bullet(doc, "Group-to-role mapping: highest-privilege wins; SSO-managed memberships tracked with is_sso_managed flag")
add_bullet(doc, "SCIM 2.0 endpoint at /api/scim/v2 (Users CRUD)")
add_bullet(doc, "Break-glass admin enforcement: must always have ≥1 local-password admin")
add_bullet(doc, "PKCE + state nonce in Redis (10-min TTL) for CSRF defense")

# Save
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
print(f"Roadmap DOCX saved: {OUT}")
print(f"Size: {OUT.stat().st_size / 1024:.1f} KB")
