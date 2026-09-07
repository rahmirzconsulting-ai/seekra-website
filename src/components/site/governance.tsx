import { ShieldCheck, Link2, FileSearch, Network, GitBranch, Lock } from 'lucide-react';
import { Reveal } from './reveal';

const PILLARS = [
  {
    icon: ShieldCheck,
    title: 'Tamper-evident audit trail',
    body: 'Every action — login, search, chat, upload, scope change, override grant, user deactivation — is recorded and hash-chained. Any retroactive edit breaks the chain, detectable on demand. Concurrent writes are safe under load.',
  },
  {
    icon: Link2,
    title: 'PII lineage tracking',
    body: 'When personal data is masked before an AI call, the event is logged with a masked sample. Prove to a regulator that no raw personal data ever left your tenant. Aggregate counts surface repeated findings at a glance.',
  },
  {
    icon: FileSearch,
    title: 'Answer provenance',
    body: 'Trace any answer through the full pipeline: question, retrieval, AI synthesis, final response. Each cited chunk shows a confidence score. Click any citation to open the source at the exact page or timestamp.',
  },
  {
    icon: Network,
    title: 'Entity relations',
    body: 'People, organizations, and locations are identified and linked automatically. Ask &ldquo;who works on the flagship project?&rdquo; and Seekra traverses the knowledge graph — not just keyword matching, but content-aware understanding.',
  },
  {
    icon: GitBranch,
    title: 'Org-tree access control',
    body: 'A tree of companies, departments, and teams. Documents scoped to a node are visible only to users in that subtree. Four classification levels (Public / Internal / Confidential / Restricted) plus per-user clearance.',
  },
  {
    icon: Lock,
    title: 'Offboard with confidence',
    body: 'When an employee leaves, deactivate their account and their existing sessions are rejected instantly — no grace period. Their row is preserved for audit, so historical activity still references them.',
  },
] as const;

export function Governance() {
  return (
    <section id="governance" className="py-20 lg:py-28 bg-[#202020] text-[#E7E6E4] border-t border-[#E7E6E4]/10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-3xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow mb-3">
            Governance · Provable &amp; Tamper-Evident
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Every answer traceable. Every PII masked. Every action auditable. Every access scoped<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#E7E6E4]/65 max-w-[640px]">
            Six governance pillars, all in production. Few platforms offer this combination — and we can prove each one with a live audit-trail query during the demo.
          </p>
        </Reveal>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-7">
          {PILLARS.map((p, i) => {
            const Icon = p.icon;
            return (
              <Reveal key={p.title} delay={(i % 3) * 100}>
                <article className="bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15 rounded-[14px] p-7 h-full">
                  <div className="w-14 h-14 rounded-[12px] bg-[#B59876]/15 flex items-center justify-center mb-5">
                    <Icon className="w-7 h-7 text-[#B59876]" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-[18px] font-semibold text-[#E7E6E4] tracking-tight leading-snug">
                    {p.title}
                  </h3>
                  <p className="mt-2 text-[13px] leading-[1.6] text-[#E7E6E4]/65">
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
