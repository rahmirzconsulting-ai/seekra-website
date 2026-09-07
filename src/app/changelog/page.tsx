import { Navbar } from '@/components/site/navbar';
import { Footer } from '@/components/site/footer';

type Release = {
  id: string;
  title: string;
  date: string;
  category: 'Access Control' | 'Connectors' | 'Intelligence' | 'Governance' | 'User Experience';
  summary: string;
  details: string[];
};

const RELEASES: Release[] = [
  // Latest first
  {
    id: '2026.09',
    title: 'Data connectors',
    date: 'September 2026',
    category: 'Connectors',
    summary: 'Nine data source connectors with incremental sync, automatic scoping, and versioning on change. Point Seekra at where your documents already live and the library populates itself.',
    details: [
      'Connectors for local/network folders, SharePoint, Google Drive, Amazon S3, Azure Blob, Google Cloud Storage, Alibaba OSS, SFTP, and email',
      'Incremental sync — only new or modified files are fetched',
      'Folder paths map to your organization tree, so documents are scoped automatically',
      'When a source file changes, a new version is created — the previous version is preserved',
    ],
  },
  {
    id: '2026.08',
    title: 'Three answer modes',
    date: 'August 2026',
    category: 'Intelligence',
    summary: 'Standard, agent, and deep answer modes plus an entity knowledge graph that understands people, organizations, and locations in your documents — in Arabic and English.',
    details: [
      'Standard mode — fast single-pass answers for most questions',
      'Agent mode — multi-step research using a small set of internal tools (search, list, summarize, find entities, compare)',
      'Deep mode — comprehensive multi-pass synthesis for complex questions that span many documents',
      'Auto-extracted entity knowledge graph — no manual tagging required',
    ],
  },
  {
    id: '2026.08',
    title: 'Enterprise access control',
    date: 'August 2026',
    category: 'Access Control',
    summary: 'Organization tree with four-level document classification and per-user clearance. Cross-scope overrides for collaboration. Offboard employees with immediate session invalidation.',
    details: [
      'Organization tree of companies, departments, and teams — access flows down the tree, never sideways',
      'Four classification levels: Public, Internal, Confidential, Restricted',
      'Per-user clearance — each user sees only documents at or below their level',
      'Cross-scope overrides grant access to a specific document without elevating clearance',
      'Deactivating a user rejects their existing sessions immediately',
    ],
  },
  {
    id: '2026.08',
    title: 'Audit chain hardening + PII lineage',
    date: 'August 2026',
    category: 'Governance',
    summary: 'Tamper-evident audit chain made safe under concurrent writes. PII lineage summary surfaces repeated findings at a glance, with masked samples for regulator review.',
    details: [
      'Concurrent audit writes no longer risk breaking the hash chain',
      'PII findings aggregated by masked sample — repeated matches shown with a count badge',
      'PII lineage summary on each document\u2019s provenance page',
    ],
  },
  {
    id: '2026.07',
    title: 'Entity extraction + relationship graph',
    date: 'July 2026',
    category: 'Intelligence',
    summary: 'People, organizations, and locations identified at indexing time. Cross-references like "this document" and "the aforementioned" resolved to the defining passage. Relationship graph with admin visualization.',
    details: [
      'Arabic and English named-entity recognition built in',
      'Cross-reference resolution — pronouns and shorthand link back to their source',
      'Relationship graph with admin visualization and entity-aware chat answers',
    ],
  },
  {
    id: '2026.07',
    title: 'Guided fallback + proactive suggestions',
    date: 'July 2026',
    category: 'Intelligence',
    summary: 'When Seekra cannot find an answer, it suggests the closest matching documents instead of returning a dead end. The empty chat screen now shows library-grounded starter questions. Each answer is followed by suggested follow-ups.',
    details: [
      'Closest-document suggestions on no-match queries',
      'Starter questions grounded in your actual document filenames',
      'Follow-up suggestion chips after each answer',
    ],
  },
  {
    id: '2026.07',
    title: 'Chat and viewer polish',
    date: 'July 2026',
    category: 'User Experience',
    summary: 'Scroll arrows on long result lists. Media in the document viewer pauses when switching documents or leaving the page. PDF rendering cleanup prevents memory leaks on long reading sessions.',
    details: [
      'Scroll arrows on chat history and search results',
      'Viewer pauses audio and video when you navigate away',
      'PDF rendering no longer leaks canvases on long sessions',
    ],
  },
];

const CATEGORY_COLORS: Record<Release['category'], string> = {
  'Access Control': '#B93C32',
  'Connectors': '#B59876',
  'Intelligence': '#4f8fdd',
  'Governance': '#5cb87a',
  'User Experience': '#b45ad4',
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
            Recent capability releases, in reverse chronological order. Each release is deployed to production and verified before it ships.
          </p>

          <div className="space-y-8">
            {RELEASES.map((r) => (
              <article
                key={r.id + r.title}
                className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7"
              >
                <div className="flex items-center gap-3 mb-3 flex-wrap">
                  <span
                    className="text-[10px] font-bold tracking-[0.14em] uppercase px-2.5 py-1 rounded-full text-white"
                    style={{ background: CATEGORY_COLORS[r.category] }}
                  >
                    {r.category}
                  </span>
                  <span className="text-[12px] text-[#E7E6E4]/55">{r.date}</span>
                </div>
                <h2 className="text-[20px] font-semibold text-[#E7E6E4] tracking-tight mb-2">
                  {r.title}
                </h2>
                <p className="text-[14px] leading-[1.65] text-[#E7E6E4]/72 mb-4">
                  {r.summary}
                </p>
                <ul className="space-y-2">
                  {r.details.map((d, j) => (
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
              Book a live demo and we&rsquo;ll walk you through every capability above against a working enterprise library — search, chat with citations, access control, connectors, governance, and the entity knowledge graph.
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
