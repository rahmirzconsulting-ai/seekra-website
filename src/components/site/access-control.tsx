import { Building2, ShieldCheck, KeyRound, UserX, GitBranch, Lock } from 'lucide-react';
import { Reveal } from './reveal';

const PILLARS = [
  {
    icon: GitBranch,
    title: 'Org-tree scoping',
    body: 'Mirror your organization as a tree of companies, departments, and teams. Documents scoped to a node are visible only to users in that subtree — access flows down, never sideways.',
  },
  {
    icon: Lock,
    title: '4-level classification',
    body: 'Every document is Public, Internal, Confidential, or Restricted. Each user sees only documents at or below their clearance level — enforced behind the scenes, not just hidden in the interface.',
  },
  {
    icon: KeyRound,
    title: 'Cross-scope overrides',
    body: 'Grant a user read access to a specific document outside their subtree — without elevating their overall clearance. The grant takes effect immediately on the next search.',
  },
  {
    icon: UserX,
    title: 'Offboard with confidence',
    body: 'When an employee leaves, deactivate their account and their existing sessions are rejected instantly. Their row is preserved for audit, so historical activity still references them — but they cannot log in.',
  },
] as const;

const CLASSIFICATIONS = [
  { name: 'Public', color: '#5cb87a', desc: 'Visible org-wide — even outside the document\u2019s home department', count: 'cls 0' },
  { name: 'Internal', color: '#4f8fdd', desc: 'Default — visible to anyone in the document\u2019s scope', count: 'cls 1' },
  { name: 'Confidential', color: '#e0764f', desc: 'Requires clearance level 2 or higher', count: 'cls 2' },
  { name: 'Restricted', color: '#B93C32', desc: 'Requires clearance level 3 — top leadership only', count: 'cls 3' },
] as const;

export function AccessControl() {
  return (
    <section id="access-control" className="py-24 lg:py-32 bg-white text-[#1F1A14] border-t border-black/[0.06]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow-ink mb-3">
            Enterprise Access Control
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Defense in depth, not defense at the interface<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#4A3F33] max-w-[880px]">
            Seekra enforces access at the deepest layer of the system — when a user searches or asks a question, the results they receive are filtered before they ever reach the screen. A user in one department cannot see another department&rsquo;s confidential documents — not because the interface hides them, but because the system never retrieves them in the first place. Even if they knew a document&rsquo;s name and tried to open it directly, access would be denied.
          </p>
        </Reveal>

        {/* 4 pillars */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 mb-12">
          {PILLARS.map((p, i) => {
            const Icon = p.icon;
            return (
              <Reveal key={p.title} delay={i * 90}>
                <article className="bg-[#F5F4F2] border border-black/[0.08] rounded-[14px] p-6 h-full">
                  <div className="w-12 h-12 rounded-[10px] bg-[#B59876]/12 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-[#B59876]" strokeWidth={1.5} />
                  </div>
                  <h3 className="text-[17px] font-semibold text-[#1F1A14] tracking-tight leading-snug">
                    {p.title}
                  </h3>
                  <p className="mt-2 text-[13px] leading-[1.55] text-[#4A3F33]">
                    {p.body}
                  </p>
                </article>
              </Reveal>
            );
          })}
        </div>

        {/* Classification legend */}
        <Reveal delay={120}>
          <div className="bg-[#202020] rounded-[14px] p-7 lg:p-8">
            <div className="flex items-center gap-3 mb-5">
              <ShieldCheck className="w-6 h-6 text-[#B59876]" strokeWidth={1.5} />
              <h3 className="text-[18px] font-semibold text-[#E7E6E4] tracking-tight">
                Four classification levels
              </h3>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {CLASSIFICATIONS.map((c, i) => (
                <div
                  key={i}
                  className="rounded-[10px] p-4 bg-[#E7E6E4]/[0.04] border border-[#E7E6E4]/15"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ background: c.color }}
                    />
                    <span className="text-[15px] font-semibold text-[#E7E6E4]">{c.name}</span>
                  </div>
                  <div className="text-[12px] text-[#E7E6E4]/65 leading-[1.5]">{c.desc}</div>
                </div>
              ))}
            </div>
            <p className="mt-5 text-[12px] italic text-[#E7E6E4]/55 leading-[1.5]">
              Administrators and auditors bypass classification. Every access decision is recorded in the tamper-evident audit trail.
            </p>
          </div>
        </Reveal>

        <Reveal delay={200}>
          <p className="mt-8 text-[14px] leading-[1.6] text-[#4A3F33] max-w-[680px]">
            <span className="font-semibold text-[#1F1A14]">Why this matters:</span> regulated industries require need-to-know access control with auditable access decisions. Seekra delivers this without the operational overhead of per-document permission lists — the organization tree plus four classification levels covers the vast majority of access policies in a few minutes of setup.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
