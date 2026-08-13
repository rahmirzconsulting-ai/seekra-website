import type { Metadata } from "next";
import { Inter, Noto_Naskh_Arabic } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

const naskh = Noto_Naskh_Arabic({
  variable: "--font-arabic",
  subsets: ["arabic"],
  weight: ["400", "500", "700"],
  display: "swap",
});

const SITE_URL = "https://seekra.pk";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Seekra — Content-Aware Intelligence for the Enterprise",
    template: "%s | Seekra",
  },
  description:
    "Self-hosted AI document intelligence for Gulf enterprises. Ask, see, and speak to your documents — every answer cited, every PII masked, every action auditable. Arabic-first, air-gap ready.",
  keywords: [
    "Seekra",
    "AI document intelligence",
    "self-hosted AI",
    "air-gapped AI",
    "Arabic AI",
    "Gulf enterprise AI",
    "data sovereignty",
    "content-aware intelligence",
    "cited AI answers",
    "PII masking",
    "tamper-evident audit",
    "document version comparison",
    "AI governance",
    "enterprise search",
    "RAG",
    "retrieval augmented generation",
    "Arabic document AI",
    "Saudi Arabia AI",
    "UAE AI",
    "government AI",
    "compliance AI",
    "document diff",
    "voice document search",
    "multilingual AI",
  ],
  authors: [{ name: "Seekra" }],
  creator: "Seekra",
  publisher: "Seekra",
  applicationName: "Seekra",
  category: "technology",
  alternates: {
    canonical: SITE_URL,
    languages: { "en-US": SITE_URL },
  },
  icons: {
    icon: [{ url: "/logo-seekra.png", type: "image/png", sizes: "512x512" }],
    shortcut: "/logo-seekra.png",
    apple: "/logo-seekra.png",
  },
  openGraph: {
    title: "Seekra — Content-Aware Intelligence for the Enterprise",
    description:
      "Your documents finally answer back. Self-hosted AI document intelligence — every answer cited, every PII masked, every action auditable. Arabic-first, air-gap ready.",
    url: SITE_URL,
    siteName: "Seekra",
    type: "website",
    locale: "en_US",
    images: [
      {
        url: "/logo-seekra.png",
        width: 512,
        height: 512,
        alt: "Seekra logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Seekra — Content-Aware Intelligence",
    description:
      "Self-hosted AI document intelligence. Every answer cited. Every PII masked. Every action auditable. Arabic-first, air-gap ready.",
    images: ["/logo-seekra.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

// JSON-LD structured data for Google Search
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Seekra",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  description:
    "Self-hosted AI document intelligence for Gulf enterprises. Ask, see, and speak to your documents — every answer cited, every PII masked, every action auditable.",
  url: SITE_URL,
  logo: `${SITE_URL}/logo-seekra.png`,
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "USD",
    description: "Book a demo for pricing.",
  },
  featureList: [
    "Conversational Q&A with page-level citations",
    "Visual / image search",
    "Arabic-first voice interaction",
    "PII masking before AI calls",
    "Tamper-evident audit trail (hash-chained)",
    "PII lineage tracking (provable PII-before-LLM)",
    "Provenance graph (full answer traceability)",
    "Confidence-aware answers",
    "Document diff / versioning",
    "Voice-driven document navigation",
    "Three deployment tiers: Cloud Native, Self-Hosted, Air-Gapped",
  ],
  publisher: {
    "@type": "Organization",
    name: "Seekra",
    url: SITE_URL,
    logo: `${SITE_URL}/logo-seekra.png`,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="reveal-no-js" suppressHydrationWarning>
      <head>
        {/* Mark JS as ready — removes the no-JS fallback so Reveal animations work.
            If JS is disabled, the class stays and .reveal elements are always visible. */}
        <script
          dangerouslySetInnerHTML={{
            __html: "document.documentElement.classList.remove('reveal-no-js');",
          }}
        />
        {/* JSON-LD structured data for Google Search */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body
        className={`${inter.variable} ${naskh.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
