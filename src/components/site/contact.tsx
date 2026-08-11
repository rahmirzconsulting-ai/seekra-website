'use client';

import { useState, type FormEvent } from 'react';
import { Mail, ArrowRight, Send, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Reveal } from './reveal';
import { SITE_CONFIG } from '@/lib/site-config';

type Status = 'idle' | 'sending' | 'sent' | 'error';

export function Contact() {
  const [status, setStatus] = useState<Status>('idle');
  const [errorMsg, setErrorMsg] = useState<string>('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus('sending');
    setErrorMsg('');

    const form = e.currentTarget;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const response = await fetch(SITE_CONFIG.formSubmitEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setStatus('sent');
        form.reset();
        // Reset status after 8 seconds so the form can be reused
        setTimeout(() => setStatus('idle'), 8000);
      } else {
        throw new Error(`Submission failed with status ${response.status}`);
      }
    } catch (err) {
      // Fallback to mailto: so the lead is never lost
      setStatus('error');
      const subject = encodeURIComponent(`Demo request — ${payload.organization || 'New lead'}`);
      const body = encodeURIComponent(
        `Name: ${payload.name}\nOrganization: ${payload.organization}\nEmail: ${payload.email}\n\n${payload.message}`
      );
      setErrorMsg(`Couldn't submit online. Click here to send via email instead:`);
      // Build the mailto link in the DOM
      window.location.href = `mailto:${SITE_CONFIG.contactEmail}?subject=${subject}&body=${body}`;
    }
  };

  return (
    <section id="contact" className="relative py-24 lg:py-32 bg-[#202020] text-[#E7E6E4] overflow-hidden">
      {/* Central radial glow */}
      <div
        aria-hidden
        className="absolute pointer-events-none"
        style={{
          width: 900,
          height: 900,
          top: -200,
          left: '50%',
          transform: 'translateX(-50%)',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(181,152,118,0.22) 0%, rgba(181,152,118,0) 65%)',
          filter: 'blur(8px)',
        }}
      />

      <div className="relative mx-auto max-w-5xl px-6 lg:px-10 text-center">
        <Reveal>
          <div className="text-[13px] font-bold tracking-[0.22em] uppercase text-[#B59876] mb-4">
            See Seekra on your own documents
          </div>
          <h2 className="font-bold tracking-tight text-[#E7E6E4]"
              style={{ fontSize: 'clamp(36px, 5.5vw, 68px)', lineHeight: 1.05, letterSpacing: '-0.03em' }}>
            Tell us about your archive<span className="text-[#B93C32]" style={{ fontSize: '1.1em' }}>.</span>
          </h2>
          <p className="mx-auto mt-6 text-[18px] leading-[1.6] text-[#E7E6E4]/78 max-w-[760px]">
            Arrange a live demo on a sample of your own documents. We will walk your team through Ask, See, Speak, and Trust — and answer every question about deployment, security, and integration.
          </p>
        </Reveal>

        <Reveal delay={150}>
          <div className="mt-10 grid md:grid-cols-5 gap-8 items-start text-left">
            {/* Form */}
            <form onSubmit={handleSubmit} className="md:col-span-3 space-y-4" noValidate>
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="name" className="block text-[11px] font-semibold tracking-[0.18em] uppercase text-[#E7E6E4]/60 mb-1.5">
                    Name <span className="text-[#B93C32]">*</span>
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    autoComplete="name"
                    className="w-full px-4 py-3 rounded-[10px] bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15 text-[#E7E6E4] placeholder:text-[#E7E6E4]/40 focus:outline-none focus:border-[#B59876] focus:bg-[#E7E6E4]/[0.10] transition-colors text-[14px]"
                    placeholder="Your full name"
                  />
                </div>
                <div>
                  <label htmlFor="organization" className="block text-[11px] font-semibold tracking-[0.18em] uppercase text-[#E7E6E4]/60 mb-1.5">
                    Organization
                  </label>
                  <input
                    id="organization"
                    name="organization"
                    type="text"
                    autoComplete="organization"
                    className="w-full px-4 py-3 rounded-[10px] bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15 text-[#E7E6E4] placeholder:text-[#E7E6E4]/40 focus:outline-none focus:border-[#B59876] focus:bg-[#E7E6E4]/[0.10] transition-colors text-[14px]"
                    placeholder="Your company"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="email" className="block text-[11px] font-semibold tracking-[0.18em] uppercase text-[#E7E6E4]/60 mb-1.5">
                  Email <span className="text-[#B93C32]">*</span>
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  className="w-full px-4 py-3 rounded-[10px] bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15 text-[#E7E6E4] placeholder:text-[#E7E6E4]/40 focus:outline-none focus:border-[#B59876] focus:bg-[#E7E6E4]/[0.10] transition-colors text-[14px]"
                  placeholder="you@organization.com"
                />
              </div>
              <div>
                <label htmlFor="message" className="block text-[11px] font-semibold tracking-[0.18em] uppercase text-[#E7E6E4]/60 mb-1.5">
                  Message
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={4}
                  className="w-full px-4 py-3 rounded-[10px] bg-[#E7E6E4]/[0.06] border border-[#E7E6E4]/15 text-[#E7E6E4] placeholder:text-[#E7E6E4]/40 focus:outline-none focus:border-[#B59876] focus:bg-[#E7E6E4]/[0.10] transition-colors text-[14px] resize-none"
                  placeholder="Tell us about your archive — document types, languages, scale, and the use case you're targeting."
                />
              </div>

              {/* Honeypot — bot trap (FormSubmit best practice) */}
              <input type="text" name="_honey" style={{ display: 'none' }} tabIndex={-1} autoComplete="off" />

              <button
                type="submit"
                disabled={status === 'sending' || status === 'sent'}
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[15px] font-semibold bg-[#B59876] text-[#202020] hover:bg-[#C9B498] transition-colors disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-[#B59876]/20"
              >
                {status === 'sending' && <Loader2 className="w-4 h-4 animate-spin" />}
                {status === 'sent' && <CheckCircle2 className="w-4 h-4" />}
                {status === 'idle' && <Send className="w-4 h-4" />}
                {status === 'error' && <AlertCircle className="w-4 h-4" />}
                {status === 'sending' && 'Sending…'}
                {status === 'sent' && 'Sent — we\'ll be in touch'}
                {status === 'error' && 'Try email instead'}
                {status === 'idle' && 'Send message'}
                {(status === 'idle' || status === 'sent') && <ArrowRight className="w-4 h-4" strokeWidth={2.5} />}
              </button>

              {status === 'sent' && (
                <p className="text-[13px] text-[#B59876] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  Thank you — we&rsquo;ll respond within 24 hours.
                </p>
              )}
              {status === 'error' && (
                <p className="text-[13px] text-[#B93C32]">
                  We couldn&rsquo;t submit online — your email client should now open with the message pre-filled. If not, email us directly at <a href={`mailto:${SITE_CONFIG.contactEmail}`} className="underline">{SITE_CONFIG.contactEmail}</a>.
                </p>
              )}
            </form>

            {/* Email display block */}
            <div className="md:col-span-2 space-y-6 md:pt-2">
              <div>
                <div className="text-[11px] font-semibold tracking-[0.18em] uppercase text-[#B59876] mb-2">
                  Direct contact
                </div>
                <a
                  href={`mailto:${SITE_CONFIG.contactEmail}`}
                  className="inline-flex items-center gap-3 text-[#E7E6E4] hover:text-[#B59876] transition-colors group"
                >
                  <Mail className="w-5 h-5 text-[#B59876] flex-shrink-0" />
                  <span className="text-[15px] font-medium break-all">{SITE_CONFIG.contactEmail}</span>
                </a>
              </div>
              <div>
                <div className="text-[11px] font-semibold tracking-[0.18em] uppercase text-[#B59876] mb-2">
                  Live app demo
                </div>
                <a
                  href={SITE_CONFIG.appBridgeUrl}
                  className="inline-flex items-center gap-3 text-[#E7E6E4] hover:text-[#B59876] transition-colors group"
                >
                  <ArrowRight className="w-5 h-5 text-[#B59876] flex-shrink-0" />
                  <span className="text-[15px] font-medium">Launch live demo</span>
                </a>
              </div>
              <div className="text-[12px] text-[#E7E6E4]/55 leading-[1.5]">
                Tell us about your archive and we&rsquo;ll arrange a live demo on a sample of your own documents.
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
