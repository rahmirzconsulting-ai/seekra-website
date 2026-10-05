/**
 * Seekra — Site Configuration
 * Single source of truth for contact email, app URL, and other configurable values.
 * Update here once and the change propagates everywhere.
 */

export const SITE_CONFIG = {
  domain: "seekra.pk",
  url: "https://seekra.pk",
  // "Launch App" goes through the /app bridge page, which probes app.seekra.pk
  // for health. If live → redirect. If offline → show "unavailable" message
  // then auto-redirect to #contact on the main site.
  appBridgeUrl: "/app",
  // The app URL the bridge page probes for health and redirects to when live.
  appInternalUrl: "https://app.seekra.pk",
  contactEmail: "rahmirz.consulting@gmail.com",
  // FormSubmit.co endpoint — posts form data to the contact email via AJAX.
  // Replace with a @seekra.pk email when ready (just change contactEmail above
  // AND the form action endpoint below).
  formSubmitEndpoint: "https://formsubmit.co/ajax/rahmirz.consulting@gmail.com",
  year: 2026,
  tagline: "Content-Aware Intelligence for the Enterprise",
} as const;

export type SiteConfig = typeof SITE_CONFIG;
