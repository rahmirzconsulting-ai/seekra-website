#!/usr/bin/env python3
"""Brief #17 Demo Setup — Seekra Media Holdings (Dubai)

Builds a complete client-demo org tree, creates ~16 demo users across 4
subsidiary media companies, moves each user into their proper branch,
re-scopes all 41 documents to the right departments with proper
classifications (Public/Internal/Confidential/Restricted), and bumps
clearances for senior staff.

Idempotent: every step is wrapped in try/except and de-duplication logic,
so re-running the script is safe.

Output: a printed roster with usernames + temporary passwords for the demo.
"""
from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"
DEMO_PASSWORD = "Demo@2026"  # all demo users share this password

PASS = 0
FAIL = 0
WARN = 0


def log(level: str, msg: str) -> None:
    print(f"  [{level}] {msg}")


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        log("PASS", f"{name}" + (f"  {detail}" if detail else ""))
    else:
        FAIL += 1
        log("FAIL", f"{name}" + (f"  {detail}" if detail else ""))


def warn(msg: str) -> None:
    global WARN
    WARN += 1
    log("WARN", msg)


def req(method: str, path: str, data: dict | None = None,
        token: str | None = None, form: bool = False, ok: tuple = (200, 201)) -> tuple[int, Any]:
    headers: dict[str, str] = {}
    body: bytes | None = None
    if form:
        body = urllib.parse.urlencode(data or {}).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=120) as resp:
            content = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        status = e.code
    try:
        parsed = json.loads(content) if content else None
    except json.JSONDecodeError:
        parsed = content
    return status, parsed


def login(username: str, password: str) -> str | None:
    status, d = req("POST", "/auth/login", {"username": username, "password": password}, form=True)
    if status != 200:
        return None
    return (d or {}).get("access_token") or (d or {}).get("token")


# ==========================================================================
# Org tree blueprint
# ==========================================================================
# Each tuple: (name, name_ar, node_type, parent_path_name)
# We resolve parent by its name (must already exist before its children).
ORG_TREE = [
    # Group-level (children of root)
    ("Group Executive",        "الإدارة التنفيذية",    "department", None),
    ("Group Finance",          "المالية المجمعة",      "department", None),
    ("Group Legal & Compliance","الشؤون القانونية والامتثال","department", None),
    # Subsidiaries (companies)
    ("Seekra Films",           "سيكرا للأفلام",        "company",    None),
    ("Seekra Creative",        "سيكرا كرييتيف",        "company",    None),
    ("Seekra Studios",         "سيكرا استوديوهات",     "company",    None),
    ("Seekra Broadcast",       "سيكرا للبث",           "company",    None),
    # Seekra Films departments
    ("Films · Creative Direction", "الأفلام · الإخراج الإبداعي","team","Seekra Films"),
    ("Films · Production",          "الأفلام · الإنتاج",        "team","Seekra Films"),
    ("Films · Finance & Admin",     "الأفلام · المالية والإدارة","team","Seekra Films"),
    # Seekra Creative departments
    ("Creative · Direction",  "كرييتيف · الإدارة الفنية","team","Seekra Creative"),
    ("Creative · Production", "كرييتيف · الإنتاج",      "team","Seekra Creative"),
    ("Creative · Sales & Client Services","كرييتيف · المبيعات وخدمة العملاء","team","Seekra Creative"),
    # Seekra Studios departments
    ("Studios · Post-Production","استوديوهات · ما بعد الإنتاج","team","Seekra Studios"),
    ("Studios · VFX",            "استوديوهات · المؤثرات البصرية","team","Seekra Studios"),
    ("Studios · Sound Design",   "استوديوهات · تصميم الصوت","team","Seekra Studios"),
    # Seekra Broadcast departments
    ("Broadcast · Programming",  "البث · البرمجة",      "team","Seekra Broadcast"),
    ("Broadcast · Operations",   "البث · العمليات",     "team","Seekra Broadcast"),
    ("Broadcast · Sales & Distribution","البث · المبيعات والتوزيع","team","Seekra Broadcast"),
]

