#!/usr/bin/env python3
"""Final verification of demo state — query each doc individually."""
import json, ssl, sys, urllib.request
BASE = "https://app-internal.seekra.pk/api"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
ADMIN_PASSWORD = "A!!!@@@2026"

# Login
body = urllib.parse.urlencode({"username":"admin","password":ADMIN_PASSWORD}).encode()
r = urllib.request.Request(BASE+"/auth/login", data=body,
    headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
    TOK = json.loads(resp.read().decode())["access_token"]

# Get list of all docs
r = urllib.request.Request(BASE+"/files/", headers={"Authorization":f"Bearer {TOK}"}, method="GET")
with urllib.request.urlopen(r, context=CTX, timeout=60) as resp:
    files = json.loads(resp.read().decode())
items = files if isinstance(files, list) else files.get("items", [])
print(f"Total docs: {len(items)}")

# Query each doc individually to get scope/classification
print(f"\n{'ID':4s}  {'Filename':42s}  {'Scope':35s}  {'Cls':3s}  {'PII':4s}  {'Status':10s}")
print("-" * 110)
class_dist = {0:0, 1:0, 2:0, 3:0}
scope_dist = {}
pii_count = 0
for f in sorted(items, key=lambda x: x['id']):
    did = f['id']
    r = urllib.request.Request(BASE+f"/files/{did}", headers={"Authorization":f"Bearer {TOK}"}, method="GET")
    with urllib.request.urlopen(r, context=CTX, timeout=30) as resp:
        doc = json.loads(resp.read().decode())
    scope = doc.get('scope_name') or 'None'
    cls = doc.get('classification')
    if cls is None: cls = -1
    pii = doc.get('pii_flagged', False)
    status = str(doc.get('status') or '?')
    class_dist[cls] = class_dist.get(cls, 0) + 1
    scope_dist[scope] = scope_dist.get(scope, 0) + 1
    if pii: pii_count += 1
    print(f"{did:4d}  {doc['filename'][:42]:42s}  {scope[:35]:35s}  {cls:3d}  {'Y' if pii else 'N':4s}  {status[:10]:10s}")

print(f"\n=== Summary ===")
print(f"Total documents: {len(items)}")
print(f"Classification distribution: {class_dist}")
print(f"Scope distribution:")
for s, n in sorted(scope_dist.items()):
    print(f"  {s}: {n}")
print(f"PII-flagged documents: {pii_count}")

# Expected
expected_class = {0: 5, 1: 9, 2: 12, 3: 6}
expected_total = 32
print(f"\n=== Verification ===")
print(f"Total = 32: {'PASS' if len(items) == expected_total else 'FAIL'} (got {len(items)})")
for c, expected in expected_class.items():
    actual = class_dist.get(c, 0)
    print(f"Class {c} = {expected}: {'PASS' if actual == expected else 'FAIL'} (got {actual})")
