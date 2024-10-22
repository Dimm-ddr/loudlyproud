// static/admin/auth-handler.js

window.addEventListener("load", function () {
  const originalInit = window.CMS.init;

  // Helper to check for unsaved changes
  const hasUnsavedChanges = () => {
    // Check if any forms are currently being edited
    const editor = document.querySelector(".cms-editor-active");
    const dirtyFields = document.querySelectorAll('[class*="dirty"]');
    return editor !== null || dirtyFields.length > 0;
  };

  // Helper to safely handle session expiry
  const handleSessionExpiry = (reason) => {
    if (hasUnsavedChanges()) {
      // Show warning to user
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
            <button onclick="window.location.reload()" style="background: white; color: #ff9800; border: none; padding: 4px 8px; border-radius: 2px; cursor: pointer;">
              Refresh Now
            </button>
          `;
        document.body.appendChild(warning);

        // Remove warning after timeout
        setTimeout(() => {
          if (document.getElementById("cms-session-warning")) {
            document.getElementById("cms-session-warning").remove();
          }
        }, warningTime);
      }
    } else {
      // No unsaved changes, safe to reload
      console.log(`Session action required (${reason}), reloading...`);
      window.location.reload();
    }
  };

  // Helper to check token expiration with Netlify Identity token format
  const isTokenNearExpiration = (token) => {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const expiryTime = payload.exp * 1000;
      const fifteenMinutes = 15 * 60 * 1000; // Increased to 15 minutes for more warning time
      return expiryTime - Date.now() <= fifteenMinutes;
    } catch (e) {
      console.error("Error checking Netlify Identity token:", e);
      return false; // Changed to false to prevent unnecessary logouts on error
    }
  };

  // Helper to clean CMS and Identity storage
  const cleanStorage = () => {
    if (!hasUnsavedChanges()) {
      Object.keys(localStorage).forEach((key) => {
        if (
          key.startsWith("cms_") ||
          key.startsWith("netlify-cms-") ||
          key.startsWith("gotrue.") ||
          key.startsWith("netlifySiteURL")
        ) {
          localStorage.removeItem(key);
        }
      });
      return true;
    }
    return false;
  };

  // Initialize Netlify Identity event handlers
  if (window.netlifyIdentity) {
    window.netlifyIdentity.on("init", (user) => {
      if (user) {
        if (!localStorage.getItem("cms_login_time")) {
          localStorage.setItem("cms_login_time", Date.now().toString());
        }
      }
    });

    window.netlifyIdentity.on("login", () => {
      localStorage.setItem("cms_login_time", Date.now().toString());
      console.log("Netlify Identity login successful");
    });

    window.netlifyIdentity.on("logout", () => {
      if (cleanStorage()) {
        console.log("Netlify Identity logout and storage cleaned");
      }
    });

    // Handle token expiry
    window.netlifyIdentity.on("error", (err) => {
      console.error("Netlify Identity error:", err);
      if (err.message.includes("token") || err.message.includes("expired")) {
        handleSessionExpiry("token error");
      }
    });
  }

  // Wrap CMS init
  window.CMS.init = (...args) => {
    const enhanceConfig = (config) => {
      const enhancedConfig = { ...config };

      // Add CMS-specific handlers
      enhancedConfig.onLogin = () => {
        console.log("CMS login successful");
        if (config.onLogin) config.onLogin();
      };

      enhancedConfig.onLogout = () => {
        if (hasUnsavedChanges()) {
          const confirmed = window.confirm(
            "You have unsaved changes. Are you sure you want to log out?",
          );
          if (!confirmed) return;
        }

        console.log("CMS logout initiated");
        cleanStorage();
        if (config.onLogout) config.onLogout();
        if (window.netlifyIdentity) {
          window.netlifyIdentity.logout();
        }
      };

      return enhancedConfig;
    };

    return originalInit.apply(
      CMS,
      args.map((arg) => (typeof arg === "object" ? enhanceConfig(arg) : arg)),
    );
  };

  // Check session on visibility change
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      const cmsToken = localStorage.getItem("netlify-cms-auth");
      const identityToken = localStorage.getItem("gotrue.user");

      if (cmsToken && isTokenNearExpiration(cmsToken)) {
        handleSessionExpiry("token near expiration");
      } else if (!identityToken && hasUnsavedChanges()) {
        console.log("No Identity session found but has unsaved changes");
        // Don't force reload, just warn the user
        handleSessionExpiry("session not found");
      }
    }
  });

  // Periodic token check (every 5 minutes)
  setInterval(
    () => {
      const token = localStorage.getItem("netlify-cms-auth");
      if (token && isTokenNearExpiration(token)) {
        // Try to refresh the session first
        if (window.netlifyIdentity) {
          window.netlifyIdentity
            .refresh()
            .then(() => {
              console.log("Session refreshed successfully");
            })
            .catch(() => {
              handleSessionExpiry("refresh failed");
            });
        }
      }
    },
    5 * 60 * 1000,
  ); // Changed to 5 minutes
});
