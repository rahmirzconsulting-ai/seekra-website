# Brief #17: Enterprise Access Control — Org Tree + Document Classification

**For:** Kimi
**Date:** 2026-08-18
**Effort:** 4 phases, ~2 weeks total
**Prerequisite:** Sidebar redesign (shipped) — the "Organization" nav item goes in the ADMINISTRATION section

## Objective

Transform Seekra from single-organization access control (collection-based) to **multi-company enterprise access control** with:
1. A configurable organization tree (group → company → department → team)
2. User-node memberships (users belong to org nodes)
3. Document scoping (documents belong to org nodes — inherited access)
4. Document classification (Public / Internal / Confidential / Restricted)
5. User clearance levels (matching classification)
6. Explicit override layer for cross-company collaboration

This enables a holding company with subsidiaries to deploy Seekra where:
- Group-wide documents are visible to all companies
- Company A's documents are NOT visible to Company B
- Confidential documents are only visible to users with confidential clearance
- Cross-company collaboration is possible via explicit overrides

## Current state (what we're replacing)

The current `permission_clause()` in `services/permissions.py`:
```python
(d.collection_id IS NULL OR d.collection_id IN
    (SELECT collection_id FROM user_permissions WHERE user_id = :perm_uid AND can_read))
```

This is collection-based: root documents (collection_id IS NULL) are visible to everyone; collection-scoped documents require an explicit `user_permissions` row. This doesn't scale to multi-company structures.

**Collections are NOT being removed** — they remain as a document organization concept (like folders). But access control moves from collections to the org tree.

---

## Phase 1: Org Tree Schema + Admin UI (3-4 days)

### File 1: Migration `backend/migrations/20260819_step44_org_tree.sql`

```sql
-- Step 44 (Brief #17): Organization tree + document classification
--
-- Enables multi-company enterprise access control:
-- - Org tree (group → company → department → team) with materialized paths
-- - User-node memberships (users belong to one or more org nodes)
-- - Document scoping (documents belong to an org node — inherited access)
-- - Document classification (4 levels: public/internal/confidential/restricted)
-- - User clearance levels (matching classification)
-- - Explicit override layer for cross-company collaboration

-- ltree extension for fast ancestor/descendant queries
CREATE EXTENSION IF NOT EXISTS ltree;

-- Organization tree nodes
CREATE TABLE IF NOT EXISTS org_nodes (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES org_nodes(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    node_type VARCHAR(20) NOT NULL DEFAULT 'department',
    -- 'group' | 'company' | 'department' | 'team'
    path LTREE NOT NULL,
    -- materialized path: e.g., '1.3.7.15' for node 15 under 7 under 3 under 1
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_org_nodes_path ON org_nodes USING GIST (path);
CREATE INDEX IF NOT EXISTS idx_org_nodes_parent ON org_nodes (parent_id);
CREATE INDEX IF NOT EXISTS idx_org_nodes_type ON org_nodes (node_type) WHERE is_active = true;

-- User → org node memberships
CREATE TABLE IF NOT EXISTS user_org_memberships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_node_id INTEGER NOT NULL REFERENCES org_nodes(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    -- user's primary org node (display name, default scope for uploads)
    role VARCHAR(20) DEFAULT 'member',
    -- 'member' | 'manager' | 'admin' (org-level admin, NOT system admin)
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, org_node_id)
);

CREATE INDEX IF NOT EXISTS idx_uom_user ON user_org_memberships (user_id);
CREATE INDEX IF NOT EXISTS idx_uom_org ON user_org_memberships (org_node_id);

-- Document scoping (replaces collection_id for access control)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS scope_org_id INTEGER REFERENCES org_nodes(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS scope_path LTREE;
-- denormalized from org_nodes.path for fast queries

CREATE INDEX IF NOT EXISTS idx_documents_scope_org ON documents (scope_org_id);
CREATE INDEX IF NOT EXISTS idx_documents_scope_path ON documents USING GIST (scope_path);

-- Document classification (4 levels)
ALTER TABLE documents ADD COLUMN IF NOT EXISTS classification SMALLINT DEFAULT 1;
-- 0=public, 1=internal, 2=confidential, 3=restricted

-- User clearance level
ALTER TABLE users ADD COLUMN IF NOT EXISTS clearance_level SMALLINT DEFAULT 1;
-- 0=public, 1=internal, 2=confidential, 3=restricted

-- Explicit access overrides (for cross-company collaboration)
CREATE TABLE IF NOT EXISTS document_overrides (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(10) DEFAULT 'read',
    -- 'read' | 'write'
    granted_by INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (document_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_overrides_doc ON document_overrides (document_id);
CREATE INDEX IF NOT EXISTS idx_overrides_user ON document_overrides (user_id);

-- Seed a root org node (the group level)
INSERT INTO org_nodes (id, parent_id, name, node_type, path)
VALUES (1, NULL, 'Organization', 'group', '1')
ON CONFLICT (id) DO NOTHING;

-- Migrate existing documents: scope to root node (everyone sees everything — same as today)
UPDATE documents SET scope_org_id = 1, scope_path = '1'::ltree WHERE scope_org_id IS NULL;

-- Migrate existing users: assign to root node
INSERT INTO user_org_memberships (user_id, org_node_id, is_primary, role)
SELECT u.id, 1, true, 'member'
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM user_org_memberships m WHERE m.user_id = u.id AND m.org_node_id = 1
);

COMMENT ON TABLE org_nodes IS 'Step 44: Organization tree. Hierarchical nodes (group/company/department/team) with ltree materialized paths for fast ancestor queries.';
COMMENT ON COLUMN documents.classification IS 'Step 44: 0=public, 1=internal, 2=confidential, 3=restricted. Default=1 (internal).';
COMMENT ON COLUMN users.clearance_level IS 'Step 44: 0=public, 1=internal, 2=confidential, 3=restricted. Default=1 (internal).';
```

