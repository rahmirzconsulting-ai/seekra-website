import { FolderSync, RefreshCw, GitBranch, ShieldAlert } from 'lucide-react';
import { Reveal } from './reveal';

const CONNECTORS = [
  { name: 'Local / network folder', desc: 'Point Seekra at a shared drive or mounted folder — new and changed files are picked up automatically, with the right scope and classification applied based on the folder path.', featured: true },
  { name: 'SharePoint / OneDrive', desc: 'Connect to a SharePoint site or OneDrive folder. Folder structure maps to your organization tree, so the right people see the right documents.' },
  { name: 'Google Drive', desc: 'Service-account authentication. Reconstructs Drive paths from the parent chain so you can scope by folder. Shared drives supported.' },
  { name: 'Amazon S3', desc: 'Sync from any S3 bucket by prefix. Resumable for large archives (tens of thousands of files).' },
  { name: 'Azure Blob Storage', desc: 'Connection-string authentication. Incremental sync detects changes via storage versioning metadata.' },
  { name: 'Google Cloud Storage', desc: 'Service-account authentication. Same incremental sync logic as Amazon S3.' },
  { name: 'Alibaba Cloud OSS', desc: 'For China-facing tenants. Same sync engine as the other object stores — no separate setup.' },
  { name: 'SFTP', desc: 'For legacy shared-host environments where files arrive over secure file transfer. Polls the remote tree on a schedule.' },
  { name: 'Email (IMAP)', desc: 'Forward messages to a dedicated ingest address — attachments are added to the library automatically, scoped by the sender\u2019s domain.' },
];

const FEATURES = [
  {
    icon: RefreshCw,
    title: 'Incremental sync',
    body: 'Seekra tracks what has already been ingested and only fetches new or modified files. Changes to a source file are detected and pulled in on the next sync cycle.',
  },
  {
    icon: GitBranch,
    title: 'Versioning on change',
    body: 'When a source file is modified, Seekra creates a new version of the document — the previous version is preserved. If the Seekra copy was also edited, a conflict is flagged for review.',
  },
  {
    icon: FolderSync,
    title: 'Automatic scoping',
    body: 'Folder paths in the source map to your organization tree. A file in "/Finance/Reports/" is automatically scoped to the Finance team — no manual classification step.',
  },
  {
    icon: ShieldAlert,
    title: 'Respects access control',
    body: 'Connectors run with administrator privileges for ingestion, but the documents they pull in are still subject to the same org-tree scoping and classification rules as any other document.',
  },
];

export function Connectors() {
  return (
    <section id="connectors" className="py-24 lg:py-32 bg-[#E7E6E4] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow-ink mb-3">
            Data Connectors
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Point Seekra at where your documents already live<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#4A3F33] max-w-[880px]">
            The most common question after a demo is &ldquo;how do I get my tens of thousands of documents in?&rdquo; — and the answer used to be &ldquo;manually, one at a time.&rdquo; Seekra&rsquo;s connector framework pulls from nine data sources automatically, with incremental sync, conflict resolution, and automatic scoping based on the folder structure you already have.
          </p>
        </Reveal>

        {/* 9 connectors grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          {CONNECTORS.map((c, i) => (
            <Reveal key={c.name} delay={(i % 3) * 80}>
              <article
                className={`rounded-[12px] p-5 h-full ${
                  c.featured
                    ? 'bg-[#202020] border border-[#B59876]/40 shadow-lg shadow-[#B59876]/10'
                    : 'bg-white border border-black/[0.08]'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className={`text-[16px] font-semibold tracking-tight ${c.featured ? 'text-[#E7E6E4]' : 'text-[#1F1A14]'}`}>
                    {c.name}
                  </h3>
                  {c.featured && (
                    <span className="text-[10px] font-bold tracking-[0.14em] uppercase text-[#B59876]">
                      Easiest start
                    </span>
                  )}
                </div>
                <p className={`text-[13px] leading-[1.55] ${c.featured ? 'text-[#E7E6E4]/72' : 'text-[#4A3F33]'}`}>
                  {c.desc}
                </p>
              </article>
            </Reveal>
          ))}
        </div>

        {/* 4 features */}
        <Reveal delay={120}>
          <div className="bg-white border border-black/[0.08] rounded-[14px] p-7 lg:p-8">
            <h3 className="text-[18px] font-semibold text-[#1F1A14] mb-5 tracking-tight">
              How sync works
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
              {FEATURES.map((f, i) => {
                const Icon = f.icon;
                return (
                  <div key={i}>
                    <div className="w-10 h-10 rounded-[8px] bg-[#B59876]/12 flex items-center justify-center mb-3">
                      <Icon className="w-5 h-5 text-[#B59876]" strokeWidth={1.5} />
                    </div>
                    <h4 className="text-[14px] font-semibold text-[#1F1A14] mb-1.5 tracking-tight">
                      {f.title}
                    </h4>
                    <p className="text-[12px] leading-[1.5] text-[#4A3F33]">
                      {f.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </Reveal>

        <Reveal delay={200}>
          <p className="mt-8 text-[14px] leading-[1.6] text-[#4A3F33] max-w-[720px]">
            <span className="font-semibold text-[#1F1A14]">In practice:</span> a typical enterprise onboarding starts with one connector pointed at a shared drive or SharePoint site. Within a sync cycle, the library is populated, scoped, and searchable. Additional connectors are added as more teams come on board.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
