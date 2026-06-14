/**
 * faq.js
 * One-open-at-a-time accordion for the FAQ page.
 * Same data-accordion pattern as pdp.js.
 */

const initFaqAccordions = () => {
  const accordions = document.querySelectorAll('[data-accordion]');
  if (!accordions.length) return;

  const closeAll = () => {
    accordions.forEach((acc) => {
      const trigger = acc.querySelector('[data-accordion-trigger]');
      const body = acc.querySelector('[data-accordion-body]');
      const icon = acc.querySelector('[data-accordion-icon]');
      if (trigger) trigger.setAttribute('aria-expanded', 'false');
      if (body) body.style.maxHeight = '0';
      if (icon) icon.style.transform = 'rotate(0deg)';
    });
  };

  accordions.forEach((accordion) => {
    const trigger = accordion.querySelector('[data-accordion-trigger]');
    const body = accordion.querySelector('[data-accordion-body]');
    const icon = accordion.querySelector('[data-accordion-icon]');
    if (!trigger || !body) return;

    trigger.addEventListener('click', () => {
      const isOpen = trigger.getAttribute('aria-expanded') === 'true';
      closeAll();
      if (!isOpen) {
        trigger.setAttribute('aria-expanded', 'true');
        body.style.maxHeight = body.scrollHeight + 'px';
        if (icon) icon.style.transform = 'rotate(180deg)';
      }
    });
  });
};

document.addEventListener('DOMContentLoaded', initFaqAccordions);
