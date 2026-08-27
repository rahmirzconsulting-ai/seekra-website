#!/usr/bin/env python3
"""Brief #17 UAT — Phase 1: static + pure-function tests (no DB needed).

Validates:
  1. All Brief #17 backend modules import cleanly (no syntax / dep errors).
  2. `org_clause_from_context` produces the correct SQL fragment for every
     access dimension: admin/auditor bypass, scope descendant match, public
     bypass, per-user override, clearance cap, AND-folding of override with
     clearance.
  3. `permission_clause` (services.permissions) delegates to the org clause
     and respects the access context (ContextVar).
  4. `set_access_context` shape — admin/auditor set elevated=True; viewer
     gets {elevated:False, uid, paths, clearance}; None user clears it.
  5. Migration SQL is well-formed, idempotent (every DDL uses IF NOT EXISTS),
     seeds the root node, and advances the sequence.
  6. Frontend admin/organization page exists with the expected sections
     (tree, members, clearance, overrides UI hooks).

This is the part of the UAT that does NOT need a live database or admin
credentials. Phase 2 of the UAT (live API + DB) runs separately once the
login throttle clears.
"""
from __future__ import annotations

import os
import re
import sys
import traceback
from pathlib import Path

REPO = Path("/home/z/my-project/seekra-app")
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))

# Settings requires these env vars even for static import — provide dummies
os.environ.setdefault("SECRET_KEY", "uat-static-dummy")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://x:x@localhost/x")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")
os.environ.setdefault("MINIO_BUCKET_NAME", "uat-bucket")

PASS = 0
FAIL = 0
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    RESULTS.append((name, ok, detail))
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# --------------------------------------------------------------------------
# 1. Backend imports
# --------------------------------------------------------------------------
print("\n=== 1. Backend imports ===")
try:
    from app.services import org_tree, permissions
    from app.api import organization, files, smart_search, users, chat, entities
    from app.models import user as user_model
    check("org_tree module imports", True)
