"""Update slides_brief.json to add formal cover + TOC at the start,
and renumber output_paths for all existing slides (shift by +2)."""
import json
from pathlib import Path

BRIEF_PATH = Path("/home/z/my-project/download/slides/slides_brief.json")
SLIDES_DIR = Path("/home/z/my-project/download/slides")

data = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))

# Step 1: Renumber existing slides' output_paths (shift by +2)
# Original slide_NN.html becomes slide_(NN+2).html
for slide in data["slides"]:
    old_path = slide["output_path"]
    # Extract slide_NN.html from the path
    filename = Path(old_path).name
    if filename.startswith("slide_") and filename.endswith(".html"):
        num_str = filename[6:8]  # extract "NN" from "slide_NN.html"
        try:
            old_num = int(num_str)
            new_num = old_num + 2
            new_filename = f"slide_{new_num:02d}.html"
            new_path = str(Path(old_path).parent / new_filename)
            slide["output_path"] = new_path
        except ValueError:
            print(f"WARN: Could not parse number from {filename}")

# Step 2: Insert the new cover slide at the start
cover_slide = {
    "title": "Formal Handbook Cover",
    "layout": "formal-cover",
    "output_path": "/home/z/my-project/download/slides/slide_01.html",
    "task_brief": (
        "FORMAL HANDBOOK COVER (Slide 1 of 16) — slide-dark background (charcoal #202020) with a subtle radial tan glow centered behind the logo. "
        "This is the FIRST slide of the deck — a formal corporate-handbook cover, NOT a marketing hero. "
        "Centered vertical layout, generous whitespace.\n\n"
        "ELEMENTS (top-to-bottom, all centered horizontally):\n"
        "1. SEEKRA LOGO: use local image at relative path 'logo-seekra.png' at 96x96px with 14px corner radius, centered.\n"
        "2. WORDMARK: 'Seekra' in Inter 700, 80px, color cream #E7E6E4, letter-spacing -0.025em, top margin 32px.\n"
        "3. DIVIDER: a horizontal tan line, 64px wide, 2px tall, background #B59876, top margin 32px, centered.\n"
        "4. SUBTITLE: 'App Profile' in Inter 500, 28px, color tan #B59876, letter-spacing 0.22em, text-transform uppercase, top margin 32px.\n"
        "5. VERSION + YEAR: 'Version 1.0  ·  2026' in Inter 400, 16px, color cream at 60% opacity, top margin 16px. The '·' separator in tan.\n"
        "\n"
        "BOTTOM BAR (absolute positioned, 48px from bottom, full width with 64px horizontal padding):\n"
        "  • LEFT: 'Prepared for: Gulf Region Enterprise & Government Buyers' in Inter 500, 12px, color cream at 50% opacity, letter-spacing 0.10em, uppercase.\n"
        "  • RIGHT: '© 2026 Seekra  ·  seekra.pk' in Inter 500, 12px, color cream at 50% opacity, letter-spacing 0.10em, uppercase.\n"
        "\n"
        "NO CTA buttons, NO chips, NO subline paragraph. The cover is intentionally minimal — just brand + document type + version. "
        "Background must be solid charcoal. Use the existing local logo file at relative path 'logo-seekra.png'.\n\n"
        "Speaker notes: short hints — 3 bullet talking points for opening the meeting: (1) introduce this as the formal App Profile handbook, (2) mention the version (1.0) and that it's prepared for Gulf enterprise and government buyers, (3) transition to the table of contents."
    )
}

# Step 3: Insert the TOC slide at position 2
toc_entries = [
    ("01", "Executive Summary", 4),
    ("02", "Why Seekra Exists", 5),
    ("03", "The Seekra Approach", 6),
    ("04", "Capability 01 — Ask", 7),
    ("05", "Capability 02 — See", 8),
    ("06", "Capability 03 — Speak", 9),
    ("07", "Trust & Sovereignty", 10),
    ("08", "Capability Comparison", 11),
    ("09", "Deployment Options", 12),
    ("10", "Use Cases — Gulf Regulated Sectors", 13),
    ("11", "Why Seekra — Differentiators", 14),
    ("12", "Get in Touch", 15),
    ("13", "Appendix — Deployment Architecture", 16),
]

