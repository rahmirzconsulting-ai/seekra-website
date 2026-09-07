import { Bot, Sparkles, Zap, Network, GitFork, Layers } from 'lucide-react';
import { Reveal } from './reveal';

const MODES = [
  {
    icon: Zap,
    eyebrow: 'Mode 01 · Auto',
    title: 'Standard answers',
    body: 'The default — one retrieval pass, one synthesis step. Right for most questions: &ldquo;what does the policy say about X?&rdquo;, &ldquo;summarize this contract&rdquo;, &ldquo;find the clause about Y&rdquo;.',
    bullets: [
      'Hybrid semantic + keyword retrieval',
      'Citations link to the exact source page or timestamp',
      'Abstains rather than hallucinates',
      'Answers in the language of the question (Arabic or English)',
    ],
  },
  {
    icon: Bot,
    eyebrow: 'Mode 02 · Agent',
    title: 'Multi-step research',
    body: 'For questions that need more than one lookup. Seekra&rsquo;s planner picks from a small set of internal tools — search, list, summarize, find entities, compare documents — and runs them in sequence, then synthesizes the answer.',
    bullets: [
      'Search across the whole library or a specific scope',
      'List documents and their attributes',
      'Summarize a single named document',
      'Find documents mentioning a person or organization',
      'Compare two documents side by side',
    ],
  },
  {
    icon: Sparkles,
    eyebrow: 'Mode 03 · Deep',
    title: 'Comprehensive cited answers',
    body: 'For complex questions that span many documents. The question is broken into focused sub-questions; each runs its own retrieval pass; chunks found by multiple passes rank highest; a comprehensive multi-section answer is synthesized.',
    bullets: [
      'Decomposition into focused sub-questions',
      'Multi-pass retrieval with cross-pass ranking',
      'Larger context budget than standard mode',
      'Multi-section answers with cited headers',
    ],
  },
];

const ENTITY_FEATURES = [
  {
    icon: Network,
    title: 'Auto-extracted knowledge graph',
    body: 'People, organizations, and locations are identified in every document during indexing — in Arabic and English. No one tags these relationships manually; the graph builds itself.',
  },
  {
    icon: GitFork,
    title: 'Co-occurrence relationships',
    body: 'When two entities appear together in a document, Seekra infers a relationship between them. The graph updates every time you add a new document — your enterprise knowledge graph is always current.',
  },
  {
    icon: Layers,
    title: 'Entity-aware answers',
    body: 'Ask &ldquo;who works on the flagship project?&rdquo; and Seekra recognizes the names and the project as entities, then traverses the graph to find the answer — not just keyword matching, but content-aware understanding.',
  },
];

export function Intelligence() {
  return (
    <section id="intelligence" className="py-24 lg:py-32 bg-[#202020] text-[#E7E6E4]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow mb-3">
            Intelligence
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Three answer modes. One knowledge graph<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#E7E6E4]/65 max-w-[880px]">
            Not every question needs the same depth of research. Seekra offers three answer modes — standard for fast Q&amp;A, agent for multi-step lookups, deep for comprehensive multi-pass synthesis — plus an automatically-built knowledge graph that understands the people, organizations, and locations in your documents.
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
              Seekra automatically identifies people, organizations, and locations in every document — in Arabic and English — and infers relationships between them. The graph updates on every upload, with no manual tagging.
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