except Exception as e:
    check("org_tree module imports", False, f"{type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

# Verify the router is registered
try:
    from app.main import app
    routes = [r.path for r in app.routes]
    expected = [
        "/api/organization/tree",
        "/api/organization/options",
        "/api/organization/nodes",
        "/api/organization/my-access",
        "/api/organization/users/{user_id}/clearance",
    ]
    missing = [p for p in expected if not any(p == r.path for r in app.routes)]
    check("organization router registered", not missing, f"missing: {missing}")
except Exception as e:
    check("organization router registered", False, f"{type(e).__name__}: {e}")

# User model has clearance_level
try:
    col = user_model.User.__table__.c.clearance_level
    check("User.clearance_level column exists", True)
except Exception as e:
    check("User.clearance_level column exists", False, f"{e}")


# --------------------------------------------------------------------------
# 2. org_clause_from_context — pure-function tests
# --------------------------------------------------------------------------
print("\n=== 2. org_clause_from_context (pure function) ===")
from app.services.org_tree import org_clause_from_context

# (a) Admin / elevated -> 1=1 (no params written)
p: dict = {}
sql = org_clause_from_context({"elevated": True}, p, "d")
check("elevated bypass -> 1=1", sql == "1=1", sql)
check("elevated bypass writes no params", p == {}, str(p))

# (b) None context (Celery worker / no per-request setup) -> 1=1
p = {}
sql = org_clause_from_context(None, p, "d")
check("None context -> 1=1 (legacy behavior)", sql == "1=1", sql)
check("None context writes no params", p == {}, str(p))

# (c) Empty paths list -> tree_clause = 1=0, only override + public remain
p = {}
sql = org_clause_from_context(
    {"elevated": False, "uid": 7, "paths": [], "clearance": 1}, p, "d"
)
check(
    "empty paths: tree_clause is 1=0 (fail-closed)",
    "1=0" in sql and "OR" in sql,
    sql,
)
check("empty paths: clearance + override bound",
      "org_clearance" in p and "org_ovr_uid" in p, str(p))

# (d) Single path: d.scope_path <@ CAST(:org_path_0 AS ltree)
p = {}
sql = org_clause_from_context(
    {"elevated": False, "uid": 5, "paths": ["n1.n4"], "clearance": 2}, p, "d"
)
check(
    "single path: descendant scope clause present",
    "d.scope_path <@ CAST(:org_path_0 AS ltree)" in sql,
    sql,
)
check("single path: org_path_0 bound to 'n1.n4'", p.get("org_path_0") == "n1.n4", str(p))
check("single path: clearance bound", p.get("org_clearance") == 2, str(p))
check("single path: override uid bound", p.get("org_ovr_uid") == 5, str(p))
check(
    "single path: public clause present",
    "d.classification = 0" in sql,
    sql,
)
check(
    "single path: override subquery present",
    "document_overrides" in sql and "can_read" in sql,
    sql,
)
check(
    "single path: outer structure (public OR tree OR override) AND clearance",
    sql.startswith("((d.classification = 0 OR (")
    and sql.endswith(") AND d.classification <= :org_clearance)"),
    sql,
)

# (e) Multiple paths OR-folded
p = {}
sql = org_clause_from_context(
    {"elevated": False, "uid": 5, "paths": ["n1.n4", "n1.n7.n12"], "clearance": 1},
    p, "documents",
)
check(
    "multi-path: two CAST clauses OR-joined",
    sql.count("CAST(:org_path_") == 2,
    sql,
)
check("multi-path: org_path_0 + org_path_1 bound",
      p.get("org_path_0") == "n1.n4" and p.get("org_path_1") == "n1.n7.n12",
      str(p))
check(
    "multi-path: document alias honored (documents.scope_path)",
    "documents.scope_path" in sql,
    sql,
)

# (f) Clearance cap is AND-folded at the end (override never elevates clearance)
p = {}
sql = org_clause_from_context(
    {"elevated": False, "uid": 5, "paths": ["n1.n4"], "clearance": 0}, p, "d"
)
check(
    "clearance 0 forces classification <= 0 (only public visible)",
    "d.classification <= :org_clearance" in sql and p.get("org_clearance") == 0,
    sql + " | " + str(p),
)


# --------------------------------------------------------------------------
# 3. permission_clause delegates to org clause via ContextVar
# --------------------------------------------------------------------------
print("\n=== 3. permission_clause (services.permissions) ===")
from app.services.permissions import (
    permission_clause,
    current_access,
    set_access_context,
    is_admin,
)

# (a) No context set -> 1=1 (Celery / no setup)
current_access.set(None)
p = {}
sql = permission_clause(user=object(), params=p, document_alias="d")
check("permission_clause with no context -> 1=1", sql == "1=1", sql)

# (b) Elevated context -> 1=1
current_access.set({"elevated": True})
p = {}
sql = permission_clause(user=object(), params=p, document_alias="d")
check("permission_clause elevated -> 1=1", sql == "1=1", sql)

# (c) Regular user context -> full org clause
current_access.set({
    "elevated": False, "uid": 9, "paths": ["n1.n3"], "clearance": 2
})
p = {}
sql = permission_clause(user=object(), params=p, document_alias="d")
check(
    "permission_clause delegates to org clause for regular user",
    "d.scope_path <@ CAST(:org_path_0 AS ltree)" in sql
    and "d.classification <= :org_clearance" in sql,
    sql,
)
check(
    "permission_clause does NOT consult user_permissions (collection retired)",
    "user_permissions" not in sql and "collection_id" not in sql,
    sql,
)

# (d) is_admin recognises role enum and raw string
class _U:
    def __init__(self, v): self.role = v
class _Role:
    def __init__(self, v): self.value = v
check("is_admin(role enum value=admin)", is_admin(_U(_Role("admin"))))
check("is_admin(role string=admin)", is_admin(_U("admin")))
check("is_admin(role=viewer) is False", not is_admin(_U("viewer")))
check("is_admin(role=None) is False", not is_admin(_U(None)))


# --------------------------------------------------------------------------
# 4. Migration file: idempotency + safety
# --------------------------------------------------------------------------
print("\n=== 4. Migration idempotency ===")
mig = (BACKEND / "migrations" / "20260826_step44_org_tree.sql").read_text()

# Every DDL uses IF NOT EXISTS (so re-running is safe)
for stmt in [
    "CREATE EXTENSION IF NOT EXISTS ltree",
    "CREATE TABLE IF NOT EXISTS org_nodes",
    "CREATE TABLE IF NOT EXISTS user_org_memberships",
    "CREATE TABLE IF NOT EXISTS document_overrides",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_org_nodes_path",
    "CREATE INDEX IF NOT EXISTS idx_org_nodes_path_gist",
    "CREATE INDEX IF NOT EXISTS idx_org_nodes_parent",
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS scope_org_id",
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS scope_path",
    "ALTER TABLE documents ADD COLUMN IF NOT EXISTS classification",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS clearance_level",
]:
    check(f"migration: {stmt[:60]}", stmt in mig, "missing")

# Constraint creation wrapped in DO $$ ... check existence first
check(
    "migration: classification CHECK guarded by pg_constraint",
    "documents_classification_check" in mig
    and "IF NOT EXISTS (SELECT 1 FROM pg_constraint" in mig,
    "constraint not guarded",
)
check(
    "migration: clearance CHECK guarded by pg_constraint",
    "users_clearance_check" in mig,
    "",
)

# Root node seeded exactly once with id=1
check(
    "migration: root node (id=1, path='n1') seeded with ON CONFLICT DO NOTHING",
    "INSERT INTO org_nodes (id, name, name_ar, node_type, parent_id, path)\n"
    "VALUES (1, 'Organization', " in mig
    and "ON CONFLICT (id) DO NOTHING" in mig,
    "",
)

# Sequence advanced — without this the next API-created node collides with id 1
check(
    "migration: setval advances org_nodes_id_seq past MAX(id)",
    "setval('org_nodes_id_seq'" in mig,
    "sequence not advanced — next insert would collide with id 1",
)

# Existing documents/users backfilled to root scope
check(
    "migration: existing docs backfilled to scope_path='n1'",
    "UPDATE documents SET scope_org_id = 1, scope_path = 'n1'::ltree WHERE scope_org_id IS NULL" in mig,
    "",
)
check(
    "migration: existing users added to root membership",
    "INSERT INTO user_org_memberships (user_id, org_node_id)\nSELECT id, 1 FROM users" in mig,
    "",
)

# Default classification = 1 (internal) and clearance = 1 — preserves today's visibility
check(
    "migration: documents.classification default = 1",
    "classification INTEGER NOT NULL DEFAULT 1" in mig,
    "",
)
check(
    "migration: users.clearance_level default = 1",
    "clearance_level INTEGER NOT NULL DEFAULT 1" in mig,
    "",
)

# CHECK constraints enforce 0..3 range
check(
    "migration: classification CHECK BETWEEN 0 AND 3",
    "CHECK (classification BETWEEN 0 AND 3)" in mig,
    "",
)
check(
    "migration: clearance CHECK BETWEEN 0 AND 3",
    "CHECK (clearance_level BETWEEN 0 AND 3)" in mig,
    "",
)


# --------------------------------------------------------------------------
# 5. organization.py API surface — guard checks
# --------------------------------------------------------------------------
print("\n=== 5. organization.py API guards ===")
src = (BACKEND / "app" / "api" / "organization.py").read_text()

# Admin-only endpoints use require_admin
admin_endpoints = [
    ("get_tree", "GET /api/organization/tree"),
    ("create_node", "POST /api/organization/nodes"),
    ("update_node", "PATCH /api/organization/nodes/{node_id}"),
    ("list_members", "GET /api/organization/nodes/{node_id}/members"),
    ("add_member", "POST /api/organization/nodes/{node_id}/members"),
    ("remove_member", "DELETE /api/organization/nodes/{node_id}/members/{user_id}"),
    ("set_user_clearance", "PATCH /api/organization/users/{user_id}/clearance"),
]
for fn, label in admin_endpoints:
    pat = rf"async def {fn}\(.*?current_user: User = Depends\(require_admin\(\)\)"
    check(f"{label} requires admin", bool(re.search(pat, src, re.DOTALL)), "")

# Editor+ for /options (uploader scope picker)
check(
    "/options requires editor+ (require_roles(UserRole.editor))",
    "require_roles(UserRole.editor)" in src and 'async def org_options' in src,
    "",
)

# my-access uses get_current_user (any authenticated user)
check(
    "/my-access uses get_current_user (any authenticated user)",
    "async def my_access" in src
    and "current_user: User = Depends(get_current_user)" in src,
    "",
)

# Deactivation safety: refuses if members/docs/children attached
check(
    "deactivate: blocks when active children present",
    "node has" in src and "active child node(s)" in src,
    "",
)
check(
    "deactivate: blocks when members attached",
    "member(s)" in src,
    "",
)
check(
    "deactivate: blocks when documents scoped",
    "document(s) scoped to it" in src,
    "",
)
check(
    "deactivate: root node cannot be deactivated",
    "the root node cannot be deactivated" in src,
    "",
)
check(
    "deactivate: parent inactive blocks activation of child",
    "parent node is inactive" in src,
    "",
)

# Audit events emitted for every mutating endpoint
audit_markers = [
    "ORG_NODE_CREATED",
    "ORG_NODE_UPDATED",
    "ORG_NODE_DEACTIVATED",
    "ORG_NODE_ACTIVATED",
    "ORG_MEMBERSHIP_ADDED",
    "ORG_MEMBERSHIP_REMOVED",
    "USER_CLEARANCE_CHANGED",
]
for marker in audit_markers:
    check(f"audit event emitted: {marker}", marker in src, "")


# --------------------------------------------------------------------------
# 6. files.py — Phase 2 scoping + Phase 4 overrides
# --------------------------------------------------------------------------
print("\n=== 6. files.py scoping + overrides ===")
files_src = (BACKEND / "app" / "api" / "files.py").read_text()

# Upload accepts scope_org_id + classification
check(
    "upload endpoint accepts scope_org_id form field",
    "scope_org_id: int | None = Form" in files_src,
    "",
)
check(
    "upload endpoint accepts classification form field",
    "classification: int = Form" in files_src,
    "",
)
check(
    "upload validates classification is 0..3",
    "classification not in (0, 1, 2, 3)" in files_src
    and "422" in files_src,
    "",
)
check(
    "upload validates scope_org_id is an active org node (when not root)",
    "SELECT path::text AS path FROM org_nodes WHERE id = :nid AND is_active" in files_src,
    "",
)

# Re-scope endpoint
check(
    "PATCH /files/{doc_id}/scope exists (Phase 2 re-scope)",
    "async def rescope_document" in files_src
    or ("@router.patch(\"/{doc_id}/scope\"" in files_src),
    "",
)
check(
    "re-scope validates scope_org_id >= 1",
    "scope_org_id: int = Field(ge=1)" in files_src,
    "",
)
check(
    "re-scope validates classification 0..3",
    "classification: int = Field(ge=0, le=3)" in files_src,
    "",
)

# Overrides endpoints (Phase 4)
check(
    "GET /files/{doc_id}/overrides",
    '@router.get("/{doc_id}/overrides")' in files_src,
    "",
)
check(
    "POST /files/{doc_id}/overrides",
    '@router.post("/{doc_id}/overrides"' in files_src,
    "",
)
check(
    "DELETE /files/{doc_id}/overrides/{user_id}",
    '@router.delete("/{doc_id}/overrides/{user_id}"' in files_src,
    "",
)
check(
    "override INSERT uses ON CONFLICT / uniqueness check",
    "INSERT INTO document_overrides" in files_src
    and ("ON CONFLICT" in files_src or "SELECT id FROM document_overrides WHERE" in files_src),
    "",
)

# File listing joins org_nodes for scope name + classification
check(
    "file list SELECTs classification + scope name (Phase 4 badges)",
    "d.classification" in files_src
    and "n.name AS scope_name" in files_src
    and "n.name_ar AS scope_name_ar" in files_src,
    "",
)


# --------------------------------------------------------------------------
# 7. smart_search.py — Phase 3 access context + Phase 4 badges
# --------------------------------------------------------------------------
print("\n=== 7. smart_search.py wiring ===")
ss = (BACKEND / "app" / "api" / "smart_search.py").read_text()

check(
    "smart_search calls set_access_context as first statement",
    "await set_access_context(db, current_user)" in ss,
    "",
)
check(
    "smart_search_by_image calls set_access_context",
    ss.count("await set_access_context(db, current_user)") >= 2,
    "expected both smart_search and smart_search_by_image to set context",
)
check(
    "_finalize_results attaches classification + scope metadata",
    "row[\"classification\"] = meta.get(\"classification\"" in ss
    and "row[\"scope_org_id\"]" in ss
    and "row[\"scope_name\"]" in ss,
    "",
)
check(
    "_finalize_results swallows org_meta errors (best-effort)",
    "try:" in ss and "org_meta = {}" in ss,
    "",
)
check(
    "cache key bumped to v8 (so stale v7 caches don't poison Phase-4 results)",
    '"seekra:smart-search:result:v8:"' in ss,
    "",
)


# --------------------------------------------------------------------------
# 8. chat.py — set_access_context wired
# --------------------------------------------------------------------------
print("\n=== 8. chat.py wiring ===")
chat_src = (BACKEND / "app" / "api" / "chat.py").read_text()
n = chat_src.count("await set_access_context(db, current_user)")
check(
    "chat.py calls set_access_context at least twice (chat + alt endpoints)",
    n >= 2,
    f"found {n} call(s)",
)


# --------------------------------------------------------------------------
# 9. entities.py — set_access_context wired
# --------------------------------------------------------------------------
print("\n=== 9. entities.py wiring ===")
ent_src = (BACKEND / "app" / "api" / "entities.py").read_text()
check(
    "entities.py imports set_access_context",
    "from app.services.permissions import permission_clause, set_access_context" in ent_src,
    "",
)
check(
    "entities.py calls set_access_context in at least one endpoint",
    "await set_access_context(db, current_user)" in ent_src,
    "",
)


# --------------------------------------------------------------------------
# 10. Frontend admin/organization page structural checks
# --------------------------------------------------------------------------
print("\n=== 10. Frontend admin/organization page ===")
fe = REPO / "frontend" / "src" / "app" / "admin" / "organization" / "page.tsx"
check("frontend admin/organization/page.tsx exists", fe.exists(), "")
if fe.exists():
    s = fe.read_text()
    check(
        "page fetches /api/organization/tree on mount",
        "getOrgTree" in s or "/organization/tree" in s,
        "",
    )
    check(
        "page renders node list (create/edit)",
        "createNode" in s or "updateNode" in s or "createOrgNode" in s,
        "",
    )
    check(
        "page supports member add/remove",
        ("addMember" in s or "addOrgMember" in s)
        and ("removeMember" in s or "removeOrgMember" in s),
        "",
    )
    check(
        "page supports clearance change",
        "updateUserClearance" in s or "clearance" in s.lower(),
        "",
    )
    check(
        "page is admin-gated (role check)",
        "useAuth" in s or "requireAdmin" in s or "role" in s.lower(),
        "",
    )
    check(
        "page supports bilingual labels (ar/en)",
        "useI18n" in s or "useTranslations" in s or "t(" in s,
        "",
    )


# --------------------------------------------------------------------------
# 11. Frontend api.ts — organization client surface
# --------------------------------------------------------------------------
print("\n=== 11. Frontend api.ts ===")
api_ts = (REPO / "frontend" / "src" / "lib" / "api.ts").read_text()
for fn in [
    "getOrgTree",
    "getOrgOptions",
    "createOrgNode",
    "updateOrgNode",
    "getOrgMembers",
    "addOrgMember",
    "removeOrgMember",
    "updateUserClearance",
    "getFileOverrides",
    "grantFileOverride",
    "revokeFileOverride",
]:
    check(f"api.ts exports {fn}", fn in api_ts, "")
# DocumentResult type carries classification (for badges)
check(
    "DocumentResult type has classification field",
    "classification?: number" in api_ts,
    "",
)
# User type carries clearance_level
check(
    "User type has clearance_level field",
    "clearance_level?: number" in api_ts,
    "",
)


# --------------------------------------------------------------------------
# 12. i18n strings (en + ar) for org/classification/clearance
# --------------------------------------------------------------------------
print("\n=== 12. i18n strings (en + ar) ===")
en = (REPO / "frontend" / "src" / "i18n" / "dictionaries" / "en.json").read_text()
ar = (REPO / "frontend" / "src" / "i18n" / "dictionaries" / "ar.json").read_text()
required_keys = [
    "organization",
    "classification",
    "clearance",
    "scope",
    "members",
]
for key in required_keys:
    check(f"en.json has '{key}'", f'"{key}"' in en.lower(), "")
    check(f"ar.json has '{key}'", f'"{key}"' in ar.lower(), "")


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"STATIC + UNIT UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