### File 2: New service `backend/app/services/org_tree.py`

```python
"""Brief #17: Organization tree management + access control.

Core functions:
- get_user_org_paths() — returns all ltree paths for a user (for SQL filtering)
- build_access_filter() — returns a SQL WHERE fragment combining org-tree + classification
- manage org nodes (CRUD)
- manage user memberships
"""
from __future__ import annotations

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_org_paths(db: AsyncSession, user_id: int) -> list[str]:
    """Get all org paths the user belongs to (for ltree ancestor matching)."""
    rows = await db.execute(sql_text("""
        SELECT n.path::text AS path
        FROM user_org_memberships m
        JOIN org_nodes n ON n.id = m.org_node_id
        WHERE m.user_id = :uid AND n.is_active = true
    """), {"uid": user_id})
    return [r[0] for r in rows.all()]


async def get_user_clearance(db: AsyncSession, user_id: int) -> int:
    """Get the user's clearance level (0-3)."""
    row = await db.execute(sql_text(
        "SELECT clearance_level FROM users WHERE id = :uid"
    ), {"uid": user_id})
    result = row.scalar()
    return result if result is not None else 1


def build_access_filter(
    user_paths: list[str],
    user_clearance: int,
    user_id: int,
    params: dict,
    document_alias: str = "d",
) -> str:
    """Build a SQL WHERE clause that filters documents by:
    1. Org tree: document's scope_path is an ancestor of (or equal to) any user path
    2. Classification: document.classification <= user_clearance
    3. Overrides: explicit grant for the user

    Uses ltree's <@ operator (is ancestor of):
    d.scope_path <@ '1.3.7' means d is scoped to a node that is an ancestor of 1.3.7
    → user in node 7 can see documents scoped to nodes 1, 3, or 7 (but not 8)
    """
    if not user_paths:
        return "1=0"  # no org membership = no access

    conditions = []
    for i, path in enumerate(user_paths):
        param_key = f"org_path_{i}"
        params[param_key] = path
        # scope_path <@ user_path: document is scoped to an ancestor of the user's node
        # This means: a document scoped to "Company A" is visible to users in
        # "Company A > Sales" (because Company A is an ancestor of Sales)
        conditions.append(f"{document_alias}.scope_path <@ :{param_key}::ltree")

    params["access_uid"] = user_id
    params["access_clearance"] = user_clearance

    return f"""
        (
            {' OR '.join(conditions)}
            OR {document_alias}.id IN (
                SELECT document_id FROM document_overrides WHERE user_id = :access_uid
            )
        )
        AND {document_alias}.classification <= :access_clearance
    """


# --- Org node CRUD ---

async def create_org_node(
    db: AsyncSession, name: str, node_type: str, parent_id: int | None
) -> dict:
    """Create a new org node. Computes the materialized path from parent."""
    if parent_id:
        row = await db.execute(sql_text(
            "SELECT path FROM org_nodes WHERE id = :pid"
        ), {"pid": parent_id})
        parent_path = row.scalar()
        if not parent_path:
            raise ValueError(f"Parent node {parent_id} not found")
    else:
        parent_path = ""

    # Insert and get the new ID
    result = await db.execute(sql_text(
        "INSERT INTO org_nodes (parent_id, name, node_type, path) "
        "VALUES (:pid, :name, :type, :path::ltree) RETURNING id"
    ), {
        "pid": parent_id,
        "name": name,
        "type": node_type,
        "path": "",  # placeholder — will update after we have the ID
    })
    new_id = result.scalar()

    # Compute path: parent_path + "." + new_id (or just new_id for root)
    new_path = f"{parent_path}.{new_id}" if parent_path else str(new_id)
    await db.execute(sql_text(
        "UPDATE org_nodes SET path = :path::ltree WHERE id = :id"
    ), {"path": new_path, "id": new_id})
    await db.commit()

    return {"id": new_id, "name": name, "node_type": node_type,
            "parent_id": parent_id, "path": new_path}


async def get_org_tree(db: AsyncSession) -> list[dict]:
    """Get the full org tree, ordered by path (hierarchical order)."""
    rows = await db.execute(sql_text("""
        SELECT id, parent_id, name, node_type, path::text, sort_order, is_active
        FROM org_nodes WHERE is_active = true
        ORDER BY path
    """))
    return [dict(r) for r in rows.mappings().all()]


async def update_org_node(db: AsyncSession, node_id: int, name: str | None = None,
                          node_type: str | None = None, sort_order: int | None = None) -> bool:
    """Update an org node. Does NOT support moving (parent change) — that requires
    path recomputation for all descendants. Add as a follow-up if needed."""
    sets = []
    params = {"id": node_id}
    if name is not None:
        sets.append("name = :name")
        params["name"] = name
    if node_type is not None:
        sets.append("node_type = :type")
        params["type"] = node_type
    if sort_order is not None:
        sets.append("sort_order = :so")
        params["so"] = sort_order
    if not sets:
        return False
    sets.append("updated_at = now()")
    await db.execute(sql_text(
        f"UPDATE org_nodes SET {', '.join(sets)} WHERE id = :id"
    ), params)
    await db.commit()
    return True


async def delete_org_node(db: AsyncSession, node_id: int) -> bool:
    """Soft-delete an org node (set is_active=false).
    Does NOT delete — preserves audit trail and allows reactivation.
    Documents scoped to this node become inaccessible (scope_org_id points to inactive node).
    Admins must re-scope documents before deleting a node."""
    await db.execute(sql_text(
        "UPDATE org_nodes SET is_active = false WHERE id = :id"
    ), {"id": node_id})
    await db.commit()
    return True


# --- User membership management ---

async def assign_user_to_node(
    db: AsyncSession, user_id: int, org_node_id: int,
    is_primary: bool = False, role: str = "member"
) -> dict:
    """Assign a user to an org node. Upsert — updates if already exists."""
    await db.execute(sql_text("""
        INSERT INTO user_org_memberships (user_id, org_node_id, is_primary, role)
        VALUES (:uid, :nid, :primary, :role)
        ON CONFLICT (user_id, org_node_id)
        DO UPDATE SET is_primary = EXCLUDED.is_primary, role = EXCLUDED.role
    """), {"uid": user_id, "nid": org_node_id,
           "primary": is_primary, "role": role})
    await db.commit()
    return {"user_id": user_id, "org_node_id": org_node_id,
            "is_primary": is_primary, "role": role}


async def remove_user_from_node(db: AsyncSession, user_id: int, org_node_id: int) -> bool:
    """Remove a user from an org node."""
    await db.execute(sql_text(
        "DELETE FROM user_org_memberships WHERE user_id = :uid AND org_node_id = :nid"
    ), {"uid": user_id, "nid": org_node_id})
    await db.commit()
    return True


async def get_user_memberships(db: AsyncSession, user_id: int) -> list[dict]:
    """Get all org node memberships for a user."""
    rows = await db.execute(sql_text("""
        SELECT m.org_node_id, m.is_primary, m.role,
               n.name, n.node_type, n.path::text
        FROM user_org_memberships m
        JOIN org_nodes n ON n.id = m.org_node_id
        WHERE m.user_id = :uid AND n.is_active = true
        ORDER BY m.is_primary DESC, n.path
    """), {"uid": user_id})
    return [dict(r) for r in rows.mappings().all()]
```

