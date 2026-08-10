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
  title: "Seekra — Content-Aware Intelligence for the Enterprise",
  description:
    "Seekra is content-aware intelligence that runs on your infrastructure. Ask, see, and speak to your archive — every answer cited to its source. Self-hosted, PII-masked, Arabic-first.",
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
      "Your documents finally answer back. Seekra is content-aware intelligence that runs on your infrastructure. Ask, see, and speak to your archive — every answer cited to its source.",
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
      "Your documents finally answer back. Self-hosted AI document intelligence for regulated enterprises. Arabic-first, PII-masked, cited answers.",
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