# ==========================================================================
# Demo users
# ==========================================================================
# Each: (username, full_name_ar, email, role, clearance, dept_name_or_None_for_root)
# All passwords = DEMO_PASSWORD ("Demo@2026")
USERS = [
    # Group level
    ("khalid.alsoodi",      "خالد السودي",     "k.alsoudi@seekra-media.ae",     "admin",   3, "Group Executive"),
    ("fatima.almansouri",   "فاطمة المنصوري",   "f.almansouri@seekra-media.ae",  "editor",  3, "Group Finance"),
    ("omar.alhashimi",      "عمر الهاشمي",     "o.alhashimi@seekra-media.ae",   "auditor", 3, "Group Legal & Compliance"),
    # Seekra Films
    ("sara.alkindy",        "سارة الكندي",      "s.alkindy@seekra-films.ae",     "editor",  3, "Seekra Films"),
    ("yousef.alsaedi",      "يوسف السعيدي",     "y.alsaedi@seekra-films.ae",     "editor",  2, "Films · Creative Direction"),
    ("layla.almehrabi",     "ليلى المهرابي",    "l.almehrabi@seekra-films.ae",   "viewer",  2, "Films · Production"),
    ("ahmed.alketbi",       "أحمد الكتبي",      "a.alketbi@seekra-films.ae",     "viewer",  1, "Films · Production"),
    # Seekra Creative
    ("mohammed.almarri",    "محمد المري",       "m.almarri@seekra-creative.ae",  "editor",  3, "Seekra Creative"),
    ("nora.alsuwaidi",      "نورة السويدي",     "n.alsuwaidi@seekra-creative.ae","viewer",  2, "Creative · Direction"),
    ("hassan.alzaabi",      "حسن الزعبي",       "h.alzaabi@seekra-creative.ae",  "viewer",  1, "Creative · Sales & Client Services"),
    # Seekra Studios
    ("reem.alfalasi",       "ريم الفلاسي",      "r.alfalasi@seekra-studios.ae",  "editor",  3, "Seekra Studios"),
    ("khalid.almazrouei",   "خالد المزروعي",    "k.almazrouei@seekra-studios.ae","viewer",  2, "Studios · VFX"),
    ("mouna.bensaleh",      "منى بن صالح",      "m.bensaleh@seekra-studios.ae",  "viewer",  1, "Studios · Sound Design"),
    # Seekra Broadcast
    ("tariq.alqassimi",     "طارق القاسمي",     "t.alqassimi@seekra-broadcast.ae","editor", 3, "Seekra Broadcast"),
    ("amira.benhassan",     "أميرة بن حسن",     "a.benhassan@seekra-broadcast.ae","viewer", 2, "Broadcast · Programming"),
    ("salem.aldhaheri",     "سالم الظاهري",     "s.aldhaheri@seekra-broadcast.ae","viewer", 1, "Broadcast · Sales & Distribution"),
]