### File 3: New API `backend/app/api/organization.py`

```python
"""Brief #17: Organization tree management API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.api.auth import require_admin
from app.core.database import get_db
from app.models.user import User
from app.services import org_tree

router = APIRouter(prefix="/api/organization", tags=["organization"])


# --- Org node CRUD ---

class OrgNodeRequest(BaseModel):
    name: str
    node_type: str = "department"
    parent_id: Optional[int] = None

@router.get("/tree")
async def get_tree(
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Get the full org tree."""
    return await org_tree.get_org_tree(db)

@router.post("/nodes")
async def create_node(
    req: OrgNodeRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Create a new org node."""
    return await org_tree.create_org_node(db, req.name, req.node_type, req.parent_id)

@router.patch("/nodes/{node_id}")
async def update_node(
    node_id: int,
    req: OrgNodeRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Update an org node."""
    await org_tree.update_org_node(db, node_id, req.name, req.node_type)
    return {"id": node_id}

@router.delete("/nodes/{node_id}")
async def delete_node(
    node_id: int,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an org node."""
    await org_tree.delete_org_node(db, node_id)
    return {"deleted": node_id}


# --- User memberships ---

class MembershipRequest(BaseModel):
    user_id: int
    org_node_id: int
    is_primary: bool = False
    role: str = "member"

@router.post("/memberships")
async def assign_membership(
    req: MembershipRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Assign a user to an org node."""
    return await org_tree.assign_user_to_node(
        db, req.user_id, req.org_node_id, req.is_primary, req.role)

@router.delete("/memberships/{user_id}/{org_node_id}")
async def remove_membership(
    user_id: int,
    org_node_id: int,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Remove a user from an org node."""
    await org_tree.remove_user_from_node(db, user_id, org_node_id)
    return {"removed": True}

@router.get("/users/{user_id}/memberships")
async def get_memberships(
    user_id: int,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Get all org memberships for a user."""
    return await org_tree.get_user_memberships(db, user_id)


# --- User clearance ---

class ClearanceRequest(BaseModel):
    clearance_level: int  # 0-3

@router.patch("/users/{user_id}/clearance")
async def set_clearance(
    user_id: int,
    req: ClearanceRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Set a user's clearance level (0=public, 1=internal, 2=confidential, 3=restricted)."""
    if not 0 <= req.clearance_level <= 3:
        raise HTTPException(400, "clearance_level must be 0-3")
    from sqlalchemy import text
    await db.execute(text(
        "UPDATE users SET clearance_level = :cl WHERE id = :uid"
    ), {"cl": req.clearance_level, "uid": user_id})
    await db.commit()
    return {"user_id": user_id, "clearance_level": req.clearance_level}
```

