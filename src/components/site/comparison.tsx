import { Reveal } from './reveal';

type Status = 'yes' | 'partial' | 'no';

type Row = {
  feature: string;
  seekra: Status;
  cloud: Status;        // ChatGPT / Gemini / generic cloud AI
  legacy: Status;       // Elastic / Solr / legacy enterprise search
};

const ROWS: Row[] = [
  // Access control
  { feature: 'Data residency inside your infrastructure', seekra: 'yes', cloud: 'no', legacy: 'yes' },
  { feature: 'Air-gapped / offline option', seekra: 'yes', cloud: 'no', legacy: 'yes' },
  { feature: 'Org-tree scoped access (company/department/team)', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: '4-level document classification + per-user clearance', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: 'Cross-scope override grants (without elevating clearance)', seekra: 'yes', cloud: 'no', legacy: 'no' },
  // Connectors
  { feature: '9 data connectors (SharePoint, Drive, S3, Azure, GCS, SFTP, OSS, IMAP, local)', seekra: 'yes', cloud: 'partial', legacy: 'partial' },
  { feature: 'Local folder auto-ingest (drop file → indexed automatically)', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: 'Source-side conflict resolution + versioning', seekra: 'yes', cloud: 'no', legacy: 'no' },
  // Intelligence
  { feature: 'Natural-language Q&A with page-level citations', seekra: 'yes', cloud: 'yes', legacy: 'no' },
  { feature: 'Agent mode (multi-step research using internal tools)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Deep answer mode (multi-pass research for complex questions)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Auto-extracted entity knowledge graph (Arabic + English)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Visual / image search', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Voice-driven document navigation (Arabic + English)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  // Governance
  { feature: 'PII masked at source (before any AI call)', seekra: 'yes', cloud: 'partial', legacy: 'yes' },
  { feature: 'PII lineage tracking (prove no raw PII left tenant)', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: 'Tamper-evident audit trail (hash-chained)', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: 'Provenance graph (full answer traceability)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Confidence-aware answers (relevance scores per source)', seekra: 'yes', cloud: 'partial', legacy: 'no' },
  { feature: 'Document version diff', seekra: 'yes', cloud: 'no', legacy: 'partial' },
  { feature: 'Abstention rather than hallucination', seekra: 'yes', cloud: 'partial', legacy: 'yes' },
  // Identity
  { feature: 'Single sign-on + automated user provisioning (Azure AD, Google Workspace)', seekra: 'partial', cloud: 'yes', legacy: 'partial' },
  { feature: 'Offboard employees with immediate access revocation', seekra: 'yes', cloud: 'partial', legacy: 'yes' },
];

function Cell({ value }: { value: Status }) {
  if (value === 'yes') {
    return <span className="text-[#B59876] font-semibold">✓ Yes</span>;
  }
  if (value === 'no') {
    return <span className="text-[#B93C32] font-semibold">✗ No</span>;
  }
  return <span className="text-[#4A3F33] font-medium italic">Partial</span>;
}

export function Comparison() {
  return (
    <section id="comparison" className="py-24 lg:py-32 bg-[#E7E6E4] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-10 lg:mb-12">
          <div className="seekra-eyebrow-ink mb-3">
            How Seekra Compares
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 42px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Three-way comparison<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.55] text-[#4A3F33] max-w-[880px]">
            Cloud AI (ChatGPT, Gemini) is strong for general-purpose work but fails on data residency and access control. Legacy enterprise search (Elastic, Solr) is strong on residency but offers no AI. Seekra is purpose-built for the gap between them — Gulf enterprise data handling with cited AI answers.
          </p>
        </Reveal>

        <Reveal delay={120}>
          <div className="bg-white border border-black/[0.10] rounded-[12px] overflow-hidden overflow-x-auto">
            <table
              className="w-full"
              style={{ fontFamily: 'Poppins, Inter, system-ui, sans-serif' }}
            >
              <thead>
                <tr className="bg-[#F5F4F2] border-b border-black/[0.10]">
                  <th className="text-left text-[11px] font-semibold tracking-[0.14em] uppercase text-[#1F1A14] px-5 py-3.5" style={{ width: '46%' }}>
                    Capability
                  </th>
                  <th className="text-center text-[11px] font-semibold tracking-[0.14em] uppercase text-[#B59876] px-3 py-3.5" style={{ width: '18%' }}>
                    Seekra
                  </th>
                  <th className="text-center text-[11px] font-semibold tracking-[0.14em] uppercase text-[#4A3F33] px-3 py-3.5" style={{ width: '18%' }}>
                    Cloud AI
                  </th>
                  <th className="text-center text-[11px] font-semibold tracking-[0.14em] uppercase text-[#4A3F33] px-3 py-3.5" style={{ width: '18%' }}>
                    Legacy Search
                  </th>
                </tr>
              </thead>
              <tbody>
                {ROWS.map((row, i) => (
                  <tr
                    key={i}
                    className={`border-b border-black/[0.05] ${i % 2 === 1 ? 'bg-[#FAFAF8]' : ''}`}
                  >
                    <td className="text-[13px] text-[#1F1A14] px-5 py-3.5 leading-snug">
                      {row.feature}
                    </td>
                    <td className="text-center text-[13px] px-3 py-3.5">
                      <Cell value={row.seekra} />
                    </td>
                    <td className="text-center text-[13px] px-3 py-3.5">
                      <Cell value={row.cloud} />
                    </td>
                    <td className="text-center text-[13px] px-3 py-3.5">
                      <Cell value={row.legacy} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>

        <Reveal delay={200}>
          <p className="mt-6 text-[12px] italic text-[#4A3F33] max-w-[860px]">
            Cloud AI = ChatGPT, Gemini, Claude, and similar general-purpose assistants. Legacy Search = Elastic, Solr, SharePoint search, and similar keyword-based enterprise search. "Partial" means the capability exists but is incomplete, requires significant configuration, or depends on a third-party integration.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