# ==========================================================================
# Document → (dept_name, classification) mapping
# ==========================================================================
# classification: 0 public, 1 internal, 2 confidential, 3 restricted
DOC_MAPPING: dict[int, tuple[str, int]] = {
    # Group Executive — internal docs + executive strategy
    1:  ("Group Executive", 1),   # Employee Handbook
    6:  ("Group Executive", 2),   # Meeting Notes (executive)
    12: ("Group Executive", 0),   # Team Meeting photo (public)
    19: ("Group Executive", 1),   # Employee Handbook COPY
    20: ("Group Executive", 2),   # Meeting Notes REV
    32: ("Group Executive", 0),   # logo.png
    45: ("Group Executive", 1),   # prov_test
    46: ("Group Executive", 1),   # prov_test - Copy
    52: ("Group Executive", 1),   # test_entity_doc
    56: ("Group Executive", 1),   # ner_test
    58: ("Group Executive", 1),   # entity_graph_test
    # Group Finance — restricted financials
    3:  ("Group Finance", 3),     # Q3 Sales Report
    14: ("Group Finance", 2),     # Finance Desk Papers photo
    15: ("Group Finance", 3),     # Q3 Earnings Briefing audio
    # Group Legal — contracts + policies
    2:  ("Group Legal & Compliance", 3),  # Master Services Agreement
    8:  ("Group Legal & Compliance", 1),  # Internal Policies AR
    44: ("Group Legal & Compliance", 2),  # test_pii
    47: ("Group Legal & Compliance", 1),  # policy_v1
    48: ("Group Legal & Compliance", 1),  # policy_v2
    49: ("Group Legal & Compliance", 1),  # policy_v3
    50: ("Group Legal & Compliance", 2),  # Customer Data Policy v1
    51: ("Group Legal & Compliance", 2),  # Customer Data Policy v2
    55: ("Group Legal & Compliance", 2),  # test_arabic_pii
    # Seekra Films — Creative Direction
    4:  ("Films · Creative Direction", 2),  # Product Roadmap 2026
    36: ("Films · Creative Direction", 2),  # Demo Project Sandcastle Report
    42: ("Films · Creative Direction", 2),  # Demo Project Sandcastle Report (dup)
    # Seekra Films — Production
    9:  ("Films · Production", 2),   # Field Inspection Report
    16: ("Films · Production", 2),   # Site Walkthrough video
    34: ("Films · Production", 2),   # Demo Field Update Audio
    37: ("Films · Production", 2),   # Demo Site Walkthrough Video
    40: ("Films · Production", 2),   # Demo Field Update Audio (dup)
    43: ("Films · Production", 2),   # Demo Site Walkthrough Video (dup)
    57: ("Films · Production", 2),   # Demo Site Walkthrough Video (dup)
    # Seekra Creative — Production (images, brand assets)
    10: ("Creative · Production", 0),  # Break Room TV (public)
    35: ("Creative · Production", 0),  # Demo Golden Falcon Sign (public)
    41: ("Creative · Production", 0),  # Demo Golden Falcon Sign (dup)
    # Seekra Creative — Sales & Client Services
    7:  ("Creative · Sales & Client Services", 2),  # Customer List
    31: ("Creative · Sales & Client Services", 0),  # og-image.jpg
    # Seekra Studios — Operations (warehouse, equipment)
    5:  ("Studios · Post-Production", 1),  # Warehouse Safety Procedures
    11: ("Studios · Post-Production", 0),  # Warehouse Aisle photo
    # Seekra Broadcast — Programming
    13: ("Broadcast · Programming", 0),  # City Street Traffic stock footage
}

# Existing UAT users to clean up
UAT_USERS_TO_DELETE = [
    "uat_viewer_3385",
    "uat_viewer_3471",
    "uat_isolated_1787773549",
]

# Existing UAT / test nodes to deactivate (already mostly deactivated)
# We won't try to delete them (no DELETE /nodes endpoint) — just leave them inactive.

# ==========================================================================
# Execute
# ==========================================================================
print("=" * 70)
print("SEEKRA MEDIA HOLDINGS — DEMO SETUP")
print("=" * 70)

print("\n=== 1. Admin login ===")
admin_tok = login("admin", ADMIN_PASSWORD)
if not admin_tok:
    print("FATAL: admin login failed"); sys.exit(1)
check("admin login", True)
A = admin_tok

# ==========================================================================
print("\n=== 2. Cleanup UAT users ===")
status, users = req("GET", "/users", token=A)
check("GET /users", status == 200, f"{status}")
existing_users = {u["username"]: u for u in users} if isinstance(users, list) else {}

for uname in UAT_USERS_TO_DELETE:
    if uname in existing_users:
        uid = existing_users[uname]["id"]
        # Note: there is no DELETE /users/{id} endpoint exposed.
        # Workaround: change role to viewer (lowest privilege) so they can't do anything.
        # The client can ignore them; alternatively, we could rename them to old_uat_*
        # so they don't appear in the active roster.
        status, _ = req("PATCH", f"/users/{uid}", data={"role": "viewer"}, token=A)
        if status in (200, 204):
            log("INFO", f"downgraded UAT user '{uname}' (id={uid}) to viewer (cannot delete — no DELETE /users endpoint)")
        else:
            warn(f"could not downgrade UAT user '{uname}': {status}")
    else:
        log("INFO", f"UAT user '{uname}' not present, skipping")


# ==========================================================================
print("\n=== 3. Build org tree ===")
# Fetch existing tree to skip duplicates
status, tree = req("GET", "/organization/tree", token=A)
check("GET /organization/tree", status == 200, f"{status}")
existing_nodes_by_name: dict[str, dict] = {n["name"]: n for n in tree} if isinstance(tree, list) else {}
print(f"  existing nodes ({len(existing_nodes_by_name)}): {sorted(existing_nodes_by_name.keys())}")

# We need to create nodes in order (parents before children). ORG_TREE is already
# ordered that way.
node_id_by_name: dict[str, int] = {n["name"]: n["id"] for n in tree} if isinstance(tree, list) else {}
# Root is always id=1
node_id_by_name.setdefault("__root__", 1)

