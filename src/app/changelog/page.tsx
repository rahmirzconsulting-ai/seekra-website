import { Navbar } from '@/components/site/navbar';
import { Footer } from '@/components/site/footer';

type Brief = {
  id: string;
  title: string;
  date: string;
  category: 'Access Control' | 'Connectors' | 'Intelligence' | 'Governance' | 'UX' | 'Platform';
  summary: string;
  details: string[];
};

const BRIEFS: Brief[] = [
  // Latest first
  {
    id: '#32',
    title: 'Data Connectors + Bulk Folder Ingestion',
    date: 'Aug 2026',
    category: 'Connectors',
    summary: '9 connector types (local folder, SharePoint, Google Drive, AWS S3, Azure Blob, GCS, SFTP, Alibaba OSS, IMAP) with incremental sync, versioning on conflict, and per-connector scope inference.',
    details: [
      'Pluggable Connector ABC with list_changes / stream_bytes / infer_scope',
      'Path-rule inference: glob pattern → (scope_org_id, classification)',
      'Conflict resolution via Brief #39 versioning',
      'Permission-scoped: connectors inherit admin tenant, enforce same access rules',
      'Async sync via Celery beat (default 5 min interval, configurable per connector)',
    ],
  },
  {
    id: '#31',
    title: 'Noun-anchored inventory count regex (EN + AR)',
    date: 'Aug 2026',
    category: 'Intelligence',
    summary: 'Fixed a regression where "how many PDF documents" missed the deterministic SQL inventory path and the LLM hallucinated a count from a few retrieved excerpts. The new regex tolerates qualifier words but requires the document/file noun.',
    details: [
      'Tolerates up to 3 qualifier words between "how many" and "documents/files"',
      'Requires the noun, so "how many days of leave" still falls through to retrieval',
      'Bilingual: Arabic regex covers كم عدد ملفات PDF phrasings',
    ],
  },
  {
    id: '#20–#24',
    title: 'Agent mode + Deep answer mode + calm UX',
    date: 'Aug 2026',
    category: 'Intelligence',
    summary: 'Three answer modes (Auto / Agent / Deep) with a segmented mode pill. Agent mode: planner picks from 5 permission-scoped tools (search_library, list_documents, summarize_document, find_entity, compare_documents). Deep mode: decompose into 2–4 sub-questions, multi-pass retrieval with cross-pass chunk ranking.',
    details: [
      'Brief #20: planner + 5 tools + steps trace + fail-open fallback',
      'Brief #21: deep answer mode, 9000-char context budget (vs 6000 normal)',
      'Brief #22: citation dedup ([1][1] → [1])',
      'Brief #23: exact-count rule in synthesis prompt (no hallucinated counts)',
      'Brief #24: segmented mode pill, + menu, lens icon, card drop target',
    ],
  },
  {
    id: '#17 P1–P6',
    title: 'Enterprise Access Control',
    date: 'Aug 2026',
    category: 'Access Control',
    summary: 'A 4-company org tree with ltree materialized paths. Document scoping + 4-level classification (Public/Internal/Confidential/Restricted). Per-user clearance. Cross-scope overrides that don\'t elevate clearance. Soft-delete users with instant token invalidation. Override cache flush.',
    details: [
      'P1–P3: org_nodes (ltree) + user_org_memberships + document_overrides tables',
      'P4: override API + Manage Access UI + classification badges',
      'P5: retire Collections UI (replaced by org-scope + classification)',
      'P6: soft-delete users, override cache flush, viewer chips, nginx cache headers',
      'Permission enforcement at the SQL query layer (defense in depth)',
    ],
  },
  {
    id: '#16',
    title: 'Entity extraction + relationship graph',
    date: 'Aug 2026',
    category: 'Intelligence',
    summary: 'Persons, organizations, and locations extracted at indexing time (Brief #16.1). Cross-reference resolution finds defining chunks for mentioned references (Brief #16.5). Entity relationship graph with edge table + deterministic inference (Brief #16.4). Graph-enriched chat with entity neighborhood context (Brief #16.5).',
    details: [
      'Arabic NER via CAMeL Tools (Brief #15.1)',
      'PII detection integrated with Arabic NER (Brief #15.2)',
      'NER integrated into entity extraction (Brief #15.3)',
      'Edge inference: CO_OCCURS, MENTIONED_IN, DIRECTED_BY, PRODUCED_BY',
      'Admin UI: /admin/entities with force-directed graph visualization',
    ],
  },
  {
    id: '#25–#30',
    title: 'Chat UX polish + viewer media teardown',
    date: 'Aug 2026',
    category: 'UX',
    summary: 'Scroll arrows on chat + search result lists. Viewer media teardown (pause on unmount + on document switch). pdf.js canvas leak fix (measurement canvases on body cleaned up).',
    details: [
      'Brief #25: chat scroll arrows',
      'Brief #26: viewer pauses media on document switch',
      'Brief #28: pdf.js measurement canvas leak fix',
      'Brief #29: chat + search scroll arrow polish',
      'Brief #30: search results scroll arrows',
    ],
  },
  {
    id: 'P14–P16',
    title: 'Audit chain advisory lock + PII lineage',
    date: 'Aug 2026',
    category: 'Governance',
    summary: 'Advisory lock on audit chain writes (fixes prev_hash race on concurrent events). PII lineage summary header on Document Provenance page. Aggregate duplicate PII findings with match_count + xN badge for repeated matches.',
    details: [
      'P14: pg_advisory_xact_lock prevents prev_hash race',
      'P15: PII lineage summary on /admin/provenance/{doc_id}',
      'P16: match_count aggregation, distinguishing Emirates-ID mask, legacy lineage compat',
    ],
  },
  {
    id: '#18, #19',
    title: 'Guided fallback + proactive guidance',
    date: 'Aug 2026',
    category: 'Intelligence',
    summary: 'Guided fallback suggests closest documents on no-match (Brief #18a). Clarifying-question base prompt for ambiguous queries (Brief #18b). Scale-safe inventory via SQL COUNT/GROUP BY (Brief #18c). /chat/starters endpoint returns library-grounded starter questions (Brief #19). Follow-up suggestion chips after each chat answer (Brief #19).',
    details: [
      '/chat/starters?lang=en returns "Summarize {latest_doc}", "What documents mention {org}?" etc.',
      'Follow-up suggestions grounded in cited documents, not generic LLM prompts',
      'Per-user + per-lang Redis cache (seekra:chat:starters:v1:{uid}:{lang})',
    ],
  },
  {
    id: '#13',
    title: 'Cross-reference resolution + entity extraction',
    date: 'Jul 2026',
    category: 'Intelligence',
    summary: 'Entity extraction at indexing time (chunk_entities table). Cross-reference resolution: "this book", "it", "the aforementioned" resolves to the defining chunk for the mentioned reference.',
    details: [
      'Chunk-level entity storage for fast scoped queries',
      'Cross-reference resolution runs after indexing, before search',
    ],
  },
];

