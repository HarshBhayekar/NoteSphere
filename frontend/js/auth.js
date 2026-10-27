/**
 * NoteSphere - Authentication Management
 * Handles Firebase Auth sign-in, sign-up, sign-out, and UI navbar synchronization
 */

let currentUserState = null;
let currentToken = null;
let authReadyResolved = false;
let authReadyResolver;
const authReadyPromise = new Promise((resolve) => {
  authReadyResolver = resolve;
});

// Helper for any page/script to await Firebase session verification
function waitForAuthReady() {
  if (authReadyResolved) return Promise.resolve(currentUserState);
  return Promise.race([
    authReadyPromise,
    new Promise((resolve) => setTimeout(() => resolve(null), 3500))
  ]);
}

// Retrieves token for API client (waiting for initial auth check if needed)
async function getCurrentToken() {
  if (currentToken) return currentToken;

  if (!authReadyResolved) {
    await waitForAuthReady();
    if (currentToken) return currentToken;
  }

  if (typeof auth !== "undefined" && auth && auth.currentUser) {
    try {
      currentToken = await auth.currentUser.getIdToken();
      return currentToken;
    } catch (e) {
      console.error("Error getting Firebase token:", e);
    }
  }

  // Check localStorage for mock dev token
  const devToken = localStorage.getItem("notesphere_dev_token");
  if (devToken) return devToken;

  return null;
}

// Retrieves current user state
async function getCurrentUser() {
  if (!authReadyResolved) {
    await waitForAuthReady();
  }
  return currentUserState;
}

// User state observer
function initAuthListener() {
  if (typeof auth !== "undefined" && auth) {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          currentToken = await user.getIdToken();
        } catch (e) {
          console.error("Error getting user token:", e);
        }
        currentUserState = {
          uid: user.uid,
          email: user.email,
          displayName: user.displayName || (user.email ? user.email.split("@")[0] : "Student"),
          role: "student"
        };
      } else {
        currentUserState = null;
        currentToken = null;
      }

      // Mark auth as resolved immediately so callers waiting on getCurrentToken() unblock
      if (!authReadyResolved) {
        authReadyResolved = true;
        if (authReadyResolver) authReadyResolver(currentUserState);
      }

      updateNavbarAuthUI();

      // Background sync with backend to get role and update profile
      if (user) {
        try {
          const syncRes = await api.syncUser({ displayName: user.displayName });
          if (syncRes && syncRes.data) {
            currentUserState = syncRes.data;
            updateNavbarAuthUI();
          }
        } catch (e) {
          console.warn("Auth sync warning:", e);
        }
      }
    });
  } else {
    // Local dev mode fallback
    const savedDevUser = localStorage.getItem("notesphere_dev_user");
    if (savedDevUser) {
      try {
        currentUserState = JSON.parse(savedDevUser);
        currentToken = localStorage.getItem("notesphere_dev_token");
      } catch (e) {
        currentUserState = null;
      }
    }
    if (!authReadyResolved) {
      authReadyResolved = true;
      if (authReadyResolver) authReadyResolver(currentUserState);
    }
    updateNavbarAuthUI();
  }
}


// Updates Navbar buttons and profile links based on current user and role
function updateNavbarAuthUI() {
  const authNav = document.getElementById("nav-auth-container");
  if (!authNav) return;

  if (currentUserState) {
    authNav.innerHTML = `
      <ul class="nav-links" style="display:flex; align-items:center; gap:20px; list-style:none; margin-right:16px;">
        <li><a href="/upload.html" class="nav-link">Upload Notes</a></li>
        <li><a href="/my-uploads.html" class="nav-link">My Uploads</a></li>
      </ul>
      <div class="user-badge">
        <span>${escapeHtml(currentUserState.displayName || currentUserState.email || "Student")}</span>
      </div>
      <button onclick="handleSignOut()" class="btn btn-secondary btn-sm">Sign Out</button>
    `;
  } else {
    authNav.innerHTML = `
      <a href="/login.html" class="btn btn-secondary btn-sm">Sign In</a>
      <a href="/register.html" class="btn btn-primary btn-sm">Get Started</a>
    `;
  }
}