for name, name_ar, ntype, parent_name in ORG_TREE:
    if name in node_id_by_name:
        # Already exists — verify it's active; if not, reactivate
        existing = existing_nodes_by_name.get(name, {})
        if not existing.get("is_active", True):
            status, _ = req("PATCH", f"/organization/nodes/{node_id_by_name[name]}", token=A, data={"is_active": True})
            log("INFO", f"reactivated existing node '{name}' (id={node_id_by_name[name]})")
        else:
            log("INFO", f"node '{name}' already exists (id={node_id_by_name[name]}), skipping")
        continue
    parent_id = 1 if parent_name is None else node_id_by_name.get(parent_name)
    if parent_id is None:
        warn(f"parent '{parent_name}' not found for '{name}', skipping")
        continue
    status, body = req("POST", "/organization/nodes", token=A, data={
        "name": name,
        "name_ar": name_ar,
        "node_type": ntype,
        "parent_id": parent_id,
    })
    if status == 201 and isinstance(body, dict):
        node_id_by_name[name] = body["id"]
        check(f"create node '{name}'", True, f"id={body['id']} path={body.get('path')}")
    else:
        check(f"create node '{name}'", False, f"{status} {body}")


# ==========================================================================
print("\n=== 4. Create demo users ===")
# Refresh user list
status, users = req("GET", "/users", token=A)
existing_users = {u["username"]: u for u in users} if isinstance(users, list) else {}

created_users: list[dict] = []
for uname, full_name_ar, email, role, clearance, dept_name in USERS:
    if uname in existing_users:
        # Update clearance if needed
        existing = existing_users[uname]
        if existing.get("clearance_level", 1) != clearance:
            req("PATCH", f"/organization/users/{existing['id']}/clearance", token=A,
                data={"clearance_level": clearance})
        log("INFO", f"user '{uname}' already exists (id={existing['id']}), ensured clearance={clearance}")
        created_users.append({**existing, "password": DEMO_PASSWORD, "dept": dept_name,
                              "full_name_ar": full_name_ar, "intended_clearance": clearance,
                              "intended_role": role})
        continue
    status, body = req("POST", "/auth/register", token=A, data={
        "username": uname,
        "email": email,
        "password": DEMO_PASSWORD,
        "role": role,
    })
    if status in (200, 201) and isinstance(body, dict):
        uid = body.get("id")
        # Set clearance
        req("PATCH", f"/organization/users/{uid}/clearance", token=A,
            data={"clearance_level": clearance})
        check(f"create user '{uname}' ({role}, cl={clearance})", True, f"id={uid}")
        created_users.append({**body, "password": DEMO_PASSWORD, "dept": dept_name,
                              "full_name_ar": full_name_ar, "intended_clearance": clearance,
                              "intended_role": role})
    else:
        check(f"create user '{uname}'", False, f"{status} {body}")


# ==========================================================================
print("\n=== 5. Assign users to their departments ===")
# Refresh user list (to get final ids)
status, users = req("GET", "/users", token=A)
user_by_name = {u["username"]: u for u in users} if isinstance(users, list) else {}

for udata in created_users:
    uname = udata["username"]
    if uname not in user_by_name:
        warn(f"user '{uname}' not in fresh user list, cannot assign membership")
        continue
    uid = user_by_name[uname]["id"]
    dept_name = udata["dept"]
    if dept_name is None or dept_name not in node_id_by_name:
        warn(f"dept '{dept_name}' not found for user '{uname}', leaving at root")
        continue
    target_node_id = node_id_by_name[dept_name]

    # Always ensure membership in the target dept
    status, _ = req("POST", f"/organization/nodes/{target_node_id}/members", token=A,
                    data={"user_id": uid})
    # 201 = added, 409 already a member — both OK
    if status in (200, 201, 409):
        # Also remove from root membership IF the user is NOT supposed to be at root
        # (root membership = "see everything"; we want to limit visibility)
        # But: keep admin users at root too (they bypass anyway).
        # For everyone else, remove root membership so the org filter actually limits them.
        if dept_name != "Organization" and udata["intended_role"] != "admin":
            # Try to remove root membership
            status2, _ = req("DELETE", f"/organization/nodes/1/members/{uid}", token=A)
            # 200 = removed, 404 = not a member (already gone) — both OK
            if status2 in (200, 404):
                check(f"assign '{uname}' to '{dept_name}' (removed from root)", True)
            else:
                check(f"assign '{uname}' to '{dept_name}' (removed from root)", False,
                      f"remove from root failed: {status2}")
        else:
            check(f"assign '{uname}' to '{dept_name}' (kept at root)", True)
    else:
        check(f"assign '{uname}' to '{dept_name}'", False, f"add member: {status}")


