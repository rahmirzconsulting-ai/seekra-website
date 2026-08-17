# Brief #16: Seekra Intelligence Upgrade — Smart Search + Video Deep-Link + Entity Relationship Graph

**Status:** For Kimi — implementation
**Date:** 2026-08-17
**Author:** Architect (reviewed with Rahmir)
**Scope:** 5 phases, ~2-3 weeks. Ship each phase as a separate commit. Each phase is independently verifiable and rollbackable.

---

## Objective

Transform Seekra from "document-centric RAG" to "entity-centric intelligence with smart search across all file types." After this brief, a user can:

- Search for "car crossing bridge" → find the exact video frame → click → video opens at 3:57
- Ask "who is connected to person X?" → get a graph-enriched answer with documents, co-occurring entities, and cross-references
- See section titles, entities, and metadata in search results (not just raw text snippets)
- Search with reformulated queries that expand vague terms into specific retrieval queries

This brief combines three workstreams:
1. **Search enrichment** (Phase 1) — bring Brief #12/#13 improvements to the search pipeline
2. **Video deep-link + dense frames** (Phases 2-3) — solve the "find the car at 3:57" use case
3. **Entity relationship graph** (Phases 4-5) — link entities across documents + graph-enriched chat

---

## Phase 1: Search Enrichment (1 day)

### Problem
The search pipeline (`smart_search.py` + `search.py`) does NOT use the improvements from Briefs #12/#13:
- No `section_title` or `document_type` in search SQL queries
- No query reformulation for vague search terms
- No entity display in search result snippets
- No cross-reference resolution in search results

### Changes

#### 1A: Add section_title + document_type to search SQL queries

**File:** `backend/app/api/smart_search.py`

Every SELECT from `document_chunks` currently selects:
```sql
c.id, c.chunk_text, c.document_id, c.page_number
```

Add `c.section_title, c.document_type` to ALL chunk SELECT queries in:
- `_document_fts_leg` (around line 262)
- `_visual_ocr_leg` (around line 307)
- `_visual_object_leg` (around line 334)
- `_doc_semantic_leg` (around line 381)
- `_visual_semantic_leg` (around line 426)

Also add to the result serialization (around line 508):
```python
"section_title": row.get("section_title"),
"document_type": row.get("document_type"),
```

**File:** `backend/app/api/search.py`

Same pattern — add `c.section_title, c.document_type` to the SELECT queries at lines 79, 96, 111.

#### 1B: Query reformulation for search

**File:** `backend/app/api/smart_search.py`

Before running the retrieval legs, check if the query is vague and reformulate it:

```python
# Phase 1: query reformulation for vague search terms
from app.api.chat import _reformulate_query, _is_vague_short
if _is_vague_short(req.query):
    reformulated = await _reformulate_query(req.query, "en")
    if reformulated != req.query:
        print(f"[SMART-SEARCH] Query reformulated: '{req.query}' -> '{reformulated}'")
        # Use reformulated for retrieval, original for display
        retrieval_query = reformulated
    else:
        retrieval_query = req.query
else:
    retrieval_query = req.query
```

Use `retrieval_query` for all retrieval legs (embedding, FTS, visual). Keep `req.query` as the displayed query in results.

**File:** `backend/app/api/search.py`

Same pattern — call `_reformulate_query()` before the search.

#### 1C: Entity display in search result snippets

**File:** `backend/app/api/smart_search.py`

