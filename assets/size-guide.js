/**
 * size-guide.js
 * Fit recommender — client-side only, no server round-trip.
 * Security: all inputs validated via parseFloat + isFinite + > 0 before use.
 * Results written via textContent (not innerHTML) — XSS-safe.
 */

/**
 * Measurements are the manufacturer's published size chart, not estimates.
 * XS is charted by the supplier but never stocked, so it is omitted — recommending
 * a size we cannot sell just produces a dead end.
 * @type {{ size: string, bustMin: number, bustMax: number, waistMin: number, waistMax: number, hipMin: number, hipMax: number }[]}
 */
const SIZE_TABLE = [
  { size: 'S',  bustMin: 32, bustMax: 34, waistMin: 24, waistMax: 26, hipMin: 34, hipMax: 36 },
  { size: 'M',  bustMin: 34, bustMax: 36, waistMin: 26, waistMax: 28, hipMin: 36, hipMax: 38 },
  { size: 'L',  bustMin: 36, bustMax: 38, waistMin: 28, waistMax: 32, hipMin: 38, hipMax: 40 },
  { size: 'XL', bustMin: 38, bustMax: 40, waistMin: 32, waistMax: 34, hipMin: 41, hipMax: 44 },
  { size: '1X', bustMin: 40, bustMax: 42, waistMin: 40, waistMax: 42, hipMin: 44, hipMax: 48 },
  { size: '2X', bustMin: 42, bustMax: 44, waistMin: 42, waistMax: 44, hipMin: 46, hipMax: 50 },
  { size: '3X', bustMin: 44, bustMax: 46, waistMin: 44, waistMax: 46, hipMin: 50, hipMax: 52 },
  { size: '4X', bustMin: 46, bustMax: 50, waistMin: 46, waistMax: 50, hipMin: 52, hipMax: 54 },
];

/**
 * Find the recommended size based on measurements.
 * Bust-first match: if bust matches all three → exact match returned immediately.
 * If only bust matches → saved as candidate (bust-priority fallback).
 * Returns size string or null if no match.
 * @param {number} bust
 * @param {number} waist
 * @param {number} hip
 * @returns {string|null}
 */
function findSize(bust, waist, hip) {
  let bustCandidate = null;

  for (const row of SIZE_TABLE) {
    const bustMatch = bust >= row.bustMin && bust <= row.bustMax;
    if (!bustMatch) continue;

    const waistMatch = waist >= row.waistMin && waist <= row.waistMax;
    const hipMatch = hip >= row.hipMin && hip <= row.hipMax;

    if (waistMatch && hipMatch) {
      return row.size;
    }

    if (bustCandidate === null) {
      bustCandidate = row.size;
    }
  }

  return bustCandidate;
}

document.addEventListener('DOMContentLoaded', () => {
  const bustInput  = document.getElementById('sg-bust');
  const waistInput = document.getElementById('sg-waist');
  const hipInput   = document.getElementById('sg-hips');
  const submitBtn  = document.getElementById('sg-submit');
  const resultDiv  = document.getElementById('sg-result');
  const sizePill   = document.getElementById('sg-size-pill');
  const noMatch    = document.getElementById('sg-no-match');

  // Guard: section not present on this page
  if (!submitBtn || !bustInput || !waistInput || !hipInput) return;

  submitBtn.addEventListener('click', () => {
    const bust  = parseFloat(bustInput.value);
    const waist = parseFloat(waistInput.value);
    const hip   = parseFloat(hipInput.value);

    // Security: validate all inputs are positive finite numbers
    const valid = [bust, waist, hip].every((v) => isFinite(v) && v > 0);

    if (!valid) {
      resultDiv.classList.add('hidden');
      noMatch.classList.remove('hidden');
      return;
    }

    const result = findSize(bust, waist, hip);

    if (result) {
      sizePill.textContent = result;
      resultDiv.classList.remove('hidden');
      noMatch.classList.add('hidden');
    } else {
      resultDiv.classList.add('hidden');
      noMatch.classList.remove('hidden');
    }
  });

  // Reset result display on any input change
  [bustInput, waistInput, hipInput].forEach((input) => {
    input?.addEventListener('input', () => {
      resultDiv.classList.add('hidden');
      noMatch.classList.add('hidden');
    });
  });
});
