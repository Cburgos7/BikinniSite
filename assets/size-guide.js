/**
 * size-guide.js
 * Fit recommender — client-side only, no server round-trip.
 * Security: all inputs validated via parseFloat + isFinite + > 0 before use.
 * Results written via textContent (not innerHTML) — XSS-safe.
 */

/** @type {{ size: string, bustMin: number, bustMax: number, waistMin: number, waistMax: number, hipMin: number, hipMax: number }[]} */
const SIZE_TABLE = [
  { size: 'XXS', bustMin: 28, bustMax: 31, waistMin: 22, waistMax: 24, hipMin: 30, hipMax: 33 },
  { size: 'XS',  bustMin: 32, bustMax: 34, waistMin: 25, waistMax: 27, hipMin: 34, hipMax: 36 },
  { size: 'S',   bustMin: 34, bustMax: 36, waistMin: 27, waistMax: 29, hipMin: 36, hipMax: 38 },
  { size: 'M',   bustMin: 36, bustMax: 38, waistMin: 29, waistMax: 31, hipMin: 38, hipMax: 40 },
  { size: 'L',   bustMin: 38, bustMax: 41, waistMin: 31, waistMax: 34, hipMin: 40, hipMax: 43 },
  { size: 'XL',  bustMin: 41, bustMax: 44, waistMin: 34, waistMax: 37, hipMin: 43, hipMax: 46 },
  { size: '2XL', bustMin: 44, bustMax: 48, waistMin: 37, waistMax: 41, hipMin: 46, hipMax: 50 },
  { size: '3XL', bustMin: 48, bustMax: 52, waistMin: 41, waistMax: 45, hipMin: 50, hipMax: 54 },
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
  if (!submitBtn) return;

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
