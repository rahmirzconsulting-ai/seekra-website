# Brief #32 — External Data Connectors + Bulk Folder Ingestion

**Author:** RahMirz (delivered to Kimi for implementation)
**Date:** 30 August 2026
**Status:** Ready for implementation
**Estimated effort:** 3–4 weeks (6 phases)
**Predecessor:** Brief #17 (org tree + classification) — connectors will infer scope + classification from source paths

---

## 1. Problem

Every customer demo ends the same way: the client loves the search, the chat, the audit trail, then asks "ok, but how do I get my 50,000 SharePoint documents in?" The current answer — "manually, one upload at a time, via the /files page" — kills deals. Seekra needs a way to ingest bulk content from existing enterprise sources without manual upload.

A secondary gap: even for fresh uploads, the UI accepts only one file per request. A user with 20 files to upload must click "Upload" 20 times.

## 2. Goals

1. **Local folder watcher** — drop files on a designated mount point, they auto-ingest within seconds. Demo-magical.
2. **Multi-file bulk upload UI** — drag-drop 20 files at once, with per-file progress and per-file scope+classification pickers.
3. **SharePoint / OneDrive connector** — most common enterprise source in Gulf market.
4. **Google Drive connector** — second most common.
5. **SMTP email attachment ingest** — forward `ingest@{tenant}.seekra.pk` → auto-upload with sender-based scope inference.
6. **Conflict resolution** — when a source file is modified, Seekra versions it (using Brief #39's existing versioning) instead of overwriting.

## 3. Non-goals

- **No bidirectional sync** — connectors are read-only into Seekra; deleting a doc in Seekra does not delete it in SharePoint.
- **No real-time push from cloud sources** — SharePoint webhooks and Drive push notifications are phase 7+ (out of scope here). Initial connectors are poll-based.
- **No content transformation** — files are ingested as-is; no format conversion, no OCR of scanned PDFs (already handled by the existing indexing pipeline).
- **No cross-tenant connector sharing** — connectors are configured per tenant.

## 4. Architecture

### 4.1 Connector framework

A pluggable adapter pattern. Each connector implements a small Python interface:

```python
# backend/app/services/connectors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

@dataclass
class ConnectorFile:
    """A file discovered by a connector."""
    source_id: str          # unique ID in the source system (e.g. SharePoint item ID)
    path: str               # full path in source, e.g. "/Films/Production/script.pdf"
    filename: str           # basename
    size: int
    content_hash: str | None # sha256 of content if cheap to compute; else None
    modified_at: datetime
    connector_id: str        # which connector discovered this file

class Connector(ABC):
    """Base class for all data connectors."""
    connector_type: str     # "local_folder", "sharepoint", "google_drive", "smtp"

    @abstractmethod
    async def list_changes(self, since: datetime | None) -> AsyncIterator[ConnectorFile]:
        """Yield files added or modified since `since`. None = full scan."""

    @abstractmethod
    async def stream_bytes(self, file: ConnectorFile) -> bytes:
        """Download the file's content."""

    @abstractmethod
    async def infer_scope(self, file: ConnectorFile) -> tuple[int | None, int]:
        """Return (scope_org_id, classification) based on the file's path.
        scope_org_id=None means root. classification default 1 (Internal)."""

    @abstractmethod
    async def close(self) -> None:
        """Release resources (HTTP sessions, file watchers, etc.)."""
```

### 4.2 Sync engine

A Celery task `sync_connector(connector_id)` runs on a schedule (default every 15 minutes, configurable per connector). The task:

1. Loads the connector config from `data_connectors` table (see 4.3).
2. Instantiates the connector.
3. Calls `list_changes(since=last_synced_at)` — yields files added/modified since last sync.
4. For each changed file:
   - Stream bytes → upload to MinIO (reuse existing `_upload_to_minio` helper).
   - Create `documents` row with scope + classification from `infer_scope()`.
   - Reuse existing indexing pipeline (chunking, embedding, PII detection, NER).
   - Record `connector_file` row (see 4.4) for tracking + future conflict detection.
5. Update `last_synced_at` on the connector config.
6. Emit `CONNECTOR_SYNCED` audit event with file count.

### 4.3 Database changes

```sql
-- backend/migrations/20260901_step45_connectors.sql

CREATE TABLE IF NOT EXISTS data_connectors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    connector_type VARCHAR(50) NOT NULL CHECK (
        connector_type IN ('local_folder', 'sharepoint', 'google_drive', 'smtp')
    ),
    config JSONB NOT NULL,           -- connector-specific config (path, credentials, etc.)
    default_scope_org_id INTEGER REFERENCES org_nodes(id),
    default_classification INTEGER NOT NULL DEFAULT 1
        CHECK (default_classification BETWEEN 0 AND 3),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    sync_interval_seconds INTEGER NOT NULL DEFAULT 900,  -- 15 min
    last_synced_at TIMESTAMP,
    last_sync_status VARCHAR(20),    -- 'ok', 'error', 'partial'
    last_error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_data_connectors_active ON data_connectors (is_active);
CREATE INDEX idx_data_connectors_type ON data_connectors (connector_type);

-- Per-file tracking (for incremental sync + conflict detection)
CREATE TABLE IF NOT EXISTS connector_files (
    id SERIAL PRIMARY KEY,
    connector_id INTEGER NOT NULL REFERENCES data_connectors(id) ON DELETE CASCADE,
    source_id VARCHAR(500) NOT NULL,   -- unique in source system
    source_path VARCHAR(1000),
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_content_hash VARCHAR(64),    -- sha256, for change detection
    source_modified_at TIMESTAMP,
    last_synced_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (connector_id, source_id)
);
CREATE INDEX idx_connector_files_doc ON connector_files (document_id);
CREATE INDEX idx_connector_files_modified ON connector_files (source_modified_at);

-- Scope inference rules (path patterns → org node + classification)
CREATE TABLE IF NOT EXISTS connector_path_rules (
    id SERIAL PRIMARY KEY,
    connector_id INTEGER NOT NULL REFERENCES data_connectors(id) ON DELETE CASCADE,
    path_pattern VARCHAR(500) NOT NULL,  -- glob pattern, e.g. "/Films/Production/**"
    scope_org_id INTEGER REFERENCES org_nodes(id),
    classification INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_connector_path_rules_connector ON connector_path_rules (connector_id);
```

### 4.4 Conflict resolution

When the sync engine sees a file whose `source_modified_at` is newer than the corresponding `connector_files.last_synced_at`:

1. If the document has been modified inside Seekra (i.e. `documents.updated_at > connector_files.last_synced_at`): log a conflict — emit `CONNECTOR_CONFLICT` audit event, do NOT overwrite. (Phase 7+ could merge; for now, last-writer-wins inside Seekra.)
2. If the document has NOT been modified inside Seekra: stream the new content, version it using the existing Brief #39 versioning (increment `version_number`, link via `version_group_id`), update `connector_files.source_content_hash` and `last_synced_at`.

## 5. Phases

### Phase 1 — Connector framework + local folder watcher (Week 1)

**Scope:**
- Migration `20260901_step45_connectors.sql` (all tables above).
- `backend/app/services/connectors/base.py` with the `Connector` ABC.
- `backend/app/services/connectors/local_folder.py` — first concrete connector.
  - `list_changes(since)`: walks the configured local path; for each file, stat `mtime` and (if `since` is None or `mtime > since`) yield a `ConnectorFile`. Use `pathlib.Path.rglob()`.
  - `stream_bytes(file)`: open the file, read bytes.
  - `infer_scope(file)`: match the file's path against `connector_path_rules.path_pattern` (use `fnmatch`); first match wins; fall back to `default_scope_org_id` + `default_classification`.
- Celery task `sync_connector(connector_id)` in `backend/app/workers/celery_tasks.py`.
- Celery beat schedule: every 60 seconds, enqueue sync for all active connectors whose `last_synced_at + sync_interval_seconds < now()`. (For local folder watcher, default `sync_interval_seconds = 60` for near-real-time.)
- Admin API:
  - `GET /api/connectors` — list all connectors (admin only)
  - `POST /api/connectors` — create a connector (admin only)
  - `PATCH /api/connectors/{id}` — update config, default scope, interval, active
  - `DELETE /api/connectors/{id}` — soft-delete (set `is_active = false`)
  - `POST /api/connectors/{id}/sync` — manual trigger (admin only)
  - `GET /api/connectors/{id}/files` — list ingested files (admin only)
  - `GET /api/connectors/{id}/path-rules` + `POST` + `PATCH` + `DELETE` for scope inference rules
- Audit events: `CONNECTOR_CREATED`, `CONNECTOR_UPDATED`, `CONNECTOR_DELETED`, `CONNECTOR_SYNCED`, `CONNECTOR_CONFLICT`, `CONNECTOR_ERROR`.
- Frontend `/admin/connectors` page: list, create, edit, deactivate, manual sync, view ingested files.
- i18n strings (en + ar) for all admin UI labels.

**Acceptance criteria:**
- Admin can create a local folder connector pointing at `/ingest/films/` with default scope = "Films · Production" team, default classification = 2 (Confidential).
- Admin adds a path rule: `/ingest/films/dailies/**` → scope "Films · Production", classification 1 (Internal).
- Admin drops `script.pdf` into `/ingest/films/` on the server filesystem.
- Within 60 seconds, the file appears in Seekra's `/files` page with the correct scope + classification, indexed, searchable.
- Admin adds `scene12_take3.mp4` to `/ingest/films/dailies/` — within 60s, ingested with classification 1 (matching the path rule, not the default).
- Admin modifies `script.pdf` in the source folder — within 60s, a new version is created (`version_number = 2`) and the old version is preserved.
- Audit trail shows `CONNECTOR_SYNCED` events with file counts.

### Phase 2 — Multi-file bulk upload UI (Week 1, parallel with Phase 1)

**Scope:**
- New endpoint `POST /api/files/bulk-upload` — accepts a multipart request with multiple `files[]` parts + a single `scope_org_id` + `classification` form field (applied to all files in the batch). Returns `{"uploaded": [{id, filename, status, scope_org_id, classification} for each file]}`.
- Per-file override: if a part has a `scope_org_id_N` or `classification_N` form field (where N matches the file index), use that instead of the batch default.
- Frontend changes in `/files` page:
  - New "Bulk upload" button next to the existing "Upload" button.
  - Opens a drop zone modal accepting drag-drop of multiple files OR file picker with multiple selection.
  - Per-file row in the modal: filename, size, scope dropdown (defaults to batch), classification dropdown (defaults to batch), progress bar.
  - "Start upload" button uploads all files in parallel (max 3 concurrent — configurable).
  - Failed uploads show a retry button per file.
  - Successful uploads show a "View in library" link.
- The existing single-file `POST /api/files/upload` endpoint remains unchanged (backwards compat).

**Acceptance criteria:**
- User drags 10 PDF files into the bulk upload modal.
- All 10 appear as rows with progress bars.
- After upload completes, all 10 are visible in `/files` with the chosen scope + classification.
- If 1 file fails (e.g. exceeds 500MB limit), the other 9 succeed; the failed row shows a retry button.
- Audit trail shows `CONTENT_UPLOAD` events for all 10 (with `bulk_upload=true` detail for the 9 successful).

### Phase 3 — SharePoint / OneDrive connector (Week 2-3)

**Scope:**
- `backend/app/services/connectors/sharepoint.py` — concrete connector.
- Uses Microsoft Graph API (`https://graph.microsoft.com/v1.0`).
- Config requires: `tenant_id`, `client_id`, `client_secret`, `site_id` (or `drive_id` for OneDrive).
- Auth: client credentials flow (app-only auth) — store access token in Redis with expiry, refresh on 401.
- `list_changes(since)`:
  - Calls `GET /sites/{site_id}/drive/items/{item_id}/children` recursively.
  - For each item: filter to files (not folders), check `lastModifiedDateTime` against `since`.
  - Returns `ConnectorFile` with `source_id = item.id`, `path = item.path`, `modified_at = item.lastModifiedDateTime`.
  - Pagination via `@odata.nextLink`.
- `stream_bytes(file)`:
  - Calls `GET /sites/{site_id}/drive/items/{item.id}/content` — returns the file bytes.
  - For large files (>5MB), use the upload session API for resumable download.
- `infer_scope(file)`: same as local folder — path rules against the SharePoint path (`/Shared Documents/Films/...`).
- Rate limiting: respect `Retry-After` header; back off on 429.
- Frontend `/admin/connectors/new` page: pick "SharePoint" → form with tenant_id, client_id, client_secret (masked), site_id, default scope, default classification, sync interval.
- "Test connection" button — calls `GET /sites/{site_id}` to verify credentials before saving.

**Acceptance criteria:**
- Admin configures a SharePoint connector with valid Azure AD app credentials.
- "Test connection" returns green.
- Within `sync_interval_seconds`, the connector pulls the first 100 files from the configured SharePoint site.
- Each file appears in Seekra with scope + classification from path rules.
- A file modified in SharePoint is re-ingested within one sync cycle (new version created).
- A file deleted in SharePoint is NOT deleted in Seekra (deletion is one-way; Seekra keeps the doc).
- Audit trail shows `CONNECTOR_SYNCED` with `sharepoint_files_processed=N`.

### Phase 4 — Google Drive connector (Week 3)

**Scope:**
- `backend/app/services/connectors/google_drive.py` — concrete connector.
- Uses Google Drive API v3 with a service account.
- Config requires: `service_account_json` (the full JSON key file, stored encrypted at rest), `root_folder_id` (the shared drive or folder to sync from).
- Auth: service account JWT flow (using `google-auth` library).
- `list_changes(since)`:
  - Calls `GET https://www.googleapis.com/drive/v3/files` with `q: modifiedTime > {since}` and `corpora: sharedDrive` or `user` depending on root_folder_id type.
  - Paginate via `nextPageToken`.
  - For each file: `source_id = file.id`, `path` reconstructed from `file.parents` (call `files.get` for each parent — cache parent paths in Redis to avoid re-fetching).
- `stream_bytes(file)`:
  - Calls `GET https://www.googleapis.com/drive/v3/files/{id}?alt=media` — returns file bytes.
  - For large files, use resumable download.
- `infer_scope(file)`: path rules against the reconstructed Google Drive path (`/My Drive/Films/...`).
- Frontend `/admin/connectors/new` form for Google Drive: upload service account JSON (stored encrypted), root folder URL (parse to ID), default scope, classification, sync interval.

**Acceptance criteria:**
- Admin uploads a service account JSON + enters a shared drive folder URL.
- "Test connection" lists the top 5 files in the folder (verifies creds).
- Within sync interval, the connector pulls files from the Google Drive folder.
- Same incremental sync + versioning behavior as SharePoint.

### Phase 5 — SMTP email attachment ingest (Week 3-4)

**Scope:**
- New `smtp_ingest` Celery task that runs a long-lived IMAP listener (using `asyncio-imap` or `imapclient`).
- Config: `imap_host`, `imap_port`, `username`, `password`, `mailbox` (default INBOX), `default_scope_org_id`, `default_classification`.
- Inference rule: an email from `*@seekra-films.ae` → scope "Seekra Films" subtree; the sender domain → scope rule table.
- For each new email:
  - Extract attachments (skip if none).
  - For each attachment: upload to MinIO, create `documents` row.
  - Use the email subject as a document tag (added to `documents.tags`).
  - Use the email sender as a metadata field (`documents.source_sender`).
  - Apply default scope + classification, OR a per-sender override (configurable).
  - Delete the email from the mailbox after successful ingest (configurable: move to "Processed" folder instead).
- Audit events: `SMTP_INGESTED` with attachment count + sender.

**Acceptance criteria:**
- Admin configures an SMTP connector for `ingest@seekra-media.ae`.
- Sends an email to that address with 2 PDF attachments, subject "Q3 contracts".
- Within 60s, both PDFs appear in Seekra with the configured default scope + classification, tagged "Q3 contracts".
- Sender `sara@seekra-films.ae` → her files auto-scoped to "Seekra Films" subtree (sender-domain rule).
- A second email from the same sender with a modified attachment → versioned, not overwritten.

### Phase 6 — Conflict resolution + versioning integration (Week 4)

**Scope:**
- When the sync engine detects a source file modification:
  - Read the current `documents.updated_at` for the Seekra doc.
  - If `documents.updated_at > connector_files.last_synced_at`: conflict — emit `CONNECTOR_CONFLICT`, do NOT overwrite. Surface in admin UI as a conflict needing resolution.
  - If `documents.updated_at <= connector_files.last_synced_at`: stream new content, create new version via Brief #39's `_create_version(doc_id, new_content)` helper.
- Conflict resolution UI in `/admin/connectors/{id}/conflicts`:
  - List pending conflicts.
  - Per conflict: "Keep Seekra version" (mark resolved, no overwrite), "Overwrite with source" (force overwrite, new version), "Merge" (phase 7+).
- Audit events for each resolution action.

**Acceptance criteria:**
- Connector pulls a file from SharePoint; user edits the file inside Seekra (via viewer notes); connector pulls the same file again (source modified externally) → conflict logged, Seekra version preserved.
- Admin clicks "Overwrite with source" → new version created, conflict resolved, audit event emitted.
- No data loss in any scenario.

## 6. Technical notes

- **Encryption at rest**: connector credentials (client_secret, service_account_json, IMAP password) must be encrypted in the DB using AES-256 with a per-tenant key. Store the key in the existing `SECRET_KEY` rotation flow.
- **Idempotency**: `connector_files.source_id + connector_id` is unique; re-syncing the same file is a no-op unless `modified_at` advanced.
- **Backpressure**: if the indexing pipeline queue depth > 1000, pause connector sync until the queue drains. Surface as `last_sync_status = 'throttled'`.
- **Permissions**: connector admin endpoints require `require_admin()`. Sync tasks inherit the connector's `tenant_id` (when multi-tenant lands in Brief #35).
- **No PII in logs**: connector credentials must never appear in logs. Use the existing `redact_pii` helper on all log lines containing connector config.
- **Frontend**: reuse the existing Seekra design system (purple primary, teal accent). Connector type icons: local folder = Folder, SharePoint = Microsoft, Google Drive = Google, SMTP = Mail.

## 7. Out of scope (future briefs)

- Bidirectional sync (delete in Seekra → delete in source).
- Real-time push from SharePoint (webhooks) / Drive (push notifications).
- Merge conflict resolution (3-way merge).
- Connector templates (one-click setup for common sources).
- Connector marketplace (third-party developers can add connectors).

## 8. Testing

- Unit tests for each connector's `list_changes` + `stream_bytes` + `infer_scope`.
- Integration tests using local folder connector with a temp dir.
- Mock SharePoint + Google Drive using `responses` library.
- UAT script (deliver to UAT engineer): create local folder connector, drop 5 files, verify ingest + scope + classification + versioning + conflict resolution.

## 9. Documentation

- Update `AGENTS.md` with the new connector framework.
- Update `GOVERNANCE.md` with the new audit event types.
- Update demo run book with a new "Section 9: Data Connectors" demo step (drop a file on the watched folder, watch it appear in 60s).

---

**End of Brief #32.**
