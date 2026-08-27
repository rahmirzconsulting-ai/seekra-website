#!/usr/bin/env python3
"""Brief #17 UAT — Phase 2: live DB + API integration tests.

Boots a portable Postgres (via pgserver), applies the Brief #17 migration,
seeds test fixtures (users, documents, org nodes, memberships, overrides),
then exercises the SQL access filter `org_clause_from_context` against the
real database — verifying the SQL fragment behaves correctly for:

  * admin / auditor bypass
  * sibling scope invisibility (fail-closed)
  * parent scope visibility (access flows DOWN the tree)
  * clearance cap (clearance 1 cannot see classification 2/3)
  * public documents (classification 0) visible org-wide
  * per-user override grants cross-scope access (without elevating clearance)
  * inactive nodes still gate (sanity)

Then it boots the FastAPI app against this DB and exercises the
/api/organization/* endpoints end-to-end:

  * admin can CRUD nodes, manage members, set clearance
  * editor can read /options but not /tree
  * viewer cannot POST/PATCH/DELETE
  * deactivation safety guards (refuses with members/docs/children attached)
  * my-access returns the caller's resolved paths + clearance + filter SQL

This is the integration half of the UAT. Static + pure-function tests
live in uat_brief17_static.py.
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import pathlib
import json
from typing import Any

REPO = pathlib.Path("/home/z/my-project/seekra-app")
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))

# Settings requires these
os.environ.setdefault("SECRET_KEY", "uat-live-dummy-secret-key-32-chars")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")
os.environ.setdefault("MINIO_BUCKET_NAME", "uat-bucket")

PASS = 0
FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# --------------------------------------------------------------------------
# Boot portable postgres
# --------------------------------------------------------------------------
print("\n=== Booting portable postgres (pgserver) ===")
import pgserver
import psycopg2

PGDATA = pathlib.Path(tempfile.mkdtemp(prefix="seekra_uat_pg_"))
pg = pgserver.PostgresServer(PGDATA)
pg.ensure_pgdata_inited()
pg.ensure_postgres_running()
DB_URI = pg.get_uri()  # e.g. postgresql:///postgres?host=/tmp/.../socket
print(f"  pg URI: {DB_URI}")

# pgserver returns a URI that asyncpg may not parse identically; normalize it.
import re
# Extract host and dbname
m = re.match(r"postgresql(?:\+psycopg2)?://(?P<user>[^@]+)@(?P<host>[^/]+)/(?P<db>[^?]+)", DB_URI)
if m:
    DB_HOST = m.group("host")
    DB_PORT = "5432"
    DB_NAME = m.group("db")
    DB_USER = m.group("user")
else:
    # Fall back: assume socket-style URI (postgresql:///postgres?host=/tmp/...)
    # parse query string
    if "?" in DB_URI:
        base, q = DB_URI.split("?", 1)
        host = None
        for kv in q.split("&"):
            if kv.startswith("host="):
                host = kv.split("=", 1)[1]
        DB_HOST = host or "localhost"
        DB_NAME = base.rsplit("/", 1)[-1] or "postgres"
    else:
        DB_HOST = "localhost"
        DB_NAME = "postgres"
    DB_USER = "postgres"
    DB_PORT = "5432"

# Set DATABASE_URL for the backend's Settings
os.environ["DATABASE_URL"] = (
    f"postgresql+asyncpg://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
print(f"  DATABASE_URL set: {os.environ['DATABASE_URL']}")

# Apply migration via psycopg2 (synchronous, simpler)
print("\n=== Applying migration ===")
conn = psycopg2.connect(DB_URI)
conn.autocommit = True
cur = conn.cursor()

# Drop+recreate public schema for a clean slate
cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
cur.execute("CREATE SCHEMA public")
cur.execute("GRANT ALL ON SCHEMA public TO postgres")
cur.execute("GRANT ALL ON SCHEMA public TO public")

mig_sql = (BACKEND / "migrations" / "20260826_step44_org_tree.sql").read_text()
cur.execute(mig_sql)
check("migration applied cleanly", True)

# Re-apply migration (idempotency check)
try:
    cur.execute(mig_sql)
    check("migration is idempotent (re-run OK)", True)
except Exception as e:
    check("migration is idempotent (re-run OK)", False, f"{type(e).__name__}: {e}")
    conn.rollback()
    conn.autocommit = True

# Verify schema
cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_name IN
    ('org_nodes','user_org_memberships','document_overrides','documents','users')
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]
check("org_nodes table exists", "org_nodes" in tables)
check("user_org_memberships table exists", "user_org_memberships" in tables)
check("document_overrides table exists", "document_overrides" in tables)

cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='documents' AND column_name IN
    ('scope_org_id','scope_path','classification')
""")
cols = [r[0] for r in cur.fetchall()]
check("documents.scope_org_id exists", "scope_org_id" in cols)
check("documents.scope_path exists", "scope_path" in cols)
check("documents.classification exists", "classification" in cols)

cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='users' AND column_name='clearance_level'
""")
check("users.clearance_level exists", cur.fetchone() is not None)

# Root node seeded
cur.execute("SELECT id, name, path::text, node_type FROM org_nodes WHERE id=1")
root = cur.fetchone()
check("root node (id=1, name='Organization', path='n1') seeded",
      root == (1, "Organization", "n1", "company"), str(root))

# Sequence advanced past id 1
cur.execute("SELECT last_value FROM org_nodes_id_seq")
seq_val = cur.fetchone()[0]
check("org_nodes_id_seq advanced past 1", seq_val >= 1, f"seq_val={seq_val}")

# ltree extension installed
cur.execute("SELECT extname FROM pg_extension WHERE extname='ltree'")
check("ltree extension installed", cur.fetchone() is not None)


# --------------------------------------------------------------------------
# Seed fixtures
# --------------------------------------------------------------------------
print("\n=== Seeding fixtures ===")

# Users (we hash passwords with passlib to match the backend's verify)
from app.core.security import get_password_hash

users_to_create = [
    # (id, username, email, role, clearance_level)
    (1, "admin", "admin@x.com", "admin", 1),
    (2, "alice", "alice@x.com", "viewer", 1),   # engineering member
    (3, "bob",   "bob@x.com",   "viewer", 1),   # sales member (sibling)
    (4, "carol", "carol@x.com", "viewer", 2),   # engineering member w/ clearance 2
    (5, "dave",  "dave@x.com",  "viewer", 3),   # engineering member w/ clearance 3
    (6, "auditor", "aud@x.com", "auditor", 1),  # auditor (elevated)
    (7, "editor",  "ed@x.com",  "editor", 1),   # editor
]
for uid, uname, email, role, cl in users_to_create:
    cur.execute(
        "INSERT INTO users (id, username, email, hashed_password, role, clearance_level) "
        "VALUES (%s, %s, %s, %s, %s::text, %s) ON CONFLICT (id) DO NOTHING",
        (uid, uname, email, get_password_hash("pass1234"), role, cl),
    )
# Sync sequences
cur.execute("SELECT setval('users_id_seq', GREATEST((SELECT MAX(id) FROM users), 1))")
conn.commit()

# Org tree:
#   n1 Organization (root, id=1)
#   n1.n2 Engineering (id=2)
#   n1.n2.n3 Backend (id=3)
#   n1.n4 Sales (id=4)
#   n1.n5 Marketing (id=5)
org_nodes = [
    (2, "Engineering", "department", 1, "n1.n2"),
    (3, "Backend",     "team",       2, "n1.n2.n3"),
    (4, "Sales",       "department", 1, "n1.n4"),
    (5, "Marketing",   "department", 1, "n1.n5"),
]
for nid, name, ntype, parent_id, path in org_nodes:
    cur.execute(
        "INSERT INTO org_nodes (id, name, name_ar, node_type, parent_id, path, is_active) "
        "VALUES (%s, %s, NULL, %s, %s, %s::ltree, TRUE) ON CONFLICT (id) DO NOTHING",
        (nid, name, ntype, parent_id, path),
    )
cur.execute("SELECT setval('org_nodes_id_seq', GREATEST((SELECT MAX(id) FROM org_nodes), 1))")
conn.commit()

# Memberships:
#   alice, carol, dave -> Engineering (2)
#   bob -> Sales (4)
#   editor -> root (1)  (so they can read everything from root down — actually editor elevation? no, editor is a regular user for org purposes)
memberships = [
    (2, 2),  # alice -> Engineering
    (4, 4),  # carol -> Engineering (clearance 2)
    (5, 2),  # dave -> Engineering (clearance 3)
    (3, 4),  # bob -> Sales
    (7, 1),  # editor -> root
]
for uid, nid in memberships:
    cur.execute(
        "INSERT INTO user_org_memberships (user_id, org_node_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
        (uid, nid),
    )
conn.commit()

# Documents:
#   d1: scoped to Engineering (n1.n2), classification=1 (internal)
#   d2: scoped to Backend (n1.n2.n3), classification=2 (confidential)
#   d3: scoped to Sales (n1.n4), classification=1
#   d4: scoped to Engineering (n1.n2), classification=3 (restricted)
#   d5: scoped to Engineering (n1.n2), classification=0 (PUBLIC — visible org-wide)
#   d6: scoped to Marketing (n1.n5), classification=1
docs = [
    (1, "Eng Roadmap",      2, "n1.n2",     1),
    (2, "Backend API Spec", 3, "n1.n2.n3",  2),
    (3, "Sales Playbook",   4, "n1.n4",     1),
    (4, "Eng Secrets",      2, "n1.n2",     3),
    (5, "Press Release",    2, "n1.n2",     0),  # public
    (6, "Mktg Plan",        5, "n1.n5",     1),
]
for did, fname, sid, spath, cls in docs:
    cur.execute(
        "INSERT INTO documents (id, filename, scope_org_id, scope_path, classification) "
        "VALUES (%s, %s, %s, %s::ltree, %s) ON CONFLICT (id) DO NOTHING",
        (did, fname, sid, spath, cls),
    )
cur.execute("SELECT setval('documents_id_seq', GREATEST((SELECT MAX(id) FROM documents), 1))")
conn.commit()

# Override: bob (Sales, uid=3) gets read on d1 (Engineering Roadmap)
cur.execute(
    "INSERT INTO document_overrides (document_id, user_id, can_read, reason, granted_by) "
    "VALUES (1, 3, TRUE, 'cross-team grant', 1) ON CONFLICT DO NOTHING"
)
conn.commit()

print("  fixtures seeded: 7 users, 5 org nodes, 6 documents, 5 memberships, 1 override")


# --------------------------------------------------------------------------
# Test the actual SQL fragment against real DB
# --------------------------------------------------------------------------
print("\n=== Live SQL access filter tests ===")
from app.services.org_tree import org_clause_from_context

async def run_filter_for_user(uid: int, paths: list[str], clearance: int) -> list[int]:
    """Apply the exact SQL fragment org_clause_from_context produces and
    return the visible document IDs."""
    params: dict[str, Any] = {}
    sql_fragment = org_clause_from_context(
        {"elevated": False, "uid": uid, "paths": paths, "clearance": clearance},
        params,
        "d",
    )
    full_sql = f"SELECT d.id FROM documents d WHERE {sql_fragment} ORDER BY d.id"
    cur.execute(full_sql, params)
    return [r[0] for r in cur.fetchall()]

# Helper: convert uid to (paths, clearance) by reading from DB
def get_user_ctx(uid: int) -> tuple[list[str], int]:
    cur.execute("""
        SELECT n.path::text FROM user_org_memberships m
        JOIN org_nodes n ON n.id = m.org_node_id
        WHERE m.user_id = %s AND n.is_active
    """, (uid,))
    paths = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT clearance_level FROM users WHERE id = %s", (uid,))
    clearance = cur.fetchone()[0]
    return paths, clearance


# (1) Alice — Engineering member, clearance 1
paths, cl = get_user_ctx(2)  # alice
visible = asyncio.run(run_filter_for_user(2, paths, cl))
# Alice should see: d1 (eng internal), d5 (eng public). NOT d2 (confidential, clearance cap),
# NOT d4 (restricted, clearance cap), NOT d3 (sales), NOT d6 (marketing)
check(
    "alice (Eng, clearance 1) sees d1 (eng internal) + d5 (eng public)",
    visible == [1, 5],
    f"got {visible}",
)

# (2) Bob — Sales member, clearance 1, BUT has override on d1
paths, cl = get_user_ctx(3)  # bob
visible = asyncio.run(run_filter_for_user(3, paths, cl))
# Bob should see: d3 (sales internal) + d1 (via override, but d1 is internal so clearance OK)
# NOT d2 (confidential - override doesn't elevate clearance)
# NOT d4 (restricted - override doesn't elevate clearance)
# NOT d5 (eng public - bob isn't in eng subtree... wait, public IS visible org-wide per the clause)
# Actually let me re-read the clause: ((public OR tree OR override) AND classification <= clearance)
# So d5 (public) is visible to bob because classification(0) <= clearance(1) AND public clause matches
check(
    "bob (Sales, clearance 1, override on d1) sees d1 (override) + d3 (sales) + d5 (public org-wide)",
    visible == [1, 3, 5],
    f"got {visible}",
)

# (3) Carol — Engineering member, clearance 2 (confidential)
paths, cl = get_user_ctx(4)  # carol
visible = asyncio.run(run_filter_for_user(4, paths, cl))
# Carol should see: d1 (eng internal), d2 (eng/backend confidential), d5 (public)
# NOT d4 (restricted, clearance 2 < 3)
# NOT d3 (sales), NOT d6 (marketing)
check(
    "carol (Eng, clearance 2) sees d1 + d2 (confidential) + d5 (public)",
    visible == [1, 2, 5],
    f"got {visible}",
)

# (4) Dave — Engineering member, clearance 3 (restricted)
paths, cl = get_user_ctx(5)  # dave
visible = asyncio.run(run_filter_for_user(5, paths, cl))
# Dave should see: d1, d2, d4 (restricted), d5 — everything in Eng subtree
check(
    "dave (Eng, clearance 3) sees d1 + d2 + d4 (restricted) + d5",
    visible == [1, 2, 4, 5],
    f"got {visible}",
)

# (5) Editor — root member, clearance 1
paths, cl = get_user_ctx(7)  # editor
visible = asyncio.run(run_filter_for_user(7, paths, cl))
# Editor at root should see all internal+public docs (clearance 1 caps at internal)
# So: d1 (internal), d3 (internal), d5 (public), d6 (internal)
# NOT d2 (confidential), NOT d4 (restricted)
check(
    "editor (root, clearance 1) sees all internal + public, not confidential/restricted",
    visible == [1, 3, 5, 6],
    f"got {visible}",
)

# (6) Elevated (admin/auditor) returns '1=1' — should see everything
sql_fragment = org_clause_from_context({"elevated": True}, {}, "d")
cur.execute(f"SELECT d.id FROM documents d WHERE {sql_fragment} ORDER BY d.id")
visible = [r[0] for r in cur.fetchall()]
check(
    "admin/auditor bypass sees all 6 documents",
    visible == [1, 2, 3, 4, 5, 6],
    f"got {visible}",
)

# (7) No-context (Celery worker / legacy path) -> 1=1 -> sees everything
sql_fragment = org_clause_from_context(None, {}, "d")
cur.execute(f"SELECT d.id FROM documents d WHERE {sql_fragment} ORDER BY d.id")
visible = [r[0] for r in cur.fetchall()]
check(
    "no-context (Celery) returns 1=1 — sees everything (legacy behavior preserved)",
    visible == [1, 2, 3, 4, 5, 6],
    f"got {visible}",
)

# (8) Empty-paths user (somehow no memberships) -> fail-closed except public
paths, cl = [], 1
visible = asyncio.run(run_filter_for_user(999, paths, cl))
check(
    "user with no memberships sees only public docs (fail-closed)",
    visible == [5],
    f"got {visible}",
)


# --------------------------------------------------------------------------
# Phase 4: my-access diagnostic shape
# --------------------------------------------------------------------------
print("\n=== my-access shape (via service directly) ===")
import asyncpg
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_my_access_shape():
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    async with AsyncSession(engine) as db:
        from app.services.org_tree import (
            get_user_org_paths, get_user_clearance, build_org_access_filter
        )
        from app.services.permissions import set_access_context

        # alice's paths + clearance
        paths = await get_user_org_paths(db, 2)
        clearance = await get_user_clearance(db, 2)
        check("alice's paths == ['n1.n2']", paths == ["n1.n2"], str(paths))
        check("alice's clearance == 1", clearance == 1, str(clearance))

        # build_org_access_filter for alice
        class _U:
            id = 2
            class _R: value = "viewer"
            role = _R()
        params: dict = {}
        sql = await build_org_access_filter(db, _U(), params, "d")
        check(
            "build_org_access_filter for alice includes scope_path <@ n1.n2",
            "d.scope_path <@ CAST(:org_path_0 AS ltree)" in sql
            and params.get("org_path_0") == "n1.n2",
            sql,
        )
        check(
            "build_org_access_filter for alice caps clearance at 1",
            params.get("org_clearance") == 1,
            str(params),
        )

    await engine.dispose()

asyncio.run(test_my_access_shape())


# --------------------------------------------------------------------------
# FastAPI app end-to-end — exercise /api/organization/* endpoints
# --------------------------------------------------------------------------
print("\n=== FastAPI /api/organization/* end-to-end ===")
from httpx import AsyncClient, ASGITransport
from app.main import app

async def api_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Login as admin
        r = await client.post("/api/auth/login", data={"username": "admin", "password": "pass1234"})
        admin_tok = r.json().get("access_token") or r.json().get("token")
        check("admin login OK", admin_tok is not None, r.text[:200])
        if not admin_tok:
            return
        A = {"Authorization": f"Bearer {admin_tok}"}

        # Login as viewer (alice)
        r = await client.post("/api/auth/login", data={"username": "alice", "password": "pass1234"})
        alice_tok = r.json().get("access_token") or r.json().get("token")
        check("alice (viewer) login OK", alice_tok is not None, r.text[:200])
        V = {"Authorization": f"Bearer {alice_tok}"}

        # Login as editor
        r = await client.post("/api/auth/login", data={"username": "editor", "password": "pass1234"})
        editor_tok = r.json().get("access_token") or r.json().get("token")
        check("editor login OK", editor_tok is not None, r.text[:200])
        E = {"Authorization": f"Bearer {editor_tok}"}

        # --- /my-access (any authenticated user) ---
        r = await client.get("/api/organization/my-access", headers=A)
        check("/my-access admin 200", r.status_code == 200, r.text[:200])
        body = r.json()
        check("/my-access admin is elevated (no paths)",
              body.get("clearance_level") == 1
              and body.get("access_filter") == "1=1",
              str(body))

        r = await client.get("/api/organization/my-access", headers=V)
        check("/my-access alice 200", r.status_code == 200, r.text[:200])
        body = r.json()
        check("/my-access alice shows paths=['n1.n2'] clearance=1",
              body.get("org_paths") == ["n1.n2"]
              and body.get("clearance_level") == 1,
              str(body))
        check("/my-access alice filter SQL includes <@ n1.n2",
              "n1.n2" in body.get("access_filter", ""),
              body.get("access_filter"))

        # --- /tree (admin only) ---
        r = await client.get("/api/organization/tree", headers=A)
        check("/tree admin 200", r.status_code == 200, r.text[:200])
        nodes = r.json()
        check("/tree returns 5 nodes (root + 4 children)",
              len(nodes) == 5, f"got {len(nodes)}: {[n['name'] for n in nodes]}")
        check("/tree root node is first (path n1)",
              nodes[0]["path"] == "n1" and nodes[0]["name"] == "Organization",
              str(nodes[0]))
        check("/tree nodes have depth field",
              all("depth" in n for n in nodes), "")
        check("/tree nodes have member_count + document_count",
              all("member_count" in n and "document_count" in n for n in nodes), "")
        check("/tree Engineering shows 3 members (alice, carol, dave)",
              next(n for n in nodes if n["name"] == "Engineering")["member_count"] == 3,
              str([n for n in nodes if n['name']=='Engineering']))

        # --- /tree RBAC ---
        r = await client.get("/api/organization/tree", headers=V)
        check("/tree viewer -> 403", r.status_code == 403, f"got {r.status_code}")
        r = await client.get("/api/organization/tree", headers=E)
        check("/tree editor -> 403", r.status_code == 403, f"got {r.status_code}")

        # --- /options (editor+admin) ---
        r = await client.get("/api/organization/options", headers=A)
        check("/options admin 200", r.status_code == 200, r.text[:200])
        r = await client.get("/api/organization/options", headers=E)
        check("/options editor 200", r.status_code == 200, r.text[:200])
        r = await client.get("/api/organization/options", headers=V)
        check("/options viewer -> 403", r.status_code == 403, f"got {r.status_code}")

        # --- POST /nodes (create new department under Engineering) ---
        r = await client.post("/api/organization/nodes", headers=A, json={
            "name": "QA Team",
            "name_ar": "فريق الجودة",
            "node_type": "team",
            "parent_id": 2,  # Engineering
        })
        check("POST /nodes admin 201", r.status_code == 201, r.text[:200])
        new_node = r.json()
        new_id = new_node.get("id")
        check("new node path is n1.n2.n<id>", new_node.get("path") == f"n1.n2.n{new_id}",
              str(new_node))
        check("new node depth is 2", new_node.get("depth") == 2, str(new_node))

        # --- POST /nodes RBAC ---
        r = await client.post("/api/organization/nodes", headers=V, json={
            "name": "Should Fail", "node_type": "team", "parent_id": 2
        })
        check("POST /nodes viewer -> 403", r.status_code == 403, f"got {r.status_code}")

        # --- POST /nodes with bad parent ---
        r = await client.post("/api/organization/nodes", headers=A, json={
            "name": "Orphan", "node_type": "team", "parent_id": 99999
        })
        check("POST /nodes bad parent -> 404", r.status_code == 404, f"got {r.status_code}")

        # --- POST /nodes with bad node_type ---
        r = await client.post("/api/organization/nodes", headers=A, json={
            "name": "Bad Type", "node_type": "division", "parent_id": 2
        })
        check("POST /nodes bad node_type -> 400", r.status_code == 400, f"got {r.status_code}")

        # --- PATCH /nodes (rename) ---
        r = await client.patch(f"/api/organization/nodes/{new_id}", headers=A, json={
            "name": "QA Team Renamed"
        })
        check("PATCH /nodes rename 200", r.status_code == 200, r.text[:200])
        check("rename applied", r.json().get("name") == "QA Team Renamed",
              str(r.json()))

        # --- PATCH /nodes (deactivate with members attached — should fail) ---
        # Engineering (id=2) has 3 members
        r = await client.patch("/api/organization/nodes/2", headers=A, json={
            "is_active": False
        })
        check("deactivate Engineering -> 409 (has members)", r.status_code == 409,
              f"got {r.status_code} {r.text[:200]}")

        # --- Deactivate the new empty QA team (should succeed) ---
        r = await client.patch(f"/api/organization/nodes/{new_id}", headers=A, json={
            "is_active": False
        })
        check("deactivate empty QA team -> 200", r.status_code == 200,
              f"got {r.status_code} {r.text[:200]}")

        # --- Deactivate root (should fail) ---
        r = await client.patch("/api/organization/nodes/1", headers=A, json={
            "is_active": False
        })
        check("deactivate root -> 400", r.status_code == 400,
              f"got {r.status_code} {r.text[:200]}")

        # --- Members endpoints ---
        r = await client.get("/api/organization/nodes/2/members", headers=A)
        check("GET /nodes/2/members 200", r.status_code == 200, r.text[:200])
        members = r.json()
        check("Engineering has 3 members", len(members) == 3,
              f"got {len(members)}: {[m.get('username') for m in members]}")

        # Add editor to Engineering
        r = await client.post("/api/organization/nodes/2/members", headers=A, json={
            "user_id": 7  # editor
        })
        check("POST /nodes/2/members editor -> 201", r.status_code == 201,
              f"got {r.status_code} {r.text[:200]}")

        # Remove editor from Engineering
        r = await client.delete("/api/organization/nodes/2/members/7", headers=A)
        check("DELETE /nodes/2/members/7 -> 200", r.status_code == 200,
              f"got {r.status_code} {r.text[:200]}")

        # Remove non-existent membership
        r = await client.delete("/api/organization/nodes/2/members/99999", headers=A)
        check("DELETE non-existent membership -> 404", r.status_code == 404,
              f"got {r.status_code}")

        # --- Clearance endpoint ---
        # Bump alice from clearance 1 to 2
        r = await client.patch("/api/organization/users/2/clearance", headers=A, json={
            "clearance_level": 2
        })
        check("PATCH alice clearance 1->2 -> 200", r.status_code == 200,
              f"got {r.status_code} {r.text[:200]}")
        check("clearance response body correct",
              r.json().get("clearance_level") == 2, str(r.json()))

        # Out-of-range clearance
        r = await client.patch("/api/organization/users/2/clearance", headers=A, json={
            "clearance_level": 5
        })
        check("PATCH clearance=5 -> 422 (out of range)", r.status_code == 422,
              f"got {r.status_code}")

        # Reset alice
        r = await client.patch("/api/organization/users/2/clearance", headers=A, json={
            "clearance_level": 1
        })
        check("PATCH alice clearance reset -> 200", r.status_code == 200,
              f"got {r.status_code}")

        # RBAC on clearance
        r = await client.patch("/api/organization/users/2/clearance", headers=V, json={
            "clearance_level": 2
        })
        check("PATCH clearance as viewer -> 403", r.status_code == 403,
              f"got {r.status_code}")

asyncio.run(api_e2e())


# --------------------------------------------------------------------------
# Phase 4: /files/{id}/overrides endpoints (live)
# --------------------------------------------------------------------------
print("\n=== /files/{doc_id}/overrides endpoints ===")
async def overrides_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        r = await client.post("/api/auth/login", data={"username": "admin", "password": "pass1234"})
        A = {"Authorization": f"Bearer {r.json().get('access_token') or r.json().get('token')}"}

        # List overrides on d1 (should have 1 — for bob)
        r = await client.get("/api/files/1/overrides", headers=A)
        check("GET /files/1/overrides 200", r.status_code == 200, r.text[:200])
        body = r.json()
        check("d1 has 1 override (bob)",
              len(body.get("overrides", [])) == 1,
              str(body))

        # Add a new override for alice on d3 (sales playbook — alice is eng, not sales)
        r = await client.post("/api/files/3/overrides", headers=A, json={
            "user_id": 2, "can_read": True, "reason": "cross-team grant for alice"
        })
        check("POST /files/3/overrides alice -> 201",
              r.status_code == 201, f"got {r.status_code} {r.text[:200]}")

        # Add duplicate override (should be idempotent or 400, not 500)
        r = await client.post("/api/files/3/overrides", headers=A, json={
            "user_id": 2, "can_read": True, "reason": "duplicate"
        })
        check("POST duplicate override -> 400 or 409 (not 500)",
              r.status_code in (400, 409), f"got {r.status_code} {r.text[:200]}")

        # Delete the override
        r = await client.delete("/api/files/3/overrides/2", headers=A)
        check("DELETE /files/3/overrides/2 -> 200",
              r.status_code == 200, f"got {r.status_code} {r.text[:200]}")

        # Delete non-existent
        r = await client.delete("/api/files/3/overrides/2", headers=A)
        check("DELETE non-existent override -> 404",
              r.status_code == 404, f"got {r.status_code}")

asyncio.run(overrides_e2e())


# --------------------------------------------------------------------------
# Phase 4: regression — search/files now respect org filter
# --------------------------------------------------------------------------
print("\n=== Search/files respect org filter (live) ===")
async def access_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Login as alice (Engineering, clearance 1)
        r = await client.post("/api/auth/login", data={"username": "alice", "password": "pass1234"})
        V = {"Authorization": f"Bearer {r.json().get('access_token') or r.json().get('token')}"}

        # GET /api/files should only show docs alice can see (d1, d5)
        r = await client.get("/api/files", headers=V)
        check("GET /files as alice 200", r.status_code == 200, r.text[:200])
        files = r.json()
        if isinstance(files, dict) and "items" in files:
            files = files["items"]
        visible_ids = sorted([f["id"] for f in files])
        check("alice /files shows only d1 + d5 (eng internal + public)",
              visible_ids == [1, 5], f"got {visible_ids}")

        # Each file should carry classification + scope_name fields
        if files:
            f0 = files[0]
            check("file item has classification field", "classification" in f0, str(f0.keys()))
            check("file item has scope_org_id field", "scope_org_id" in f0, str(f0.keys()))
            check("file item has scope_name field", "scope_name" in f0, str(f0.keys()))

asyncio.run(access_e2e())


# --------------------------------------------------------------------------
# Cleanup
# --------------------------------------------------------------------------
cur.close()
conn.close()
pg.stop()
print("\n" + "=" * 60)
print(f"INTEGRATION UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
