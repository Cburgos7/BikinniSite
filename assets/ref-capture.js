/**
 * ref-capture.js
 * Shared referral-code utility — consumed by ga4.js and upromote.js.
 *
 * Runs at module evaluation time (top-level, before DOMContentLoaded) so the
 * value is available synchronously to any importer on the same page.
 *
 * Side effects:
 *   - Reads ?ref= query param on first load; writes to sessionStorage under
 *     key "upromote_ref" if the value is non-empty.
 *
 * Exports:
 *   getInfluencerCode() — returns the referral code or utm_campaign fallback.
 */

// Capture ref param on module evaluation (single write path — T-06-06)
const _ref = new URLSearchParams(location.search).get('ref') || '';
if (_ref) {
  sessionStorage.setItem('upromote_ref', _ref);
}

/**
 * Returns the active influencer / referral code for the current session.
 * Priority order:
 *   1. sessionStorage "upromote_ref" (set by ?ref= on any page in session)
 *   2. utm_campaign query param on the current URL
 *   3. null if neither is present
 *
 * @returns {string|null}
 */
export function getInfluencerCode() {
  return (
    sessionStorage.getItem('upromote_ref') ||
    new URLSearchParams(location.search).get('utm_campaign') ||
    null
  );
}
