import { Landmark, Gavel, Wallet, Stethoscope, Zap } from 'lucide-react';
import { Reveal } from './reveal';

const SECTORS = [
  {
    icon: Landmark,
    label: 'Government & Public Sector',
    desc: 'Sovereign archives, classified document handling, Arabic-first citizen services, complete audit trail.',
  },
  {
    icon: Gavel,
    label: 'Legal & Compliance',
    desc: 'Case-file Q&A with verifiable citations. Privileged-document isolation. Read-only auditor oversight.',
  },
  {
    icon: Wallet,
    label: 'Banking & Financial Services',
    desc: 'Policy and contract search across thousands of documents. Personal information redacted before AI.',
  },
  {
    icon: Stethoscope,
    label: 'Healthcare',
    desc: 'Patient record Q&A, image-based diagnostic search, on-prem deployment for HIPAA-equivalent rules.',
  },
  {
    icon: Zap,
    label: 'Energy & Utilities',
    desc: 'Field inspection photos searchable by image. Arabic-first operations documentation. Air-gapped option.',
  },
] as const;

export function UseCases() {
  return (
    <section className="py-20 lg:py-28 bg-[#E7E6E4] text-[#1F1A14] border-t border-black/[0.06]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-3xl mb-10 lg:mb-12">
          <div className="seekra-eyebrow-ink mb-3">
            Who Seekra Is Built For
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(24px, 3.5vw, 38px)', lineHeight: 1.2, letterSpacing: '-0.02em' }}>
            Built for the Gulf&rsquo;s most regulated sectors<span className="text-[#B93C32]">.</span>
          </h2>
        </Reveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-5">
          {SECTORS.map((sector, i) => {
            const Icon = sector.icon;
            return (
              <Reveal key={sector.label} delay={i * 90}>
                <article className="bg-white border border-black/[0.08] rounded-[12px] p-5 h-full shadow-sm flex flex-col">
                  <div className="w-12 h-12 rounded-[10px] bg-[#B59876]/12 flex items-center justify-center mb-3">
                    <Icon className="w-6 h-6 text-[#B59876]" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-[15px] font-semibold text-[#1F1A14] tracking-tight leading-snug">
                    {sector.label}
                  </h3>
                  <p className="mt-1.5 text-[12px] leading-[1.5] text-[#4A3F33] flex-1">
                    {sector.desc}
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
