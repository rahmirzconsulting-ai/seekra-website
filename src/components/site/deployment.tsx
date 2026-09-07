import { Cloud, Server, Lock, KeyRound } from 'lucide-react';
import { Reveal } from './reveal';

const TIERS = [
  {
    tier: 'Tier 01 · Fastest',
    title: 'Cloud Native',
    body: 'Seekra runs in your cloud tenant and can leverage industry-leading external AI models, with PII automatically masked before any external call. Best AI capability, fastest to deploy.',
    icon: Cloud,
    featured: false,
    connectors: 'All connectors',
    sso: 'Major cloud identity providers + on-prem',
  },
  {
    tier: 'Tier 02 · Sovereign',
    title: 'Self-Hosted',
    body: 'Seekra runs entirely on your own infrastructure — cloud VM or on-premises servers — with AI models hosted locally. Full data sovereignty. Nothing leaves your network.',
    icon: Server,
    featured: false,
    connectors: 'All connectors',
    sso: 'Major cloud identity providers + on-prem',
  },
  {
    tier: 'Tier 03 · Maximum Security',
    title: 'Air-Gapped',
    body: 'Fully isolated self-hosted deployment with no external network connection. For classified, sovereign, or maximum-security workloads where even update traffic is not permitted.',
    icon: Lock,
    featured: true,
    connectors: 'Local folder + SFTP only',
    sso: 'On-prem identity provider',
  },
];

const PLATFORM_FEATURES = [
  {
    icon: KeyRound,
    title: 'Single sign-on (SSO)',
    body: 'Single sign-on integration with major cloud and on-premises identity providers. New hires are provisioned automatically based on their identity-provider group membership; offboards propagate within minutes. A fallback local login is available for break-glass administrators.',
  },
];

export function Deployment() {
  return (
    <section id="deployment" className="py-24 lg:py-32 bg-[#D8D6D3] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow-ink mb-3">
            Deployment
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Three tiers. One platform. You choose<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#4A3F33] max-w-[880px]">
            Seekra runs in three deployment tiers — from cloud-native to fully air-gapped — so you choose exactly where the AI runs and how isolated your environment is. The platform stays the same; only the AI location and network exposure change. All three tiers support single sign-on and the full feature set.
          </p>
        </Reveal>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 items-start">
          {TIERS.map((tier, i) => {
            const Icon = tier.icon;
            return (
              <Reveal
                key={tier.title}
                delay={i * 120}
                className={tier.featured ? 'md:-mt-3' : ''}
              >
                <article
                  className={`relative rounded-[14px] p-7 lg:p-8 h-full overflow-hidden ${
                    tier.featured
                      ? 'bg-[#202020] border border-[#B59876]/40 shadow-2xl shadow-[#B59876]/20'
                      : 'bg-white border border-black/[0.10] shadow-sm'
                  }`}
                >
                  {/* Featured glow */}
                  {tier.featured && (
                    <div
                      aria-hidden
                      className="absolute pointer-events-none"
                      style={{
                        width: 320,
                        height: 320,
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        borderRadius: '50%',
                        background: 'radial-gradient(circle, rgba(181,152,118,0.30) 0%, rgba(181,152,118,0) 65%)',
                        filter: 'blur(8px)',
                      }}
                    />
                  )}

                  <div className="relative">
                    {/* Icon square */}
                    <div
                      className={`w-16 h-16 rounded-[12px] flex items-center justify-center ${
                        tier.featured ? 'bg-[#B59876]/18' : 'bg-[#B59876]/10'
                      }`}
                    >
                      <Icon
                        className={`w-9 h-9 ${tier.featured ? 'text-[#B59876]' : 'text-[#B59876]'}`}
                        strokeWidth={1.5}
                      />
                    </div>

                    {/* Title */}
                    <h3
                      className={`mt-5 text-[22px] font-semibold tracking-tight ${
                        tier.featured ? 'text-[#E7E6E4]' : 'text-[#1F1A14]'
                      }`}
                    >
                      {tier.title}
                    </h3>

                    {/* Body */}
                    <p
                      className={`mt-3 text-[14px] leading-[1.6] ${
                        tier.featured ? 'text-[#E7E6E4]/78' : 'text-[#4A3F33]'
                      }`}
                    >
                      {tier.body}
                    </p>

                    {/* Integration badges */}
                    <div className="mt-5 space-y-2">
                      <div className={`text-[11px] ${tier.featured ? 'text-[#E7E6E4]/65' : 'text-[#4A3F33]'}`}>
                        <span className="font-semibold tracking-tight">Connectors:</span> {tier.connectors}
                      </div>
                      <div className={`text-[11px] ${tier.featured ? 'text-[#E7E6E4]/65' : 'text-[#4A3F33]'}`}>
                        <span className="font-semibold tracking-tight">SSO:</span> {tier.sso}
                      </div>
                    </div>

                    {/* Tier label */}
                    <div className="mt-6 text-[11px] font-semibold tracking-[0.18em] uppercase text-[#B59876]">
                      {tier.tier}
                    </div>
                  </div>
                </article>
              </Reveal>
            );
          })}
        </div>

        {/* Platform feature: SSO */}
        <div className="mt-10 grid md:grid-cols-1 gap-5 max-w-2xl">
          {PLATFORM_FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <Reveal key={i} delay={i * 100}>
                <article className="bg-white border border-black/[0.08] rounded-[12px] p-5 flex gap-4">
                  <div className="w-11 h-11 rounded-[10px] bg-[#B59876]/12 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-[#B59876]" strokeWidth={1.5} />
                  </div>
                  <div>
                    <h4 className="text-[15px] font-semibold text-[#1F1A14] tracking-tight mb-1">
                      {f.title}
                    </h4>
                    <p className="text-[12px] leading-[1.55] text-[#4A3F33]">
                      {f.body}
                    </p>
                  </div>
                </article>
              </Reveal>
            );
          })}
        </div>

        <Reveal delay={300}>
          <p className="mt-10 text-[12px] italic text-[#4A3F33]">
            No pricing is published. Deployment tier and scale are discussed in person during the demo.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