### File 4: Register router in `backend/app/main.py`

```python
from app.api import ..., organization, ...
app.include_router(organization.router)
```

### File 5: Frontend — Admin Organization page

**File:** `frontend/src/app/admin/organization/page.tsx`

A page with two panels:

**Left panel: Org tree viewer**
- Renders the tree hierarchically (indented by depth)
- Each node shows: name, type badge (group/company/department/team), user count
- Click a node to select it → right panel shows details
- "Add Node" button → form with name, type dropdown, parent selector
- Edit/Delete buttons on each node

**Right panel: Node details**
- Selected node's name, type, path
- List of users assigned to this node (with add/remove)
- "Assign User" button → user picker modal
- Documents scoped to this node (read-only count)

### File 6: Sidebar nav — add Organization to ADMINISTRATION section

**File:** `frontend/src/components/sidebar-nav.tsx`

In the ADMINISTRATION section items, add:
```typescript
{ href: "/admin/organization/", icon: Network, label: tf("nav.organization", "Organization") },
```

### File 7: i18n strings

```json
// en.json
"nav.organization": "Organization",
"org.title": "Organization Tree",
"org.addNode": "Add Node",
"org.nodeType": "Node Type",
"org.parentNode": "Parent Node",
"org.assignUser": "Assign User",
"org.clearance": "Clearance Level",
"org.clearance.public": "Public",
"org.clearance.internal": "Internal",
"org.clearance.confidential": "Confidential",
"org.clearance.restricted": "Restricted",
"org.type.group": "Group",
"org.type.company": "Company",
"org.type.department": "Department",
"org.type.team": "Team"

// ar.json
"nav.organization": "الهيكل التنظيمي",
"org.title": "شجرة المؤسسة",
"org.addNode": "إضافة عقدة",
"org.nodeType": "نوع العقدة",
"org.parentNode": "العقدة الأم",
"org.assignUser": "تعيين مستخدم",
"org.clearance": "مستوى التصريح",
"org.clearance.public": "عام",
"org.clearance.internal": "داخلي",
"org.clearance.confidential": "سري",
"org.clearance.restricted": "مقيد",
"org.type.group": "مجموعة",
"org.type.company": "شركة",
"org.type.department": "قسم",
"org.type.team": "فريق"
```

