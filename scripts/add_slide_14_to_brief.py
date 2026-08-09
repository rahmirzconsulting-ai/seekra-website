"""Add slide 14 entry to slides_brief.json."""
import json
from pathlib import Path

brief_path = Path("/home/z/my-project/download/slides/slides_brief.json")
data = json.loads(brief_path.read_text(encoding="utf-8"))

slide_14 = {
    "title": "Appendix — Deployment Architecture",
    "layout": "appendix-full-diagram",
    "output_path": "/home/z/my-project/download/slides/slide_14.html",
    "task_brief": (
        "DARK SLIDE — slide-dark background (charcoal #202020) with one soft radial tan glow positioned top-right. "
        "This is an APPENDIX reference slide placed at the END of the deck — used when the client asks for architectural detail beyond the 3-card overview on slide 10.\n\n"
        "LAYOUT: minimal slide chrome — the embedded architecture diagram fills most of the canvas.\n"
        "  • Top row: small eyebrow (12px Inter 700, letter-spacing 0.22em, uppercase, color tan #B59876) on the left: 'APPENDIX · DEPLOYMENT ARCHITECTURE'; small page tag on the right (11px Inter 600, letter-spacing 0.18em, uppercase, cream at 55% opacity): 'REFERENCE'\n"
        "  • Caption below eyebrow (13px Inter 400, cream at 75% opacity, line-height 1.5, max-width 1100px): 'Three deployment tiers visualised side-by-side. The same Seekra application, PII masking layer, and document store run in all three tiers — only the AI model location and network exposure change.'\n"
        "  • Diagram: the architecture PNG embedded at 1200px wide, centered horizontally. The PNG itself contains its own title, 3 panels (Cloud Native / Self-Hosted / Air-Gapped), component cards inside dashed customer-boundary boxes, network state bars, and a footer legend.\n"
        "  • Bottom footer note (11px Inter italic, cream at 45% opacity, centered, letter-spacing 0.06em): 'Detailed architecture reference · See full-resolution diagram for additional detail'\n\n"
        "The embedded diagram is at relative path 'seekra_deployment_architecture.png' — a 4800x2338px PNG generated from a Playwright+CSS render of an HTML diagram (see /home/z/my-project/scripts/deployment_diagram.py for the source).\n\n"
        "Speaker notes: short hints — 5 bullet talking points: (1) use this slide when the client asks for architectural detail beyond the 3-card overview, (2) walk left-to-right: Cloud Native → Self-Hosted → Air-Gapped, (3) point out the dashed customer boundary — note how AI box moves from outside (tier 1) to inside (tiers 2 & 3), (4) the network bar at bottom of each tier is the key differentiator: amber connected → green updates-only → brick-red fully isolated, (5) offer to walk through a single tier in depth on a follow-up call."
    )
}

# Append slide 14 to the slides list
data["slides"].append(slide_14)

# Update the design block to note the 3-tier model
if "design" in data and isinstance(data["design"], dict):
    data["design"]["deployment_model"] = "3-tier: Cloud Native (external AI with PII masking) / Self-Hosted (local AI) / Air-Gapped (local AI, fully isolated)"

brief_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK  slides_brief.json updated — now {len(data['slides'])} slides")
for i, s in enumerate(data["slides"], 1):
    print(f"  {i:02d}. {s['title']}")