After retrieving chunks, fetch their entities (same pattern as chat.py Brief #13):

```python
# Phase 1: fetch entities for retrieved chunks
text_chunk_ids = [r["chunk_id"] for r in results if r.get("chunk_id")]
if text_chunk_ids:
    try:
        ent_rows = (await db.execute(sql_text(
            "SELECT chunk_id, entity_type, entity_value FROM chunk_entities "
            "WHERE chunk_id = ANY(CAST(:ids AS int[]))"
        ), {"ids": text_chunk_ids})).mappings().all()
        ent_map = {}
        for er in ent_rows:
            ent_map.setdefault(er["chunk_id"], []).append(
                (er["entity_type"], er["entity_value"]))
        for r in results:
            r["entities"] = ent_map.get(r.get("chunk_id"), [])
    except Exception:
        pass
```

Include the entities in the search result serialization:
```python
"entities": [{"type": t, "value": v} for t, v in (r.get("entities") or [])[:5]]
```

#### 1D: Frontend — display section title + entities in search results

**File:** `frontend/src/app/search/page.tsx`

In the search result card rendering, add:
- Section title as a subtitle under the filename: "→ Section: Data Retention"
- Entity chips below the snippet: `[date: 7 years] [amount: $50,000] [reference: Article 5.3]`

### Verification (Phase 1)

```bash
# Search for a vague term
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"retention"}' \
  https://app-internal.seekra.pk/api/smart-search | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', [])[:3]:
    print(f'  {r.get(\"filename\")} → {r.get(\"section_title\",\"N/A\")}')
    for e in (r.get('entities') or [])[:3]:
        print(f'    [{e[\"type\"]}: {e[\"value\"]}]')
"
```

Expected: search results include section titles + entity chips. Vague query "retention" gets reformulated to "data retention period rules conditions" in backend logs.

### Commit message
```
Brief #16.1: Search enrichment — section titles + query reformulation + entities in results
```

---

## Phase 2: Dense Video Frame Extraction (2 days)

### Problem
Currently: 12 evenly-spaced frames per video (`VISUAL_MAX_VIDEO_FRAMES=12`). A 30-minute video gets 12 frames — one every 2.5 minutes. A specific moment like "car at 3:57" is likely missed.

### Changes

#### 2A: Increase default frame density

**File:** `backend/app/services/visual_ai.py`

Change the default from 12 to 60 (1 frame per ~30 seconds for a 30-minute video):

```python
MAX_VIDEO_FRAMES = int(os.getenv("VISUAL_MAX_VIDEO_FRAMES", "60"))
```

Also change the frame distribution from evenly-spaced to time-interval-based:

```python
# Phase 2: time-interval-based frame extraction
FRAME_INTERVAL_SECONDS = float(os.getenv("VISUAL_FRAME_INTERVAL", "10.0"))  # 1 frame per 10 seconds

def _video_frame_candidates(filename: str, file_bytes: bytes) -> list[dict]:
    # ... existing setup ...
    duration = frame_count / fps if frame_count > 0 and fps > 0 else 0

    if duration > 0 and fps > 0:
        # Extract 1 frame every FRAME_INTERVAL_SECONDS, capped at MAX_VIDEO_FRAMES
        num_frames = min(MAX_VIDEO_FRAMES, int(duration / FRAME_INTERVAL_SECONDS))
        if num_frames < 1:
            num_frames = 1
        frame_positions = [
            min(frame_count - 1, int((i * FRAME_INTERVAL_SECONDS) * fps))
            for i in range(num_frames)
        ]
    else:
        # Fallback: evenly spaced
        frame_limit = max(1, MAX_VIDEO_FRAMES)
        frame_positions = [
            min(frame_count - 1, int(i * frame_count / frame_limit))
            for i in range(frame_limit)
        ]

    for frame_position in frame_positions:
        # ... existing extraction code ...
        timestamp = frame_position / fps if fps > 0 else None
        candidates.append({
            "asset_type": "video_frame",
            "image": image,
            "start_time": round(timestamp, 1) if timestamp else None,
            "end_time": round(timestamp + FRAME_INTERVAL_SECONDS, 1) if timestamp else None,
        })
```

**Config:** Add to `backend/app/config.py`:
```python
visual_frame_interval: float = 10.0  # seconds between extracted video frames
visual_max_frames: int = 60          # cap on total frames per video
```

#### 2B: Frame caption generation (optional but high-value)

**File:** `backend/app/services/visual_ai.py`

After extracting each frame, generate a 1-sentence caption using the LLM:

```python
async def _generate_frame_caption(image_base64: str) -> str:
    """Generate a 1-sentence description of a video frame using the LLM.
    Fail-open: returns empty string on any error."""
    try:
        # Use Groq/Gemini vision model to caption the frame
        # OR: use CLIP zero-shot classification with a list of scene descriptions
        # The simplest approach: use CLIP text similarity against a set of scene templates
        # and return the best match as the "caption"
        pass
    except Exception:
        return ""
```

Store the caption in `visual_assets` as a new column `caption TEXT`.

**Migration:**
```sql
ALTER TABLE visual_assets ADD COLUMN IF NOT EXISTS caption TEXT;
```

The caption becomes searchable text — searching for "car crossing bridge" matches a frame whose caption is "A car is crossing a bridge over a river."

**Note:** If LLM-based captioning is too slow at indexing time, use CLIP zero-shot classification instead — classify each frame against 200+ scene templates ("car on bridge", "person at desk", "building exterior", etc.) and store the top-3 matches as labels.

### Verification (Phase 2)

```bash
# Upload a short test video (30 seconds)
# After processing, check how many visual_assets were created:
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app-internal.seekra.pk/api/visual/summary?document_id=$VIDEO_DOC_ID" | python3 -m json.tool

# Expected: ~3-6 video_frame assets (1 per 10 seconds for a 30-second video)
# Each with start_time, thumbnail, and (if captioning implemented) a caption
```

### Commit message
```
Brief #16.2: Dense video frame extraction (1 frame per 10s, configurable) + optional frame captions
```

---

## Phase 3: Timestamp Deep-Linking + Video Search (2 days)

### Problem
When search finds a video frame, clicking it opens the viewer — but the video plays from the start, not from the timestamp where the match was found. The user has to manually scrub to find the moment.

### Changes

#### 3A: Viewer accepts timestamp parameter

**File:** `frontend/src/app/viewer/page.tsx`

The viewer already accepts `?doc=42&t=237` (via the search page's seek chips). Verify that:
1. The `<video>` element seeks to `t` seconds on load
2. The timestamp is displayed as "3:57" in the UI

If this already works (from Step 14 work), no change needed. If not, add:
```typescript
useEffect(() => {
  const t = parseFloat(searchParams.get('t') || '0');
  if (t > 0 && videoRef.current) {
    videoRef.current.currentTime = t;
  }
}, [searchParams]);
```

#### 3B: Search results for video include "Jump to X:XX" button

**File:** `frontend/src/app/search/page.tsx`

For video_frame results with `start_time`, add a clickable timestamp button:

```tsx
{result.start_time != null && (
  <Link href={`/viewer/?doc=${result.document_id}&t=${result.start_time}`}>
    <Clock className="w-3 h-3" />
    {formatTimestamp(result.start_time)}
  </Link>
)}
```

#### 3C: Timestamp filter in search

**File:** `backend/app/api/smart_search.py`

Add an optional `video_timestamp` parameter to `SmartSearchRequest`:

```python
class SmartSearchRequest(BaseModel):
    query: str
    # ... existing fields ...
    video_timestamp: Optional[float] = None  # seconds — filter video results to this timestamp ±30s
```

When `video_timestamp` is provided, add a WHERE clause to the visual legs:
```sql
AND va.start_time BETWEEN :ts_start AND :ts_end
```
Where `ts_start = video_timestamp - 30` and `ts_end = video_timestamp + 30`.

This lets the client search "car bridge" + filter to timestamp 237 (3:57) → finds only video frames near 3:57.

#### 3D: Natural language timestamp parsing

**File:** `backend/app/api/smart_search.py`

Before running retrieval, parse the query for timestamp hints:

```python
import re

def _extract_timestamp(query: str) -> float | None:
    """Extract a timestamp from a search query.
    Supports: '3:57', 'at 3:57', 'timestamp 237', 'at 3 minutes 57 seconds'
    """
    # MM:SS format
    m = re.search(r'\b(\d{1,2}):(\d{2})\b', query)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    # "at X seconds" / "timestamp X"
    m = re.search(r'(?:at|timestamp|time)\s+(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|s)?', query, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None
```

If a timestamp is found, strip it from the query (it's not a search term) and set `video_timestamp`.

### Verification (Phase 3)

```bash
# Search for "car bridge at 3:57"
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"car bridge at 3:57"}' \
  https://app-internal.seekra.pk/api/smart-search | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('results', []):
    if r.get('start_time') is not None:
        print(f'  Video frame at {r[\"start_time\"]}s — {r.get(\"labels\",[])}')
"
```

Expected: video frame results near 237 seconds (3:57), with thumbnail + labels. Clicking the result opens the viewer at 3:57.

### Commit message
```
Brief #16.3: Timestamp deep-linking + video search (natural language timestamp parsing + viewer seek)
```

---

## Phase 4: Entity Relationship Graph — Data + API + UI (3-4 days)

### Based on: "Entity Relationship Layer Proposal" (Kimi's proposal, architect-approved)

### Problem
Entities are stored in `chunk_entities` (from Briefs #13/#15) but are NOT linked. There's no queryable relationship structure — only per-chunk rows. You can't ask "show me everything connected to person X" or "which contracts reference Article 5?"

### Changes

#### 4A: Migration — entity_relationships edge table

**File:** `backend/migrations/20260817_step43_entity_graph.sql`

```sql
CREATE TABLE IF NOT EXISTS entity_relationships (
    id BIGSERIAL PRIMARY KEY,
    subject_type VARCHAR(30) NOT NULL,    -- person, organization, location, reference, date, amount, misc
    subject_value TEXT NOT NULL,
    relation VARCHAR(40) NOT NULL,        -- DEFINES, REFERENCES, CO_OCCURS, MENTIONS, PART_OF_VERSION_CHAIN
    object_type VARCHAR(30) NOT NULL,
    object_value TEXT NOT NULL,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id INTEGER REFERENCES document_chunks(id) ON DELETE CASCADE,
    confidence FLOAT DEFAULT 1.0,          -- 1.0 = deterministic, <1.0 = inferred
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_er_subject ON entity_relationships (subject_type, subject_value);
CREATE INDEX IF NOT EXISTS idx_er_object ON entity_relationships (object_type, object_value);
CREATE INDEX IF NOT EXISTS idx_er_relation ON entity_relationships (relation);
CREATE INDEX IF NOT EXISTS idx_er_doc ON entity_relationships (document_id);

COMMENT ON TABLE entity_relationships IS 'Step 43: entity relationship graph edges. Deterministic only (no LLM). Built at indexing time from Briefs #13/#15 entity data + cross-references.';
```

#### 4B: Relationship inference at indexing time

**File:** `backend/app/services/entity_graph.py` (new)

```python
"""Phase 4: deterministic relationship inference at indexing time.

Builds edges from:
1. DEFINES — chunk starts with "Article 5.3" → entity "5.3" DEFINES in this chunk
2. REFERENCES — chunk mentions "Article 5.3" but doesn't define it → entity "5.3" REFERENCES this chunk
3. CO_OCCURS — two entities in the same chunk → CO_OCCURS (weight = chunk count)
4. MENTIONS — entity → document mapping (every entity in a document)
5. PART_OF_VERSION_CHAIN — from version_group_id (document A is version 1, document B is version 2)

All deterministic — no LLM calls. Runs at indexing time, after entity extraction.
"""
```

The inference function takes the extracted entities + cross-references + version info and populates `entity_relationships`.

**File:** `backend/app/workers/celery_tasks.py`

After entity extraction (Brief #13) and cross-reference detection (Brief #13.2), call the relationship inference:

```python
# Phase 4: build entity relationships
from app.services.entity_graph import build_relationships
build_relationships(cur, conn, doc_id, chunk_items, entities_per_chunk, cross_refs, version_group_id)
```

#### 4C: API — entity search + graph traversal

**File:** `backend/app/api/entities.py` (new)

```python
router = APIRouter(prefix="/api/entities", tags=["entities"])

@router.get("/search")
# Entity autocomplete: GET /api/entities/search?q=خالد
# Returns matching entities (persons, orgs, locations, references)

@router.get("/{entity_value}/graph")
# Graph traversal: GET /api/entities/خالد العتيبي/graph?depth=2
# Returns nodes + edges within depth 2 (recursive CTE, result-capped at 100)
# Uses: WITH RECURSIVE ... on entity_relationships

@router.get("/documents/{doc_id}/entities")
# Per-document entity map: GET /api/entities/documents/42/entities
# Returns all entities + relationships for a specific document
```

Register the router in `main.py`.

#### 4D: Frontend — entity panel + simple graph view

**File:** `frontend/src/app/admin/entities/page.tsx` (new)

Admin page with:
1. Entity search bar (autocomplete)
2. Graph view: depth-1 radial list of nodes + edges (no physics library — just a styled list)
3. Click an entity → see its relationships (documents, co-occurring entities, cross-references)
4. Click a document → see its entity map

**File:** `frontend/src/components/sidebar-nav.tsx`

Add to admin nav:
```typescript
...(isAdmin ? [{ href: "/admin/entities/", icon: Share2, label: tf("nav.entities", "Entities") }] : []),
```

**File:** i18n — add EN + AR strings for entity graph UI.

#### 4E: Backfill

**File:** `backend/app/services/entity_graph.py`

```python
def backfill_relationships(batch_size: int = 100) -> dict:
    """One-off: build entity_relationships for existing documents.
    Iterates documents, fetches their entities + cross-refs + version info,
    and populates the edge table. Idempotent: skips documents that already
    have relationship rows."""
```

### Verification (Phase 4)

```bash
# After migration + backfill:

# Entity search
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app-internal.seekra.pk/api/entities/search?q=خالد" | python3 -m json.tool

# Graph traversal
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app-internal.seekra.pk/api/entities/خالد/graph?depth=2" | python3 -m json.tool

# Per-document entity map
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://app-internal.seekra.pk/api/entities/documents/50/entities" | python3 -m json.tool
```

Expected: entities found, relationships returned, graph traversable to depth 2.

### Commit message
```
Brief #16.4: Entity relationship graph — edge table + deterministic inference + API + admin UI
```

---

## Phase 5: Graph-Enriched Chat Answers (2-3 days)

### Problem
When a user asks "who is connected to person X?" or "which contracts reference Article 5?", the chat pipeline uses vector retrieval only — it doesn't query the entity graph. The answer is limited to what's in the retrieved chunks, not what's in the relationship structure.

### Changes

#### 5A: Graph context injection in chat

**File:** `backend/app/api/chat.py`

After retrieval and before building the LLM prompt, check if the question names a known entity. If yes, fetch its depth-1 graph neighborhood and inject it as additional context:

```python
# Phase 5: graph-enriched context
from app.services.entity_graph import get_entity_neighborhood

graph_context = ""
try:
    # Check if the question mentions a known entity
    # Simple approach: search entity_relationships for subject_value or object_value
    # that appears in the question text
    neighborhood = await get_entity_neighborhood(db, question, depth=1)
    if neighborhood:
        graph_lines = []
        for edge in neighborhood[:10]:  # cap at 10 edges
            graph_lines.append(
                f"- {edge['subject_value']} ({edge['subject_type']}) "
                f"—{edge['relation']}→ "
                f"{edge['object_value']} ({edge['object_type']}) "
                f"[Doc {edge.get('document_id','?')}]"
            )
        graph_context = "\n\n--- Entity graph context ---\n" + "\n".join(graph_lines)
except Exception:
    pass  # graph unavailable — vector-only context

# Append graph_context to the existing context
context = "\n\n---\n\n".join(
    [_ctx_line(r) for r in rows] + [_visual_ctx_line(v) for v in visual_hits]
    + xref_lines
) + graph_context  # ← graph context appended here
```

#### 5B: Graph context budget

The graph context is capped at 1000 characters (deducted from the 6000-char context budget):

```python
MAX_GRAPH_CONTEXT_CHARS = 1000
if len(graph_context) > MAX_GRAPH_CONTEXT_CHARS:
    graph_context = graph_context[:MAX_GRAPH_CONTEXT_CHARS] + "..."
```

The existing `{context[:6000]}` in the LLM prompt becomes `{context[:6000 - MAX_GRAPH_CONTEXT_CHARS]}` to make room.

#### 5C: PII masking applies to graph context

Graph entities can contain person names (PII). The graph context goes through the same `redact_pii_with_findings()` as the rest of the context — it's already covered because the graph_context is appended to the main `context` string before PII masking runs.

#### 5D: Audit event

Log a `ENTITY_GRAPH_QUERIED` audit event when graph context is injected (hash-chained via Brief #6):

```python
if graph_context:
    await audit_event(db, request, current_user.id,
        "ENTITY_GRAPH_QUERIED",
        f"Graph context injected for question: {question[:100]}")
```

### Verification (Phase 5)

```bash
# Ask a graph-aware question
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Show me every document connected to person خالد"}' \
  https://app-internal.seekra.pk/api/chat/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('ANSWER:', data.get('answer','N/A')[:500])
print('SOURCES:', len(data.get('sources',[])))
# The answer should reference documents connected to خالد via the entity graph
# — not just chunks that textually mention خالد
"
```

Expected: answer references documents connected to the entity, with graph-derived context cited alongside vector-retrieved chunks.

### Commit message
```
Brief #16.5: Graph-enriched chat — inject entity neighborhood as additional context + PII masking + audit
```

---

## What NOT to touch

- **The existing retrieval legs** (vector, FTS, visual) — don't change how they work, only what they select and how results are displayed
- **The LLM prompt structure** (Brief #12) — graph context is injected as additional context, not as prompt instructions
- **The PII detection/masking pipeline** — graph context goes through the same PII masking as regular context
- **The audit chain** — graph queries log a standard audit event, hash-chained via Brief #6
- **The provenance endpoint** — don't modify it. The entity graph is a separate API surface
- **The diff endpoint** — don't modify it
- **The confidence computation** (Brief #9) — graph context doesn't affect the confidence tier

## Commit sequence

| Phase | Commit | What | Effort |
|---|---|---|---|
| 1 | Brief #16.1 | Search enrichment (section titles + reformulation + entities) | 1 day |
| 2 | Brief #16.2 | Dense video frames (1 per 10s, configurable) + optional captions | 2 days |
| 3 | Brief #16.3 | Timestamp deep-linking + video search (NL timestamp parsing) | 2 days |
| 4 | Brief #16.4 | Entity graph (edge table + inference + API + admin UI) | 3-4 days |
| 5 | Brief #16.5 | Graph-enriched chat (inject neighborhood + PII + audit) | 2-3 days |

## Questions before you start

1. **Frame captioning: LLM-based or CLIP-based?** LLM gives better captions ("a car is crossing a bridge") but costs tokens per frame at indexing time. CLIP zero-shot is free but less descriptive. My take: start with CLIP zero-shot (free, fast), add LLM captions as a follow-up if needed.

2. **Entity disambiguation: how to handle same-name different-person?** v1 treats identical normalized strings as one node. Document this limitation. Disambiguation is a future brief.

3. **Graph depth: cap at 2?** My recommendation: depth 1 for chat context injection (fast, focused), depth 2 for the admin UI graph view (more exploration). Cap at depth 2 — deeper traversals are slow and produce noisy results.

4. **Performance: recursive CTE on 100k edges?** Test early. If too slow, add a materialized view or cache the depth-1 neighborhood in Redis.

5. **Video frame storage: MinIO thumbnails for 60 frames?** Each thumbnail is ~10-50KB JPEG. 60 frames = ~3MB per video. Acceptable. If storage is a concern, reduce thumbnail resolution.

## Final note

This is the brief that delivers "Ask anything. Find everything." After all 5 phases:
- Search finds the right document, page, video frame, or audio segment
- Video results deep-link to the exact timestamp
- Entity graph connects people, organizations, references, and documents across the archive
- Chat answers are enriched with graph relationships
- PII masking, audit chain, and provenance cover the new graph data

Ship each phase separately. Verify each before moving to the next. Your call on implementation details within each phase is final.