// Centralized authentication error formatter
function formatAuthErrorMessage(error) {
  if (!error) return "An unexpected error occurred. Please try again.";

  const code = error.code || "";
  const msg = (error.message || error.toString() || "").toLowerCase();

  if (code === "auth/email-already-in-use" || msg.includes("email-already-in-use") || msg.includes("email already in use")) {
    return 'User account already exists. Please <a href="/login.html" style="font-weight:600; text-decoration:underline; color:inherit;">sign in here</a>.';
  }

  if (code === "auth/user-not-found" || msg.includes("user-not-found") || msg.includes("user not found")) {
    return 'Account not found. Please <a href="/register.html" style="font-weight:600; text-decoration:underline; color:inherit;">register here</a> to create a new account.';
  }

  if (code === "auth/wrong-password" || msg.includes("wrong-password") || msg.includes("wrong password")) {
    return "Incorrect password. Please verify your credentials and try again.";
  }

  if (code === "auth/invalid-credential" || msg.includes("invalid-credential")) {
    return 'Invalid email or password. If you do not have an account yet, please <a href="/register.html" style="font-weight:600; text-decoration:underline; color:inherit;">create an account</a>.';
  }

  if (code === "auth/weak-password" || msg.includes("weak-password")) {
    return "Password is too weak. Please use at least 6 characters (letters and numbers recommended).";
  }

  if (code === "auth/invalid-email" || msg.includes("invalid-email")) {
    return "Please enter a valid email address (e.g. student@example.edu).";
  }

  if (code === "auth/user-disabled" || msg.includes("user-disabled")) {
    return "This user account has been disabled. Please contact the administrator.";
  }

  if (code === "auth/too-many-requests" || msg.includes("too-many-requests")) {
    return "Too many failed attempts. Access temporarily locked for security. Please wait a few moments and try again.";
  }

  if (code === "auth/network-request-failed" || msg.includes("network-request-failed")) {
    return "Network connection error. Please verify your internet connection and try again.";
  }

  if (code === "auth/id-token-expired" || code === "auth/user-token-expired" || msg.includes("token-expired") || msg.includes("expired")) {
    return 'Your session has timed out. Please <a href="/login.html" style="font-weight:600; text-decoration:underline; color:inherit;">sign in again</a>.';
  }

  if (code === "auth/operation-not-allowed" || msg.includes("operation-not-allowed")) {
    return "Email & Password authentication is not enabled in Firebase Authentication console. Please contact the administrator.";
  }

  return error.message || "Unable to complete request. Please verify your information and try again.";
}

// Sign In
async function handleSignIn(email, password) {
  if (!email || !password) {
    throw new Error("Please enter both email address and password.");
  }

  if (typeof auth !== "undefined" && auth) {
    const cred = await auth.signInWithEmailAndPassword(email, password);
    currentToken = await cred.user.getIdToken();
    currentUserState = {
      uid: cred.user.uid,
      email: cred.user.email,
      displayName: cred.user.displayName || email.split("@")[0],
      role: "student"
    };

    try {
      const syncRes = await api.syncUser();
      if (syncRes && syncRes.data) {
        currentUserState = syncRes.data;
      }
    } catch (syncErr) {
      console.warn("Backend user sync warning during sign in:", syncErr);
    }

    updateNavbarAuthUI();
    return currentUserState;
  } else {
    // Dev login simulation
    const user = {
      uid: "dev_student_" + Date.now().toString(36),
      email,
      displayName: email.split("@")[0],
      role: "student"
    };
    const token = `dev-token-student-${user.uid}`;
    localStorage.setItem("notesphere_dev_user", JSON.stringify(user));
    localStorage.setItem("notesphere_dev_token", token);
    currentUserState = user;
    currentToken = token;
    updateNavbarAuthUI();
    return user;
  }
}

// Register
async function handleRegister(name, email, password) {
  if (!email || !password) {
    throw new Error("Please complete all required fields.");
  }
  if (password.length < 6) {
    throw new Error("Password must be at least 6 characters long.");
  }

  if (typeof auth !== "undefined" && auth) {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    if (name) {
      try {
        await cred.user.updateProfile({ displayName: name });
      } catch (profErr) {
        console.warn("Profile update warning:", profErr);
      }
    }
    currentToken = await cred.user.getIdToken();
    currentUserState = {
      uid: cred.user.uid,
      email: cred.user.email,
      displayName: name || email.split("@")[0],
      role: "student"
    };

    try {
      const syncRes = await api.syncUser({ displayName: name });
      if (syncRes && syncRes.data) {
        currentUserState = syncRes.data;
      }
    } catch (syncErr) {
      console.warn("Backend user sync warning during registration:", syncErr);
    }

    updateNavbarAuthUI();
    return currentUserState;
  } else {
    // Dev register simulation
    const role = email.toLowerCase().includes("admin") ? "admin" : "student";
    const user = {
      uid: "dev_" + role + "_" + Date.now().toString(36),
      email,
      displayName: name || email.split("@")[0],
      role
    };
    const token = `dev-token-${role}-${user.uid}`;
    localStorage.setItem("notesphere_dev_user", JSON.stringify(user));
    localStorage.setItem("notesphere_dev_token", token);
    currentUserState = user;
    currentToken = token;
    updateNavbarAuthUI();
    return user;
  }
}

// Sign Out
async function handleSignOut() {
  if (typeof auth !== "undefined" && auth) {
    await auth.signOut();
  }
  localStorage.removeItem("notesphere_dev_user");
  localStorage.removeItem("notesphere_dev_token");
  currentUserState = null;
  currentToken = null;
  updateNavbarAuthUI();
  window.location.href = "/";
}

// Initialize auth listener immediately
initAuthListener();
document.addEventListener("DOMContentLoaded", updateNavbarAuthUI);

