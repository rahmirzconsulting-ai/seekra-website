import { Navbar } from '@/components/site/navbar';
import { Hero } from '@/components/site/hero';
import { Problem } from '@/components/site/problem';
import { Capabilities } from '@/components/site/capabilities';
import { AccessControl } from '@/components/site/access-control';
import { Connectors } from '@/components/site/connectors';
import { Intelligence } from '@/components/site/intelligence';
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
        <AccessControl />
        <Connectors />
        <Intelligence />
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
