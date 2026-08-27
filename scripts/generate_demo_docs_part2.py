#!/usr/bin/env python3
"""Generate demo docs 12-22 (Films + Creative subsidiaries).

Imports the helper functions from part 1.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, "/home/z/my-project/scripts")
# Import helpers from part 1
from demo_doc_helpers import (
    write_pdf, write_docx, write_xlsx, write_pptx, write_jpg, write_png,
    write_mp3, write_mp4, write_text, write_csv,
    OUT, SEEKRA_PRIMARY, SEEKRA_ACCENT, SEEKRA_GOLD, SEEKRA_DARK,
)

PASS = FAIL = 0
def log(ok, msg):
    global PASS, FAIL
    print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
    if ok: PASS += 1
    else: FAIL += 1


print("=" * 60)
print("GENERATING DEMO DOCUMENTS — PART 2 (Films + Creative)")
print("=" * 60)

# ----------------------------------------------------------------------
# Films · Creative Direction (3 docs)
# ----------------------------------------------------------------------
print("\n=== Films · Creative Direction (3 docs) ===")

# 12: Golden Falcon Script v3 (PDF, Confidential)
write_pdf(
    "12_Golden_Falcon_Script_v3.pdf",
    "PROJECT GOLDEN FALCON — Original Screenplay (v3)",
    [
        "## Written by",
        "Yousef Al Saedi · Story by Sara Al Kindy & Yousef Al Saedi",
        "## FADE IN:",
        "EXT. DUBAI DESERT — DAWN",
        "A pale gold light spills across the dunes. A lone BEDOUIN RIDER crests a ridge on a grey Arabian mare. His kaffiyeh is streaked with sand. In his right hand he carries a brass telescope wrapped in oxblood leather.",
        "The rider halts. He unwraps the telescope — it is ornately engraved with the image of a falcon catching a gazelle. He raises it to his eye.",
        "POV — THROUGH TELESCOPE",
        "Far across the desert floor, a CAMP. Soldiers in modern tactical gear. Three black SUVs. And there, kneeling in chains beside a water truck — a YOUNG WOMAN in a white thobe. Her hair is dark. She is looking directly at us, as if she can see through the telescope.",
        "The rider lowers the telescope. He is shaken.",
        "RIDER (V.O.)",
        "(in Arabic, subtitled)",
        "They have her. The falcon's daughter.",
        "CUT TO:",
        "EXT. AL FAHIDI HISTORIC DISTRICT — DAY",
        "TARIK (38, lean, weathered) emerges from a wind tower house into the narrow sikkah. He carries an old leather satchel. The door behind him is hand-carved with a single symbol: a falcon in flight.",
        "A BLACK MERCEDES glides to a stop at the end of the alley. Two men in dark suits step out.",
        "TARIK",
        "(to himself)",
        "Yousef. Always early.",
        "YOUSEF (45, gold-rimmed glasses, immaculate kandura) emerges from the Mercedes. He is smiling, but the smile does not reach his eyes.",
        "YOUSEF",
        "Tarik. My brother. I told you — three more days. Why do you make me come here?",
        "TARIK",
        "Three more days, three more weeks. The answer is the same.",
        "YOUSEF",
        "The Patron is not a patient man.",
        "TARIK",
        "Then the Patron should not have sent his soldiers to take her.",
        "Yousef stops. The smile vanishes.",
        "YOUSEF",
        "(low, dangerous)",
        "Be careful, Tarik. The old ways do not protect you anymore.",
        "Tarik opens the satchel. Inside, nested in red velvet, is the brass telescope.",
        "TARIK",
        "The old ways are why she is still alive.",
        "## SCENE 12 — INT. ABANDONED CARAVANSERAI — NIGHT",
        "This is the scene for which additional VFX work has been approved by the Board (Q3 meeting minutes, 15 September 2026). The caravanserai interior is lit by 400 candles and a single shaft of moonlight through the oculus.",
        "Tarik unwraps the telescope. He places it on a stone altar. The falcon engraving begins to glow — a soft, golden light, pulsing in time with a heartbeat we hear but cannot source.",
        "TARIK",
        "(whispering)",
        "Show me where she is.",
        "The telescope lifts from the altar — slowly, impossibly — and rotates in mid-air. It points south. Through its lens, we see the camp from the opening scene. The Young Woman lifts her head.",
        "## FADE OUT.",
        "## END OF EXCERPT — Full screenplay 142 pages. Revision 3 locked 5 September 2026.",
    ],
    subtitle="Confidential — Seekra Films Creative Direction · Draft 3 · 5 September 2026",
    metadata={
        "Genre": "Thriller / Arabic Heritage",
        "Runtime Target": "128 minutes",
        "Budget": "AED 48.2M (with AED 2.0M contingency for VFX)",
        "Director": "Yousef Al Saedi",
        "Producer": "Sara Al Kindy, Seekra Films",
        "Theatrical Release": "18 December 2026",
    },
)
log(True, "12_Golden_Falcon_Script_v3.pdf")

# 13: Creative Treatment Pitch Deck (PPTX, Confidential)
write_pptx(
    "13_Golden_Falcon_Creative_Treatment.pptx",
    "Project Golden Falcon — Creative Treatment",
    [
        {"title": "Logline", "body": [
            "When his estranged brother abducts the last heir of a forbidden Bedouin bloodline,",
            "a former antiquities detective must wield a 400-year-old brass telescope —",
            "the only artifact that can reveal the truth across the desert — to bring her home.",
            "",
            "Genre: Arabic Heritage Thriller",
            "Tone: Sicario meets Lawrence of Arabia",
            "Runtime: 128 minutes",
        ]},
        {"title": "Themes", "body": [
            "• Heritage vs. modernity — the telescope as a bridge between worlds",
            "• Family loyalty tested by ambition",
            "• The price of memory — what we owe to those who came before",
            "• The falcon as metaphor: vision, freedom, sacrifice",
        ]},
        {"title": "Tone & Visual Language", "body": [
            "• Palette: desert gold, oxblood, deep teal, charcoal",
            "• Aspect ratio: 2.39:1 anamorphic",
            "• Lighting: naturalistic; candlelight for ritual scenes",
            "• Camera: long lenses for the desert vistas; handheld intimacy for interiors",
            "• Sound design: sparse score, layered with traditional oud and contemporary synth",
        ]},
        {"title": "Comparable Titles", "body": [
            "• Theeb (2014) — Jordanian Oscar nominee",
            "• Sicario (2015) — modern thriller pacing",
            "• The Kite Runner (2007) — heritage + personal journey",
            "• A Hologram for the King (2016) — Saudi setting",
        ]},
        {"title": "Target Audience", "body": [
            "• Primary: Arabic-speaking adults 25-54 across GCC, MENA",
            "• Secondary: International art-house audiences via festival circuit",
            "• Streaming: Netflix MENA, StarzPlay, Shahid Originals",
            "• Theatrical: GCC-wide day-and-date release 18 Dec 2026",
        ]},
        {"title": "Cast Vision", "body": [
            "• Tarik (lead): Egyptian-Gulf actor, 35-45, name talent required",
            "• Yousef (antagonist): Emirati, 40-50, gravitas",
            "• The Young Woman: GCC or North African, 20-28, bilingual",
            "• Supporting: 8-10 named roles; 200+ background",
        ]},
        {"title": "Locations", "body": [
            "• Principal: Jebel Jais, Ras Al Khaimah (desert sequences)",
            "• Al Fahidi Historic District, Dubai (Tarik's home)",
            "• Mira Studios soundstage (caravanserai interior — Scene 12)",
            "• Liwa Desert (final act — 4 days)",
        ]},
        {"title": "Budget Summary", "body": [
            "• Above-the-line: AED 14.2M (cast, director, writer, producer fees)",
            "• Below-the-line: AED 26.8M (crew, equipment, locations, post)",
            "• VFX: AED 5.2M (Scene 12 telescope effect + 14 augmentation shots)",
            "• Contingency: AED 2.0M (approved Q3 board)",
            "• Total: AED 48.2M",
        ]},
        {"title": "Revenue Projections", "body": [
            "• Theatrical GCC: AED 32-45M",
            "• Netflix MENA pre-sale: AED 18M (closed)",
            "• StarzPlay: AED 6M (closed)",
            "• International sales: AED 8-15M (in negotiation)",
            "• Total projected revenue: AED 64-84M",
        ]},
    ],
)
log(True, "13_Golden_Falcon_Creative_Treatment.pptx")

# 14: Director Vision Notes (TXT, Confidential)
write_text(
    "14_Director_Vision_Notes.txt",
    """PROJECT GOLDEN FALCON — DIRECTOR'S VISION NOTES
