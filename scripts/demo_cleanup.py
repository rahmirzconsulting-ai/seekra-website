#!/usr/bin/env python3
"""Demo cleanup: soft-delete 3 UAT users + hard-delete all existing documents.

Phase 6 soft-delete preserves audit trail; document delete is hard (via
existing DELETE /files/{doc_id} endpoint which removes MinIO object + DB row).
"""
from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"

UAT_USERS = ["uat_viewer_3385", "uat_viewer_3471", "uat_isolated_1787773549"]

PASS = FAIL = 0


def req(method, path, data=None, token=None, form=False):
    headers = {}
    body = None
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
        with urllib.request.urlopen(r, context=CTX, timeout=180) as resp:
            content = resp.read().decode()
            return resp.status, (json.loads(content) if content else None)
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content) if content else None
        except json.JSONDecodeError:
            return e.code, content


def login(username, password):
    s, d = req("POST", "/auth/login", {"username": username, "password": password}, form=True)
    if s != 200:
        raise SystemExit(f"login failed: {s} {d}")
    return d["access_token"]


def check(name, ok, detail=""):
    global PASS, FAIL
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  {detail}" if detail and not ok else ""))
    if ok: PASS += 1
    else: FAIL += 1


print("=" * 60)
print("DEMO CLEANUP")
print("=" * 60)

admin_tok = login("admin", ADMIN_PASSWORD)
print(f"admin login OK")

# --- 1. Soft-delete UAT users ---
print("\n=== 1. Soft-delete UAT users ===")
s, users = req("GET", "/users/", token=admin_tok)
check("GET /users/", s == 200, str(s))
user_by_name = {u["username"]: u for u in users} if isinstance(users, list) else {}

for uname in UAT_USERS:
    u = user_by_name.get(uname)
    if not u:
        print(f"  SKIP  {uname} not found")
        continue
    uid = u["id"]
    # If already deactivated, skip
    if not u.get("is_active", True):
        print(f"  SKIP  {uname} (id={uid}) already deactivated")
        continue
    s, d = req("DELETE", f"/users/{uid}", token=admin_tok)
    check(f"soft-delete {uname} (id={uid})",
          s == 200, f"{s} {d}")
    if s == 200:
        print(f"        -> deactivated (row preserved for audit)")

# --- 2. Delete all existing documents ---
print("\n=== 2. Delete all existing documents ===")
s, files = req("GET", "/files/?limit=200", token=admin_tok)
check("GET /files/", s == 200, str(s))
docs = files if isinstance(files, list) else (files or {}).get("items", [])
print(f"  found {len(docs)} documents to delete")

deleted = 0
errors = 0
for doc in docs:
    did = doc["id"]
    fname = doc.get("filename", "?")
    s, d = req("DELETE", f"/files/{did}", token=admin_tok)
    if s in (200, 204):
        deleted += 1
        if deleted % 10 == 0 or deleted == len(docs):
            print(f"  deleted {deleted}/{len(docs)}...")
    else:
        errors += 1
        print(f"  FAIL  doc {did} '{fname}': {s} {d}")
        time.sleep(0.5)

check(f"deleted {deleted}/{len(docs)} documents",
      deleted == len(docs), f"errors: {errors}")

# Final verify
print("\n=== Final state ===")
s, files = req("GET", "/files/?limit=200", token=admin_tok)
remaining = files if isinstance(files, list) else (files or {}).get("items", [])
print(f"  remaining documents: {len(remaining)}")
check("repository is empty", len(remaining) == 0, f"{len(remaining)} remain")

s, users = req("GET", "/users/", token=admin_tok)
active = [u for u in users if u.get("is_active", True)]
inactive = [u for u in users if not u.get("is_active", True)]
print(f"  active users: {len(active)}")
print(f"  inactive users: {len(inactive)} (preserved for audit)")
check("3 UAT users now inactive",
      sum(1 for u in inactive if u["username"] in UAT_USERS) == 3,
      f"{[u['username'] for u in inactive if u['username'] in UAT_USERS]}")

print("\n" + "=" * 60)
print(f"CLEANUP COMPLETE: {PASS} PASS / {FAIL} FAIL")
print("=" * 60)
sys.exit(1 if FAIL else 0)
