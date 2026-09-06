import { SITE_CONFIG } from '@/lib/site-config';

export function Footer() {
  return (
    <footer className="bg-[#1A1A1A] text-[#E7E6E4] py-10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        {/* Release banner */}
        <div className="mb-8 p-4 rounded-[12px] bg-[#B59876]/[0.08] border border-[#B59876]/25 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#B59876] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#B59876]"></span>
            </span>
            <div>
              <div className="text-[13px] font-semibold text-[#B59876] tracking-tight">
                New: Data connectors + enterprise access control
              </div>
              <div className="text-[11px] text-[#E7E6E4]/65 mt-0.5">
                9 data source connectors · organization-tree scoping · 4-level classification · request a demo to see them live
              </div>
            </div>
          </div>
          <a
            href="/changelog"
            className="text-[12px] font-medium text-[#E7E6E4] border border-[#E7E6E4]/30 px-3.5 py-1.5 rounded-full hover:border-[#B59876]/60 hover:text-[#B59876] transition-colors flex-shrink-0"
          >
            View changelog →
          </a>
        </div>

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
            <a href="#access-control" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Access Control</a>
            <a href="#connectors" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Connectors</a>
            <a href="#intelligence" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Intelligence</a>
            <a href="#governance" className="text-[#E7E6E4]/70 hover:text-[#B59876] transition-colors">Governance</a>
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
