#!/usr/bin/env python3
"""Upload all 32 demo documents to the Seekra backend with proper
scope_org_id + classification.

Reads /api/organization/options to map department names to IDs,
then uploads each file via multipart POST to /api/files/upload.

The upload endpoint accepts scope_org_id + classification form fields
(Brief #17 Phase 2).
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"
DOCS_DIR = Path("/home/z/my-project/scripts/demo_docs")

# Mapping: filename -> (dept_name, classification)
# classification: 0 public, 1 internal, 2 confidential, 3 restricted
DOC_MAPPING = {
    "01_Employee_Handbook_2026.pdf":               ("Group Executive", 1),
    "02_Q3_Board_Meeting_Minutes.docx":            ("Group Executive", 2),
    "03_Group_Strategy_2026-2027.pptx":            ("Group Executive", 3),
    "04_All_Hands_Team_Photo.jpg":                 ("Group Executive", 0),
    "05_Q3_Earnings_Briefing.mp3":                 ("Group Finance", 3),
    "06_Q3_Financial_Statements.xlsx":             ("Group Finance", 3),
    "07_Budget_Review_Photo.jpg":                  ("Group Finance", 2),
    "08_Master_Services_Agreement_MiraStudios.pdf":("Group Legal & Compliance", 3),
    "09_Customer_Data_Protection_Policy.docx":     ("Group Legal & Compliance", 2),
    "10_Internal_Policies_Arabic.docx":            ("Group Legal & Compliance", 1),
    "11_Employee_Passport_Roster.xlsx":            ("Group Legal & Compliance", 3),
    "12_Golden_Falcon_Script_v3.pdf":              ("Films · Creative Direction", 2),
    "13_Golden_Falcon_Creative_Treatment.pptx":    ("Films · Creative Direction", 2),
    "14_Director_Vision_Notes.txt":                ("Films · Creative Direction", 2),
    "15_Golden_Falcon_Budget_Breakdown.xlsx":      ("Films · Production", 3),
    "16_Daily_Call_Sheet_2026-09-15.pdf":          ("Films · Production", 1),
    "17_Scene12_Take3_OnSet.mp4":                  ("Films · Production", 2),
    "18_Field_Audio_Update_Day4.mp3":              ("Films · Production", 2),
    "19_Films_Vendor_Invoices.csv":                ("Films · Finance & Admin", 2),
    "20_Films_Payroll_October_2026.xlsx":          ("Films · Finance & Admin", 3),
    "21_Emirates_Advertising_Awards_Brief.pdf":    ("Creative · Direction", 2),
    "22_Dubai_Tourism_Pitch_Deck.pptx":            ("Creative · Direction", 2),
    "23_Golden_Falcon_Logo_Concept.png":           ("Creative · Production", 0),
    "24_Branding_Display.jpg":                     ("Creative · Production", 0),
    "25_Active_Client_List.csv":                   ("Creative · Sales & Client Services", 3),
    "26_Dubai_Tourism_Contract.pdf":               ("Creative · Sales & Client Services", 2),
    "27_Warehouse_Safety_Procedures.docx":         ("Studios · Post-Production", 1),
    "28_Golden_Falcon_Edit_Schedule.xlsx":         ("Studios · Post-Production", 1),
    "29_VFX_Shot_List_Scene12.pdf":                ("Studios · VFX", 2),
    "30_Sound_Design_Brief.docx":                  ("Studios · Sound Design", 1),
    "31_City_Street_Stock_Footage.mp4":            ("Broadcast · Programming", 0),
    "32_Streaming_Distribution_Agreement.pdf":     ("Broadcast · Sales & Distribution", 3),
}

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  {detail}" if detail and not ok else ""))
    if ok: PASS += 1
    else: FAIL += 1


def login(username, password):
    body = urllib.parse.urlencode({"username": username, "password": password}).encode()
    r = urllib.request.Request(
        BASE + "/auth/login", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
        return json.loads(resp.read().decode())["access_token"]


def get_org_options(token):
    r = urllib.request.Request(
        BASE + "/organization/options",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
        return json.loads(resp.read().decode())


def upload_file(token, filepath: Path, scope_org_id: int, classification: int):
    """Upload a single file via curl (proven multipart implementation)."""
    import subprocess
    result = subprocess.run(
        [
            "curl", "-sk", "-X", "POST", BASE + "/files/upload",
            "-H", f"Authorization: Bearer {token}",
            "-F", f"file=@{filepath}",
            "-F", "folder=/",
            "-F", f"scope_org_id={scope_org_id}",
            "-F", f"classification={classification}",
        ],
        capture_output=True, text=True, timeout=300,
    )
    try:
        return 200 if result.returncode == 0 else 500, json.loads(result.stdout)
    except json.JSONDecodeError:
        return 500, result.stdout + result.stderr


print("=" * 60)
print("UPLOADING 32 DEMO DOCUMENTS")
print("=" * 60)

admin_tok = login("admin", ADMIN_PASSWORD)
print("admin login OK")

# Get org options to map dept_name -> node_id
opts = get_org_options(admin_tok)
node_id_by_name = {n["name"]: n["id"] for n in opts}
print(f"  found {len(node_id_by_name)} active org nodes")
print(f"  dept names available: {sorted(node_id_by_name.keys())}")

# Verify all dept names in DOC_MAPPING exist in the tree
missing_depts = set()
for fname, (dept, _) in DOC_MAPPING.items():
    if dept not in node_id_by_name:
        missing_depts.add(dept)
if missing_depts:
    print(f"  FATAL: missing departments in tree: {missing_depts}")
    sys.exit(1)
print("  all departments in DOC_MAPPING exist in org tree")

# Upload each document
print("\n=== Uploading documents ===")
uploaded_ids = []
for fname in sorted(DOC_MAPPING.keys()):
    dept, classification = DOC_MAPPING[fname]
    scope_id = node_id_by_name[dept]
    filepath = DOCS_DIR / fname
    if not filepath.exists():
        check(f"upload {fname}", False, "file not found locally")
        continue

    s, d = upload_file(admin_tok, filepath, scope_id, classification)
    # Response shape: {'uploaded': [{'id': ..., 'filename': ..., 'status': 'processing'}]}
    uploaded_list = d.get("uploaded", []) if isinstance(d, dict) else []
    if s == 200 and uploaded_list and "id" in uploaded_list[0]:
        check(f"upload {fname} -> {dept} (cls={classification})",
              True, f"id={uploaded_list[0]['id']}")
        uploaded_ids.append(uploaded_list[0]["id"])
    else:
        check(f"upload {fname}", False, f"{s} {d}")

    # Brief pause to avoid overwhelming the indexing pipeline
    time.sleep(1.5)

print(f"\n  uploaded {len(uploaded_ids)}/{len(DOC_MAPPING)} documents")

# Verify final state
print("\n=== Verify final state ===")
r = urllib.request.Request(
    BASE + "/files/?limit=200",
    headers={"Authorization": f"Bearer {admin_tok}"},
    method="GET",
)
with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
    files = json.loads(resp.read().decode())
all_docs = files if isinstance(files, list) else files.get("items", [])
print(f"  total documents in repository: {len(all_docs)}")
check("32 documents uploaded", len(all_docs) == 32, f"got {len(all_docs)}")

# Classification distribution
class_dist = {0: 0, 1: 0, 2: 0, 3: 0}
for f in all_docs:
    c = f.get("classification", 1) or 1
    class_dist[c] = class_dist.get(c, 0) + 1
print(f"  classification distribution: {class_dist}")
check("5 public docs", class_dist.get(0, 0) == 5, str(class_dist))
check("9 internal docs", class_dist.get(1, 0) == 9, str(class_dist))
check("12 confidential docs", class_dist.get(2, 0) == 12, str(class_dist))
check("6 restricted docs", class_dist.get(3, 0) == 6, str(class_dist))

print("\n" + "=" * 60)
print(f"UPLOAD COMPLETE: {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
sys.exit(1 if FAIL else 0)
