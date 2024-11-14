interface Window {
  announceChange: (message: string) => void;
}

document.addEventListener('DOMContentLoaded', () => {
  // Add aria-live region for dynamic content
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.classList.add('sr-only');
  document.body.appendChild(liveRegion);

  // Export function for announcing changes
  window.announceChange = (message: string): void => {
    liveRegion.textContent = message;
  };
}); 