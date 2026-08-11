/**
 * Seekra — Site Configuration
 * Single source of truth for contact email, app URL, and other configurable values.
 * Update here once and the change propagates everywhere.
 */

export const SITE_CONFIG = {
  domain: "seekra.pk",
  url: "https://seekra.pk",
  // The bridge page URL — visitors hit this first, get redirected to the app if it's live
  // or see a "book a demo" message if EC2 is offline.
  appBridgeUrl: "/app",
  // The actual EC2 hostname where the Seekra app runs. The bridge page probes
  // `${appInternalUrl}/api/health` to detect if EC2 is up. Configure this as a
  // separate subdomain (e.g., app-internal.seekra.pk) pointing to your EC2 IP.
  // Update this when your EC2 IP changes.
  appInternalUrl: "https://app-internal.seekra.pk",
  contactEmail: "rahmirz.consulting@gmail.com",
  // FormSubmit.co endpoint — posts form data to the contact email via AJAX.
  // Replace with a @seekra.pk email when ready (just change contactEmail above
  // AND the form action endpoint below).
  formSubmitEndpoint: "https://formsubmit.co/ajax/rahmirz.consulting@gmail.com",
  year: 2026,
  tagline: "Content-Aware Intelligence for the Enterprise",
} as const;

export type SiteConfig = typeof SITE_CONFIG;
