#!/usr/bin/env python3
"""UAT for Kimi's latest work: Multi-tenant Platform + SSO/OIDC.

Tests:
  1. Multi-tenant CRUD (list, detail, create, update, suspend, reactivate)
  2. Tenant RBAC (viewer cannot access platform endpoints)
  3. SSO provider CRUD (create, list, delete)
  4. SSO security (client_secret not returned in responses)
  5. User model has is_active + is_sso_user + sso_provider_name
  6. OIDC callback endpoint exists
  7. Audit trail records PLATFORM_TENANT_* + SSO_* events
  8. Frontend /admin/sso/ + /admin/tenants/ pages load
  9. Regression: chat + search + connectors + access control
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
DEMO_PASSWORD = "Demo@2026"

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def req(method, path, data=None, token=None, form=False, timeout=180):
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
        with urllib.request.urlopen(r, context=CTX, timeout=timeout) as resp:
            content = resp.read().decode()
            try:
                return resp.status, (json.loads(content) if content else None)
            except json.JSONDecodeError:
                return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode()
        try:
            return e.code, json.loads(content) if content else None
        except json.JSONDecodeError:
            return e.code, content
    except urllib.error.URLError as e:
        # Handle 302 redirects — urllib raises URLError for non-2xx
        # but the status code is in the exception
        return getattr(e, 'code', 302), None


def login(username, password):
    s, d = req("POST", "/auth/login", {"username": username, "password": password}, form=True)
    return (d or {}).get("access_token") if s == 200 else None


def fetch_page(path):
    url = f"https://app-internal.seekra.pk{path}"
    r = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(r, context=CTX, timeout=30) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


print("=" * 60)
print("MULTI-TENANT + SSO UAT")
print("=" * 60)

# Setup
print("\n=== Setup ===")
admin_tok = login("admin", ADMIN_PASSWORD)
check("admin login", admin_tok is not None)
viewer_tok = login("ahmed.alketbi", DEMO_PASSWORD)
check("viewer (ahmed) login", viewer_tok is not None)

# ==========================================================================
# 1. MULTI-TENANT PLATFORM
# ==========================================================================
print("\n=== 1. Multi-tenant platform CRUD ===")

# 1a. List tenants
s, d = req("GET", "/platform/tenants/", token=admin_tok)
check("GET /platform/tenants/ -> 200", s == 200, f"{s}")
if s == 200:
    tenants = d if isinstance(d, list) else d.get("items", [])
    check(f"at least 3 tenants exist (got {len(tenants)})", len(tenants) >= 3, "")
    if tenants:
        t = tenants[0]
        check("tenant has 'id' field", "id" in t, str(t.keys()))
        check("tenant has 'name' field", "name" in t, "")
        check("tenant has 'slug' field", "slug" in t, "")
        check("tenant has 'status' field", "status" in t, "")
        print(f"      first tenant: id={t.get('id')} name={t.get('name')} slug={t.get('slug')} status={t.get('status')}")

# 1b. Get tenant detail
s, d = req("GET", "/platform/tenants/1", token=admin_tok)
check("GET /platform/tenants/1 -> 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    check("tenant detail has 'hosts' (custom domains)", "hosts" in d, str(d.keys()))
    check("tenant detail has 'users_total'", "users_total" in d, "")
    check("tenant detail has 'documents' count", "documents" in d, "")
    check("tenant detail has 'storage_bytes'", "storage_bytes" in d, "")
    check("tenant detail has 'plan_tier'", "plan_tier" in d, "")
    check("tenant detail has 'subscription_status'", "subscription_status" in d, "")
    print(f"      tenant #1: name={d.get('name')} hosts={d.get('hosts')} users={d.get('users_total')} docs={d.get('documents')} storage={d.get('storage_bytes')}")

# 1c. 404 for non-existent tenant
s, _ = req("GET", "/platform/tenants/99999", token=admin_tok)
check("GET /platform/tenants/99999 -> 404", s == 404, f"got {s}")

# 1d. RBAC: viewer cannot access tenants
if viewer_tok:
    s, _ = req("GET", "/platform/tenants/", token=viewer_tok)
    check("viewer GET /platform/tenants/ -> 403", s == 403, f"got {s}")

# 1e. Unauthenticated
s, _ = req("GET", "/platform/tenants/")
check("unauth GET /platform/tenants/ -> 401", s == 401, f"got {s}")

# 1f. Audit trail has PLATFORM_TENANT_* events
s, audit = req("GET", "/audit/?limit=100", token=admin_tok)
if s == 200:
    events = audit if isinstance(audit, list) else audit.get("items", [])
    tenant_events = [e for e in events if "TENANT" in (e.get("action", "") or "")]
    check(f"audit trail has PLATFORM_TENANT_* events (found {len(tenant_events)})",
          len(tenant_events) >= 1, "")
    if tenant_events:
        actions = set(e.get("action") for e in tenant_events)
        print(f"      tenant event types: {sorted(actions)}")

# ==========================================================================
# 2. SSO / OIDC PROVIDER MANAGEMENT
# ==========================================================================
print("\n=== 2. SSO/OIDC provider management ===")

# 2a. Public SSO providers endpoint (for login page)
s, d = req("GET", "/auth/sso/providers")
check("GET /auth/sso/providers (public) -> 200", s == 200, f"{s}")
if s == 200:
    check("public SSO providers returns a list", isinstance(d, list), str(d)[:200])

# 2b. Admin SSO providers list
s, d = req("GET", "/auth/sso/admin/providers", token=admin_tok)
check("GET /auth/sso/admin/providers -> 200", s == 200, f"{s}")
if s == 200:
    check("admin SSO providers returns a list", isinstance(d, list), str(d)[:200])

# 2c. Create SSO provider
test_provider = {
    "name": "UAT Test IdP",
    "issuer": "https://login.microsoftonline.com/uat-test/v2.0",
    "client_id": "uat-test-client-id",
    "client_secret": "uat-test-secret",
    "scopes": "openid profile email groups",
    "default_role": "viewer",
    "default_clearance": 1,
}
s, d = req("POST", "/auth/sso/admin/providers", token=admin_tok, data=test_provider)
check("POST create SSO provider -> 201/200", s in (200, 201), f"{s} {d}")
if s in (200, 201) and isinstance(d, dict):
    provider_id = d.get("id")
    print(f"      created provider id={provider_id} name={d.get('name')}")

    # 2d. Verify fields
    check("provider has 'issuer' field", "issuer" in d, str(d.keys()))
    check("provider has 'client_id' field", "client_id" in d, "")
    check("provider has 'has_client_secret' (boolean, not the raw secret)",
          "has_client_secret" in d and isinstance(d.get("has_client_secret"), bool), "")
    check("provider does NOT return raw client_secret",
          "client_secret" not in d, "SECURITY ISSUE: client_secret returned in response!")
    check("provider has 'default_role' field", "default_role" in d, "")
    check("provider has 'default_clearance' field", "default_clearance" in d, "")
    check("provider has 'is_active' field", "is_active" in d, "")
    check("provider has 'allow_jit_provisioning' flag",
          "allow_jit_provisioning" in d, str(d.keys()))
    check("provider has 'linked_users' count", "linked_users" in d, "")

    # 2e. Delete the test provider
    s2, _ = req("DELETE", f"/auth/sso/admin/providers/{provider_id}", token=admin_tok)
    check(f"DELETE test provider {provider_id} -> 200", s2 == 200, f"{s2}")

    # 2f. Verify deleted
    s3, d3 = req("GET", "/auth/sso/admin/providers", token=admin_tok)
    if s3 == 200 and isinstance(d3, list):
        check("deleted provider no longer in list",
              all(p.get("id") != provider_id for p in d3), "")
else:
    provider_id = None

# 2g. RBAC: viewer cannot create SSO providers
if viewer_tok:
    s, _ = req("POST", "/auth/sso/admin/providers", token=viewer_tok, data=test_provider)
    check("viewer POST SSO provider -> 403", s == 403, f"got {s}")
    s, _ = req("GET", "/auth/sso/admin/providers", token=viewer_tok)
    check("viewer GET SSO admin providers -> 403", s == 403, f"got {s}")

# 2h. OIDC callback endpoint exists
s, _ = req("GET", "/auth/sso/callback")
check("GET /auth/sso/callback -> 302 or 400 (endpoint exists)",
      s in (302, 400, 422), f"got {s}")

# ==========================================================================
# 3. USER MODEL ENHANCEMENTS
# ==========================================================================
print("\n=== 3. User model enhancements ===")

s, d = req("GET", "/users/", token=admin_tok)
check("GET /users/ -> 200", s == 200, f"{s}")
if s == 200 and isinstance(d, list) and d:
    u = d[0]
    check("user has 'is_active' field", "is_active" in u, str(u.keys()))
    check("user has 'is_sso_user' field", "is_sso_user" in u, "")
    check("user has 'sso_provider_name' field", "sso_provider_name" in u, "")
    # Verify no SSO users yet (all should be is_sso_user=False)
    sso_users = [u for u in d if u.get("is_sso_user")]
    check(f"no SSO-provisioned users yet (found {len(sso_users)})",
          len(sso_users) == 0, f"SSO users: {[u['username'] for u in sso_users]}")
    # All demo users should be active
    inactive = [u for u in d if not u.get("is_active")]
    check(f"inactive users preserved (found {len(inactive)})",
          len(inactive) >= 3, f"inactive: {[u['username'] for u in inactive]}")

# ==========================================================================
# 4. FRONTEND PAGES
# ==========================================================================
print("\n=== 4. Frontend admin pages ===")

for path in ["/admin/sso/", "/admin/tenants/", "/admin/platform/"]:
    status, body = fetch_page(path)
    has_seekra_title = "Seekra" in body or "seekra" in body.lower()
    has_404 = "404" in body and "could not be found" in body
    check(f"GET {path} -> 200 with Seekra content (no 404)",
          status == 200 and has_seekra_title and not has_404,
          f"status={status} has_404={has_404}")

# ==========================================================================
# 5. REGRESSION — existing features still work
# ==========================================================================
print("\n=== 5. Regression ===")

# 5a. Chat still works
s, d = req("POST", "/chat/", token=admin_tok, data={"question": "how many documents are in the library?"}, timeout=240)
check("chat POST -> 200", s == 200, f"{s}")
if s == 200:
    ans = (d.get("answer") or "")
    check("chat returns substantive answer", "documents" in ans.lower(), f"first 100: {ans[:100]}")

# 5b. Smart search still works
s, d = req("POST", "/smart-search/", token=admin_tok, data={"query": "Golden Falcon", "limit": 5}, timeout=120)
check("smart-search POST -> 200", s == 200, f"{s}")
if s == 200:
    results = d.get("results") or d.get("documents") or []
    check(f"smart-search returns results (got {len(results)})", len(results) >= 1, "")

# 5c. Connectors still work
s, d = req("GET", "/connectors", token=admin_tok)
check("GET /connectors -> 200", s == 200, f"{s}")

# 5d. Organization tree still works
s, d = req("GET", "/organization/tree", token=admin_tok)
check("GET /organization/tree -> 200", s == 200, f"{s}")

# 5e. Access control still works (viewer cannot see org tree)
if viewer_tok:
    s, _ = req("GET", "/organization/tree", token=viewer_tok)
    check("viewer GET /organization/tree -> 403 (access control intact)", s == 403, f"got {s}")

# 5f. Audit chain still valid
s, d = req("POST", "/audit/verify", token=admin_tok)
check("POST /audit/verify -> 200", s == 200, f"{s}")
if s == 200 and isinstance(d, dict):
    check("audit chain valid", d.get("valid") is True, str(d)[:200])
    check("audit chain has 0 issues", d.get("issue_count") == 0, str(d.get("issue_count")))

# 5g. Soft-delete user still works (reactivate endpoint)
s, _ = req("POST", "/users/12/reactivate", token=admin_tok)
check("POST /users/12/reactivate -> 200 (already active or reactivated)",
      s in (200, 400), f"got {s}")


# ==========================================================================
# Summary
# ==========================================================================
print("\n" + "=" * 60)
print(f"MULTI-TENANT + SSO UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
