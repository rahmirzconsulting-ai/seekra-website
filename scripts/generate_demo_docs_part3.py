#!/usr/bin/env python3
"""Demo doc generation — Part 3 (docs 23-32: Creative Production + Sales +
Studios + Broadcast).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/z/my-project/scripts")
from demo_doc_helpers import (
    write_pdf, write_docx, write_xlsx, write_pptx, write_jpg, write_png,
    write_mp3, write_mp4, write_text, write_csv, OUT,
)

PASS = FAIL = 0
def log(ok, msg):
    global PASS, FAIL
    print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
    if ok: PASS += 1
    else: FAIL += 1


print("=" * 60)
print("GENERATING DEMO DOCUMENTS — PART 3 (docs 23-32)")
print("=" * 60)

# Creative · Production (2)
print("\n=== Creative · Production (2 docs) ===")
write_png("23_Golden_Falcon_Logo_Concept.png",
          "Golden Falcon Logo Concept",
          "Brand Identity · v0.3 concept",
          )
log(True, "23_Golden_Falcon_Logo_Concept.png")

write_jpg("24_Branding_Display.jpg",
          "DIFC Lobby Branding Display",
          "Seekra HQ Reception · March 2026",
          bg_color=(245, 247, 252),
          )
log(True, "24_Branding_Display.jpg")

# Creative · Sales & Client Services (2)
print("\n=== Creative · Sales & Client Services (2 docs) ===")
write_csv("25_Active_Client_List.csv",
    [
        ["CL-001", "Dubai Tourism & Commerce Marketing", "DTCM", "Government",
         "Hassan Al Zaabi", "+971 50 234 5678", "hassan.zaabi@dtcm.gov.ae",
         "784-1991-8901234-5", "AED 6.8M", "Active", "2026-03-15"],
        ["CL-002", "Emirates Airlines", "Emirates", "Corporate",
         "Sarah Whitcombe", "+971 4 214 4444", "s.whitcombe@emirates.com",
         "784-1982-2345678-9", "AED 4.2M", "Active", "2026-04-22"],
        ["CL-003", "Aldar Properties PJSC", "Aldar", "Corporate",
         "Mohammed Al Mehairi", "+971 2 818 3333", "m.almehairi@aldar.com",
         "784-1986-3456789-0", "AED 3.5M", "Active", "2026-05-10"],
        ["CL-004", "Mubadala Investment Company", "Mubadala", "Government",
         "Aisha Al Neyadi", "+971 2 413 9999", "aishan@mubadala.com",
         "784-1989-4567890-1", "AED 12.0M", "Active", "2026-01-08"],
        ["CL-005", "Saudi Tourism Authority", "STA", "Government (KSA)",
         "Faisal Al Saud", "+966 11 222 3333", "f.alsaud@stc.com.sa",
         "784-1984-5678901-2", "AED 8.4M", "Active", "2026-06-15"],
        ["CL-006", "ADNOC Distribution", "ADNOC", "Corporate",
         "Khalifa Al Hammadi", "+971 2 696 4444", "khalifa.h@adnoc.ae",
         "784-1987-6789012-3", "AED 2.1M", "Active", "2026-07-01"],
        ["CL-007", "Majid Al Futtaim Group", "MAF", "Corporate",
         "Lina Haddad", "+971 4 709 5000", "lina.haddad@maf.co.ae",
         "784-1988-7890123-4", "AED 5.6M", "Active", "2026-02-20"],
        ["CL-008", "DP World UAE Region", "DP World", "Corporate",
         "Salem Bin Sulayem", "+971 4 881 6000", "salem.bs@dpworld.com",
         "784-1983-8901234-5", "AED 4.8M", "Active", "2026-05-30"],
        ["CL-009", "Etisalat by e&", "Etisalat", "Corporate",
         "Mariam Al Suwaidi", "+971 2 800 2300", "mariam.s@etisalat.ae",
         "784-1990-9012345-6", "AED 3.9M", "Active", "2026-04-05"],
        ["CL-010", "Saudi Aramco", "Aramco", "Corporate (KSA)",
         "Turki Al Naimi", "+966 13 873 5555", "turki.naimi@aramco.com",
         "784-1981-1234567-8", "AED 9.2M", "Active", "2026-03-22"],
    ],
    ["Client ID", "Client Name", "Short Name", "Sector",
     "Primary Contact", "Phone", "Email", "Emirates ID",
     "Contract Value (AED)", "Status", "Onboarded"],
)
log(True, "25_Active_Client_List.csv")

write_pdf("26_Dubai_Tourism_Contract.pdf",
    "Services Contract — Dubai Tourism & Commerce Marketing",
    [
        "## Contract Reference: DTCM-CRE-2026-0412",
        "## Parties",
        "This Services Contract (\"Contract\") is entered into on 1 March 2026 by and between:",
        "**Dubai Tourism & Commerce Marketing (DTCM)**, an entity of the Government of Dubai, having its principal office at Level 32, Emirates Towers, Sheikh Zayed Road, Dubai, United Arab Emirates (\"Client\");",
        "and",
        "**Seekra Creative FZ-LLC**, a limited liability company incorporated in the Dubai Multi Commodities Centre (DMCC) under license number 36722, having its registered office at JLT Cluster X, Level 14, Dubai, United Arab Emirates (\"Agency\").",
        "## 1. Scope of Services",
        "The Agency shall provide creative strategy, concept development, film production, post-production, digital asset production, and media buying services for the Client's 2026 summer campaign tentatively titled \"See Dubai Differently\" (the \"Campaign\"). Detailed deliverables, milestones, and specifications are set forth in Schedule A.",
        "## 2. Term",
        "This Contract commences on 1 March 2026 and concludes on 31 August 2026, covering the full Campaign lifecycle from concept through post-campaign reporting. Pre-production may commence immediately upon signature.",
        "## 3. Fees & Payment",
        "Total contract value: AED 6,800,000 (six million eight hundred thousand dirhams), inclusive of all UAE VAT where applicable. Payable in four milestone installments: 20% upon signature, 30% upon delivery of creative concept, 30% upon delivery of master films, and 20% upon delivery of post-campaign report.",
        "All payments shall be made by wire transfer within 30 days of invoice to: Seekra Creative FZ-LLC · Emirates NBD · IBAN: AE070331234567890123456 · SWIFT: EBILAEAD023",
        "## 4. Deliverables",
        "Schedule A deliverables include: (a) Creative strategy document; (b) Three 60-second hero films in 16:9 master format; (c) 300+ digital asset cutdowns in 9:16, 1:1, and 16:9 formats; (d) Out-of-home creative in 6 sheet, 48 sheet, and digital formats; (e) Experiential design for three pop-up installations; (f) Media buy plan and execution; (g) Post-campaign analytics report.",
        "## 5. Intellectual Property",
        "All creative work product, including but not limited to films, designs, copy, music, and derivative works, shall become the exclusive property of Client upon full payment of all fees. Agency retains the right to use the work for awards submissions and agency reel purposes, subject to Client's prior written approval (not to be unreasonably withheld).",
        "## 6. Confidentiality",
        "Each party shall hold in strict confidence all non-public information disclosed by the other party. Confidentiality obligations survive expiration or termination of this Contract for a period of five (5) years.",
        "## 7. Termination",
        "Either party may terminate this Contract for material breach upon 14 days written notice and failure to cure. Client may terminate for convenience upon payment of a termination fee equal to 25% of the unperformed contract value plus costs of work in progress.",
        "## 8. Governing Law & Dispute Resolution",
        "This Contract is governed by the laws of the United Arab Emirates. Disputes shall be resolved through binding arbitration administered by the Emirates Maritime Arbitration Centre (EMAC) under its Rules, seat Dubai, language English, single arbitrator.",
        "## 9. Signatures",
        "For DTCM: Signed by Hassan Al Zaabi, Director of Marketing. Date: 1 March 2026.",
        "For Seekra Creative FZ-LLC: Signed by Mohammed Al Marri, Chief Executive Officer. Emirates ID 784-1985-2345678-9. Date: 1 March 2026.",
    ],
    subtitle="Confidential — Executed 1 March 2026 · DTCM Reference DTCM-CRE-2026-0412",
    metadata={
        "Effective Date": "1 March 2026",
        "Contract Value": "AED 6,800,000",
        "Term": "1 Mar 2026 – 31 Aug 2026",
        "Governing Law": "UAE Federal Law",
        "Arbitration": "EMAC, Dubai, 1 arbitrator",
    },
)
log(True, "26_Dubai_Tourism_Contract.pdf")

# Studios · Post-Production (2)
print("\n=== Studios · Post-Production (2 docs) ===")
write_docx("27_Warehouse_Safety_Procedures.docx",
    "Warehouse Safety Procedures — Seekra Studios Jebel Ali",
    [
        ("body", "Version 2.1 · Effective 1 September 2026 · Owner: Studios Operations"),
        ("h1", "1. Purpose"),
        ("body", "This document defines the safety procedures for all Seekra Studios warehouse and post-production facilities at Jebel Ali Free Zone. Compliance is mandatory for all employees, contractors, and visitors."),
        ("h1", "2. Emergency Exits & Assembly Points"),
        ("body", "The Jebel Ali facility has six emergency exits, clearly marked with green illuminated signage. Primary assembly point: North Parking Lot, Grid Reference B7. Secondary assembly point (if primary is unsafe): East Gate Visitor Lot. Floor wardens are designated for each zone and wear orange high-visibility vests during evacuations."),
        ("body", "Fire drills are conducted quarterly. The next scheduled drill is 15 December 2026 at 10:00 AM. All personnel must participate and sign the drill attendance log."),
        ("h1", "3. Hazardous Materials"),
        ("body", "The facility stores limited quantities of: lithium-ion batteries (camera equipment), isopropyl alcohol (cleaning), and compressed gas cylinders (helium for lighting rigs). All hazardous materials are stored in the designated HM cabinet in Bay 4, with appropriate Safety Data Sheets (SDS) posted on the cabinet door."),
        ("body", "Spill response kits are located at: Bay 2 (entrance), Bay 4 (HM cabinet), and Bay 7 (loading dock). Any spill must be reported to the Floor Warden immediately."),
        ("h1", "4. Equipment Handling"),
        ("body", "All personnel operating forklifts, scissor lifts, or boom lifts must hold a valid UAE-recognized certification. Pre-use inspection is required for every shift. Maximum load capacities are posted on each piece of equipment and must never be exceeded."),
        ("body", "Camera equipment valued above AED 50,000 must be transported in hard-shell cases with two-person handling for stairs or uneven surfaces."),
        ("h1", "5. Personal Protective Equipment (PPE)"),
        ("body", "Required PPE by zone: Bay 1-3 (post-production suites) — none required; Bay 4-6 (equipment storage) — closed-toe shoes; Bay 7 (loading dock) — high-visibility vest, steel-toe boots, hard hat; Crane operations (anywhere) — hard hat, high-visibility vest, exclusion zone enforced at 1.5x maximum reach."),
        ("h1", "6. Incident Reporting"),
        ("body", "All incidents, near-misses, and unsafe conditions must be reported within 24 hours via the Seekra Incident Reporting Portal at safety.seekra-media.ae. The report shall include: date/time, location, persons involved, description, immediate actions taken, and recommended preventive measures."),
        ("body", "Serious incidents (any injury requiring medical attention, any property damage exceeding AED 10,000, any fire) must be reported by phone to the Operations Manager within 1 hour."),
        ("h1", "7. First Aid & Emergency Contacts"),
        ("body", "First aid stations are located at: Reception (Bay 1), Bay 4 (HM cabinet), and Bay 7 (loading dock). The Operations Manager (Tariq Hassan, +971 50 555 0100) is the primary emergency contact. The Jebel Ali Medical Centre (+971 4 815 4444) is the nearest hospital — 7 minutes by car."),
        ("h1", "8. Review & Updates"),
        ("body", "This document is reviewed annually by the Studios Safety Committee. The next scheduled review is 1 September 2027. Any interim updates will be communicated via email and posted on facility notice boards."),
    ],
    subtitle="Internal — All Studios Staff & Visitors · Seekra Studios Jebel Ali Facility",
)
log(True, "27_Warehouse_Safety_Procedures.docx")

write_xlsx("28_Golden_Falcon_Edit_Schedule.xlsx",
    [{
        "name": "Edit Schedule",
        "headers": ["Week", "Phase", "Editor", "Start Date", "End Date",
                    "Scenes", "Hours Budgeted", "Hours Used", "Status"],
        "rows": [
            ["W1", "Assembly Cut", "Ahmed Al Blooshi", "2026-10-26", "2026-10-30", "1-4", "40", "0", "Not Started"],
            ["W2", "Assembly Cut", "Ahmed Al Blooshi", "2026-11-02", "2026-11-06", "5-9", "40", "0", "Not Started"],
            ["W3", "Assembly Cut", "Ahmed Al Blooshi", "2026-11-09", "2026-11-13", "10-14", "40", "0", "Not Started"],
            ["W4", "Rough Cut", "Ahmed Al Blooshi", "2026-11-16", "2026-11-20", "All", "40", "0", "Not Started"],
            ["W5", "Director Review", "Yousef Al Saedi", "2026-11-23", "2026-11-27", "All", "32", "0", "Not Started"],
            ["W6", "Fine Cut v1", "Ahmed Al Blooshi", "2026-11-30", "2026-12-04", "All", "40", "0", "Not Started"],
            ["W7", "Producer Review", "Sara Al Kindy", "2026-12-07", "2026-12-11", "All", "32", "0", "Not Started"],
            ["W8", "Picture Lock Prep", "Ahmed Al Blooshi", "2026-12-14", "2026-12-18", "All", "40", "0", "Not Started"],
            ["W9", "Picture Lock", "All stakeholders", "2026-12-21", "2026-12-23", "All", "24", "0", "Not Started"],
            ["W10-11", "Color Grading", "Reem Al Falasi", "2027-01-04", "2027-01-15", "All", "80", "0", "Not Started"],
            ["W12", "Sound Design", "Salem Al Zaabi", "2027-01-18", "2027-01-22", "All", "40", "0", "Not Started"],
            ["W13", "Music Score", "Composer (TBC)", "2027-01-25", "2027-01-29", "All", "40", "0", "Not Started"],
            ["W14", "Final Mix", "Salem Al Zaabi", "2027-02-01", "2027-02-05", "All", "40", "0", "Not Started"],
            ["W15", "VFX Integration", "Khalid Al Mazrouei", "2027-02-08", "2027-02-12", "12 + 14 augmentation", "40", "0", "Not Started"],
            ["W16", "Mastering & Delivery", "Reem Al Falasi", "2027-02-15", "2027-02-19", "All", "40", "0", "Not Started"],
        ],
    }],
)
log(True, "28_Golden_Falcon_Edit_Schedule.xlsx")

# Studios · VFX (1)
print("\n=== Studios · VFX (1 doc) ===")
write_pdf("29_VFX_Shot_List_Scene12.pdf",
    "VFX Shot List — Scene 12 (Caravanserai Interior)",
    [
        "## Project: Project Golden Falcon · Scene 12",
        "## VFX Supervisor: Khalid Al Mazrouei",
        "## Total Shots: 14 (1 hero, 13 augmentation)",
        "## Budgeted Cost: AED 5,200,000 (approved Q3 board, includes AED 2.0M contingency)",
        "## Hero Shot: VFX-12-001",
        "Description: The brass telescope lifts from the stone altar and rotates in mid-air, pointing south. Duration: 8 seconds on screen.",
        "Approach: Physical magnet rig on altar (built by Seekra Studios art dept). Telescope is real brass, weighing 4.2 kg. VFX removes the rig and adds the soft golden glow pulsing in time with the heartbeat sound design. Rotation is achieved practically with a concealed stepper motor inside the altar — VFX removes the motor shadow.",
        "Vendor: In-house Seekra Studios VFX team. Estimated hours: 320. Delivery: 5 February 2027.",
        "## Augmentation Shots: VFX-12-002 through VFX-12-014",
        "VFX-12-002: Candle flames enhanced with subtle particle simulation (13 shots in sequence). 8 hours each = 104 hours total.",
        "VFX-12-003: Moonlight shaft through oculus — color grade adjustment + atmospheric haze. 24 hours.",
        "VFX-12-004: Tarik's face — subtle reflection of glowing telescope in his eyes. 16 hours.",
        "VFX-12-005: Dust particles in moonlight shaft — practical dust augmented with CG. 32 hours.",
        "VFX-12-006: Telescope engraving close-up — falcon image appears to move slightly. 40 hours.",
        "VFX-12-007: Wide shot of caravanserai — candlelight balance across 400 practicals. 48 hours.",
        "VFX-12-008: Tarik's hand on the telescope — skin tone continuity. 12 hours.",
        "VFX-12-009: Altar surface — texture enhancement, blood-red velvet detail. 20 hours.",
        "VFX-12-010: Background tapestry — pattern continuity. 8 hours.",
        "VFX-12-011: Reflection in telescope brass — Tarik's face appears briefly. 36 hours.",
        "VFX-12-012: Final pullback — composite of three plates (Tarik, telescope, candlelit interior). 80 hours.",
        "VFX-12-013: Sky replacement through oculus — moon and stars. 24 hours.",
        "VFX-12-014: Cleanup — rig removal, wire removal, safety mat removal. 48 hours.",
        "## Total Estimated Hours: 1,012",
        "## Average Rate: AED 5,200/hour (in-house rate)",
        "## Notes",
        "All shots will be reviewed in dailies with Director Yousef Al Saedi and DP Marco Beltrami. Final delivery to color grading: 5 February 2027. The hero shot (VFX-12-001) is the critical path item — any delay there impacts the entire post schedule.",
        "The magnet rig approach (vs. full CG) was chosen by the Director specifically for the weight and presence of the practical telescope. The VFX team has confirmed feasibility with the art department. Risk: if the magnet release mechanism is unreliable on set, we will fall back to a fully CG telescope for the lift shot — but this is Plan B and not the recommended approach.",
    ],
    subtitle="Confidential — VFX Team & Director Only · 24 August 2026",
    metadata={
        "VFX Supervisor": "Khalid Al Mazrouei",
        "Total Shots": "14",
        "Budgeted Hours": "1,012",
        "Budget (AED)": "5,200,000",
        "Delivery Date": "5 February 2027",
    },
)
log(True, "29_VFX_Shot_List_Scene12.pdf")

# Studios · Sound Design (1)
print("\n=== Studios · Sound Design (1 doc) ===")
write_docx("30_Sound_Design_Brief.docx",
    "Sound Design Brief — Project Golden Falcon",
    [
        ("body", "Project: Golden Falcon · Date: 12 September 2026 · Owner: Salem Al Zaabi, Sound Designer"),
        ("h1", "1. Creative Direction"),
        ("body", "The sound design for Golden Falcon must serve the Director's vision of 'revelation, not spectacle.' The audience should never feel manipulated; every sound must feel earned and necessary. The palette is sparse — oud, breath, wind, the heartbeat of the telescope — punctuated by moments of absolute silence."),
        ("h1", "2. Soundscape Layers"),
        ("body", "Layer 1 — Environment: Naturalistic desert wind (recorded on set at Jebel Jais), distant bird calls, the soft step of the horse. Recorded in stereo with a Sennheiser MKH 416 shotgun and a Sound Devices MixPre-6. Library: 4.2 hours of raw location ambience."),
        ("body", "Layer 2 — Music: Original score by a composer TBC. Sparse, contemporary, using oud and viola da gamba as primary voices. Score budget: AED 1,200,000 (including recording at Seekra Studios Sound Stage B). Total score runtime target: 38 minutes across the 128-minute film."),
        ("body", "Layer 3 — Foley: Footsteps on sand, gravel, stone; fabric movement (kaffiyeh, thobe, abaya); brass telescope handling (weight, friction, the click of the lens cap). Recorded at Seekra Studios Foley Pit. Foley artist: Mouna Bensaleh."),
        ("body", "Layer 4 — Voice: Dialogue is in Arabic (Gulf dialect, with classical Arabic for ritual moments). ADR for two scenes: Scene 8 (Tarik at the ridge, wind noise) and Scene 14 (Young Woman's first line). ADR session booked for 14-15 November 2026."),
        ("h1", "3. Scene 12 Specific Direction"),
        ("body", "Scene 12 — the caravanserai interior — is the sonic centerpiece of the film. The brief: 90 seconds of near-silence, broken only by the heartbeat (sub-bass, 50 BPM), the candle flames (high-frequency shimmer, like distant wind chimes), and Tarik's breath. When the telescope lifts, the heartbeat stops. There is one full second of absolute silence. Then the heartbeat resumes, faster — 70 BPM. The audience should feel their own heartbeat sync with the film."),
        ("body", "Sound supervisor notes: The silence after the lift must be real silence — no room tone, no dither. This is technically demanding but emotionally essential. We will need to record absolute silence in the Foley pit (sealed, sound-treated) and use it deliberately."),
        ("h1", "4. Technical Specifications"),
        ("body", "Master format: Dolby Atmos 7.1.4 (9.1 bed + 4 height channels). Delivery: 24-bit/48kHz BWAV masters. Cinema mix: 5.1 fold-down for theaters without Atmos. Streaming masters: stereo and 5.1 for Netflix MENA, StarzPlay, Shahid deliverables."),
        ("h1", "5. Schedule"),
        ("body", "Spotting session with Director: 18 January 2027 (after picture lock). Foley recording: 25 January - 5 February 2027. Music recording: 8-12 February 2027. Pre-mix: 15-19 February 2027. Final mix: 22-26 February 2027. Master delivery: 1 March 2027."),
        ("h1", "6. Deliverables"),
        ("body", "Final theatrical mix (Atmos + 5.1 fold-down), streaming masters (stereo + 5.1 for each platform), M&E (Music & Effects) tracks for international dubbing, and a complete sound asset library for archival. All deliverables to be uploaded to the Seekra Studios asset management system with SHA-256 checksums."),
    ],
    subtitle="Internal — Sound Team & Director · 12 September 2026",
)
log(True, "30_Sound_Design_Brief.docx")

# Broadcast · Programming (1)
print("\n=== Broadcast · Programming (1 doc) ===")
write_mp4("31_City_Street_Stock_Footage.mp4",
    "DUBAI CITY STREET",
    "Stock Footage · Broadcast Programming · 4K 30fps",
    duration=10,
)
log(True, "31_City_Street_Stock_Footage.mp4")

# Broadcast · Sales & Distribution (1)
print("\n=== Broadcast · Sales & Distribution (1 doc) ===")
write_pdf("32_Streaming_Distribution_Agreement.pdf",
    "Streaming Distribution Agreement — Seekra Play & Netflix MENA",
    [
        "## Contract Reference: SMH-DIST-2026-0034",
        "## Parties",
        "This Streaming Distribution Agreement (\"Agreement\") is entered into on 5 October 2026 by and between:",
        "**Seekra Broadcast FZ-LLC**, a limited liability company incorporated in the Dubai Multi Commodities Centre (DMCC) under license number 36724, having its registered office at JLT Cluster X, Level 14, Dubai, United Arab Emirates (\"Licensor\");",
        "and",
        "**Netflix Services MENA FZ-LLC**, a limited liability company incorporated in the Dubai Internet City under license number 31892, having its registered office at Building 12, Dubai Internet City, Dubai, United Arab Emirates (\"Licensee\").",
        "## 1. Licensed Content",
        "The Licensed Content is the feature film currently titled \"Project Golden Falcon\" (the \"Film\"), with a final cut runtime of approximately 128 minutes, directed by Yousef Al Saedi, produced by Seekra Films. Final master delivery to Licensee no later than 1 March 2027.",
        "## 2. Territory & Term",
        "Territory: Kingdom of Saudi Arabia, United Arab Emirates, State of Kuwait, State of Qatar, Kingdom of Bahrain, Sultanate of Oman, Arab Republic of Egypt, and Hashemite Kingdom of Jordan (the \"MENA Territory\").",
        "Term: 24 months from theatrical release + 14 days (i.e. 1 January 2028 to 31 December 2029). Licensee has a non-exclusive first window after theatrical and StarzPlay's pay-TV window.",
        "## 3. License Fee",
        "Licensee shall pay Licensor a non-refundable license fee of USD 4,900,000 (four million nine hundred thousand US dollars), equivalent to approximately AED 18,000,000, payable in three installments: 30% upon signature, 40% upon master delivery, and 30% upon theatrical release.",
        "All payments shall be made by wire transfer to: Seekra Broadcast FZ-LLC · Mashreq Bank · IBAN: AE340033123456789012345 · SWIFT: BOMLAEAD022",
        "## 4. Licensee Obligations",
        "Licensee shall: (a) make the Film available on its streaming service within 14 days of theatrical release; (b) provide marketing support valued at not less than USD 250,000 across the Licensee's owned channels; (c) deliver quarterly viewership reports (unique viewers, completion rates, geographic breakdown); (d) maintain Arabic and English subtitle tracks at minimum, with the option to add additional language tracks at Licensee's discretion.",
        "## 5. Licensor Obligations",
        "Licensor shall: (a) deliver the master in 4K UHD HDR10 with Dolby Atmos audio, per the technical specification in Schedule B; (b) deliver all required metadata, key art, trailers, and marketing assets no later than 14 days before theatrical release; (c) warrant that the Film is free of all encumbrances except those disclosed in writing; (d) procure all necessary music and talent clearances for streaming distribution.",
        "## 6. Marketing & Premiere",
        "Theatrical premiere: 18 December 2026 at VOX Cinemas, Mall of the Emirates, Dubai. Red carpet event jointly organized by Licensor and Seekra Films. Licensee invited as honored guest. Licensee shall have the right to host an exclusive press screening at its Dubai office in the week following premiere.",
        "## 7. Audit Rights",
        "Licensor shall have the right, no more than once per calendar year and upon 30 days written notice, to audit Licensee's records relating to the Film's viewership and any revenue-share calculations (if applicable in future windows). Audit costs borne by Licensor unless discrepancies exceeding 5% are found, in which case Licensee bears the cost.",
        "## 8. Termination",
        "Either party may terminate for material breach upon 30 days written notice and failure to cure. Licensor may terminate immediately if the Film is not delivered by 1 April 2027 (90 days grace from the 1 March 2027 deadline).",
        "## 9. Governing Law & Dispute Resolution",
        "This Agreement is governed by the laws of the United Arab Emirates. Disputes shall be resolved through binding arbitration administered by the Dubai International Financial Centre Arbitration Centre (DIAC), seat Dubai, language English, three arbitrators.",
        "## 10. Signatures",
        "For Seekra Broadcast FZ-LLC: Signed by Tariq Al Qassimi, Chief Executive Officer. Emirates ID 784-1984-3456789-0. Date: 5 October 2026.",
        "For Netflix Services MENA FZ-LLC: Signed by [Signature on file]. Date: 5 October 2026.",
    ],
    subtitle="Restricted — Executed 5 October 2026 · SMH Legal Reference SMH-DIST-2026-0034",
    metadata={
        "Effective Date": "5 October 2026",
        "Contract Value": "USD 4,900,000 (≈ AED 18,000,000)",
        "Territory": "MENA (8 countries)",
        "Term": "24 months (1 Jan 2028 – 31 Dec 2029)",
        "Premiere Date": "18 December 2026",
        "Arbitration": "DIAC, Dubai, 3 arbitrators",
    },
)
log(True, "32_Streaming_Distribution_Agreement.pdf")

print("\n" + "=" * 60)
print(f"PART 3 (docs 23-32): {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
