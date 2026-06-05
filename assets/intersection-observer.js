export function observeReveal(elements, options = {}) {
  const defaults = { threshold: 0.15, rootMargin: '0px 0px -40px 0px' };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { ...defaults, ...options });
  elements.forEach(el => observer.observe(el));
  return observer;
}
