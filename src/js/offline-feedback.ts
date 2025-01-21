document.addEventListener("DOMContentLoaded", () => {
  // Get feedback form URL from the page if available (for direct feedback page visits)
  const feedbackUrlElement = document.querySelector("code");
  const feedbackUrl = feedbackUrlElement?.textContent?.trim();

  // Handle direct visits to feedback page
  if (
    window.location.pathname.includes("/feedback") &&
    navigator.onLine &&
    feedbackUrl
  ) {
    window.location.href = feedbackUrl;
    return;
  }

  // Handle feedback link clicks
  const feedbackLinks = document.querySelectorAll('a[href*="feedback"]');
  const handleFeedbackClick = (e: Event) => {
    if (!navigator.onLine) {
      e.preventDefault();
      window.location.href = "/feedback";
    }
  };

  feedbackLinks.forEach((link) => {
    link.addEventListener("click", handleFeedbackClick);
  });

  // Listen for online/offline events
  window.addEventListener("online", () => {
    // If we're on the feedback page and go back online, redirect to the form
    if (window.location.pathname.includes("/feedback") && feedbackUrl) {
      window.location.href = feedbackUrl;
    }
  });

  window.addEventListener("offline", () => {
    console.log("Gone offline");
  });
});
