/**
 * carousel.js
 * Vanilla JS ES module, self-initialising — drives the arrow buttons on every
 * [data-carousel] rail rendered by snippets/carousel.liquid.
 *
 * Scrolling itself is 100% CSS (overflow-x + scroll-snap). This module adds
 * nothing a touch or trackpad user needs; it exists solely because a desktop
 * mouse has no horizontal axis. So the buttons ship with `hidden` in the markup
 * and are only revealed here — if this file fails to load, the rail still
 * scrolls and no inert controls are left on screen.
 *
 * The snippet emits one <script> tag per carousel, but a module URL is only
 * ever evaluated once per document, so this runs a single time and picks up
 * every rail on the page.
 */

// Below this width the layout is touch-first and arrows would just cover cards.
const POINTER_QUERY = '(min-width: 768px)';
const MOTION_QUERY = '(prefers-reduced-motion: reduce)';

// Sub-pixel slack: scrollWidth/clientWidth are fractional after zoom or on
// hi-dpi displays, so an exact comparison flickers the buttons at the ends.
const EPSILON = 4;

function show(btn) {
  btn.classList.remove('hidden');
  btn.classList.add('flex');
}

function hide(btn) {
  btn.classList.remove('flex');
  btn.classList.add('hidden');
}

/**
 * Distance one arrow press should travel: as many whole cards as currently fit,
 * so a click never leaves a card half-cropped against the left edge.
 */
function pageDistance(rail) {
  const slide = rail.firstElementChild;
  if (!slide) return rail.clientWidth;

  const gap = parseFloat(getComputedStyle(rail).columnGap) || 0;
  const step = slide.getBoundingClientRect().width + gap;
  if (!step) return rail.clientWidth;

  const perView = Math.max(1, Math.floor(rail.clientWidth / step));
  return step * perView;
}

function initCarousel(root) {
  const rail = root.querySelector('[data-carousel-rail]');
  const prev = root.querySelector('[data-carousel-prev]');
  const next = root.querySelector('[data-carousel-next]');
  if (!rail || !prev || !next) return;

  const pointer = window.matchMedia(POINTER_QUERY);
  const reduceMotion = window.matchMedia(MOTION_QUERY);

  function sync() {
    const maxScroll = rail.scrollWidth - rail.clientWidth;
    const overflows = maxScroll > EPSILON;
    const enabled = overflows && pointer.matches;
    const offset = rail.scrollLeft;

    if (enabled && offset > EPSILON) show(prev);
    else hide(prev);

    if (enabled && offset < maxScroll - EPSILON) show(next);
    else hide(next);
  }

  function scrollBy(direction) {
    rail.scrollBy({
      left: direction * pageDistance(rail),
      behavior: reduceMotion.matches ? 'auto' : 'smooth',
    });
  }

  prev.addEventListener('click', () => scrollBy(-1));
  next.addEventListener('click', () => scrollBy(1));

  rail.addEventListener('scroll', sync, { passive: true });
  window.addEventListener('resize', sync);
  pointer.addEventListener('change', sync);

  // Lazy-loaded card images have no height attribute, so the rail's scrollWidth
  // is not final at DOMContentLoaded. Re-measure once the box settles.
  if ('ResizeObserver' in window) {
    new ResizeObserver(sync).observe(rail);
  }

  sync();
}

function init() {
  document.querySelectorAll('[data-carousel]').forEach(initCarousel);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
