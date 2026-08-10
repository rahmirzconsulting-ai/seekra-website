'use client';

import { useEffect, useState } from 'react';
import { ArrowRight, ChevronRight } from 'lucide-react';

const SCENES = [
  {
    id: 'ask',
    label: 'Ask — answers with citations',
    pill: 'Ask',
    caption: 'Answers with citations',
    render: () => <AskScene />,
  },
  {
    id: 'see',
    label: 'See — search by image',
    pill: 'See',
    caption: 'Search by image',
    render: () => <SeeScene />,
  },
  {
    id: 'speak',
    label: 'Speak — Arabic, English',
    pill: 'Speak',
    caption: 'Arabic · English',
    render: () => <SpeakScene />,
  },
  {
    id: 'trust',
    label: 'Trust — nothing leaves the box',
    pill: 'Trust',
    caption: 'Nothing leaves the box',
    render: () => <TrustScene />,
  },
] as const;

const SCENE_INTERVAL = 5000;

export function Hero() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    // Don't auto-advance if user prefers reduced motion
    if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    const timer = setInterval(() => {
      setActive((v) => (v + 1) % SCENES.length);
    }, SCENE_INTERVAL);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="relative pt-32 pb-24 lg:pt-40 lg:pb-32 overflow-hidden bg-[#202020] text-[#E7E6E4]">
      {/* Soft radial tan glow top-left */}
      <div
        aria-hidden
        className="absolute pointer-events-none"
        style={{
          width: 720,
          height: 720,
          top: -260,
          left: -200,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(181,152,118,0.20) 0%, rgba(181,152,118,0) 65%)',
          filter: 'blur(8px)',
        }}
      />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-10 grid lg:grid-cols-12 gap-10 lg:gap-16 items-center">
        {/* LEFT — Headline + subline + chips + CTAs */}
        <div className="lg:col-span-6 lg:pr-4">
          {/* Top eyebrow */}
          <div className="text-[12px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-4 lg:mb-6">
            Content-Aware Intelligence
          </div>

          {/* Hero headline */}
          <h1 className="font-bold tracking-tight text-[#E7E6E4] leading-[1.08]"
              style={{ fontSize: 'clamp(30px, 3.8vw, 54px)', letterSpacing: '-0.022em', maxWidth: '600px' }}>
            Your documents finally{' '}
            <span className="text-[#B59876]">answer back</span>
            <span className="text-[#B93C32]" style={{ fontSize: '1.1em' }}>.</span>
          </h1>

          {/* Hero subline */}
          <p className="mt-6 text-[17px] lg:text-[19px] leading-[1.55] text-[#E7E6E4]/75 max-w-[640px]">
            Seekra is content-aware intelligence that runs on your infrastructure. Ask, see, and speak to your archive — every answer cited to its source.
          </p>

          {/* Name meaning callout */}
          <div className="mt-5 inline-flex items-center gap-3 px-4 py-2.5 rounded-lg bg-[#B59876]/10 border border-[#B59876]/30 border-l-[3px] border-l-[#B59876]">
            <span className="text-[11px] font-bold tracking-[0.22em] uppercase text-[#B59876]">
              The name
            </span>
            <span className="text-[16px] lg:text-[17px] font-medium text-[#E7E6E4]">
              <span className="font-bold text-[#B59876]">Seek</span>
              <span className="text-[#B93C32] font-bold mx-1">+</span>
              <span className="font-bold text-[#B59876]">era</span>
              <span className="text-[#E7E6E4]/80 ml-2">— a new era of seeking.</span>
            </span>
          </div>

          {/* Floating glass chips */}
          <div className="mt-7 flex flex-wrap gap-2.5">
            {[
              { icon: '✓', text: 'Cited answers' },
              { text: 'العربية · English', arabic: true },
              { icon: '▣', text: '100% visual match' },
              { icon: '⛨', text: 'Air-gapped ready' },
            ].map((chip, i) => (
              <span
                key={i}
                className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[13px] font-medium bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15 text-[#E7E6E4] ${
                  chip.arabic ? 'font-arabic' : ''
                }`}
              >
                {chip.icon && <span className="text-[#B59876]">{chip.icon}</span>}
                {chip.text}
              </span>
            ))}
          </div>

          {/* CTA row */}
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <a
              href="#contact"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-semibold bg-[#B59876] text-[#202020] hover:bg-[#C9B498] transition-colors shadow-lg shadow-[#B59876]/20"
            >
              Book a Demo
              <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
            </a>
            <a
              href="#capabilities"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-medium text-[#E7E6E4] border border-[#E7E6E4]/30 hover:border-[#B59876]/60 hover:text-[#B59876] transition-all"
            >
              See how it works
              <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* RIGHT — Browser frame with crossfading slideshow */}
        <div className="lg:col-span-6 relative">
          <BrowserFrame url="app.seekra.pk">
            <div className="relative w-full h-[340px] sm:h-[400px] lg:h-[440px] overflow-hidden rounded-b-[10px] bg-[#F5F4F2]">
              {SCENES.map((scene, i) => (
                <div
                  key={scene.id}
                  className="absolute inset-0 transition-opacity duration-700 ease-out"
                  style={{ opacity: active === i ? 1 : 0 }}
                  aria-hidden={active !== i}
                >
                  {/* Ken Burns subtle zoom on active scene */}
                  <div
                    className="w-full h-full"
                    style={{
                      transform: active === i ? 'scale(1.04)' : 'scale(1)',
                      transition: `transform ${SCENE_INTERVAL}ms ease-out`,
                    }}
                  >
                    {scene.render()}
                  </div>
                </div>
              ))}
            </div>
          </BrowserFrame>

          {/* Caption pill — cycles with the scene */}
          <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-[#202020] border border-[#B59876]/40 text-[12px] font-medium text-[#B59876] whitespace-nowrap shadow-lg">
            {SCENES[active].caption}
          </div>

          {/* Progress dots — clickable */}
          <div className="mt-6 flex justify-center gap-2">
            {SCENES.map((scene, i) => (
              <button
                key={scene.id}
                onClick={() => setActive(i)}
                aria-label={`Show ${scene.label}`}
                className={`h-2 rounded-full transition-all duration-300 ${
                  active === i ? 'w-8 bg-[#B59876]' : 'w-2 bg-[#E7E6E4]/30 hover:bg-[#E7E6E4]/50'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────
   Browser frame wrapper
   ───────────────────────────────────────────────────────────── */
function BrowserFrame({ url, children }: { url: string; children: React.ReactNode }) {
  return (
    <div className="relative bg-white border border-[#E7E6E4]/30 rounded-[14px] shadow-2xl shadow-[#B59876]/15 overflow-hidden">
      {/* Browser chrome */}
      <div className="h-9 bg-[#F5F4F2] border-b border-black/[0.06] flex items-center px-4 relative">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#B93C32]" />
          <span className="w-2 h-2 rounded-full bg-[#B59876]" />
          <span className="w-2 h-2 rounded-full bg-[#202020]" />
        </div>
        <div className="absolute left-1/2 -translate-x-1/2 px-3.5 py-1 bg-white border border-black/10 rounded text-[11px] font-mono text-[#4A3F33]">
          {url}
        </div>
      </div>
      {children}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Scene 1 — Ask (chat with citations)
   ───────────────────────────────────────────────────────────── */
function AskScene() {
  return (
    <div className="p-5 lg:p-6 h-full overflow-hidden bg-[#F5F4F2]">
      <div className="flex justify-end mb-3">
        <div className="max-w-[80%] bg-[#202020] text-[#E7E6E4] px-3 py-2 rounded-[10px] text-[12px] leading-snug">
          What does our policy say about data retention for customer records?
        </div>
      </div>
      <div className="max-w-[92%]">
        <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#B59876] mb-1">
          Seekra
        </div>
        <div className="text-[12px] leading-[1.55] text-[#1F1A14]">
          Customer records must be retained for seven years from the date of account closure, after which they are securely destroyed [1]. Records flagged as part of an active investigation are exempt and held until legal release [2].
        </div>
        <div className="mt-2.5 flex flex-wrap gap-1.5">
          <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#B59876]/15 border border-[#B59876]/30 text-[#1F1A14]">
            [1] Customer Data Policy v3 · p.14
          </span>
          <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#B59876]/15 border border-[#B59876]/30 text-[#1F1A14]">
            [2] Legal Hold Procedure · p.3
          </span>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Scene 2 — See (visual search results)
   ───────────────────────────────────────────────────────────── */
function SeeScene() {
  const results = [
    { match: 92 },
    { match: 86 },
    { match: 78 },
  ];
  return (
    <div className="p-5 lg:p-6 h-full overflow-hidden bg-[#F5F4F2]">
      <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#4A3F33]">
        Visual Search
      </div>
      <div className="mt-2 w-full h-[100px] border-2 border-dashed border-[#B59876]/50 rounded-[10px] flex flex-col items-center justify-center gap-1.5 bg-[#B59876]/[0.04]">
        <div className="text-[#B59876] text-[24px]">↑</div>
        <div className="text-[11px] font-medium text-[#4A3F33]">Upload a photo or scan</div>
      </div>
      <div className="mt-3.5 text-[10px] font-bold tracking-[0.18em] uppercase text-[#4A3F33]">
        Similar Results
      </div>
      <div className="mt-1.5 grid grid-cols-3 gap-2">
        {results.map((r, i) => (
          <div key={i} className="bg-[#EAE8E5] border border-black/[0.08] rounded-[8px] overflow-hidden">
            <div
              className="h-[55px] flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, rgba(181,152,118,0.30), rgba(181,152,118,0.10))',
              }}
            >
              <span className="text-[#B59876] text-[18px]">▣</span>
            </div>
            <div className="p-1.5">
              <div className="h-1 bg-black/[0.08] rounded overflow-hidden">
                <div
                  className="h-full bg-[#B59876]"
                  style={{ width: `${r.match}%` }}
                />
              </div>
              <div className="mt-1 text-[9px] font-mono font-medium text-[#4A3F33]">{r.match}% match</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2.5 text-[10px] italic text-[#4A3F33]">
        Detected: site inspection · equipment · safety helmets
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Scene 3 — Speak (Arabic + English voice)
   ───────────────────────────────────────────────────────────── */
function SpeakScene() {
  return (
    <div className="p-6 h-full flex flex-col items-center justify-center gap-5 bg-[#F5F4F2]">
      <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-[#B59876]/15 border border-[#B59876]/40 text-[18px] font-medium text-[#202020]">
        <span className="font-arabic text-[#202020]">العربية</span>
        <span className="text-[#B59876]">·</span>
        <span>English</span>
      </div>
      <div className="flex items-center gap-4 text-[#B59876]">
        <span className="text-[28px]">◖</span>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#B59876] animate-pulse" />
          <span className="w-1.5 h-1.5 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.2s' }} />
          <span className="w-1.5 h-1.5 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.4s' }} />
          <span className="w-1.5 h-1.5 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.6s' }} />
        </div>
        <span className="text-[28px]">⇄</span>
      </div>
      <div className="text-center max-w-[280px]">
        <div className="text-[14px] font-semibold text-[#202020]">
          Speech-to-text in, spoken answers out
        </div>
        <div className="mt-1 text-[12px] text-[#4A3F33] leading-snug">
          Arabic as a first-class citizen — proper RTL rendering and Arabic-capable fonts.
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Scene 4 — Trust (security visualization)
   ───────────────────────────────────────────────────────────── */
function TrustScene() {
  const items = [
    { icon: '▦', label: 'Self-hosted' },
    { icon: '⊘', label: 'PII masked' },
    { icon: '⛨', label: 'Air-gapped' },
    { icon: '✓', label: 'Audit trail' },
  ];
  return (
    <div className="p-6 h-full flex flex-col items-center justify-center gap-5 bg-[#202020]">
      <div className="text-center">
        <div className="text-[10px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-2">
          Trust · Security &amp; Sovereignty
        </div>
        <div className="text-[24px] font-bold text-[#E7E6E4] leading-tight tracking-tight">
          Nothing leaves the box<span className="text-[#B93C32]">.</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 max-w-[300px]">
        {items.map((item, i) => (
          <div
            key={i}
            className="flex items-center gap-2.5 px-3 py-2 rounded-[8px] bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15"
          >
            <span className="text-[#B59876] text-[18px]">{item.icon}</span>
            <span className="text-[12px] font-medium text-[#E7E6E4]">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
