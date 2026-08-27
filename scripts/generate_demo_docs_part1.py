#!/usr/bin/env python3
"""Demo doc generation — Part 1 (docs 1-11).

Imports helpers from demo_doc_helpers.py.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/home/z/my-project/scripts")
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
print("GENERATING 32 DEMO DOCUMENTS — PART 1 (docs 1-11)")
print("=" * 60)

# Group Executive (4)
print("\n=== Group Executive (4 docs) ===")
write_pdf("01_Employee_Handbook_2026.pdf", "Employee Handbook 2026",
    ["## Welcome to Seekra Media Holdings",
     "Seekra Media Holdings is a Dubai-headquartered media production holding company operating four subsidiaries across film, advertising, post-production, and broadcast. This handbook is the authoritative reference for every employee across Seekra Films, Seekra Creative, Seekra Studios, and Seekra Broadcast.",
     "We are committed to fostering a creative, inclusive, and lawful workplace that reflects the cultural values of the United Arab Emirates and the professional standards of the global media industry. All employees are expected to read this handbook within their first week of employment and acknowledge receipt via the HR portal.",
     "## Code of Conduct",
     "All employees must adhere to the Seekra Code of Conduct, which requires honesty, respect, confidentiality, and compliance with UAE Federal Law and the Dubai Creative Clusters Authority regulations. Conflicts of interest must be disclosed in writing to the Group Legal & Compliance department within 14 days of identification.",
     "## Working Hours & Leave",
     "Standard working hours are 9:00 AM to 6:00 PM, Sunday through Thursday, with a one-hour lunch break. Annual leave entitlement is 30 calendar days per year of service. Sick leave is governed by UAE Labor Law (Federal Decree-Law No. 33 of 2021) — 15 days paid sick leave per year, with medical certificate required for absences exceeding two consecutive days.",
     "## Confidentiality & Data Protection",
     "Employees may encounter confidential client information, unreleased creative work, financial data, and personal data of staff and talent. All such information is governed by our Customer Data Protection Policy and must never be shared outside the company without explicit written authorization from Group Legal.",
     "## Health, Safety & Emergency Procedures",
     "Each Seekra facility has designated emergency exits, assembly points, and floor wardens. The DIFC headquarters assembly point is the Gate Village Podium Level 2. On film set locations, the Production Manager serves as the safety officer. All incidents must be reported within 24 hours via the Seekra Incident Reporting Portal.",
     "## Whistleblower Protection",
     "Employees who report suspected misconduct in good faith are protected from retaliation. Reports may be made anonymously through the Speak-Up portal or directly to the Group Chief Compliance Officer at compliance@seekra-media.ae.",
     "## Acknowledgement",
     "By accepting employment with Seekra Media Holdings, you acknowledge that you have received, read, and understood this handbook. Your manager will request electronic acknowledgement via the HR portal within seven calendar days of your start date."],
    subtitle="Group HR · Effective January 2026 · Version 4.0",
    metadata={"Document Owner": "Group HR (hr@seekra-media.ae)",
              "Approved By": "Khalid Alsoodi, Group CEO",
              "Effective Date": "1 January 2026",
              "Next Review": "1 January 2027",
              "Classification": "Internal — for all employees"})
log(True, "01_Employee_Handbook_2026.pdf")

write_docx("02_Q3_Board_Meeting_Minutes.docx",
    "Board of Directors — Q3 2026 Meeting Minutes",
    [("body", "Date: 15 September 2026"),
     ("body", "Location: Seekra HQ, DIFC, Gate Village Building 4, Boardroom 12B"),
     ("body", "Attendees: Khalid Alsoodi (Group CEO, Chair), Fatima Al Mansouri (Group CFO), Omar Al Hashimi (Group Legal), Sara Al Kindy (CEO, Seekra Films), Mohammed Al Marri (CEO, Seekra Creative), Reem Al Falasi (CEO, Seekra Studios), Tariq Al Qassimi (CEO, Seekra Broadcast)"),
     ("body", "Secretary: Aisha Al Blooshi, Group Corporate Secretary"),
     ("h2", "1. Call to Order"),
     ("body", "The meeting was called to order at 10:03 AM by Chair Khalid Alsoodi. A quorum was confirmed with all seven directors present."),
     ("h2", "2. Approval of Previous Minutes"),
     ("body", "The minutes of the Q2 2026 board meeting (14 June 2026) were reviewed. Omar Al Hashimi motioned to approve; Mohammed Al Marri seconded. Motion carried unanimously."),
     ("h2", "3. CFO Financial Review"),
     ("body", "Fatima Al Mansouri presented the Q3 financial statements. Group revenue reached AED 247.8 million for the quarter, representing 18% year-over-year growth. The films segment led growth with AED 112.4 million, driven primarily by the Project Golden Falcon pre-sales to Netflix MENA and StarzPlay."),
     ("body", "EBITDA margin improved to 22.4% from 19.1% in Q2, reflecting strong cost discipline across all four subsidiaries. Free cash flow was AED 38.6 million, of which AED 25 million has been allocated to the Project Golden Falcon completion reserve."),
     ("body", "The board approved the Q3 financial statements as presented and authorized their filing with the DIFC Registrar of Companies."),
     ("h2", "4. Project Golden Falcon Status Update"),
     ("body", "Sara Al Kindy reported that principal photography on Project Golden Falcon is 78% complete, with the final shoot block scheduled for 10-24 October 2026 at the Jebel Jais location. Total production budget stands at AED 48.2 million, which is 4.2% over the original budget due to extended stunt rehearsal and additional VFX work for Scene 12."),
     ("body", "The board approved a contingency drawdown of AED 2.0 million from the completion reserve to cover the additional VFX scope, subject to Reem Al Falasi's confirmation of delivery timeline."),
     ("h2", "5. Legal & Compliance Report"),
     ("body", "Omar Al Hashimi reported that the Master Services Agreement with Mira Studios has been executed and is now in effect. The Customer Data Protection Policy has been updated to align with the UAE Personal Data Protection Law (PDPL) issued in September 2021, with full employee training scheduled for October 2026."),
     ("h2", "6. Strategic Acquisitions"),
     ("body", "Khalid Alsoodi presented a confidential memorandum regarding the proposed acquisition of a 51% stake in Arabian Post House, a regional VFX studio. After discussion, the board authorized management to proceed with due diligence and a definitive agreement, with a target close date of 15 December 2026."),
     ("h2", "7. Next Meeting"),
     ("body", "The next board meeting is scheduled for 14 December 2026 at 10:00 AM, location TBC."),
     ("h2", "8. Adjournment"),
     ("body", "The meeting was adjourned at 1:47 PM. Minutes prepared by Aisha Al Blooshi, reviewed and approved by Chair Khalid Alsoodi on 18 September 2026.")],
    subtitle="Confidential — Board Members & Executives Only · 15 September 2026")
log(True, "02_Q3_Board_Meeting_Minutes.docx")

write_pptx("03_Group_Strategy_2026-2027.pptx",
    "Seekra Media Holdings — Group Strategy 2026-2027",
    [{"title": "Executive Summary", "body": [
        "- Group revenue target: AED 1.05 billion by FY2027 (from AED 880M in FY2025)",
        "- EBITDA margin expansion: 22% to 26% via shared services consolidation",
        "- Headcount growth: 612 to 780 FTEs across four subsidiaries",
        "- Three strategic pillars: Content Leadership, Operational Excellence, Regional Expansion"]},
     {"title": "Content Leadership", "body": [
        "- Produce 4 feature films and 2 documentary series per year",
        "- Build Seekra Originals IP library — target 12 owned titles by end of 2027",
        "- Establish Seekra Films as the #1 Arabic-language feature film studio in the GCC",
        "- Partnership pipeline: Netflix MENA, StarzPlay, Shahid, OSN"]},
     {"title": "Operational Excellence", "body": [
        "- Consolidate post-production at Seekra Studios Jebel Ali facility",
        "- Implement AI-driven content intelligence platform (Seekra internal deployment)",
        "- Reduce average film post-production cycle from 18 weeks to 12 weeks",
        "- Shared services: HR, Finance, Legal, IT — AED 14M annual savings target"]},
     {"title": "Regional Expansion", "body": [
        "- Open Seekra Creative Riyadh office (Q1 2027) — Saudi Vision 2030 opportunity",
        "- Acquire 51% stake in Arabian Post House (VFX) — board approved Q3 2026",
        "- Evaluate Egyptian content production partnership (Cairo) — feasibility Q4 2026",
        "- Broadcast streaming launch: Q3 2027 — Seekra Play OTT platform"]},
     {"title": "Financial Projections", "body": [
        "- FY2026E: Revenue AED 920M, EBITDA AED 200M, Net Debt/EBITDA 1.8x",
        "- FY2027E: Revenue AED 1,050M, EBITDA AED 273M, Net Debt/EBITDA 1.4x",
        "- Capex plan: AED 95M over 2 years (Studios expansion + OTT platform)",
        "- Funding: 60% operating cash flow, 25% project finance, 15% strategic investor"]},
     {"title": "Key Risks & Mitigations", "body": [
        "- Talent retention: Implement long-term incentive plan (LTIP) Q4 2026",
        "- Content piracy: Blockchain watermarking + legal enforcement unit",
        "- Regulatory changes: Active engagement with UAE Media Council and DCD",
        "- FX exposure: 75% of revenue in AED; natural hedge on USD-denominated capex"]},
     {"title": "Approval & Next Steps", "body": [
        "- Board approval requested: 15 September 2026",
        "- Detailed FY2026 operating plans due: 30 October 2026",
        "- FY2027 operating plans due: 30 March 2027",
        "- Quarterly strategy review at each board meeting"]}])
log(True, "03_Group_Strategy_2026-2027.pptx")

write_jpg("04_All_Hands_Team_Photo.jpg", "Annual All-Hands 2026",
          "DIFC Headquarters · 12 March 2026")
log(True, "04_All_Hands_Team_Photo.jpg")

# Group Finance (3)
print("\n=== Group Finance (3 docs) ===")
write_mp3("05_Q3_Earnings_Briefing.mp3",
    "Q3 2026 Earnings Briefing. This is Fatima Al Mansouri, Group Chief Financial Officer of Seekra Media Holdings. "
    "I am pleased to report our strongest quarter to date. Group revenue reached two hundred forty seven point eight million dirhams, "
    "an eighteen percent increase year over year. The films segment led growth with one hundred twelve point four million dirhams, "
    "driven primarily by pre-sales of Project Golden Falcon to Netflix MENA and StarzPlay. "
    "EBITDA margin improved to twenty two point four percent from nineteen point one percent in Q2, "
    "reflecting strong cost discipline across all four subsidiaries. "
    "Free cash flow was thirty eight point six million dirhams, of which twenty five million has been allocated to the Project Golden Falcon completion reserve. "
    "We are raising full year guidance to nine hundred twenty million dirhams in revenue and two hundred million in EBITDA. "
    "Looking ahead, we expect Q4 to be even stronger, with the theatrical release of Project Golden Falcon scheduled for 18 December 2026. "
    "Thank you, and I will now hand over to the CEO for strategic questions.")
log(True, "05_Q3_Earnings_Briefing.mp3")

write_xlsx("06_Q3_Financial_Statements.xlsx", [
    {"name": "P&L Q3 2026",
     "headers": ["Line Item", "Q3 2026 (AED M)", "Q2 2026 (AED M)", "Q3 2025 (AED M)", "YoY %"],
     "rows": [
        ["Revenue — Films", "112.4", "84.2", "72.1", "+55.9%"],
        ["Revenue — Creative", "58.7", "52.1", "44.8", "+31.0%"],
        ["Revenue — Studios", "41.2", "38.9", "33.6", "+22.6%"],
        ["Revenue — Broadcast", "35.5", "33.8", "30.4", "+16.8%"],
        ["Total Revenue", "247.8", "209.0", "180.9", "+37.0%"],
        ["Cost of Services", "(165.4)", "(142.1)", "(128.7)", "+28.5%"],
        ["Gross Profit", "82.4", "66.9", "52.2", "+57.9%"],
        ["Gross Margin %", "33.3%", "32.0%", "28.9%", "+440 bps"],
        ["Operating Expenses", "(26.8)", "(27.1)", "(24.2)", "+10.7%"],
        ["EBITDA", "55.6", "39.8", "28.0", "+98.6%"],
        ["EBITDA Margin %", "22.4%", "19.1%", "15.5%", "+690 bps"],
        ["Depreciation & Amortization", "(8.2)", "(7.9)", "(6.4)", "+28.1%"],
        ["EBIT", "47.4", "31.9", "21.6", "+119.4%"],
        ["Finance Costs", "(3.8)", "(4.2)", "(3.6)", "+5.6%"],
        ["Net Profit Before Tax", "43.6", "27.7", "18.0", "+142.2%"],
        ["Corporate Tax (9%)", "(3.9)", "(2.5)", "(1.6)", "+143.8%"],
        ["Net Profit", "39.7", "25.2", "16.4", "+142.1%"]]},
    {"name": "Balance Sheet Snapshot",
     "headers": ["Item", "30 Sep 2026 (AED M)", "30 Jun 2026 (AED M)", "Change"],
     "rows": [
        ["Cash & Equivalents", "84.2", "62.1", "+22.1"],
        ["Trade Receivables", "94.8", "88.4", "+6.4"],
        ["Inventory (Work-in-Progress)", "67.5", "54.2", "+13.3"],
        ["Total Current Assets", "246.5", "204.7", "+41.8"],
        ["PP&E (net)", "188.4", "182.9", "+5.5"],
        ["Goodwill & Intangibles", "62.8", "62.8", "0.0"],
        ["Total Assets", "497.7", "450.4", "+47.3"],
        ["Trade Payables", "(42.6)", "(38.9)", "(3.7)"],
        ["Deferred Revenue", "(28.4)", "(24.1)", "(4.3)"],
        ["Long-term Debt", "(85.0)", "(87.5)", "2.5"],
        ["Total Equity", "341.7", "299.9", "+41.8"]]}])
log(True, "06_Q3_Financial_Statements.xlsx")

write_jpg("07_Budget_Review_Photo.jpg", "Q3 Budget Review Session",
          "Finance Department · 14 September 2026", bg_color=(250, 245, 235))
log(True, "07_Budget_Review_Photo.jpg")

# Group Legal & Compliance (4)
print("\n=== Group Legal & Compliance (4 docs) ===")
write_pdf("08_Master_Services_Agreement_MiraStudios.pdf",
    "Master Services Agreement — Mira Studios FZ-LLC",
    ["## Parties",
     "This Master Services Agreement (\"Agreement\") is entered into on 1 September 2026 by and between:",
     "**Seekra Films FZ-LLC**, a limited liability company incorporated in the Dubai Multi Commodities Centre (DMCC) under license number 36721, having its registered office at JLT Cluster X, Level 14, Dubai, United Arab Emirates (\"Client\"); and",
     "**Mira Studios FZ-LLC**, a limited liability company incorporated in the Dubai Studio City under license number 41287, having its registered office at Building 7, Dubai Studio City, Dubai, United Arab Emirates (\"Service Provider\").",
     "## 1. Services",
     "The Service Provider agrees to provide sound stage rental, lighting equipment, and on-set technical crew services for the production of the feature film tentatively titled \"Project Golden Falcon\" (the \"Production\"). Detailed service specifications, schedules, and pricing are set forth in Schedule A attached hereto.",
     "## 2. Term",
     "This Agreement commences on 1 September 2026 and continues until 31 December 2026, unless terminated earlier in accordance with Section 8 below. The term may be extended by mutual written agreement of the parties.",
     "## 3. Fees & Payment",
     "Client shall pay Service Provider a fixed fee of AED 4,250,000 (four million two hundred fifty thousand dirhams), payable in three installments: 30% upon signature, 40% upon commencement of principal photography, and 30% upon delivery of final invoice. All payments shall be made by wire transfer to:",
     "Mira Studios FZ-LLC · Bank: Emirates NBD · Account: AE070331234567890123456 · SWIFT: EBILAEAD023",
     "## 4. Confidentiality",
     "Each party shall hold in strict confidence all Confidential Information disclosed by the other party, including without limitation production schedules, talent agreements, financial terms, and creative materials. Confidentiality obligations survive termination for a period of seven (7) years.",
     "## 5. Intellectual Property",
     "All deliverables created under this Agreement, including all footage, sound recordings, and creative work, shall be deemed work-for-hire and the sole property of Client. Service Provider assigns all rights, title, and interest in such deliverables to Client upon creation.",
     "## 6. Insurance & Indemnification",
     "Service Provider shall maintain comprehensive general liability insurance of not less than AED 5,000,000 per occurrence and professional indemnity insurance of AED 2,000,000 in the aggregate. Each party shall indemnify the other against any third-party claims arising from its negligence or breach of this Agreement.",
     "## 7. Force Majeure",
     "Neither party shall be liable for any failure or delay in performance due to causes beyond its reasonable control, including acts of God, war, terrorism, civil unrest, government action, pandemic, or natural disaster. The affected party shall notify the other within 72 hours and use commercially reasonable efforts to resume performance.",
     "## 8. Termination",
     "Either party may terminate this Agreement for material breach upon 30 days written notice, provided the breaching party fails to cure such breach within the notice period. Client may terminate immediately for convenience upon payment of a termination fee equal to 15% of the unperformed contract value.",
     "## 9. Governing Law & Dispute Resolution",
     "This Agreement is governed by the laws of the United Arab Emirates. Any dispute shall be resolved through binding arbitration administered by the Dubai International Financial Centre Arbitration Centre (DIAC) under its Rules in force, seat Dubai, language English, three arbitrators.",
     "## 10. Signatures",
     "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.",
     "For Seekra Films FZ-LLC: Signed by Sara Al Kindy, Chief Executive Officer. Emirates ID 784-1985-1234567-8. Date: 1 September 2026.",
     "For Mira Studios FZ-LLC: Signed by Mira Hassan Bensaleh, Managing Director. Emirates ID 784-1988-9876543-2. Date: 1 September 2026."],
    subtitle="Restricted — Executed 1 September 2026 · DMCC Reference MA-2026-0892",
    metadata={"Effective Date": "1 September 2026",
              "Contract Value": "AED 4,250,000",
              "Term": "1 Sep 2026 to 31 Dec 2026",
              "Governing Law": "UAE Federal Law",
              "Arbitration": "DIAC, Dubai, 3 arbitrators"})
log(True, "08_Master_Services_Agreement_MiraStudios.pdf")

write_docx("09_Customer_Data_Protection_Policy.docx",
    "Customer Data Protection Policy",
    [("body", "Version 3.0 · Effective 1 October 2026 · Owner: Group Legal & Compliance"),
     ("h1", "1. Purpose & Scope"),
     ("body", "This policy establishes the requirements for the collection, processing, storage, and sharing of personal data within Seekra Media Holdings and its four subsidiaries (Seekra Films, Seekra Creative, Seekra Studios, and Seekra Broadcast). It is aligned with the UAE Federal Decree-Law No. 45 of 2021 regarding the Protection of Personal Data (PDPL) and the General Data Protection Regulation (GDPR) where applicable to EU data subjects."),
     ("h1", "2. Definitions"),
     ("body", "Personal Data: Any information relating to an identified or identifiable natural person, including but not limited to name, Emirates ID, passport number, contact details, biometric data, and online identifiers."),
     ("body", "Processing: Any operation performed on personal data, including collection, recording, storage, use, disclosure, and deletion."),
     ("body", "Data Subject: The natural person to whom the personal data relates."),
     ("h1", "3. Lawful Basis for Processing"),
     ("body", "Seekra processes personal data only where there is a lawful basis, including: (a) the data subject has given consent; (b) processing is necessary for performance of a contract; (c) processing is required by law; or (d) processing is in the legitimate interests of Seekra and does not override the rights of the data subject."),
     ("h1", "4. Data Minimization & Retention"),
     ("body", "Only the minimum personal data necessary for the stated purpose shall be collected. Personal data shall not be retained longer than necessary. Default retention periods: employee records — 7 years post-employment; customer contact data — 3 years post-relationship; financial transaction records — 10 years (per UAE Commercial Companies Law)."),
     ("h1", "5. Data Subject Rights"),
     ("body", "Data subjects have the right to: (a) be informed of processing; (b) access their personal data; (c) rectify inaccurate data; (d) erase their data (subject to legal retention); (e) restrict processing; (f) data portability; and (g) object to processing. Requests must be submitted to dpo@seekra-media.ae and will be actioned within 30 days."),
     ("h1", "6. Security Measures"),
     ("body", "Seekra implements technical and organizational measures including: AES-256 encryption at rest; TLS 1.3 in transit; role-based access control with least-privilege principle; multi-factor authentication for all privileged accounts; quarterly security audits; annual penetration testing; and immediate revocation of access upon employee departure."),
     ("body", "Personal data is processed only within the UAE unless explicit consent for cross-border transfer is obtained, in compliance with PDPL Article 22."),
     ("h1", "7. Breach Notification"),
     ("body", "Any suspected or confirmed data breach must be reported to the Data Protection Officer (dpo@seekra-media.ae) within 2 hours of discovery. The DPO shall assess severity and notify the UAE Data Office within 72 hours where required by PDPL Article 9. Affected data subjects shall be notified without undue delay where the breach is likely to result in high risk to their rights."),
     ("h1", "8. Data Protection Impact Assessment"),
     ("body", "A DPIA must be conducted prior to deploying any new technology or process that is likely to result in high risk to data subjects, including AI/ML systems processing personal data, biometric processing, large-scale monitoring, or cross-border data transfers."),
     ("h1", "9. Training & Awareness"),
     ("body", "All employees must complete mandatory data protection training upon joining and annually thereafter. The training is delivered via the Seekra Learning Portal and a passing score of 80% is required."),
     ("h1", "10. Governance & Review"),
     ("body", "This policy is owned by the Group Chief Compliance Officer and reviewed annually by the Board Audit & Risk Committee. The next scheduled review is 1 October 2027.")],
    subtitle="Confidential — All Staff · Aligned with UAE PDPL & GDPR")
log(True, "09_Customer_Data_Protection_Policy.docx")

write_docx("10_Internal_Policies_Arabic.docx",
    "السياسات الداخلية للموظفين",
    [("body", "الإصدار 3.0 · ساري المفعول من 1 أكتوبر 2026 · المالك: الإدارة القانونية والامتثال"),
     ("h1", "1. الغرض والنطاق"),
     ("body", "تحدد هذه الوثيقة السياسات الداخلية لشركة سيكرا القابضة للإعلام وشركاتها التابعة الأربع (سيكرا للأفلام، سيكرا كرييتيف، سيكرا استوديوهات، سيكرا للبث). تهدف هذه السياسات إلى ضمان الامتثال لقوانين دولة الإمارات العربية المتحدة وتوفير بيئة عمل آمنة ومنتجة لجميع الموظفين."),
     ("h1", "2. ساعات العمل والإجازات"),
     ("body", "ساعات العمل الرسمية هي من 9:00 صباحاً حتى 6:00 مساءً من الأحد إلى الخميس، مع استراحة غداء مدتها ساعة واحدة. الإجازة السنوية المستحقة هي 30 يوماً تقويمياً عن كل سنة خدمة. تنظم الإجازات المرضية بموجب قانون العمل الإماراتي (المرسوم بقانون اتحادي رقم 33 لسنة 2021)."),
     ("h1", "3. السلوك المهني"),
     ("body", "يُتوقع من جميع الموظفين الالتزام بأعلى المعايير الأخلاقية والمهنية. يشمل ذلك الاحترام المتبادل، والحفاظ على السرية، وتجنب تضارب المصالح. يجب الإفصاح عن أي تضارب محتمل للمصالح كتابياً إلى قسم الامتثال خلال 14 يوماً من اكتشافه."),
     ("h1", "4. حماية البيانات"),
     ("body", "تلتزم سيكرا بحماية البيانات الشخصية وفقاً لمرسوم بقانون اتحادي رقم 45 لسنة 2021 بشأن حماية البيانات الشخصية. يجب على الموظفين التعامل مع جميع البيانات الشخصية بحذر شديد وعدم مشاركتها مع أطراف خارجية دون إذن كتابي صريح من الإدارة القانونية."),
     ("h1", "5. الصحة والسلامة"),
     ("body", "تتمتع سيكرا بنظام شامل للصحة والسلامة المهنية في جميع مرافقها. نقطة التجمع في حالة الطوارئ في المقر الرئيسي هي البوابة الثانية، الطابق الأول. على جميع الموظفين الإبلاغ عن أي حادث خلال 24 ساعة عبر بوابة الإبلاغ عن الحوادث."),
     ("h1", "6. السياسات المالية"),
     ("body", "يجب الحصول على موافقة مسبقة من المالية لجميع المصروفات التي تتجاوز 5,000 درهم. تُقدم تقارير المصروفات الشهرية قبل اليوم الخامس من الشهر التالي. تُعالج جميع المدفوعات عبر النظام المالي المعتمد (Oracle Cloud ERP)."),
     ("h1", "7. استخدام الموارد التقنية"),
     ("body", "أجهزة الكمبيوتر والإنترنت والبريد الإلكتروني هي ممتلكات الشركة ومخصصة للاستخدام المهني. يُحظر استخدامها لأغراض شخصية مفرطة أو لأنشطة غير قانونية. جميع البيانات المخزنة على أجهزة الشركة تخضع للمراقبة ويمكن الوصول إليها من قبل قسم تكنولوجيا المعلومات."),
     ("h1", "8. الإبلاغ عن المخالفات"),
     ("body", "يمكن للموظفين الإبلاغ عن أي مخالفات مشتبه بها بشكل سري عبر بوابة التحدث (Speak-Up) أو مباشرة إلى مسؤول الامتثال على compliance@seekra-media.ae. يتمتع المُبلّغون بحماية كاملة من الانتقام وفقاً لسياسة حماية المُبلّغين."),
     ("h1", "9. المراجعة والاعتماد"),
     ("body", "هذه السياسات مراجعة ومُعتمدة من مجلس الإدارة. المراجعة التالية المقررة في 1 أكتوبر 2027. أي تعديلات ستُتوثق وتُوزع على جميع الموظفين عبر البريد الإلكتروني وبوابة الموارد البشرية.")],
    subtitle="داخلي — لجميع الموظفين · متوافق مع قانون العمل الإماراتي")
log(True, "10_Internal_Policies_Arabic.docx")

write_xlsx("11_Employee_Passport_Roster.xlsx", [{
    "name": "Active Employees 2026",
    "headers": ["Employee ID", "Full Name (EN)", "Full Name (AR)", "Passport Number",
                "Emirates ID", "Nationality", "Date of Birth", "Position", "Department"],
    "rows": [
        ["S-1001", "Khalid Alsoodi", "خالد السودي", "P-AE7845123", "784-1985-1234567-8", "UAE", "12-Mar-1985", "Group CEO", "Group Executive"],
        ["S-1002", "Fatima Al Mansouri", "فاطمة المنصوري", "P-AE7892341", "784-1987-2345678-9", "UAE", "08-Jul-1987", "Group CFO", "Group Finance"],
        ["S-1003", "Omar Al Hashimi", "عمر الهاشمي", "P-AE7456789", "784-1984-3456789-0", "UAE", "23-Nov-1984", "Group Auditor", "Group Legal"],
        ["S-1004", "Sara Al Kindy", "سارة الكندي", "P-AE7123456", "784-1989-4567890-1", "UAE", "04-Feb-1989", "CEO Films", "Seekra Films"],
        ["S-1005", "Yousef Al Saedi", "يوسف السعيدي", "P-AE7234567", "784-1986-5678901-2", "UAE", "17-Jun-1986", "Creative Director", "Films · Direction"],
        ["S-1006", "Layla Al Mehrabi", "ليلى المهرابي", "P-AE7345678", "784-1990-6789012-3", "UAE", "29-Sep-1990", "Production Lead", "Films · Production"],
        ["S-1007", "Ahmed Al Ketbi", "أحمد الكتبي", "P-AE7456780", "784-1992-7890123-4", "UAE", "11-Dec-1992", "Production Assistant", "Films · Production"],
        ["S-1008", "Mira Hassan Bensaleh", "منى بن صالح", "P-MA8876543", "784-1988-9876543-2", "Morocco", "15-May-1988", "Studio Manager", "Mira Studios"],
        ["S-1009", "Reem Al Falasi", "ريم الفلاسي", "P-AE7567890", "784-1991-8901234-5", "UAE", "07-Jan-1991", "CEO Studios", "Seekra Studios"],
        ["S-1010", "Khalid Al Mazrouei", "خالد المزروعي", "P-AE7678901", "784-1993-9012345-6", "UAE", "19-Apr-1993", "VFX Artist", "Studios · VFX"]]}])
log(True, "11_Employee_Passport_Roster.xlsx")

print("\n" + "=" * 60)
print(f"PART 1 (docs 1-11): {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
