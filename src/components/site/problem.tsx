import { FolderX, CloudOff, HelpCircle } from 'lucide-react';
import { Reveal } from './reveal';

const PROBLEMS = [
  {
    num: '01',
    icon: FolderX,
    title: 'Knowledge buried in files',
    body: 'Critical information lives inside thousands of PDFs, scans, and Office documents that no one can effectively search. Staff spend hours locating a single clause, and institutional knowledge walks out the door when experienced employees leave.',
  },
  {
    num: '02',
    icon: CloudOff,
    title: 'Cloud AI means data leaves the building',
    body: 'Mainstream AI assistants ask you to upload your documents to their servers. For government, legal, healthcare, and financial work, that is often non-negotiable — the data cannot leave your jurisdiction or your network.',
  },
  {
    num: '03',
    icon: HelpCircle,
    title: "Answers without sources can't be trusted",
    body: 'When an AI produces an answer with no link to where the information came from, it cannot be verified. In regulated environments, an unverifiable answer is the same as no answer at all.',
  },
];

export function Problem() {
  return (
    <section className="py-24 lg:py-32 bg-[#E7E6E4] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-3xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow-ink mb-3">
            Why Seekra Exists
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Three problems every large archive suffers from<span className="text-[#B93C32]">.</span>
          </h2>
        </Reveal>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {PROBLEMS.map((p, i) => {
            const Icon = p.icon;
            return (
              <Reveal key={p.num} delay={i * 120}>
                <article className="bg-white border border-black/[0.08] rounded-[14px] p-8 h-full shadow-sm">
                  <div className="font-mono font-semibold text-[28px] text-[#B59876] tabular-nums">
                    {p.num}
                  </div>
                  <Icon
                    className="w-9 h-9 mt-4 text-[#B59876]"
                    strokeWidth={1.5}
                  />
                  <h3 className="mt-4 text-[22px] font-semibold text-[#1F1A14] leading-snug tracking-tight">
                    {p.title}
                  </h3>
                  <p className="mt-3 text-[15px] leading-[1.6] text-[#4A3F33]">
                    {p.body}
                  </p>
                </article>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
