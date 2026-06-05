let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;
const speed = 0.12;

export function initCustomCursor(cursorEl) {
  if (!cursorEl || window.matchMedia('(pointer: coarse)').matches) return;
  document.addEventListener('mousemove', e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });
  function animate() {
    cursorX += (mouseX - cursorX) * speed;
    cursorY += (mouseY - cursorY) * speed;
    cursorEl.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
    requestAnimationFrame(animate);
  }
  animate();
}

const cursor = document.getElementById('custom-cursor');
if (cursor) initCustomCursor(cursor);