---

## Phase 2: Document Scoping on Upload (2-3 days)

### File 1: `backend/app/api/files.py` — add scope + classification to upload

When a user uploads a document, they can optionally specify:
- `scope_org_id` — which org node the document belongs to (default: user's primary org node)
- `classification` — 0-3 (default: 1 = internal)

Add these as optional form fields in the upload endpoint:

```python
@router.post("/upload")
async def upload_files(
    request: Request,
    files: list[UploadFile] | None = File(default=None),
    file: UploadFile | None = File(default=None),
    folder: str = "/",
    scope_org_id: int | None = Form(default=None),
    classification: int | None = Form(default=None),
    current_user: User = Depends(require_roles(UserRole.editor)),
    db: AsyncSession = Depends(get_db),
):
    # ... existing upload logic ...

    # Brief #17: set document scope + classification
    # Default scope: user's primary org node
    if scope_org_id is None:
        # Get user's primary org node
        from app.services.org_tree import get_user_memberships
        memberships = await get_user_memberships(db, current_user.id)
        primary = next((m for m in memberships if m["is_primary"]), None)
        scope_org_id = primary["org_node_id"] if primary else 1  # fallback to root

    # Get the path for the scope_org_id
    from sqlalchemy import text
    scope_row = await db.execute(text(
        "SELECT path FROM org_nodes WHERE id = :oid AND is_active = true"
    ), {"oid": scope_org_id})
    scope_path = scope_row.scalar()
    if not scope_path:
        scope_org_id = 1
        scope_path = "1"

    # Set on the document
    doc.scope_org_id = scope_org_id
    doc.scope_path = scope_path
    doc.classification = classification if classification is not None else 1
```

### File 2: Frontend — upload page additions

**File:** `frontend/src/app/upload/page.tsx`

Add to the upload form:
- **Scope dropdown** — shows the org tree (selectable nodes). Default: user's primary node.
- **Classification dropdown** — 4 options (Public/Internal/Confidential/Restricted). Default: Internal.

### File 3: Frontend — files page shows scope + classification badges

**File:** `frontend/src/app/files/page.tsx`

Add to each file row:
- **Scope badge** — small text showing the org node name (e.g., "Company A > Sales")
- **Classification badge** — colored pill:
  - 🔵 Public (blue)
  - ⚪ Internal (gray)
  - 🟠 Confidential (amber)
  - 🔴 Restricted (red)

---

## Phase 3: Access Control Integration (2-3 days)

### File 1: `backend/app/services/permissions.py` — replace permission_clause

Replace the current collection-based `permission_clause()` with the new org-tree + classification filter:

```python
"""Brief #17: Org-tree + classification access control.

Replaces the collection-based permission_clause with a two-dimensional filter:
1. Org tree: document scope_path is an ancestor of the user's org path
2. Classification: document.classification <= user.clearance_level
3. Overrides: explicit grants for cross-company collaboration
"""
from __future__ import annotations

import contextvars
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text as sql_text

current_search_user: contextvars.ContextVar = contextvars.ContextVar(
    "seekra_current_search_user", default=None
)


def is_admin(user) -> bool:
    role = getattr(user, "role", None)
    value = getattr(role, "value", role)
    return str(value) == "admin"


def is_auditor(user) -> bool:
    role = getattr(user, "role", None)
    value = getattr(role, "value", role)
    return str(value) == "auditor"


async def get_access_filter(
    db: AsyncSession, user, params: dict, document_alias: str = "d"
) -> str:
    """Build a SQL WHERE clause for document access.

    Combines org-tree access + classification clearance + overrides.
    Returns '1=1' for admins and auditors (they see everything).
    """
    if user is None or is_admin(user) or is_auditor(user):
        return "1=1"

    from app.services.org_tree import get_user_org_paths, get_user_clearance

    user_paths = await get_user_org_paths(db, user.id)
    user_clearance = await get_user_clearance(db, user.id)

    from app.services.org_tree import build_access_filter
    return build_access_filter(
        user_paths, user_clearance, user.id, params, document_alias
    )
```

**Important**: This changes `permission_clause` from a **synchronous** function to an **async** function. Every call site that currently does:

```python
perm_sql = permission_clause(user, params, "d")
```

Must change to:

```python
perm_sql = await get_access_filter(db, user, params, "d")
```

### File 2: Update ALL call sites

The `permission_clause` is used in these files — ALL must be updated:

1. `backend/app/api/files.py` — lines 155, 180
2. `backend/app/api/search.py` — line 40
3. `backend/app/api/chat.py` — lines 335, 411, 432, 457, 620, 730, 846, 965
4. `backend/app/api/smart_search.py` — `_filter_clause` function
5. `backend/app/api/entities.py` — lines 33, 63, 115
6. `backend/app/api/visual.py` — any permission checks
7. `backend/app/api/provenance.py` — any permission checks

**This is the riskiest part of the brief.** Every API endpoint that queries documents must use the new access filter. Missing one = security hole (user sees documents they shouldn't).

**Strategy**: Search for every occurrence of `permission_clause` in the codebase and replace each one. The function signature changes (now async + takes db), so the compiler will catch any missed call sites.

### File 3: Update the smart-search ContextVar pattern

The `current_search_user` ContextVar is used by smart-search's internal legs (which don't receive a db session). This needs to be updated to also carry the user's org paths + clearance:

```python
# Instead of just storing the user, store a pre-computed access context
current_search_user: contextvars.ContextVar = contextvars.ContextVar(
    "seekra_current_search_user", default=None
)

# In the smart_search endpoint, before running legs:
from app.services.org_tree import get_user_org_paths, get_user_clearance
user_paths = await get_user_org_paths(db, current_user.id)
user_clearance = await get_user_clearance(db, current_user.id)
current_search_user.set({
    "user": current_user,
    "org_paths": user_paths,
    "clearance": user_clearance,
})
```

Then `_filter_clause` reads from the ContextVar instead of calling `permission_clause`:

```python
def _filter_clause(req, params, document_alias="d"):
    ctx = current_search_user.get()
    if ctx is None or is_admin(ctx["user"]) or is_auditor(ctx["user"]):
        return ""
    from app.services.org_tree import build_access_filter
    return " AND (" + build_access_filter(
        ctx["org_paths"], ctx["clearance"], ctx["user"].id, params, document_alias
    ) + ")"
```

---

## Phase 4: Classification UI + Document Overrides (1-2 days)

### File 1: Frontend — classification badges everywhere

Add classification badges to:
- Files page (each file row)
- Search results (each result card)
- Chat sources (each source)
- Upload form (selector)
- Provenance page

### File 2: API — document overrides

**File:** `backend/app/api/files.py`

Add endpoints:
```python
@router.post("/{doc_id}/overrides")
# Grant a user access to a specific document (cross-company collaboration)

@router.delete("/{doc_id}/overrides/{user_id}")
# Revoke override

@router.get("/{doc_id}/overrides")
# List overrides for a document
```

### File 3: Frontend — override management

On the Files page, add a "Manage Access" button for each document:
- Opens a modal showing current overrides
- "Add Access" → user picker → grants read/write
- "Remove Access" → revokes override
- Shows which users have explicit access beyond org-tree

### File 4: Audit events

Log classification changes + override grants:
```python
# When classification changes:
await audit_event(db, request, current_user.id,
    "CONTENT_CLASSIFICATION_CHANGED",
    f"Document {doc_id} classification changed to {new_level} by {current_user.username}")

# When override granted:
await audit_event(db, request, current_user.id,
    "CONTENT_OVERRIDE_GRANTED",
    f"User {target_user_id} granted {permission} access to document {doc_id} by {current_user.username}")
```

---

## What NOT to touch

- **Collections** — they stay as a document organization concept (folders). Access control moves to org tree, but collections are still used for grouping.
- **The existing user_permissions table** — keep it for backward compatibility. New deployments use org tree; existing deployments can migrate gradually.
- **The audit chain** (Brief #6) — classification changes and override grants are logged as standard audit events.
- **PII detection/masking** — classification and PII are independent. PII masking happens regardless of classification.
- **Entity graph** (Brief #16) — entity queries use the same access filter, no change needed.

## Migration safety

The migration is **additive and backward-compatible**:
1. New columns (`scope_org_id`, `scope_path`, `classification`, `clearance_level`) are added with defaults
2. Existing documents are scoped to the root node (everyone sees everything — same as today)
3. Existing users are assigned to the root node + get clearance level 1 (internal — same as today)
4. The old `permission_clause` is replaced, but the new one returns the same result for root-scoped documents
5. Admins can gradually add org nodes, re-scope documents, and set clearance levels

## How to verify

### Test 1 — Migration applies cleanly
```bash
docker compose exec -T postgres psql -U postgres -d genoa < backend/migrations/20260819_step44_org_tree.sql
docker compose exec -T postgres psql -U postgres -d genoa -c "\dt org_nodes"
docker compose exec -T postgres psql -U postgres -d genoa -c "\d documents" | grep -E "scope_org|classification"
docker compose exec -T postgres psql -U postgres -d genoa -c "\d users" | grep clearance
```

### Test 2 — Root node exists + documents migrated
```bash
docker compose exec -T postgres psql -U postgres -d genoa -c "SELECT * FROM org_nodes WHERE id = 1;"
docker compose exec -T postgres psql -U postgres -d genoa -c "SELECT count(*) FROM documents WHERE scope_org_id = 1;"
```

### Test 3 — All existing documents still visible
```bash
# Login as existing user, search — should return same results as before
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"data retention"}' \
  https://app-internal.seekra.pk/api/smart-search/ | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('results',[])))"
```

### Test 4 — Create org nodes + assign users
```bash
# Create Company A under root
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Company A","node_type":"company","parent_id":1}' \
  https://app-internal.seekra.pk/api/organization/nodes

# Assign a user to Company A
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":5,"org_node_id":2,"is_primary":true}' \
  https://app-internal.seekra.pk/api/organization/memberships
```

### Test 5 — Document scoping works
```bash
# Upload a document scoped to Company A (classification=confidential)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "scope_org_id=2" \
  -F "classification=2" \
  https://app-internal.seekra.pk/api/files/upload

# User in Company A should see it
# User in root only (not in Company A) should NOT see it
# User with clearance=1 (internal) should NOT see it (classification=2 requires clearance>=2)
```

### Test 6 — Admin UI renders
Navigate to `/admin/organization/` — should show the org tree with add/edit/delete.

## Commit messages

Ship as 4 commits:
```
Brief #17.1: Org tree schema + service + API + admin UI
Brief #17.2: Document scoping on upload + classification selector
Brief #17.3: Access control integration (replace permission_clause with org-tree + classification filter)
Brief #17.4: Classification badges + document overrides + audit events
```

## Questions before you start

1. **ltree extension availability?** The `ankane/pgvector` image should have ltree available (it's a standard PostgreSQL contrib module). Verify with `SELECT * FROM pg_available_extensions WHERE name = 'ltree';`. If not available, fall back to a text-based path column with `LIKE` queries (slower but works everywhere).

2. **Should the migration auto-create child nodes for existing collections?** My take: no — let the admin manually build the org tree. Collections and org nodes are different concepts. Migration only creates the root node + migrates everything to it.

3. **Should non-admin users see the org tree?** My take: no — the org tree management is admin-only. Regular users just see their documents (filtered by their org membership). They don't need to know the full org structure.

4. **Should the permission_clause replacement be phased?** My take: no — replace it all at once in Phase 3. The old function returns "1=1" for admins and the new one does too. The difference is only for non-admin users, who currently see root documents (which are now root-node-scoped — same result). So the replacement is safe.

5. **Should we support moving org nodes (changing parent)?** My take: not in v1. Moving a node requires recomputing paths for all descendants. Add as a follow-up if needed. For now, delete + recreate is the workaround.
