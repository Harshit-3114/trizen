import React, { createContext, useContext, useState, useEffect } from "react";
import { authService } from "../services/authService";

interface AuthContextType {
  user: any;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<any>;
  register: (email: string, password: string, full_name: string) => Promise<any>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const storedUser = authService.getCurrentUser();
    const isAuth = authService.isAuthenticated();
    setUser(storedUser);
    setIsAuthenticated(isAuth);
  }, []);

  const login = async (email: string, password: string) => {
    const result = await authService.login(email, password);
    setUser(result.user);
    setIsAuthenticated(true);
    return result;
  };

  const register = async (email: string, password: string, full_name: string) => {
    const result = await authService.register(email, password, full_name);
    setUser(result.user);
    setIsAuthenticated(true);
    return result;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