Yousef Al Saedi · 28 August 2026

These notes are private to the creative team. Do not distribute.

THE FILM I WANT TO MAKE
========================
I want to make a film about the weight of inheritance — not money, but the
stories, the artifacts, the debts of memory that pass from one generation
to the next. Tarik has spent his life trying to escape his family's
legacy. The telescope is the thing he could never escape. It chose him.

THE TELESCOPE
=============
The brass telescope is the second protagonist of this film. It must feel
heavy, real, ancient. The VFX team has been briefed: when it lifts from
the altar in Scene 12, the audience must believe it. No flash, no CGI
sheen. Just gravity releasing, slowly, like a held breath.

I have asked Reem at Seekra Studios to build a physical rig — a magnet
system on the altar that can hold the telescope, then release it on cue.
We will augment with VFX only to remove the rig. This is the right way.

THE DESERT
==========
The desert is not a backdrop. It is a character. It decides who lives.
We are shooting Jebel Jais at dawn — never midday. The light in our film
is always the light of revelation, never the light of exposure.

TARIK AND YOUSEF
================
Tarik and Yousef are brothers. They grew up in the same house, with the
same father, the same telescope on the same shelf. One became a thief.
The other became a librarian. The film asks: what made the difference?

I do not want to answer that question for the audience.