# Build TOC task_brief
toc_entries_text = "\n".join(
    f"  • Row {i+1}: number='{num}', title='{title}', page={page}"
    for i, (num, title, page) in enumerate(toc_entries)
)

toc_slide = {
    "title": "Table of Contents",
    "layout": "toc",
    "output_path": "/home/z/my-project/download/slides/slide_02.html",
    "task_brief": (
        "TABLE OF CONTENTS (Slide 2 of 16) — slide-light background (cream #E7E6E4), text color ink-strong (#1F1A14). "
        "This is a formal handbook Table of Contents page.\n\n"
        "LAYOUT: Single column, max-width 1100px, centered horizontally with generous left/right padding.\n\n"
        "TOP BLOCK:\n"
        "  • EYEBROW (13px Inter 800, letter-spacing 0.22em, uppercase, color brick red #B93C32): 'CONTENTS'\n"
        "  • HEADLINE (Inter 700, 56px, line-height 1.1, letter-spacing -0.025em, color #1F1A14, top margin 12px): 'Everything in this profile, in order.'\n"
        "    Render the period in brick red (#B93C32).\n"
        "  • LEAD PARAGRAPH (Inter 400, 15px, line-height 1.55, color #4A3F33, top margin 12px, max-width 720px): 'Thirteen sections, top to bottom. Read in order for the full picture, or jump to a section if you are looking for something specific.'\n\n"
        "TOC LIST (top margin 36px, 13 entries in a single column):\n"
        "Each row is a horizontal flex with:\n"
        "  • NUMERAL: '01' through '13' (Inter 600, 22px, color tan #B59876, font-feature-settings 'tnum', width 56px, fixed)\n"
        "  • TITLE: section title (Inter 500, 18px, color #1F1A14, flex-grow)\n"
        "  • DOTTED LEADER: a 1px dotted line in tan #B59876/40%, flex-grow, margin-horizontal 16px\n"
        "  • PAGE NUMBER: page number (Inter 500, 18px, color #1F1A14, font-feature-settings 'tnum')\n"
        "Row height: 44px, vertical-aligned middle. Bottom border 1px hair-light between rows.\n"
        "Hover state not needed (static slide).\n\n"
        "ENTRIES (render verbatim):\n" + toc_entries_text + "\n\n"
        "FOOTER (bottom of slide, 32px from bottom, centered, 11px Inter 400 italic, color #4A3F33): 'Seekra · App Profile v1.0 · 2026'\n\n"
        "NO photos. Solid cream background. The list should feel like a real book table of contents — clean, scannable, with proper dotted leader lines between titles and page numbers.\n\n"
        "Speaker notes: short hints — 3 bullet talking points: (1) introduce the structure of the deck (13 sections, ~16 slides total), (2) mention the four narrative chunks: problem → approach → capabilities → trust/deployment, (3) invite the client to jump to a section if they want to focus on a specific topic."
    )
}

# Insert at the beginning of slides list
data["slides"].insert(0, cover_slide)
data["slides"].insert(1, toc_slide)

# Update design block to note the handbook structure
if "design" in data and isinstance(data["design"], dict):
    data["design"]["format"] = "Professional handbook (formal cover + TOC + 13 content sections + closing)"
    data["design"]["total_slides"] = 16

BRIEF_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"OK  slides_brief.json updated — now {len(data['slides'])} slides")
print()
print("New slide order:")
for i, s in enumerate(data["slides"], 1):
    filename = Path(s["output_path"]).name
    print(f"  {i:02d}. {filename:<20}  {s['title']}")
