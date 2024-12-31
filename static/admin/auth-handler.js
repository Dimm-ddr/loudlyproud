// static/admin/auth-handler.js

// Store interval reference
let tokenCheckInterval;

window.addEventListener("load", function () {
  // Clear any existing interval first
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval);
  }

  // Set new interval and store reference
  tokenCheckInterval = setInterval(checkTokenExpiration, 60000);

  // Clear interval on page unload
  window.addEventListener('unload', () => {
    if (tokenCheckInterval) {
      clearInterval(tokenCheckInterval);
    }
  });

  // Helper to check for unsaved changes
  const hasUnsavedChanges = () => {
    const editor = document.querySelector(".cms-editor-active");
    const dirtyFields = document.querySelectorAll('[class*="dirty"]');
    return editor !== null || dirtyFields.length > 0;
  };

  // Helper to clean up auth-related storage
  const cleanAuthStorage = () => {
    // Clear Netlify Identity specific items
    localStorage.clear(); // Clear everything to be thorough
    sessionStorage.clear(); // Clear session storage as well

    // Remove any session cookies
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/.netlify/;`;
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/admin;`;
    });
  };

  // Handle logout and cleanup
  const handleLogout = async () => {
    try {
      // Try to logout from Netlify Identity first
      const netlifyIdentity = window.netlifyIdentity;
      if (netlifyIdentity && netlifyIdentity.currentUser()) {
        await netlifyIdentity.logout();
      }
    } catch (e) {
      console.error("Error during Netlify Identity logout:", e);
    }

    cleanAuthStorage();

    // Force reload from server, not cache
    window.location.href =
      window.location.href.split("#")[0] + "?t=" + Date.now();
  };

  // Helper to handle session expiry
  const handleSessionExpiry = (reason) => {
    if (hasUnsavedChanges()) {
      const warningTime = 5 * 60 * 1000; // 5 minutes
      const message = `Your session will expire soon. Please save your changes and refresh the page. You have approximately 5 minutes.`;

      if (!document.getElementById("cms-session-warning")) {
        const warning = document.createElement("div");
        warning.id = "cms-session-warning";
        warning.style.cssText = `
          position: fixed;
          top: 16px;
          right: 16px;
          padding: 16px;
          background: #ff9800;
          color: white;
          border-radius: 4px;
          z-index: 9999;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        `;
        warning.innerHTML = `
          <div style="margin-bottom: 8px;">${message}</div>
          <button onclick="handleLogout()" style="background: white; color: #ff9800; border: none; padding: 4px 8px; border-radius: 2px; cursor: pointer;">
            Refresh Now
          </button>
        `;
        document.body.appendChild(warning);

        setTimeout(() => {
          if (document.getElementById("cms-session-warning")) {
            document.getElementById("cms-session-warning").remove();
          }
        }, warningTime);
      }
    } else {
      handleLogout();
    }
  };

  // Check for expired token on load
  const checkTokenExpiration = () => {
    const token = localStorage.getItem("netlify-cms-user");
    if (token) {
      try {
        const { exp } = JSON.parse(atob(token.split(".")[1]));
        if (exp * 1000 < Date.now()) {
          handleSessionExpiry("Token expired");
        }
      } catch (e) {
        console.error("Error checking token expiration:", e);
        handleLogout();
      }
    }
  };

  // Add error event listeners for various authentication issues
  window.addEventListener("unhandledrejection", function (event) {
    if (
      event.reason &&
      (event.reason.toString().includes("Git Gateway Error") ||
        event.reason.toString().includes("Failed to fetch") ||
        event.reason.toString().includes("API_ERROR"))
    ) {
      event.preventDefault(); // Prevent the default error handling
      handleLogout();
    }
  });

  // Listen for specific HTTP errors
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    try {
      const response = await originalFetch(...args);
      if (
        response.status === 401 ||
        response.status === 403 ||
        response.status === 400
      ) {
        if (args[0].includes("git/settings") || args[0].includes("git/token")) {
          handleLogout();
          return new Response(null, { status: 401 });
        }
      }
      return response;
    } catch (error) {
      handleLogout();
      throw error;
    }
  };

  // Check token on load and periodically
  checkTokenExpiration();
  setInterval(checkTokenExpiration, 60000); // Check every minute

  // Make logout handler available globally
  window.handleLogout = handleLogout;
});
