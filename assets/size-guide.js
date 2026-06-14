/**
 * size-guide.js
 * Fit recommender — client-side only, no server round-trip.
 * Security: all inputs validated via parseFloat + isFinite + > 0 before use.
 * Results written via textContent (not innerHTML) — XSS-safe.
 */

/** @type {{ size: string, bustMin: number, bustMax: number, waistMin: number, waistMax: number, hipMin: number, hipMax: number }[]} */
const SIZE_TABLE = [
  { size: 'XXS', bustMin: 28, bustMax: 31, waistMin: 22, waistMax: 24, hipMin: 30, hipMax: 33 },
  { size: 'XS',  bustMin: 32, bustMax: 33, waistMin: 25, waistMax: 26, hipMin: 34, hipMax: 35 },
  { size: 'S',   bustMin: 34, bustMax: 35, waistMin: 27, waistMax: 28, hipMin: 36, hipMax: 37 },
  { size: 'M',   bustMin: 36, bustMax: 37, waistMin: 29, waistMax: 30, hipMin: 38, hipMax: 39 },
  { size: 'L',   bustMin: 38, bustMax: 40, waistMin: 31, waistMax: 33, hipMin: 40, hipMax: 42 },
  { size: 'XL',  bustMin: 41, bustMax: 43, waistMin: 34, waistMax: 36, hipMin: 43, hipMax: 45 },
  { size: '2XL', bustMin: 44, bustMax: 47, waistMin: 37, waistMax: 40, hipMin: 46, hipMax: 49 },
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
