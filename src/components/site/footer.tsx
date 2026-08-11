import { SITE_CONFIG } from '@/lib/site-config';

export function Footer() {
  return (
    <footer className="bg-[#1A1A1A] text-[#E7E6E4] py-10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          {/* Logo + tagline */}
          <div className="flex items-center gap-3">
            <img
              src="/logo-seekra.png"
              alt="Seekra logo"
              width={32}
              height={32}
              className="rounded-md"
              style={{ width: 32, height: 32 }}
            />
            <div>
              <div className="text-[15px] font-semibold tracking-tight">Seekra</div>
              <div className="text-[11px] text-[#E7E6E4]/55 leading-tight">
                Content-aware intelligence for the enterprise
              </div>
            </div>
          </div>

          {/* Anchor links */}
          <nav className="flex flex-wrap items-center gap-x-6 gap-y-2 text-[13px]">
            <a href="#capabilities" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Capabilities</a>
            <a href="#security" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Security</a>
            <a href="#comparison" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Comparison</a>
            <a href="#deployment" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Deployment</a>
            <a href="#contact" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Contact</a>
            <a
              href={SITE_CONFIG.appBridgeUrl}
              className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors"
            >
              Launch App
            </a>
          </nav>

          {/* Email + copyright */}
          <div className="text-right text-[12px] text-[#E7E6E4]/55 leading-relaxed">
            <a
              href={`mailto:${SITE_CONFIG.contactEmail}`}
              className="hover:text-[#B59876] transition-colors block"
            >
              {SITE_CONFIG.contactEmail}
            </a>
            <div className="mt-1">© {SITE_CONFIG.year} Seekra · seekra.pk</div>
          </div>
        </div>
      </div>
    </footer>
  );
}