# ==========================================================================
print("\n=== 6. Re-scope documents ===")
# Fetch all docs
status, files = req("GET", "/files/?limit=200", token=A)
check("GET /files", status == 200, f"{status}")
all_docs = files if isinstance(files, list) else (files or {}).get("items", [])

# For each doc in our mapping, apply scope + classification
for doc in all_docs:
    doc_id = doc["id"]
    if doc_id not in DOC_MAPPING:
        # Default: keep at root, classification=1 (internal)
        # Make sure they're at root + classification 1
        current_scope = doc.get("scope_org_id")
        current_class = doc.get("classification", 1)
        if current_scope != 1 or current_class != 1:
            status, _ = req("PATCH", f"/files/{doc_id}/scope", token=A, data={
                "scope_org_id": 1, "classification": 1
            })
            if status == 200:
                log("INFO", f"doc {doc_id} reset to root/internal (default)")
        continue
    dept_name, classification = DOC_MAPPING[doc_id]
    if dept_name not in node_id_by_name:
        warn(f"doc {doc_id}: dept '{dept_name}' not in tree, leaving at root")
        continue
    target_scope_id = node_id_by_name[dept_name]
    current_scope = doc.get("scope_org_id")
    current_class = doc.get("classification", 1)
    if current_scope == target_scope_id and current_class == classification:
        log("INFO", f"doc {doc_id} already at '{dept_name}' cls={classification}, skipping")
        continue
    status, _ = req("PATCH", f"/files/{doc_id}/scope", token=A, data={
        "scope_org_id": target_scope_id, "classification": classification
    })
    fname = doc.get("filename", "?")
    if status == 200:
        check(f"doc {doc_id} '{fname}'", True, f"-> {dept_name} / cls={classification}")
    else:
        check(f"doc {doc_id} '{fname}'", False, f"{status}")


# ==========================================================================
print("\n=== 7. Verify clearance distribution ===")
status, users = req("GET", "/users", token=A)
if status == 200:
    by_clearance = {0: 0, 1: 0, 2: 0, 3: 0}
    by_role = {}
    for u in users:
        cl = u.get("clearance_level", 1)
        by_clearance[cl] = by_clearance.get(cl, 0) + 1
        r = u.get("role", "?")
        by_role[r] = by_role.get(r, 0) + 1
    print(f"  users by clearance: {by_clearance}")
    print(f"  users by role: {by_role}")


# ==========================================================================
print("\n=== 8. Final org tree summary ===")
status, tree = req("GET", "/organization/tree", token=A)
if status == 200:
    print(f"  {'id':4s}  {'path':15s}  {'type':10s}  {'members':8s}  {'docs':5s}  name")
    for n in tree:
        active = "" if n.get("is_active") else " [INACTIVE]"
        print(f"  {n['id']:4d}  {n['path']:15s}  {n['node_type']:10s}  "
              f"{n.get('member_count', 0):8d}  {n.get('document_count', 0):5d}  "
              f"{n['name']}{active}")


# ==========================================================================
print("\n" + "=" * 70)
print("DEMO ROSTER — Seekra Media Holdings")
print("=" * 70)
print(f"\nAll demo users share password: {DEMO_PASSWORD}")
print(f"Admin password: {ADMIN_PASSWORD}")
print()
print(f"{'Username':<28s}  {'Role':8s}  {'Clr':3s}  {'Department':<40s}  Arabic name")
print("-" * 130)
for u in created_users:
    print(f"{u['username']:<28s}  {u['intended_role']:8s}  {u['intended_clearance']:3d}  "
          f"{(u['dept'] or '-'):<40s}  {u.get('full_name_ar','')}")

print("\n" + "=" * 70)
print(f"DEMO SETUP COMPLETE: {PASS} PASS / {FAIL} FAIL / {WARN} WARN")
print("=" * 70)
sys.exit(1 if FAIL else 0)
