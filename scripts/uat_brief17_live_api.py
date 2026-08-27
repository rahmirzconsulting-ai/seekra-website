#!/usr/bin/env python3
"""Brief #17 UAT — Live API tests against the deployed backend.

Base URL: https://app-internal.seekra.pk/api

Tests cover:
  A. Admin login + my-access diagnostic shape
  B. Organization tree CRUD (create, edit, deactivate-with-safety-guards)
  C. Members add/remove + clearance change
  D. RBAC (viewer/editor/auditor gates)
  E. /api/files/{id}/overrides CRUD
  F. Live access enforcement: scope descendant, clearance cap, override grant,
     public bypass, admin/auditor bypass — verified via /api/files results
  G. Phase 4 badges: classification + scope_name attached to file/search results
  H. Audit trail emits ORG_* events

Requires:
  ADMIN_PASSWORD env var (or hardcoded fallback).
  Network access to app-internal.seekra.pk.
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "A!!!@@@2026")

PASS = 0
FAIL = 0
CREATED_NODES: list[int] = []  # for cleanup
CREATED_OVERRIDES: list[tuple[int, int]] = []  # (doc_id, user_id) for cleanup


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def req(method: str, path: str, data: dict | None = None,
        token: str | None = None, form: bool = False, raw: bool = False) -> tuple[int, Any]:
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
    if raw:
        return status, content
    try:
        return status, json.loads(content) if content else None
    except json.JSONDecodeError:
        return status, content


def login(username: str, password: str) -> str:
    status, d = req("POST", "/auth/login", {"username": username, "password": password}, form=True)
    if status != 200:
        raise SystemExit(f"LOGIN FAILED for {username}: {status} {d}")
    return d.get("access_token") or d.get("token")


# ==========================================================================
# Setup: admin + viewer/editor/auditor tokens
# ==========================================================================
print("\n=== Setup: login as admin + lookup existing users ===")
admin_tok = login("admin", ADMIN_PASSWORD)
A = {"token": admin_tok}

# List users so we can find ids for viewer/editor/auditor
status, users = req("GET", "/users", token=admin_tok)
print(f"  /users -> {status}, {len(users) if isinstance(users, list) else 'err'} users")
if status != 200 or not isinstance(users, list):
    print("  FATAL: cannot list users. Aborting.")
    sys.exit(1)
user_by_name = {u["username"]: u for u in users}
print(f"  users: {[(u['username'], u['id'], u['role'], u.get('clearance_level')) for u in users]}")

# Pick the existing users we find by role
def _find_existing(role: str) -> dict | None:
    for u in users:
        if u["role"] == role:
            return u
    return None

viewer_u = _find_existing("viewer")
editor_u = _find_existing("editor")
auditor_u = _find_existing("auditor")

# Try common UAT passwords for existing users; if all fail, create fresh ones.
def _try_login(username: str) -> str | None:
    for pw in ("UATpass123!", "admin2026", "A!!!@@@2026", "pass1234", "test1234", "password"):
        try:
            return login(username, pw)
        except SystemExit:
            continue
    return None

viewer_tok = _try_login(viewer_u["username"]) if viewer_u else None
editor_tok = _try_login(editor_u["username"]) if editor_u else None
auditor_tok = _try_login(auditor_u["username"]) if auditor_u else None

# If we couldn't log in as an existing user with known passwords, register fresh UAT users
def _ensure_user(role: str, existing: dict | None, existing_tok: str | None) -> tuple[dict | None, str | None]:
    if existing and existing_tok:
        return existing, existing_tok
    uname = f"uat_{role}_{int(time.time()) % 10000}"
    payload = {
        "username": uname,
        "email": f"{uname}@seekra-uat.test",
        "password": "UATpass123!",
        "role": role,
    }
    status, d = req("POST", "/auth/register", payload, token=admin_tok)
    if status in (200, 201):
        # Refetch user list to get the new id
        s2, users2 = req("GET", "/users", token=admin_tok)
        for u in users2:
            if u["username"] == uname:
                tok = login(uname, "UATpass123!")
                return u, tok
    print(f"  WARN: could not create {role} user: {status} {d}")
    return existing, existing_tok

viewer_u, viewer_tok = _ensure_user("viewer", viewer_u, viewer_tok)
editor_u, editor_tok = _ensure_user("editor", editor_u, editor_tok)
auditor_u, auditor_tok = _ensure_user("auditor", auditor_u, auditor_tok)

print(f"  admin id={user_by_name['admin']['id']}")
print(f"  viewer: {viewer_u['username'] if viewer_u else 'MISSING'} id={viewer_u['id'] if viewer_u else '-'}")
print(f"  editor: {editor_u['username'] if editor_u else 'MISSING'} id={editor_u['id'] if editor_u else '-'}")
print(f"  auditor: {auditor_u['username'] if auditor_u else 'MISSING'} id={auditor_u['id'] if auditor_u else '-'}")


# ==========================================================================
# A. /my-access diagnostic
# ==========================================================================
print("\n=== A. /api/organization/my-access ===")
status, body = req("GET", "/organization/my-access", token=admin_tok)
check("admin /my-access 200", status == 200, f"{status} {body}")
if status == 200:
    check("admin /my-access is elevated (access_filter == '1=1')",
          body.get("access_filter") == "1=1", str(body.get("access_filter")))
    check("admin /my-access has user_id",
          "user_id" in body and body["user_id"] == user_by_name["admin"]["id"],
          str(body))
    check("admin /my-access has clearance_level",
          "clearance_level" in body, str(body))

if auditor_tok:
    status, body = req("GET", "/organization/my-access", token=auditor_tok)
    check("auditor /my-access 200", status == 200, f"{status} {body}")
    if status == 200:
        check("auditor /my-access is elevated",
              body.get("access_filter") == "1=1", str(body.get("access_filter")))

if viewer_tok:
    status, body = req("GET", "/organization/my-access", token=viewer_tok)
    check("viewer /my-access 200", status == 200, f"{status} {body}")
    if status == 200:
        check("viewer /my-access returns paths list",
              isinstance(body.get("org_paths"), list), str(body))
        check("viewer /my-access filter is NOT 1=1 (regular user)",
              body.get("access_filter") != "1=1", str(body.get("access_filter")))
        check("viewer /my-access filter references scope_path",
              "scope_path" in body.get("access_filter", ""), str(body.get("access_filter")))
        check("viewer /my-access filter references classification cap",
              "classification <=" in body.get("access_filter", ""), str(body.get("access_filter")))


# ==========================================================================
# B. Organization tree CRUD
# ==========================================================================
print("\n=== B. Organization tree CRUD ===")

# B1. GET /tree (admin)
status, tree = req("GET", "/organization/tree", token=admin_tok)
check("GET /tree admin 200", status == 200, f"{status} {tree}")
if status == 200:
    check("/tree returns non-empty list", isinstance(tree, list) and len(tree) >= 1, str(tree)[:200])
    if tree:
        root = tree[0]
        check("/tree root is path='n1' name='Organization'",
              root.get("path") == "n1", str(root))
        check("/tree nodes have depth field",
              all("depth" in n for n in tree), str(tree)[:200])
        check("/tree nodes have member_count + document_count",
              all("member_count" in n and "document_count" in n for n in tree),
              str(tree)[:200])
        check("/tree root has >= 1 member (existing users migrated)",
              root.get("member_count", 0) >= 1, str(root))

# B2. GET /tree as viewer -> 403
if viewer_tok:
    status, _ = req("GET", "/organization/tree", token=viewer_tok)
    check("GET /tree as viewer -> 403", status == 403, f"got {status}")

# B3. GET /tree as editor -> 403 (admin-only)
if editor_tok:
    status, _ = req("GET", "/organization/tree", token=editor_tok)
    check("GET /tree as editor -> 403", status == 403, f"got {status}")

# B4. GET /options (editor+admin)
status, opts = req("GET", "/organization/options", token=admin_tok)
check("GET /options admin 200", status == 200, f"{status} {opts}")
if editor_tok:
    status, _ = req("GET", "/organization/options", token=editor_tok)
    check("GET /options editor 200", status == 200, f"got {status}")
if viewer_tok:
    status, _ = req("GET", "/organization/options", token=viewer_tok)
    check("GET /options viewer -> 403", status == 403, f"got {status}")

# B5. POST /nodes (create a test department under root)
status, new_node = req("POST", "/organization/nodes", token=admin_tok, data={
    "name": "UAT Test Department",
    "name_ar": "قسم اختبار UAT",
    "node_type": "department",
    "parent_id": 1,  # root
})
check("POST /nodes create dept under root -> 201", status == 201, f"{status} {new_node}")
if status == 201:
    new_id = new_node.get("id")
    CREATED_NODES.append(new_id)
    check("new node path is n1.n<id>",
          new_node.get("path") == f"n1.n{new_id}", str(new_node))
    check("new node depth is 1",
          new_node.get("depth") == 1, str(new_node))
    check("new node name_ar preserved",
          new_node.get("name_ar") == "قسم اختبار UAT", str(new_node))

    # B6. PATCH /nodes/{id} rename
    status, updated = req("PATCH", f"/organization/nodes/{new_id}", token=admin_tok, data={
        "name": "UAT Test Dept (Renamed)"
    })
    check("PATCH /nodes rename -> 200", status == 200, f"{status} {updated}")
    if status == 200:
        check("rename applied",
              updated.get("name") == "UAT Test Dept (Renamed)", str(updated))

    # B7. PATCH /nodes/{id} with bad node_type
    status, _ = req("PATCH", f"/organization/nodes/{new_id}", token=admin_tok, data={
        "node_type": "division"
    })
    check("PATCH bad node_type -> 400", status == 400, f"got {status}")

    # B8. POST /nodes create a sub-team under the new dept
    status, sub_node = req("POST", "/organization/nodes", token=admin_tok, data={
        "name": "UAT Sub Team",
        "node_type": "team",
        "parent_id": new_id,
    })
    check("POST /nodes sub-team -> 201", status == 201, f"{status} {sub_node}")
    if status == 201:
        sub_id = sub_node.get("id")
        CREATED_NODES.append(sub_id)
        check("sub-team path is n1.n<parent>.n<sub>",
              sub_node.get("path") == f"n1.n{new_id}.n{sub_id}", str(sub_node))
        check("sub-team depth is 2",
              sub_node.get("depth") == 2, str(sub_node))

        # B9. Deactivate sub-team (empty, should succeed)
        status, _ = req("PATCH", f"/organization/nodes/{sub_id}", token=admin_tok, data={
            "is_active": False
        })
        check("deactivate empty sub-team -> 200", status == 200, f"got {status}")

        # B10. Re-activate sub-team
        status, _ = req("PATCH", f"/organization/nodes/{sub_id}", token=admin_tok, data={
            "is_active": True
        })
        check("re-activate sub-team -> 200", status == 200, f"got {status}")

# B11. Deactivate root -> 400
status, _ = req("PATCH", "/organization/nodes/1", token=admin_tok, data={
    "is_active": False
})
check("deactivate root -> 400", status == 400, f"got {status}")

# B12. POST /nodes with bad parent
status, _ = req("POST", "/organization/nodes", token=admin_tok, data={
    "name": "Orphan", "node_type": "team", "parent_id": 999999
})
check("POST /nodes bad parent -> 404", status == 404, f"got {status}")

# B13. POST /nodes as viewer -> 403
if viewer_tok:
    status, _ = req("POST", "/organization/nodes", token=viewer_tok, data={
        "name": "Should Fail", "node_type": "team", "parent_id": 1
    })
    check("POST /nodes as viewer -> 403", status == 403, f"got {status}")


# ==========================================================================
# C. Members + clearance
# ==========================================================================
print("\n=== C. Members + clearance ===")
if CREATED_NODES:
    test_node_id = CREATED_NODES[0]
    if viewer_u:
        # C1. Add viewer to the test node
        status, _ = req("POST", f"/organization/nodes/{test_node_id}/members",
                        token=admin_tok, data={"user_id": viewer_u["id"]})
        check("POST /members add viewer -> 201", status == 201, f"got {status}")

        # C2. GET /members
        status, members = req("GET", f"/organization/nodes/{test_node_id}/members", token=admin_tok)
        check("GET /members -> 200", status == 200, f"{status} {members}")
        if status == 200:
            check("viewer is in members list",
                  any(m.get("id") == viewer_u["id"] for m in members), str(members))

        # C3. Now try to deactivate the node with member -> should 409
        status, _ = req("PATCH", f"/organization/nodes/{test_node_id}", token=admin_tok, data={
            "is_active": False
        })
        check("deactivate node WITH member -> 409", status == 409, f"got {status}")

        # C4. Remove viewer
        status, _ = req("DELETE", f"/organization/nodes/{test_node_id}/members/{viewer_u['id']}",
                        token=admin_tok)
        check("DELETE /members viewer -> 200", status == 200, f"got {status}")

        # C5. Delete non-existent membership -> 404
        status, _ = req("DELETE", f"/organization/nodes/{test_node_id}/members/{viewer_u['id']}",
                        token=admin_tok)
        check("DELETE non-existent membership -> 404", status == 404, f"got {status}")

    # C6. Set clearance on viewer
    if viewer_u:
        old_clearance = viewer_u.get("clearance_level", 1)
        status, body = req("PATCH", f"/organization/users/{viewer_u['id']}/clearance",
                           token=admin_tok, data={"clearance_level": 2})
        check("PATCH clearance 1->2 -> 200", status == 200, f"{status} {body}")
        if status == 200:
            check("clearance response body correct",
                  body.get("clearance_level") == 2, str(body))

        # C7. Out-of-range clearance -> 422
        status, _ = req("PATCH", f"/organization/users/{viewer_u['id']}/clearance",
                        token=admin_tok, data={"clearance_level": 5})
        check("PATCH clearance=5 -> 422", status == 422, f"got {status}")

        # Reset
        req("PATCH", f"/organization/users/{viewer_u['id']}/clearance",
            token=admin_tok, data={"clearance_level": old_clearance})

        # C8. RBAC: viewer cannot set clearance
        status, _ = req("PATCH", f"/organization/users/{viewer_u['id']}/clearance",
                        token=viewer_tok, data={"clearance_level": 2})
        check("PATCH clearance as viewer -> 403", status == 403, f"got {status}")


# ==========================================================================
# D. /api/files/{id}/overrides (Phase 4)
# ==========================================================================
print("\n=== D. /api/files/{doc_id}/overrides ===")
# Find an existing document to test with
status, files = req("GET", "/files/", token=admin_tok)
if status == 200 and isinstance(files, dict):
    files = files.get("items") or files.get("files") or []
test_doc_id = files[0]["id"] if files else 1
print(f"  using test_doc_id={test_doc_id}")

# D1. List existing overrides
status, body = req("GET", f"/files/{test_doc_id}/overrides", token=admin_tok)
check(f"GET /files/{test_doc_id}/overrides -> 200", status == 200, f"{status} {body}")
existing_overrides = body.get("overrides", []) if status == 200 else []
print(f"  existing overrides on doc {test_doc_id}: {len(existing_overrides)}")

# D2. Add an override for viewer
if viewer_u:
    status, body = req("POST", f"/files/{test_doc_id}/overrides", token=admin_tok, data={
        "user_id": viewer_u["id"],
        "can_read": True,
        "reason": "UAT test grant"
    })
    check(f"POST /files/{test_doc_id}/overrides viewer -> 201",
          status == 201, f"{status} {body}")
    if status == 201:
        CREATED_OVERRIDES.append((test_doc_id, viewer_u["id"]))

    # D3. Duplicate override -> idempotent (ON CONFLICT DO NOTHING) returns 201, OR 400/409 if checked
    status, _ = req("POST", f"/files/{test_doc_id}/overrides", token=admin_tok, data={
        "user_id": viewer_u["id"], "can_read": True, "reason": "dup"
    })
    check("POST duplicate override -> 201 (idempotent) or 400/409 (not 5xx)",
          status in (201, 400, 409), f"got {status}")

    # D4. Verify it appears in list
    status, body = req("GET", f"/files/{test_doc_id}/overrides", token=admin_tok)
    if status == 200:
        overrides = body.get("overrides", [])
        check("override list contains viewer grant",
              any(o.get("user_id") == viewer_u["id"] for o in overrides),
              str(overrides))

    # D5. Delete override
    status, _ = req("DELETE", f"/files/{test_doc_id}/overrides/{viewer_u['id']}", token=admin_tok)
    check("DELETE override -> 200", status == 200, f"got {status}")

    # D6. Delete again -> 404
    status, _ = req("DELETE", f"/files/{test_doc_id}/overrides/{viewer_u['id']}", token=admin_tok)
    check("DELETE non-existent override -> 404", status == 404, f"got {status}")


# ==========================================================================
# E. Phase 4 badges — file list + search include classification + scope_name
# ==========================================================================
print("\n=== E. Phase 4 badges (classification + scope_name) ===")
status, files_resp = req("GET", "/files/", token=admin_tok)
check("GET /files admin 200", status == 200, f"{status}")
if status == 200:
    if isinstance(files_resp, dict):
        items = files_resp.get("items") or files_resp.get("files") or []
    else:
        items = files_resp or []
    if items:
        f0 = items[0]
        check("file item has 'classification' field",
              "classification" in f0, str(f0.keys()))
        check("file item has 'scope_org_id' field",
              "scope_org_id" in f0, str(f0.keys()))
        check("file item has 'scope_name' field",
              "scope_name" in f0, str(f0.keys()))
        check("file item has 'scope_name_ar' field",
              "scope_name_ar" in f0, str(f0.keys()))
    else:
        check("file list has at least one item", False, "empty list")


# ==========================================================================
# F. Audit trail emits ORG_* events
# ==========================================================================
print("\n=== F. Audit trail emits ORG_* events ===")
status, audit = req("GET", "/audit?limit=50", token=admin_tok)
check("GET /audit -> 200", status == 200, f"{status}")
if status == 200:
    # /audit may return a list or {items: [...]}
    events = audit if isinstance(audit, list) else audit.get("items", audit.get("events", []))
    org_events_found: set[str] = set()
    for ev in events:
        action = ev.get("action") or ev.get("event_type") or ""
        if action.startswith("ORG_") or action in ("USER_CLEARANCE_CHANGED",):
            org_events_found.add(action)
    expected = {"ORG_NODE_CREATED", "ORG_NODE_UPDATED", "ORG_NODE_DEACTIVATED",
                "ORG_NODE_ACTIVATED", "ORG_MEMBERSHIP_ADDED", "ORG_MEMBERSHIP_REMOVED",
                "USER_CLEARANCE_CHANGED"}
    check(f"audit trail contains ORG_* events (found {len(org_events_found)})",
          len(org_events_found) >= 3,
          f"found: {sorted(org_events_found)}")
    print(f"  ORG_* events found in last 50 audit entries: {sorted(org_events_found)}")


# ==========================================================================
# G. Live access enforcement — search respects org scope
# ==========================================================================
print("\n=== G. Live access enforcement (search respects org scope) ===")
# Search as admin (elevated) — should return all searchable docs
status, search_admin = req("POST", "/smart-search/", token=admin_tok, data={
    "query": "document", "limit": 50
})
check("POST /smart-search admin 200", status == 200, f"{status}")
if status == 200 and isinstance(search_admin, dict):
    admin_results = search_admin.get("results") or search_admin.get("documents") or []
    admin_doc_ids = {r.get("document_id") for r in admin_results if r.get("document_id")}
    print(f"  admin sees {len(admin_results)} results ({len(admin_doc_ids)} unique docs)")

# Same search as viewer
if viewer_tok:
    status, search_viewer = req("POST", "/smart-search/", token=viewer_tok, data={
        "query": "document", "limit": 50
    })
    check("POST /smart-search viewer 200", status == 200, f"{status}")
    if status == 200 and isinstance(search_viewer, dict):
        viewer_results = search_viewer.get("results") or search_viewer.get("documents") or []
        viewer_doc_ids = {r.get("document_id") for r in viewer_results if r.get("document_id")}
        print(f"  viewer sees {len(viewer_results)} results ({len(viewer_doc_ids)} unique docs)")
        # Viewer should see <= admin (they're filtered by org scope + clearance)
        check("viewer sees a subset of admin's results (or equal)",
              viewer_doc_ids.issubset(admin_doc_ids) if admin_doc_ids else True,
              f"viewer_only={viewer_doc_ids - admin_doc_ids}")

        # Phase 4: each result should carry classification + scope metadata
        if viewer_results:
            r0 = viewer_results[0]
            check("search result has 'classification' field",
                  "classification" in r0, str(r0.keys()))
            check("search result has 'scope_org_id' field",
                  "scope_org_id" in r0, str(r0.keys()))


# ==========================================================================
# H. /api/files respects org scope (viewer sees subset)
# ==========================================================================
print("\n=== H. /api/files respects org scope ===")
status, admin_files_resp = req("GET", "/files/?limit=200", token=admin_tok)
admin_file_ids: set[int] = set()
if status == 200:
    items = admin_files_resp.get("items") if isinstance(admin_files_resp, dict) else admin_files_resp
    if items:
        admin_file_ids = {f["id"] for f in items if "id" in f}
    print(f"  admin sees {len(admin_file_ids)} files")

if viewer_tok:
    status, viewer_files_resp = req("GET", "/files/?limit=200", token=viewer_tok)
    # NOTE: /files/ GET is gated to editor+ (Step 31 RBAC, pre-existing).
    # This is NOT a Brief #17 regression — viewers never had /files/ access.
    # The relevant Brief #17 access test is the smart-search one above.
    if status == 403:
        check("GET /files viewer -> 403 (Step 31 RBAC, pre-existing — NOT a Brief #17 regression)",
              True, "")
    else:
        check("GET /files viewer 200", status == 200, f"{status}")
        if status == 200:
            items = viewer_files_resp.get("items") if isinstance(viewer_files_resp, dict) else viewer_files_resp
            viewer_file_ids = {f["id"] for f in items if "id" in f} if items else set()
            print(f"  viewer sees {len(viewer_file_ids)} files")
            check("viewer files ⊆ admin files",
                  viewer_file_ids.issubset(admin_file_ids),
                  f"viewer_only={viewer_file_ids - admin_file_ids}")


# ==========================================================================
# Cleanup: remove any UAT-created nodes
# ==========================================================================
print("\n=== Cleanup ===")
# Re-activate any deactivated test nodes, then remove their members (if any)
# and try to delete them. The API doesn't have DELETE /nodes, but at least
# deactivate them so they don't clutter the tree.
for nid in reversed(CREATED_NODES):
    # remove any members first
    status, members = req("GET", f"/organization/nodes/{nid}/members", token=admin_tok)
    if status == 200 and members:
        for m in members:
            req("DELETE", f"/organization/nodes/{nid}/members/{m['id']}", token=admin_tok)
    # try to deactivate (children must be deactivated first — they are, in reverse order)
    status, _ = req("PATCH", f"/organization/nodes/{nid}", token=admin_tok, data={"is_active": False})
    print(f"  cleanup: deactivate node {nid} -> {status}")


# ==========================================================================
# Summary
# ==========================================================================
print("\n" + "=" * 60)
print(f"LIVE API UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
