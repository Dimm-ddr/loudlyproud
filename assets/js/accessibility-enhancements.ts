interface Window {
  announceChange: (message: string) => void;
}

document.addEventListener('DOMContentLoaded', () => {
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.classList.add('sr-only');
  document.body.appendChild(liveRegion);

  window.announceChange = (message: string): void => {
    liveRegion.textContent = message;
  };
});


