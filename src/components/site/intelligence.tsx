import { Bot, Sparkles, Zap, Network, GitFork, Layers } from 'lucide-react';
import { Reveal } from './reveal';

const MODES = [
  {
    icon: Zap,
    eyebrow: 'Mode 01 · Auto',
    title: 'Standard single-pass answer',
    body: 'The default — one retrieval pass, one synthesis call. Fast (3–8 seconds). Right for 80% of questions: "what does the policy say about X?", "summarize this contract", "find the clause about Y".',
    badge: '3–8s',
    bullets: [
      'Hybrid semantic + keyword retrieval over chunks',
      'Citations link to source page / timestamp',
      'Abstains rather than hallucinates',
      'Bilingual — answers in the language of the question',
    ],
  },
  {
    icon: Bot,
    eyebrow: 'Mode 02 · Agent',
    title: 'Planner picks from 5 tools',
    body: 'For questions that need multiple steps. The planner LLM emits a small JSON plan: which tools to call, in what order. Each tool is a deterministic, permission-scoped query — the LLM never touches the database directly.',
    badge: '15–60s',
    bullets: [
      'search_library — hybrid semantic + keyword search',
      'list_documents — library overview (deterministic SQL)',
      'summarize_document — AI summary of one named doc',
      'find_entity — docs mentioning a person or organization',
      'compare_documents — chunk-level diff of two named docs',
    ],
  },
  {
    icon: Sparkles,
    eyebrow: 'Mode 03 · Deep',
    title: 'Multi-pass research, comprehensive cited answer',
    body: 'For complex questions that need synthesis across many documents. The question is decomposed into 2–4 sub-questions; each runs its own retrieval pass; chunks found by MULTIPLE passes rank highest; a comprehensive cited answer is synthesized.',
    badge: '5–20s',
    bullets: [
      'Decomposition into 2–4 focused sub-questions',
      'Multi-pass retrieval with cross-pass chunk ranking',
      'Larger context budget (9,000 chars vs 6,000)',
      'Multi-section answers with cited headers',
    ],
  },
] as const;

const ENTITY_FEATURES = [
  {
    icon: Network,
    title: 'Auto-extracted knowledge graph',
    body: 'Persons, organizations, and locations are extracted from every document during indexing — in Arabic and English. No human tags these relationships; the graph builds itself.',
  },
  {
    icon: GitFork,
    title: 'Co-occurrence relationships',
    body: 'When two entities appear in the same document, Seekra infers a relationship. The graph updates every time you upload a new document — your enterprise knowledge graph, always current.',
  },
  {
    icon: Layers,
    title: 'Entity-aware chat',
    body: 'Ask "who is the director of Project Golden Falcon?" — Seekra recognizes Yousef Al Saedi as a person entity and Project Golden Falcon as a title entity, then matches them via the graph. Not keyword matching — content-aware.',
  },
] as const;

export function Intelligence() {
  return (
    <section id="intelligence" className="py-24 lg:py-32 bg-[#202020] text-[#E7E6E4]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow mb-3">
            Intelligence · Briefs #20, #21, #16
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Three answer modes. One knowledge graph<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#E7E6E4]/65 max-w-[880px]">
            Not every question needs the same research depth. Seekra offers three answer modes — Auto for fast Q&amp;A, Agent for multi-step research, Deep for comprehensive multi-pass synthesis — plus an auto-built entity knowledge graph that understands people, organizations, and the relationships between them.
          </p>
        </Reveal>

        {/* 3 answer modes */}
        <div className="grid lg:grid-cols-3 gap-6 mb-16">
          {MODES.map((m, i) => {
            const Icon = m.icon;
            return (
              <Reveal key={m.title} delay={i * 100}>
                <article className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7 h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-[10px] bg-[#B59876]/15 flex items-center justify-center">
                      <Icon className="w-6 h-6 text-[#B59876]" strokeWidth={1.5} />
                    </div>
                    <span className="text-[10px] font-bold tracking-[0.14em] uppercase text-[#B59876] bg-[#B59876]/12 px-2 py-1 rounded-full">
                      {m.badge}
                    </span>
                  </div>
                  <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#B59876] mb-2">
                    {m.eyebrow}
                  </div>
                  <h3 className="text-[18px] font-semibold text-[#E7E6E4] tracking-tight leading-snug mb-2">
                    {m.title}
                  </h3>
                  <p className="text-[13px] leading-[1.6] text-[#E7E6E4]/65 mb-4">
                    {m.body}
                  </p>
                  <ul className="space-y-2">
                    {m.bullets.map((b, j) => (
                      <li key={j} className="flex items-start gap-2 text-[12px] leading-[1.5] text-[#E7E6E4]/85">
                        <span className="text-[#B59876] mt-0.5 flex-shrink-0">›</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </article>
              </Reveal>
            );
          })}
        </div>

        {/* Entity graph sub-section */}
        <Reveal delay={120}>
          <div className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7 lg:p-8">
            <div className="flex items-center gap-3 mb-6">
              <Network className="w-6 h-6 text-[#B59876]" strokeWidth={1.5} />
              <h3 className="text-[20px] font-semibold text-[#E7E6E4] tracking-tight">
                Entity knowledge graph
              </h3>
            </div>
            <p className="text-[14px] leading-[1.6] text-[#E7E6E4]/72 max-w-[760px] mb-7">
              Seekra automatically extracts persons, organizations, and locations from every document — in Arabic and English — and infers co-occurrence relationships. The graph updates on every upload, with no human tagging.
            </p>
            <div className="grid sm:grid-cols-3 gap-5">
              {ENTITY_FEATURES.map((f, i) => {
                const Icon = f.icon;
                return (
                  <div key={i}>
                    <div className="w-10 h-10 rounded-[8px] bg-[#B59876]/15 flex items-center justify-center mb-3">
                      <Icon className="w-5 h-5 text-[#B59876]" strokeWidth={1.5} />
                    </div>
                    <h4 className="text-[14px] font-semibold text-[#E7E6E4] mb-1.5 tracking-tight">
                      {f.title}
                    </h4>
                    <p className="text-[12px] leading-[1.55] text-[#E7E6E4]/65">
                      {f.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
