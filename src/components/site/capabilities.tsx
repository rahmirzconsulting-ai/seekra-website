import { CheckCircle2, MessageSquare, ScanSearch, Mic } from 'lucide-react';
import { Reveal } from './reveal';

const CAPABILITIES = [
  {
    id: 'ask',
    eyebrow: 'Capability 01 · Ask',
    title: 'Answers you can verify in one click',
    body: 'Staff type a question in plain language and Seekra responds with an answer drawn from the organization\u2019s own documents. Every claim in the response is marked with a numbered citation that links to the exact source document and page, opening instantly in the built-in viewer.',
    bullets: [
      'Natural-language questions — no query syntax to learn',
      'Numbered citations link to the exact source page',
      'Built-in viewer opens PDF, Word, Excel, and PowerPoint in the browser',
      'Critical for compliance-driven buyers who require verifiable AI',
    ],
    icon: MessageSquare,
    visual: <AskVisual />,
    reverse: false,
  },
  {
    id: 'see',
    eyebrow: 'Capability 02 · See',
    title: 'Search your archive with a photograph',
    body: 'Upload a photo, scanned image, or screenshot, and Seekra finds visually similar items across the entire archive using image similarity. Each result shows a similarity score and a label describing what the image most likely shows, plus the documents it relates to.',
    bullets: [
      'Field inspections, damage photos, site images — searchable without any text',
      'Image-to-image similarity with detected-content labels',
      'A differentiator almost no competitor offers',
      'Works for scans, photographs, screenshots, and document page images',
    ],
    icon: ScanSearch,
    visual: <SeeVisual />,
    reverse: true,
  },
  {
    id: 'speak',
    eyebrow: 'Capability 03 · Speak',
    title: 'Speak to your archive. In Arabic or English.',
    body: 'Seekra supports full voice interaction — speech in, spoken answers out. Arabic is a first-class citizen, with correct right-to-left rendering and Arabic-capable fonts. English sits alongside it with full parity, not as a translated afterthought.',
    bullets: [
      'Speech-to-text in, spoken answers out',
      'Arabic as a first-class citizen — proper RTL rendering',
      'English with full parity — not a translated afterthought',
      'Built for the Gulf market where this combination is rare',
    ],
    icon: Mic,
    visual: <SpeakVisual />,
    reverse: false,
  },
] as const;

export function Capabilities() {
  return (
    <section id="capabilities" className="bg-[#E7E6E4] text-[#1F1A14]">
      {CAPABILITIES.map((cap, i) => (
        <div
          key={cap.id}
          className={`py-20 lg:py-28 ${i % 2 === 1 ? 'bg-[#D8D6D3]/40' : ''}`}
        >
          <div className="mx-auto max-w-7xl px-6 lg:px-10">
            <div className="grid lg:grid-cols-12 gap-10 lg:gap-16 items-center">
              {/* Text column */}
              <Reveal className={`lg:col-span-6 ${cap.reverse ? 'lg:order-2' : ''}`}>
                <div className="text-[13px] font-bold tracking-[0.22em] uppercase text-[#1F1A14] mb-3">
                  {cap.eyebrow}
                </div>
                <h2 className="font-bold tracking-tight text-[#1F1A14] mb-5"
                    style={{ fontSize: 'clamp(28px, 3.8vw, 46px)', lineHeight: 1.12, letterSpacing: '-0.025em' }}>
                  {cap.title}<span className="text-[#B93C32]">.</span>
                </h2>
                <p className="text-[16px] leading-[1.65] text-[#4A3F33] max-w-[540px]">
                  {cap.body}
                </p>
                <ul className="mt-6 space-y-3">
                  {cap.bullets.map((b, j) => (
                    <li key={j} className="flex items-start gap-3">
                      <CheckCircle2 className="w-[18px] h-[18px] text-[#B59876] flex-shrink-0 mt-0.5" strokeWidth={2.5} />
                      <span className="text-[14px] font-medium text-[#1F1A14] leading-[1.5]">{b}</span>
                    </li>
                  ))}
                </ul>
              </Reveal>

              {/* Visual column */}
              <Reveal delay={150} className={`lg:col-span-6 ${cap.reverse ? 'lg:order-1' : ''}`}>
                <div className="relative">
                  {/* Soft glow behind the frame */}
                  <div
                    aria-hidden
                    className="absolute -inset-6 rounded-[24px]"
                    style={{
                      background: 'radial-gradient(circle at center, rgba(181,152,118,0.18) 0%, rgba(181,152,118,0) 65%)',
                    }}
                  />
                  <div className="relative">{cap.visual}</div>
                </div>
              </Reveal>
            </div>
          </div>
        </div>
      ))}
    </section>
  );
}

/* ─────────────────────────────────────────────────────────────
   Browser frame mockups (pure CSS — no images)
   ───────────────────────────────────────────────────────────── */
