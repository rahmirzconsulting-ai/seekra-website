import { Server, EyeOff, ShieldCheck, ScrollText } from 'lucide-react';
import { Reveal } from './reveal';

const SECURITY_CARDS = [
  {
    icon: Server,
    title: 'Three deployment tiers',
    body: 'Cloud-native, self-hosted, or fully air-gapped. You choose where the AI runs.',
  },
  {
    icon: EyeOff,
    title: 'PII masked at the source',
    body: 'Names, IDs, emails, and phone numbers redacted before any AI call. Every masking event is logged with hash-chained lineage.',
  },
  {
    icon: ShieldCheck,
    title: 'Tamper-evident audit trail',
    body: 'Every action is hash-chained. Any retroactive edit breaks the chain — detectable on demand via the admin API.',
  },
  {
    icon: ScrollText,
    title: 'Full audit logging + provenance',
    body: 'Trace any answer to its source chunk, its PII findings, and the LLM calls that received the masked version.',
  },
] as const;

export function Trust() {
  return (
    <section id="security" className="relative py-24 lg:py-32 bg-[#202020] text-[#E7E6E4] overflow-hidden">
      {/* Soft radial tan glow top-right */}
      <div
        aria-hidden
        className="absolute pointer-events-none"
        style={{
          width: 720,
          height: 720,
          top: -260,
          right: -200,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(181,152,118,0.20) 0%, rgba(181,152,118,0) 65%)',
          filter: 'blur(8px)',
        }}
      />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="text-[13px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-3">
            Trust · Security &amp; Sovereignty
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(36px, 5.5vw, 64px)', lineHeight: 1.05, letterSpacing: '-0.03em' }}>
            Nothing leaves the box<span className="text-[#B93C32]" style={{ fontSize: '1.15em' }}>.</span>
          </h2>
          <p className="mt-6 text-[17px] leading-[1.6] text-[#E7E6E4]/78 max-w-[860px]">
            Three deployment tiers — cloud-native, self-hosted, or fully air-gapped. You choose where the AI runs and how isolated your environment is. Personal information is masked at the source before any AI model is involved. In self-hosted and air-gapped deployments, the AI model itself runs on your servers — nothing leaves the box.
          </p>
        </Reveal>

        <div className="grid sm:grid-cols-2 gap-6">
          {SECURITY_CARDS.map((card, i) => {
            const Icon = card.icon;
            return (
              <Reveal key={card.title} delay={i * 120}>
                <article className="bg-[#E7E6E4]/[0.05] border border-[#E7E6E4]/15 rounded-[14px] p-6 lg:p-7 h-full">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 flex-shrink-0 rounded-[12px] bg-[#B59876]/15 flex items-center justify-center">
                      <Icon className="w-7 h-7 text-[#B59876]" strokeWidth={1.5} />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-[18px] font-semibold text-[#E7E6E4] tracking-tight leading-snug">
                        {card.title}
                      </h3>
                      <p className="mt-1.5 text-[14px] leading-[1.55] text-[#E7E6E4]/70">
                        {card.body}
                      </p>
                    </div>
                  </div>
                </article>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
