import api from "./api";

async function fetchMe(token: string) {
  const response = await api.get("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export const authService = {
  login: async (email: string, password: string) => {
    // Backend uses OAuth2 password flow (form-encoded)
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);
    const response = await api.post("/auth/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    const token = response.data.access_token;
    if (token) {
      localStorage.setItem("access_token", token);
      const user = await fetchMe(token);
      localStorage.setItem("user", JSON.stringify(user));
      return { access_token: token, user };
    }
    return response.data;
  },

  register: async (email: string, password: string, full_name: string) => {
    await api.post("/auth/register", {
      email,
      password,
      full_name,
      role: "member",
    });
    // Register returns the user (no token) -> log in immediately
    return authService.login(email, password);
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  },

  getCurrentUser: () => {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem("access_token");
  },
};
