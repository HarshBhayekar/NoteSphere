/**
 * NoteSphere - Central API Client
 * Wraps HTTP requests and attaches Firebase Bearer Token automatically
 */

const API_BASE = "/api";

async function getAuthHeader() {
  if (typeof getCurrentToken === "function") {
    const token = await getCurrentToken();
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

async function request(endpoint, options = {}) {
  const authHeaders = await getAuthHeader();
  const headers = {
    ...authHeaders,
    ...(options.headers || {})
  };

  // If body is NOT FormData, default to application/json
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    if (typeof options.body !== "string") {
      options.body = JSON.stringify(options.body);
    }
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  const contentType = response.headers.get("content-type") || "";
  let data = null;
  if (contentType.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    const message = (data && data.message) || `Request failed with status ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.details = (data && data.error) || null;

    if (response.status === 401) {
      const isAuthPage = window.location.pathname.includes("login.html") || window.location.pathname.includes("register.html");
      if (!isAuthPage && typeof showToast === "function") {
        showToast("Your session has timed out. Please sign in again.", "warning");
      }
    }

    throw error;
  }

  return data;
}

const api = {
  // Public
  getNotes: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/notes${query ? "?" + query : ""}`);
  },
  getNoteById: (id) => request(`/notes/${id}`),
  getSubjects: (semester) => {
    const q = semester ? `?semester=${semester}` : "";
    return request(`/subjects${q}`);
  },
  getDownloadUrl: (id) => request(`/notes/${id}/download?json=true`),

  // Protected User Actions
  uploadNote: (formData) => request("/notes", { method: "POST", body: formData }),
  getMyNotes: () => request("/my-notes"),
  deleteNote: (id) => request(`/notes/${id}`, { method: "DELETE" }),
  syncUser: (userData) => request("/auth/sync", { method: "POST", body: userData }),
  getMe: () => request("/auth/me")
};
