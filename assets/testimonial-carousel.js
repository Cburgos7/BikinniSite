/**
 * testimonial-carousel.js
 * Vanilla JS ES module — named export only, no default export.
 * Auto-rotates testimonial quotes with IntersectionObserver + hover-pause.
 *
 * Security: T-03-15 — uses textContent (not innerHTML) for all quote/author writes.
 * Performance: T-03-16 — timer only runs when section is in viewport.
 */

const ACTIVE_DOT_CLASSES = ['w-4', 'h-2', 'rounded-full', 'bg-coral', 'transition-all', 'duration-300'];
const INACTIVE_DOT_CLASSES = ['w-2', 'h-2', 'rounded-full', 'bg-mid', 'transition-all', 'duration-300'];
const FADE_DURATION = 500;
const INTERVAL_MS = 5000;

function applyDotState(btn, isActive) {
  if (isActive) {
    btn.classList.remove(...INACTIVE_DOT_CLASSES);
    btn.classList.add(...ACTIVE_DOT_CLASSES);
  } else {
    btn.classList.remove(...ACTIVE_DOT_CLASSES);
    btn.classList.add(...INACTIVE_DOT_CLASSES);
  }
}

export function init() {
  // --- Read JSON data from Liquid-rendered script tag ---
  const dataEl = document.getElementById('testimonial-data');
  if (!dataEl) return;

  let data;
  try {
    data = JSON.parse(dataEl.textContent);
  } catch {
    return;
  }

  // Carousel only makes sense with 2+ quotes
  if (!Array.isArray(data) || data.length < 2) return;

  // --- DOM references ---
  const sectionEl = document.getElementById('testimonial-section');
  const quoteEl = document.getElementById('testimonial-quote');
  const authorEl = document.getElementById('testimonial-author');
  const dotsContainer = document.getElementById('testimonial-dots');

  if (!sectionEl || !quoteEl || !authorEl || !dotsContainer) return;

  // --- Build dot buttons ---
  const dots = data.map((_, i) => {
    const btn = document.createElement('button');
    btn.setAttribute('aria-label', `Go to testimonial ${i + 1}`);
    applyDotState(btn, i === 0);
    btn.addEventListener('click', () => showQuote(i));
    dotsContainer.appendChild(btn);
    return btn;
  });

  // --- State ---
  let currentIndex = 0;

  // --- showQuote: fade out → swap content → fade in ---
  function showQuote(index) {
    // Fade out
    quoteEl.classList.add('opacity-0');
    authorEl.classList.add('opacity-0');

    setTimeout(() => {
      const item = data[index];

      // Use textContent to prevent HTML injection (T-03-15)
      quoteEl.textContent = item.quote || '';

      // Build author text node + optional location span
      authorEl.textContent = '';
      const authorText = document.createTextNode(item.author || '');
      authorEl.appendChild(authorText);

      if (item.location) {
        const sep = document.createTextNode(' · ');
        authorEl.appendChild(sep);

        const locSpan = document.createElement('span');
        locSpan.className = 'font-body text-xs text-mid font-normal normal-case tracking-normal';
        locSpan.textContent = item.location;
        authorEl.appendChild(locSpan);
      }

      // Fade back in
      quoteEl.classList.remove('opacity-0');
      authorEl.classList.remove('opacity-0');

      // Sync dots
      dots.forEach((btn, i) => applyDotState(btn, i === index));

      currentIndex = index;
    }, FADE_DURATION);
  }

  // --- Auto-rotation ---
  function next() {
    showQuote((currentIndex + 1) % data.length);
  }

  let timer = null;

  function startTimer() {
    if (timer !== null) return; // already running
    timer = setInterval(next, INTERVAL_MS);
  }

  function stopTimer() {
    clearInterval(timer);
    timer = null;
  }

  // --- IntersectionObserver: only run timer when section is visible (T-03-16) ---
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          startTimer();
        } else {
          stopTimer();
        }
      });
    },
    { threshold: 0 }
  );
  observer.observe(sectionEl);

  // --- Hover pause / resume ---
  sectionEl.addEventListener('mouseenter', stopTimer);
  sectionEl.addEventListener('mouseleave', startTimer);

  // --- Touch pause / resume ---
  sectionEl.addEventListener('touchstart', stopTimer, { passive: true });
  sectionEl.addEventListener('touchend', startTimer, { passive: true });
}
