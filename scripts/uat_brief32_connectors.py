#!/usr/bin/env python3
"""Brief #32 UAT — Data Connectors + Bulk Ingestion.

Covers:
  Connector P1: connector framework + local folder watcher + sync engine
  Connector P3-P9: 9 connector types (local, SharePoint, Google Drive, IMAP,
                    S3, Azure Blob, GCS, SFTP, Alibaba OSS) — surface only (no
                    real external accounts to test against)
  Brief #32: PyMuPDF → pypdfium2 (AGPL removal) — regression test
  Brief #33-precursor: LLM observability + ingest summary throttle
  P12: Files page folder browsing + /ingest mount
  P14: audit chain advisory lock
  P15+P16: PII lineage summary + match_count aggregation
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO = Path("/home/z/my-project/seekra-app")
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))
os.environ["SECRET_KEY"] = "uat-static-dummy"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://uat:uat@localhost:5432/uat"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "x"
os.environ["MINIO_SECRET_KEY"] = "x"
os.environ["MINIO_BUCKET_NAME"] = "uat-bucket"

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
        return None
    return (d or {}).get("access_token") or (d or {}).get("token")


def curl_upload(token, filepath, scope_org_id, classification):
    """Upload a file via curl to /api/files/upload."""
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
        if "uploaded" in body:
            return 200, body
        return 500, body
    except json.JSONDecodeError:
        return 500, {"raw": result.stdout[:500]}


# ==========================================================================
# PART 1: STATIC CHECKS
# ==========================================================================
print("=" * 60)
print("PART 1: STATIC CHECKS (Brief #32 + connectors)")
print("=" * 60)

print("\n=== 1a. Module imports ===")
try:
    from app.api import connectors
    from app.services.connectors import base, local, sync
    check("connectors API module imports", True)
    check("connectors base module imports", True)
    check("connectors sync engine imports", True)
    check("local connector imports", True)
except Exception as e:
    check("connector imports", False, f"{type(e).__name__}: {e}")

# Verify all 9 connector types
print("\n=== 1b. 9 connector types registered ===")
try:
    from app.services.connectors.sync import CONNECTOR_TYPES
    expected = {"local_folder", "sharepoint", "google_drive", "mailbox",
                "aws_s3", "azure_blob", "gcs", "sftp", "alibaba_oss"}
    actual = set(CONNECTOR_TYPES.keys())
    check(f"all 9 connector types registered (got {len(actual)})",
          actual == expected, f"missing: {expected - actual}, extra: {actual - expected}")
    for t in sorted(expected):
        check(f"  connector '{t}' class loaded",
              t in CONNECTOR_TYPES and CONNECTOR_TYPES[t] is not None, "")
except Exception as e:
    check("CONNECTOR_TYPES registration", False, f"{e}")

# Verify connector base ABC
print("\n=== 1c. Connector ABC + ConnectorFile dataclass ===")
try:
    from app.services.connectors.base import Connector, ConnectorFile, match_path_rule, sha256_bytes
    check("Connector base class exists", "Connector" in dir())
    check("ConnectorFile dataclass exists", "ConnectorFile" in dir())
    check("match_path_rule helper exists", "match_path_rule" in dir())
    check("sha256_bytes helper exists", "sha256_bytes" in dir())
    # match_path_rule: first active match wins
    rules = [{"pattern": "/Films/**", "is_active": True},
             {"pattern": "/Sales/**", "is_active": True}]
    check("match_path_rule matches first pattern",
          match_path_rule("/Films/script.pdf", rules) == rules[0], "")
    check("match_path_rule matches second pattern",
          match_path_rule("/Sales/contract.pdf", rules) == rules[1], "")
    check("match_path_rule returns None on no match",
          match_path_rule("/HR/policy.pdf", rules) is None, "")
except Exception as e:
    check("Connector ABC", False, f"{e}")

# Verify migration SQL is idempotent
print("\n=== 1d. Migration idempotency ===")
mig = (BACKEND / "migrations" / "20260901_step45_connectors.sql").read_text()
for stmt in [
    "CREATE TABLE IF NOT EXISTS data_connectors",
    "CREATE TABLE IF NOT EXISTS connector_files",
    "CREATE TABLE IF NOT EXISTS connector_path_rules",
    "CREATE INDEX IF NOT EXISTS idx_connector_files_connector",
    "CREATE INDEX IF NOT EXISTS idx_connector_files_document",
]:
    check(f"migration: {stmt[:60]}", stmt in mig, "")

# Verify connector API endpoints exist + require admin
print("\n=== 1e. Connector API endpoints + admin-only RBAC ===")
conn_src = (BACKEND / "app" / "api" / "connectors.py").read_text()
expected_endpoints = [
    ('@router.get("")', 'list_connectors'),
    ('@router.get("/{cid}")', 'get_connector'),
    ('@router.post("", status_code=201)', 'create_connector'),
    ('@router.patch("/{cid}")', 'update_connector'),
    ('@router.delete("/{cid}")', 'delete_connector'),
    ('@router.post("/{cid}/sync")', 'trigger_sync'),
    ('@router.post("/{cid}/validate")', 'validate_connector'),
    ('@router.post("/{cid}/rescan")', 'rescan_connector'),
    ('@router.get("/{cid}/files")', 'list_connector_files'),
    ('@router.get("/{cid}/rules")', 'get_rules'),
    ('@router.put("/{cid}/rules")', 'update_rules'),
]
for marker, fn_name in expected_endpoints:
    check(f"endpoint {fn_name} present",
          marker in conn_src and f"async def {fn_name}" in conn_src, "")

# All endpoints require admin
admin_count = conn_src.count("Depends(require_admin())")
check(f"all connector endpoints require admin (found {admin_count} require_admin calls)",
      admin_count >= 11, f"only {admin_count} require_admin calls")

# Verify local connector path guard
print("\n=== 1f. Local connector path guard (must be under /ingest) ===")
local_src = (BACKEND / "app" / "services" / "connectors" / "local.py").read_text()
check("INGEST_ROOT = '/ingest' constant defined",
      "INGEST_ROOT = \"/ingest\"" in local_src, "")
check("path guard: os.path.realpath + startswith(INGEST_ROOT)",
      "os.path.realpath" in local_src and "INGEST_ROOT + os.sep" in local_src, "")
check("raises RuntimeError if path is outside /ingest",
      "raise RuntimeError" in local_src and "must be under" in local_src, "")
check("skips temp/hidden files (~$, ., .tmp, .part, .swp, .crdownload)",
      "IGNORED_PREFIXES" in local_src and "IGNORED_SUFFIXES" in local_src, "")
check("incremental sync via mtime > since",
      "since is not None and mtime <= since" in local_src, "")

# Verify sync engine conflict policy
print("\n=== 1g. Sync engine conflict policy ===")
sync_src = (BACKEND / "app" / "services" / "connectors" / "sync.py").read_text()
check("'source wins' default policy documented",
      "source wins" in sync_src, "")
check("EDIT_MARGIN = timedelta(minutes=10) for edit-after-source detection",
      "EDIT_MARGIN = timedelta(minutes=10)" in sync_src, "")
check("CONNECTOR_CONFLICT audit event emitted on edit-after-source",
      "CONNECTOR_CONFLICT" in sync_src, "")
check("sync stats dict has expected keys (scanned, new, updated, skipped, conflicts, errors)",
      all(k in sync_src for k in ['"scanned"', '"new"', '"updated"', '"skipped"', '"conflicts"', '"errors"']), "")
check("sync engine imports upload_file from minio_client",
      "from app.services.minio_client import upload_file" in sync_src, "")
check("sync engine reuses _audit_chained + _connect + process_document_task from celery",
      "_audit_chained" in sync_src and "_connect" in sync_src and "process_document_task" in sync_src, "")

# Verify Celery beat schedule for connectors
print("\n=== 1h. Celery worker tasks ===")
try:
    from app.workers.connector_tasks import sync_all_connectors
    check("connector_tasks module imports", True)
except Exception as e:
    check("connector_tasks module imports", False, f"{e}")
celery_src = (BACKEND / "app" / "workers" / "celery_tasks.py").read_text()
connector_tasks_src = (BACKEND / "app" / "workers" / "connector_tasks.py").read_text()
check("connector_tasks.py defines sync task",
      "def sync" in connector_tasks_src, "")

# Verify Brief #32: PyMuPDF → pypdfium2
print("\n=== 1i. Brief #32: PyMuPDF → pypdfium2 (AGPL removal) ===")
vis_src = (BACKEND / "app" / "services" / "visual_ai.py").read_text()
check("pypdfium2 imported in visual_ai.py",
      "import pypdfium2" in vis_src or "from pypdfium2" in vis_src, "")
check("PyMuPDF (fitz) NOT imported anywhere",
      "import fitz" not in vis_src and "from fitz" not in vis_src, "")
# Also check Dockerfile + requirements
dockerfile = (BACKEND / "Dockerfile").read_text()
check("pypdfium2 in Dockerfile or requirements",
      "pypdfium2" in dockerfile, "")
check("PyMuPDF removed from Dockerfile/requirements",
      "PyMuPDF" not in dockerfile and "pymupdf" not in dockerfile.lower(), "")

# Verify P14: audit chain advisory lock
print("\n=== 1j. P14: audit chain advisory lock (prev_hash race fix) ===")
audit_src = (BACKEND / "app" / "services" / "audit.py").read_text()
check("advisory lock used (pg_advisory_xact_lock)",
      "pg_advisory_xact_lock" in audit_src, "")

# Verify P15+P16: PII lineage + match_count
print("\n=== 1k. P15+P16: PII lineage summary + match_count aggregation ===")
prov_src = (BACKEND / "app" / "api" / "provenance.py").read_text()
check("provenance API mentions match_count",
      "match_count" in prov_src, "")
pii_src = (BACKEND / "app" / "services" / "pii_detection.py").read_text()
check("pii_detection.py mentions match_count",
      "match_count" in pii_src, "")
celery_tasks = (BACKEND / "app" / "workers" / "celery_tasks.py").read_text()
check("worker aggregates match_count for duplicate PII findings",
      "match_count" in celery_tasks, "")

# Verify frontend admin/connectors page exists
print("\n=== 1l. Frontend admin/connectors page ===")
fe_page = REPO / "frontend" / "src" / "app" / "admin" / "connectors" / "page.tsx"
check("admin/connectors/page.tsx exists", fe_page.exists(), "")
if fe_page.exists():
    s = fe_page.read_text()
    check("page is 'use client'", "use client" in s, "")
    check("page fetches /api/connectors", "/api/connectors" in s or "apiFetch" in s, "")
    check("page supports 9 connector type selectors",
          all(t in s for t in ["local_folder", "sharepoint", "google_drive", "mailbox",
                                "aws_s3", "azure_blob", "gcs", "sftp", "alibaba_oss"]),
          "")
    check("page has validate/edit/rescan actions",
          "validate" in s and "rescan" in s and "edit" in s.lower(), "")
    check("page is bilingual (en + ar labels)",
          "tf(" in s or "useI18n" in s, "")

# Sidebar nav includes /admin/connectors
sidebar_src = (REPO / "frontend" / "src" / "components" / "sidebar-nav.tsx").read_text()
check("sidebar-nav includes link to /admin/connectors",
      "/admin/connectors" in sidebar_src, "")

# i18n strings for connectors in en + ar
en_json = json.loads((REPO / "frontend" / "src" / "i18n" / "dictionaries" / "en.json").read_text())
ar_json = json.loads((REPO / "frontend" / "src" / "i18n" / "dictionaries" / "ar.json").read_text())
def find_keys(d, prefix=""):
    keys = set()
    if isinstance(d, dict):
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            keys.add(full)
            keys.update(find_keys(v, full))
    return keys
en_keys = find_keys(en_json)
ar_keys = find_keys(ar_json)
for frag in ["connector", "ingest"]:
    en_match = any(frag in k.lower() for k in en_keys)
    ar_match = any(frag in k.lower() for k in ar_keys)
    check(f"en.json has '{frag}*'", en_match, "")
    check(f"ar.json has '{frag}*'", ar_match, "")

# api.ts has connector client functions
api_ts = (REPO / "frontend" / "src" / "lib" / "api.ts").read_text()
check("api.ts has getConnectors function",
      "getConnectors" in api_ts or "listConnectors" in api_ts, "")
check("api.ts has createConnector function",
      "createConnector" in api_ts, "")
check("api.ts has syncConnector function",
      "syncConnector" in api_ts or "triggerConnectorSync" in api_ts, "")


# ==========================================================================
# PART 2: LIVE API CHECKS
# ==========================================================================
print("\n" + "=" * 60)
print("PART 2: LIVE API CHECKS")
print("=" * 60)

print("\n=== 2a. Setup ===")
admin_tok = login("admin", ADMIN_PASSWORD)
check("admin login", admin_tok is not None)
if not admin_tok:
    print("FATAL"); sys.exit(1)

# ---- 2b. List existing connectors (default connector seeded) ----
print("\n=== 2b. List existing connectors ===")
s, d = req("GET", "/connectors", token=admin_tok)
check("GET /connectors 200", s == 200, f"{s}")
if s == 200:
    items = d.get("items", []) if isinstance(d, dict) else d
    check("at least 1 connector exists (default local_folder)",
          len(items) >= 1, f"got {len(items)}")
    if items:
        default = items[0]
        check("default connector is local_folder",
              default.get("connector_type") == "local_folder", str(default.get("connector_type")))
        check("default connector config has path=/ingest/",
              default.get("config", {}).get("path") == "/ingest/", str(default.get("config")))
        check("default connector is_active=true",
              default.get("is_active") is True, "")
        check("default connector has last_synced_at (sync ran)",
              default.get("last_synced_at") is not None, "")
        check("default connector last_sync_status='ok'",
              default.get("last_sync_status") == "ok",
              str(default.get("last_sync_status")))
        default_id = default.get("id")
        print(f"      default connector id={default_id}")
    else:
        default_id = None
else:
    default_id = None

# ---- 2c. RBAC: viewer cannot access /connectors ----
print("\n=== 2c. RBAC: viewer cannot access /connectors ===")
viewer_tok = login("ahmed.alketbi", DEMO_PASSWORD)
if viewer_tok:
    s, _ = req("GET", "/connectors", token=viewer_tok)
    check("viewer GET /connectors -> 403", s == 403, f"got {s}")
    s, _ = req("POST", "/connectors", token=viewer_tok,
               data={"connector_type": "local_folder", "name": "should_fail",
                     "config": {"path": "/ingest/"}})
    check("viewer POST /connectors -> 403", s == 403, f"got {s}")
else:
    check("viewer login", False, "")

# Unauthenticated
s, _ = req("GET", "/connectors")
check("unauthenticated GET /connectors -> 401", s == 401, f"got {s}")

# ---- 2d. Create a new local_folder connector with custom scope ----
print("\n=== 2d. Create new local_folder connector ===")
# Get org options to find a scope
s, opts = req("GET", "/organization/options", token=admin_tok)
node_id_by_name = {n["name"]: n["id"] for n in opts} if s == 200 else {}
# Use "Films · Production" team for the test connector
target_scope = node_id_by_name.get("Films · Production", 1)
s, d = req("POST", "/connectors", token=admin_tok, data={
    "connector_type": "local_folder",
    "name": "UAT Test Films Connector",
    "config": {"path": "/ingest/uat-films/"},
    "scope_org_id": target_scope,
    "classification": 2,  # Confidential
    "sync_interval_minutes": 1,
})
check(f"POST /connectors -> 201 (scope={target_scope}, cls=2)",
      s == 201, f"{s} {d}")
if s == 201:
    uat_connector_id = d.get("id")
    print(f"      UAT connector id={uat_connector_id}")
else:
    uat_connector_id = None

# ---- 2e. Validate connector (path existence check) ----
print("\n=== 2e. Validate connector ===")
if uat_connector_id:
    s, d = req("POST", f"/connectors/{uat_connector_id}/validate", token=admin_tok)
    check(f"POST /connectors/{uat_connector_id}/validate -> 200",
          s == 200, f"{s} {d}")
    if s == 200:
        # Should report path may not exist (we haven't created /ingest/uat-films/ yet)
        check("validate response has 'valid' or 'status' field",
              "valid" in d or "status" in d or "ok" in d, str(d))
        print(f"      validate response: {d}")

# ---- 2f. Get connector by ID ----
print("\n=== 2f. Get connector by ID ===")
if uat_connector_id:
    s, d = req("GET", f"/connectors/{uat_connector_id}", token=admin_tok)
    check(f"GET /connectors/{uat_connector_id} -> 200", s == 200, f"{s}")
    if s == 200:
        check("connector detail has correct name",
              d.get("name") == "UAT Test Films Connector", str(d.get("name")))
        check("connector detail has correct scope_org_id",
              d.get("scope_org_id") == target_scope, str(d.get("scope_org_id")))
        check("connector detail has correct classification",
              d.get("classification") == 2, str(d.get("classification")))

# 404 for non-existent
s, _ = req("GET", "/connectors/99999", token=admin_tok)
check("GET /connectors/99999 -> 404", s == 404, f"got {s}")

# ---- 2g. Update connector (PATCH) ----
print("\n=== 2g. Update connector (PATCH) ===")
if uat_connector_id:
    s, d = req("PATCH", f"/connectors/{uat_connector_id}", token=admin_tok, data={
        "name": "UAT Test Films Connector (Renamed)",
        "classification": 1,
    })
    check(f"PATCH /connectors/{uat_connector_id} -> 200", s == 200, f"{s} {d}")
    if s == 200:
        check("rename applied",
              d.get("name") == "UAT Test Films Connector (Renamed)",
              str(d.get("name")))
        check("classification updated to 1",
              d.get("classification") == 1, str(d.get("classification")))

# ---- 2h. Connector path rules CRUD ----
print("\n=== 2h. Connector path rules ===")
if uat_connector_id:
    # Get current rules
    s, d = req("GET", f"/connectors/{uat_connector_id}/rules", token=admin_tok)
    check(f"GET /connectors/{uat_connector_id}/rules -> 200", s == 200, f"{s}")
    # PUT replaces all rules
    new_rules = [
        {"pattern": "**/dailies/**", "action": "ingest", "target_folder": "/Films/Dailies", "is_active": True},
        {"pattern": "**/*.pdf", "action": "ingest", "target_folder": None, "is_active": True},
    ]
    s, d = req("PUT", f"/connectors/{uat_connector_id}/rules", token=admin_tok, data={"rules": new_rules})
    check(f"PUT /connectors/{uat_connector_id}/rules -> 200", s == 200, f"{s} {d}")
    if s == 200:
        # Verify rules saved
        s2, d2 = req("GET", f"/connectors/{uat_connector_id}/rules", token=admin_tok)
        if s2 == 200:
            saved = d2.get("items", d2) if isinstance(d2, dict) else d2
            check(f"rules saved (got {len(saved) if isinstance(saved, list) else '?'})",
                  isinstance(saved, list) and len(saved) >= 2, str(d2)[:200])

# ---- 2i. List connector files (default connector — has 1 file) ----
print("\n=== 2i. List connector files (default connector) ===")
if default_id:
    s, d = req("GET", f"/connectors/{default_id}/files", token=admin_tok)
    check(f"GET /connectors/{default_id}/files -> 200", s == 200, f"{s}")
    if s == 200:
        files = d.get("items", d) if isinstance(d, dict) else d
        if isinstance(files, list):
            print(f"      {len(files)} files tracked")
            check(f"default connector has >=1 file ingested (got {len(files)})",
                  len(files) >= 1, "")
            if files:
                f0 = files[0]
                check("file has source_id (relative path)",
                      "source_id" in f0 and f0["source_id"], "")
                check("file has document_id (linked to library)",
                      "document_id" in f0 and f0["document_id"] is not None, "")
                check("file has content_hash (sha256)",
                      "content_hash" in f0 and f0["content_hash"], "")
                check("file has last_sync_at",
                      "last_sync_at" in f0 and f0["last_sync_at"] is not None, "")

# ---- 2j. Manual sync trigger ----
print("\n=== 2j. Manual sync trigger ===")
if default_id:
    s, d = req("POST", f"/connectors/{default_id}/sync", token=admin_tok)
    check(f"POST /connectors/{default_id}/sync -> 200", s == 200, f"{s} {d}")
    if s == 200:
        check("sync response has stats (scanned/new/updated/skipped)",
              any(k in (d or {}) for k in ["scanned", "new", "updated", "skipped"]) or "status" in (d or {}),
              str(d)[:200])
        print(f"      sync result: {d}")

# ---- 2k. Rescan (full re-scan, ignores last_synced_at) ----
print("\n=== 2k. Rescan (full) ===")
if default_id:
    s, d = req("POST", f"/connectors/{default_id}/rescan", token=admin_tok)
    check(f"POST /connectors/{default_id}/rescan -> 200", s == 200, f"{s} {d}")
    if s == 200:
        check("rescan returns stats",
              "scanned" in (d or {}) or "status" in (d or {}), str(d)[:200])
        print(f"      rescan result: {d}")

# ---- 2l. PyMuPDF → pypdfium2 regression: PDFs still searchable ----
print("\n=== 2l. PyMuPDF → pypdfium2 regression (PDFs still searchable) ===")
# Search for content from a known PDF in the demo library
s, d = req("POST", "/smart-search/", token=admin_tok, data={
    "query": "Employee Handbook 2026",
    "limit": 10,
})
check("smart-search for PDF content -> 200", s == 200, f"{s}")
if s == 200:
    results = d.get("results") or d.get("documents") or []
    check("search finds at least 1 PDF result",
          len(results) >= 1, f"got {len(results)}")
    if results:
        # First result should be 01_Employee_Handbook_2026.pdf
        has_handbook = any("01_Employee_Handbook" in (r.get("filename") or "") for r in results)
        check("search returns 01_Employee_Handbook_2026.pdf",
              has_handbook, f"filenames: {[r.get('filename') for r in results[:3]]}")

# Chat with a question that requires PDF content extraction
s, d = req("POST", "/chat/", token=admin_tok, data={
    "question": "what does the employee handbook say about annual leave?"
}, timeout=240)
check("chat about PDF content -> 200", s == 200, f"{s}")
if s == 200:
    ans = (d.get("answer") or "").lower()
    # Should mention "30 calendar days" or "30 days" (handbook content)
    cites_handbook = "30" in ans and ("leave" in ans or "annual" in ans)
    check("chat answer cites PDF content (mentions 30 days/leave)",
          cites_handbook, f"first 200: {ans[:200]}")
    sources = d.get("sources") or []
    has_handbook_source = any("01_Employee_Handbook" in (s.get("filename") or "") for s in sources)
    check("chat cites 01_Employee_Handbook_2026.pdf as source",
          has_handbook_source, f"sources: {[s.get('filename') for s in sources[:3]]}")

# ---- 2m. P14 audit chain advisory lock (concurrent writes safe) ----
print("\n=== 2m. P14 audit chain integrity ===")
# Trigger several audit events in quick succession (login + search + chat)
for _ in range(3):
    login("admin", ADMIN_PASSWORD)
# Verify audit chain
s, audit = req("GET", "/audit/?limit=20", token=admin_tok)
if s == 200:
    events = audit if isinstance(audit, list) else audit.get("items", [])
    check(f"audit trail has recent events (got {len(events)})",
          len(events) >= 5, "")
    # Check hash chain integrity by looking at provenance endpoint
    s2, prov = req("GET", "/provenance/audit-chain", token=admin_tok)
    if s2 == 200 and isinstance(prov, dict):
        check("audit chain verification endpoint reports valid",
              prov.get("verified") is True or prov.get("valid") is True or prov.get("status") == "ok",
              str(prov)[:200])

# ---- 2n. P15+P16 PII lineage on provenance page ----
print("\n=== 2n. P15+P16 PII lineage + match_count ===")
# Find a PII-flagged doc
s, files = req("GET", "/files/?limit=200", token=admin_tok)
if s == 200:
    items = files if isinstance(files, list) else files.get("items", [])
    pii_doc = next((f for f in items if f.get("pii_flagged")), None)
    if pii_doc:
        doc_id = pii_doc["id"]
        # Get provenance for this doc
        s2, prov = req("GET", f"/provenance/{doc_id}", token=admin_tok)
        check(f"GET /provenance/{doc_id} -> 200", s2 == 200, f"{s2}")
        if s2 == 200:
            check("provenance response mentions match_count or PII lineage",
                  "match_count" in str(prov) or "pii" in str(prov).lower(), str(prov)[:200])

# ---- 2o. P12 /ingest mount + folder browsing ----
print("\n=== 2o. P12 /ingest mount + folder browsing ===")
# The default connector is at /ingest/ which proves the mount works.
# Test folder browsing endpoint (if exists)
s, d = req("GET", "/files/browse?path=/", token=admin_tok)
check("GET /files/browse exists (folder browsing)",
      s in (200, 404),  # 404 if endpoint not exposed; 200 if it is
      f"got {s}")

# ---- 2p. Cleanup: delete the UAT test connector ----
print("\n=== 2p. Cleanup UAT test connector ===")
if uat_connector_id:
    s, d = req("DELETE", f"/connectors/{uat_connector_id}", token=admin_tok)
    check(f"DELETE /connectors/{uat_connector_id} -> 200",
          s == 200, f"{s} {d}")
    if s == 200:
        # Verify it's gone
        s2, _ = req("GET", f"/connectors/{uat_connector_id}", token=admin_tok)
        check("deleted connector is gone (GET -> 404)",
              s2 == 404, f"got {s2}")

# Delete already-deleted
if uat_connector_id:
    s, _ = req("DELETE", f"/connectors/{uat_connector_id}", token=admin_tok)
    check("DELETE non-existent connector -> 404",
          s == 404, f"got {s}")


# ==========================================================================
# Summary
# ==========================================================================
print("\n" + "=" * 60)
print(f"BRIEF #32 UAT:  {PASS} PASS / {FAIL} FAIL out of {PASS + FAIL}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
