#!/usr/bin/env python3
"""Archive legacy/test org nodes by renaming with 'ZZ Archived —' prefix.

The API has no DELETE /nodes endpoint, so we can't truly delete them.
Instead: rename with a clear archived prefix + ensure inactive, so they
sort to the bottom of the tree and are obviously leftovers.

This makes the client-demo tree visually clean.
"""
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"

# Nodes to archive (everything created before the demo setup)
LEGACY_NODE_IDS = [2, 3, 4, 5, 6, 7, 8, 9]


def req(method, path, data=None, token=None):
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content)
        except json.JSONDecodeError:
            return e.code, content


# Login
s, d = req("POST", "/auth/login",
           {"username": "admin", "password": ADMIN_PASSWORD},
           form=False) if False else (None, None)

# Use form encoding for login
import urllib.parse
body = urllib.parse.urlencode({"username": "admin", "password": ADMIN_PASSWORD}).encode()
r = urllib.request.Request(BASE + "/auth/login", data=body,
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            method="POST")
with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
    d = json.loads(resp.read().decode())
TOK = d["access_token"]
print(f"admin login OK")

print("\n=== Renaming legacy nodes ===")
for nid in LEGACY_NODE_IDS:
    # Get current node
    s, node = req("GET", f"/organization/tree", token=TOK)
    if s != 200:
        print(f"  FAIL  could not fetch tree: {s}")
        continue
    current = next((n for n in node if n["id"] == nid), None)
    if not current:
        print(f"  SKIP  node {nid} not found")
        continue
    old_name = current["name"]
    # Already archived?
    if old_name.startswith("ZZ Archived —"):
        print(f"  SKIP  node {nid} already archived: '{old_name}'")
        continue
    new_name = f"ZZ Archived — {old_name}"
    # PATCH
    s, body = req("PATCH", f"/organization/nodes/{nid}", token=TOK, data={"name": new_name})
    if s == 200:
        # Also ensure inactive
        if current.get("is_active"):
            s2, _ = req("PATCH", f"/organization/nodes/{nid}", token=TOK, data={"is_active": False})
            extra = f" + deactivated ({s2})"
        else:
            extra = " (already inactive)"
        print(f"  PASS  node {nid}: '{old_name}' -> '{new_name}'{extra}")
    else:
        print(f"  FAIL  node {nid}: {s} {body}")


# Final tree summary
print("\n=== Final org tree (clean demo view) ===")
s, tree = req("GET", "/organization/tree", token=TOK)
if s == 200:
    active = [n for n in tree if n.get("is_active")]
    archived = [n for n in tree if not n.get("is_active")]
    print(f"\n--- {len(active)} ACTIVE nodes (demo structure) ---")
    for n in sorted(active, key=lambda x: x["path"]):
        print(f"  id={n['id']:3d}  {n['path']:15s}  {n['node_type']:10s}  {n['name']}")
    print(f"\n--- {len(archived)} ARCHIVED nodes (legacy, sorted to bottom) ---")
    for n in sorted(archived, key=lambda x: x["name"]):
        print(f"  id={n['id']:3d}  {n['path']:15s}  {n['name']}")
