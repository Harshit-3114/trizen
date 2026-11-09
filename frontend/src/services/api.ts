import axios from "axios";

// CRA uses REACT_APP_* env vars. Backend serves versioned API under /api/v1.
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";
export const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Redirect to login on 401 (except the login call itself)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes("/auth/login")
    ) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      if (!window.location.pathname.startsWith("/gallery")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/** Resolve a photo storage_url ("/uploads/..." or absolute S3 URL) to a full URL. */
export function photoUrl(storageUrl: string): string {
  if (/^https?:\/\//i.test(storageUrl)) return storageUrl;
  const path = storageUrl.startsWith("/") ? storageUrl : `/${storageUrl}`;
  return `${API_ORIGIN}${path}`;
}

export default api;
