'use client';

import { useEffect, useState } from 'react';
import { ArrowRight, Mail, Loader2, CheckCircle2, AlertCircle, RotateCw } from 'lucide-react';
import { SITE_CONFIG } from '@/lib/site-config';

type Status = 'checking' | 'live' | 'offline';

const HEALTH_TIMEOUT_MS = 3500; // 3.5s — generous enough for slow networks, short enough to feel snappy
const REDIRECT_DELAY_MS = 1200; // brief "Redirecting…" beat before sending them to the app

export default function AppBridgePage() {
  const [status, setStatus] = useState<Status>('checking');

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);

    // Hit the EC2 health endpoint. If it returns 200, the app is live and we redirect.
    // If it times out, errors, or returns non-200, the app is offline → show "book a demo" UI.
    fetch(`${SITE_CONFIG.appInternalUrl}/api/health`, {
      method: 'GET',
      mode: 'cors',
      signal: controller.signal,
      cache: 'no-store',
    })
      .then((res) => {
        if (res.ok) {
          if (!cancelled) setStatus('live');
        } else {
          if (!cancelled) setStatus('offline');
        }
      })
      .catch(() => {
        if (!cancelled) setStatus('offline');
      })
      .finally(() => {
        clearTimeout(timeout);
      });

    return () => {
      cancelled = true;
      clearTimeout(timeout);
      controller.abort();
    };
  }, []);

  // When status flips to 'live', wait briefly then redirect to the actual app
  useEffect(() => {
    if (status !== 'live') return;
    const redirectTimer = setTimeout(() => {
      window.location.href = SITE_CONFIG.appInternalUrl;
    }, REDIRECT_DELAY_MS);
    return () => clearTimeout(redirectTimer);
  }, [status]);

  return (
    <div className="min-h-screen flex flex-col bg-[#202020] text-[#E7E6E4]">
      {/* Subtle radial tan glow top-right — matches the main site's hero */}
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

      {/* Top brand bar — Seekra logo + wordmark, clickable back to home */}
      <header className="relative z-10 border-b border-[#E7E6E4]/10">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 h-16 lg:h-20 flex items-center justify-between">
          <a href="/" className="flex items-center gap-3 group" aria-label="Back to Seekra home">
            <img
              src="/logo-seekra.png"
              alt="Seekra logo"
              width={36}
              height={36}
              className="rounded-lg"
              style={{ width: 36, height: 36 }}
            />
            <span className="font-semibold text-[20px] tracking-tight text-[#E7E6E4] group-hover:text-white transition-colors">
              Seekra
            </span>
          </a>
          <a
            href="/"
            className="text-sm font-medium text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors"
          >
            Back to website →
          </a>
        </div>
      </header>

      {/* Center content */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-6 lg:px-10 py-16">
        <div className="max-w-2xl w-full text-center">

          {/* CHECKING state — initial loading */}
          {status === 'checking' && (
            <CheckingState />
          )}

          {/* LIVE state — redirecting */}
          {status === 'live' && (
            <LiveState appUrl={SITE_CONFIG.appInternalUrl} />
          )}

          {/* OFFLINE state — book a demo */}
          {status === 'offline' && (
            <OfflineState />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#E7E6E4]/10 py-6">
        <div className="mx-auto max-w-7xl px-6 lg:px-10 text-center text-[12px] text-[#E7E6E4]/50 tracking-[0.10em] uppercase">
          © {SITE_CONFIG.year} Seekra · seekra.pk
        </div>
      </footer>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   CHECKING — initial loading state
   ───────────────────────────────────────────────────────────── */
function CheckingState() {
  return (
    <div className="animate-fade-in">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[#B59876]/10 border border-[#B59876]/30 mb-8">
        <Loader2 className="w-9 h-9 text-[#B59876] animate-spin" strokeWidth={1.5} />
      </div>
      <div className="text-[12px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-4">
        Checking
      </div>
      <h1 className="font-bold tracking-tight text-[#E7E6E4] mb-4"
          style={{ fontSize: 'clamp(28px, 4.5vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.025em' }}>
        Checking Seekra app status<span className="text-[#B93C32]">…</span>
      </h1>
      <p className="text-[16px] leading-[1.55] text-[#E7E6E4]/65 max-w-[480px] mx-auto">
        Verifying the demo server is online. This usually takes 1–2 seconds.
      </p>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   LIVE — redirecting to the actual app
   ───────────────────────────────────────────────────────────── */
function LiveState({ appUrl }: { appUrl: string }) {
  return (
    <div className="animate-fade-in">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[#B59876]/15 border border-[#B59876]/40 mb-8">
        <CheckCircle2 className="w-10 h-10 text-[#B59876]" strokeWidth={1.5} />
      </div>
      <div className="text-[12px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-4">
        Online
      </div>
      <h1 className="font-bold tracking-tight text-[#E7E6E4] mb-4"
          style={{ fontSize: 'clamp(28px, 4.5vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.025em' }}>
        Seekra app is live<span className="text-[#B59876]">.</span>
      </h1>
      <p className="text-[16px] leading-[1.6] text-[#E7E6E4]/75 max-w-[520px] mx-auto mb-8">
        Redirecting you to the live demo now. If you are not redirected automatically in a moment, click the button below.
      </p>
      <a
        href={appUrl}
        className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-semibold bg-[#B59876] text-[#202020] hover:bg-[#C9B498] transition-colors shadow-lg shadow-[#B59876]/20"
      >
        <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
        Open the app
      </a>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   OFFLINE — branded "book a demo" message
   ───────────────────────────────────────────────────────────── */
function OfflineState() {
  return (
    <div className="animate-fade-in">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[#B93C32]/10 border border-[#B93C32]/40 mb-8">
        <AlertCircle className="w-10 h-10 text-[#B93C32]" strokeWidth={1.5} />
      </div>
      <div className="text-[12px] font-bold tracking-[0.22em] uppercase text-[#B93C32] mb-4">
        Offline
      </div>
      <h1 className="font-bold tracking-tight text-[#E7E6E4] mb-5"
          style={{ fontSize: 'clamp(28px, 4.5vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.025em' }}>
        The live demo server is currently offline<span className="text-[#B93C32]">.</span>
      </h1>
      <p className="text-[16px] lg:text-[17px] leading-[1.65] text-[#E7E6E4]/75 max-w-[560px] mx-auto mb-10">
        We spin the demo server up on demand for serious evaluations — it is not always running to conserve cloud costs. Book a demo and we&rsquo;ll have a live environment ready for you within 24 hours, with sample documents and a guided walkthrough of Ask, See, Speak, and Trust.
      </p>

      <div className="flex flex-wrap items-center justify-center gap-4">
        <a
          href="/#contact"
          className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-semibold bg-[#B59876] text-[#202020] hover:bg-[#C9B498] transition-colors shadow-lg shadow-[#B59876]/20"
        >
          Book a Demo
          <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
        </a>
        <a
          href={`mailto:${SITE_CONFIG.contactEmail}?subject=${encodeURIComponent('Demo request — saw app offline message')}`}
          className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-medium text-[#E7E6E4] border border-[#E7E6E4]/30 hover:border-[#B59876]/60 hover:text-[#B59876] transition-all"
        >
          <Mail className="w-4 h-4" />
          Email us
        </a>
      </div>

      {/* Retry option — in case the user thinks this was a false negative */}
      <div className="mt-12 pt-8 border-t border-[#E7E6E4]/10">
        <p className="text-[13px] text-[#E7E6E4]/55 mb-3">
          Think this is a mistake? Try again:
        </p>
        <button
          onClick={() => window.location.reload()}
          className="inline-flex items-center gap-2 text-[13px] font-medium text-[#B59876] hover:text-[#C9B498] transition-colors"
        >
          <RotateCw className="w-3.5 h-3.5" />
          Retry connection
        </button>
      </div>
    </div>
  );
}
