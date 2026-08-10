import { Reveal } from './reveal';

type Row = {
  feature: string;
  seekra: 'yes' | 'partial';
  cloud: 'yes' | 'partial' | 'no';
};

const ROWS: Row[] = [
  { feature: 'Data residency inside your infrastructure', seekra: 'yes', cloud: 'no' },
  { feature: 'Air-gapped / offline option', seekra: 'yes', cloud: 'no' },
  { feature: 'PII masked at source', seekra: 'yes', cloud: 'partial' },
  { feature: 'Page-level citations to source', seekra: 'yes', cloud: 'partial' },
  { feature: 'Visual / image search', seekra: 'yes', cloud: 'partial' },
  { feature: 'Arabic voice (first-class)', seekra: 'yes', cloud: 'partial' },
  { feature: 'Offline operation', seekra: 'yes', cloud: 'no' },
];

function Status({ value }: { value: Row['seekra'] | Row['cloud'] }) {
  if (value === 'yes') {
    return <span className="text-[#B59876] font-semibold">✓ Yes</span>;
  }
  if (value === 'no') {
    return <span className="text-[#B93C32] font-semibold">✗ No</span>;
  }
  return <span className="text-[#4A3F33] font-medium italic">Partial</span>;
}

export function Comparison() {
  return (
    <section id="comparison" className="py-24 lg:py-32 bg-[#E7E6E4] text-[#1F1A14]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <Reveal className="max-w-4xl mb-10 lg:mb-12">
          <div className="text-[13px] font-bold tracking-[0.22em] uppercase text-[#1F1A14] mb-3">
            How Seekra Compares
          </div>
          <h2 className="font-bold tracking-tight text-[#1F1A14]"
              style={{ fontSize: 'clamp(28px, 4vw, 42px)', lineHeight: 1.15, letterSpacing: '-0.02em' }}>
            An honest comparison<span className="text-[#B93C32]">.</span>
          </h2>
          <p className="mt-4 text-[16px] leading-[1.55] text-[#4A3F33] max-w-[880px]">
            Cloud AI assistants are strong for general-purpose work. The comparison below concerns enterprise data handling — where Seekra is purpose-built.
          </p>
        </Reveal>

        <Reveal delay={120}>
          <div className="bg-white border border-black/[0.10] rounded-[12px] overflow-hidden overflow-x-auto">
            <table
              className="w-full"
              style={{ fontFamily: 'Poppins, Inter, system-ui, sans-serif' }}
            >
              <thead>
                <tr className="bg-[#F5F4F2] border-b border-black/[0.10]">
                  <th className="text-left text-[11px] font-semibold tracking-[0.14em] uppercase text-[#1F1A14] px-5 py-3.5" style={{ width: '50%' }}>
                    Capability
                  </th>
                  <th className="text-left text-[11px] font-semibold tracking-[0.14em] uppercase text-[#1F1A14] px-5 py-3.5" style={{ width: '25%' }}>
                    Seekra
                  </th>
                  <th className="text-left text-[11px] font-semibold tracking-[0.14em] uppercase text-[#1F1A14] px-5 py-3.5" style={{ width: '25%' }}>
                    Typical Cloud AI
                  </th>
                </tr>
              </thead>
              <tbody>
                {ROWS.map((row, i) => (
                  <tr
                    key={row.feature}
                    className={`border-b border-black/[0.06] last:border-0 ${
                      i % 2 === 1 ? 'bg-black/[0.02]' : ''
                    }`}
                  >
                    <td className="px-5 py-3.5 text-[14px] font-medium text-[#1F1A14]">
                      {row.feature}
                    </td>
                    <td className="px-5 py-3.5 text-[14px]">
                      <Status value={row.seekra} />
                    </td>
                    <td className="px-5 py-3.5 text-[14px]">
                      <Status value={row.cloud} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>

        <Reveal delay={240}>
          <p className="mt-6 text-[12px] italic text-[#4A3F33] max-w-[1000px]">
            Cloud AI tools are excellent generalists. This comparison concerns enterprise data handling, sovereignty, and verifiable answers — not general-purpose assistant quality.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
