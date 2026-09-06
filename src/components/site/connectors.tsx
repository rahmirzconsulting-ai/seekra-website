import { FolderSync, RefreshCw, GitBranch, ShieldAlert } from 'lucide-react';
import { Reveal } from './reveal';

const CONNECTORS = [
  { name: 'Local folder', desc: 'Drop files on /ingest/ mount — auto-indexed in 60s. Path rules infer scope + classification from the folder path.', featured: true },
  { name: 'SharePoint / OneDrive', desc: 'Microsoft Graph API. Polls every 15 min (configurable). Path rules map SharePoint folders to org-tree nodes.', featured: false },
  { name: 'Google Drive', desc: 'Service-account auth. Reconstructs Drive paths from parent chain. Shared drives supported.', featured: false },
  { name: 'AWS S3', desc: 'Bucket + prefix sync. IAM or static credentials. Resumable for large folders (10k+ files).', featured: false },
  { name: 'Azure Blob', desc: 'Connection string + container. Incremental sync via ETag change detection.', featured: false },
  { name: 'Google Cloud Storage', desc: 'Service-account JSON. Bucket + prefix. Same incremental logic as S3.', featured: false },
  { name: 'Alibaba OSS', desc: 'For China-facing tenants. OSS access-key + bucket. Same sync engine as other object stores.', featured: false },
  { name: 'SFTP', desc: 'Host + key-based auth. Polls the remote tree; incremental via mtime. For legacy shared-host environments.', featured: false },
  { name: 'IMAP / SMTP', desc: 'Forward ingest@your-tenant.seekra.pk → attachments auto-ingest. Sender domain maps to org scope.', featured: false },
];

const FEATURES = [
  {
    icon: RefreshCw,
    title: 'Incremental sync',
    body: 'Tracks last_synced_at per connector; only fetches new or modified files. Detects deletions (configurable: keep or remove).',
  },
  {
    icon: GitBranch,
    title: 'Versioning on conflict',
    body: 'When a source file is modified, Seekra creates a new version (Brief #39). If the Seekra copy was also edited, a CONNECTOR_CONFLICT audit event is emitted for review.',
  },
  {
    icon: FolderSync,
    title: 'Path-rule inference',
    body: 'Glob patterns map source paths to org-tree nodes + classification. /Films/Production/** → Films · Production team, Confidential. Per-connector rules; first match wins.',
  },
  {
    icon: ShieldAlert,
    title: 'Permission-scoped',
    body: 'Every connector inherits the admin\u2019s tenant. Sync tasks enforce the same access rules as interactive users — no privilege escalation through connectors.',
  },
] as const;

export function Connectors() {
  return (
    <section id="connectors" className="py-24 lg:py-32 bg-[#E7E6E4] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-12 lg:mb-16">
          <div className="seekra-eyebrow-ink mb-3">
            Data Connectors · Brief #32
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 44px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            Point Seekra at your SharePoint. We&rsquo;ll have it indexed by morning<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.6] text-[#4A3F33] max-w-[880px]">
            The #1 onboarding blocker for enterprise content AI is "how do I get my 50,000 documents in?" — without connectors, the answer is "manually, one at a time." Seekra&rsquo;s connector framework pulls from 9 data sources automatically, with incremental sync, conflict resolution, and per-connector scope inference.
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
                      Demo-ready
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
            <span className="font-semibold text-[#1F1A14]">The killer demo moment:</span> during a live demo, drop a file on the watched /ingest/ folder — within 60 seconds, it appears in the Seekra library with the correct scope + classification, fully indexed and searchable. No manual upload, no IT ticket.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
