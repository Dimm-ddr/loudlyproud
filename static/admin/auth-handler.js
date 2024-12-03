// static/admin/auth-handler.js

window.addEventListener("load", function () {
  // Helper to check for unsaved changes
  const hasUnsavedChanges = () => {
    const editor = document.querySelector(".cms-editor-active");
    const dirtyFields = document.querySelectorAll('[class*="dirty"]');
    return editor !== null || dirtyFields.length > 0;
  };

  // Helper to clean up auth-related storage
  const cleanAuthStorage = () => {
    // Clear Netlify Identity specific items
    localStorage.removeItem("netlify-cms-user");
    localStorage.removeItem("netlify-cms-api");
    localStorage.removeItem("netlify-cms-collection");
    localStorage.removeItem("netlify-cms-slug");
    localStorage.removeItem("netlifySiteURL");
    localStorage.removeItem("nf_jwt");

    // Clear any Git Gateway tokens
    localStorage.removeItem("git-gateway-repo");
    localStorage.removeItem("git-gateway-branch");
    localStorage.removeItem("git-gateway-token");

    // Remove any session cookies
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    });
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

  // Handle logout and cleanup
  const handleLogout = () => {
    cleanAuthStorage();
    window.location.reload();
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

  // Add error event listener for Git Gateway errors
  window.addEventListener("unhandledrejection", function (event) {
    if (event.reason && event.reason.toString().includes("Git Gateway Error")) {
      handleLogout();
    }
  });

  // Check token on load and periodically
  checkTokenExpiration();
  setInterval(checkTokenExpiration, 60000); // Check every minute

  // Make logout handler available globally
  window.handleLogout = handleLogout;
});
