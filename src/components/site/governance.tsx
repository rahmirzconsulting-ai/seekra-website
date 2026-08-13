import { ShieldCheck, Link2, FileSearch } from 'lucide-react';
import { Reveal } from './reveal';

const PILLARS = [
  {
    icon: ShieldCheck,
    title: 'Tamper-evident audit',
    body: 'Every action is hash-chained. Any retroactive edit breaks the chain — detectable on demand.',
  },
  {
    icon: Link2,
    title: 'PII lineage tracking',
    body: 'When PII is masked before an LLM call, the event is logged. Prove it was never sent in raw form.',
  },
  {
    icon: FileSearch,
    title: 'Provenance graph',
    body: 'Trace any answer to its source chunk, its PII findings, and the LLM calls that received the masked version.',
  },
] as const;

export function Governance() {
  return (
    <section className="py-20 lg:py-28 bg-[#202020] text-[#E7E6E4] border-t border-[#E7E6E4]/10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-3xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow mb-3">
            Governance · Provable &amp; Tamper-Evident
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Every answer traceable. Every PII masked. Every action auditable<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#E7E6E4]/65 max-w-[640px]">
            No competitor in the Gulf enterprise AI segment offers this combination.
          </p>
        </Reveal>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {PILLARS.map((p, i) => {
            const Icon = p.icon;
            return (
              <Reveal key={p.title} delay={i * 120}>
                <article className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7 h-full">
                  <div className="w-14 h-14 rounded-[12px] bg-[#B59876]/15 flex items-center justify-center mb-5">
                    <Icon className="w-7 h-7 text-[#B59876]" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-[18px] font-semibold text-[#E7E6E4] tracking-tight leading-snug">
                    {p.title}
                  </h3>
                  <p className="mt-2 text-[14px] leading-[1.6] text-[#E7E6E4]/65">
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
