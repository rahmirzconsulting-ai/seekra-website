import { Navbar } from '@/components/site/navbar';
import { Hero } from '@/components/site/hero';
import { Problem } from '@/components/site/problem';
import { Capabilities } from '@/components/site/capabilities';
import { Trust } from '@/components/site/trust';
import { Governance } from '@/components/site/governance';
import { Comparison } from '@/components/site/comparison';
import { Deployment } from '@/components/site/deployment';
import { UseCases } from '@/components/site/use-cases';
import { Contact } from '@/components/site/contact';
import { Footer } from '@/components/site/footer';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-[#202020]">
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Problem />
        <Capabilities />
        <Trust />
        <Governance />
        <Comparison />
        <Deployment />
        <UseCases />
        <Contact />
      </main>
      <Footer />
    </div>
  );
}