const CATEGORY_COLORS: Record<Brief['category'], string> = {
  'Access Control': '#B93C32',
  'Connectors': '#B59876',
  'Intelligence': '#4f8fdd',
  'Governance': '#5cb87a',
  'UX': '#b45ad4',
  'Platform': '#4A3F33',
};

export default function ChangelogPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#202020]">
      <Navbar />
      <main className="flex-1 pt-32 pb-24">
        <div className="mx-auto max-w-4xl px-6 lg:px-10">
          <div className="text-[12px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-3">
            Release notes
          </div>
          <h1 className="font-bold tracking-tight text-[#E7E6E4] mb-3"
              style={{ fontSize: 'clamp(32px, 4.5vw, 48px)', lineHeight: 1.1, letterSpacing: '-0.022em' }}>
            What&rsquo;s new in Seekra<span className="text-[#B93C32]">.</span>
          </h1>
          <p className="text-[16px] leading-[1.6] text-[#E7E6E4]/72 mb-12 max-w-[640px]">
            Briefs #13 through #32 — six months of focused, incremental shipping. Each brief is a self-contained scope, deployed to production, UAT-verified before merge. The most recent is at the top.
          </p>

          <div className="space-y-8">
            {BRIEFS.map((b) => (
              <article
                key={b.id}
                className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7"
              >
                <div className="flex items-center gap-3 mb-3 flex-wrap">
                  <span
                    className="text-[10px] font-bold tracking-[0.14em] uppercase px-2.5 py-1 rounded-full text-white"
                    style={{ background: CATEGORY_COLORS[b.category] }}
                  >
                    {b.category}
                  </span>
                  <span className="text-[12px] font-mono text-[#B59876]">{b.id}</span>
                  <span className="text-[12px] text-[#E7E6E4]/55">{b.date}</span>
                </div>
                <h2 className="text-[20px] font-semibold text-[#E7E6E4] tracking-tight mb-2">
                  {b.title}
                </h2>
                <p className="text-[14px] leading-[1.65] text-[#E7E6E4]/72 mb-4">
                  {b.summary}
                </p>
                <ul className="space-y-2">
                  {b.details.map((d, j) => (
                    <li key={j} className="flex items-start gap-2 text-[13px] leading-[1.55] text-[#E7E6E4]/85">
                      <span className="text-[#B59876] mt-1 flex-shrink-0">›</span>
                      <span>{d}</span>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>

          <div className="mt-12 p-5 rounded-[12px] bg-[#B59876]/[0.08] border border-[#B59876]/25">
            <div className="text-[13px] font-semibold text-[#B59876] mb-1.5">
              Want to see these in production?
            </div>
            <div className="text-[13px] leading-[1.55] text-[#E7E6E4]/85">
              We run a live demo at <a href="#contact" className="text-[#B59876] underline hover:text-[#C9B498]">app-internal.seekra.pk</a> with a 32-document Dubai media-holding library. Book a 45-minute walkthrough and we&rsquo;ll show you every brief above against real content.
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
