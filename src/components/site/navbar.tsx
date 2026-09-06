'use client';

import { useEffect, useState, useRef } from 'react';
import { Menu, X, ArrowRight, ChevronDown } from 'lucide-react';
import { SITE_CONFIG } from '@/lib/site-config';

// Grouped nav structure: 4 top-level groups + Contact
// - Platform → Capabilities + Intelligence (what Seekra does)
// - Trust    → Access Control + Governance (how Seekra protects)
// - Connect  → Connectors + Deployment (how Seekra fits in)
// - Compare  → Comparison (how Seekra stacks up)
type NavGroup = {
  id: string;
  label: string;
  items: { href: string; label: string; desc: string }[];
};

const NAV_GROUPS: NavGroup[] = [
  {
    id: 'platform',
    label: 'Platform',
    items: [
      { href: '#capabilities', label: 'Capabilities', desc: 'Ask, see, speak — in Arabic and English' },
      { href: '#intelligence', label: 'Intelligence', desc: 'Three answer modes + entity knowledge graph' },
    ],
  },
  {
    id: 'trust',
    label: 'Trust',
    items: [
      { href: '#access-control', label: 'Access Control', desc: 'Org-tree scoping + 4-level classification' },
      { href: '#governance', label: 'Governance', desc: 'Audit trail · PII lineage · provenance' },
    ],
  },
  {
    id: 'connect',
    label: 'Connect',
    items: [
      { href: '#connectors', label: 'Connectors', desc: '9 data sources · auto-ingest' },
      { href: '#deployment', label: 'Deployment', desc: 'Cloud · self-hosted · air-gapped' },
    ],
  },
  {
    id: 'compare',
    label: 'Compare',
    items: [
      { href: '#comparison', label: 'Comparison', desc: 'Seekra vs cloud AI vs legacy search' },
    ],
  },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleGroupEnter = (id: string) => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setOpenGroup(id);
  };

  const handleGroupLeave = () => {
    closeTimer.current = setTimeout(() => setOpenGroup(null), 150);
  };

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

        {/* Desktop nav — grouped dropdowns */}
        <ul className="hidden lg:flex items-center gap-1">
          {NAV_GROUPS.map((group) => (
            <li
              key={group.id}
              className="relative"
              onMouseEnter={() => handleGroupEnter(group.id)}
              onMouseLeave={handleGroupLeave}
            >
              <button
                onClick={() =>
                  setOpenGroup((cur) => (cur === group.id ? null : group.id))
                }
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-full text-sm font-medium transition-all tracking-tight ${
                  openGroup === group.id
                    ? 'text-[#B59876] bg-[#E7E6E4]/[0.06]'
                    : 'text-[#E7E6E4]/80 hover:text-[#B59876]'
                }`}
                aria-expanded={openGroup === group.id}
              >
                {group.label}
                <ChevronDown
                  className={`w-3.5 h-3.5 transition-transform duration-200 ${
                    openGroup === group.id ? 'rotate-180' : ''
                  }`}
                  strokeWidth={2.5}
                />
              </button>

              {/* Dropdown panel */}
              {openGroup === group.id && (
                <div
                  className="absolute top-full left-0 mt-1 pt-1"
                  onMouseEnter={() => handleGroupEnter(group.id)}
                  onMouseLeave={handleGroupLeave}
                >
                  <div className="min-w-[260px] bg-[#202020] border border-[#E7E6E4]/12 rounded-[12px] shadow-2xl shadow-black/40 overflow-hidden">
                    {group.items.map((item) => (
                      <a
                        key={item.href}
                        href={item.href}
                        onClick={() => setOpenGroup(null)}
                        className="block px-4 py-3 hover:bg-[#E7E6E4]/[0.06] transition-colors border-b border-[#E7E6E4]/[0.06] last:border-b-0"
                      >
                        <div className="text-[14px] font-semibold text-[#E7E6E4] tracking-tight">
                          {item.label}
                        </div>
                        <div className="text-[11px] text-[#E7E6E4]/55 mt-0.5 leading-snug">
                          {item.desc}
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </li>
          ))}
          <li>
            <a
              href="#contact"
              className="px-3.5 py-2 text-sm font-medium text-[#E7E6E4]/80 hover:text-[#B59876] transition-colors tracking-tight"
            >
              Contact
            </a>
          </li>
        </ul>

        {/* Desktop CTA buttons */}
        <div className="hidden lg:flex items-center gap-3">
          <a
            href={SITE_CONFIG.appBridgeUrl}
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

      {/* Mobile drawer — expanded with groups + descriptions */}
      {menuOpen && (
        <div className="lg:hidden bg-[#202020]/97 backdrop-blur-md border-t border-white/10 max-h-[80vh] overflow-y-auto">
          <div className="px-6 py-5 space-y-5">
            {NAV_GROUPS.map((group) => (
              <div key={group.id}>
                <div className="text-[11px] font-bold tracking-[0.18em] uppercase text-[#B59876] mb-2 px-1">
                  {group.label}
                </div>
                <div className="space-y-1">
                  {group.items.map((item) => (
                    <a
                      key={item.href}
                      href={item.href}
                      className="block px-3 py-2.5 rounded-[10px] hover:bg-[#E7E6E4]/[0.06] transition-colors"
                      onClick={() => setMenuOpen(false)}
                    >
                      <div className="text-[15px] font-medium text-[#E7E6E4]/95 tracking-tight">
                        {item.label}
                      </div>
                      <div className="text-[12px] text-[#E7E6E4]/55 mt-0.5 leading-snug">
                        {item.desc}
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            ))}
            <div className="pt-2 border-t border-white/10">
              <a
                href="#contact"
                className="block px-3 py-2.5 text-[15px] font-medium text-[#E7E6E4]/95 hover:text-[#B59876] transition-colors"
                onClick={() => setMenuOpen(false)}
              >
                Contact
              </a>
            </div>
            <div className="pt-2 space-y-2">
              <a
                href={SITE_CONFIG.appBridgeUrl}
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
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
