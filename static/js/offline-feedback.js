// src/js/offline-feedback.ts
document.addEventListener("DOMContentLoaded", () => {
  const feedbackUrlElement = document.querySelector("code");
  const feedbackUrl = feedbackUrlElement?.textContent?.trim();
  if (window.location.pathname.includes("/feedback") && navigator.onLine && feedbackUrl) {
    window.location.href = feedbackUrl;
    return;
  }
  const feedbackLinks = document.querySelectorAll('a[href*="feedback"]');
  const handleFeedbackClick = (e) => {
    if (!navigator.onLine) {
      e.preventDefault();
      window.location.href = "/feedback";
    }
  };
  feedbackLinks.forEach((link) => {
    link.addEventListener("click", handleFeedbackClick);
  });
  window.addEventListener("online", () => {
    if (window.location.pathname.includes("/feedback") && feedbackUrl) {
      window.location.href = feedbackUrl;
    }
  });
  window.addEventListener("offline", () => {
    console.log("Gone offline");
  });
});
//# sourceMappingURL=offline-feedback.js.map