function BrowserFrameShell({ url, children }: { url: string; children: React.ReactNode }) {
  return (
    <div className="relative bg-white border border-black/[0.18] rounded-[12px] shadow-2xl shadow-[#B59876]/15 overflow-hidden">
      <div className="h-9 bg-[#F5F4F2] border-b border-black/[0.08] flex items-center px-4 relative">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#B93C32]" />
          <span className="w-2 h-2 rounded-full bg-[#B59876]" />
          <span className="w-2 h-2 rounded-full bg-[#202020]" />
        </div>
        <div className="absolute left-1/2 -translate-x-1/2 px-3.5 py-1 bg-white border border-black/10 rounded text-[11px] font-mono text-[#4A3F33]">
          {url}
        </div>
      </div>
      <div className="p-5 lg:p-6">{children}</div>
    </div>
  );
}

function AskVisual() {
  return (
    <BrowserFrameShell url="app.seekra.pk">
      <div className="space-y-4">
        {/* User message */}
        <div className="flex justify-end">
          <div className="max-w-[80%] bg-[#202020] text-[#E7E6E4] px-3.5 py-2.5 rounded-[10px] text-[13px] leading-snug">
            What does our policy say about data retention for customer records?
          </div>
        </div>
        {/* Seekra answer */}
        <div className="max-w-[92%]">
          <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#B59876] mb-1.5">
            Seekra
          </div>
          <div className="text-[13px] leading-[1.55] text-[#1F1A14]">
            Customer records must be retained for seven years from the date of account closure, after which they are securely destroyed [1]. Records flagged as part of an active investigation are exempt and held until legal release [2].
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <span className="inline-block px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#B59876]/15 border border-[#B59876]/30 text-[#1F1A14]">
              [1] Customer Data Policy v3 · p.14
            </span>
            <span className="inline-block px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#B59876]/15 border border-[#B59876]/30 text-[#1F1A14]">
              [2] Legal Hold Procedure · p.3
            </span>
          </div>
        </div>
      </div>
    </BrowserFrameShell>
  );
}

function SeeVisual() {
  const results = [
    { match: 92 },
    { match: 86 },
    { match: 78 },
  ];
  return (
    <BrowserFrameShell url="app.seekra.pk">
      <div className="text-[10px] font-bold tracking-[0.18em] uppercase text-[#4A3F33]">
        Visual Search
      </div>
      <div className="mt-2 w-full h-[110px] border-2 border-dashed border-[#B59876]/50 rounded-[10px] flex flex-col items-center justify-center gap-2 bg-[#B59876]/[0.04]">
        <ScanSearch className="w-7 h-7 text-[#B59876]" strokeWidth={1.5} />
        <div className="text-[12px] font-medium text-[#4A3F33]">Upload a photo or scan</div>
      </div>
      <div className="mt-4 text-[10px] font-bold tracking-[0.18em] uppercase text-[#4A3F33]">
        Similar Results
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2">
        {results.map((r, i) => (
          <div key={i} className="bg-[#EAE8E5] border border-black/[0.08] rounded-[8px] overflow-hidden">
            <div
              className="h-[55px] flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, rgba(181,152,118,0.30), rgba(181,152,118,0.10))',
              }}
            >
              <span className="text-[#B59876] text-[22px]">▣</span>
            </div>
            <div className="p-1.5">
              <div className="h-1 bg-black/[0.08] rounded overflow-hidden">
                <div className="h-full bg-[#B59876]" style={{ width: `${r.match}%` }} />
              </div>
              <div className="mt-1 text-[10px] font-mono font-medium text-[#4A3F33]">{r.match}% match</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 text-[11px] italic text-[#4A3F33]">
        Detected: site inspection · equipment · safety helmets
      </div>
    </BrowserFrameShell>
  );
}

function SpeakVisual() {
  return (
    <BrowserFrameShell url="app.seekra.pk">
      <div className="py-8 flex flex-col items-center justify-center gap-6">
        <div className="inline-flex items-center gap-4 px-5 py-3 rounded-full bg-[#B59876]/15 border border-[#B59876]/40 text-[20px] font-medium text-[#1F1A14]">
          <span className="font-arabic text-[#1F1A14]">العربية</span>
          <span className="text-[#B59876]">·</span>
          <span>English</span>
        </div>
        <div className="flex items-center gap-5 text-[#B59876]">
          <Mic className="w-8 h-8" strokeWidth={1.5} />
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#B59876] animate-pulse" />
            <span className="w-2 h-2 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.2s' }} />
            <span className="w-2 h-2 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.4s' }} />
            <span className="w-2 h-2 rounded-full bg-[#B59876] animate-pulse" style={{ animationDelay: '0.6s' }} />
          </div>
        </div>
        <div className="text-center max-w-[320px]">
          <div className="text-[15px] font-semibold text-[#1F1A14]">
            Speech-to-text in, spoken answers out
          </div>
          <div className="mt-1.5 text-[13px] text-[#4A3F33] leading-snug">
            Arabic as a first-class citizen — proper RTL rendering and Arabic-capable fonts.
          </div>
        </div>
      </div>
    </BrowserFrameShell>
  );
}
