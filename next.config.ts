import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ─── Static export for Cloudflare Pages / GitHub Pages ───
  // Produces a fully static `out/` directory that can be served by any
  // static host. No server runtime required — perfect for this marketing
  // site (no API routes, no SSR data fetching, no ISR).
  output: "export",

  // Emit static HTML for each route. Required for `output: "export"`.
  // Disabled because the site is a single page with hash anchor navigation
  // (no dynamic routes to pre-render).
  trailingSlash: true,

  // Disable image optimization — static export cannot use the server-side
  // optimizer. The site uses next/image with `unoptimized` automatically
  // when output: "export" is set, but we make it explicit.
  images: {
    unoptimized: true,
  },

  // Build-time TypeScript checking is fine — the project is lint-clean.
  typescript: {
    ignoreBuildErrors: false,
  },

  reactStrictMode: true,
};

export default nextConfig;
