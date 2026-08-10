'use client';

import { useEffect, useState } from 'react';
import { Menu, X, ArrowRight } from 'lucide-react';
import { SITE_CONFIG } from '@/lib/site-config';

const NAV_LINKS = [
  { href: '#capabilities', label: 'Capabilities' },
  { href: '#security', label: 'Security' },
  { href: '#comparison', label: 'Comparison' },
  { href: '#deployment', label: 'Deployment' },
  { href: '#contact', label: 'Contact' },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'backdrop-blur-md bg-[#202020]/85 border-b border-white/10'
          : 'bg-transparent'
      }`}
    >
      <nav className="mx-auto max-w-7xl px-6 lg:px-10 h-16 lg:h-20 flex items-center justify-between">
        {/* Logo lockup */}
        <a href="#" className="flex items-center gap-3 group" aria-label="Seekra home">
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

        {/* Desktop nav links */}
        <ul className="hidden lg:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium text-[#E7E6E4]/80 hover:text-[#B59876] transition-colors tracking-tight"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Desktop CTA buttons */}
        <div className="hidden lg:flex items-center gap-3">
          <a
            href={SITE_CONFIG.appUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium text-[#E7E6E4] border border-[#E7E6E4]/30 hover:border-[#B59876]/60 hover:text-[#B59876] transition-all"
          >
            Launch App
          </a>
          <a
            href="#contact"
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold bg-[#B59876] text-[#202020] hover:bg-[#C9B498] transition-colors"
          >
            Book a Demo
            <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
          </a>
        </div>

        {/* Mobile menu button */}
        <button
          className="lg:hidden text-[#E7E6E4] p-2 -mr-2"
          aria-label="Open menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
        >
          {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile drawer */}
      {menuOpen && (
        <div className="lg:hidden bg-[#202020]/95 backdrop-blur-md border-t border-white/10">
          <ul className="px-6 py-4 space-y-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="block py-3 text-base text-[#E7E6E4]/90 hover:text-[#B59876] transition-colors"
                  onClick={() => setMenuOpen(false)}
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li className="pt-3 space-y-2">
              <a
                href={SITE_CONFIG.appUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center py-3 rounded-full text-sm font-medium text-[#E7E6E4] border border-[#E7E6E4]/30"
                onClick={() => setMenuOpen(false)}
              >
                Launch App
              </a>
              <a
                href="#contact"
                className="block w-full text-center py-3 rounded-full text-sm font-semibold bg-[#B59876] text-[#202020]"
                onClick={() => setMenuOpen(false)}
              >
                Book a Demo
              </a>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
}
