#!/usr/bin/env python3
"""Upload 32 demo docs with per-doc verification.

Uses curl via subprocess (proven to work in isolated tests).
After each upload, verifies scope_org_id + classification were saved
by querying GET /files/{id}. If verification fails, retries once.
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://app-internal.seekra.pk/api"
ADMIN_PASSWORD = "A!!!@@@2026"
DOCS_DIR = Path("/home/z/my-project/scripts/demo_docs")

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


def log(level, msg):
    print(f"  [{level}] {msg}")


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}" + (f"  {detail}" if detail else ""))


def login():
    body = urllib.parse.urlencode({"username": "admin", "password": ADMIN_PASSWORD}).encode()
    r = urllib.request.Request(
        BASE + "/auth/login", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    CTX = ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
        return json.loads(resp.read().decode())["access_token"]


def get_org_options(token):
    import ssl as _ssl
    CTX = _ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = _ssl.CERT_NONE
    r = urllib.request.Request(
        BASE + "/organization/options",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
        return json.loads(resp.read().decode())


def upload_via_curl(token, filepath: Path, scope_org_id: int, classification: int) -> tuple[int, dict]:
    """Upload via curl subprocess. Returns (http_status, response_json)."""
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
        body = json.loads(result.stdout)
        # Treat 200-style response (has 'uploaded' field) as success
        if "uploaded" in body:
            return 200, body
        # If body has 'detail' it's an error
        return 500, body
    except json.JSONDecodeError:
        return 500, {"raw": result.stdout[:500], "stderr": result.stderr[:500]}


def verify_doc(token, doc_id: int) -> dict | None:
    """Query GET /files/{doc_id} and return the parsed body."""
    import ssl as _ssl
    CTX = _ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = _ssl.CERT_NONE
    r = urllib.request.Request(
        BASE + f"/files/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def rescope_doc(token, doc_id: int, scope_org_id: int, classification: int) -> bool:
    """PATCH /files/{doc_id}/scope to set scope + classification explicitly."""
    body = json.dumps({"scope_org_id": scope_org_id, "classification": classification}).encode()
    import ssl as _ssl
    CTX = _ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = _ssl.CERT_NONE
    r = urllib.request.Request(
        BASE + f"/files/{doc_id}/scope",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=30) as resp:
            return resp.status == 200
    except Exception:
        return False


print("=" * 60)
print("UPLOADING 32 DEMO DOCS (with per-doc verification)")
print("=" * 60)

admin_tok = login()
print("admin login OK")

opts = get_org_options(admin_tok)
node_id_by_name = {n["name"]: n["id"] for n in opts}
print(f"  {len(node_id_by_name)} active org nodes")

print("\n=== Uploading documents ===")
uploaded_count = 0
for fname in sorted(DOC_MAPPING.keys()):
    dept, classification = DOC_MAPPING[fname]
    scope_id = node_id_by_name[dept]
    filepath = DOCS_DIR / fname

    # Upload
    s, d = upload_via_curl(admin_tok, filepath, scope_id, classification)
    if s != 200:
        check(f"upload {fname}", False, f"{s} {d}")
        continue

    doc_id = d["uploaded"][0]["id"]

    # Wait briefly for processing
    time.sleep(2)

    # Verify scope/classification were saved
    info = verify_doc(admin_tok, doc_id) or {}
    saved_scope = info.get("scope_org_id")
    saved_cls = info.get("classification")

    if saved_scope != scope_id or saved_cls != classification:
        # Fallback: explicitly PATCH /files/{id}/scope
        ok = rescope_doc(admin_tok, doc_id, scope_id, classification)
        if ok:
            time.sleep(1)
            info2 = verify_doc(admin_tok, doc_id) or {}
            saved_scope = info2.get("scope_org_id")
            saved_cls = info2.get("classification")
            if saved_scope == scope_id and saved_cls == classification:
                check(f"upload {fname}", True,
                      f"id={doc_id} scope={dept} cls={classification} (via PATCH fallback)")
                uploaded_count += 1
                continue
        check(f"upload {fname}", False,
              f"id={doc_id} but scope={saved_scope} (want {scope_id}) cls={saved_cls} (want {classification})")
    else:
        check(f"upload {fname}", True,
              f"id={doc_id} scope={dept} cls={classification}")
        uploaded_count += 1

print(f"\n  uploaded + verified: {uploaded_count}/32")

# Final summary
print("\n=== Final summary ===")
import ssl as _ssl
CTX = _ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = _ssl.CERT_NONE
r = urllib.request.Request(
    BASE + "/files/?limit=200",
    headers={"Authorization": f"Bearer {admin_tok}"},
    method="GET",
)
with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
    files = json.loads(resp.read().decode())
all_docs = files if isinstance(files, list) else files.get("items", [])
print(f"  total docs in repository: {len(all_docs)}")

class_dist = {0: 0, 1: 0, 2: 0, 3: 0}
scope_dist = {}
for f in all_docs:
    c = f.get("classification")
    if c is None:
        c = -1
    class_dist[c] = class_dist.get(c, 0) + 1
    s = f.get("scope_name") or "(none)"
    scope_dist[s] = scope_dist.get(s, 0) + 1
print(f"  classification distribution: {class_dist}")
print(f"  scope distribution:")
for s, n in sorted(scope_dist.items()):
    print(f"    {s}: {n}")

print("\n" + "=" * 60)
print(f"COMPLETE: {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
sys.exit(1 if FAIL else 0)