THE YOUNG WOMAN
================
She does not speak until Scene 14. Until then, she is only eyes. When she
finally speaks, it is in Arabic, and she says: "You came for the
telescope. Not for me."

That is the moment the film turns.

SCENE 12 — REVISED APPROACH
============================
After the board approved the additional VFX budget, I have reconsidered
the caravanserai sequence. The original plan was a single 4-minute
tracking shot. After testing, this is too risky for the candle
choreography.

New approach: three shots, ~90 seconds each, stitched visually through
the telescope's rotation. This gives Reem's team more flexibility on
the VFX integration and gives the actors a more achievable performance
target.

I have discussed this with Sara and with Layla (production). Layla will
update the call sheet for 12-15 October (Jebel Jais block) to reflect
the new shot list.

CLOSING
=======
I have been writing this film for six years. I am ready.

— Yousef
""",
)
log(True, "14_Director_Vision_Notes.txt")

# ----------------------------------------------------------------------
# Films · Production (4 docs)
# ----------------------------------------------------------------------
print("\n=== Films · Production (4 docs) ===")

# 15: Budget Breakdown (XLSX, Restricted)
write_xlsx(
    "15_Golden_Falcon_Budget_Breakdown.xlsx",
    [{
        "name": "Budget Summary",
        "headers": ["Category", "Sub-Category", "Vendor", "Budgeted (AED)",
                    "Committed (AED)", "Actual to Date (AED)", "Variance"],
        "rows": [
            ["Above-the-Line", "Director Fee", "Yousef Al Saedi", "2,500,000", "2,500,000", "1,875,000", "625,000"],
            ["Above-the-Line", "Lead Cast", "Talent Agency GCC", "8,200,000", "8,200,000", "6,150,000", "2,050,000"],
            ["Above-the-Line", "Producer Fees", "Sara Al Kindy", "1,800,000", "1,800,000", "1,350,000", "450,000"],
            ["Above-the-Line", "Screenplay Rights", "Internal", "850,000", "850,000", "850,000", "0"],
            ["Above-the-Line", "Subtotal", "", "13,350,000", "13,350,000", "10,225,000", "3,125,000"],
            ["Below-the-Line", "Crew (above)", "Various", "4,800,000", "4,800,000", "3,600,000", "1,200,000"],
            ["Below-the-Line", "Equipment Rental", "Mira Studios", "3,250,000", "3,250,000", "2,710,000", "540,000"],
            ["Below-the-Line", "Location Fees", "RAK Film Commission", "1,450,000", "1,450,000", "1,087,500", "362,500"],
            ["Below-the-Line", "Set Construction", "Studio Art Dept", "2,100,000", "2,100,000", "1,890,000", "210,000"],
            ["Below-the-Line", "Costumes & Wardrobe", "House of Taneeq", "680,000", "680,000", "595,000", "85,000"],
            ["Below-the-Line", "Catering & Craft", "Desert Kitchen LLC", "420,000", "420,000", "378,000", "42,000"],
            ["Below-the-Line", "Transport & Vehicles", "Speedy Motors UAE", "510,000", "510,000", "459,000", "51,000"],
            ["Below-the-Line", "Insurance & Bond", "AIG MENA", "850,000", "850,000", "850,000", "0"],
            ["Below-the-Line", "Subtotal", "", "14,060,000", "14,060,000", "11,569,500", "2,490,500"],
            ["Post-Production", "Editorial", "Seekra Studios", "1,800,000", "1,800,000", "540,000", "1,260,000"],
            ["Post-Production", "Sound Design", "Seekra Studios", "950,000", "950,000", "0", "950,000"],
            ["Post-Production", "Color Grading", "Seekra Studios", "680,000", "680,000", "0", "680,000"],
            ["Post-Production", "Music & Score", "Composer (TBC)", "1,200,000", "0", "0", "1,200,000"],
            ["Post-Production", "VFX", "Seekra Studios VFX", "5,200,000", "5,200,000", "1,560,000", "3,640,000"],
            ["Post-Production", "Subtotal", "", "9,830,000", "8,630,000", "2,100,000", "7,730,000"],
            ["Contingency", "Board-approved (Q3)", "Reserved", "2,000,000", "0", "0", "2,000,000"],
            ["GRAND TOTAL", "", "", "39,240,000", "38,040,000", "23,894,500", "15,345,500"],
        ],
    }],
)
log(True, "15_Golden_Falcon_Budget_Breakdown.xlsx")

# 16: Daily Call Sheet (PDF, Internal)
write_pdf(
    "16_Daily_Call_Sheet_2026-09-15.pdf",
    "Daily Call Sheet — 15 September 2026 (Day 22 of 68)",
    [
        "## Project: Golden Falcon · Production Block 2 of 4",
        "## Location: Jebel Jais, Ras Al Khaimah — Base Camp Grid Reference 25.9412°N, 56.1371°E",
        "## Weather Forecast: 32°C / 18% humidity / wind NE 12 km/h / sunrise 06:03 / sunset 18:24 / moonrise 19:51 (98% waxing gibbous)",
        "## Crew Call: 05:00 · First Shot: 06:30 · Lunch: 12:00–12:45 · Wrap: 18:30",
        "## Scenes Scheduled: Scene 7 (Bedouin Rider cresting ridge) — Pages 1.5",
        "## Cast On Set",
        "Tariq — Actor TBC (stand-in Abdulrahman) — Arrive 05:00 · Makeup 05:30 · On set 06:15",
        "Bedouin Rider (silhouette) — Stand-in Khalid — Arrive 04:45 · Makeup 05:00",
        "Grey Arabian Mare 'Layla' — Wrangler Hassan — Arrive 04:30 · Cool down 12:00 and 17:00",
        "## Department Heads",
        "Director: Yousef Al Saedi · Producer: Sara Al Kindy · Production Manager: Layla Al Mehrabi · DP: Marco Beltrami · 1st AD: Tariq Hassan · Gaffer: James Park · Key Grip: Ahmed Al Blooshi · Sound: Salem Al Zaabi · Costume: Nadia Hasan · Makeup: Farah Al Suwaidi · Stunt Coordinator: Vlad Petrov · Location Manager: Mouna Bensaleh (Mira Studios liaison)",
        "## Equipment",
        "Camera: ARRI Alexa Mini LF + Cooke S7/i primes (25mm, 32mm, 50mm, 75mm) + Angenieux 24-290 zoom",
        "Grip: 30ft Technocrane + Russian Arm on tracking vehicle · Wescam stabilised head",
        "Lighting: 18K HMI x2 for sunrise augmentation · Astera tubes x40 for candle practicals",
        "Sound: Sound Devices Scorpio + Lectrosonics wireless x8 · Boom op + 2 utility",
        "## Safety Notes",
        "Heat protocol: 15-min shade breaks every 90 min · Iced water at craft service · Horse welfare: vet on call (Dr. Aisha, +971 50 123 4567) · No drones below 50m after 17:00 (RAK airport approach)",
        "## Catering",
        "Breakfast: 05:00-06:00 · Lunch: 12:00-12:45 · Hot dinner wrap: 18:45 (caterer Desert Kitchen, halal certified)",
        "## Tomorrow",
        "16 September: Scene 8 — Tarik at the ridge. Crew call 05:15. Forecast: similar conditions.",
    ],
    subtitle="Internal — Cast & Crew Only · Issued 14 September 2026 22:14 by Layla Al Mehrabi",
)
log(True, "16_Daily_Call_Sheet_2026-09-15.pdf")

# 17: Scene 12 Take 3 OnSet MP4 (MP4, Confidential) — for timestamp demo
write_mp4(
    "17_Scene12_Take3_OnSet.mp4",
    "SCENE 12 — TAKE 3",
    "Project Golden Falcon · Caravanserai Interior · 24 September 2026",
    duration=15,
)
log(True, "17_Scene12_Take3_OnSet.mp4")

# 18: Field Audio Update Day 4 (MP3, Confidential)
write_mp3(
    "18_Field_Audio_Update_Day4.mp3",
    "Field audio update, day four, Jebel Jais. This is Layla, production manager. "
    "Today we wrapped Scene 7, the Bedouin Rider sequence, with five usable takes. "
    "The horse was a star. Yousef is happy with take three specifically — the silhouette against the dawn light is exactly what he storyboarded. "
    "Tomorrow we move to Scene 8, Tarik at the ridge. Crew call is five fifteen AM. "
    "One issue: the candle practicals for Scene 12 are arriving late from the supplier. They were supposed to be on set by tomorrow evening, "
    "now confirmed for Saturday morning. This does not block us tomorrow or Friday, but I want to flag it for Saturday's setup. "
    "I will update the call sheet tonight. Anything urgent, call me directly. Goodnight.",
)
log(True, "18_Field_Audio_Update_Day4.mp3")

# ----------------------------------------------------------------------
# Films · Finance & Admin (2 docs)
# ----------------------------------------------------------------------
print("\n=== Films · Finance & Admin (2 docs) ===")

# 19: Vendor Invoices (CSV, Confidential)
write_csv(
    "19_Films_Vendor_Invoices.csv",
    [
        ["INV-2026-0001", "Mira Studios FZ-LLC", "Sound stage rental Sep 2026", "1,275,000.00", "AED", "2026-09-30", "Paid", "2026-10-05"],
        ["INV-2026-0002", "House of Taneeq", "Costumes Block 2", "215,000.00", "AED", "2026-09-15", "Paid", "2026-09-22"],
        ["INV-2026-0003", "Desert Kitchen LLC", "Catering Block 2 weeks 1-3", "84,000.00", "AED", "2026-09-21", "Paid", "2026-09-28"],
        ["INV-2026-0004", "Speedy Motors UAE", "Vehicle hire 4x4 x6 (Sep)", "92,500.00", "AED", "2026-09-30", "Pending", ""],
        ["INV-2026-0005", "RAK Film Commission", "Location permit fees", "345,000.00", "AED", "2026-09-10", "Paid", "2026-09-15"],
        ["INV-2026-0006", "Studio Art Dept", "Set construction Scene 12", "612,000.00", "AED", "2026-09-25", "Pending", ""],
        ["INV-2026-0007", "AIG MENA", "Production insurance premium", "850,000.00", "AED", "2026-09-01", "Paid", "2026-09-08"],
        ["INV-2026-0008", "ARRI Rental Dubai", "Camera package Block 2", "425,000.00", "AED", "2026-09-30", "Pending", ""],
        ["INV-2026-0009", "Marco Beltrami (DP)", "DP fee Block 2 (3 weeks)", "390,000.00", "AED", "2026-09-30", "Pending", ""],
        ["INV-2026-0010", "Vlad Petrov Stunts", "Stunt coordination Block 2", "175,000.00", "AED", "2026-09-25", "Paid", "2026-10-01"],
        ["INV-2026-0011", "Dr. Aisha Veterinary", "On-set vet (horse welfare)", "18,500.00", "AED", "2026-09-20", "Paid", "2026-09-25"],
        ["INV-2026-0012", "Mira Studios FZ-LLC", "Lighting equipment upgrade", "180,000.00", "AED", "2026-09-30", "Pending", ""],
    ],
    ["Invoice #", "Vendor", "Description", "Amount", "Currency", "Invoice Date", "Status", "Payment Date"],
)
log(True, "19_Films_Vendor_Invoices.csv")

# 20: Payroll October 2026 (XLSX, Restricted) — PII scenario
write_xlsx(
    "20_Films_Payroll_October_2026.xlsx",
    [{
        "name": "Films Payroll Oct 2026",
        "headers": ["Employee ID", "Name", "Position", "Gross Salary (AED)",
                    "Bank", "IBAN", "Account #", "Net Pay (AED)"],
        "rows": [
            ["S-1004", "Sara Al Kindy", "CEO Seekra Films", "62,500.00", "Emirates NBD", "AE070331234567890123456", "1023456789", "56,875.00"],
            ["S-1005", "Yousef Al Saedi", "Creative Director", "45,000.00", "ADCB", "AE230203012345678901234", "2030123456", "40,950.00"],
            ["S-1006", "Layla Al Mehrabi", "Production Lead", "28,500.00", "Emirates Islamic", "AE640890123456789012345", "8901234567", "25,935.00"],
            ["S-1007", "Ahmed Al Ketbi", "Production Assistant", "12,800.00", "FAB", "AE140311234567890123456", "3112345678", "11,648.00"],
            ["S-1101", "Marco Beltrami", "DP (Contractor)", "65,000.00", "HSBC UAE", "AE520228901234567890123", "2289012345", "59,150.00"],
            ["S-1102", "Tariq Hassan", "1st AD", "32,000.00", "Emirates NBD", "AE070331987654321098765", "1987654321", "29,120.00"],
            ["S-1103", "James Park", "Gaffer", "21,500.00", "ADCB", "AE230203456789012345678", "4567890123", "19,565.00"],
            ["S-1104", "Nadia Hasan", "Costume Designer", "24,000.00", "Emirates Islamic", "AE640890876543210987654", "8765432109", "21,840.00"],
            ["S-1105", "Farah Al Suwaidi", "Makeup Lead", "18,500.00", "FAB", "AE140311234598765432109", "1234598765", "16,835.00"],
            ["S-1106", "Salem Al Zaabi", "Sound Recordist", "19,800.00", "Emirates NBD", "AE070331876543210987654", "1876543210", "18,018.00"],
        ],
    }],
)
log(True, "20_Films_Payroll_October_2026.xlsx")

# ----------------------------------------------------------------------
# Creative · Direction (2 docs)
# ----------------------------------------------------------------------
print("\n=== Creative · Direction (2 docs) ===")

# 21: Emirates Advertising Awards Brief (PDF, Confidential)
write_pdf(
    "21_Emirates_Advertising_Awards_Brief.pdf",
    "Emirates Advertising Awards 2026 — Submission Brief",
    [
        "## Client: Dubai Tourism & Commerce Marketing (DTCM)",
        "## Project: 'See Dubai Differently' — Multichannel Campaign",
        "## Submission Category: Integrated Marketing Campaign — Tourism",
        "## Background",
        "Dubai Tourism appointed Seekra Creative in March 2026 to develop and execute an integrated marketing campaign targeting millennial and Gen Z travelers from GCC, Europe, and South Asia. The campaign objective was to reposition Dubai beyond luxury shopping — surfacing the city's creative, heritage, and adventure experiences.",
        "The campaign launched on 1 June 2026 across TV, digital, out-of-home, and experiential channels, running through 31 August 2026 (peak summer season).",
        "## Creative Strategy",
        "The strategic insight: 'Dubai is the only city where you can surf at dawn, ride a horse through a desert sunset, and edit a film at midnight — all in the same day, all within 45 minutes of each other.'",
        "We named this 'See Dubai Differently' — a campaign built around three ordinary people discovering three extraordinary versions of the city: the surfer, the rider, the editor.",
        "## Execution",
        "Three 60-second hero films, each centered on one character. Cross-cut between their activity and the city that enables it. Director: Nora Al Suwaidi. DP: Marco Beltrami (shared with Golden Falcon shoot). Shot across Dubai: Kite Beach, Al Marmoom Desert, Alserkal Avenue.",
        "300+ digital assets derived from the hero films: 15s and 30s cutdowns, vertical 9:16 for TikTok/Reels, square for Instagram feed, 1920x1080 for YouTube pre-roll.",
        "Experiential: pop-up photo installations at The Dubai Mall, City Walk, and Alserkal Avenue during July 2026 — over 47,000 visitor interactions measured.",
        "## Results",
        "Reach: 23.4M unique individuals across all channels (target: 18M).",
        "Engagement: 4.2M video completions (target: 2.5M). 68% above benchmark.",
        "Sentiment: 91% positive/neutral across social listening (benchmark: 78%).",
        "Visit impact: Dubai visitor arrivals in Jul-Aug 2026 were 14% higher year-over-year (DTCM official statistics, partial attribution).",
        "Brand lift: 'Dubai = creative city' association rose from 31% to 47% in target markets.",
        "## Budget & ROI",
        "Total campaign budget: AED 6.8M (creative production + media buy + experiential).",
        "Cost per completed view: AED 1.62 (industry benchmark: AED 2.40).",
        "Estimated tourism revenue impact: AED 340M+ (DTCM econometric model).",
        "## Why This Deserves to Win",
        "This campaign did not sell Dubai — it let Dubai sell itself, by surfacing the authentic creative pulse that 90% of tourists never see. It moved the brand from luxury to creativity without abandoning luxury. It delivered above benchmark on every measurable metric. And it was made in Dubai, by Dubai talent, for a global audience — which is exactly what the Emirates Advertising Awards exist to celebrate.",
    ],
    subtitle="Confidential — Submission for Emirates Advertising Awards 2026 · Category: Integrated Tourism Campaign",
    metadata={
        "Agency": "Seekra Creative (Mohammed Al Marri, CEO)",
        "Client": "Dubai Tourism & Commerce Marketing",
        "Campaign": "See Dubai Differently",
        "Total Budget": "AED 6.8M",
        "ROI": "AED 340M+ tourism impact",
    },
)
log(True, "21_Emirates_Advertising_Awards_Brief.pdf")

# 22: Dubai Tourism Pitch Deck (PPTX, Confidential)
write_pptx(
    "22_Dubai_Tourism_Pitch_Deck.pptx",
    "See Dubai Differently — Pitch Deck",
    [
        {"title": "The Insight", "body": [
            "Dubai is marketed as a luxury destination.",
            "But 67% of under-35 travelers say luxury marketing 'turns them off.'",
            "They want authenticity. They want to discover.",
            "",
            "Dubai has more authentic creative energy than any city in the region.",
            "We just never showed it.",
        ]},
        {"title": "The Strategy", "body": [
            "Stop selling Dubai as luxury.",
            "Start showing Dubai as the only city where you can:",
            "  — surf at dawn",
            "  — ride a horse through a desert sunset",
            "  — edit a film at midnight",
            "  — all in the same day, all within 45 minutes of each other.",
            "",
            "Three characters. Three ordinary people. Three extraordinary days.",
        ]},
        {"title": "The Films", "body": [
            "Hero Film 1: 'The Surfer' — Kite Beach, 5:30 AM",
            "Hero Film 2: 'The Rider' — Al Marmoom Desert, 6:15 PM",
            "Hero Film 3: 'The Editor' — Alserkal Avenue, 11:42 PM",
            "",
            "Each 60 seconds. Each cut to a 30s and 15s for digital.",
            "Cross-cut between character and city — the city is the second protagonist.",
        ]},
        {"title": "The Talent", "body": [
            "Director: Nora Al Suwaidi (Emirati, 32, rising star)",
            "DP: Marco Beltrami (Italian, Dubai-based, 12 years in region)",
            "Cast: 3 leads + 60 background — all UAE residents",
            "Crew: 80% UAE-based talent",
            "",
            "We are not bringing in a foreign eye. We are showing ours.",
        ]},
        {"title": "The Distribution", "body": [
            "TV: OSN, Shahid, MBC — 8-week run, primetime",
            "Digital: YouTube pre-roll, TikTok, Instagram Reels, Snapchat",
            "OOH: Dubai Mall, City Walk, Mall of the Emirates, metro stations",
            "Experiential: 3 pop-up photo installations in July",
            "PR: Launch event + influencer partnerships (15 macro, 80 micro)",
        ]},
        {"title": "The Numbers", "body": [
            "Total campaign budget: AED 6.8M",
            "  — Creative production: AED 2.4M",
            "  — Media buy: AED 3.6M",
            "  — Experiential + PR: AED 0.8M",
            "",
            "Forecast reach: 18M unique (GCC + EU + South Asia)",
            "Forecast video completions: 2.5M",
            "Forecast brand lift: +15 points on 'Dubai = creative'",
        ]},
        {"title": "Why Seekra Creative", "body": [
            "We are Dubai-based. We know the city.",
            "We have the production muscle (Seekra Studios post-production in-house).",
            "We have the broadcast reach (Seekra Broadcast distribution).",
            "We are the only agency in the region that can shoot, edit, and air",
            "  a campaign without a single external vendor.",
            "",
            "And we believe in this story.",
        ]},
    ],
)
log(True, "22_Dubai_Tourism_Pitch_Deck.pptx")

print("\n" + "=" * 60)
print(f"PART 2 (docs 12-22): {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
